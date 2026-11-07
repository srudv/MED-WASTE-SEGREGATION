# Analytics Summary — Medical Waste Segregation Records

**Project:** MED-WASTE-SEGREGATION  
**Issue:** Data Analytics — #4  
**Input:** `data/processed/medical_waste_cleaned.csv` (output of Issue #3)  
**Scope:** 1,482 records, 2026-10-01 to 2026-10-30 (30 days)  
**Reproduce:** `python -m src.analytics` or run `notebooks/02_data_analytics.ipynb`

> **Read this first.** The dataset appears to be simulated (see `docs/data_sources.md`). The results describe this file and show the analysis workflow. They are not evidence about real hospitals.

## 1. Key findings

1. **Segregation accuracy.** 98 of 1,463 records with a known status were misclassified, a rate of **6.7%** (95% CI 5.5% to 8.1%).
2. **No group stands out.** Misclassification rates differ by ward, floor, waste category, bin colour and bin ID in the raw numbers, but none of these differences is statistically significant (chi-square, smallest p = 0.65). The highest category rate (Syringes, 10.0%, n=70) and the lowest (Chemical Containers, 2.7%, n=74) are within what chance produces with samples this small.
3. **AI confidence does not predict errors.** Median AI confidence is 0.85 for correct records and 0.83 for misclassified ones (no significant difference, Mann-Whitney p = 0.46). A confidence threshold would not catch the misclassifications.
4. **Alerts come from two sources.** 323 of 1,467 records (22.0%) triggered an alert. 100% of misclassified records (n=96) triggered one, and among correctly segregated records the alert rate is 99.5% when the bin is more than 85% full (n=218) versus 0.0% at 85% or below (n=1110). Of the 313 alerts with complete data, 96 follow a misclassification and 217 a nearly full bin. This is a pattern in the data, not a documented rule.
5. **Weights are skewed and similar across groups.** The median record weighs 200.6 g (mean 275.6 g, skewness 4.1). Category medians range only from 170 g to 234 g, and weight shows no significant difference between categories (Kruskal-Wallis p = 0.88), wards (p = 1.00) or floors (p = 0.99).
6. **Activity is steady over time.** Records per day average 49.3 (range 35 to 62). There is no significant trend in daily records (p = 0.25), daily weight (p = 0.69) or daily misclassification rate (p = 0.44), no weekday effect (p = 0.23) and no busy hour (p = 0.42; hourly counts run from 51 to 75).
7. **Bin fill levels.** Mean fill level is 52.8% and 16.4% of readings are above 85%. Fill levels show no significant difference between the 12 bins (Kruskal-Wallis p = 0.17).

## 2. Distributions

- **Waste categories** (19 types, 1,462 records with a category): the most frequent are Contaminated Recyclable Plastics (89, 6.1%), Expired Medications (86, 5.9%), Blades (85, 5.8%). The least frequent is Metallic & Plastic Waste (57, 3.9%). Counts are fairly even but not perfectly equal (p = 0.68 against equal shares).
- **Target bin colours:** Yellow Bin is the most common (318, 21.5%) and White Bin the least (168, 11.3%); p < 0.001 against equal shares. Colours are unequal because different numbers of waste categories share each bin colour.
- **Wards:** General Ward is the most common (200, 13.8%) and ICU the least (158, 10.9%); p = 0.36 against equal shares.
- **Floors:** Floor 3 is the most common (305, 21.0%) and Floor 4 the least (261, 17.9%); p = 0.37 against equal shares.
- **Bin IDs:** BIN_07 is the most common (142, 9.7%) and BIN_01 the least (105, 7.2%); p = 0.27 against equal shares.

Full counts and shares for every category are in `reports/summary_statistics.csv` (section `category_distribution`).

## 3. Statistical measures

| Variable | Records | Missing | Mean | Median | Std | Min | Q1 | Q3 | Max |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Weight_Grams | 1,451 | 31 | 275.57 | 200.60 | 265.94 | 14.30 | 115.80 | 333.40 | 4155.50 |
| AI_Confidence_Score | 1,460 | 22 | 0.84 | 0.85 | 0.08 | 0.70 | 0.77 | 0.92 | 0.99 |
| Bin_Fill_Level_Percentage | 1,457 | 25 | 52.78 | 53.00 | 28.06 | 0.00 | 28.00 | 78.00 | 100.00 |

Rank correlations between the three numeric columns are all close to zero (weight vs confidence -0.01, weight vs fill level 0.05, confidence vs fill level 0.04), so none of them predicts another.

## 4. Comparisons

Misclassification rate by waste category, sorted from highest to lowest (95% Wilson confidence intervals):

| Waste category | Records | Misclassified | Rate | 95% CI |
|---|---:|---:|---:|---|
| Syringes | 70 | 7 | 10.0% | 4.9% to 19.2% |
| Glassware | 82 | 8 | 9.8% | 5.0% to 18.1% |
| Metallic & Plastic Waste | 57 | 5 | 8.8% | 3.8% to 18.9% |
| Urine/Body Fluids | 73 | 6 | 8.2% | 3.8% to 16.8% |
| IV Bags/Tubes | 76 | 6 | 7.9% | 3.7% to 16.2% |
| Paper Wrappers | 64 | 5 | 7.8% | 3.4% to 17.0% |
| Hazardous Chemicals | 78 | 6 | 7.7% | 3.6% to 15.8% |
| Office Trash | 82 | 6 | 7.3% | 3.4% to 15.1% |
| Food Waste | 82 | 6 | 7.3% | 3.4% to 15.1% |
| Expired Medications | 83 | 6 | 7.2% | 3.4% to 14.9% |
| Anatomical Waste | 71 | 5 | 7.0% | 3.0% to 15.4% |
| Needles | 72 | 5 | 6.9% | 3.0% to 15.2% |
| Cotton Swabs | 73 | 4 | 5.5% | 2.2% to 13.3% |
| Used Bandages | 74 | 4 | 5.4% | 2.1% to 13.1% |
| Surgical Waste | 80 | 4 | 5.0% | 2.0% to 12.2% |
| Non-Infectious Waste | 82 | 4 | 4.9% | 1.9% to 11.9% |
| Blades | 84 | 4 | 4.8% | 1.9% to 11.6% |
| Contaminated Recyclable Plastics | 87 | 3 | 3.4% | 1.2% to 9.7% |
| Chemical Containers | 74 | 2 | 2.7% | 0.7% to 9.3% |

Tests of whether the segregation outcome depends on each attribute:

| Attribute | Chi-square | Degrees of freedom | p-value | Result |
|---|---:|---:|---:|---|
| Waste_Category | 8.79 | 18 | 0.96 | not significant (some small cells) |
| Hospital_Ward | 1.84 | 7 | 0.97 | not significant |
| Floor_Number | 1.83 | 4 | 0.77 | not significant |
| Target_Bin_Color | 1.90 | 5 | 0.86 | not significant |
| Bin_ID | 8.72 | 11 | 0.65 | not significant |

Alert rate by bin fill level:

| Fill level (%) | Records | Alerts | Alert rate |
|---|---:|---:|---:|
| 0 to 50 | 677 | 41 | 6.1% |
| over 50 to 70 | 296 | 27 | 9.1% |
| over 70 to 80 | 158 | 9 | 5.7% |
| over 80 to 85 | 73 | 1 | 1.4% |
| over 85 to 90 | 78 | 78 | 100.0% |
| over 90 to 95 | 84 | 84 | 100.0% |
| over 95 to 100 | 77 | 76 | 98.7% |

Waste weight is compared by category, ward, floor, bin colour and bin ID with Kruskal-Wallis tests (suited to skewed data). The smallest p-value is p = 0.20, so no attribute shows a reliable weight difference. Full group tables are in `reports/summary_statistics.csv`.

## 5. Time trends

- **Daily:** 1,480 dated records over 30 days, 49.3 per day on average.
- **Weekday:** averages run from 43.0 records per day (Saturday) to 54.2 (Wednesday), a difference that is not statistically significant (p = 0.23). Totals are divided by the number of each weekday in the window, because a month contains four of some weekdays and five of others.
- **Hour of day:** the busiest hour is 17:00 and the quietest 8:00, with no significant departure from an even spread (p = 0.42).
- **Trend:** straight-line trends over the month are not significant for records per day (slope +0.18, p = 0.25), daily weight (p = 0.69) or daily misclassification rate (p = 0.44).
- The first and last calendar weeks are partial; the weekly table in `reports/summary_statistics.csv` lists the days each week covers.

## 6. Recommendations

Each one is tied to a finding above. Treat them as design suggestions, since the data is simulated.

1. **Do not rely on AI confidence to catch errors** (finding 3). Add a different safeguard, such as a second check on the item or a periodic manual audit of correctly-labelled items.
2. **Aim to lower the overall misclassification rate, not a single ward or category** (finding 2). The overall rate is 6.7% and no group is reliably worse. Collect more records per category before targeting any one, since the highest raw rates (Syringes) rest on only 70 records.
3. **Use the fill-level alert as the trigger for emptying bins** (finding 4). Almost every alert on a correctly segregated record occurs above 85% fill, and no bin is reliably fuller than the others (finding 7), so one common emptying rule fits all 12 bins better than bin-specific schedules.
4. **Keep alerts for misclassification and full bins separate** (finding 4). Today both produce the same `Alert_Triggered` flag, so staff cannot tell whether to re-sort an item or empty a bin.
5. **Staff for steady demand** (finding 6). No weekday or hour is reliably busier, so no peak-hour staffing is justified by this data.
6. **Collect data over a longer period and from real bins.** One month cannot show seasonal effects, and simulated records cannot show how a real system performs.

## 7. Limitations

- **Simulated data.** Patterns reflect how the file was generated (see `docs/data_sources.md`).
- **One month.** 2026-10-01 to 2026-10-30, so seasonal trends cannot be studied.
- **Missing values** (up to 2.6% per column) were skipped, so each table is based on the records with a value. The number of records is shown for every comparison.
- **Duplicate record IDs.** `Record_ID` is not unique (see `docs/data_quality_report.md`). The analysis does not use it.
- **Alert rule is inferred.** The link between alerts, misclassification and fill level is what the data shows, not a documented rule.
- **Many small groups.** Rates for single categories or bins rest on 50 to 190 records, so their intervals are wide, and some chi-square cells are small.
- **Multiple tests.** Several tests were run at the 5% level. Since none of the group differences is significant, correcting for multiple tests would not change the conclusions.

## 8. Files

| File | Content |
|---|---|
| `src/analytics.py` | Reusable analysis, validation and report functions |
| `notebooks/02_data_analytics.ipynb` | Step-by-step analysis with charts |
| `reports/summary_statistics.csv` | Every statistic in long format: section, variable, group, statistic, value, unit |
| `reports/analytics_summary.md` | This report, generated by `python -m src.analytics` |
