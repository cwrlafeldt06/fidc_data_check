#!/usr/bin/env python3
"""
Quick fund analysis - simplified interface.
Just run this script for the most common use case.
"""

import sys
from datetime import datetime
from run_fund_analysis import run_complete_analysis

def main():
    """Quick analysis with sensible defaults."""
    
    # Default parameters
    fund_alias = 'pi'
    reference_date = '2025-05-30'
    output_format = 'excel'
    
    # Allow simple command line overrides
    if len(sys.argv) > 1:
        first_arg = sys.argv[1].lower()
        
        # Check if it's a predefined fund
        predefined_funds = ['pi', 'ai', 'akira1', 'akira2', 'bigpicture1', 'bigpicture2', 'bigpicture3', 'bigpicture4', 'kickass1', 'kickass2']
        if first_arg in predefined_funds:
            fund_alias = first_arg
        else:
            print("❌ Invalid fund specification")
            print("Usage: python quick_analysis.py [pi|ai|akira1|akira2|bigpicture1|bigpicture2|bigpicture3|bigpicture4|kickass1|kickass2] [excel|csv|google_sheets]")
            sys.exit(1)
    
    # Get output format from second argument
    if len(sys.argv) > 2:
        output_format = sys.argv[2].lower()
    
    # Validate output format
    if output_format not in ['excel', 'csv', 'google_sheets']:
        print("❌ Format must be 'excel', 'csv', or 'google_sheets'")
        print("Usage: python quick_analysis.py [pi|ai|akira1|akira2|bigpicture1|bigpicture2|bigpicture3|bigpicture4|kickass1|kickass2] [excel|csv|google_sheets]")
        sys.exit(1)
    
    print("🎯 QUICK FUND ANALYSIS")
    print("=" * 30)
    print(f"Fund: {fund_alias.upper()}")
    print(f"Format: {output_format}")
    print("=" * 30)
    print()
    
    # Run the analysis
    success = run_complete_analysis(
        fund_alias=fund_alias,
        fund_user_id='',
        fund_csv_path=None,
        reference_date=reference_date,
        output_format=output_format,
        skip_comparison=False
    )
    
    if success:
        print("\n✨ Check the 'reports/formatted_exports/' folder for your results!")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main() 