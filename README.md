# FIDC Data Check - CSV Comparison Tool

A comprehensive tool for comparing CSV files and BigQuery data, specifically designed for validating fund reports against internal cession order data.

## Overview

This tool helps you verify if fund reports match your internal data by:
- Extracting data from BigQuery (`infinitepay-production.maindb.cession_orders`)
- Comparing it with fund CSV reports
- Matching records by cession order ID (`NumeroContrato` in fund reports ↔ `id` in internal database)
- Generating detailed comparison reports

## Installation

1. **Clone and setup the environment:**
```bash
cd /path/to/fidc_data_check
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Setup Google Cloud credentials** (one of the following):
   - Set up Application Default Credentials: `gcloud auth application-default login`
   - Download service account JSON key and set `GOOGLE_APPLICATION_CREDENTIALS` environment variable
   - Use the `--credentials` option with path to service account JSON
   'gcloud auth login --enable-gdrive-access --update-adc'

## 🔐 Google Sheets Integration (Optional)

To export differences directly to Google Sheets:

1. **See detailed setup guide:** [GOOGLE_SHEETS_SETUP.md](GOOGLE_SHEETS_SETUP.md)
2. **Quick setup:**
   - Create a Google Cloud project
   - Enable Google Sheets API and Google Drive API
   - Create a service account and download credentials JSON
   - Rename to `google_credentials.json` and place in project root
   - **Important:** This file is already excluded from git for security

3. **Test the setup:**
   ```bash
   python analyze_differences.py --fund pi --format google_sheets
   ```

> **Security Note:** Never commit `google_credentials.json` to the repository. Use the template file (`google_credentials_template.json`) to understand the structure.

## Quick Start

### 1. Run commands

# Export to Excel (default)
python analyze_differences.py --fund pi --format excel

# Export to Google Sheets (requires setup)
python analyze_differences.py --fund pi --format google_sheets

# Export to CSV
python analyze_differences.py --fund pi --format csv

# Only export data (skip analysis)
python analyze_differences.py --fund pi --format excel --export-only

# Use specific file
python analyze_differences.py --file reports/differences/pi_fund_differences.csv --format excel

### 3. Analyze Individual Files

```bash
# Get information about a CSV file
python csv_compare_cli.py info "data/fund_report.csv"

# Create a configuration file
python csv_compare_cli.py create-config my_config.json
```

## Key Features

### 🔍 **Smart Record Matching**
- Matches records by cession order ID (`NumeroContrato` ↔ `id`)
- Handles different row orders between files
- Identifies missing, extra, and modified records

### 📊 **Multiple Comparison Types**
- **Full**: Complete record-by-record comparison
- **Schema**: Compare column structure and data types
- **Statistical**: Compare data distributions and summaries
- **Subset**: Check if one dataset is contained in another

### 📈 **Rich Reporting**
- **Console**: Quick text-based reports
- **HTML**: Interactive reports with charts and visualizations
- **JSON**: Machine-readable structured reports

### ⚙️ **Flexible Configuration**
```json
{
  "float_tolerance": 1e-10,
  "ignore_case": false,
  "ignore_whitespace": true,
  "ignore_columns": ["timestamp", "processing_date"],
  "key_columns": ["NumeroContrato"],
  "description": "Configuration for cession order comparison"
}
```

## File Structure

```
fidc_data_check/
├── src/
│   ├── core/
│   │   ├── csv_loader.py          # CSV file loading and validation
│   │   ├── comparator.py          # Main comparison logic
│   │   └── bigquery_loader.py     # BigQuery data extraction
│   └── reports/
│       ├── html_reporter.py       # HTML report generation
│       └── json_reporter.py       # JSON report generation
├── sql/
│   └── extract_cession_orders.sql # BigQuery extraction query
├── data/                          # Your CSV files
├── tests/                         # Unit tests
├── csv_compare_cli.py            # Main CLI interface
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## Data Schema

The tool expects both internal and fund data to have these columns:

| Column | Description | Type |
|--------|-------------|------|
| DataReferencia | Reference date | String |
| NumeroContrato | Cession order ID | String |
| CodCnpj | Fund CNPJ code | Integer |
| NomeFundo | Fund name | String |
| CnpjSacado | Debtor CNPJ | Integer |
| NomeSacado | Debtor name | String |
| TipoProduto | Product type | String |
| TaxaCessao | Cession rate | Float |
| ValorAquisicao | Acquisition value | Float |
| ValorPresente | Present value | Float |
| ValorFace | Face value | Float |
| DataAquisicao | Acquisition date | String |
| DataVencimento | Maturity date | String |
| RatingContrato | Contract rating | String |
| DiasAtraso | Days overdue | Integer |
| ValorDesembolso | Disbursement value | Float |
| Bandeira | Card brand | String |
| Banco | Bank code | Integer |
| Agencia | Agency code | Integer |
| Conta | Account code | Integer |
| Prazo | Term | Integer |
| PrazoAtual | Current term | Integer |
| Reverse | Reverse flag | Float |

## Examples

### Example 1: Daily Fund Report Validation

```bash
# Download today's fund report and compare with internal data
python csv_compare_cli.py compare-with-internal \
    "downloads/Posição_em_carteira_cw_20697244_2025_05_30.csv" \
    --reference-date "2025-05-30" \
    --format html \
    --output "reports/daily_validation_$(date +%Y%m%d).html" \
    --config comparison_config.json \
    --verbose
```

### Example 2: Multiple Fund Reports Analysis

```bash
# Compare reports from two different funds
python csv_compare_cli.py compare \
    "data/fund_19441218_report.csv" \
    "data/fund_20697244_report.csv" \
    --type statistical \
    --format html \
    --output "analysis/funds_comparison.html" \
    --title "Multi-Fund Portfolio Analysis"
```

### Example 3: Data Quality Check

```bash
# Check data quality of fund report
python csv_compare_cli.py info "data/fund_report.csv"

# Extract internal data for manual analysis
python csv_compare_cli.py compare-with-internal \
    "data/fund_report.csv" \
    --export-internal "exports/internal_$(date +%Y%m%d).csv" \
    --format json \
    --output "reports/quality_check.json"
```

## Interpretation Guide

### 🟢 **Perfect Match**
- `Data Identical: YES`
- `Match Percentage: 100%`
- `Missing Records: 0`

### 🟡 **Partial Match**
- Some records match, others don't
- Check `missing_records` and `different_records` sections
- May indicate timing differences or data processing issues

### 🔴 **No Match**
- `Match Percentage: 0%`
- `Common Records: 0`
- Indicates completely different datasets or incorrect mapping

### 📊 **Common Scenarios**

1. **Different Record Counts**: Normal if reports cover different time periods
2. **Value Differences**: Check tolerance settings and rounding differences
3. **Missing Records**: May indicate partial data or filtering differences
4. **Schema Mismatches**: Column names or types don't align

## Troubleshooting

### BigQuery Authentication Issues
```bash
# Setup default credentials
gcloud auth application-default login

# Or use service account
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
```

### Memory Issues with Large Files
- Use `--type statistical` for quick overview
- Increase system memory or use cloud computing
- Consider sampling large datasets

### Encoding Problems
- Tool auto-detects encoding (UTF-8, Latin-1, etc.)
- For stubborn files, save as UTF-8 manually

### Performance Optimization
- Use `--config` to ignore irrelevant columns
- Set appropriate `float_tolerance` for numeric comparisons
- Use `subset` comparison for large datasets

## Contributing

This tool is designed for FIDC data validation. To extend functionality:

1. Add new comparison types in `src/core/comparator.py`
2. Create custom reporters in `src/reports/`
3. Extend BigQuery integration in `src/core/bigquery_loader.py`

## Support

For questions or issues:
1. Check the verbose output: `--verbose`
2. Review the configuration file
3. Validate your BigQuery access and SQL query
4. Ensure data schemas match expected format 