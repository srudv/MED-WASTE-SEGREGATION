# Data Cleaning & Validation Report

## 1. Overview
The raw hospital waste transaction dataset was cleaned and verified to ensure high data integrity for machine learning evaluation and Power BI dashboard visualization.

## 2. Transformations Applied
* **Deduplication:** Validated uniqueness of `Record_ID`; zero duplicate records detected.
* **Timestamp Normalization:** Timestamps standardized to ISO datetime format (`YYYY-MM-DD HH:MM:SS`), spanning calendar October 2026.
* **Numerical Bounds Checking:**
  * `Weight_Grams` bounded to physical limits (min 14.3g, max 645.1g); converted to `Weight_KG` with 3-decimal precision.
  * `AI_Confidence_Score` constrained to $[0.70, 0.99]$.
  * `Bin_Fill_Level_Percentage` verified between $0.0\%$ and $100.0\%$.
* **Categorical Mapping:** Standardized bin colors (*Yellow*, *Red*, *Blue*, *White*, *Black*, *Green*) and status labels (*Correctly Segregated*, *Override*, *Misclassified*, *Pending*).
* **Fill Urgency Classification:** Derived `Dustbin_Waste_Level` into three standard operational buckets: `Low` ($<50\%$), `Medium` ($50-85\%$), and `High` ($\ge 86\%$).

## 3. Post-Cleaning Quality Summary
* **Total Validated Records:** 1,489 rows
* **Total Fields:** 14 columns
* **Missing / Null Values:** 0 nulls across all feature columns
