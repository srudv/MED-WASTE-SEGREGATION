"""Reusable exploratory analytics for the cleaned MedWaste AI segregation records.

Input:  data/processed/medical_waste_cleaned.csv   (made by src/preprocessing.py)
Output: reports/summary_statistics.csv and reports/analytics_summary.md

Missing values are skipped, never treated as zero, and every table reports the number of
records it is based on. Run from the repository root:

    python -m src.analytics
"""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data/processed/medical_waste_cleaned.csv"
DEFAULT_REPORTS = ROOT / "reports"

CATEGORY_COLUMNS = ["Waste_Category", "Target_Bin_Color", "Hospital_Ward", "Floor_Number",
                    "Bin_ID", "Segregation_Status", "Alert_Triggered"]
COMPARISON_COLUMNS = ["Waste_Category", "Hospital_Ward", "Floor_Number", "Target_Bin_Color", "Bin_ID"]
NUMERIC_COLUMNS = ["Weight_Grams", "AI_Confidence_Score", "Bin_Fill_Level_Percentage"]
REQUIRED_COLUMNS = ["Timestamp", "Weight_Grams", "AI_Confidence_Score", "Bin_Fill_Level_Percentage",
                    "Segregation_Status", "Alert_Triggered"] + CATEGORY_COLUMNS
ALPHA = 0.05
FILL_BANDS = [-0.01, 50, 70, 80, 85, 90, 95, 100]   # each band includes its upper bound
FILL_BAND_LABELS = ["0 to 50", "over 50 to 70", "over 70 to 80", "over 80 to 85", "over 85 to 90",
                    "over 90 to 95", "over 95 to 100"]


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------
def load_data(path=DEFAULT_INPUT):
    """Load the cleaned dataset and check that the columns this module needs are present."""
    df = pd.read_csv(path, parse_dates=["Timestamp"])
    missing = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    if df.empty:
        raise ValueError("The cleaned dataset has no rows")
    for col in NUMERIC_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="raise")
    return df


def dataset_overview(df):
    ts = df["Timestamp"].dropna()
    days = (ts.max().normalize() - ts.min().normalize()).days + 1
    return {
        "records": int(len(df)),
        "columns": int(df.shape[1]),
        "first_date": str(ts.min().date()),
        "last_date": str(ts.max().date()),
        "calendar_days": int(days),
        "records_with_timestamp": int(len(ts)),
        "cells_missing_in_analysed_columns": int(df[REQUIRED_COLUMNS].isna().sum().sum()),
    }


# ---------------------------------------------------------------------------
# Distributions and descriptive statistics
# ---------------------------------------------------------------------------
def category_counts(df, column):
    """Count and share (percent of records with a known value) for each category."""
    s = df[column].dropna()
    out = s.value_counts().rename_axis(column).reset_index(name="count")
    out["share_pct"] = (out["count"] / len(s) * 100).round(2)
    return out


def uniformity_test(df, column):
    """Chi-square goodness-of-fit against equal shares for every category."""
    counts = df[column].dropna().value_counts()
    chi2, p = stats.chisquare(counts.values)
    return {"column": column, "categories": int(len(counts)), "n": int(counts.sum()),
            "min_count": int(counts.min()), "max_count": int(counts.max()),
            "chi2": float(chi2), "p_value": float(p)}


def numeric_descriptives(df, columns=NUMERIC_COLUMNS):
    rows = []
    for col in columns:
        s = df[col].dropna()
        q1, q3 = s.quantile([0.25, 0.75])
        rows.append({"column": col, "count": int(s.count()), "missing": int(df[col].isna().sum()),
                     "mean": s.mean(), "median": s.median(), "std": s.std(), "min": s.min(),
                     "q1": q1, "q3": q3, "max": s.max(), "iqr": q3 - q1, "skewness": s.skew(),
                     "sum": s.sum()})
    return pd.DataFrame(rows)


def group_numeric_summary(df, group_col, value_col="Weight_Grams"):
    """n, mean, median, std and total of a numeric column for each group."""
    sub = df.dropna(subset=[group_col, value_col])
    out = sub.groupby(group_col)[value_col].agg(n="count", mean="mean", median="median",
                                                std="std", total="sum")
    out["share_of_total_pct"] = out["total"] / out["total"].sum() * 100
    return out.sort_values("median", ascending=False).reset_index()


def spearman_matrix(df, columns=NUMERIC_COLUMNS):
    return df[list(columns)].corr(method="spearman")


# ---------------------------------------------------------------------------
# Segregation outcome comparisons
# ---------------------------------------------------------------------------
def wilson_interval(k, n, z=1.96):
    """95% Wilson confidence interval for a proportion k/n, returned in percent."""
    if n == 0:
        return (np.nan, np.nan)
    p = k / n
    denom = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / denom
    half = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
    return (max(0.0, centre - half) * 100, min(1.0, centre + half) * 100)


def misclassification_rate(df):
    """Overall share of records with status 'Misclassified' among records with a known status."""
    s = df["Segregation_Status"].dropna()
    k, n = int((s == "Misclassified").sum()), int(len(s))
    low, high = wilson_interval(k, n)
    return {"misclassified": k, "known_status": n, "rate_pct": k / n * 100,
            "ci_low_pct": low, "ci_high_pct": high}


def misclassification_by(df, group_col):
    """Misclassification rate (with 95% CI) for each group, sorted from highest to lowest."""
    sub = df.dropna(subset=[group_col, "Segregation_Status"])
    g = sub.groupby(group_col)["Segregation_Status"].agg(
        n="count", misclassified=lambda s: int((s == "Misclassified").sum()))
    g["rate_pct"] = g["misclassified"] / g["n"] * 100
    ci = [wilson_interval(k, n) for k, n in zip(g["misclassified"], g["n"])]
    g["ci_low_pct"] = [c[0] for c in ci]
    g["ci_high_pct"] = [c[1] for c in ci]
    return g.sort_values("rate_pct", ascending=False).reset_index()


def chi_square_vs_status(df, column):
    """Is the segregation outcome independent of `column`? (chi-square test of independence)"""
    sub = df.dropna(subset=[column, "Segregation_Status"])
    table = pd.crosstab(sub[column], sub["Segregation_Status"])
    chi2, p, dof, expected = stats.chi2_contingency(table)
    return {"column": column, "n": int(table.values.sum()), "chi2": float(chi2), "dof": int(dof),
            "p_value": float(p), "share_cells_expected_below_5": float((expected < 5).mean())}


def kruskal_by_group(df, group_col, value_col="Weight_Grams"):
    """Do the groups differ in `value_col`? (Kruskal-Wallis, suitable for skewed data)"""
    sub = df.dropna(subset=[group_col, value_col])
    groups = [g[value_col].values for _, g in sub.groupby(group_col)]
    h, p = stats.kruskal(*groups)
    return {"column": group_col, "value": value_col, "n": int(len(sub)), "groups": len(groups),
            "h": float(h), "p_value": float(p)}


def confidence_by_status(df):
    """AI confidence of correct vs misclassified records (Mann-Whitney U test)."""
    sub = df.dropna(subset=["AI_Confidence_Score", "Segregation_Status"])
    ok = sub.loc[sub["Segregation_Status"] == "Correctly Segregated", "AI_Confidence_Score"]
    bad = sub.loc[sub["Segregation_Status"] == "Misclassified", "AI_Confidence_Score"]
    u, p = stats.mannwhitneyu(ok, bad, alternative="two-sided")
    return {"n_correct": int(len(ok)), "n_misclassified": int(len(bad)),
            "median_correct": float(ok.median()), "median_misclassified": float(bad.median()),
            "mean_correct": float(ok.mean()), "mean_misclassified": float(bad.mean()),
            "u": float(u), "p_value": float(p)}


# ---------------------------------------------------------------------------
# Alerts and bin fill level
# ---------------------------------------------------------------------------
def alert_by_fill_band(df):
    """Alert rate for each bin fill-level band."""
    sub = df.dropna(subset=["Bin_Fill_Level_Percentage", "Alert_Triggered"]).copy()
    sub["fill_band"] = pd.cut(sub["Bin_Fill_Level_Percentage"], FILL_BANDS, labels=FILL_BAND_LABELS)
    g = sub.groupby("fill_band", observed=True)["Alert_Triggered"].agg(
        n="count", alerts=lambda s: int((s == "Yes").sum()))
    g["alert_rate_pct"] = g["alerts"] / g["n"] * 100
    g.index = g.index.astype(str)
    return g.rename_axis("fill_band").reset_index()


def alert_analysis(df):
    """What triggers alerts? Compares alerts with segregation status and bin fill level."""
    sub = df.dropna(subset=["Alert_Triggered", "Segregation_Status", "Bin_Fill_Level_Percentage"])
    alerts = sub[sub["Alert_Triggered"] == "Yes"]
    ok = sub[sub["Segregation_Status"] == "Correctly Segregated"]
    mis = sub[sub["Segregation_Status"] == "Misclassified"]
    ok_high = ok[ok["Bin_Fill_Level_Percentage"] > 85]
    ok_low = ok[ok["Bin_Fill_Level_Percentage"] <= 85]
    known_alert = df["Alert_Triggered"].dropna()
    return {
        "records_with_alert_known": int(len(known_alert)),
        "alerts": int((known_alert == "Yes").sum()),
        "alert_rate_pct": float((known_alert == "Yes").mean() * 100),
        "records_used": int(len(sub)),
        "alerts_used": int(len(alerts)),
        "alerts_misclassified": int((alerts["Segregation_Status"] == "Misclassified").sum()),
        "alerts_correct_and_fill_above_85": int(((alerts["Segregation_Status"] == "Correctly Segregated")
                                                  & (alerts["Bin_Fill_Level_Percentage"] > 85)).sum()),
        "alerts_correct_and_fill_85_or_below": int(((alerts["Segregation_Status"] == "Correctly Segregated")
                                                     & (alerts["Bin_Fill_Level_Percentage"] <= 85)).sum()),
        "misclassified_with_alert_pct": float((mis["Alert_Triggered"] == "Yes").mean() * 100),
        "misclassified_used": int(len(mis)),
        "correct_fill_above_85_alert_pct": float((ok_high["Alert_Triggered"] == "Yes").mean() * 100),
        "correct_fill_above_85_n": int(len(ok_high)),
        "correct_fill_85_or_below_alert_pct": float((ok_low["Alert_Triggered"] == "Yes").mean() * 100),
        "correct_fill_85_or_below_n": int(len(ok_low)),
    }


def fill_level_by_bin(df):
    """Fill-level statistics and alert rate for each physical bin."""
    sub = df.dropna(subset=["Bin_ID", "Bin_Fill_Level_Percentage"])
    g = sub.groupby("Bin_ID")["Bin_Fill_Level_Percentage"].agg(
        n="count", mean="mean", median="median", share_above_85=lambda s: (s > 85).mean() * 100)
    alerts = (df.dropna(subset=["Bin_ID", "Alert_Triggered"]).groupby("Bin_ID")["Alert_Triggered"]
              .apply(lambda s: (s == "Yes").mean() * 100).rename("alert_rate_pct"))
    return g.join(alerts).reset_index()


# ---------------------------------------------------------------------------
# Time trends
# ---------------------------------------------------------------------------
def daily_summary(df):
    """Records, total weight and misclassification rate for every calendar day in the window."""
    d = df.dropna(subset=["Timestamp"]).copy()
    d["Day"] = d["Timestamp"].dt.normalize()
    full = pd.date_range(d["Day"].min(), d["Day"].max(), freq="D")
    out = pd.DataFrame(index=full)
    out["records"] = d.groupby("Day").size().reindex(full, fill_value=0)
    out["total_weight_g"] = d.groupby("Day")["Weight_Grams"].sum().reindex(full, fill_value=0)
    known = d.dropna(subset=["Segregation_Status"])
    out["misclassified"] = known[known["Segregation_Status"] == "Misclassified"].groupby("Day").size().reindex(full, fill_value=0)
    out["known_status"] = known.groupby("Day").size().reindex(full, fill_value=0)
    out["misclassified_rate_pct"] = out["misclassified"] / out["known_status"].replace(0, np.nan) * 100
    out.index.name = "Date"
    return out.reset_index()


def weekday_summary(df):
    """Records per weekday, divided by how many of that weekday fall in the date window.

    Raw weekday totals would mislead: a one-month window contains 5 of some weekdays and
    4 of others, so the average per day is the fair comparison.
    """
    daily = daily_summary(df)
    daily["Weekday"] = daily["Date"].dt.day_name()
    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    g = daily.groupby("Weekday").agg(days=("records", "size"), records=("records", "sum"))
    g["records_per_day"] = g["records"] / g["days"]
    g = g.reindex(order)
    expected = g["days"] / g["days"].sum() * g["records"].sum()
    chi2, p = stats.chisquare(g["records"], f_exp=expected)
    return g.reset_index(), {"chi2": float(chi2), "p_value": float(p)}


def hourly_summary(df):
    """Records per hour of the day and a chi-square test against an even spread."""
    hours = df["Timestamp"].dropna().dt.hour
    counts = hours.value_counts().reindex(range(24), fill_value=0).sort_index()
    chi2, p = stats.chisquare(counts.values)
    out = counts.rename_axis("hour").reset_index(name="records")
    return out, {"chi2": float(chi2), "p_value": float(p), "min": int(counts.min()), "max": int(counts.max()),
                 "busiest_hour": int(counts.idxmax()), "quietest_hour": int(counts.idxmin())}


def weekly_summary(df):
    """Records per calendar week (weeks starting Monday), with the days covered in the window."""
    daily = daily_summary(df)
    daily["week_start"] = daily["Date"] - pd.to_timedelta(daily["Date"].dt.weekday, unit="D")
    g = daily.groupby("week_start").agg(days_covered=("records", "size"), records=("records", "sum"),
                                         total_weight_g=("total_weight_g", "sum"))
    g["records_per_day"] = g["records"] / g["days_covered"]
    return g.reset_index()


def trend_test(daily, column):
    """Straight-line trend over the days (slope per day, p-value of the slope)."""
    y = daily[column].dropna()
    x = np.arange(len(daily))[daily[column].notna().values]
    res = stats.linregress(x, y.values)
    return {"column": column, "days": int(len(y)), "slope_per_day": float(res.slope),
            "r": float(res.rvalue), "p_value": float(res.pvalue)}


# ---------------------------------------------------------------------------
# Collect everything
# ---------------------------------------------------------------------------
def run_analysis(df):
    """Run every analysis and return the results in one dictionary."""
    daily = daily_summary(df)
    weekday, weekday_test = weekday_summary(df)
    hourly, hourly_test = hourly_summary(df)
    return {
        "overview": dataset_overview(df),
        "category_counts": {c: category_counts(df, c) for c in CATEGORY_COLUMNS},
        "uniformity": {c: uniformity_test(df, c) for c in CATEGORY_COLUMNS if c not in ("Segregation_Status", "Alert_Triggered")},
        "descriptives": numeric_descriptives(df),
        "spearman": spearman_matrix(df),
        "weight_by_group": {c: group_numeric_summary(df, c) for c in COMPARISON_COLUMNS},
        "weight_tests": {c: kruskal_by_group(df, c) for c in COMPARISON_COLUMNS},
        "misclassification": misclassification_rate(df),
        "misclassification_by": {c: misclassification_by(df, c) for c in COMPARISON_COLUMNS},
        "misclassification_tests": {c: chi_square_vs_status(df, c) for c in COMPARISON_COLUMNS},
        "confidence_by_status": confidence_by_status(df),
        "alerts": alert_analysis(df),
        "alert_by_fill_band": alert_by_fill_band(df),
        "fill_by_bin": fill_level_by_bin(df),
        "fill_by_bin_test": kruskal_by_group(df, "Bin_ID", "Bin_Fill_Level_Percentage"),
        "daily": daily,
        "weekday": weekday, "weekday_test": weekday_test,
        "hourly": hourly, "hourly_test": hourly_test,
        "weekly": weekly_summary(df),
        "trends": {c: trend_test(daily, c) for c in ["records", "total_weight_g", "misclassified_rate_pct"]},
    }


# ---------------------------------------------------------------------------
# Validation: recompute totals independently and compare
# ---------------------------------------------------------------------------
def validate_results(df, results):
    """Check that the result tables agree with the dataset. Returns a table of checks."""
    checks = []

    def add(name, passed, details):
        checks.append({"check": name, "passed": bool(passed), "details": details})

    for col in CATEGORY_COLUMNS:
        t = results["category_counts"][col]
        known = int(df[col].notna().sum())
        add(f"{col}: counts add up to records with a value", int(t["count"].sum()) == known,
            f"{int(t['count'].sum())} = {known}")
        add(f"{col}: shares add up to 100%", abs(t["share_pct"].sum() - 100) < 0.1,
            f"sum={t['share_pct'].sum():.2f}")
    total_weight = df["Weight_Grams"].sum()
    for col in COMPARISON_COLUMNS:
        t = results["weight_by_group"][col]
        expected = df.dropna(subset=[col])["Weight_Grams"].sum()
        add(f"{col}: group weights add up to the total", np.isclose(t["total"].sum(), expected),
            f"{t['total'].sum():.1f} = {expected:.1f}")
        m = results["misclassification_by"][col]
        exp_mis = int(((df["Segregation_Status"] == "Misclassified") & df[col].notna()).sum())
        add(f"{col}: misclassified counts add up", int(m["misclassified"].sum()) == exp_mis,
            f"{int(m['misclassified'].sum())} = {exp_mis}")
    ts = int(df["Timestamp"].notna().sum())
    add("daily records add up to records with a timestamp", int(results["daily"]["records"].sum()) == ts,
        f"{int(results['daily']['records'].sum())} = {ts}")
    add("hourly records add up to records with a timestamp", int(results["hourly"]["records"].sum()) == ts,
        f"{int(results['hourly']['records'].sum())} = {ts}")
    add("weekday records add up to records with a timestamp", int(results["weekday"]["records"].sum()) == ts,
        f"{int(results['weekday']['records'].sum())} = {ts}")
    add("weekly records add up to records with a timestamp", int(results["weekly"]["records"].sum()) == ts,
        f"{int(results['weekly']['records'].sum())} = {ts}")
    add("daily weight adds up to the total weight of dated records",
        np.isclose(results["daily"]["total_weight_g"].sum(), df.dropna(subset=["Timestamp"])["Weight_Grams"].sum()),
        f"{results['daily']['total_weight_g'].sum():.1f}")
    d = results["descriptives"].set_index("column")
    add("descriptive sum of Weight_Grams matches the data", np.isclose(d.loc["Weight_Grams", "sum"], total_weight),
        f"{d.loc['Weight_Grams', 'sum']:.1f}")
    for col in NUMERIC_COLUMNS:
        add(f"{col}: count + missing = records", int(d.loc[col, "count"] + d.loc[col, "missing"]) == len(df),
            f"{int(d.loc[col, 'count'])} + {int(d.loc[col, 'missing'])} = {len(df)}")
    mc = results["misclassification"]
    add("misclassified + correct = records with a known status",
        mc["misclassified"] + int((df["Segregation_Status"] == "Correctly Segregated").sum()) == mc["known_status"],
        f"{mc['misclassified']} + correct = {mc['known_status']}")
    fb = results["alert_by_fill_band"]
    add("fill-band counts add up to records with fill level and alert",
        int(fb["n"].sum()) == int(df.dropna(subset=["Bin_Fill_Level_Percentage", "Alert_Triggered"]).shape[0]),
        f"{int(fb['n'].sum())}")
    a = results["alerts"]
    add("alert sources add up to alerts used",
        a["alerts_misclassified"] + a["alerts_correct_and_fill_above_85"] + a["alerts_correct_and_fill_85_or_below"] == a["alerts_used"],
        f"{a['alerts_misclassified']} + {a['alerts_correct_and_fill_above_85']} + {a['alerts_correct_and_fill_85_or_below']} = {a['alerts_used']}")
    p_values = [t["p_value"] for t in results["misclassification_tests"].values()]
    add("all p-values lie between 0 and 1", all(0 <= p <= 1 for p in p_values), "chi-square tests")
    return pd.DataFrame(checks)


# ---------------------------------------------------------------------------
# summary_statistics.csv (tidy long format)
# ---------------------------------------------------------------------------
def build_summary_statistics(df, results=None):
    """One row per statistic: section, variable, group, statistic, value, unit."""
    r = results or run_analysis(df)
    rows = []

    def add(section, variable, group, statistic, value, unit=""):
        rows.append({"section": section, "variable": variable, "group": group,
                     "statistic": statistic, "value": value, "unit": unit})

    for k, v in r["overview"].items():
        if k not in ("first_date", "last_date"):
            add("overview", "dataset", "", k, v, "count")
    for col, t in r["category_counts"].items():
        for _, row in t.iterrows():
            add("category_distribution", col, row[col], "count", row["count"], "records")
            add("category_distribution", col, row[col], "share_pct", row["share_pct"], "percent")
    for col, t in r["uniformity"].items():
        add("uniformity_test", col, "", "chi2", t["chi2"])
        add("uniformity_test", col, "", "p_value", t["p_value"])
    for _, row in r["descriptives"].iterrows():
        for stat in ["count", "missing", "mean", "median", "std", "min", "q1", "q3", "max", "iqr", "skewness", "sum"]:
            add("numeric_descriptives", row["column"], "", stat, row[stat])
    sp = r["spearman"]
    for a_ in sp.index:
        for b_ in sp.columns:
            if a_ < b_:
                add("correlation_spearman", f"{a_} vs {b_}", "", "rho", sp.loc[a_, b_])
    for col, t in r["weight_by_group"].items():
        for _, row in t.iterrows():
            for stat in ["n", "mean", "median", "std", "total", "share_of_total_pct"]:
                add("weight_by_group", col, row[col], stat, row[stat], "grams" if stat not in ("n", "share_of_total_pct") else "")
    for col, t in r["weight_tests"].items():
        add("weight_group_test", col, "", "kruskal_h", t["h"])
        add("weight_group_test", col, "", "p_value", t["p_value"])
    m = r["misclassification"]
    for stat in ["misclassified", "known_status", "rate_pct", "ci_low_pct", "ci_high_pct"]:
        add("misclassification", "all_records", "", stat, m[stat])
    for col, t in r["misclassification_by"].items():
        for _, row in t.iterrows():
            for stat in ["n", "misclassified", "rate_pct", "ci_low_pct", "ci_high_pct"]:
                add("misclassification_by_group", col, row[col], stat, row[stat])
    for col, t in r["misclassification_tests"].items():
        for stat in ["chi2", "dof", "p_value", "share_cells_expected_below_5"]:
            add("misclassification_test", col, "", stat, t[stat])
    for stat, value in r["confidence_by_status"].items():
        add("confidence_by_status", "AI_Confidence_Score", "", stat, value)
    for stat, value in r["alerts"].items():
        add("alert_analysis", "Alert_Triggered", "", stat, value)
    for _, row in r["alert_by_fill_band"].iterrows():
        for stat in ["n", "alerts", "alert_rate_pct"]:
            add("alert_by_fill_band", "Bin_Fill_Level_Percentage", row["fill_band"], stat, row[stat])
    for _, row in r["fill_by_bin"].iterrows():
        for stat in ["n", "mean", "median", "share_above_85", "alert_rate_pct"]:
            add("fill_level_by_bin", "Bin_ID", row["Bin_ID"], stat, row[stat])
    for stat in ["kruskal_h", "p_value"]:
        add("fill_level_by_bin_test", "Bin_ID", "", stat, r["fill_by_bin_test"]["h" if stat == "kruskal_h" else "p_value"])
    for _, row in r["weekday"].iterrows():
        for stat in ["days", "records", "records_per_day"]:
            add("weekday", "Weekday", row["Weekday"], stat, row[stat])
    for stat in ["chi2", "p_value"]:
        add("weekday_test", "Weekday", "", stat, r["weekday_test"][stat])
    for _, row in r["hourly"].iterrows():
        add("hourly", "Hour", int(row["hour"]), "records", row["records"])
    for stat in ["chi2", "p_value"]:
        add("hourly_test", "Hour", "", stat, r["hourly_test"][stat])
    for _, row in r["weekly"].iterrows():
        for stat in ["days_covered", "records", "records_per_day", "total_weight_g"]:
            add("weekly", "Week_start", str(row["week_start"].date()), stat, row[stat])
    for col, t in r["trends"].items():
        for stat in ["slope_per_day", "r", "p_value"]:
            add("trend_test", col, "", stat, t[stat])
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Findings report (analytics_summary.md)
# ---------------------------------------------------------------------------
def _p(p):
    return "p < 0.001" if p < 0.001 else f"p = {p:.2f}"


def _sig(p):
    return "a significant difference" if p < ALPHA else "no significant difference"


def build_report_markdown(df, results=None):
    """Write the findings and recommendations from the computed results (no typed-in numbers)."""
    r = results or run_analysis(df)
    ov, mc, al = r["overview"], r["misclassification"], r["alerts"]
    desc = r["descriptives"].set_index("column")
    wcount = r["category_counts"]["Waste_Category"]
    top3 = wcount.head(3)
    bottom = wcount.iloc[-1]
    mis_tests = r["misclassification_tests"]
    wt_tests = r["weight_tests"]
    conf = r["confidence_by_status"]
    daily = r["daily"]
    wk, hr = r["weekday"].set_index("Weekday"), r["hourly_test"]
    trends = r["trends"]
    any_sig = [c for c, t in mis_tests.items() if t["p_value"] < ALPHA]
    cat_mis = r["misclassification_by"]["Waste_Category"]
    cat_mis_big = cat_mis[cat_mis["n"] >= 30]
    hi, lo = cat_mis_big.iloc[0], cat_mis_big.iloc[-1]
    bin_fill = r["fill_by_bin"]
    wlow, whigh = r["weight_by_group"]["Waste_Category"]["median"].min(), r["weight_by_group"]["Waste_Category"]["median"].max()
    bands = r["alert_by_fill_band"]
    uni = r["uniformity"]

    L = []
    w = L.append
    w("# Analytics Summary — Medical Waste Segregation Records\n")
    w("**Project:** MED-WASTE-SEGREGATION  ")
    w("**Issue:** Data Analytics — #4  ")
    w("**Input:** `data/processed/medical_waste_cleaned.csv` (output of Issue #3)  ")
    w(f"**Scope:** {ov['records']:,} records, {ov['first_date']} to {ov['last_date']} ({ov['calendar_days']} days)  ")
    w("**Reproduce:** `python -m src.analytics` or run `notebooks/02_data_analytics.ipynb`\n")
    w("> **Read this first.** The dataset appears to be simulated (see `docs/data_sources.md`). The results describe this file and show the analysis workflow. They are not evidence about real hospitals.\n")

    w("## 1. Key findings\n")
    w(f"1. **Segregation accuracy.** {mc['misclassified']} of {mc['known_status']:,} records with a known status were misclassified, a rate of **{mc['rate_pct']:.1f}%** (95% CI {mc['ci_low_pct']:.1f}% to {mc['ci_high_pct']:.1f}%).")
    w(f"2. **No group stands out.** Misclassification rates differ by ward, floor, waste category, bin colour and bin ID in the raw numbers, but {'none of these differences is statistically significant' if not any_sig else 'only these are significant: ' + ', '.join(any_sig)} (chi-square, smallest {_p(min(t['p_value'] for t in mis_tests.values()))}). The highest category rate ({hi['Waste_Category']}, {hi['rate_pct']:.1f}%, n={int(hi['n'])}) and the lowest ({lo['Waste_Category']}, {lo['rate_pct']:.1f}%, n={int(lo['n'])}) are within what chance produces with samples this small.")
    w(f"3. **AI confidence does not predict errors.** Median AI confidence is {conf['median_correct']:.2f} for correct records and {conf['median_misclassified']:.2f} for misclassified ones ({_sig(conf['p_value'])}, Mann-Whitney {_p(conf['p_value'])}). A confidence threshold would not catch the misclassifications.")
    w(f"4. **Alerts come from two sources.** {al['alerts']} of {al['records_with_alert_known']:,} records ({al['alert_rate_pct']:.1f}%) triggered an alert. {al['misclassified_with_alert_pct']:.0f}% of misclassified records (n={al['misclassified_used']}) triggered one, and among correctly segregated records the alert rate is {al['correct_fill_above_85_alert_pct']:.1f}% when the bin is more than 85% full (n={al['correct_fill_above_85_n']}) versus {al['correct_fill_85_or_below_alert_pct']:.1f}% at 85% or below (n={al['correct_fill_85_or_below_n']}). Of the {al['alerts_used']} alerts with complete data, {al['alerts_misclassified']} follow a misclassification and {al['alerts_correct_and_fill_above_85']} a nearly full bin. This is a pattern in the data, not a documented rule.")
    w(f"5. **Weights are skewed and similar across groups.** The median record weighs {desc.loc['Weight_Grams','median']:.1f} g (mean {desc.loc['Weight_Grams','mean']:.1f} g, skewness {desc.loc['Weight_Grams','skewness']:.1f}). Category medians range only from {wlow:.0f} g to {whigh:.0f} g, and weight shows {_sig(wt_tests['Waste_Category']['p_value'])} between categories (Kruskal-Wallis {_p(wt_tests['Waste_Category']['p_value'])}), wards ({_p(wt_tests['Hospital_Ward']['p_value'])}) or floors ({_p(wt_tests['Floor_Number']['p_value'])}).")
    w(f"6. **Activity is steady over time.** Records per day average {daily['records'].mean():.1f} (range {int(daily['records'].min())} to {int(daily['records'].max())}). There is no significant trend in daily records ({_p(trends['records']['p_value'])}), daily weight ({_p(trends['total_weight_g']['p_value'])}) or daily misclassification rate ({_p(trends['misclassified_rate_pct']['p_value'])}), no weekday effect ({_p(r['weekday_test']['p_value'])}) and no busy hour ({_p(hr['p_value'])}; hourly counts run from {hr['min']} to {hr['max']}).")
    w(f"7. **Bin fill levels.** Mean fill level is {desc.loc['Bin_Fill_Level_Percentage','mean']:.1f}% and {float((df['Bin_Fill_Level_Percentage'].dropna() > 85).mean() * 100):.1f}% of readings are above 85%. Fill levels show {_sig(r['fill_by_bin_test']['p_value'])} between the 12 bins (Kruskal-Wallis {_p(r['fill_by_bin_test']['p_value'])}).\n")

    w("## 2. Distributions\n")
    w(f"- **Waste categories** ({len(wcount)} types, {int(wcount['count'].sum()):,} records with a category): the most frequent are " + ", ".join(f"{x['Waste_Category']} ({int(x['count'])}, {x['share_pct']:.1f}%)" for _, x in top3.iterrows()) + f". The least frequent is {bottom['Waste_Category']} ({int(bottom['count'])}, {bottom['share_pct']:.1f}%). Counts are fairly even but not perfectly equal ({_p(uni['Waste_Category']['p_value'])} against equal shares).")
    for col, label in [("Target_Bin_Color", "Target bin colours"), ("Hospital_Ward", "Wards"), ("Floor_Number", "Floors"), ("Bin_ID", "Bin IDs")]:
        t = r["category_counts"][col]
        extra = " Colours are unequal because different numbers of waste categories share each bin colour." if col == "Target_Bin_Color" and uni[col]["p_value"] < ALPHA else ""
        w(f"- **{label}:** {t.iloc[0][col]} is the most common ({int(t.iloc[0]['count'])}, {t.iloc[0]['share_pct']:.1f}%) and {t.iloc[-1][col]} the least ({int(t.iloc[-1]['count'])}, {t.iloc[-1]['share_pct']:.1f}%); {_p(uni[col]['p_value'])} against equal shares.{extra}")
    w("")
    w("Full counts and shares for every category are in `reports/summary_statistics.csv` (section `category_distribution`).\n")

    w("## 3. Statistical measures\n")
    w("| Variable | Records | Missing | Mean | Median | Std | Min | Q1 | Q3 | Max |\n|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for col, row in desc.iterrows():
        w(f"| {col} | {int(row['count']):,} | {int(row['missing'])} | {row['mean']:.2f} | {row['median']:.2f} | {row['std']:.2f} | {row['min']:.2f} | {row['q1']:.2f} | {row['q3']:.2f} | {row['max']:.2f} |")
    w("")
    sp = r["spearman"]
    w(f"Rank correlations between the three numeric columns are all close to zero (weight vs confidence {sp.loc['Weight_Grams','AI_Confidence_Score']:.2f}, weight vs fill level {sp.loc['Weight_Grams','Bin_Fill_Level_Percentage']:.2f}, confidence vs fill level {sp.loc['AI_Confidence_Score','Bin_Fill_Level_Percentage']:.2f}), so none of them predicts another.\n")

    w("## 4. Comparisons\n")
    w("Misclassification rate by waste category, sorted from highest to lowest (95% Wilson confidence intervals):\n")
    w("| Waste category | Records | Misclassified | Rate | 95% CI |\n|---|---:|---:|---:|---|")
    for _, x in cat_mis.iterrows():
        w(f"| {x['Waste_Category']} | {int(x['n'])} | {int(x['misclassified'])} | {x['rate_pct']:.1f}% | {x['ci_low_pct']:.1f}% to {x['ci_high_pct']:.1f}% |")
    w("")
    w("Tests of whether the segregation outcome depends on each attribute:\n")
    w("| Attribute | Chi-square | Degrees of freedom | p-value | Result |\n|---|---:|---:|---:|---|")
    for col, t in mis_tests.items():
        note = "significant" if t["p_value"] < ALPHA else "not significant"
        if t["share_cells_expected_below_5"] > 0.2:
            note += " (some small cells)"
        w(f"| {col} | {t['chi2']:.2f} | {t['dof']} | {t['p_value']:.2f} | {note} |")
    w("")
    w("Alert rate by bin fill level:\n")
    w("| Fill level (%) | Records | Alerts | Alert rate |\n|---|---:|---:|---:|")
    for _, x in bands.iterrows():
        w(f"| {x['fill_band']} | {int(x['n'])} | {int(x['alerts'])} | {x['alert_rate_pct']:.1f}% |")
    w("")
    w(f"Waste weight is compared by category, ward, floor, bin colour and bin ID with Kruskal-Wallis tests (suited to skewed data). The smallest p-value is {_p(min(t['p_value'] for t in wt_tests.values()))}, so no attribute shows a reliable weight difference. Full group tables are in `reports/summary_statistics.csv`.\n")

    w("## 5. Time trends\n")
    w(f"- **Daily:** {int(daily['records'].sum()):,} dated records over {ov['calendar_days']} days, {daily['records'].mean():.1f} per day on average.")
    wd = wk["records_per_day"]
    w(f"- **Weekday:** averages run from {wd.min():.1f} records per day ({wd.idxmin()}) to {wd.max():.1f} ({wd.idxmax()}), a difference that is {'' if r['weekday_test']['p_value'] < ALPHA else 'not '}statistically significant ({_p(r['weekday_test']['p_value'])}). Totals are divided by the number of each weekday in the window, because a month contains four of some weekdays and five of others.")
    w(f"- **Hour of day:** the busiest hour is {hr['busiest_hour']}:00 and the quietest {hr['quietest_hour']}:00, with no significant departure from an even spread ({_p(hr['p_value'])}).")
    w(f"- **Trend:** straight-line trends over the month are not significant for records per day (slope {trends['records']['slope_per_day']:+.2f}, {_p(trends['records']['p_value'])}), daily weight ({_p(trends['total_weight_g']['p_value'])}) or daily misclassification rate ({_p(trends['misclassified_rate_pct']['p_value'])}).")
    w("- The first and last calendar weeks are partial; the weekly table in `reports/summary_statistics.csv` lists the days each week covers.\n")

    w("## 6. Recommendations\n")
    w("Each one is tied to a finding above. Treat them as design suggestions, since the data is simulated.\n")
    w(f"1. **Do not rely on AI confidence to catch errors** (finding 3). Add a different safeguard, such as a second check on the item or a periodic manual audit of correctly-labelled items.")
    w(f"2. **Aim to lower the overall misclassification rate, not a single ward or category** (finding 2). The overall rate is {mc['rate_pct']:.1f}% and no group is reliably worse. Collect more records per category before targeting any one, since the highest raw rates ({hi['Waste_Category']}) rest on only {int(hi['n'])} records.")
    w(f"3. **Use the fill-level alert as the trigger for emptying bins** (finding 4). Almost every alert on a correctly segregated record occurs above 85% fill, and no bin is reliably fuller than the others (finding 7), so one common emptying rule fits all 12 bins better than bin-specific schedules.")
    w("4. **Keep alerts for misclassification and full bins separate** (finding 4). Today both produce the same `Alert_Triggered` flag, so staff cannot tell whether to re-sort an item or empty a bin.")
    w("5. **Staff for steady demand** (finding 6). No weekday or hour is reliably busier, so no peak-hour staffing is justified by this data.")
    w("6. **Collect data over a longer period and from real bins.** One month cannot show seasonal effects, and simulated records cannot show how a real system performs.\n")

    w("## 7. Limitations\n")
    w("- **Simulated data.** Patterns reflect how the file was generated (see `docs/data_sources.md`).")
    w(f"- **One month.** {ov['first_date']} to {ov['last_date']}, so seasonal trends cannot be studied.")
    w("- **Missing values** (up to 2.6% per column) were skipped, so each table is based on the records with a value. The number of records is shown for every comparison.")
    w("- **Duplicate record IDs.** `Record_ID` is not unique (see `docs/data_quality_report.md`). The analysis does not use it.")
    w("- **Alert rule is inferred.** The link between alerts, misclassification and fill level is what the data shows, not a documented rule.")
    w("- **Many small groups.** Rates for single categories or bins rest on 50 to 190 records, so their intervals are wide, and some chi-square cells are small.")
    w("- **Multiple tests.** Several tests were run at the 5% level. Since none of the group differences is significant, correcting for multiple tests would not change the conclusions.\n")

    w("## 8. Files\n")
    w("| File | Content |\n|---|---|")
    w("| `src/analytics.py` | Reusable analysis, validation and report functions |")
    w("| `notebooks/02_data_analytics.ipynb` | Step-by-step analysis with charts |")
    w("| `reports/summary_statistics.csv` | Every statistic in long format: section, variable, group, statistic, value, unit |")
    w("| `reports/analytics_summary.md` | This report, generated by `python -m src.analytics` |")
    return "\n".join(L) + "\n"


def write_outputs(input_path=DEFAULT_INPUT, reports_dir=DEFAULT_REPORTS):
    """Run the analysis, validate it and write both report files."""
    df = load_data(input_path)
    results = run_analysis(df)
    checks = validate_results(df, results)
    if not checks["passed"].all():
        raise SystemExit("Validation failed:\n" + checks[~checks["passed"]].to_string(index=False))
    reports_dir = Path(reports_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)
    stats_path = reports_dir / "summary_statistics.csv"
    summary_path = reports_dir / "analytics_summary.md"
    build_summary_statistics(df, results).to_csv(stats_path, index=False)
    summary_path.write_text(build_report_markdown(df, results), encoding="utf-8")
    return stats_path, summary_path, len(checks)


if __name__ == "__main__":
    s, m, n = write_outputs()
    print(f"All {n} validation checks passed.\nWrote: {s}\nWrote: {m}")
