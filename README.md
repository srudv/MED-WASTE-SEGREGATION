# Raw Data: Bio-Medical Waste Management in India (2023)

This folder holds the raw data for the MED-WASTE-SEGREGATION project (Data Analytics & Visualization).
The data is **not modified or cleaned** here. Cleaning and preprocessing belong to the next stage.

## Files

| File | What it is |
|---|---|
| `AR_BMWM_2023.pdf` | Original report, kept exactly as downloaded: *Annual Report on Biomedical Waste Management for the year 2023*, Central Pollution Control Board (CPCB), Ministry of Environment, Forest & Climate Change, Government of India. |
| `medical_waste.csv` | The State/UT-wise table (Annexure-I, report pages 39-41) extracted from the PDF into CSV form. |

## About `medical_waste.csv`

- **Rows:** 37, one for each of 36 States/UTs plus DGAFMS (Directorate General of Armed Forces Medical Services). Daman & Diu and Dadra & Nagar Haveli are reported together as one row, exactly as in the report.
- **Columns:** 23, in the same order as Annexure-I. Descriptions are in `docs/data_dictionary.xlsx`.
- **Reporting period:** calendar year 2023 (January to December), as submitted by State Pollution Control Boards / Pollution Control Committees.
- **Units:** waste quantities are in kg/day. Everything else is a count.

## How the CSV was produced

1. The Annexure-I table was extracted from the PDF with Python (`pdfplumber`).
2. Column headings were rewritten in `snake_case` (e.g. "Total no. of Beds" became `total_beds`).
3. Three State names that the PDF had broken across lines were rejoined (Chhattisgarh, Lakshadweep, Maharashtra).
4. The printed `total` row was left out of the CSV so it can't be double-counted in analysis. It was used for checking instead.

No numbers were changed, rounded, filled in or removed.

**Check:** for all 21 numeric columns, the sum of the 37 rows equals the printed total row (differences of at most 0.01 on kg/day columns, from rounding).

## Special values (kept exactly as printed)

| Value | Where | Notes |
|---|---|---|
| `INP` | 6 cells | Not defined in the report. It appears to mean "information not provided" (an assumption). |
| `NIL` | 34 cells | The report's own word for "none". |
| `NA` | 1 cell (Tripura, `show_cause_notices`) | Not defined in the report. |
| *(empty)* | 2 cells (Chandigarh `show_cause_notices`, DGAFMS `deep_burial_hcf`) | Left blank in the report. |
| Text | Daman & Diu / Dadra & Nagar Haveli, columns `cbwtfs_operational` and `cbwtfs_with_ocems` | The report entered the notes "Utilizing CBWTF of Gujarat" and "Utilising gujarat facility" instead of numbers. |

Because of these codes, numeric columns are text-typed in the raw file. They are converted to numbers during preprocessing.

## Known issues in the source report

See `docs/data_sources.md` for the full list of limitations.
