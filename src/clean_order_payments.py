# Importing
import os
import pandas as pd
import numpy as np

# Cleaning Order Payments Data
def clean_order_payments_data():
    raw_dir = "data/raw"
    processed_dir = "data/processed"
    os.makedirs(processed_dir, exist_ok=True)

    file_path = os.path.join(raw_dir, "olist_order_payments_dataset.csv")
    print("Loading the Clean Order Payments Dataset")

    # Checking if Raw Dataset Exists
    if not os.path.exists(file_path):
        print("Error! Dataset Not Found")
        return

    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip()

    initial_row_count = len(df)
    print(f"Initial Row Count: {initial_row_count}")

    # Handling Missing Values
    if "order_id" in df.columns:
        df = df.dropna(subset=["order_id"])

    # Standardizing Payment Type
    if "payment_type" in df.columns:
        df["payment_type"] = df["payment_type"].fillna("unknown")
        df["payment_type"] = df["payment_type"].astype(str).str.strip().str.lower()

    # Cleaning numeric Metrics 
    if "payment_installments" in df.columns:
        df["payment_installments"] = pd.to_numeric(df["payment_installments"], errors="coerce").fillna(1).astype(int)
        df["payment_installments"] = df["payment_installments"].apply(lambda x: max(1, x))

    if "payment_value" in df.columns:
        df["payment_value"] = pd.to_numeric(df["payment_value"], errors="coerce")
        median_val = df["payment_value"].median()
        df["payment_value"] = df["payment_value"].fillna(median_val)
        df = df[df["payment_value"] >= 0]

    # High Installment Flag 
    df["is_high_installment"] = df["payment_installments"].apply(lambda x: 1 if x > 5 else 0)

    # Aggregated Payment Metrics 
    order_payment_agg = df.groupby("order_id").agg(
        total_payment_value=("payment_value", "sum"),
        max_payment_installments=("payment_installments", "max"),
        payment_types_used=("payment_type", lambda x: ", ".join(x.unique())),
        payment_sequential_count=("payment_sequential", "max")
    ).reset_index()

    final_row_count = len(order_payment_agg)
    print(f"Final Aggregated Row Count (Unique Orders): {final_row_count}")

    output_path = os.path.join(processed_dir, "order_payments_cleaned.csv")
    order_payment_agg.to_csv(output_path, index=False)
    print("Cleaned Order Payments Dataset Created")

if __name__ == "__main__":
    clean_order_payments_data()