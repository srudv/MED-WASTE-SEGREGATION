"""Reusable cleaning and validation functions for CPCB medical-waste data."""
import pandas as pd

TEXT_COLUMNS = {"state_ut"}
IDENTIFIER_COLUMNS = {"s_no"}
ZERO_TOKENS = {"NIL"}
MISSING_TOKENS = {"INP", "NA", ""}
STATE_RENAMES = {
    "Telengana": "Telangana",
    "J & K": "Jammu & Kashmir",
    "Andaman Nicobar": "Andaman and Nicobar Islands",
    "Daman &Diu and Dadra & Nagar Haveli": "Daman & Diu and Dadra & Nagar Haveli",
}

def load_raw(path):
    """Load raw CSV as strings so source codes and blanks are not lost."""
    return pd.read_csv(path, dtype=str, keep_default_na=False)

def clean_dataframe(raw_df):
    """Return cleaned data and a cell-level audit of special-value conversions."""
    df = raw_df.copy()
    audit = []
    for col in df.columns:
        if col in TEXT_COLUMNS:
            continue
        if col in IDENTIFIER_COLUMNS:
            df[col] = pd.to_numeric(df[col], errors="raise").astype("Int64")
            continue
        converted = []
        for idx, value in df[col].items():
            token = str(value).strip()
            upper = token.upper()
            if upper in ZERO_TOKENS:
                converted.append(0.0)
                audit.append({"row_number": idx + 2, "column": col, "original_value": value,
                              "cleaned_value": 0, "decision": "NIL interpreted as zero/none per source documentation"})
            elif upper in MISSING_TOKENS:
                converted.append(float("nan"))
                decision = f"{upper} retained as missing; source does not define it as zero" if token else "Blank source cell retained as missing"
                audit.append({"row_number": idx + 2, "column": col, "original_value": value,
                              "cleaned_value": None, "decision": decision})
            else:
                try:
                    converted.append(float(token))
                except ValueError:
                    converted.append(float("nan"))
                    audit.append({"row_number": idx + 2, "column": col, "original_value": value,
                                  "cleaned_value": None, "decision": "Non-numeric explanatory text retained as missing; see audit"})
        df[col] = pd.Series(converted, index=df.index, dtype="float64")
    df["state_ut"] = df["state_ut"].replace(STATE_RENAMES)
    audit_df = pd.DataFrame(audit, columns=["row_number", "column", "original_value", "cleaned_value", "decision"])
    return df, audit_df

def validate_dataframe(df):
    """Return validation checks; does not silently delete or alter source records."""
    checks = []
    def add(name, passed, details):
        checks.append({"check": name, "passed": bool(passed), "details": details})
    add("37 source records retained", len(df) == 37, f"rows={len(df)}")
    add("23 columns retained", len(df.columns) == 23, f"columns={len(df.columns)}")
    add("serial numbers unique", df["s_no"].is_unique, f"unique={df['s_no'].nunique()}")
    add("serial numbers complete", df["s_no"].notna().all(), f"missing={df['s_no'].isna().sum()}")
    add("state labels unique", df["state_ut"].is_unique, f"unique={df['state_ut'].nunique()}")
    numeric = [c for c in df.columns if c not in TEXT_COLUMNS]
    non_numeric = [c for c in numeric if not pd.api.types.is_numeric_dtype(df[c])]
    add("numeric fields converted", not non_numeric, f"non-numeric columns={non_numeric}")
    add("no duplicate complete rows", not df.duplicated().any(), f"duplicate_rows={int(df.duplicated().sum())}")
    return pd.DataFrame(checks)

def iqr_outlier_summary(df):
    """Flag potential IQR outliers for review; never remove aggregated observations."""
    rows = []
    for col in df.select_dtypes(include="number").columns:
        if col == "s_no":
            continue
        values = df[col].dropna()
        if len(values) < 4:
            continue
        q1, q3 = values.quantile([0.25, 0.75])
        iqr = q3 - q1
        low, high = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        flagged = values[(values < low) | (values > high)]
        rows.append({"column": col, "lower_iqr_fence": low, "upper_iqr_fence": high,
                     "flagged_count": len(flagged),
                     "flagged_states": "; ".join(df.loc[flagged.index, "state_ut"].tolist())})
    return pd.DataFrame(rows)
