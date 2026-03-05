# Tanaken Project Scraper & Business Analysis

This project is a specialized toolkit for extracting, translating, and analyzing historical project data from the [TANAKEN website](https://www.tanaken-1982.co.jp/).

## Features
- **Project Scraper (`scraper.py`)**: Crawls the main project list and individual detail pages to extract project information. Includes a local caching mechanism to prevent redundant network requests.
- **Japanese to English Translator (`translate_csv.py`)**: A comprehensive translation tool with a custom-mapped dictionary of technical construction and demolition terms to provide a high-quality English output.
- **Business Trends Analyzer (`business_analysis.py`)**: Calculates YoY KPIs including project volume, location trends, contractor type shifts (Prime vs. Sub), and project specializations.
- **Business Analysis Report**: A generated Markdown report summarizing strategic findings from the scraped data.

## Installation
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
1. Run the scraper: `python3 scraper.py`
2. Translate the output: `python3 translate_csv.py`
3. Generate the business analysis: `python3 business_analysis.py`

## Output
- `tanaken_projects_english.csv`: The final, translated database.
- `TANAKEN_Business_Analysis_Report.md`: A summary of the business analysis findings.
