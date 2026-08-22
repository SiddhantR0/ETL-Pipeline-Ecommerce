# Importing
import os
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")
plt.rcParams.update({'figure.autolayout': True})

def analyze_sellers():
    # Establishing Database Connection
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/database/olist.db"))
    conn = sqlite3.connect(db_path)

    # Retrieving Seller Metrics, Order Volume, Fulfillment Duration, and Review Scores
    query = """
        SELECT 
            s.seller_id,
            s.seller_state,
            oi.order_id,
            oi.price,
            oi.freight_value,
            julianday(o.order_delivered_customer_date) - julianday(o.order_purchase_timestamp) AS fulfillment_duration_days,
            julianday(o.order_delivered_customer_date) - julianday(o.order_estimated_delivery_date) AS delivery_delay_days,
            r.review_score
        FROM sellers s
        JOIN order_items oi ON s.seller_id = oi.seller_id
        JOIN orders o ON oi.order_id = o.order_id
        LEFT JOIN order_reviews r ON oi.order_id = r.order_id
        WHERE o.order_delivered_customer_date IS NOT NULL;
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    # Compute Seller Revenue and Volume Performance
    seller_summary = df.groupby('seller_id').agg({
        'price': ['sum', 'mean', 'count'],
        'fulfillment_duration_days': 'mean',
        'delivery_delay_days': lambda x: (x > 0).mean() * 100,
        'review_score': 'mean',
        'seller_state': 'first'
    }).round(2)

    seller_summary.columns = ['Total Revenue', 'Avg Item Price', 'Item Count', 'Avg Fulfillment Days', 'Delay Rate (%)', 'Avg Review Score', 'State']
    
    # Reset index so 'seller_id' and 'State' are regular columns for downstream grouping
    seller_summary = seller_summary.reset_index()
    
    # Calculate State-Level Seller Distribution
    state_summary = seller_summary.groupby('State').agg({
        'Total Revenue': 'sum',
        'Item Count': 'sum',
        'seller_id': 'count',
        'Avg Review Score': 'mean'
    }).round(2)
    state_summary.columns = ['Total Revenue', 'Item Count', 'Seller Count', 'Avg Review Score']
    state_summary = state_summary.sort_values('Total Revenue', ascending=False)

    # Classify Sellers by Volume Tiers
    seller_summary['Volume Tier'] = pd.qcut(
        seller_summary['Item Count'],
        q=4,
        labels=['Low Volume', 'Medium Volume', 'High Volume', 'Top Volume']
    )
    tier_summary = seller_summary.groupby('Volume Tier', observed=False).agg({
        'Total Revenue': 'mean',
        'Avg Review Score': 'mean',
        'Delay Rate (%)': 'mean',
        'Item Count': 'count'
    }).round(2)
    tier_summary.columns = ['Avg Revenue', 'Avg Review Score', 'Avg Delay Rate (%)', 'Seller Count']

    # Generate and Save the Visualization 
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # Panel 1: Top 10 Sellers by Revenue
    top_10_sellers = seller_summary.sort_values('Total Revenue', ascending=False).head(10).sort_values('Total Revenue', ascending=True)
    axes[0, 0].barh(range(len(top_10_sellers)), top_10_sellers['Total Revenue'], color='steelblue')
    axes[0, 0].set_yticks(range(len(top_10_sellers)))
    axes[0, 0].set_yticklabels([f"Seller ...{sid[-6:]}" for sid in top_10_sellers['seller_id']], fontsize=9)
    axes[0, 0].set_title("Top 10 Sellers by Gross Revenue", fontsize=14, fontweight="bold")
    axes[0, 0].set_xlabel("Total Revenue (R$)", fontsize=12)
    axes[0, 0].set_ylabel("Seller ID (Suffix)", fontsize=12)
    
    # Panel 2: Seller Revenue by State (Top 5 States)
    top_states = state_summary.head(5)
    axes[0, 1].bar(top_states.index, top_states['Total Revenue'], color='mediumseagreen')
    axes[0, 1].set_title("Top 5 Seller States by Revenue", fontsize=14, fontweight="bold")
    axes[0, 1].set_xlabel("State", fontsize=12)
    axes[0, 1].set_ylabel("Total Revenue (R$)", fontsize=12)
    
    # Panel 3: Fulfillment Duration vs Review Score
    axes[1, 0].scatter(df['fulfillment_duration_days'], df['review_score'], alpha=0.15, s=10, color='darkorange')
    axes[1, 0].set_title("Fulfillment Duration vs Review Score", fontsize=14, fontweight="bold")
    axes[1, 0].set_xlabel("Fulfillment Duration (Days)", fontsize=12)
    axes[1, 0].set_ylabel("Review Score", fontsize=12)
    axes[1, 0].set_xlim(0, 60)
    
    # Panel 4: Delay Rate vs Average Review Score by Seller
    axes[1, 1].scatter(seller_summary['Delay Rate (%)'], seller_summary['Avg Review Score'], alpha=0.3, s=15, color='mediumpurple')
    axes[1, 1].set_title("Seller Delay Rate (%) vs Average Review Score", fontsize=14, fontweight="bold")
    axes[1, 1].set_xlabel("Delay Rate (%)", fontsize=12)
    axes[1, 1].set_ylabel("Average Review Score", fontsize=12)
    axes[1, 1].set_ylim(0, 5.5)
    
    plt.tight_layout()
    
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/output"))
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "sellers_analysis.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    # Print Executive Summary
    print_summary(df, seller_summary, state_summary, tier_summary, output_path)


def print_summary(df, seller_summary, state_summary, tier_summary, output_path):
    """
    Prints a comprehensive executive summary of the seller performance analysis.
    All metrics are presented in a clean, formatted structure for reporting purposes.
    """

    print("\n" + "=" * 70)
    print("EXECUTIVE SUMMARY: SELLER PERFORMANCE AND FULFILLMENT ANALYSIS")
    print("=" * 70)

    print("\nTOP 10 SELLERS BY REVENUE")
    print("-" * 70)
    top_sellers_display = seller_summary.sort_values('Total Revenue', ascending=False).head(10)
    print(top_sellers_display[['seller_id', 'Total Revenue', 'Item Count', 'Avg Review Score', 'Delay Rate (%)', 'State']].to_string(index=False))

    print("\nSELLER PERFORMANCE BY STATE (TOP 10)")
    print("-" * 70)
    print(state_summary.head(10).to_string())

    print("\nSELLER VOLUME TIER BENCHMARKS")
    print("-" * 70)
    print(tier_summary.to_string())

    print("\nMACRO SELLER METRICS")
    print("-" * 70)
    print(f"Total Unique Sellers Evaluated: {len(seller_summary):,}")
    print(f"Total Items Sold Across Sellers: {len(df):,}")
    print(f"Overall Average Fulfillment Duration: {df['fulfillment_duration_days'].mean():.2f} days")
    print(f"Overall Average Seller Review Score: {df['review_score'].mean():.2f} / 5.0")

    print("\nOUTPUT FILES")
    print("-" * 70)
    print(f"Visualization saved to: {output_path}")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    analyze_sellers()