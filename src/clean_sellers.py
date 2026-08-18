# Importing
import os
import pandas as pd
import numpy as np 

# Cleaning Sellers Data
def clean_sellers_data():
    raw_dir = "data/raw"
    processed_dir = "data/processed"
    os.makedirs(processed_dir, exist_ok=True)

    file_path = os.path.join(raw_dir, "olist_sellers_dataset.csv")
    print("Loading the Clean Sellers Dataset")

    # Checking if Raw Dataset Exists
    if not os.path.exists(file_path):
        print("Error! Dataset Not Found")
        return

    df = pd.read_csv(file_path)

    df.columns = df.columns.str.strip()

    initial_row_count = len(df)
    print(f"Initial Row Count: {initial_row_count}")

    # Handling Missing  Values
    if "seller_id" in df.columns:
        df = df.dropna(subset=["seller_id"])

    df.drop_duplicates(subset=["seller_id"], inplace=True)

    # Cleaning City Text
    if "seller_city" in df.columns:
        df["seller_city"] = df["seller_city"].fillna("Unknown")
        df["seller_city"] = df["seller_city"].astype(str).str.strip().str.replace(r"\s+", " ", regex=True).str.title()

    # Cleaning State Text
    if "seller_state" in df.columns:
        df["seller_state"] = df["seller_state"].fillna("UNKNOWN")
        df["seller_state"] = df["seller_state"].astype(str).str.strip().str.upper()

    # Standardizing Zip Code Prefix Format 
    if "seller_zip_code_prefix" in df.columns:
        df["seller_zip_code_prefix"] = pd.to_numeric(df["seller_zip_code_prefix"], errors='coerce')
        df["seller_zip_code_prefix"] = df["seller_zip_code_prefix"].fillna(0)
        df["seller_zip_code_prefix"] = df["seller_zip_code_prefix"].astype(int).astype(str).str.zfill(5)

    # State Mapping 
    def map_brazilian_regions(state):
        north = {'AC', 'AP', 'AM', 'PA', 'RO', 'RR', 'TO'}
        northeast = {'AL', 'BA', 'CE', 'MA', 'PB', 'PE', 'PI', 'RN', 'SE'}
        central_west = {'DF', 'GO', 'MT', 'MS'}
        southeast = {'ES', 'MG', 'RJ', 'SP'}
        south = {'PR', 'RS', 'SC'}
        
        if state in north:
            return 'North'
        elif state in northeast:
            return 'Northeast'
        elif state in central_west:
            return 'Central-West'
        elif state in southeast:
            return 'Southeast'
        elif state in south:
            return 'South'
        else:
            return 'Unknown'

    if "seller_state" in df.columns:
        df["seller_region"] = df["seller_state"].apply(map_brazilian_regions)

    # Flagging Unknown Cities
    df["seller_is_unknown_city"] = df["seller_city"].apply(lambda x: 1 if x == "Unknown" else 0)

    final_row_count = len(df)
    print(f"Final Row Count: {final_row_count}")

    # Exporting the Clean Data to csv
    output_path = os.path.join(processed_dir, "sellers_cleaned.csv")
    df.to_csv(output_path, index=False)
    print("Cleaned Sellers Dataset Created")

if __name__ == "__main__":
    clean_sellers_data()