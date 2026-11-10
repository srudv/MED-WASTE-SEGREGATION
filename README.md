# AI-Based Medical Waste Management System

An academic data analytics project that explores medical-waste segregation records through **data collection, data cleaning, exploratory analysis, visualization, and a Power BI dashboard**.

The repository is organized into six numbered stages so that the project workflow is easy to understand, review, and extend.

> **Dataset note:** The current dataset was supplied by a project teammate and has no independently verifiable public source. The project documentation indicates that it may be simulated. Results describe this project dataset only; they must not be presented as verified hospital measurements, regulatory-compliance evidence, or proof of real-world AI accuracy.



## Table of Contents

- [Project Overview](#project-overview)
- [Problem Statement](#problem-statement)
- [Objectives](#objectives)
- [Project Workflow](#project-workflow)
- [Repository Structure](#repository-structure)
- [Dataset Description](#dataset-description)
- [Technology Stack](#technology-stack)
- [Installation and Setup](#installation-and-setup)
- [Working with Each Stage](#working-with-each-stage)
- [Dashboard](#dashboard)
- [Reproducibility and Data Validation](#reproducibility-and-data-validation)
- [Limitations](#limitations)
- [Future Enhancements](#future-enhancements)
- [Contributors](#contributors)

---

## Project Overview

Healthcare facilities generate different categories of waste that need to be identified, segregated, monitored, and handled appropriately. This project demonstrates how a structured dataset can be prepared and analyzed to explore waste categories, hospital wards, disposal weights, recorded segregation outcomes, bin-fill levels, and alert activity.

The project follows a data workflow:

1. Define the problem and project objectives.
2. Review and document the supplied dataset.
3. Clean and preprocess the raw records.
4. Analyze the cleaned data and calculate descriptive/statistical summaries.
5. Create charts to communicate patterns in the data.
6. Present selected information through a Power BI dashboard artifact.

This repository is an **academic prototype and analytics workflow**. It is not, by itself, a deployed real-time hospital monitoring system.

## Problem Statement

Medical-waste records may contain duplicate identifiers, inconsistent text labels, invalid timestamps, missing values, or incorrectly formatted numeric fields. If these issues are not checked before analysis, summaries and visualizations may be misleading.

The project aims to organize the supplied records, document data-quality operations, explore available fields, and communicate the results through reproducible analytical assets and a dashboard.

## Objectives

- Document the project scope, dataset, and field definitions.
- Preserve the original CSV and prepare a cleaned version for analysis.
- Standardize relevant text, timestamp, and numeric fields.
- Explore waste-category, ward, weight, segregation-status, confidence-score, bin-fill, and alert fields where available.
- Produce clear charts with appropriate titles, labels, units, and context.
- Provide a Power BI Desktop dashboard file for further inspection.
- Maintain an understandable, version-controlled project structure.

## Project Workflow

| Stage | Folder | Main purpose |
|---|---|---|
| 01 | `01_Project_Proposal/` | Defines the problem, objectives, scope, and methodology. |
| 02 | `02_Data_Collection/` | Stores the original dataset and its documentation. |
| 03 | `03_Data_Cleaning/` | Contains preprocessing code, notebook, cleaned CSV, and quality report. |
| 04 | `04_Data_Analysis/` | Contains analytical code, notebook, summary statistics, and findings. |
| 05 | `05_Data_Visualization/` | Contains chart-generation code, notebook, and exported figures. |
| 06 | `06_Dashboard/` | Contains the Power BI Desktop dashboard file and instructions. |

## Repository Structure

```text
MED-WASTE-SEGREGATION/
│
├── 01_Project_Proposal/
│   ├── README.md
│   └── project_proposal.md
│
├── 02_Data_Collection/
│   ├── README.md
│   ├── MedWaste_AI_Uncleaned_1500_Records.csv
│   ├── data_collection.md
│   ├── data_dictionary.xlsx
│   └── data_sources.md
│
├── 03_Data_Cleaning/
│   ├── README.md
│   ├── 01_data_cleaning.ipynb
│   ├── data_cleaning.py
│   ├── MedWaste_AI_Cleaned_1500_Records.csv
│   └── data_cleaning_report.md
│
├── 04_Data_Analysis/
│   ├── README.md
│   ├── 02_data_analytics.ipynb
│   ├── analytics.py
│   ├── summary_statistics.csv
│   └── analytics_summary.md
│
├── 05_Data_Visualization/
│   ├── README.md
│   ├── 03_data_visualization.ipynb
│   ├── visualization.py
│   ├── visualization_summary.md
│   ├── 01_*.png / 01_*.svg
│   ├── 02_*.png / 02_*.svg
│   ├── ...
│   └── 08_*.png / 08_*.svg
│
├── 06_Dashboard/
│   ├── README.md
│   └── AI-Driven Medical Waste Segregation System ( dashboard ).pbix
│
├── requirements.txt
├── README.md
└── LICENSE
```

Each numbered folder has its own `README.md` describing the files and purpose of that stage. Open those folder-level READMEs for more detailed instructions.

## Dataset Description

The raw dataset is stored at:

`02_Data_Collection/MedWaste_AI_Uncleaned_1500_Records.csv`

The repository documentation describes it as a supplied dataset containing approximately 1,500 records and fields such as:

- `Record_ID` — record identifier.
- `Timestamp` — date and time associated with a record.
- `Hospital_Ward` and `Floor_Number` — reported location.
- `Waste_Category` — waste category recorded in the dataset.
- `Target_Bin_Color` and `Bin_ID` — target bin label and bin identifier.
- `Weight_Grams` — recorded weight.
- `AI_Confidence_Score` — recorded confidence value.
- `Segregation_Status` — recorded segregation outcome.
- `Bin_Fill_Level_Percentage` — recorded fill level.
- `Alert_Triggered` — recorded alert flag.

The cleaning documentation describes additional derived fields, including `Weight_KG` and `Dustbin_Waste_Level`.

**Provenance:** The source notes say the CSV was supplied by a project teammate and do not identify an independently verifiable publisher or public source URL. Treat the data as simulated/unverified unless its provenance is independently established. Do not attribute this transaction-level dataset to CPCB or another organization without evidence.

## Technology Stack

| Technology | Use |
|---|---|
| Python | Main programming language for data processing and analysis. |
| pandas | CSV handling, cleaning, grouping, and tabular operations. |
| NumPy | Numerical operations and derived values. |
| SciPy | Statistical tests used in the analysis assets. |
| Matplotlib | Data visualization and chart exports. |
| Jupyter Notebook | Interactive exploration and documentation. |
| Microsoft Power BI Desktop | Dashboard/report authoring using a PBIX file. |
| Git and GitHub | Version control, collaboration, and project hosting. |

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/srudv/MED-WASTE-SEGREGATION.git
cd MED-WASTE-SEGREGATION
```

### 2. Create and activate a virtual environment (recommended)

**Windows:**

```bash
python -m venv .venv
.venv\Scripts\activate
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Open the notebooks

```bash
jupyter notebook
```

Open the notebooks in workflow order, starting with the cleaning notebook, then analysis, and finally visualization. Before running, check the input/output paths and imports noted below.

## Working with Each Stage

### Stage 01 — Project Proposal

Open `01_Project_Proposal/project_proposal.md` to review the background, problem statement, objectives, scope, and proposed methodology.

### Stage 02 — Data Collection

Review the raw CSV and the supporting documentation:

- `data_collection.md`
- `data_dictionary.xlsx`
- `data_sources.md`

Keep the original CSV unchanged. Use it as the source input for preprocessing.

### Stage 03 — Data Cleaning

Main files:

- `03_Data_Cleaning/01_data_cleaning.ipynb`
- `03_Data_Cleaning/data_cleaning.py`
- `03_Data_Cleaning/MedWaste_AI_Cleaned_1500_Records.csv`
- `03_Data_Cleaning/data_cleaning_report.md`

The documented cleaning workflow includes duplicate checks, timestamp parsing, text normalization, numeric conversion and range checks, weight conversion, and a derived bin-fill urgency label.

**Important:** The current script's default input/output paths do not yet match the raw and cleaned CSV locations in this repository. Review and correct those paths before executing the script. Verify the generated row count, column count, missing values, duplicate handling, and numeric bounds against the cleaning report.

### Stage 04 — Data Analysis

Main files:

- `04_Data_Analysis/02_data_analytics.ipynb`
- `04_Data_Analysis/analytics.py`
- `04_Data_Analysis/summary_statistics.csv`
- `04_Data_Analysis/analytics_summary.md`

The analysis assets explore distributions and relationships in the available fields, including waste categories, wards, weights, segregation outcomes, confidence values, bin-fill levels, and alerts.

**Important:** The current analysis module still refers to paths from an older repository layout. Update its input path to use the cleaned CSV in `03_Data_Cleaning/` and its output paths to the current analysis folder. Regenerate the summary statistics and written findings from the same verified cleaned dataset before treating the reported values as final.

### Stage 05 — Data Visualization

Main files:

- `05_Data_Visualization/03_data_visualization.ipynb`
- `05_Data_Visualization/visualization.py`
- `05_Data_Visualization/visualization_summary.md`
- Eight chart exports in PNG and SVG formats.

The existing chart topics include:

1. Waste-category record counts.
2. Record distribution by hospital ward.
3. Waste-weight distribution.
4. Weight distribution by category.
5. Misclassification rate by category.
6. Alert rate by bin-fill level.
7. Daily record counts.
8. Weekday and hourly patterns.

PNG files are convenient for presentations; SVG files can be scaled without losing image quality.

**Important:** The current visualization script still refers to imports and paths from the previous folder layout. Update the imports and file paths, then regenerate and verify the charts from the current cleaned dataset.

### Stage 06 — Dashboard

Open the PBIX file in Microsoft Power BI Desktop. If prompted, reconnect the data source to:

`03_Data_Cleaning/MedWaste_AI_Cleaned_1500_Records.csv`

Refresh the data and verify the report's visuals, measures, labels, filters, and units before presenting it. See `06_Dashboard/README.md` for more instructions.

## Dashboard

The repository includes a Power BI Desktop report:

`06_Dashboard/AI-Driven Medical Waste Segregation System ( dashboard ).pbix`

The PBIX file is a dashboard development artifact. It does not by itself mean that the report is publicly published, automatically refreshed, or connected to live hospital sensors.

## Reproducibility and Data Validation

Before describing the project as a fully reproducible end-to-end pipeline, complete these checks:

1. Correct the cleaning script and notebook paths so they read the raw CSV in `02_Data_Collection/` and write the cleaned CSV in `03_Data_Cleaning/`.
2. Update analysis imports and paths to use the current numbered folders.
3. Update visualization imports and paths to use the current numbered folders.
4. Regenerate the analysis summary, statistics, and charts from the same cleaned dataset.
5. Reconcile the documented difference between the cleaning report (1,489 rows and 14 columns) and the analytics summary (1,482 records and 19 columns).
6. Confirm that data-quality claims, such as missing-value counts and numeric ranges, match the actual cleaned CSV.
7. Refresh the Power BI data source and compare dashboard values with the regenerated analysis outputs.

Until these checks are completed, treat the saved analysis summaries and charts as project artifacts that require verification, not as independently reproduced final results.

## Limitations

- The dataset has no independently verifiable public source and may be simulated.
- The records should not be interpreted as verified measurements from real hospitals.
- Recorded AI confidence scores do not establish actual model accuracy.
- Recorded segregation outcomes do not prove regulatory compliance.
- The current cleaning and analysis documentation report different dataset shapes.
- Some scripts and notebooks still need path/import updates for the numbered folder structure.
- The PBIX file requires refresh and validation before its figures are treated as current.
- The repository does not establish a live hospital sensor deployment.

## Future Enhancements

- Establish a single canonical dataset schema and data dictionary.
- Add automated tests for duplicate IDs, invalid timestamps, missing values, category labels, and numeric ranges.
- Make scripts accept configurable input and output paths.
- Add one end-to-end command to run cleaning, analysis, and visualization.
- Regenerate reports and figures automatically from the verified cleaned dataset.
- Validate and document all Power BI measures and visuals.
- If real hospital data is used in future, obtain appropriate permission and apply privacy and data-governance safeguards.
- If an AI classifier is developed, evaluate it against independently reviewed labels using a confusion matrix, precision, recall, F1-score, and per-class metrics.

## Contributors

- Repository owner and project contributors: see the GitHub repository's **Contributors** section.

---

**Repository:** [srudv/MED-WASTE-SEGREGATION](https://github.com/srudv/MED-WASTE-SEGREGATION)

