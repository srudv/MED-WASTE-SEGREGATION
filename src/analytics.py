"""Reusable exploratory analytics for the CPCB 2023 biomedical-waste dataset."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data/processed/medical_waste_cleaned.csv"
DEFAULT_REPORTS = ROOT / "reports"
NUMERIC_COLUMNS = ["bedded_hcfs","non_bedded_hcfs","total_hcfs","total_beds","hcfs_applied_authorization","hcfs_granted_authorization","hcfs_without_authorization","hcfs_utilizing_cbwtf","bmw_generated_kg_day","bmw_treated_disposed_kg_day","hcfs_with_captive_treatment","captive_incinerators","cbwtfs_operational","cbwtfs_under_construction","deep_burial_hcf","deep_burial_cbwtf","bmw_treated_captive_kg_day","bmw_treated_cbwtf_kg_day","violations_hcf_cbwtf","show_cause_notices","cbwtfs_with_ocems"]

def load_data(path=DEFAULT_INPUT):
    df = pd.read_csv(path)
    required = {"state_ut","s_no","bmw_generated_kg_day","bmw_treated_disposed_kg_day"}
    missing = required.difference(df.columns)
    if missing: raise ValueError(f"Missing required columns: {sorted(missing)}")
    if len(df) != 37: raise ValueError(f"Expected 37 reporting entities, found {len(df)}")
    if df["state_ut"].duplicated().any(): raise ValueError("Duplicate reporting-entity labels")
    return df

def numeric_frame(df):
    out = df.copy()
    for col in NUMERIC_COLUMNS:
        if col in out: out[col] = pd.to_numeric(out[col], errors="coerce")
    return out

def treatment_metrics(df):
    d = numeric_frame(df)
    generated = d["bmw_generated_kg_day"].sum()
    treated = d["bmw_treated_disposed_kg_day"].sum()
    captive = d["bmw_treated_captive_kg_day"].sum()
    cbwtf = d["bmw_treated_cbwtf_kg_day"].sum()
    return {"reporting_entities": int(len(d)), "generated_kg_day_total": float(generated),
            "treated_disposed_kg_day_total": float(treated),
            "treated_to_generated_percent": float(treated/generated*100) if generated else float("nan"),
            "treated_minus_generated_kg_day": float(treated-generated),
            "captive_treatment_kg_day": float(captive), "cbwtf_treatment_kg_day": float(cbwtf),
            "captive_share_of_reported_treatment_percent": float(captive/treated*100) if treated else float("nan"),
            "cbwtf_share_of_reported_treatment_percent": float(cbwtf/treated*100) if treated else float("nan")}

def build_summary_statistics(df):
    d = numeric_frame(df)
    records = []
    for col in NUMERIC_COLUMNS:
        if col not in d: continue
        s = d[col].dropna()
        if s.empty: continue
        stats = {"count":s.count(),"missing":d[col].isna().sum(),"sum":s.sum(),"mean":s.mean(),
                 "median":s.median(),"std_sample":s.std(),"min":s.min(),"q1":s.quantile(.25),
                 "q3":s.quantile(.75),"max":s.max()}
        for stat,value in stats.items():
            records.append({"section":"column_descriptive_statistics","metric":col,"statistic":stat,
                            "category":"","value":value,"unit":"kg/day or count; see column name"})
    for metric,value in treatment_metrics(d).items():
        records.append({"section":"derived_metrics","metric":metric,"statistic":"value",
                        "category":"","value":value,"unit":"as indicated by metric name"})
    for _,row in d[["state_ut","bmw_generated_kg_day","bmw_treated_disposed_kg_day"]].iterrows():
        records.append({"section":"entity_comparison","metric":"bmw_generated_kg_day",
                        "statistic":"generated_kg_day","category":row["state_ut"],
                        "value":row["bmw_generated_kg_day"],"unit":"kg/day"})
        records.append({"section":"entity_comparison","metric":"bmw_treated_disposed_kg_day",
                        "statistic":"treated_disposed_kg_day","category":row["state_ut"],
                        "value":row["bmw_treated_disposed_kg_day"],"unit":"kg/day"})
    return pd.DataFrame(records)

def write_outputs(input_path=DEFAULT_INPUT, reports_dir=DEFAULT_REPORTS):
    df = load_data(input_path)
    reports_dir.mkdir(parents=True, exist_ok=True)
    output = reports_dir / "summary_statistics.csv"
    build_summary_statistics(df).to_csv(output, index=False)
    return output

if __name__ == "__main__":
    print("Wrote:", write_outputs())
    print(pd.Series(treatment_metrics(load_data())).to_string())
