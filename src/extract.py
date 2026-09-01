import os
import tarfile
import logging

def extract_data():
    raw_dir = "data/raw"
    os.makedirs(raw_dir, exist_ok=True)

    expected_files = [
        "olist_customers_dataset.csv",
        "olist_geolocation_dataset.csv",
        "olist_order_items_dataset.csv",
        "olist_order_payments_dataset.csv",
        "olist_order_reviews_dataset.csv",
        "olist_orders_dataset.csv",
        "olist_products_dataset.csv",
        "olist_sellers_dataset.csv"
    ]
    
    all_files_exist = all(os.path.exists(os.path.join(raw_dir, f)) for f in expected_files)

    if all_files_exist:
        logging.info("Raw datasets already extracted. Skipping.")
        return

    tar_path = os.path.join(raw_dir, "olist_data.tar.gz")
    
    if os.path.exists(tar_path):
        logging.info("Local tarball found. Extracting data...")
        with tarfile.open(tar_path, "r:gz") as tar_ref:
            tar_ref.extractall(path=raw_dir)
        logging.info("Extraction Complete!")
    else:
        logging.error("Fatal: olist_data.tar.gz not found in data/raw/")
        raise FileNotFoundError("olist_data.tar.gz is missing from the repository.")

if __name__ == "__main__": 
    extract_data()