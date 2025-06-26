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
│   ├── get_fund_info.py         # Get fund information by user ID
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
│   ├── extract_cession_orders.sql  # Main data extraction query
│   └── get_fund_info.sql           # Fund information query
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
   - **Predefined Funds**: Select PI or AI funds (built-in configuration)
   - **Custom Funds**: Enter any fund user ID, fetch fund information, then upload CSV for analysis

### Command Line Interface

#### For Fund Analysis (Most Common Use Case)

1. **Quick Analysis** (simplest option):
   ```bash
   cd scripts/
   # Predefined funds
   python quick_analysis.py [pi|ai] [excel|csv|google_sheets]
   
   # Custom funds
   python quick_analysis.py <fund_user_id> <csv_file_path> [excel|csv|google_sheets]
   ```

2. **Full Analysis Pipeline**:
   ```bash
   cd scripts/
   # Predefined funds
   python run_fund_analysis.py --fund pi --format excel
   
   # Custom funds
   python run_fund_analysis.py --fund-user-id 12345678 --fund-csv /path/to/fund.csv --format excel
   ```

3. **Step-by-Step Analysis**:
   ```bash
   cd scripts/
   # Step 1: Extract data and find differences
   # Predefined funds
   python export_differences.py --fund-alias pi --reference-date 2025-05-30
   
   # Custom funds
   python export_differences.py --fund-user-id 12345678 --fund-csv /path/to/fund.csv --reference-date 2025-05-30
   
   # Step 2: Export formatted results
   python analyze_differences.py --fund <fund_identifier>
   ```

4. **Get Fund Information**:
   ```bash
   cd scripts/
   python get_fund_info.py 12345678
   ```

#### For General CSV Comparison

```bash
cd cli/
python csv_compare_cli.py compare file1.csv file2.csv --format html
```

#### For Internal Data Comparison

```bash
cd cli/
# Predefined funds
python csv_compare_cli.py compare-with-internal fund_report.csv --fund pi

# Custom funds
python csv_compare_cli.py compare-with-internal fund_report.csv --fund-user-id 12345678
```

## File Purposes

### CLI Tools (`cli/`)
- **csv_compare_cli.py**: General-purpose CSV comparison tool with multiple output formats

### Analysis Scripts (`scripts/`)
- **quick_analysis.py**: Simplified interface for common fund analysis (supports both predefined and custom funds)
- **run_fund_analysis.py**: Complete pipeline orchestrator with all options (supports both predefined and custom funds)
- **export_differences.py**: Extracts internal data, compares with fund reports (supports both predefined and custom funds)
- **analyze_differences.py**: Formats differences for final output
- **get_fund_info.py**: Retrieves fund information by user ID

### Core Library (`src/`)
- Contains reusable modules for data loading, comparison, and reporting
- Used by both CLI tools and analysis scripts

### SQL Queries (`sql/`)
- **extract_cession_orders.sql**: Main query for extracting cession data (supports both fund alias and user ID filtering)
- **get_fund_info.sql**: Query for retrieving fund information by user ID

## Running from Project Root

If you want to run scripts from the project root directory, use:

```bash
# For predefined funds
python scripts/quick_analysis.py pi excel
python scripts/run_fund_analysis.py --fund pi --format excel

# For custom funds
python scripts/quick_analysis.py 12345678 /path/to/fund.csv excel
python scripts/run_fund_analysis.py --fund-user-id 12345678 --fund-csv /path/to/fund.csv --format excel

# For CLI tools  
python cli/csv_compare_cli.py compare file1.csv file2.csv
python cli/csv_compare_cli.py compare-with-internal fund_report.csv --fund-user-id 12345678
```

## Fund Types

### Predefined Funds
- **PI Fund**: ID 20697244, alias 'pi'
- **AI Fund**: ID 19441218, alias 'ai'

These funds have predefined configurations and don't require CSV file upload for analysis.

### Custom Funds
Any fund with a valid user ID can be analyzed by:
1. Providing the fund user ID
2. Uploading the corresponding CSV file
3. The system will automatically fetch fund information from the database

## Output Files

- **Data Exports**: `reports/data_exports/` - Raw internal and fund data
- **Differences**: `reports/differences/` - Detailed difference analysis
- **Formatted Exports**: `reports/formatted_exports/` - Final Excel/CSV outputs
- **Comparisons**: `reports/comparisons/` - General comparison reports

## New Features

### Custom Fund Support
- Enter any fund user ID to analyze custom funds
- Automatic fund information retrieval from database
- Fund name display after successful lookup
- Drag-and-drop CSV upload for custom fund analysis
- Support for custom funds in both web interface and CLI tools

### Enhanced Fund Analysis
- Unified interface supporting both predefined and custom funds
- Better error handling and validation
- Improved file naming with fund identifiers
- Legacy compatibility with existing predefined funds

This structure separates concerns clearly:
- CLI tools for general use
- Scripts for specific fund analysis workflows  
- Core modules for shared functionality
- Clear output organization
- Support for both predefined and custom funds 