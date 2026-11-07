# 03 — Data Cleaning

## Purpose
This folder contains the preprocessing code, cleaning notebook, cleaned dataset and quality report. The goal is to standardize the supplied records and document the changes made before analysis.

## Files
- `01_data_cleaning.ipynb` — notebook documenting the cleaning workflow.
- `data_cleaning.py` — reusable Python preprocessing script.
- `MedWaste_AI_Cleaned_1500_Records.csv` — cleaned dataset produced for downstream work.
- `data_cleaning_report.md` — summary of transformations and post-cleaning quality checks.

## Cleaning operations documented
The workflow covers duplicate Record_ID checks, timestamp parsing, text normalization, numeric type conversion and bounds checks, weight conversion to kilograms, and derivation/standardization of bin-fill urgency levels.

## Input and output
- Raw input: `../02_Data_Collection/MedWaste_AI_Uncleaned_1500_Records.csv`
- Cleaned output stored in this folder: `MedWaste_AI_Cleaned_1500_Records.csv`

## Reproducibility note
The current script's default input/output filenames do not yet match the repository's actual raw and cleaned CSV filenames or this folder layout. Review/update those paths before running the script from a fresh clone. The notebook and report should also be checked against the resulting CSV so their record counts and validation claims agree.

## Recommended order
1. Inspect the raw dataset in `../02_Data_Collection/`.
2. Review and run the notebook after confirming its paths.
3. Validate the cleaned CSV and compare its row/column counts with `data_cleaning_report.md`.
4. Pass the verified cleaned dataset to the analysis stage.
