# Raw medical-waste data

## File
`medical_waste.csv` is a **10-row excerpt transcribed from the visible preview** of Dataful's dataset, *Medical Waste: Year- and State-wise Quantity of Bio-Medical Waste Generated, Treated and Disposed*. It is not the full 1,260-row dataset and must not be treated as a complete national dataset.

- Source/preview: https://dataful.in/datasets/19381/
- Underlying source cited by the publisher: Central Pollution Control Board (CPCB), *Annual Report - Inventory on Bio Medical Waste Management*: https://cpcb.nic.in/status-of-bmw-management/
- Coverage of the full published dataset: 2008–2024; 1,260 rows; state/year granularity.
- Units: kilograms per day.
- Extract scope: the first ten 2024 rows shown in the page preview (Andaman and Nicobar Islands, Andhra Pradesh, Arunachal Pradesh, Assam, and Bihar; generated and treated/disposed measures where visible).
- Collection method: manual transcription of the public preview on 2026-10-27. No imputation or transformation was applied to the values shown. CSV serialization only.
- Important: obtain the full downloadable source from the Dataful page or the CPCB annual reports before drawing national conclusions. Keep the downloaded original in a separate raw-source file and record its exact filename, date, and checksum.

## Interpretation
The `category` field contains publisher/source wording. CPCB terminology for “treated” versus “treated and disposed” may vary across years; do not silently normalize these labels. Empty `note` values are blank, not zero or “not applicable”.
