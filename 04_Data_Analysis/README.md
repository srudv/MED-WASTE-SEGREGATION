# 04 — Data Analysis

## Purpose
This folder contains the exploratory analysis notebook, reusable analysis module, summary statistics and written findings. The analysis stage is intended to describe patterns in the cleaned medical-waste records without treating missing values as zero.

## Files
- `02_data_analytics.ipynb` — Jupyter notebook for the analysis workflow.
- `analytics.py` — reusable analysis functions and statistical calculations.
- `summary_statistics.csv` — exported descriptive statistics.
- `analytics_summary.md` — narrative summary of the reported findings.

## Topics covered
The analysis assets examine waste-category and ward distributions, waste weights, segregation outcomes, AI confidence, alert activity, bin fill levels and time-based patterns where timestamps are available.

## Data interpretation
The source documentation indicates that the supplied dataset may be simulated and is not independently verified real-hospital data. Findings should therefore be described as patterns in this project dataset only, not as evidence about hospitals generally or validated AI-system performance.

## Reproducibility warning
The current analysis module still refers to older paths such as `data/processed/medical_waste_cleaned.csv` and `reports/`, while the current repository stores the cleaned CSV in `../03_Data_Cleaning/` and analysis outputs in this folder. Update those paths and verify the notebook imports before claiming that the workflow runs from a fresh clone. Also regenerate the summary CSV and report from the current cleaned dataset before presenting the figures as current results.
