# Importing
import os
import sys
import logging
from src.clean_customer import clean_customer_data
from src.clean_sellers import clean_sellers_data
from src.clean_products import clean_products_data
from src.clean_geolocation import clean_geolocation_data
from src.clean_orders import clean_orders_data
from src.clean_order_items import clean_order_items
from src.clean_order_reviews import clean_order_reviews_data
from src.clean_order_payments import clean_order_payments_data

# Setting up Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Main Function for Running
def run_pipeline():
    logging.info("Starting ETL Pipeline")
    
    tasks = [
        ("Customers", clean_customer_data),
        ("Sellers", clean_sellers_data),
        ("Products", clean_products_data),
        ("Geolocation", clean_geolocation_data),
        ("Orders", clean_orders_data),
        ("Order Items", clean_order_items),
        ("Order Reviews", clean_order_reviews_data),
        ("Order Payments", clean_order_payments_data)
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