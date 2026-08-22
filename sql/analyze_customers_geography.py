# Importing
import os
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")
plt.rcParams.update({'figure.autolayout': True})

def analyze_customers_geography():
    # Establishing Database Connection
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/database/olist.db"))
    conn = sqlite3.connect(db_path)

    # Retrieving Customer Geographies, Orders, and Payments
    query = """
        SELECT 
            c.customer_id,
            c.customer_unique_id,
            c.customer_city,
            c.customer_state,
            o.order_id,
            COALESCE(p.total_payment_value, 0) AS total_payment_value
        FROM customers c
        LEFT JOIN orders o ON c.customer_id = o.customer_id
        LEFT JOIN order_payments p ON o.order_id = p.order_id;
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    # Map States to Brazilian Macro-Regions
    region_mapping = {
        'SP': 'Southeast', 'RJ': 'Southeast', 'MG': 'Southeast', 'ES': 'Southeast',
        'PR': 'South', 'SC': 'South', 'RS': 'South',
        'BA': 'Northeast', 'CE': 'Northeast', 'PE': 'Northeast', 'MA': 'Northeast', 
        'PB': 'Northeast', 'RN': 'Northeast', 'AL': 'Northeast', 'SE': 'Northeast', 'PI': 'Northeast',
        'DF': 'Central-West', 'GO': 'Central-West', 'MT': 'Central-West', 'MS': 'Central-West',
        'AM': 'North', 'PA': 'North', 'RO': 'North', 'AC': 'North', 'AP': 'North', 'RR': 'North', 'TO': 'North'
    }
    df['customer_region'] = df['customer_state'].map(region_mapping).fillna('Other')

    # Compute State-Level Summary
    state_summary = df.groupby('customer_state').agg({
        'customer_unique_id': 'nunique',
        'order_id': 'count',
        'total_payment_value': 'sum'
    }).rename(columns={
        'customer_unique_id': 'Unique Customers',
        'order_id': 'Total Orders',
        'total_payment_value': 'Total Revenue'
    }).sort_values('Unique Customers', ascending=False)

    # Compute Region-Level Summary
    region_summary = df.groupby('customer_region').agg({
        'customer_unique_id': 'nunique'
    }).rename(columns={'customer_unique_id': 'Unique Customers'}).sort_values('Unique Customers', ascending=False)

    # Compute City-Level Summary (Top Cities)
    city_summary = df.groupby(['customer_state', 'customer_city']).agg({
        'customer_unique_id': 'nunique',
        'order_id': 'count',
        'total_payment_value': 'sum'
    }).reset_index().rename(columns={
        'customer_state': 'State',
        'customer_city': 'City',
        'customer_unique_id': 'Unique Customers',
        'order_id': 'Total Orders',
        'total_payment_value': 'Total Revenue'
    })
    top_cities = city_summary.sort_values('Unique Customers', ascending=False).head(15)

    # Generate and Save the 4-Panel Visualization 
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # Panel 1: Top 10 States by Unique Customer Count
    top_states = state_summary.head(10).sort_values('Unique Customers', ascending=True)
    axes[0, 0].barh(top_states.index, top_states['Unique Customers'], color='dodgerblue')
    axes[0, 0].set_title("Top 10 States by Unique Customer Count", fontsize=14, fontweight="bold")
    axes[0, 0].set_xlabel("Unique Customers", fontsize=12)
    axes[0, 0].set_ylabel("State", fontsize=12)
    
    # Panel 2: Customer Share by Macro-Region
    axes[0, 1].pie(
        region_summary['Unique Customers'], 
        labels=region_summary.index, 
        autopct='%1.1f%%', 
        colors=sns.color_palette("muted"), 
        startangle=90,
        textprops={'fontsize': 12, 'fontweight': 'bold'}
    )
    axes[0, 1].set_title("Customer Share by Brazilian Macro-Region", fontsize=14, fontweight="bold")
    
    # Panel 3: Top 10 Cities by Unique Customers
    top_10_cities = top_cities.head(10).sort_values('Unique Customers', ascending=True)
    axes[1, 0].barh(top_10_cities['City'] + " (" + top_10_cities['State'] + ")", top_10_cities['Unique Customers'], color='mediumseagreen')
    axes[1, 0].set_title("Top 10 Cities by Unique Customer Concentration", fontsize=14, fontweight="bold")
    axes[1, 0].set_xlabel("Unique Customers", fontsize=12)
    axes[1, 0].set_ylabel("City (State)", fontsize=12)
    
    # Panel 4: Revenue vs Unique Customers per State (Scatter)
    axes[1, 1].scatter(state_summary['Unique Customers'], state_summary['Total Revenue'] / 1000, color='darkorange', s=80, alpha=0.8)
    axes[1, 1].set_title("State Customer Volume vs. Total Revenue (in thousands)", fontsize=14, fontweight="bold")
    axes[1, 1].set_xlabel("Unique Customers", fontsize=12)
    axes[1, 1].set_ylabel("Total Revenue (k BRL)", fontsize=12)
    
    plt.tight_layout()
    
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/output"))
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "customer_geography_analysis.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    # Print Executive Summary
    print_summary(df, state_summary, top_cities, output_path)


def print_summary(df, state_summary, top_cities, output_path):
    """
    Prints a comprehensive executive summary of the customer geography analysis.
    All metrics are presented in a clean, formatted structure for reporting purposes.
    """

    print("\n" + "=" * 70)
    print("EXECUTIVE SUMMARY: CUSTOMER GEOGRAPHY & REGIONAL DISTRIBUTION")
    print("=" * 70)

    print("\nSTATE-LEVEL CUSTOMER & REVENUE SUMMARY (TOP 10)")
    print("-" * 70)
    print(state_summary.head(10).to_string())

    print("\nTOP CITIES BY CUSTOMER CONCENTRATION (TOP 10)")
    print("-" * 70)
    print(top_cities[['City', 'State', 'Unique Customers', 'Total Orders', 'Total Revenue']].head(10).to_string(index=False))

    print("\nMACRO GEOGRAPHY METRICS")
    print("-" * 70)
    print(f"Total Unique Customers Tracked: {df['customer_unique_id'].nunique():,}")
    print(f"Total States Represented: {len(state_summary)}")
    print(f"Total Cities Represented: {df['customer_city'].nunique():,}")

    print("\nOUTPUT FILES")
    print("-" * 70)
    print(f"Visualization saved to: {output_path}")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    analyze_customers_geography()