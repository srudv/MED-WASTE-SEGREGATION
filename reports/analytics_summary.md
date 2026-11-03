# Medical Waste Analytics Summary — India, 2023

**Source:** CPCB Annual Report on Biomedical Waste Management for 2023, Annexure-I  
**Input:** data/processed/medical_waste_cleaned.csv  
**Coverage:** 37 reporting entities; 23 columns; waste quantities in kg/day.

## Executive findings

- Reported biomedical waste generation totals **743,147.531 kg/day**.
- Reported treated/disposed quantity totals **694,353.322 kg/day**, or **93.43%** of reported generation. Treated minus generated is **−48,794.209 kg/day**. This aggregate difference is not proof that the difference represents untreated waste.
- Mean generation per reporting entity is **20,085.07 kg/day**; median is **8,776.51 kg/day**, indicating a right-skewed distribution.
- Top five generators: Uttar Pradesh (**99,115.08**), Maharashtra (**77,862.00**), Karnataka (**74,013.82**), Kerala (**68,122.53**) and Tamil Nadu (**59,261.04 kg/day**).
- Reported captive treatment is **22,656.631 kg/day** and CBWTF treatment is **671,696.582 kg/day** (approximately **3.26%** and **96.74%** of the treated total).
- The dataset reports **234 operational CBWTFs**, **30 under construction**, **435,257 healthcare facilities** and **3,091,847 beds**.

## Interpretation and recommendations

1. Prioritize capacity and compliance review in high-volume entities. High generation alone does not indicate poor performance; consider population, facility mix and reporting completeness.
2. Review state-level differences between generation and treatment/disposal. Verify source records and reporting periods before interpreting them as operational shortfalls.
3. Monitor captive and CBWTF treatment capacity separately. CBWTFs account for most reported treatment quantity, making service continuity and geographic access important.
4. Follow up on undefined or missing source values (INP, NA and blanks). Missing values must not be interpreted as zero.
5. Future data collection should include monthly/quarterly observations, population and bed-occupancy context, and explicit yellow/red/white/blue waste-category quantities.

## Scope limitations

- This is a **single-year (calendar year 2023)** State/UT aggregate. There is no monthly or multi-year time dimension, so time trends cannot be calculated.
- No biomedical-waste colour-category fields exist, so category distributions and item-level waste-type frequencies cannot be calculated.
- State/UT aggregates conceal facility-level variation. DGAFMS and the combined Daman & Diu / Dadra & Nagar Haveli row are reporting entities.
- INP, NA and blank values are not equivalent to zero. The preprocessing documentation states NIL was mapped to zero.
- The 93.43% aggregate ratio is not a verified compliance rate and may be affected by reporting differences and source inconsistencies.

## Reproducibility

From the repository root:

```bash
pip install -r requirements.txt
python -m src.analytics
jupyter notebook notebooks/02_data_analytics.ipynb
```

The script writes reports/summary_statistics.csv. The notebook repeats the checks, tables and visual analysis. The existing cleaned input is referenced in place and is not duplicated.

## Validation status

Confirmed that the committed cleaned input contains 37 rows and 23 columns. Aggregate totals, mean, median and top-five ranking were recomputed from that CSV for this report. The module and notebook include runtime schema, row-count and unique-label checks. The notebook has **not** been run in a hosted GitHub environment; run it locally to confirm plots render in the user's environment.
