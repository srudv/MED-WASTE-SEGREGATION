# Data Quality Report — Medical Waste Dataset

**Project:** MED-WASTE-SEGREGATION  
**Issue:** Data Cleaning and Preprocessing — #3  
**Source:** `data/raw/medical_waste.csv`, 1,500 simulated waste-segregation records, October 2026 (see `docs/data_sources.md`)  
**Result:** `data/processed/medical_waste_cleaned.csv`, 1,482 rows and 19 columns

## 1. Input and preservation

- Input: `data/raw/medical_waste.csv` (1,500 rows, 12 columns), read as text so that no value is converted on the way in.
- The raw file is never overwritten. The notebook compares a SHA-256 checksum of the raw file before and after cleaning and confirms it is unchanged.
- Cleaned output is saved separately to `data/processed/medical_waste_cleaned.csv`.
- Every changed cell is recorded in an audit table (row number in the raw CSV, `Record_ID`, column, original value, cleaned value, reason). The notebook shows it and the audit has 1,154 entries.
- Code: `src/preprocessing.py` (reusable functions) and `notebooks/01_data_cleaning.ipynb` (step-by-step run with outputs).

## 2. Missing values and placeholders

- The raw file has **201 blank cells** in 9 of 12 columns. `Record_ID`, `Timestamp` and `Target_Bin_Color` have none.
- Placeholder text is treated as missing: `Unknown`, `nan`, `N/A` and `not recorded`.
- Values that cannot be mapped to a standard label (see section 4) and impossible numbers (section 5) are also set to missing.
- **No imputation.** There is no safe rule for guessing a ward, a weight or an AI confidence, and the missing share is small. Missing does not mean zero.

Missing values in the cleaned data:

| Column | Missing | Share |
|---|---:|---:|
| Record_ID | 0 | 0.00% |
| Timestamp | 2 | 0.13% |
| Hospital_Ward | 38 | 2.56% |
| Floor_Number | 27 | 1.82% |
| Waste_Category | 20 | 1.35% |
| Target_Bin_Color | 1 | 0.07% |
| Bin_ID | 23 | 1.55% |
| Weight_Grams | 31 | 2.09% |
| AI_Confidence_Score | 22 | 1.48% |
| Segregation_Status | 19 | 1.28% |
| Bin_Fill_Level_Percentage | 25 | 1.69% |
| Alert_Triggered | 15 | 1.01% |

## 3. Duplicate records

| Check | Result | Handling |
|---|---|---|
| Fully identical rows | 0 | Nothing to remove |
| Rows identical in every field except `Record_ID` | 36 rows in 18 pairs | Second occurrence removed (18 rows), first kept. Listed below. |
| `Record_ID` used by two rows with different content | 22 rows, 11 IDs | Both rows kept and flagged in `Duplicate_Record_ID` |

The removed rows repeat another row down to the minute, ward, floor, bin, weight, confidence and fill level, so they are the same record entered twice with a new ID. Matching was done on cleaned values, so spelling variants cannot hide a copy.

| Removed Record_ID | Raw CSV line | Kept Record_ID | Raw CSV line |
|---|---:|---|---:|
| REC0380 | 381 | REC0301 | 302 |
| REC0441 | 442 | REC0033 | 34 |
| REC0474 | 475 | REC0442 | 443 |
| REC0493 | 494 | REC0369 | 370 |
| REC0536 | 537 | REC0189 | 190 |
| REC0554 | 555 | REC0036 | 37 |
| REC0562 | 563 | REC0372 | 373 |
| REC0570 | 571 | REC0428 | 429 |
| REC0745 | 746 | REC0716 | 717 |
| REC0843 | 844 | REC0201 | 202 |
| REC0867 | 868 | REC0331 | 332 |
| REC1067 | 1068 | REC0005 | 6 |
| REC1152 | 1153 | REC0120 | 121 |
| REC1177 | 1178 | REC0271 | 272 |
| REC1294 | 1295 | REC0277 | 278 |
| REC1309 | 1310 | REC0232 | 233 |
| REC1318 | 1319 | REC0376 | 377 |
| REC1408 | 1409 | REC1062 | 1063 |

The reused `Record_ID` values were not repaired. The IDs do not follow the row order cleanly enough to fix them without guessing, so `Record_ID` is not a unique key in the cleaned file. Use `Row_Number` (the line number in the raw CSV), which is unique.

## 4. Label and data-type corrections

All text was trimmed and compared in lower case. Variants were mapped to one standard label. Values that cannot be mapped safely were set to missing, not guessed.

| Column | Distinct raw values | Standard values | Cells standardised | Set to missing (not mappable) |
|---|---:|---:|---:|---:|
| Hospital_Ward | 29 | 8 | 197 | 0 |
| Floor_Number | 13 | 5 | 170 | 2 |
| Waste_Category | 40 | 19 | 72 | 2 |
| Target_Bin_Color | 14 | 6 | 181 | 1 |
| Bin_ID | 25 | 12 | 26 | 1 |
| Segregation_Status | 7 | 2 | 256 | 1 |
| Alert_Triggered | 7 | 2 | 180 | 2 |

Examples of corrections:

- Ward: `opd` → `OPD`, `ER` and `Emergency Deptt` → `Emergency`, `Lab` → `Laboratory`, `Operation Theater` → `OT`, `Paediatrics` → `Pediatrics`, `ICUU` → `ICU`.
- Floor: `F3` → `Floor 3`, `1st Floor` → `Floor 1`, `floor-2` → `Floor 2`, `ground floor` → `Ground`, `Fourth Floor` → `Floor 4`.
- Waste category: `Cotton swab` → `Cotton Swabs`, `Expired medication` → `Expired Medications`, `Non infectious waste` → `Non-Infectious Waste`, `IV Bags / Tubes` → `IV Bags/Tubes`.
- Bin colour: `yellow bin`, `Yellow` → `Yellow Bin`; `RED BIN` → `Red Bin`; `green` → `Green Bin`.
- Bin ID: `bin_3` → `BIN_03`; leading spaces removed.
- Segregation status: `Correct` → `Correctly Segregated`; `Misclassified / Override Required` and `Wrong` → `Misclassified`.
- Alert: `no` → `No`, `YES` → `Yes`.

Set to missing because they have no clear standard value: ward `Unknown` and `nan`; floor `Basement` and `Floor 9`; waste category `Medical Waste` and `Other`; bin colour `Purple Bin`; bin ID `BIN_99`; segregation status `Pending`; alert `1` and `Maybe`.

Data types:

| Column | Raw | Cleaned |
|---|---|---|
| Record_ID | text | text |
| Timestamp | text | datetime |
| Hospital_Ward | text | text |
| Floor_Number | text | text |
| Waste_Category | text | text |
| Target_Bin_Color | text | text |
| Bin_ID | text | text |
| Weight_Grams | text | decimal number |
| AI_Confidence_Score | text | decimal number |
| Segregation_Status | text | text |
| Bin_Fill_Level_Percentage | text | decimal number |
| Alert_Triggered | text | text |

Text in numeric columns: `1,250` → 1250 (comma removed), `85%` → 85, `full` → 100 (bin fill level), `unknown` and `N/A` → missing.

Timestamps: 5 of 1,500 were not in the standard `YYYY-MM-DD HH:MM:SS` form.

| Raw value | Decision |
|---|---|
| `2026/10/12 08:15` | Converted (year first) |
| `10-15-2026 19:45` | Converted (month first; 15 cannot be a month) |
| `07/10/2026 14:30` | Ambiguous (7 October or 10 July). Read as 7 October because every other record is dated October 2026. |
| `not recorded` | Set to missing |
| `2026-13-40 25:61:00` | Impossible date, set to missing |

## 5. Invalid records

Impossible values were set to missing. The rest of the record is kept, because the other fields are still usable.

| Column | Rule | Raw values set to missing |
|---|---|---|
| Weight_Grams | greater than 0 and at most 50,000 g | 250000, -25, 999999, 0 |
| AI_Confidence_Score | between 0 and 1 | 1.4, 2.5, -0.2 |
| Bin_Fill_Level_Percentage | between 0 and 100 | -10, 180, 125 |

The 50,000 g (50 kg) weight limit is generous on purpose: the largest remaining weight is 4,155.5 g, and the two removed values (250,000 and 999,999 g) are far outside anything else in the file.

**Consistency flag.** 88 records (5.9%) have a target bin colour that differs from the colour most often used for their waste category (for example Needles that are usually Green Bin). They are flagged in `Category_Bin_Mismatch` and left unchanged. The usual colour is taken from the data itself, not from an external regulation.

## 6. Outliers

Outliers are identified with the 1.5 × IQR rule on the cleaned values. They are **flagged, not removed**.

| Column | Lower fence | Upper fence | Flagged |
|---|---:|---:|---:|
| Weight_Grams | -210.6 | 659.8 | 105 |
| AI_Confidence_Score | 0.545 | 1.145 | 0 |
| Bin_Fill_Level_Percentage | -47.0 | 153.0 | 0 |

Weights are right-skewed (median 200.6 g), so the rule flags the heavy tail (105 values, from 664.6 to 4155.5 g). Large items are plausible in a hospital, so they stay in the data and are marked in `Weight_Outlier`. AI confidence and bin fill level have no outliers after impossible values are removed.

## 7. Encoding and scaling

Not applied to the cleaned dataset. The planned analytics and charts need real units (grams, percent) and readable labels. `encode_and_scale()` in `src/preprocessing.py` returns a one-hot encoded and min-max scaled copy for any later modelling step, and the notebook demonstrates it without saving it.

## 8. Columns added to the cleaned dataset

| Column | Meaning |
|---|---|
| `Row_Number` | Line number of the record in the raw CSV. Unique key. |
| `Duplicate_Record_ID` | True when the `Record_ID` is shared with another kept row |
| `Category_Bin_Mismatch` | True when the bin colour differs from the usual one for the category |
| `Weight_Outlier` | True when the weight is outside the 1.5 × IQR fences |
| `Date`, `Hour`, `Weekday` | Derived from `Timestamp` for time-based charts |

## 9. Validation results

| Check | Result | Details |
|---|---|---|
| every raw row accounted for | Pass | 1500 raw = 1482 kept + 18 removed copies |
| 12 raw columns kept | Pass | all present |
| Row_Number is unique | Pass | unique=1482 |
| no rows identical except for Record_ID | Pass | remaining=0 |
| Timestamp is datetime | Pass | dtype=datetime64[ns] |
| timestamps inside 1-30 Oct 2026 | Pass | min=2026-10-01 01:23:00, max=2026-10-30 23:58:00 |
| Hospital_Ward uses only standard values | Pass | 8 distinct values |
| Floor_Number uses only standard values | Pass | 5 distinct values |
| Waste_Category uses only standard values | Pass | 19 distinct values |
| Target_Bin_Color uses only standard values | Pass | 6 distinct values |
| Bin_ID uses only standard values | Pass | 12 distinct values |
| Segregation_Status uses only standard values | Pass | 2 distinct values |
| Alert_Triggered uses only standard values | Pass | 2 distinct values |
| Weight_Grams is numeric | Pass | dtype=float64 |
| AI_Confidence_Score is numeric | Pass | dtype=float64 |
| Bin_Fill_Level_Percentage is numeric | Pass | dtype=float64 |
| weights between 0 and 50,000 g | Pass | min=14.3, max=4155.5 |
| AI confidence between 0 and 1 | Pass | min=0.7, max=0.99 |
| bin fill level between 0 and 100 | Pass | min=0.0, max=100.0 |

All 19 checks pass, and the raw file checksum is unchanged after the run.

## 10. Remaining limitations

- The data appears to be simulated (see `docs/data_sources.md`). Cleaning makes it consistent, not real.
- The decisions on `full` = 100 and the October 2026 reading of `07/10/2026` are judgement calls. Each affects one cell, and both are in the audit.
- Missing values remain (up to 2.6% per column). Analyses should skip them, not treat them as zero.
- `Record_ID` is not unique. Use `Row_Number`.

## 11. How to reproduce

```bash
pip install -r requirements.txt
python -m src.preprocessing          # writes data/processed/medical_waste_cleaned.csv
jupyter notebook notebooks/01_data_cleaning.ipynb
```
