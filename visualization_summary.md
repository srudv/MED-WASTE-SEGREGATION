# Visualization Summary — Medical Waste Segregation Records

**Project:** MED-WASTE-SEGREGATION  
**Issue:** Data Visualization — #5  
**Input:** `data/processed/medical_waste_cleaned.csv` (Issue #3), numbers from `src/analytics.py` (Issue #4)  
**Scope:** 1,482 records, 2026-10-01 to 2026-10-30

> The dataset appears to be simulated (see `docs/data_sources.md`). The charts describe this file and demonstrate the workflow. They are not evidence about real hospitals.

## Charts created

Eight charts are drawn by `src/visualization.py` and `notebooks/03_data_visualization.ipynb`. Each is exported as PNG and SVG to `reports/figures/` (16 files).

| # | File | Chart | What it shows |
|---|---|---|---|
| 1 | `01_waste_category_counts` | Horizontal bars | Records per waste category: 57 to 89 records per category, an even spread |
| 2 | `02_ward_distribution` | Horizontal bars | Records per ward: ICU lowest (158), General Ward highest (200) |
| 3 | `03_weight_distribution` | Histogram, log scale | Weight per record is strongly right-skewed: median 201 g, mean 276 g |
| 4 | `04_weight_by_category` | Box plot | Weight spread per category; no significant difference (p = 0.88) |
| 5 | `05_misclassification_by_category` | Dot plot with 95% intervals | Misclassification rate per category against the overall 6.7% |
| 6 | `06_alert_rate_by_fill_level` | Bars | Alert rate for each bin fill band; alerts jump to about 100% above 85% fill |
| 7 | `07_daily_records` | Bars and 7-day line | Records per day (35 to 62), no significant trend |
| 8 | `08_weekday_and_hour` | Two bar charts | Average records per weekday (43.0 to 54.2) and per hour (51 to 75); no significant pattern |

## How the charts were designed

- **Honest scales.** Bars start at zero. The weight histogram uses a log axis because weights are strongly right-skewed, and says so on the chart.
- **Uncertainty is shown.** The misclassification chart draws 95% Wilson confidence intervals, since many categories have only 55 to 90 records.
- **Sample sizes are on the charts.** Each chart carries a footer with the number of records and the data caveat.
- **Fair weekday comparison.** Weekday totals are divided by the number of each weekday in the month.
- **Outliers.** The category box plot hides outliers for readability; the histogram shows the full range.
- **Colour.** Dark grey is the default; red marks the item the reader should compare against (a median, the overall rate, or bins above 85% fill).
- **No fabricated views.** Missing values are skipped, never plotted as zero.

## Key readings

- **Segregation accuracy:** 6.7% of records were misclassified. Every category's interval overlaps this rate, so no category is reliably worse (chart 5).
- **Alerts:** 96 alerts follow a misclassification and 217 a bin more than 85% full (chart 6).
- **Activity over time:** steady at 49.3 records per day; no busy weekday or hour (charts 7 and 8).
- **Weights:** most records weigh under about 333 g (75th percentile), with a few heavier items stretching the tail (charts 3 and 4).

## Interpretation limitations

- The data is simulated and covers one month, so seasonal or long-term trends cannot be shown.
- Differences between categories are within chance. The charts show the raw rates and weights, but they should not be read as rankings.
- Alert behaviour is a pattern seen in the data, not a documented rule.
- Records with missing values are left out of the chart that needs the missing field. The footer of each chart gives the number of records used.
- Correlation does not imply causation.

## Reproduce

```bash
pip install -r requirements.txt
python -m src.visualization          # writes reports/figures/*.png and *.svg and this summary
jupyter notebook notebooks/03_data_visualization.ipynb
```

The script and notebook check that every export exists, is not empty and is a valid PNG or SVG.
