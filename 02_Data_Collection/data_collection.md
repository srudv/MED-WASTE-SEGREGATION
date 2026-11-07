# Data Collection Documentation

## 1. Overview
This project integrates two primary medical-waste data sources to evaluate healthcare compliance and automate waste segregation:
1. **National Baseline (CPCB 2023 Annual Report):** State/UT-level biomedical waste statistics from the Central Pollution Control Board (Annexure-I), reporting aggregate generation and CBWTF infrastructure across India.
2. **Hospital Clinical Trial Dataset (`MedWaste_AI_Cleaned_1500_Records.csv`):** 1,489 discrete disposal logs gathered in October 2026 across 8 hospital departments equipped with smart IoT bins and computer-vision classification sensors.

## 2. Sensor Hardware Specifications
* **Computer Vision Camera:** High-speed edge RGB sensor capturing waste items at point-of-disposal (inference time < 250ms).
* **Load Cells:** Dual-strain gauge weight sensors measuring item mass from 1g to 5,000g (+/- 2g accuracy).
* **Ultrasonic Distance Sensors:** HC-SR04 ultrasonic transducers measuring vertical bin headspace every 30 seconds to calculate fill level percentage (0% to 100%).

## 3. Data Dictionary
| Field | Type | Description |
| :--- | :--- | :--- |
| `Record_ID` | String | Unique transaction identifier (REC0001 - REC1500) |
| `Timestamp` | DateTime | Timestamp of waste disposal event (YYYY-MM-DD HH:MM:SS) |
| `Hospital_Ward` | String | Hospital department (Emergency, ICU, OPD, OT, General Ward, Lab, Pediatrics, Radiology) |
| `Floor_Number` | String | Location floor (Ground, Floor 1, Floor 2, Floor 3, Floor 4) |
| `Waste_Category` | String | Specific clinical waste item (19 unique categories) |
| `Target_Bin_Color` | String | Prescribed color stream (Yellow, Red, Blue, White, Black, Green) |
| `Bin_ID` | String | Container device tag (BIN_01 to BIN_12) |
| `Weight_Grams` | Float | Disposal weight in grams |
| `AI_Confidence_Score` | Float | Model classification certainty score (0.70 to 0.99) |
| `Segregation_Status` | String | Compliance outcome (Correctly Segregated, Override, Misclassified, Pending) |
| `Bin_Fill_Level_Percentage` | Float | Current container fill level (0.0% to 100.0%) |
| `Alert_Triggered` | String | Boolean alert flag (Yes / No) |
| `Weight_KG` | Float | Weight converted to kilograms (`Weight_Grams / 1000`) |
| `Dustbin_Waste_Level` | String | Categorical urgency status (Low, Medium, High) |
