# Importing
import os
import pandas as pd
import numpy as np

# Cleaning Geolocation Data
def clean_geolocation_data():
    raw_dir = "data/raw"
    processed_dir = "data/processed"
    os.makedirs(processed_dir, exist_ok=True)

    file_path = os.path.join(raw_dir, "olist_geolocation_dataset.csv")
    print("Loading the Clean Geolocation Dataset")

    # Checking if Raw Dataset Exists
    if not os.path.exists(file_path):
        print("Error! Dataset Not Found")
        return

    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip()

    initial_row_count = len(df)
    print(f"Initial Row Count: {initial_row_count}")

    # Standardizing Zip Code Prefix  
    if "geolocation_zip_code_prefix" in df.columns:
        df["geolocation_zip_code_prefix"] = pd.to_numeric(df["geolocation_zip_code_prefix"], errors='coerce')
        df["geolocation_zip_code_prefix"] = df["geolocation_zip_code_prefix"].fillna(0)
        df["geolocation_zip_code_prefix"] = df["geolocation_zip_code_prefix"].astype(int).astype(str).str.zfill(5)

    # Cleaning City and State Text
    if "geolocation_city" in df.columns:
        df["geolocation_city"] = df["geolocation_city"].fillna("Unknown")
        df["geolocation_city"] = df["geolocation_city"].astype(str).str.strip().str.replace(r"\s+", " ", regex=True).str.title()

    if "geolocation_state" in df.columns:
        df["geolocation_state"] = df["geolocation_state"].fillna("Unknown")
        df["geolocation_state"] = df["geolocation_state"].astype(str).str.strip().str.upper()

    # Filtering Outlier Coordinates 
    if "geolocation_lat" in df.columns and "geolocation_lng" in df.columns:
        valid_lat = (df["geolocation_lat"] >= -35.0) & (df["geolocation_lat"] <= 5.0)
        valid_lng = (df["geolocation_lng"] >= -74.0) & (df["geolocation_lng"] <= -32.0)
        
        outliers_count = ~(valid_lat & valid_lng)
        df = df[valid_lat & valid_lng]

    # Calculating Dispersion and Aggregating Centroids
    agg_funcs = {
        "geolocation_lat": ["median", "std"],
        "geolocation_lng": ["median", "std"],
        "geolocation_city": lambda x: x.mode()[0] if not x.mode().empty else "Unknown",
        "geolocation_state": lambda x: x.mode()[0] if not x.mode().empty else "Unknown",
        "geolocation_zip_code_prefix": "count"  
    }
    
    df_clean = df.groupby("geolocation_zip_code_prefix").agg(agg_funcs)
    
    df_clean.columns = [
        "geolocation_centroid_lat", 
        "geolocation_lat_std", 
        "geolocation_centroid_lng", 
        "geolocation_lng_std", 
        "geolocation_city", 
        "geolocation_state", 
        "geolocation_points_density_count"
    ]
    
    df_clean = df_clean.reset_index()

    # Filling NaN Values
    df_clean["geolocation_lat_std"] = df_clean["geolocation_lat_std"].fillna(0.0)
    df_clean["geolocation_lng_std"] = df_clean["geolocation_lng_std"].fillna(0.0)

    # Area Classification
    df_clean["geolocation_spatial_spread"] = np.sqrt(
        df_clean["geolocation_lat_std"]**2 + df_clean["geolocation_lng_std"]**2
    )

    # Classifying Zone Density
    def classify_zone_type(row):
        if row["geolocation_points_density_count"] > 50 and row["geolocation_spatial_spread"] < 0.05:
            return "urban area"
        elif row["geolocation_points_density_count"] > 10:
            return "metropolitan area"
        else:
            return "rural area"

    df_clean["geolocation_zone_type"] = df_clean.apply(classify_zone_type, axis=1)

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

    if "geolocation_state" in df_clean.columns:
        df_clean["geolocation_region"] = df_clean["geolocation_state"].apply(map_brazilian_regions)

    final_row_count = len(df_clean)
    print(f"Final Row Count (Unique Zip Codes): {final_row_count}")

    # Exporting the Clean Data to csv
    output_path = os.path.join(processed_dir, "geolocation_cleaned.csv")
    df_clean.to_csv(output_path, index=False)
    print("Cleaned Geolocation Dataset Created")

if __name__ == "__main__":
    clean_geolocation_data()