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

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def run_complete_analysis(fund_alias='pi', reference_date='2025-05-30', output_format='excel', skip_comparison=False):
    """
    Run the complete fund analysis pipeline:
    1. Extract data and compare (export_differences.py)
    2. Export formatted results (analyze_differences.py)
    """
    
    print("🚀 STARTING COMPLETE FUND ANALYSIS PIPELINE")
    print("="*60)
    print(f"Fund: {fund_alias.upper()}")
    print(f"Reference Date: {reference_date}")
    print(f"Output Format: {output_format}")
    print("="*60)
    print()
    
    # Step 1: Run comparison and generate differences (unless skipped)
    if not skip_comparison:
        print("📊 STEP 1: EXTRACTING DATA AND COMPARING")
        print("-" * 40)
        
        try:
            # Import and run the export_differences function
            from export_differences import export_differences
            
            result = export_differences(fund_alias=fund_alias, reference_date=reference_date)
            
            if result and 'differences_file' in result:
                differences_file = result['differences_file']
                print(f"✅ Comparison completed successfully!")
                print(f"📁 Differences file: {differences_file}")
            else:
                print("⚠️  No differences found or comparison failed.")
                return False
                
        except Exception as e:
            print(f"❌ Error in comparison step: {e}")
            return False
    else:
        print("⏭️  STEP 1: SKIPPED (using existing differences file)")
        differences_file = None
    
    print()
    
    # Step 2: Export formatted results
    print("📋 STEP 2: EXPORTING FORMATTED RESULTS")
    print("-" * 40)
    
    try:
        # Import and run the export_formatted_differences function
        from analyze_differences import export_formatted_differences
        
        export_df = export_formatted_differences(
            differences_file=differences_file,
            fund_alias=fund_alias,
            output_format=output_format
        )
        
        if export_df is not None:
            print(f"✅ Formatted export completed successfully!")
            print(f"📊 Exported {len(export_df):,} meaningful difference records")
        else:
            print("⚠️  Export failed or no data to export.")
            return False
            
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
  # Run complete analysis for PI fund
  python run_fund_analysis.py --fund pi --date 2025-05-30 --format excel
  
  # Run with Google Sheets export
  python run_fund_analysis.py --fund pi --format google_sheets
  
  # Skip comparison step (use existing differences)
  python run_fund_analysis.py --fund pi --skip-comparison --format csv
  
  # Run for AI fund
  python run_fund_analysis.py --fund ai --date 2025-05-30 --format excel
'''
    )
    
    available_funds = get_available_funds()
    
    parser.add_argument(
        '--fund', 
        choices=['pi', 'ai'], 
        default='pi',
        help='Fund alias to analyze (default: pi)'
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
    
    # Validate date format
    try:
        datetime.strptime(args.date, '%Y-%m-%d')
    except ValueError:
        print("❌ Error: Date must be in YYYY-MM-DD format")
        sys.exit(1)
    
    # Run the analysis
    success = run_complete_analysis(
        fund_alias=args.fund,
        reference_date=args.date,
        output_format=args.format,
        skip_comparison=args.skip_comparison
    )
    
    if not success:
        sys.exit(1)

def check_setup():
    """Check if all required components are available."""
    print("🔍 CHECKING SETUP")
    print("="*40)
    
    # Check Python packages
    required_packages = [
        'pandas', 'numpy', 'google-cloud-bigquery', 
        'openpyxl', 'gspread', 'google-auth'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} (missing)")
            missing_packages.append(package)
    
    # Check data files
    print("\n📁 DATA FILES:")
    data_dir = Path("data")
    if data_dir.exists():
        csv_files = list(data_dir.glob("*.csv"))
        if csv_files:
            for csv_file in csv_files:
                print(f"✅ {csv_file.name}")
        else:
            print("⚠️  No CSV files found in data/ directory")
    else:
        print("❌ data/ directory not found")
    
    # Check Google credentials
    print("\n🔐 GOOGLE CREDENTIALS:")
    if Path("google_credentials.json").exists():
        print("✅ google_credentials.json found")
    else:
        print("⚠️  google_credentials.json not found (Google Sheets export won't work)")
        print("   See GOOGLE_SHEETS_SETUP.md for setup instructions")
    
    # Check output directories
    print("\n📂 OUTPUT DIRECTORIES:")
    for dir_name in ["reports", "reports/differences", "reports/formatted_exports"]:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"✅ {dir_name}/")
        else:
            print(f"📁 {dir_name}/ (will be created)")
    
    print("\n" + "="*40)
    if missing_packages:
        print("⚠️  Install missing packages with:")
        print(f"   pip install {' '.join(missing_packages)}")
    else:
        print("✅ All required packages are installed!")

if __name__ == "__main__":
    main() 