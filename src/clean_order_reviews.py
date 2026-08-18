# Importing
import os
import pandas as pd
import numpy as np

# Cleaning Order Reviews Data
def clean_order_reviews_data():
    raw_dir = "data/raw"
    processed_dir = "data/processed"
    os.makedirs(processed_dir, exist_ok=True)

    file_path = os.path.join(raw_dir, "olist_order_reviews_dataset.csv")
    print("Loading the Clean Order Reviews Dataset")

    # Checking if Raw Dataset Exists
    if not os.path.exists(file_path):
        print("Error! Dataset Not Found")
        return

    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip()

    initial_row_count = len(df)
    print(f"Initial Row Count: {initial_row_count}")

    # Handling Missing Values
    if "review_id" in df.columns and "order_id" in df.columns:
        df = df.dropna(subset=["review_id", "order_id"])

    df.drop_duplicates(subset=["review_id"], inplace=True)

    # Handling Missing Review Titles (Olist dataset uses review_comment_title)
    title_col = "review_comment_title" if "review_comment_title" in df.columns else "review_title"
    if title_col in df.columns:
        df[title_col] = df[title_col].fillna("No Title")
        df[title_col] = df[title_col].astype(str).str.strip().str.replace(r"\s+", " ", regex=True)
        if title_col != "review_title":
            df.rename(columns={title_col: "review_title"}, inplace=True)
    else:
        df["review_title"] = "No Title"

    # Handling Missing Review Messages (Olist dataset uses review_comment_message)
    msg_col = "review_comment_message" if "review_comment_message" in df.columns else "review_message"
    if msg_col in df.columns:
        df[msg_col] = df[msg_col].fillna("No Message")
        df[msg_col] = df[msg_col].astype(str).str.strip().str.replace(r"\s+", " ", regex=True)
        if msg_col != "review_message":
            df.rename(columns={msg_col: "review_message"}, inplace=True)
    else:
        df["review_message"] = "No Message"

    # Parsing Timestamps
    date_cols = ["review_creation_date", "review_answer_timestamp"]
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # Review Response Delay Calculation
    if "review_creation_date" in df.columns and "review_answer_timestamp" in df.columns:
        df["review_response_delay_hours"] = (
            df["review_answer_timestamp"] - df["review_creation_date"]
        ).dt.total_seconds() / 3600.0

        median_delay = df["review_response_delay_hours"].median()
        df["review_response_delay_hours"] = df["review_response_delay_hours"].fillna(median_delay)

    # Review Score Categorization 
    if "review_score" in df.columns:
        df["review_score"] = pd.to_numeric(df["review_score"], errors="coerce").fillna(3).astype(int)
        
        def categorize_score(score):
            if score >= 4:
                return "Positive"
            elif score == 3:
                return "Neutral"
            else:
                return "Negative"
                
        df["review_sentiment_category"] = df["review_score"].apply(categorize_score)

    final_row_count = len(df)
    print(f"Final Row Count: {final_row_count}")

    # Exporting the Clean Data to csv
    output_path = os.path.join(processed_dir, "order_reviews_cleaned.csv")
    df.to_csv(output_path, index=False)
    print("Cleaned Order Reviews Dataset Created")

if __name__ == "__main__":
    clean_order_reviews_data()