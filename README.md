# Medical Waste Segregation — Data Analytics & Visualization

A data analytics project exploring India's biomedical-waste management data for 2023, using the CPCB annual report.

## Repository structure

```text
MED-WASTE-SEGREGATION/
├── data/
│   ├── raw/                 # Original extracted CSV
│   ├── processed/           # Cleaned dataset
│   └── reference/           # CPCB source report and data dictionary
├── docs/                    # Proposal, problem statement, workflow and data notes
├── notebooks/               # Cleaning, analytics and visualization notebooks
├── reports/
│   └── figures/             # Exported charts
├── src/                     # Reusable Python modules
├── requirements.txt
├── README.md
└── LICENSE
```

## Data and workflow

1. Raw data: `data/raw/medical_waste.csv`
2. Preprocessing: `notebooks/01_data_cleaning.ipynb` and `src/preprocessing.py`
3. Cleaned data: `data/processed/medical_waste_cleaned.csv`
4. Analytics: `notebooks/02_data_analytics.ipynb` and `src/analytics.py`
5. Visualization: `notebooks/03_data_visualization.ipynb` and `src/visualization.py`
6. Outputs: `reports/`, with exported charts in `reports/figures/`

## Setup

```bash
pip install -r requirements.txt
```

Generate visualizations from the repository root:

```bash
python -m src.visualization
```

Open the notebooks in numerical order to explore the complete workflow. Refer to `docs/data_sources.md` and `docs/data_quality_report.md` for source details and data limitations.

## Important data limitations

The source dataset represents calendar year 2023 and is aggregated by State/UT/reporting entity. It does not contain monthly time-series observations or biomedical-waste colour-category quantities. Analyses and charts are therefore restricted to fields actually available in the source.
