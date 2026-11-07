# 05 — Data Visualization

## Purpose
This folder contains the visualization notebook, reusable chart-generation code, chart exports and a written guide to the figures. Charts are intended to make the dataset's distributions and analysis results easier to inspect.

## Files
- `03_data_visualization.ipynb` — notebook for the visualization workflow.
- `visualization.py` — reusable Matplotlib chart functions.
- `visualization_summary.md` — chart descriptions, interpretation notes and limitations.
- `01_*.png/.svg` through `08_*.png/.svg` — eight chart exports in PNG and SVG formats.

## Visualizations included
1. Waste-category record counts.
2. Record distribution by hospital ward.
3. Waste-weight distribution.
4. Weight distribution by waste category.
5. Misclassification rate by category, with uncertainty intervals.
6. Alert rate by bin-fill level.
7. Daily record counts.
8. Weekday and hour patterns.

## File formats
- **PNG** is convenient for slides and documents.
- **SVG** is scalable and useful for reports or web/dashboard integration.

## Interpretation
The chart notes identify the data as a simulated October 2026 dataset. These figures describe the supplied project records only and must not be presented as verified real-hospital findings.

## Reproducibility warning
The current script imports `src.analytics` and expects the older `data/processed/` and `reports/figures/` layout. The repository now stores the analysis code, cleaned data and chart exports in numbered stage folders. Update the script/notebook paths and imports, then regenerate and verify all charts before treating them as reproducible outputs from a fresh clone.
