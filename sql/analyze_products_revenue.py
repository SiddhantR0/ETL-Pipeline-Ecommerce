# Importing
import os
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")
plt.rcParams.update({'figure.autolayout': True})

def analyze_products_and_revenue():
    # Establishing Database Connection
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/database/olist.db"))
    conn = sqlite3.connect(db_path)

    # Retrieving Product Performance, Pricing and Satisfaction Data
    query = """
        SELECT 
            p.product_id,
            p.product_category_name AS product_category,
            p.product_name_lenght AS product_name_length,
            p.product_description_lenght AS product_description_length,
            p.product_photos_qty,
            p.product_weight_g,
            p.product_length_cm,
            p.product_height_cm,
            p.product_width_cm,
            oi.order_id,
            oi.price,
            oi.freight_value,
            oi.shipping_limit_date,
            r.review_score
        FROM products p
        JOIN order_items oi ON p.product_id = oi.product_id
        LEFT JOIN order_reviews r ON oi.order_id = r.order_id
        WHERE oi.price IS NOT NULL;
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    # Compute Category Revenue and Volume Metrics
    category_revenue = df.groupby('product_category').agg({
        'price': ['sum', 'mean', 'count'],
        'review_score': 'mean'
    }).round(2)

    category_revenue.columns = ['Total Revenue', 'Avg Price', 'Order Count', 'Avg Review Score']
    category_revenue = category_revenue.sort_values('Total Revenue', ascending=False)

    # Calculate Revenue Concentration
    total_revenue = df['price'].sum()
    category_revenue['Revenue Share (%)'] = (category_revenue['Total Revenue'] / total_revenue) * 100
    category_revenue['Cumulative Share (%)'] = category_revenue['Revenue Share (%)'].cumsum()

    # Compute Price Distribution and Outlier Detection
    q1 = df['price'].quantile(0.25)
    q3 = df['price'].quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    outliers_high = len(df[df['price'] > upper_bound])
    outliers_low = len(df[df['price'] < lower_bound])

    # Segment Prices into Quintiles for Satisfaction Analysis
    df['price_quintile'] = pd.qcut(
        df['price'], 
        q=5, 
        labels=['Lowest Price', 'Low Price', 'Medium Price', 'High Price', 'Highest Price']
    )
    price_review = df.groupby('price_quintile', observed=False)['review_score'].agg(['mean', 'count']).round(2)
    price_review.columns = ['Avg Review Score', 'Order Count']

    # Classify Categories into Performance Groups
    revenue_median = category_revenue['Total Revenue'].median()
    satisfaction_median = category_revenue['Avg Review Score'].median()
    
    category_revenue['Performance Group'] = 'Other'
    category_revenue.loc[
        (category_revenue['Total Revenue'] > revenue_median) & 
        (category_revenue['Avg Review Score'] > satisfaction_median),
        'Performance Group'
    ] = 'Star Performer'
    category_revenue.loc[
        (category_revenue['Total Revenue'] <= revenue_median) & 
        (category_revenue['Avg Review Score'] > satisfaction_median),
        'Performance Group'
    ] = 'Satisfaction Leader'
    category_revenue.loc[
        (category_revenue['Total Revenue'] > revenue_median) & 
        (category_revenue['Avg Review Score'] <= satisfaction_median),
        'Performance Group'
    ] = 'Revenue Driver'
    category_revenue.loc[
        (category_revenue['Total Revenue'] <= revenue_median) & 
        (category_revenue['Avg Review Score'] <= satisfaction_median),
        'Performance Group'
    ] = 'Underperformer'

    star_categories = category_revenue[category_revenue['Performance Group'] == 'Star Performer']

    # Analyze Freight Economics
    df['freight_ratio'] = df['freight_value'] / df['price']
    high_freight_categories = df.groupby('product_category')['freight_ratio'].mean().sort_values(ascending=False).head(5)

    # Generate and Save the Visualization 
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # Panel 1: Top 10 Categories by Revenue
    top_10_revenue = category_revenue.head(10).sort_values('Total Revenue', ascending=True)
    axes[0, 0].barh(top_10_revenue.index, top_10_revenue['Total Revenue'], color='steelblue')
    axes[0, 0].set_title("Top 10 Product Categories by Revenue", fontsize=14, fontweight="bold")
    axes[0, 0].set_xlabel("Total Revenue (R$)", fontsize=12)
    axes[0, 0].set_ylabel("Product Category", fontsize=12)
    
    # Panel 2: Price Distribution
    axes[0, 1].hist(df['price'], bins=50, color='lightblue', edgecolor='black', alpha=0.7)
    axes[0, 1].axvline(df['price'].mean(), color='red', linestyle='--', label=f'Mean: R${df["price"].mean():.2f}')
    axes[0, 1].axvline(df['price'].median(), color='green', linestyle='--', label=f'Median: R${df["price"].median():.2f}')
    axes[0, 1].set_title("Price Distribution Across All Orders", fontsize=14, fontweight="bold")
    axes[0, 1].set_xlabel("Price (R$)", fontsize=12)
    axes[0, 1].set_ylabel("Frequency (Log Scale)", fontsize=12)
    axes[0, 1].legend()
    axes[0, 1].set_yscale('log')
    
    # Panel 3: Price vs Review Score
    axes[1, 0].scatter(df['price'], df['review_score'], alpha=0.2, s=10, color='navy')
    axes[1, 0].set_title("Price vs Customer Satisfaction", fontsize=14, fontweight="bold")
    axes[1, 0].set_xlabel("Price (R$ - Log Scale)", fontsize=12)
    axes[1, 0].set_ylabel("Review Score", fontsize=12)
    axes[1, 0].set_xscale('log')
    
    # Panel 4: Average Review by Price Quintile
    price_review_sorted = price_review.reset_index()
    axes[1, 1].bar(price_review_sorted['price_quintile'], price_review_sorted['Avg Review Score'], color='teal')
    axes[1, 1].axhline(y=df['review_score'].mean(), color='red', linestyle='--', label=f'Overall Mean: {df["review_score"].mean():.2f}')
    axes[1, 1].set_title("Average Review Score by Price Quintile", fontsize=14, fontweight="bold")
    axes[1, 1].set_xlabel("Price Quintile", fontsize=12)
    axes[1, 1].set_ylabel("Average Review Score", fontsize=12)
    axes[1, 1].set_ylim(0, 5.5)
    axes[1, 1].legend()
    
    plt.tight_layout()
    
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/output"))
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "products_revenue_analysis.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    # Print Executive Summary
    print_summary(df, category_revenue, total_revenue, price_review, 
                  star_categories, high_freight_categories, output_path)


def print_summary(df, category_revenue, total_revenue, price_review,
                  star_categories, high_freight_categories, output_path):
    """
    Prints a comprehensive executive summary of the product and revenue analysis.
    All metrics are presented in a clean, formatted structure for reporting purposes.
    """

    print("\n" + "=" * 70)
    print("EXECUTIVE SUMMARY: PRODUCT AND REVENUE ANALYSIS")
    print("=" * 70)

    print("\nTOP 10 PRODUCT CATEGORIES BY REVENUE")
    print("-" * 70)
    print(category_revenue.head(10).to_string())

    print("\nREVENUE CONCENTRATION ANALYSIS")
    print("-" * 70)
    print(f"Total Revenue Across All Orders: R${total_revenue:,.2f}")
    print(f"Number of Categories with Revenue: {len(category_revenue)}")
    print(f"Top 5 Categories Revenue Share: {category_revenue['Cumulative Share (%)'].iloc[4]:.1f}%")
    print(f"Top 10 Categories Revenue Share: {category_revenue['Cumulative Share (%)'].iloc[9]:.1f}%")

    print("\nPRICE DISTRIBUTION STATISTICS")
    print("-" * 70)
    price_stats = df['price'].describe()
    print(price_stats.to_string())

    print("\nAVERAGE REVIEW SCORE BY PRICE QUINTILE")
    print("-" * 70)
    print(price_review.to_string())

    print("\nPRODUCT CATEGORY PERFORMANCE MATRIX")
    print("-" * 70)
    print(category_revenue[['Total Revenue', 'Avg Review Score', 'Order Count', 'Performance Group']].head(15).to_string())

    print("\nPRODUCT CATEGORY PERFORMANCE GROUPS")
    print("-" * 70)
    performance_summary = category_revenue.groupby('Performance Group').agg({
        'Total Revenue': ['sum', 'count']
    }).round(2)
    performance_summary.columns = ['Total Revenue', 'Category Count']
    print(performance_summary.to_string())

    print("\nTOP STAR PERFORMERS")
    print("-" * 70)
    print(star_categories[['Total Revenue', 'Avg Review Score', 'Order Count']].head(5).to_string())

    print("\nFREIGHT COST TO PRODUCT PRICE RATIO ANALYSIS")
    print("-" * 70)
    freight_stats = df['freight_ratio'].describe()
    print("Freight-to-Price Ratio Statistics:")
    print(freight_stats.to_string())
    print("\nCategories with Highest Freight-to-Price Ratio:")
    print(high_freight_categories.round(3).to_string())

    print("\nEXECUTIVE SUMMARY")
    print("-" * 70)
    print(f"Categories Analyzed: {len(category_revenue)}")
    print(f"Total Orders Analyzed: {len(df):,}")
    print(f"Total Revenue: R${total_revenue:,.2f}")
    print(f"Average Order Value: R${df['price'].mean():.2f}")
    print(f"Median Order Value: R${df['price'].median():.2f}")
    print(f"Most Valuable Category: {category_revenue.index[0]} (R${category_revenue['Total Revenue'].iloc[0]:,.2f})")
    print(f"Best Rated Category: {category_revenue['Avg Review Score'].idxmax()} ({category_revenue['Avg Review Score'].max():.2f})")

    print("\nOUTPUT FILES")
    print("-" * 70)
    print(f"Visualization saved to: {output_path}")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    analyze_products_and_revenue()