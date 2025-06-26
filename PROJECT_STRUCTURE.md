# Project Structure

This project has been organized into a clear folder structure for better maintainability and usability.

## Directory Structure

```
fidc_data_check/
├── cli/                    # Command line interface tools
│   ├── __init__.py
│   └── csv_compare_cli.py  # General CSV comparison CLI tool
├── scripts/                # Analysis and processing scripts
│   ├── __init__.py
│   ├── analyze_differences.py    # Format differences for export
│   ├── export_differences.py    # Extract and compare fund data
│   ├── quick_analysis.py        # Quick fund analysis interface
│   └── run_fund_analysis.py     # Main analysis orchestrator
├── src/                    # Core library modules
│   ├── core/              # Core functionality
│   │   ├── csv_loader.py
│   │   ├── comparator.py
│   │   └── bigquery_loader.py
│   └── reports/           # Report generators
│       ├── html_reporter.py
│       └── json_reporter.py
├── frontend/               # Web dashboard (React + Node.js)
│   ├── server/            # Express.js backend API
│   │   ├── package.json
│   │   ├── server.js      # Main API server
│   │   └── uploads/       # Temporary file storage
│   ├── client/            # React frontend
│   │   ├── package.json
│   │   ├── src/
│   │   │   ├── components/ # UI components
│   │   │   ├── pages/     # Application pages
│   │   │   ├── utils/     # API utilities
│   │   │   └── App.js     # Main app component
│   │   └── public/        # Static assets
│   └── README.md          # Frontend documentation
├── data/                   # Input data files
├── reports/                # Generated reports and outputs
│   ├── comparisons/       # Comparison reports
│   ├── differences/       # Difference analysis files
│   ├── data_exports/      # Raw data exports
│   └── formatted_exports/ # Final formatted outputs
├── sql/                    # SQL queries
├── tests/                  # Test files
└── tools/                  # Utility scripts and helpers
```

## How to Use

### Web Dashboard (Recommended)

1. **Start the web interface**:
   ```bash
   # Terminal 1: Start backend server
   cd frontend/server
   npm install && npm run dev
   
   # Terminal 2: Start frontend
   cd frontend/client  
   npm install && npm start
   ```
   Then open http://localhost:3000 in your browser.

2. **CSV File Comparison**: Upload two CSV files and get interactive reports
3. **Fund Analysis**: Upload fund reports and analyze against internal data

### Command Line Interface

#### For Fund Analysis (Most Common Use Case)

1. **Quick Analysis** (simplest option):
   ```bash
   cd scripts/
   python quick_analysis.py [pi|ai] [excel|csv|google_sheets]
   ```

2. **Full Analysis Pipeline**:
   ```bash
   cd scripts/
   python run_fund_analysis.py --fund pi --format excel
   ```

3. **Step-by-Step Analysis**:
   ```bash
   cd scripts/
   # Step 1: Extract data and find differences
   python export_differences.py pi 2025-05-30
   
   # Step 2: Export formatted results
   python analyze_differences.py
   ```

#### For General CSV Comparison

```bash
cd cli/
python csv_compare_cli.py compare file1.csv file2.csv --format html
```

#### For Internal Data Comparison

```bash
cd cli/
python csv_compare_cli.py compare-with-internal fund_report.csv --fund pi
```

## File Purposes

### CLI Tools (`cli/`)
- **csv_compare_cli.py**: General-purpose CSV comparison tool with multiple output formats

### Analysis Scripts (`scripts/`)
- **quick_analysis.py**: Simplified interface for common fund analysis
- **run_fund_analysis.py**: Complete pipeline orchestrator with all options
- **export_differences.py**: Extracts internal data, compares with fund reports
- **analyze_differences.py**: Formats differences for final output

### Core Library (`src/`)
- Contains reusable modules for data loading, comparison, and reporting
- Used by both CLI tools and analysis scripts

## Running from Project Root

If you want to run scripts from the project root directory, use:

```bash
# For scripts
python scripts/quick_analysis.py pi excel
python scripts/run_fund_analysis.py --fund pi --format excel

# For CLI tools  
python cli/csv_compare_cli.py compare file1.csv file2.csv
```

## Output Files

- **Data Exports**: `reports/data_exports/` - Raw internal and fund data
- **Differences**: `reports/differences/` - Detailed difference analysis
- **Formatted Exports**: `reports/formatted_exports/` - Final Excel/CSV outputs
- **Comparisons**: `reports/comparisons/` - General comparison reports

This structure separates concerns clearly:
- CLI tools for general use
- Scripts for specific fund analysis workflows  
- Core modules for shared functionality
- Clear output organization 