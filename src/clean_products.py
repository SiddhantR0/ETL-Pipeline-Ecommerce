# Importing
import os
import pandas as pd
import numpy as np 

# Cleaning Products Data
def clean_products_data():
    raw_dir = "data/raw"
    processed_dir = "data/processed"
    os.makedirs(processed_dir, exist_ok=True)

    file_path = os.path.join(raw_dir, "olist_products_dataset.csv")
    translation_path = os.path.join(raw_dir, "product_category_name_translation.csv")
    print("Loading the Clean Product And Product Translation Dataset")

    # Checking if Raw Dataset Exists
    if not os.path.exists(file_path):
        print("Error! Dataset Not Found")
        return

    df = pd.read_csv(file_path)

    df.columns = df.columns.str.strip()

    initial_row_count = len(df)
    print(f"Initial Row Count: {initial_row_count}")

    # Handling Duplicate Values
    df.drop_duplicates(subset=["product_id"], inplace=True)

    # Cleaning Category Name Text
    if "product_category_name" in df.columns:
        df["product_category_name"] = df["product_category_name"].fillna("Unknown")
        df["product_category_name"] = df["product_category_name"].astype(str).str.replace("_", " ").str.lower().str.strip()

    # Merging Translation iff Available
    if os.path.exists(translation_path):
        print("Merging Product Category Translation")
        trans_df = pd.read_csv(translation_path)
        trans_df.columns = trans_df.columns.str.strip()

        trans_df["product_category_name"] = trans_df["product_category_name"].astype(str).str.replace("_"," ").str.lower().str.strip()
        trans_df["product_category_name_english"] = trans_df["product_category_name_english"].astype(str).str.replace("_"," ").str.lower().str.strip()

        df = df.merge(trans_df, on="product_category_name", how="left")
        df["product_category_name_english"] = df["product_category_name_english"].fillna("Unknown")

    # Assigning Missing Dimensions and Weights
    dimension_cols = [
        "product_name_lenght",
        "product_description_lenght",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm"
    ]

    for col in dimension_cols:
        if col in df.columns:
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)

    # Calculations
    df["product_volume_cm3"] = df["product_length_cm"] * df["product_height_cm"] * df["product_width_cm"]
    df["product_volumetric_weight_g"] = df["product_volume_cm3"] / 5.0
    df["product_chargeable_weight_g"] = np.maximum(df["product_weight_g"], df["product_volumetric_weight_g"])

    # Density Calculation (Calculated AFTER volume exists)
    df["product_density_g_cm3"] = np.where(
        df["product_volume_cm3"] > 0,
        df["product_weight_g"] / df["product_volume_cm3"],
        0
    )

    # Categorizing Product Sizes in Tiers
    def size_tiers(volume):
        if volume < 1000:
            return "small"
        elif volume < 10000:
            return "medium"
        elif volume < 50000:
            return "large"
        else:
            return "bulky"

    df["product_size_tier"] = df["product_volume_cm3"].apply(size_tiers)

    # Categorizing Photo Counts 
    def photo_tiers(quantity):
        if quantity == 0:
            return "no photos"
        elif quantity <= 2:
            return "low amount of photos"
        elif quantity <= 5:
            return "medium amount of photos"
        else:
            return "high amount of photos"

    if "product_photos_qty" in df.columns:
        df["product_photo_tier"] = df["product_photos_qty"].apply(photo_tiers)

    final_row_count = len(df)
    print(f"Final Row Count: {final_row_count}")

    # Exporting the Clean Data to csv
    output_path = os.path.join(processed_dir, "products_cleaned.csv")
    df.to_csv(output_path, index=False)
    print("Cleaned Product Dataset Created")

if __name__ == "__main__":
    clean_products_data()