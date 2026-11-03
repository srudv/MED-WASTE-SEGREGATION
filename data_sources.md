# Data Sources

Project: MED-WASTE-SEGREGATION (Data Analytics & Visualization)
Issue: Data Collection, Medical Waste Dataset (#2)
Date accessed: 3 November 2026

## 1. Primary source (included in `data/raw/`)

| Item | Details |
|---|---|
| Title | Annual Report on Biomedical Waste Management for the year 2023 |
| Publisher | Central Pollution Control Board (CPCB), Ministry of Environment, Forest & Climate Change, Government of India |
| URL | https://cpcb.nic.in/uploads/Projects/Bio-Medical-Waste/AR_BMWM_2023.pdf |
| Format | PDF, 42 pages |
| Data used | Annexure-I, State/UT-wise status of biomedical waste management (report pages 39-41) |
| Coverage | 36 States/UTs plus DGAFMS (Armed Forces Medical Services), calendar year 2023 |
| Raw files | `data/raw/AR_BMWM_2023.pdf` (original, untouched) and `data/raw/medical_waste.csv` (extracted table) |

**Why this source:** it is the official national compilation. State Pollution Control Boards submit annual reports to CPCB under the Bio-Medical Waste Management Rules, 2016, and CPCB compiles them. It is free to download and covers every State/UT, so it suits comparison, ranking and mapping in the analytics and visualization stages.

## 2. License and terms of use

The report states no license. It is a Government of India publication that CPCB makes freely available on its website. It is used here for academic, non-commercial coursework with full attribution to CPCB. Check CPCB's website terms if the project is ever published or used commercially.

## 3. Collection method

1. The PDF was downloaded from the CPCB URL above and stored unchanged.
2. The Annexure-I table was extracted into CSV with Python (`pdfplumber`). Extraction used AI assistance (Claude); mention this if your course requires it.
3. Only these changes were made: headings rewritten in `snake_case`, three State names rejoined where the PDF had split them across lines, and the printed `total` row left out of the CSV.
4. The extraction was verified: for all 21 numeric columns, the sum of the 37 rows matches the printed total row (rounding differences of at most 0.01).

## 4. Other datasets identified (not included in `data/raw/`)

| Dataset | Type | Relevance | License note |
|---|---|---|---|
| "medicwaste" dataset on Roboflow Universe | Images with object labels | Used to train this project's YOLO waste-detection model | Not verified here. Check the license on the Roboflow dataset page. |
| "Medical Waste" image dataset on Kaggle (user sumn2u) | Images with COCO / Pascal VOC annotations | Public reference dataset for medical-waste object detection (13 categories) | A mirror site lists CC BY 4.0. Confirm on the Kaggle page before relying on it. |
| Dataful, State-wise Bio-Medical Waste Generated, Treated and Disposed (2008-2024) | Tabular, state-wise | Multi-year version of similar CPCB data | Paid download, so not used. |

## 5. Limitations

1. **Aggregated, one year.** Each row is one State/UT total for 2023. There are no item-level, hospital-level or time-series records, and no breakdown by colour category (yellow, red, white, blue). It supports state-level analytics, not training an image classifier.
2. **Self-reported.** Figures were submitted by State Pollution Control Boards / Pollution Control Committees. CPCB notes that 14 States/UTs submitted late (after July 2024) and that it flagged gaps and discrepancies to the States.
3. **Generation vs treatment gaps.** CPCB reports that waste generated exceeds waste treated in several States/UTs (Assam, Bihar, Jharkhand, Karnataka, Kerala, Madhya Pradesh, Manipur, Mizoram, Nagaland, Puducherry). Some States attribute this to incomplete information, so the gap may partly be a reporting gap.
4. **Missing and coded values.** The table contains `INP`, `NIL`, `NA`, two blank cells and two text notes in numeric columns (see `data/raw/README.md`). The report does not define `INP` or `NA`.
5. **Inconsistencies inside the report**, for example:
   - The text says 743 tons/day of waste was generated in one place and 859 tons/day in another (section 3.2).
   - Arunachal Pradesh has 450 HCFs in Annexure-I (324 non-bedded), but the State section (9.3) lists 159 HCFs (33 non-bedded).
   - Maharashtra's HCFs granted authorization is 2,173 in Annexure-I and 2,186 in section 9.21.
   - Ladakh's table shows no CBWTF but its narrative mentions 4 operational CBWTFs.
   - The Annexure-I column headed "COEMS" appears to mean OCEMS (Online Continuous Emission Monitoring System), as used elsewhere in the report.
   - Column numbering in the Annexure header is irregular (XII follows X, and XVI appears twice).
6. **Units.** Waste quantities in the table are kg/day, while the report text sometimes uses tons/day.
7. **Combined entity.** Daman & Diu and Dadra & Nagar Haveli are a single row.

## 6. Suggested citation

Central Pollution Control Board. (n.d.). *Annual Report on Biomedical Waste Management for the year 2023*. Ministry of Environment, Forest & Climate Change, Government of India. https://cpcb.nic.in/uploads/Projects/Bio-Medical-Waste/AR_BMWM_2023.pdf
