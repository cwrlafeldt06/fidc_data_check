#!/usr/bin/env python3
"""
Main orchestrator for fund analysis pipeline.
Runs the complete process: get data, compare, and export formatted results.
"""

import argparse
import sys
import os
from pathlib import Path
from datetime import datetime
import subprocess

# Add project root and src to path for imports
project_root = os.path.join(os.path.dirname(__file__), '..')
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, project_root)
sys.path.insert(0, src_path)

def run_complete_analysis(fund_alias='', fund_user_id='', reference_date='2025-05-30', 
                         fund_csv_path=None, output_format='excel', 
                         skip_comparison=False, export_data=True, export_differences=True, 
                         output_only=False):
    """
    Run the complete fund analysis pipeline:
    1. Extract data and compare (export_differences.py)
    2. Export formatted results (analyze_differences.py)
    
    Args:
        fund_alias: Fund alias ('pi' or 'ai', optional)
        fund_user_id: Fund user ID (optional, required if fund_alias not provided)
        fund_csv_path: Path to fund CSV file (optional)
        reference_date: Date for analysis
        output_format: Final output format ('excel', 'google_sheets', 'csv')
        skip_comparison: Skip data extraction and comparison step
        export_data: Whether to export raw/processed data files
        export_differences: Whether to export difference analysis files
        output_only: If True, only creates the final output file (skips all intermediate files)
    """
    
    if not fund_alias and not fund_user_id:
        raise ValueError("Either fund_alias or fund_user_id must be provided")
    
    if output_only:
        export_data = False
        export_differences = False
    
    fund_identifier = fund_alias if fund_alias else fund_user_id
    
    print("🚀 STARTING COMPLETE FUND ANALYSIS PIPELINE")
    print("="*60)
    print(f"Fund Alias: {fund_alias if fund_alias else 'N/A'}")
    print(f"Fund User ID: {fund_user_id if fund_user_id else 'N/A'}")
    print(f"Fund CSV: {fund_csv_path if fund_csv_path else 'Auto-detect/Predefined'}")
    print(f"Reference Date: {reference_date}")
    print(f"Output Format: {output_format}")
    print(f"Export Data Files: {'Yes' if export_data else 'No'}")
    print(f"Export Differences Files: {'Yes' if export_differences else 'No'}")
    print(f"Output Only Mode: {'Yes' if output_only else 'No'}")
    print("="*60)
    print()
    
    # Step 1: Run comparison and generate differences (unless skipped)
    if not skip_comparison:
        print("📊 STEP 1: EXTRACTING DATA AND COMPARING")
        print("-" * 40)
        
        try:
            # Import and run the export_differences function
            from export_differences import export_differences
            
            result = export_differences(
                fund_alias=fund_alias,
                fund_user_id=fund_user_id,
                reference_date=reference_date,
                fund_csv_path=fund_csv_path,
                export_data=export_data,
                export_differences=export_differences
            )
            
            if result and ('differences_file' in result or 'diff_df' in result):
                differences_file = result.get('differences_file')
                diff_df = result.get('diff_df')  # Use DataFrame directly if no file was created
                fund_name = result.get('fund_name')
                fund_identifier = result.get('fund_identifier', fund_identifier)
                
                print(f"✅ Comparison completed successfully!")
                if fund_name:
                    print(f"📋 Fund: {fund_name} ({fund_identifier})")
                if differences_file:
                    print(f"📁 Differences file: {differences_file}")
                else:
                    print(f"📊 Found {len(diff_df)} differences (file export skipped)")
            else:
                print("⚠️  No differences found or comparison failed.")
                return False
                
        except Exception as e:
            print(f"❌ Error in comparison step: {e}")
            return False
    else:
        print("⏭️  STEP 1: SKIPPED (using existing differences file)")
        differences_file = None
        diff_df = None
        fund_identifier = fund_alias if fund_alias else fund_user_id
    
    print()
    
    # Step 2: Export formatted results
    print("📋 STEP 2: EXPORTING FORMATTED RESULTS")
    print("-" * 40)
    
    try:
        # Import and run the export_formatted_differences function
        from analyze_differences import export_formatted_differences
        
        # If we have a DataFrame from step 1 but no file, we need to handle this differently
        if not skip_comparison and diff_df is not None and differences_file is None:
            # We need to modify the analyze_differences function to accept a DataFrame directly
            # For now, let's create a temporary file
            from pathlib import Path
            from datetime import datetime
            temp_dir = Path("reports/temp")
            temp_dir.mkdir(parents=True, exist_ok=True)
            temp_file = temp_dir / f"temp_differences_{fund_identifier}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            diff_df.to_csv(temp_file, index=False)
            differences_file = str(temp_file)
            print(f"📄 Created temporary differences file for processing: {temp_file}")
        
        export_df = export_formatted_differences(
            differences_file=differences_file,
            fund_alias=fund_identifier,
            output_format=output_format
        )
        
        if export_df is not None:
            print(f"✅ Formatted export completed successfully!")
            print(f"📊 Exported {len(export_df):,} meaningful difference records")
        else:
            print("⚠️  Export failed or no data to export.")
            return False
            
        # Clean up temporary file if created
        if not skip_comparison and diff_df is not None:
            try:
                temp_file.unlink()
                print(f"🗑️  Cleaned up temporary file: {temp_file}")
            except:
                pass
            
    except Exception as e:
        print(f"❌ Error in export step: {e}")
        return False
    
    print()
    print("🎉 PIPELINE COMPLETED SUCCESSFULLY!")
    print("="*60)
    return True

def get_available_funds():
    """Get list of available fund aliases based on data files."""
    data_dir = Path("data")
    funds = []
    
    if data_dir.exists():
        # Look for fund CSV files
        csv_files = list(data_dir.glob("*.csv"))
        for csv_file in csv_files:
            if "20697244" in csv_file.name:  # PI fund
                funds.append("pi")
            elif "19441218" in csv_file.name:  # AI fund  
                funds.append("ai")
    
    return list(set(funds)) if funds else ["pi", "ai"]

def main():
    """Main entry point with command line interface."""
    
    parser = argparse.ArgumentParser(
        description='Complete fund analysis pipeline: extract, compare, and export',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Run complete analysis for PI fund (creates all files)
  python run_fund_analysis.py --fund pi --date 2025-05-30 --format excel
  
  # Run analysis for custom fund using user ID
  python run_fund_analysis.py --fund-user-id 12345678 --fund-csv /path/to/fund.csv --date 2025-05-30 --format excel
  
  # Only create the final Excel file (no intermediate files)
  python run_fund_analysis.py --fund pi --format excel --output-only
  
  # Skip data exports, only create differences and final output
  python run_fund_analysis.py --fund pi --format excel --no-data-export
  
  # Skip differences files, only create data exports and final output
  python run_fund_analysis.py --fund pi --format csv --no-differences-export
  
  # Only create the Google Sheets output
  python run_fund_analysis.py --fund pi --format google_sheets --output-only
  
  # Skip comparison step (use existing differences)
  python run_fund_analysis.py --fund pi --skip-comparison --format csv --output-only
  
  # Run for AI fund with only final CSV output
  python run_fund_analysis.py --fund ai --format csv --output-only

File Creation Options:
  --output-only           Only creates the final output file (Excel/CSV/Sheets)
  --no-data-export        Skips: internal_data_*.csv, fund_data_*.csv, merged_dataset_*.csv  
  --no-differences-export Skips: differences_*.csv, identical_sample_*.csv
  
  By default, all file types are created for full analysis capability.
'''
    )
    
    available_funds = get_available_funds()
    
    parser.add_argument(
        '--fund', 
        choices=['pi', 'ai'], 
        help='Fund alias to analyze (pi or ai)'
    )
    
    parser.add_argument(
        '--fund-user-id',
        help='Fund user ID to analyze (alternative to --fund)'
    )
    
    parser.add_argument(
        '--fund-csv',
        help='Path to fund CSV file (required when using --fund-user-id)'
    )
    
    parser.add_argument(
        '--date',
        default='2025-05-30',
        help='Reference date in YYYY-MM-DD format (default: 2025-05-30)'
    )
    
    parser.add_argument(
        '--format',
        choices=['excel', 'google_sheets', 'csv'],
        default='excel',
        help='Output format for results (default: excel)'
    )
    
    parser.add_argument(
        '--skip-comparison',
        action='store_true',
        help='Skip the comparison step and use existing differences file'
    )
    
    parser.add_argument(
        '--no-data-export',
        action='store_true',
        help='Skip exporting raw data files (internal data, fund data, merged dataset)'
    )
    
    parser.add_argument(
        '--no-differences-export',
        action='store_true',
        help='Skip exporting differences analysis files (differences.csv, identical_sample.csv)'
    )
    
    parser.add_argument(
        '--output-only',
        action='store_true',
        help='Only create the final output file (Excel/CSV/Sheets) - skips all intermediate files'
    )
    
    parser.add_argument(
        '--list-funds',
        action='store_true',
        help='List available funds and exit'
    )
    
    parser.add_argument(
        '--check-setup',
        action='store_true',
        help='Check if all required files and dependencies are available'
    )
    
    args = parser.parse_args()
    
    # Handle special commands
    if args.list_funds:
        print("Available funds:")
        for fund in available_funds:
            print(f"  - {fund}")
        return
    
    if args.check_setup:
        check_setup()
        return
    
    # Validate fund specification
    if not args.fund and not args.fund_user_id:
        print("❌ Error: Either --fund or --fund-user-id must be provided")
        parser.print_help()
        sys.exit(1)
    
    if args.fund_user_id and not args.fund_csv:
        print("❌ Error: --fund-csv is required when using --fund-user-id")
        sys.exit(1)
    
    # Validate date format
    try:
        datetime.strptime(args.date, '%Y-%m-%d')
    except ValueError:
        print("❌ Error: Date must be in YYYY-MM-DD format")
        sys.exit(1)
    
    # Run the analysis
    success = run_complete_analysis(
        fund_alias=args.fund or '',
        fund_user_id=args.fund_user_id or '',
        fund_csv_path=args.fund_csv,
        reference_date=args.date,
        output_format=args.format,
        skip_comparison=args.skip_comparison,
        export_data=not args.no_data_export,
        export_differences=not args.no_differences_export,
        output_only=args.output_only
    )
    
    if not success:
        sys.exit(1)

def check_setup():
    """Check if all required dependencies and files are available."""
    print("🔍 CHECKING SETUP")
    print("="*30)
    
    # Check Python packages
    required_packages = ['pandas', 'google-cloud-bigquery', 'openpyxl']
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - Install with: pip install {package}")
    
    # Check directories
    dirs_to_check = ['reports', 'sql', 'src']
    for dir_name in dirs_to_check:
        if Path(dir_name).exists():
            print(f"✅ {dir_name}/ directory")
        else:
            print(f"❌ {dir_name}/ directory missing")
    
    # Check SQL files
    sql_files = ['extract_cession_orders.sql', 'get_fund_info.sql']
    for sql_file in sql_files:
        sql_path = Path("sql") / sql_file
        if sql_path.exists():
            print(f"✅ {sql_file}")
        else:
            print(f"❌ {sql_file} missing")
    
    print()
    print("Setup check completed!")

if __name__ == "__main__":
    main() 