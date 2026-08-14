# Importing
import os
import pandas as pd

# Cleaning Order Items
def clean_order_items():
    raw_dir = "data/raw"
    processed_dir = "data/processed"
    os.makedirs(processed_dir, exist_ok=True)

    file_path = os.path.join(raw_dir, "olist_order_items_dataset.csv")
    print("Loading the Raw Order Items Data")

    # Checking if Raw Dataset Exists
    if not os.path.exists(file_path):
        print("Error! Dataset Not Found")
        return

    df = pd.read_csv(file_path)

    df.columns = df.columns.str.strip()

    initial_row_count = len(df)
    print(f"Initial Row Count: {initial_row_count}")

    # Handling Missing Values
    df.dropna(subset=["order_id","order_item_id","product_id","seller_id","price","freight_value"], inplace=True)

    df.drop_duplicates(subset=["order_id","order_item_id"], inplace=True)

    # Making the Datatype to Numeric
    numeric_cols = ["price","freight_value","order_item_id"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Parsing Date and Time 
    if "shipping_limit_date" in df.columns: 
        df["shipping_limit_date"] = pd.to_datetime(df["shipping_limit_date"], errors="coerce")

    # Calculating Total Item Value
    if "price" in df.columns and "freight_value" in df.columns:
        df["total_item_value"] = df["price"] + df["freight_value"]

    # Freight Value to Price Ratio Calculation 
    if "price" in df.columns and "freight_value" in df.columns and "total_item_value" in df.columns: 
        df["freight_ratio"] = df["freight_value"] / df["total_item_value"].replace(0, pd.NA)

    # Seperating Item Price Tiers
    if "price" in df.columns:
        bins = [-float("inf"), 50, 200, 500, float("inf")]
        labels = ["Budget", "Mid-Range", "Premium", "Luxury"]
        df["price_tiers"] = pd.cut(df["price"], bins=bins, labels=labels)

    final_row_count = len(df)
    print(f"Final Row Count: {final_row_count}")

    # Exporting the Clean Data to csv
    output_path = os.path.join(processed_dir, "order_items_cleaned.csv")
    df.to_csv(output_path, index=False)
    print("Clean Order Items Dataset Created")

if __name__ == "__main__":
    clean_order_items()
