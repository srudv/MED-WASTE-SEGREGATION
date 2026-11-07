# Data Sources

Project: MED-WASTE-SEGREGATION (Data Analytics & Visualization)
Issue: Data Collection, Medical Waste Dataset (#2)
Date received: 7 November 2026

## 1. Primary source (included in `data/raw/`)

| Item | Details |
|---|---|
| Title | MedWaste AI Uncleaned 1500 Records |
| Provided by | A project teammate, shared as a CSV file |
| Format | CSV, 1,500 rows x 12 columns |
| Raw file | `data/raw/medical_waste.csv` (identical to the file received) |
| Period covered | 1 to 30 October 2026 |
| Subject | Waste-disposal records from a hospital waste-segregation system: ward, floor, waste type, target bin colour, bin ID, weight, AI confidence, segregation result, bin fill level and alert flag |

**Why this source:** the earlier dataset (CPCB state-wise table) had only 37 rows and no item-level fields. This one has 1,500 records with waste category, bin colour and segregation outcome, which matches the project's topic and gives enough records for cleaning, analytics and charts.

## 2. What this data is (and is not)

The file has no source link, publisher or documentation, and the signs point to simulated data, not real measurements:

- All 1,500 records fall within a single month, and the categories, wards, floors and bins are spread almost evenly.
- Every waste category maps to a bin colour in the same pattern (for example Needles to Green Bin, Food Waste to Black Bin), apart from a small share of mismatches.
- Errors appear to have been inserted on purpose: impossible dates, weights such as 999999 g, AI confidence above 1, and the same value written several ways.
- Bin IDs run only from BIN_01 to BIN_12, and the AI confidence column is consistent with this project's own AI segregation idea.

**Therefore:** this dataset is suitable for practising the data-analytics workflow (cleaning, analysis, visualization). It must not be used to draw conclusions about real hospitals, real waste volumes or real model accuracy.

> **To confirm and complete:** the file does not record who generated it, with what tool, or on what date. Add that here once the teammate confirms.

## 3. License and terms of use

No license is stated. The file was supplied by a team member for this academic, non-commercial coursework project. Do not publish or reuse it outside the project without the creator's permission.

## 4. Collection method

1. The CSV was received from a project teammate and copied into `data/raw/medical_waste.csv` without any change (checked byte for byte against the received file).
2. It was then profiled with Python (`pandas`) to count blank cells, non-standard values, duplicate IDs and out-of-range numbers. The results are in `data/reference/data_dictionary.xlsx` and `data/README.md`.
3. No value was changed, removed, filled in or reformatted.

## 5. Other datasets identified (not included in `data/raw/`)

| Dataset | Type | Relevance | License note |
|---|---|---|---|
| CPCB, *Annual Report on Biomedical Waste Management 2023* (https://cpcb.nic.in/uploads/Projects/Bio-Medical-Waste/AR_BMWM_2023.pdf) | State/UT-wise table, 37 rows | Real national figures. It was the first dataset for this project but is too small, so it is kept in `data/reference/` as background only. | Government of India publication, free to download, no license stated. Cite CPCB. |
| "medicwaste" dataset on Roboflow Universe | Images with object labels | Used to train this project's YOLO waste-detection model | Not verified here. Check the license on the Roboflow dataset page. |
| "Medical Waste" image dataset on Kaggle (user sumn2u) | Images with COCO / Pascal VOC annotations | Public reference dataset for medical-waste object detection | A mirror site lists CC BY 4.0. Confirm on the Kaggle page before relying on it. |

## 6. Limitations

1. **Simulated, not real.** See section 2. Patterns in the data reflect how it was generated, not how a real hospital behaves.
2. **One month only.** All records are from October 2026, so seasonal or long-term trends cannot be studied.
3. **Uncleaned by design.** 201 blank cells, 11 reused Record_IDs, 18 repeated records, 5 unusable timestamps, text in numeric columns, impossible numbers and inconsistent labels (see `data/README.md`). Cleaning is the job of the next issue.
4. **Reused Record_IDs.** 11 IDs appear twice with different content, so `Record_ID` cannot be used as a unique key.
   **Repeated records.** 18 pairs of rows are identical in every field except `Record_ID`, so they look like the same record entered twice.
5. **Ambiguous values.** `07/10/2026 14:30` could be 7 October or 10 July. Labels such as `Pending`, `Maybe`, `Other` and `Medical Waste` have no clear standard value.
6. **No codebook.** Column meanings in `data/reference/data_dictionary.xlsx` were inferred from names and values, not from source documentation.
7. **Small categories.** Some categories (for example `Purple Bin`, `BIN_99`, `Floor 9`) occur only once, so they are likely entry errors.

## 7. Suggested citation

Project teammate. (2026). *MedWaste AI Uncleaned 1500 Records* [Simulated dataset, CSV]. MED-WASTE-SEGREGATION project, unpublished coursework data.
