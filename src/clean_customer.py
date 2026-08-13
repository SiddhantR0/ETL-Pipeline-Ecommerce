# Importing
import os
import pandas as pd

# Cleaning Customers Data
def clean_customer_data():
    raw_dir = "data/raw"
    processed_dir = "data/processed"
    os.makedirs(processed_dir, exist_ok=True)

    file_path = os.path.join(raw_dir, "olist_customers_dataset.csv")
    print("Loading the Raw Customers Data")

    # Checking if Raw Dataset Exists
    if not os.path.exists(file_path):
        print("Error! Dataset Not Found")
        return

    df = pd.read_csv(file_path, dtype={"customer_zip_code_prefix": str})

    df.columns = df.columns.str.strip()
    
    initial_row_count = len(df)
    print(f"Initial Row Count: {initial_row_count}")

    # Handling Missing Values
    id_cols = ["customer_id", "customer_unique_id"]
    df.dropna(subset=id_cols, inplace=True)

    df.drop_duplicates(inplace=True)

    # Cleaning Text Data's
    if "customer_zip_code_prefix" in df.columns:
        df["customer_zip_code_prefix"] = df["customer_zip_code_prefix"].str.zfill(5)

    if "customer_city" in df.columns:
        df["customer_city"] = df["customer_city"].astype(str).str.strip().str.replace(r"\s+", " ", regex=True).str.title()

    if "customer_state" in df.columns:
        df["customer_state"] = df["customer_state"].astype(str).str.upper().str.strip()

    final_row_count = len(df)
    print(f"Final Row Count: {final_row_count}")

    # Exporting the clean data to csv
    output_path = os.path.join(processed_dir, "customers_cleaned.csv")
    df.to_csv(output_path, index=False)
    print("Cleaned Customer Dataset Created")

if __name__ == "__main__":
    clean_customer_data()