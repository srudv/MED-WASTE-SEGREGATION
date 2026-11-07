"""Reusable chart generation for the cleaned MedWaste AI segregation records.

Every chart takes its numbers from src/analytics.py, so the charts always agree with
reports/summary_statistics.csv. Charts are exported as PNG and SVG to reports/figures/.

Run from the repository root:

    python -m src.visualization
"""
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter

from src import analytics as an

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = an.DEFAULT_INPUT
DEFAULT_OUT = ROOT / "reports/figures"
DEFAULT_SUMMARY = ROOT / "reports/visualization_summary.md"

INK, GREY, LIGHT, ACCENT = "#1f1f1f", "#8c8c8c", "#d4d4d4", "#d62728"
FOOTER = "Simulated dataset, October 2026."

plt.rcParams.update({
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.titlesize": 13, "axes.titleweight": "bold", "axes.labelsize": 10.5,
    "font.size": 10, "figure.dpi": 100, "svg.hashsalt": "medwaste-segregation",
})


def load_visualization_data(path=DEFAULT_DATA):
    """Load the cleaned dataset (same loader and checks as the analytics module)."""
    return an.load_data(path)


def _footer(fig, text):
    fig.text(0.01, 0.005, f"{FOOTER} {text}", fontsize=8, color=GREY, ha="left", va="bottom")


def _finish(fig, note):
    fig.tight_layout(rect=(0, 0.035, 1, 1))
    _footer(fig, note)
    return fig


# ---------------------------------------------------------------------------
# The charts. Each returns a Matplotlib figure.
# ---------------------------------------------------------------------------
def chart_waste_category_counts(df, results):
    t = results["category_counts"]["Waste_Category"].sort_values("count")
    fig, ax = plt.subplots(figsize=(9, 7))
    bars = ax.barh(t["Waste_Category"], t["count"], color=INK)
    ax.bar_label(bars, labels=[f"{int(c)}  ({s:.1f}%)" for c, s in zip(t["count"], t["share_pct"])],
                 padding=4, fontsize=8.5)
    ax.set(title="Records per waste category", xlabel="Number of records", ylabel="")
    ax.set_xlim(0, t["count"].max() * 1.18)
    return _finish(fig, f"n = {int(t['count'].sum()):,} records with a waste category.")


def chart_ward_distribution(df, results):
    t = results["category_counts"]["Hospital_Ward"].sort_values("count")
    fig, ax = plt.subplots(figsize=(8, 4.8))
    bars = ax.barh(t["Hospital_Ward"], t["count"], color=INK)
    ax.bar_label(bars, labels=[f"{int(c)}  ({s:.1f}%)" for c, s in zip(t["count"], t["share_pct"])],
                 padding=4, fontsize=9)
    ax.set(title="Records per hospital ward", xlabel="Number of records", ylabel="")
    ax.set_xlim(0, t["count"].max() * 1.2)
    return _finish(fig, f"n = {int(t['count'].sum()):,} records with a ward.")


def chart_weight_distribution(df, results):
    w = df["Weight_Grams"].dropna()
    bins = np.logspace(np.log10(w.min()), np.log10(w.max()), 40)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.hist(w, bins=bins, color=INK, edgecolor="white", linewidth=0.4)
    ax.set_xscale("log")
    ticks = [t for t in (10, 30, 100, 300, 1000, 3000) if w.min() * 0.8 <= t <= w.max() * 1.3]
    ax.set_xticks(ticks)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:,.0f}"))
    ax.axvline(w.median(), color=ACCENT, lw=1.8, label=f"Median {w.median():.0f} g")
    ax.axvline(w.mean(), color=GREY, lw=1.8, ls="--", label=f"Mean {w.mean():.0f} g")
    ax.set(title="Distribution of waste weight per record", xlabel="Weight per record (grams, log scale)",
           ylabel="Number of records")
    ax.legend(frameon=False)
    return _finish(fig, f"n = {len(w):,} records with a weight. The log scale spreads out a long right tail.")


def chart_weight_by_category(df, results):
    t = results["weight_by_group"]["Waste_Category"].sort_values("median")
    order = list(t["Waste_Category"])
    data = [df.loc[df["Waste_Category"] == c, "Weight_Grams"].dropna() for c in order]
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.boxplot(data, showfliers=False, medianprops={"color": ACCENT, "linewidth": 1.8},
               boxprops={"color": INK}, whiskerprops={"color": INK}, capprops={"color": INK})
    ax.set_xticks(range(1, len(order) + 1))
    ax.set_xticklabels(order, rotation=65, ha="right")
    ax.set(title="Weight per record by waste category (sorted by median)", ylabel="Weight per record (grams)",
           xlabel="")
    p = results["weight_tests"]["Waste_Category"]["p_value"]
    return _finish(fig, f"Boxes show the middle 50% of records, red line = median, outliers hidden. "
                        f"Categories do not differ significantly (Kruskal-Wallis p = {p:.2f}).")


def chart_misclassification_by_category(df, results):
    m = results["misclassification_by"]["Waste_Category"].sort_values("rate_pct")
    overall = results["misclassification"]
    fig, ax = plt.subplots(figsize=(9, 7))
    err = [m["rate_pct"] - m["ci_low_pct"], m["ci_high_pct"] - m["rate_pct"]]
    ax.errorbar(m["rate_pct"], range(len(m)), xerr=err, fmt="o", color=INK, ecolor=GREY, capsize=3)
    ax.axvline(overall["rate_pct"], color=ACCENT, ls="--", lw=1.6, label=f"Overall rate {overall['rate_pct']:.1f}%")
    ax.set_yticks(range(len(m)))
    ax.set_yticklabels(m["Waste_Category"])
    ax.set(title="Misclassification rate by waste category", xlabel="Records misclassified (%), with 95% confidence interval",
           ylabel="")
    ax.legend(frameon=False, loc="lower right")
    p = min(t["p_value"] for t in results["misclassification_tests"].values())
    return _finish(fig, f"n = {overall['known_status']:,} records with a known status. Every interval overlaps the overall rate; "
                        f"no attribute shows a significant difference (smallest p = {p:.2f}).")


def chart_alert_rate_by_fill(df, results):
    b = results["alert_by_fill_band"]
    a = results["alerts"]
    fig, ax = plt.subplots(figsize=(9, 5))
    colors = [ACCENT if lab.startswith(("over 85", "over 90", "over 95")) else INK for lab in b["fill_band"]]
    bars = ax.bar(b["fill_band"], b["alert_rate_pct"], color=colors)
    ax.bar_label(bars, labels=[f"{r:.0f}%\nn={int(n)}" for r, n in zip(b["alert_rate_pct"], b["n"])], fontsize=8.5, padding=3)
    ax.set(title="Alert rate by bin fill level", xlabel="Bin fill level (%)", ylabel="Records that triggered an alert (%)")
    ax.set_ylim(0, 118)
    note = f"n = {int(b['n'].sum()):,} records with fill level and alert."
    if a["alerts_correct_and_fill_85_or_below"] == 0:
        note += " At 85% fill or below, alerts come only from misclassified items."
    return _finish(fig, note)


def chart_daily_records(df, results):
    d = results["daily"].copy()
    d["rolling"] = d["records"].rolling(7, min_periods=4).mean()
    fig, ax = plt.subplots(figsize=(10, 4.6))
    ax.bar(d["Date"], d["records"], color=LIGHT, label="Records per day", width=0.85)
    ax.plot(d["Date"], d["rolling"], color=INK, lw=2.2, label="7-day average")
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    ax.set(title="Records per day", xlabel="Date", ylabel="Number of records")
    ax.set_ylim(0, d["records"].max() * 1.25)
    ax.legend(frameon=False, loc="upper right", ncol=2)
    tr = results["trends"]["records"]
    return _finish(fig, f"n = {int(d['records'].sum()):,} dated records over {len(d)} days. "
                        f"Linear trend: {tr['slope_per_day']:+.2f} records/day (p = {tr['p_value']:.2f}, not significant).")


def chart_weekday_and_hour(df, results):
    wk, hr = results["weekday"], results["hourly"]
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6), gridspec_kw={"width_ratios": [1, 1.6]})
    axes[0].bar(wk["Weekday"].str[:3], wk["records_per_day"], color=INK)
    axes[0].axhline(results["daily"]["records"].mean(), color=ACCENT, ls="--", lw=1.4, label="Daily average")
    axes[0].set(title="Average records per day, by weekday", ylabel="Records per day")
    axes[0].set_ylim(0, wk["records_per_day"].max() * 1.28)
    axes[0].legend(frameon=False, loc="upper right")
    axes[1].bar(hr["hour"], hr["records"], color=INK)
    axes[1].set_xticks(range(0, 24, 2))
    axes[1].set(title="Records by hour of day", xlabel="Hour of day (24-hour clock)", ylabel="Number of records")
    return _finish(fig, f"Weekday totals are divided by the number of each weekday in the month. "
                        f"No weekday effect (p = {results['weekday_test']['p_value']:.2f}) and no busy hour (p = {results['hourly_test']['p_value']:.2f}).")


CHARTS = [
    ("01_waste_category_counts", chart_waste_category_counts),
    ("02_ward_distribution", chart_ward_distribution),
    ("03_weight_distribution", chart_weight_distribution),
    ("04_weight_by_category", chart_weight_by_category),
    ("05_misclassification_by_category", chart_misclassification_by_category),
    ("06_alert_rate_by_fill_level", chart_alert_rate_by_fill),
    ("07_daily_records", chart_daily_records),
    ("08_weekday_and_hour", chart_weekday_and_hour),
]


# ---------------------------------------------------------------------------
# Export and validation
# ---------------------------------------------------------------------------
def _save(fig, path, ext):
    meta = {"Date": None} if ext == "svg" else {"Software": None}
    fig.savefig(path, dpi=150, bbox_inches="tight", format=ext, metadata=meta, facecolor="white")


def generate_all_charts(data=None, output_dir=DEFAULT_OUT, formats=("png", "svg"), results=None, show=False):
    """Draw every chart and export it in each format. Returns the list of written paths."""
    df = load_visualization_data() if data is None else data
    results = results or an.run_analysis(df)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for stem, func in CHARTS:
        fig = func(df, results)
        for ext in formats:
            path = output_dir / f"{stem}.{ext}"
            _save(fig, path, ext)
            paths.append(path)
        if show:
            plt.show()
        plt.close(fig)
    return paths


def validate_exports(paths):
    """Check that every exported file exists, is not empty and is a valid PNG or SVG."""
    import xml.etree.ElementTree as ET
    rows = []
    for p in map(Path, paths):
        ok, detail = p.exists() and p.stat().st_size > 0, "exists"
        if ok and p.suffix == ".png":
            ok = p.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
            detail = "valid PNG header"
        elif ok and p.suffix == ".svg":
            try:
                ok = ET.parse(p).getroot().tag.endswith("svg")
                detail = "valid SVG XML"
            except ET.ParseError:
                ok, detail = False, "SVG does not parse"
        rows.append({"file": p.name, "size_kb": round(p.stat().st_size / 1024, 1) if p.exists() else 0,
                     "passed": bool(ok), "details": detail})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# reports/visualization_summary.md
# ---------------------------------------------------------------------------
def build_summary_markdown(df, results=None):
    r = results or an.run_analysis(df)
    ov, mc, al = r["overview"], r["misclassification"], r["alerts"]
    d = r["descriptives"].set_index("column")
    cats = r["category_counts"]["Waste_Category"]
    wards = r["category_counts"]["Hospital_Ward"]
    mis_cat = r["misclassification_by"]["Waste_Category"]
    big = mis_cat[mis_cat["n"] >= 30]
    daily, wk, hr = r["daily"], r["weekday"].set_index("Weekday")["records_per_day"], r["hourly_test"]
    wt = r["weight_tests"]["Waste_Category"]
    L = []
    w = L.append
    w("# Visualization Summary — Medical Waste Segregation Records\n")
    w("**Project:** MED-WASTE-SEGREGATION  ")
    w("**Issue:** Data Visualization — #5  ")
    w("**Input:** `data/processed/medical_waste_cleaned.csv` (Issue #3), numbers from `src/analytics.py` (Issue #4)  ")
    w(f"**Scope:** {ov['records']:,} records, {ov['first_date']} to {ov['last_date']}\n")
    w("> The dataset appears to be simulated (see `docs/data_sources.md`). The charts describe this file and demonstrate the workflow. They are not evidence about real hospitals.\n")
    w("## Charts created\n")
    w(f"Eight charts are drawn by `src/visualization.py` and `notebooks/03_data_visualization.ipynb`. Each is exported as PNG and SVG to `reports/figures/` ({len(CHARTS) * 2} files).\n")
    w("| # | File | Chart | What it shows |\n|---|---|---|---|")
    w(f"| 1 | `01_waste_category_counts` | Horizontal bars | Records per waste category: {int(cats['count'].min())} to {int(cats['count'].max())} records per category, an even spread |")
    w(f"| 2 | `02_ward_distribution` | Horizontal bars | Records per ward: {wards.iloc[-1]['Hospital_Ward']} lowest ({int(wards.iloc[-1]['count'])}), {wards.iloc[0]['Hospital_Ward']} highest ({int(wards.iloc[0]['count'])}) |")
    w(f"| 3 | `03_weight_distribution` | Histogram, log scale | Weight per record is strongly right-skewed: median {d.loc['Weight_Grams','median']:.0f} g, mean {d.loc['Weight_Grams','mean']:.0f} g |")
    w(f"| 4 | `04_weight_by_category` | Box plot | Weight spread per category; no significant difference (p = {wt['p_value']:.2f}) |")
    w(f"| 5 | `05_misclassification_by_category` | Dot plot with 95% intervals | Misclassification rate per category against the overall {mc['rate_pct']:.1f}% |")
    w(f"| 6 | `06_alert_rate_by_fill_level` | Bars | Alert rate for each bin fill band; alerts jump to about 100% above 85% fill |")
    w(f"| 7 | `07_daily_records` | Bars and 7-day line | Records per day ({int(daily['records'].min())} to {int(daily['records'].max())}), no significant trend |")
    w(f"| 8 | `08_weekday_and_hour` | Two bar charts | Average records per weekday ({wk.min():.1f} to {wk.max():.1f}) and per hour ({hr['min']} to {hr['max']}); no significant pattern |\n")
    w("## How the charts were designed\n")
    w("- **Honest scales.** Bars start at zero. The weight histogram uses a log axis because weights are strongly right-skewed, and says so on the chart.")
    w("- **Uncertainty is shown.** The misclassification chart draws 95% Wilson confidence intervals, since many categories have only 55 to 90 records.")
    w("- **Sample sizes are on the charts.** Each chart carries a footer with the number of records and the data caveat.")
    w("- **Fair weekday comparison.** Weekday totals are divided by the number of each weekday in the month.")
    w("- **Outliers.** The category box plot hides outliers for readability; the histogram shows the full range.")
    w("- **Colour.** Dark grey is the default; red marks the item the reader should compare against (a median, the overall rate, or bins above 85% fill).")
    w("- **No fabricated views.** Missing values are skipped, never plotted as zero.\n")
    w("## Key readings\n")
    w(f"- **Segregation accuracy:** {mc['rate_pct']:.1f}% of records were misclassified. Every category's interval overlaps this rate, so no category is reliably worse (chart 5).")
    w(f"- **Alerts:** {al['alerts_misclassified']} alerts follow a misclassification and {al['alerts_correct_and_fill_above_85']} a bin more than 85% full (chart 6).")
    w(f"- **Activity over time:** steady at {daily['records'].mean():.1f} records per day; no busy weekday or hour (charts 7 and 8).")
    w(f"- **Weights:** most records weigh under about {d.loc['Weight_Grams','q3']:.0f} g (75th percentile), with a few heavier items stretching the tail (charts 3 and 4).\n")
    w("## Interpretation limitations\n")
    w("- The data is simulated and covers one month, so seasonal or long-term trends cannot be shown.")
    w("- Differences between categories are within chance. The charts show the raw rates and weights, but they should not be read as rankings.")
    w("- Alert behaviour is a pattern seen in the data, not a documented rule.")
    w("- Records with missing values are left out of the chart that needs the missing field. The footer of each chart gives the number of records used.")
    w("- Correlation does not imply causation.\n")
    w("## Reproduce\n")
    w("```bash\npip install -r requirements.txt\npython -m src.visualization          # writes reports/figures/*.png and *.svg and this summary\njupyter notebook notebooks/03_data_visualization.ipynb\n```\n")
    w("The script and notebook check that every export exists, is not empty and is a valid PNG or SVG.")
    return "\n".join(L) + "\n"


def main():
    plt.switch_backend("Agg")
    df = load_visualization_data()
    results = an.run_analysis(df)
    paths = generate_all_charts(df, results=results)
    checks = validate_exports(paths)
    if not checks["passed"].all():
        raise SystemExit("Export validation failed:\n" + checks[~checks["passed"]].to_string(index=False))
    DEFAULT_SUMMARY.write_text(build_summary_markdown(df, results), encoding="utf-8")
    print(f"Wrote {len(paths)} chart files to {DEFAULT_OUT.relative_to(ROOT)} (all valid)")
    print(f"Wrote {DEFAULT_SUMMARY.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
