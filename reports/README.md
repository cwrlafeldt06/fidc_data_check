# FIDC Data Check Reports

This folder contains all reports, exports, and analysis outputs from the FIDC data validation system.

## Directory Structure

### 📊 `/differences`
Contains detailed difference analysis between fund reports and internal data:
- `*_fund_differences.csv` - Records with value discrepancies
- `*_fund_identical_sample.csv` - Sample of matching records for comparison

### 📈 `/comparisons` 
Contains comparison reports in various formats:
- `*.html` - Interactive HTML reports with charts and visualizations
- `*.json` - Structured JSON reports for programmatic analysis
- `*.txt` - Plain text console output reports

### 🔍 `/analysis`
Contains statistical analysis and pattern investigation:
- `difference_patterns_*.csv` - Analysis of difference patterns
- `statistical_summaries_*.txt` - Statistical breakdowns
- `outlier_analysis_*.csv` - Investigation of significant discrepancies

### 💾 `/data_exports`
Contains raw data exports for further analysis:
- `internal_data_*.csv` - BigQuery extractions
- `fund_data_processed_*.csv` - Processed fund report data
- `merged_datasets_*.csv` - Combined datasets for analysis

## File Naming Convention

Files follow the pattern: `{type}_{fund}_{date}_{description}.{ext}`

Examples:
- `differences_pi_20250530_detailed.csv`
- `comparison_ai_20250530_report.html`
- `analysis_pi_20250530_patterns.txt`

## Usage

1. **For investigators**: Start with files in `/comparisons` for overview
2. **For auditors**: Focus on `/differences` for specific discrepancies  
3. **For analysts**: Use `/data_exports` for custom analysis
4. **For patterns**: Review `/analysis` for trend identification

## Retention Policy

- Keep reports for current month + 3 months
- Archive older reports to separate storage
- Maintain audit trail for compliance 