# Importing
import os
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")
plt.rcParams.update({'figure.autolayout': True})

def analyze_geolocation():
    # Establishing Database Connection
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/database/olist.db"))
    conn = sqlite3.connect(db_path)

    # Retrieving Geolocation Centroids and Regional Mapping
    query = """
        SELECT 
            geolocation_zip_code_prefix,
            geolocation_centroid_lat,
            geolocation_centroid_lng,
            geolocation_city,
            geolocation_state,
            geolocation_points_density_count,
            geolocation_zone_type,
            geolocation_region
        FROM geolocation;
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    # Compute State-Level Metrics
    state_summary = df.groupby('geolocation_state').agg({
        'geolocation_zip_code_prefix': 'count',
        'geolocation_centroid_lat': ['mean', 'min', 'max'],
        'geolocation_centroid_lng': ['mean', 'min', 'max'],
        'geolocation_points_density_count': 'sum'
    }).round(4)

    state_summary.columns = ['Zip Code Count', 'Mean Lat', 'Min Lat', 'Max Lat', 'Mean Lng', 'Min Lng', 'Max Lng', 'Total Points']
    state_summary = state_summary.sort_values('Zip Code Count', ascending=False)

    # Calculate Coordinate Dispersion Spans (Bounding Box Spans)
    state_summary['Lat Span'] = state_summary['Max Lat'] - state_summary['Min Lat']
    state_summary['Lng Span'] = state_summary['Max Lng'] - state_summary['Min Lng']

    # Compute City Density (Top Cities by Zip Code Count)
    city_summary = df.groupby(['geolocation_state', 'geolocation_city']).agg({
        'geolocation_zip_code_prefix': 'count',
        'geolocation_centroid_lat': 'mean',
        'geolocation_centroid_lng': 'mean'
    }).reset_index()
    city_summary.columns = ['State', 'City', 'Zip Code Count', 'Lat', 'Lng']
    top_cities = city_summary.sort_values('Zip Code Count', ascending=False).head(15)

    # Generate and Save the Visualization 
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # Panel 1: Geographic Scatter Map of Centroids (Downsampled for Performance)
    sample_df = df.sample(n=min(20000, len(df)), random_state=42)
    axes[0, 0].scatter(sample_df['geolocation_centroid_lng'], sample_df['geolocation_centroid_lat'], alpha=0.15, s=2, color='dodgerblue')
    axes[0, 0].set_title("Brazil Geolocation Centroids Scatter Plot (Sampled)", fontsize=14, fontweight="bold")
    axes[0, 0].set_xlabel("Centroid Longitude", fontsize=12)
    axes[0, 0].set_ylabel("Centroid Latitude", fontsize=12)
    
    # Panel 2: Zip Code Density by State (Top 10)
    top_states = state_summary.head(10).sort_values('Zip Code Count', ascending=True)
    axes[0, 1].barh(top_states.index, top_states['Zip Code Count'], color='mediumseagreen')
    axes[0, 1].set_title("Top 10 States by Zip Code Count", fontsize=14, fontweight="bold")
    axes[0, 1].set_xlabel("Zip Code Prefix Count", fontsize=12)
    axes[0, 1].set_ylabel("State", fontsize=12)
    
    # Panel 3: Latitude Span by State (Bounding Box)
    axes[1, 0].barh(top_states.index, top_states['Lat Span'], color='darkorange')
    axes[1, 0].set_title("Latitude Span (North-South Spread) by State", fontsize=14, fontweight="bold")
    axes[1, 0].set_xlabel("Latitude Degrees Span", fontsize=12)
    axes[1, 0].set_ylabel("State", fontsize=12)
    
    # Panel 4: Top 10 Cities by Zip Code Coverage
    top_10_cities = top_cities.head(10).sort_values('Zip Code Count', ascending=True)
    axes[1, 1].barh(top_10_cities['City'] + " (" + top_10_cities['State'] + ")", top_10_cities['Zip Code Count'], color='mediumpurple')
    axes[1, 1].set_title("Top 10 Cities by Zip Code Coverage", fontsize=14, fontweight="bold")
    axes[1, 1].set_xlabel("Zip Code Count", fontsize=12)
    axes[1, 1].set_ylabel("City (State)", fontsize=12)
    
    plt.tight_layout()
    
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/output"))
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "geolocation_analysis.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    # Print Executive Summary
    print_summary(df, state_summary, top_cities, output_path)


def print_summary(df, state_summary, top_cities, output_path):
    """
    Prints a comprehensive executive summary of the geolocation and spatial distribution analysis.
    All metrics are presented in a clean, formatted structure for reporting purposes.
    """

    print("\n" + "=" * 70)
    print("EXECUTIVE SUMMARY: GEOLOCATION AND SPATIAL DISTRIBUTION ANALYSIS")
    print("=" * 70)

    print("\nSTATE-LEVEL GEOLOCATION SUMMARY (TOP 10)")
    print("-" * 70)
    print(state_summary[['Zip Code Count', 'Mean Lat', 'Mean Lng', 'Lat Span', 'Lng Span', 'Total Points']].head(10).to_string())

    print("\nTOP CITIES BY ZIP CODE COVERAGE (TOP 10)")
    print("-" * 70)
    print(top_cities[['City', 'State', 'Zip Code Count', 'Lat', 'Lng']].head(10).to_string(index=False))

    print("\nMACRO GEOLOCATION METRICS")
    print("-" * 70)
    print(f"Total Unique Zip Code Prefixes Tracked: {len(df):,}")
    print(f"Total States Covered: {len(state_summary)}")
    print(f"Overall Latitude Range: {df['geolocation_centroid_lat'].min():.4f} to {df['geolocation_centroid_lat'].max():.4f}")
    print(f"Overall Longitude Range: {df['geolocation_centroid_lng'].min():.4f} to {df['geolocation_centroid_lng'].max():.4f}")

    print("\nOUTPUT FILES")
    print("-" * 70)
    print(f"Visualization saved to: {output_path}")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    analyze_geolocation()