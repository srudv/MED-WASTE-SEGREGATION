
from pathlib import Path
import re

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data/raw/medical_waste.csv"
CLEAN_PATH = ROOT / "data/processed/medical_waste_cleaned.csv"

# ---------------------------------------------------------------------------
# Standard values and mappings
# ---------------------------------------------------------------------------
CATEGORICAL_COLUMNS = [
    "Hospital_Ward", "Floor_Number", "Waste_Category", "Target_Bin_Color",
    "Bin_ID", "Segregation_Status", "Alert_Triggered",
]

# Text that means "no value". Compared in lower case after trimming.
MISSING_TOKENS = {"", "nan", "none", "null", "unknown", "n/a", "na", "not recorded"}

WARD_MAP = {
    "emergency": "Emergency", "er": "Emergency", "emergency deptt": "Emergency",
    "icu": "ICU", "icuu": "ICU",
    "ot": "OT", "operation theater": "OT",
    "general ward": "General Ward",
    "opd": "OPD",
    "laboratory": "Laboratory", "lab": "Laboratory",
    "pediatrics": "Pediatrics", "paediatrics": "Pediatrics",
    "radiology": "Radiology",
}
FLOOR_MAP = {
    "ground": "Ground", "ground floor": "Ground",
    "floor 1": "Floor 1", "1st floor": "Floor 1",
    "floor 2": "Floor 2", "floor-2": "Floor 2",
    "floor 3": "Floor 3", "f3": "Floor 3",
    "floor 4": "Floor 4", "fourth floor": "Floor 4",
}
CATEGORY_MAP = {
    "anatomical waste": "Anatomical Waste",
    "blades": "Blades",
    "chemical containers": "Chemical Containers",
    "contaminated recyclable plastics": "Contaminated Recyclable Plastics",
    "cotton swabs": "Cotton Swabs", "cotton swab": "Cotton Swabs",
    "expired medications": "Expired Medications", "expired medication": "Expired Medications",
    "food waste": "Food Waste",
    "glassware": "Glassware",
    "hazardous chemicals": "Hazardous Chemicals",
    "iv bags/tubes": "IV Bags/Tubes", "iv bags / tubes": "IV Bags/Tubes",
    "metallic & plastic waste": "Metallic & Plastic Waste",
    "needles": "Needles",
    "non-infectious waste": "Non-Infectious Waste", "non infectious waste": "Non-Infectious Waste",
    "office trash": "Office Trash",
    "paper wrappers": "Paper Wrappers",
    "surgical waste": "Surgical Waste",
    "syringes": "Syringes",
    "urine/body fluids": "Urine/Body Fluids",
    "used bandages": "Used Bandages",
}
BIN_COLORS = ["Yellow", "Black", "Red", "Green", "Blue", "White"]
STATUS_MAP = {
    "correctly segregated": "Correctly Segregated", "correct": "Correctly Segregated",
    "misclassified / override required": "Misclassified", "misclassified": "Misclassified",
    "wrong": "Misclassified",
}
ALERT_MAP = {"yes": "Yes", "no": "No"}

VALID_BIN_IDS = {f"BIN_{i:02d}" for i in range(1, 13)}

# Numeric validity rules (values outside the range are impossible, not just unusual)
WEIGHT_MAX_GRAMS = 50_000          # 50 kg for one record; next largest raw value is 4,155.5 g
CONFIDENCE_RANGE = (0.0, 1.0)
FILL_RANGE = (0.0, 100.0)

EXPECTED_RAW_COLUMNS = [
    "Record_ID", "Timestamp", "Hospital_Ward", "Floor_Number", "Waste_Category",
    "Target_Bin_Color", "Bin_ID", "Weight_Grams", "AI_Confidence_Score",
    "Segregation_Status", "Bin_Fill_Level_Percentage", "Alert_Triggered",
]


def load_raw(path=RAW_PATH):
    """Load the raw CSV as text so no value is converted or lost on the way in."""
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def _norm(value):
    """Trim, collapse repeated spaces and lower-case a text value."""
    return re.sub(r"\s+", " ", str(value).strip()).lower()


def _is_missing(value):
    return _norm(value) in MISSING_TOKENS


class _Audit:
    """Collects one row per changed cell."""

    def __init__(self, raw_df):
        self.rows = []
        self.raw_df = raw_df

    def add(self, idx, column, original, cleaned, decision):
        self.rows.append({
            "row_number": idx + 2,                      # line number in the raw CSV file
            "record_id": str(self.raw_df.at[idx, "Record_ID"]).strip(),
            "column": column,
            "original_value": original,
            "cleaned_value": None if pd.isna(cleaned) else cleaned,
            "decision": decision,
        })

    def frame(self):
        cols = ["row_number", "record_id", "column", "original_value", "cleaned_value", "decision"]
        return pd.DataFrame(self.rows, columns=cols)


# ---------------------------------------------------------------------------
# Column cleaners
# ---------------------------------------------------------------------------
def _clean_mapped(df, raw_df, col, mapper, audit, what):
    """Standardise a category column. `mapper(normalised_text)` returns the standard
    value or None when the value cannot be mapped safely."""
    out = []
    for idx, raw in raw_df[col].items():
        if _is_missing(raw):
            out.append(np.nan)
            if str(raw).strip() != "":
                audit.add(idx, col, raw, np.nan, f"Placeholder text treated as missing")
            continue
        std = mapper(_norm(raw))
        if std is None:
            out.append(np.nan)
            audit.add(idx, col, raw, np.nan, f"Not a valid {what}; set to missing (not guessed)")
        else:
            out.append(std)
            if std != raw:
                audit.add(idx, col, raw, std, f"Standardised {what} (case, spacing, spelling or alias)")
    df[col] = pd.Series(out, index=df.index, dtype="object")


def _bin_color_mapper(text):
    word = text.replace(" bin", "").strip()
    return f"{word.capitalize()} Bin" if word.capitalize() in BIN_COLORS else None


def _bin_id_mapper(text):
    match = re.fullmatch(r"bin_(\d{1,2})", text)
    if not match:
        return None
    std = f"BIN_{int(match.group(1)):02d}"
    return std if std in VALID_BIN_IDS else None


def parse_timestamps(raw_series, audit=None, df_index=None):
    """Parse mixed-format timestamps.

    * ISO format is used as is.
    * `YYYY/MM/DD HH:MM` and `MM-DD-YYYY HH:MM` are unambiguous and are converted.
    * `DD/MM/YYYY` vs `MM/DD/YYYY` is ambiguous; it is resolved with the date window of the
      valid ISO records and left missing if neither reading (or both) fits.
    * Impossible dates and text such as 'not recorded' become missing.
    """
    iso = pd.to_datetime(raw_series.str.strip(), format="%Y-%m-%d %H:%M:%S", errors="coerce")
    low, high = iso.min().normalize(), iso.max().normalize() + pd.Timedelta(days=1)
    results = {}
    for idx, raw in raw_series.items():
        text = str(raw).strip()
        parsed, note = pd.NaT, None
        if pd.notna(iso[idx]):
            parsed = iso[idx]
        elif re.fullmatch(r"\d{4}/\d{2}/\d{2} \d{2}:\d{2}", text):
            parsed = pd.to_datetime(text, format="%Y/%m/%d %H:%M", errors="coerce")
            note = "Converted from YYYY/MM/DD format"
        elif re.fullmatch(r"\d{2}-\d{2}-\d{4} \d{2}:\d{2}", text):
            parsed = pd.to_datetime(text, format="%m-%d-%Y %H:%M", errors="coerce")
            note = "Converted from MM-DD-YYYY format (month first)"
        elif re.fullmatch(r"\d{2}/\d{2}/\d{4} \d{2}:\d{2}", text):
            day_first = pd.to_datetime(text, format="%d/%m/%Y %H:%M", errors="coerce")
            month_first = pd.to_datetime(text, format="%m/%d/%Y %H:%M", errors="coerce")
            fits = [d for d in (day_first, month_first) if pd.notna(d) and low <= d < high]
            if len(fits) == 1:
                parsed = fits[0]
                note = "Ambiguous DD/MM vs MM/DD; resolved with the October 2026 date window of the other records"
            else:
                note = "Ambiguous date that could not be resolved"
        else:
            note = "Not a usable timestamp (text or impossible date)"
        results[idx] = parsed
        if audit is not None and note is not None:
            audit.add(idx, "Timestamp", raw,
                      parsed.strftime("%Y-%m-%d %H:%M:%S") if pd.notna(parsed) else np.nan,
                      note if pd.notna(parsed) else note + "; set to missing")
    return pd.Series(results).astype("datetime64[ns]")


def _clean_numeric(df, raw_df, col, valid, audit, text_rules=None, label=""):
    """Convert text to numbers and blank out impossible values.

    `valid(x)` returns True for an acceptable number. `text_rules` maps a normalised text
    value to a number (for example 'full' to 100).
    """
    text_rules = text_rules or {}
    out = []
    for idx, raw in raw_df[col].items():
        text = str(raw).strip()
        if text == "":
            out.append(np.nan)
            continue
        norm = _norm(text)
        value, note = np.nan, None
        if norm in text_rules:
            value, note = text_rules[norm], f"'{text}' converted to {text_rules[norm]}"
        elif norm in MISSING_TOKENS:
            note = "Placeholder text treated as missing"
        else:
            try:
                value = float(norm.replace(",", "").rstrip("%").strip())
                if norm != text and ("," in norm or norm.endswith("%")):
                    note = "Removed thousands separator or % sign"
            except ValueError:
                note = "Text in a numeric column; set to missing"
        if pd.notna(value) and not valid(value):
            audit.add(idx, col, raw, np.nan, f"Impossible {label} value; set to missing")
            value = np.nan
        elif note is not None:
            audit.add(idx, col, raw, value, note)
        out.append(value)
    df[col] = pd.Series(out, index=df.index, dtype="float64")


# ---------------------------------------------------------------------------
# Main cleaning function
# ---------------------------------------------------------------------------
def clean_dataframe(raw_df):
    """Return (cleaned_df, audit_df, duplicates_df).

    cleaned_df    one row per distinct record, standard labels, real numeric types, plus
                  Row_Number, derived date columns and review flags.
    audit_df      one row per changed cell (what changed, why).
    duplicates_df raw rows removed because they repeat another row in every field except
                  Record_ID.
    """
    missing_cols = set(EXPECTED_RAW_COLUMNS) - set(raw_df.columns)
    if missing_cols:
        raise ValueError(f"Missing expected columns: {sorted(missing_cols)}")

    audit = _Audit(raw_df)
    df = pd.DataFrame(index=raw_df.index)
    df["Row_Number"] = raw_df.index + 2   # line number in the raw CSV (header is line 1)

    # Identifier: trim only
    df["Record_ID"] = raw_df["Record_ID"].str.strip()
    for idx in raw_df.index[raw_df["Record_ID"] != df["Record_ID"]]:
        audit.add(idx, "Record_ID", raw_df.at[idx, "Record_ID"], df.at[idx, "Record_ID"], "Removed leading/trailing spaces")

    df["Timestamp"] = parse_timestamps(raw_df["Timestamp"], audit)

    _clean_mapped(df, raw_df, "Hospital_Ward", WARD_MAP.get, audit, "ward")
    _clean_mapped(df, raw_df, "Floor_Number", FLOOR_MAP.get, audit, "floor")
    _clean_mapped(df, raw_df, "Waste_Category", CATEGORY_MAP.get, audit, "waste category")
    _clean_mapped(df, raw_df, "Target_Bin_Color", _bin_color_mapper, audit, "bin colour")
    _clean_mapped(df, raw_df, "Bin_ID", _bin_id_mapper, audit, "bin ID (BIN_01 to BIN_12)")
    _clean_mapped(df, raw_df, "Segregation_Status", STATUS_MAP.get, audit, "segregation status")
    _clean_mapped(df, raw_df, "Alert_Triggered", ALERT_MAP.get, audit, "alert flag (Yes/No)")

    _clean_numeric(df, raw_df, "Weight_Grams", lambda x: 0 < x <= WEIGHT_MAX_GRAMS, audit, label="weight")
    _clean_numeric(df, raw_df, "AI_Confidence_Score",
                   lambda x: CONFIDENCE_RANGE[0] <= x <= CONFIDENCE_RANGE[1], audit, label="confidence")
    _clean_numeric(df, raw_df, "Bin_Fill_Level_Percentage",
                   lambda x: FILL_RANGE[0] <= x <= FILL_RANGE[1], audit,
                   text_rules={"full": 100.0}, label="fill level")

    df = df[["Row_Number"] + EXPECTED_RAW_COLUMNS]

    # ---- Duplicates -------------------------------------------------------
    # Rows that are identical in every field except Record_ID (same minute, ward, weight,
    # bin ...) are copies. Compare the cleaned values so spelling variants do not hide them.
    key_cols = [c for c in EXPECTED_RAW_COLUMNS if c != "Record_ID"]
    is_copy = df.duplicated(subset=key_cols, keep="first")
    duplicates_df = raw_df.loc[is_copy].copy()
    duplicates_df.insert(0, "Row_Number", df.loc[is_copy, "Row_Number"])
    for idx in df.index[is_copy]:
        audit.add(idx, "(whole row)", raw_df.at[idx, "Record_ID"], np.nan,
                  "Row removed: identical to an earlier row in every field except Record_ID")
    df = df.loc[~is_copy].copy()

    # ---- Flags and derived columns ---------------------------------------
    df["Duplicate_Record_ID"] = df["Record_ID"].duplicated(keep=False)
    df["Date"] = df["Timestamp"].dt.date
    df["Hour"] = df["Timestamp"].dt.hour.astype("Int64")
    df["Weekday"] = df["Timestamp"].dt.day_name()
    expected = expected_bin_by_category(df)
    df["Category_Bin_Mismatch"] = (
        df["Waste_Category"].notna() & df["Target_Bin_Color"].notna()
        & (df["Target_Bin_Color"] != df["Waste_Category"].map(expected))
    )
    df["Weight_Outlier"] = flag_iqr_outliers(df["Weight_Grams"])
    df = df.reset_index(drop=True)
    return df, audit.frame(), duplicates_df


def expected_bin_by_category(df):
    """Most common target bin for each waste category in the data.

    This is derived from the data itself (not an external regulation) and is only used to
    flag records whose bin colour disagrees with the usual one for their category.
    """
    known = df.dropna(subset=["Waste_Category", "Target_Bin_Color"])
    counts = known.groupby(["Waste_Category", "Target_Bin_Color"]).size().unstack(fill_value=0)
    return counts.idxmax(axis=1)


def iqr_fences(series, k=1.5):
    values = series.dropna()
    q1, q3 = values.quantile([0.25, 0.75])
    iqr = q3 - q1
    return q1 - k * iqr, q3 + k * iqr


def flag_iqr_outliers(series, k=1.5):
    """True where a value lies outside the 1.5 x IQR fences. Flagged, never removed."""
    low, high = iqr_fences(series, k)
    return series.notna() & ((series < low) | (series > high))


def iqr_outlier_summary(df, columns=("Weight_Grams", "AI_Confidence_Score", "Bin_Fill_Level_Percentage")):
    """Table of IQR fences and flagged counts for the numeric columns."""
    rows = []
    for col in columns:
        low, high = iqr_fences(df[col])
        flagged = flag_iqr_outliers(df[col])
        rows.append({"column": col, "lower_fence": round(low, 3), "upper_fence": round(high, 3),
                     "flagged_count": int(flagged.sum()),
                     "min_flagged": df.loc[flagged, col].min() if flagged.any() else np.nan,
                     "max_flagged": df.loc[flagged, col].max() if flagged.any() else np.nan})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------
def validate_dataframe(df, raw_df=None, duplicates_df=None):
    """Return a table of pass/fail checks on the cleaned data. Nothing is altered."""
    checks = []

    def add(name, passed, details):
        checks.append({"check": name, "passed": bool(passed), "details": details})

    if raw_df is not None and duplicates_df is not None:
        add("every raw row accounted for", len(df) + len(duplicates_df) == len(raw_df),
            f"{len(raw_df)} raw = {len(df)} kept + {len(duplicates_df)} removed copies")
    add("12 raw columns kept", all(c in df.columns for c in EXPECTED_RAW_COLUMNS), "all present")
    add("Row_Number is unique", df["Row_Number"].is_unique, f"unique={df['Row_Number'].nunique()}")
    add("no rows identical except for Record_ID",
        not df.duplicated(subset=[c for c in EXPECTED_RAW_COLUMNS if c != "Record_ID"]).any(),
        f"remaining={int(df.duplicated(subset=[c for c in EXPECTED_RAW_COLUMNS if c != 'Record_ID']).sum())}")
    add("Timestamp is datetime", pd.api.types.is_datetime64_any_dtype(df["Timestamp"]),
        f"dtype={df['Timestamp'].dtype}")
    ts = df["Timestamp"].dropna()
    add("timestamps inside 1-30 Oct 2026",
        ts.between("2026-10-01", "2026-10-31").all(), f"min={ts.min()}, max={ts.max()}")
    for col, valid in [("Hospital_Ward", set(WARD_MAP.values())),
                       ("Floor_Number", set(FLOOR_MAP.values())),
                       ("Waste_Category", set(CATEGORY_MAP.values())),
                       ("Target_Bin_Color", {f"{c} Bin" for c in BIN_COLORS}),
                       ("Bin_ID", VALID_BIN_IDS),
                       ("Segregation_Status", set(STATUS_MAP.values())),
                       ("Alert_Triggered", set(ALERT_MAP.values()))]:
        bad = sorted(set(df[col].dropna()) - valid)
        add(f"{col} uses only standard values", not bad,
            f"{df[col].nunique()} distinct values" if not bad else f"unexpected={bad}")
    for col in ["Weight_Grams", "AI_Confidence_Score", "Bin_Fill_Level_Percentage"]:
        add(f"{col} is numeric", pd.api.types.is_float_dtype(df[col]), f"dtype={df[col].dtype}")
    w = df["Weight_Grams"].dropna()
    add("weights between 0 and 50,000 g", ((w > 0) & (w <= WEIGHT_MAX_GRAMS)).all(), f"min={w.min()}, max={w.max()}")
    c = df["AI_Confidence_Score"].dropna()
    add("AI confidence between 0 and 1", c.between(0, 1).all(), f"min={c.min()}, max={c.max()}")
    f = df["Bin_Fill_Level_Percentage"].dropna()
    add("bin fill level between 0 and 100", f.between(0, 100).all(), f"min={f.min()}, max={f.max()}")
    return pd.DataFrame(checks)


def missing_value_report(df):
    """Missing count and share for each column of the cleaned data."""
    cols = EXPECTED_RAW_COLUMNS
    out = pd.DataFrame({"missing": df[cols].isna().sum()})
    out["missing_pct"] = (out["missing"] / len(df) * 100).round(2)
    return out


# ---------------------------------------------------------------------------
# Optional encoding and scaling (for modelling, not applied to the cleaned CSV)
# ---------------------------------------------------------------------------
def encode_and_scale(df, numeric_cols=("Weight_Grams", "AI_Confidence_Score", "Bin_Fill_Level_Percentage")):
    """Return a modelling-ready copy: one-hot encoded categories and min-max scaled numbers.

    The cleaned CSV is deliberately NOT scaled or encoded, because descriptive statistics
    and charts need the real units (grams, percent) and readable labels. Use this function
    only if a later step (clustering, a classifier) needs it. Missing values stay missing.
    """
    out = df[list(numeric_cols)].copy()
    for col in numeric_cols:
        lo, hi = out[col].min(), out[col].max()
        out[col] = (out[col] - lo) / (hi - lo)
    dummies = pd.get_dummies(df[CATEGORICAL_COLUMNS], dummy_na=False, dtype=int)
    return pd.concat([out, dummies], axis=1)


def save_cleaned(df, path=CLEAN_PATH):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    out = df.copy()
    out["Timestamp"] = out["Timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
    out.to_csv(path, index=False)
    return path


def main():
    raw = load_raw()
    cleaned, audit, dups = clean_dataframe(raw)
    checks = validate_dataframe(cleaned, raw, dups)
    failed = checks[~checks["passed"]]
    if not failed.empty:
        raise SystemExit(f"Validation failed:\n{failed.to_string(index=False)}")
    path = save_cleaned(cleaned)
    print(f"Raw rows: {len(raw)} | cleaned rows: {len(cleaned)} | removed copies: {len(dups)} | audit entries: {len(audit)}")
    print(f"All {len(checks)} validation checks passed. Saved {path}")


if __name__ == "__main__":
    main()
