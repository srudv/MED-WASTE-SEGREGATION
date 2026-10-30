# Data sources and collection notes

## 1. India state/year biomedical-waste quantities (primary quantitative source)

- **Dataset page:** https://dataful.in/datasets/19381/
- **Underlying official source:** Central Pollution Control Board (CPCB), *Annual Report - Inventory on Bio Medical Waste Management*: https://cpcb.nic.in/status-of-bmw-management/
- **Publisher/citation shown on Dataful:** Ministry of Environment, Forest and Climate Change. (2026). *Medical Waste: Year- and State-wise Quantity of Bio-Medical Waste Generated, Treated and Disposed* [Dataset]. Dataful. https://dataful.in/datasets/19381
- **Attributes:** `year`, `state`, `category`, `value`, `unit`, `note`.
- **Coverage/granularity:** 2008–2024, yearly by state/territory; publisher page reports 1,260 rows and 6 columns, updated 29 July 2026.
- **License/terms:** No explicit open-data license was verified on the dataset page during collection. Treat reuse rights as **not confirmed**; review Dataful terms and CPCB source terms before redistribution. Attribution is included here. The official source is the preferred source for obtaining original annual-report material.
- **Collection method in this repository:** A 10-row excerpt was transcribed from the public Dataful page preview on 2026-10-27. This is a preview extract, **not** the complete dataset. No synthetic rows were added; no source values were imputed or normalized.
- **Limitations:** The preview excerpt contains only five states/territories and year 2024, so it cannot support national or temporal trend conclusions. Some values are absent in the full source. The publisher notes that CPCB wording for “treated” and “treated and disposed” varies by year. The `value` field is described as a string in the publisher metadata despite representing quantities; validate types during preprocessing.

## 2. WHO healthcare-waste categories and characteristics (classification reference)

- **Source:** World Health Organization, *Health-care waste*, fact sheet updated 24 October 2024.
- **URL:** https://www.who.int/news-room/fact-sheets/detail/health-care-waste
- **Use:** Category definitions and examples for infectious, pathological, sharps, chemical, pharmaceutical/cytotoxic, radioactive, and general non-hazardous waste; general context on hazardous versus non-hazardous waste.
- **License/terms:** WHO copyright applies; the fact sheet is a reference, not a downloadable tabular dataset. This repository links to and summarizes the source rather than reproducing the full publication. Check the source's reuse terms for downstream redistribution.
- **Collection method:** Reviewed the published fact sheet on 2026-10-27 and recorded category names/examples in documentation. No WHO quantitative observations are inserted into `medical_waste.csv`.
- **Limitations:** WHO's broad international categories are not identical to India's statutory color-coded biomedical-waste segregation rules. Use the applicable Indian Biomedical Waste Management Rules and local institutional SOPs for operational segregation.

## 3. India official biomedical-waste reporting index

- **Source:** CPCB, Status of Biomedical Waste Management.
- **URL:** https://cpcb.nic.in/status-of-bmw-management/
- **Use:** Official entry point for CPCB annual reports/inventory material and validation against the secondary compiled dataset.
- **License/terms:** No explicit dataset license confirmed here; consult CPCB terms and the individual reports.
- **Collection method:** Source link recorded for follow-up verification; no annual report was downloaded or transformed for this commit.

## Reproducibility and data integrity

- `data/raw/medical_waste.csv` is a manually transcribed preview excerpt, not a full source-file mirror. The file's schema follows the six fields shown by Dataful.
- Do not describe this excerpt as the complete CPCB dataset.
- For a complete raw-data release, download the full CSV from the Dataful dataset page or retrieve CPCB annual reports, preserve the downloaded file unchanged, and record retrieval date, source filename, license/terms, and SHA-256 checksum.
- Derived/cleaned tables should be stored under `data/processed/`; never overwrite raw source files.
