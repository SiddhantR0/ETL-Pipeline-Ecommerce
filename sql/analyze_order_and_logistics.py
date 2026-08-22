# Importing
import os
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")
plt.rcParams.update({'figure.autolayout': True})

def analyze_logistics():
    # Establishing Database Connection
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/database/olist.db"))
    conn = sqlite3.connect(db_path)

    # Retrieving Order Logistics, Timestamps, Delivery Performance, and Review Scores
    query = """
        SELECT 
            o.order_id,
            c.customer_state,
            julianday(o.order_delivered_customer_date) - julianday(o.order_purchase_timestamp) AS fulfillment_duration_days,
            julianday(o.order_estimated_delivery_date) - julianday(o.order_purchase_timestamp) AS estimated_duration_days,
            julianday(o.order_delivered_customer_date) - julianday(o.order_estimated_delivery_date) AS delivery_delay_days,
            r.review_score
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        LEFT JOIN order_reviews r ON o.order_id = r.order_id
        WHERE o.order_delivered_customer_date IS NOT NULL 
          AND o.order_purchase_timestamp IS NOT NULL;
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    # Calculate Delivery Status Categorization
    df['delivery_status'] = df['delivery_delay_days'].apply(
        lambda x: 'Early / On-Time' if x <= 0 else 'Delayed'
    )

    # Compute State-Level Logistics Summary
    state_summary = df.groupby('customer_state').agg({
        'order_id': 'count',
        'fulfillment_duration_days': 'mean',
        'delivery_delay_days': lambda x: (x > 0).mean() * 100,
        'review_score': 'mean'
    }).round(2)

    state_summary.columns = ['Total Orders', 'Avg Fulfillment Days', 'Delay Rate (%)', 'Avg Review Score']
    state_summary = state_summary.sort_values('Avg Fulfillment Days', ascending=False)

    # Status Breakdown Share
    status_counts = df['delivery_status'].value_counts()

    # Generate and Save the 4-Panel Visualization 
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # Panel 1: Distribution of Fulfillment Duration (Days)
    sns.histplot(df['fulfillment_duration_days'].clip(upper=45), bins=45, ax=axes[0, 0], color='dodgerblue', kde=True)
    axes[0, 0].set_title("Distribution of Actual Fulfillment Duration (Capped at 45 Days)", fontsize=14, fontweight="bold")
    axes[0, 0].set_xlabel("Fulfillment Duration (Days)", fontsize=12)
    axes[0, 0].set_ylabel("Order Frequency", fontsize=12)
    
    # Panel 2: Delivery Performance Breakdown (On-Time vs Delayed)
    axes[0, 1].pie(
        status_counts.values, 
        labels=status_counts.index, 
        autopct='%1.1f%%', 
        colors=['mediumseagreen', 'indianred'], 
        startangle=90,
        textprops={'fontsize': 12, 'fontweight': 'bold'}
    )
    axes[0, 1].set_title("Overall Delivery Performance Share", fontsize=14, fontweight="bold")
    
    # Panel 3: Top 10 States with Longest Average Fulfillment Duration
    top_states_duration = state_summary.head(10).sort_values('Avg Fulfillment Days', ascending=True)
    axes[1, 0].barh(top_states_duration.index, top_states_duration['Avg Fulfillment Days'], color='darkorange')
    axes[1, 0].set_title("Top 10 States by Longest Average Fulfillment Duration", fontsize=14, fontweight="bold")
    axes[1, 0].set_xlabel("Average Fulfillment Days", fontsize=12)
    axes[1, 0].set_ylabel("Customer State", fontsize=12)
    
    # Panel 4: Fulfillment Duration vs Review Score
    sample_df = df.sample(n=min(10000, len(df)), random_state=42)
    axes[1, 1].scatter(sample_df['fulfillment_duration_days'], sample_df['review_score'], alpha=0.2, s=15, color='mediumpurple')
    axes[1, 1].set_title("Fulfillment Duration vs. Customer Review Score", fontsize=14, fontweight="bold")
    axes[1, 1].set_xlabel("Fulfillment Duration (Days)", fontsize=12)
    axes[1, 1].set_ylabel("Review Score (1-5)", fontsize=12)
    axes[1, 1].set_xlim(0, 50)
    axes[1, 1].set_ylim(0.5, 5.5)
    
    plt.tight_layout()
    
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/output"))
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "logistics_analysis.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    # Print Executive Summary
    print_summary(df, state_summary, status_counts, output_path)


def print_summary(df, state_summary, status_counts, output_path):
    """
    Prints a comprehensive executive summary of the logistics and delivery performance analysis.
    All metrics are presented in a clean, formatted structure for reporting purposes.
    """

    print("\n" + "=" * 70)
    print("EXECUTIVE SUMMARY: ORDER LOGISTICS & DELIVERY PERFORMANCE ANALYSIS")
    print("=" * 70)

    print("\nSTATE-LEVEL LOGISTICS PERFORMANCE (TOP 10 LONGEST FULFILLMENT)")
    print("-" * 70)
    print(state_summary.head(10).to_string())

    print("\nDELIVERY STATUS BREAKDOWN")
    print("-" * 70)
    total_orders = len(df)
    for status, count in status_counts.items():
        pct = (count / total_orders) * 100
        print(f"{status}: {count:,} orders ({pct:.2f}%)")

    print("\nMACRO LOGISTICS METRICS")
    print("-" * 70)
    print(f"Total Delivered Orders Analyzed: {total_orders:,}")
    print(f"Overall Average Fulfillment Duration: {df['fulfillment_duration_days'].mean():.2f} days")
    print(f"Overall Average Estimated Duration: {df['estimated_duration_days'].mean():.2f} days")
    print(f"Overall Average Delivery Delay: {df['delivery_delay_days'].mean():.2f} days")
    print(f"Overall Average Customer Review Score: {df['review_score'].mean():.2f} / 5.0")

    print("\nOUTPUT FILES")
    print("-" * 70)
    print(f"Visualization saved to: {output_path}")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    analyze_logistics()