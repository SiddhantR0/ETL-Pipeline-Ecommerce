# Importing
import os
import pandas as pd 

# Cleaning Orders Data
def clean_orders_data():
    raw_dir = "data/raw"
    processed_dir = "data/processed"
    os.makedirs(processed_dir, exist_ok=True)

    file_path = os.path.join(raw_dir, "olist_orders_dataset.csv")
    print("Loading the Raw Orders Data")

    # Checking if Raw Dataset Exists
    if not os.path.exists(file_path):
        print("Error! Dataset Not Found")
        return

    df = pd.read_csv(file_path)

    df.columns = df.columns.str.strip()

    initial_row_count = len(df)
    print(f"Initial Row Count: {initial_row_count}")

    # Handling Missing Values
    df.dropna(subset=["order_id", "customer_id", "order_status"], inplace=True)

    df.drop_duplicates(subset=["order_id"], inplace=True)

    # Parsing Date and Time 
    dateandtime_cols = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ]

    for col in dateandtime_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # Calculating Delivery Delay
    if "order_delivered_customer_date" in df.columns and "order_estimated_delivery_date" in df.columns:
        df["delivery_delay_days"] = (
            df["order_delivered_customer_date"] - df["order_estimated_delivery_date"]        
        ).dt.total_seconds() / 86400.0

    # Calculating Approval Time 
    if "order_purchase_timestamp" in df.columns and "order_approved_at" in df.columns:
        df["approval_time_hours"] = (
            df["order_approved_at"] - df["order_purchase_timestamp"]
        ).dt.total_seconds() / 3600.0

    # Delivery Status Flag 
    if "delivery_delay_days" in df.columns:
        df["is_late"] = df["delivery_delay_days"] > 0

    # Order's Transit Time
    if "order_delivered_customer_date" in df.columns and "order_purchase_timestamp" in df.columns:
        df["fulfillment_time_days"] = (
            df["order_delivered_customer_date"] - df["order_purchase_timestamp"]
        ).dt.total_seconds() / 86400.0

    if "order_delivered_customer_date" in df.columns and "order_delivered_carrier_date" in df.columns:
        df["carrier_transit_days"] = (
            df["order_delivered_customer_date"] - df["order_delivered_carrier_date"]
        ).dt.total_seconds() / 86400.0

    # Checking the Purchase Timing 
    if "order_purchase_timestamp" in df.columns: 
        df["purchase_hour"] = df["order_purchase_timestamp"].dt.hour
        df["purchase_day_of_week"] = df["order_purchase_timestamp"].dt.day_name()
        df["purchase_month"] = df["order_purchase_timestamp"].dt.month

    # Calculating Delivery Estimation 
    if "order_estimated_delivery_date" in df.columns and "order_purchase_timestamp" in df.columns:
        df["estimated_delivery_duration_days"] = (
            df["order_estimated_delivery_date"] - df["order_purchase_timestamp"]
        ).dt.total_seconds() / 86400.0

    # Cleaning Order Status
    if "order_status" in df.columns:
        df["order_status"] = df["order_status"].astype(str).str.lower().str.strip()

    final_row_count = len(df)
    print(f"Final Row Count: {final_row_count}")

    # Exporting the Clean Data to csv
    output_path = os.path.join(processed_dir, "orders_cleaned.csv")
    df.to_csv(output_path, index=False)
    print("Cleaned Orders Dataset Created")

if __name__ == "__main__":
    clean_orders_data()