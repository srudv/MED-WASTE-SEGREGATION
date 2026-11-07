# 02 — Data Collection

## Purpose
This folder stores the original dataset and the documentation describing its fields, collection context and limitations. Keep the original CSV unchanged so that cleaning can always be reproduced from the source file.

## Files
- `MedWaste_AI_Uncleaned_1500_Records.csv` — supplied raw dataset (1,500 records).
- `data_dictionary.xlsx` — spreadsheet describing the dataset fields.
- `data_collection.md` — overview of the dataset, fields and collection context.
- `data_sources.md` — source provenance, suitability, licensing and limitations.

## Dataset contents
The records describe disposal events and include fields such as record ID, timestamp, hospital ward, floor, waste category, target bin colour, bin ID, weight, AI confidence score, segregation status, bin fill level and alert flag.

## Data provenance and responsible use
The source documentation notes that the CSV was supplied by a project teammate and has no independently verifiable publisher or source URL. Its patterns suggest that it may be simulated. Treat it as an academic practice dataset, not verified measurements from a real hospital. Do not use it to claim real hospital waste volumes, real AI accuracy or regulatory compliance.

## Workflow
1. Preserve the raw CSV.
2. Review `data_dictionary.xlsx`, `data_collection.md` and `data_sources.md`.
3. Use the raw CSV as the input for the cleaning stage in `../03_Data_Cleaning/`.
