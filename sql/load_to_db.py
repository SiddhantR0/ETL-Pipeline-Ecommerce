# Importing
import os
import sqlite3
import pandas as pd

# Loading Into Database
def load_processed_data_to_db():
    processed_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/processed"))
    db_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/database"))
    os.makedirs(db_dir, exist_ok=True)
    
    db_path = os.path.join(db_dir, "olist.db")
    print(f"Connecting to SQLite database at: {db_path}")
    
    conn = sqlite3.connect(db_path)
    
    datasets = {
        "customers_cleaned.csv": "customers",
        "sellers_cleaned.csv": "sellers",
        "products_cleaned.csv": "products",
        "geolocation_cleaned.csv": "geolocation",
        "orders_cleaned.csv": "orders",
        "order_items_cleaned.csv": "order_items",
        "order_reviews_cleaned.csv": "order_reviews",
        "order_payments_cleaned.csv": "order_payments"
    }
    
    for filename, table_name in datasets.items():
        file_path = os.path.join(processed_dir, filename)
        
        if os.path.exists(file_path):
            print(f"Loading {filename} into table '{table_name}'")
            df = pd.read_csv(file_path)
        
            df.to_sql(table_name, conn, if_exists="replace", index=False)
            print(f"Successfully Loaded {len(df):,} rows into '{table_name}'")
        else:
            print(f"{filename} not found in {processed_dir}")
            
    conn.close()
    print("All Processed Datasets Successfully Loaded into the SQLite Database")

if __name__ == "__main__":
    load_processed_data_to_db()
