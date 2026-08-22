# Importing
import os
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")
plt.rcParams.update({'figure.autolayout': True})

def analyze_payments():
    # Establishing Database Connection
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/database/olist.db"))
    conn = sqlite3.connect(db_path)

    # Retrieving Aggregated Payment Metrics, Order Values, and Review Scores
    query = """
        SELECT 
            p.order_id,
            p.total_payment_value,
            p.max_payment_installments,
            p.payment_types_used,
            p.payment_sequential_count,
            oi.price,
            oi.freight_value,
            r.review_score
        FROM order_payments p
        JOIN order_items oi ON p.order_id = oi.order_id
        LEFT JOIN order_reviews r ON p.order_id = r.order_id
        WHERE p.total_payment_value IS NOT NULL;
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    # Compute Payment Type Performance Metrics
    payment_summary = df.groupby('payment_types_used').agg({
        'total_payment_value': ['sum', 'mean', 'count'],
        'max_payment_installments': 'mean',
        'review_score': 'mean'
    }).round(2)

    payment_summary.columns = ['Total Value', 'Avg Value', 'Transaction Count', 'Avg Installments', 'Avg Review Score']
    payment_summary = payment_summary.sort_values('Total Value', ascending=False)

    # Calculate Payment Type Share
    total_payment_value = df['total_payment_value'].sum()
    payment_summary['Value Share (%)'] = (payment_summary['Total Value'] / total_payment_value) * 100

    # Analyze Installment Behavior
    installment_summary = df.groupby('max_payment_installments').agg({
        'total_payment_value': ['mean', 'count'],
        'review_score': 'mean'
    }).round(2)
    installment_summary.columns = ['Avg Payment Value', 'Transaction Count', 'Avg Review Score']

    # Generate and Save the Visualization 
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # Panel 1: Transaction Volume by Payment Type
    type_counts = df['payment_types_used'].value_counts()
    axes[0, 0].bar(type_counts.index, type_counts.values, color='cornflowerblue')
    axes[0, 0].set_title("Transaction Count by Payment Type", fontsize=14, fontweight="bold")
    axes[0, 0].set_xlabel("Payment Types Used", fontsize=12)
    axes[0, 0].set_ylabel("Transaction Count", fontsize=12)
    axes[0, 0].tick_params(axis='x', rotation=15)
    
    # Panel 2: Total Value by Payment Type
    axes[0, 1].bar(payment_summary.index, payment_summary['Total Value'], color='mediumseagreen')
    axes[0, 1].set_title("Total Revenue by Payment Type", fontsize=14, fontweight="bold")
    axes[0, 1].set_xlabel("Payment Types Used", fontsize=12)
    axes[0, 1].set_ylabel("Total Value (R$)", fontsize=12)
    axes[0, 1].tick_params(axis='x', rotation=15)
    
    # Panel 3: Payment Installment Distribution
    installments_filtered = df[df['max_payment_installments'] <= 12]['max_payment_installments']
    axes[1, 0].hist(installments_filtered, bins=12, color='darkorange', edgecolor='black', alpha=0.7, align='left')
    axes[1, 0].set_title("Max Installments Distribution (1-12)", fontsize=14, fontweight="bold")
    axes[1, 0].set_xlabel("Max Installments", fontsize=12)
    axes[1, 0].set_ylabel("Frequency", fontsize=12)
    
    # Panel 4: Average Review Score by Payment Type
    axes[1, 1].bar(payment_summary.index, payment_summary['Avg Review Score'], color='mediumpurple')
    axes[1, 1].axhline(y=df['review_score'].mean(), color='red', linestyle='--', label=f'Overall Mean: {df["review_score"].mean():.2f}')
    axes[1, 1].set_title("Average Review Score by Payment Type", fontsize=14, fontweight="bold")
    axes[1, 1].set_xlabel("Payment Types Used", fontsize=12)
    axes[1, 1].set_ylabel("Average Review Score", fontsize=12)
    axes[1, 1].set_ylim(0, 5.5)
    axes[1, 1].legend()
    axes[1, 1].tick_params(axis='x', rotation=15)
    
    plt.tight_layout()
    
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/output"))
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "payments_analysis.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    # Print Executive Summary
    print_summary(df, payment_summary, installment_summary, total_payment_value, output_path)


def print_summary(df, payment_summary, installment_summary, total_payment_value, output_path):
    """
    Prints a comprehensive executive summary of the payment methods analysis.
    All metrics are presented in a clean, formatted structure for reporting purposes.
    """

    print("\n" + "=" * 70)
    print("EXECUTIVE SUMMARY: PAYMENT METHODS AND INSTALLMENTS ANALYSIS")
    print("=" * 70)

    print("\nPAYMENT TYPE PERFORMANCE BREAKDOWN")
    print("-" * 70)
    print(payment_summary.to_string())

    print("\nOVERALL PAYMENT METRICS")
    print("-" * 70)
    print(f"Total Payment Value Tracked: R${total_payment_value:,.2f}")
    print(f"Total Transactions Evaluated: {len(df):,}")
    print(f"Average Payment Value: R${df['total_payment_value'].mean():.2f}")
    print(f"Median Payment Value: R${df['total_payment_value'].median():.2f}")
    print(f"Average Installments (Overall): {df['max_payment_installments'].mean():.2f}")

    print("\nINSTALLMENT BEHAVIOR SUMMARY (TOP TIERS)")
    print("-" * 70)
    print(installment_summary.head(10).to_string())

    print("\nOUTPUT FILES")
    print("-" * 70)
    print(f"Visualization saved to: {output_path}")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    analyze_payments()