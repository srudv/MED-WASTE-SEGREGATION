import pandas as pd
import numpy as np

def clean_medical_waste_data(input_path='MedWaste_AI_Cleaned_1500_Records.csv', output_path='medwaste_cleaned.csv'):
    print(f"Loading raw dataset from {input_path}...")
    df = pd.read_csv(input_path)
    initial_rows = len(df)
    
    # 1. Drop duplicates
    df = df.drop_duplicates(subset=['Record_ID']).copy()
    
    # 2. Parse timestamps
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
    df = df.dropna(subset=['Timestamp'])
    
    # 3. Standardize text columns
    text_cols = ['Hospital_Ward', 'Floor_Number', 'Waste_Category', 'Target_Bin_Color', 'Segregation_Status', 'Alert_Triggered']
    for col in text_cols:
        df[col] = df[col].astype(str).str.strip()
        
    # 4. Handle numeric constraints
    df['Weight_Grams'] = pd.to_numeric(df['Weight_Grams'], errors='coerce').clip(lower=1.0)
    df['Weight_KG'] = (df['Weight_Grams'] / 1000.0).round(3)
    df['AI_Confidence_Score'] = pd.to_numeric(df['AI_Confidence_Score'], errors='coerce').clip(0.0, 1.0)
    df['Bin_Fill_Level_Percentage'] = pd.to_numeric(df['Bin_Fill_Level_Percentage'], errors='coerce').clip(0.0, 100.0)
    
    # 5. Populate Dustbin_Waste_Level if missing
    if 'Dustbin_Waste_Level' not in df.columns or df['Dustbin_Waste_Level'].isnull().any():
        conditions = [
            df['Bin_Fill_Level_Percentage'] < 50.0,
            (df['Bin_Fill_Level_Percentage'] >= 50.0) & (df['Bin_Fill_Level_Percentage'] < 86.0),
            df['Bin_Fill_Level_Percentage'] >= 86.0
        ]
        choices = ['Low', 'Medium', 'High']
        df['Dustbin_Waste_Level'] = np.select(conditions, choices, default='Medium')
        
    df.to_csv(output_path, index=False)
    print(f"Data cleaned successfully: {len(df)} records saved to {output_path}.")
    return df

if __name__ == '__main__':
    clean_medical_waste_data()
