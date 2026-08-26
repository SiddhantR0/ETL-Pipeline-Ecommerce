# Importing
import os
import sys
import logging
import zipfile
from kaggle.api.kaggle_api_extended import KaggleApi

from src.clean_customer import clean_customer_data
from src.clean_sellers import clean_sellers_data
from src.clean_products import clean_products_data
from src.clean_geolocation import clean_geolocation_data
from src.clean_orders import clean_orders_data
from src.clean_order_items import clean_order_items
from src.clean_order_reviews import clean_order_reviews_data
from src.clean_order_payments import clean_order_payments_data

from sql.analyze_order_and_logistics import analyze_logistics
from sql.analyze_products_revenue import analyze_products_and_revenue
from sql.analyze_payments import analyze_payments
from sql.analyze_sellers import analyze_sellers
from sql.analyze_customers_geography import analyze_customers_geography
from sql.analyze_geolocation import analyze_geolocation

# Setting up Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Extracting Data
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
        print("All Datasets Already Exists")
        return

    # Authenticating w/ Kaggle API
    print("Authenticating with Kaggle API")
    api = KaggleApi()
    api.authenticate()

    # Downloading Dataset
    print("Downloading Dataset From Kaggle")
    api.dataset_download_files('olistbr/brazilian-ecommerce', path=raw_dir, unzip=False)

    # Unzipping Dataset
    zip_path = os.path.join(raw_dir, "brazilian-ecommerce.zip")
    if os.path.exists(zip_path):
        print("Extracting Zip File")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(raw_dir)
        os.remove(zip_path)
        print("Extraction Complete")
    else:
        raise FileNotFoundError("Zip File Not Found")

# Main Function for Running
def run_pipeline():
    logging.info("Starting ETL Pipeline Setup")
    
    try:
        extract_data()
    except Exception as e:
        logging.error(f"Failed to extract datasets: {e}")
        sys.exit(1)

    logging.info("Starting ETL Pipeline Execution")
    
    tasks = [
        ("Customers", clean_customer_data),
        ("Sellers", clean_sellers_data),
        ("Products", clean_products_data),
        ("Geolocation", clean_geolocation_data),
        ("Orders", clean_orders_data),
        ("Order Items", clean_order_items),
        ("Order Reviews", clean_order_reviews_data),
        ("Order Payments", clean_order_payments_data),
        ("Logistics Analysis", analyze_logistics),
        ("Products & Revenue Analysis", analyze_products_and_revenue),
        ("Payments Analysis", analyze_payments),
        ("Sellers Performance Analysis", analyze_sellers),
        ("Customer Geography Analysis", analyze_customers_geography),
        ("Geolocation Spatial Analysis", analyze_geolocation)
    ]
    
    for task_name, task_func in tasks:
        try:
            logging.info(f"Running Cleaning Module: {task_name}")
            task_func()
            logging.info(f"Completed: {task_name}")
        except Exception as e:
            logging.error(f"Failure in {task_name}: {e}")
            sys.exit(1) 

    logging.info("ETL Pipeline Execution Finished Successfully.")

if __name__ == "__main__":
    run_pipeline()