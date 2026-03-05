import pandas as pd
import numpy as np
import os

def analyze_business_trends(file_path):
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    # Load the data
    df = pd.read_csv(file_path, encoding="utf-8-sig")

    # 1. Clean and Extract Year from Report Date
    # Typical format: 2025-02-03 or 2024-07-25
    df['Year'] = df['Report Date'].str.extract(r'(\d{4})')
    df = df.dropna(subset=['Year'])
    df['Year'] = df['Year'].astype(int)

    # 2. KPI: Number of Projects per Year
    projects_per_year = df.groupby('Year').size().reset_index(name='Total Projects')

    # 3. KPI: Top Locations by Year
    # Location might have "Tokyo", "Kanagawa", etc.
    location_trends = df.groupby(['Year', 'Location']).size().unstack(fill_value=0)
    top_locations = df['Location'].value_counts().head(5).index
    location_trends_top = location_trends[top_locations] if all(loc in location_trends.columns for loc in top_locations) else location_trends

    # 4. KPI: Contractor Type Trends (Prime vs Sub)
    contract_trends = df.groupby(['Year', 'Contract Type']).size().unstack(fill_value=0)

    # 5. KPI: Project Type (Building Type) Trends
    type_trends = df.groupby(['Year', 'Building Type']).size().unstack(fill_value=0)
    top_types = df['Building Type'].value_counts().head(5).index
    type_trends_top = type_trends[top_types] if all(t in type_trends.columns for t in top_types) else type_trends

    # 6. KPI: Work Details (if exists)
    # The Work Details column might be sparse or contain "Demolition"
    # Let's count how many mentions of "Demolition" are in Project Title if Work Details is empty
    df['Is_Demolition'] = df['Project Title'].str.contains('Demolition', case=False, na=False)
    demolition_trends = df.groupby('Year')['Is_Demolition'].sum().reset_index(name='Demolition Projects')

    # Printing the results for synthesis
    print("=== YEAR-ON-YEAR PROJECT VOLUME ===")
    print(projects_per_year.to_string(index=False))
    
    print("\n=== TOP LOCATION TRENDS (YOY) ===")
    print(location_trends_top.tail(10).to_string())

    print("\n=== CONTRACT TYPE TRENDS (YOY) ===")
    print(contract_trends.tail(10).to_string())

    print("\n=== TOP BUILDING TYPE TRENDS (YOY) ===")
    print(type_trends_top.tail(10).to_string())

    print("\n=== DEMOLITION SPECIFIC TRENDS (YOY) ===")
    print(demolition_trends.tail(10).to_string(index=False))

    # Overall Statistics
    print("\n=== GLOBAL TOTALS ===")
    print(f"Total Projects Analyzed: {len(df)}")
    print(f"Primary Location: {df['Location'].mode()[0]} ({df['Location'].value_counts().max()} projects)")
    print(f"Primary Project Type: {df['Building Type'].mode()[0]}")

if __name__ == "__main__":
    analyze_business_trends("tanaken_projects_english.csv")
