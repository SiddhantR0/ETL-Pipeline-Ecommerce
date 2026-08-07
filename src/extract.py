# Importing
import os
import zipfile
from kaggle.api.kaggle_api_extended import KaggleApi
from pandas import api 

# Extracting Data
def extract_data():
    raw_dir = "data/raw"
    os.makedirs(raw_dir, exist_ok=True)

    # Checking if Data Already Exists
    if os.path.exists(os.path.join(raw_dir,"olist_customers_dataset.csv")):
        print("Data Already Exists")
        return

    # Authenticating w/ Kaggle API
    print("Authenticating with Kaggle API")
    api = KaggleApi()
    api.authenticate()

    # Downloading Dataset
    print("Downloading Dataset From Kaggle")
    api.dataset_download_files('olistbr/brazilian-ecommerce',path= raw_dir, unzip=False)

    # Unzipping Dataset
    zip_path = os.path.join(raw_dir,"brazilian-ecommerce.zip")
    if os.path.exists(zip_path):
        print("Extracting Zip File")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(raw_dir)
        os.remove(zip_path)
        print("Extraction Complete")
    else:
        raise FileNotFoundError("Zip File Not Found")

if __name__ == "__main__":
    extract_data()