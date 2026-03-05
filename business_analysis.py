import pandas as pd
import numpy as np
import os

def generate_pivot_report(file_path):
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    # Load data
    df = pd.read_csv(file_path, encoding="utf-8-sig")

    # 1. Date Preparation
    df['Year'] = df['Report Date'].str.extract(r'(\d{4})')
    df = df.dropna(subset=['Year'])
    df['Year'] = df['Year'].astype(int)

    def create_sorted_pivot(df, row_col):
        # Create pivot with Year as columns and category as rows
        pivot = pd.crosstab(df[row_col], df['Year'], margins=True, margins_name="Grand Total")
        
        # Sort rows (excluding Grand Total) by the Grand Total column descending
        data_rows = pivot.drop("Grand Total")
        total_row = pivot.loc[["Grand Total"]]
        
        data_rows = data_rows.sort_values(by="Grand Total", ascending=False)
        
        # Combine back
        sorted_pivot = pd.concat([data_rows, total_row])
        
        # Ensure year columns (numeric) are sorted ascending (left to right)
        # The Grand Total column will naturally be at the end due to margins=True
        return sorted_pivot

    # 2. Pivot Table: Location vs Year
    pivot_location = create_sorted_pivot(df, 'Location')

    # 3. Pivot Table: Contract Type vs Year
    pivot_contract = create_sorted_pivot(df, 'Contract Type')

    # 4. Pivot Table: Building Type vs Year
    pivot_type = create_sorted_pivot(df, 'Building Type')

    # 5. Volume & Growth Summary
    yearly_volume = df.groupby('Year').size().reset_index(name='Project Count')
    yearly_volume['YoY Growth (%)'] = yearly_volume['Project Count'].pct_change().fillna(0) * 100
    yearly_volume['YoY Growth (%)'] = yearly_volume['YoY Growth (%)'].map('{:,.1f}%'.format)

    # --- Generate the Markdown Report ---
    with open("TANAKEN_Detailed_Business_Analysis.md", "w", encoding="utf-8") as f:
        f.write("# TANAKEN Comprehensive Business Pivot Analysis\n\n")
        
        f.write("## 1. Annual Project Volume & Growth Summary\n")
        f.write(yearly_volume.to_markdown(index=False) + "\n\n")

        f.write("## 2. Pivot Table: Location vs Year (Sorted by Volume)\n")
        f.write("> Rows are sorted by total project count in descending order. Years are columns (First to Last).\n\n")
        f.write(pivot_location.to_markdown() + "\n\n")

        f.write("## 3. Pivot Table: Contract Type vs Year (Sorted by Volume)\n")
        f.write("> Rows are sorted by total project count in descending order. Years are columns (First to Last).\n\n")
        f.write(pivot_contract.to_markdown() + "\n\n")

        f.write("## 4. Pivot Table: Building Type vs Year (Sorted by Volume)\n")
        f.write("> Rows are sorted by total project count in descending order. Years are columns (First to Last).\n\n")
        f.write(pivot_type.to_markdown() + "\n\n")

        f.write("## 5. Strategic Summary\n")
        total_projects = len(df)
        prime_total = df[df['Contract Type'].str.contains('Prime', na=False)].shape[0]
        prime_pct = (prime_total / total_projects) * 100
        
        f.write(f"- **Total Database Records:** {total_projects}\n")
        f.write(f"- **Lifetime Prime Contractor Adoption:** {prime_pct:.1f}%\n")
        f.write(f"- **Core Market Ward:** {df['Location'].mode()[0]}\n")
        f.write("- **Analysis Note:** These pivot tables prioritize high-volume categories at the top of the rows, allowing for immediate identification of key business drivers across the 2010-2025 timeline.\n")

    print("Success: Refined pivot tables embedded in 'TANAKEN_Detailed_Business_Analysis.md'.")

if __name__ == "__main__":
    generate_pivot_report("tanaken_projects_english.csv")
