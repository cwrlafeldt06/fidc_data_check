#!/usr/bin/env python3
"""
Export differences between internal and fund data in formatted output.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import sys
import glob

def export_formatted_differences(differences_file=None, fund_identifier='pi', output_format='excel'):
    """
    Export differences data in the requested format with specific columns:
    - id (NumeroContrato)
    - internal face value
    - fund face value  
    - internal acquisition value
    - fund acquisition value
    
    Supports Google Sheets, Excel, or CSV output.
    """
    
    # If no specific file provided, find the most recent differences file
    if not differences_file:
        differences_dir = Path("reports/differences")
        if differences_dir.exists():
            # Find most recent differences file for the specified fund
            pattern = f"differences_{fund_identifier}_*.csv"
            files = list(differences_dir.glob(pattern))
            if not files:
                # Try alternative patterns
                pattern = f"{fund_identifier}_fund_differences.csv"
                files = list(differences_dir.glob(pattern))
            if not files:
                # Try with legacy fund alias patterns
                legacy_patterns = [
                    f"differences_pi_*.csv",
                    f"differences_ai_*.csv",
                    "pi_fund_differences.csv",
                    "ai_fund_differences.csv"
                ]
                for legacy_pattern in legacy_patterns:
                    files.extend(list(differences_dir.glob(legacy_pattern)))
            
            if files:
                differences_file = max(files, key=lambda p: p.stat().st_mtime)
                print(f"Using most recent differences file: {differences_file}")
            else:
                print(f"❌ No differences files found for fund '{fund_identifier}' in {differences_dir}")
                return
        else:
            print("❌ Reports directory not found. Run export_differences.py first.")
            return
    else:
        differences_file = Path(differences_file)
    
    if not differences_file.exists():
        print(f"❌ File not found: {differences_file}")
        return
    
    # Load the differences
    diff_df = pd.read_csv(differences_file)
    
    print('=== EXPORTING FORMATTED DIFFERENCES ===')
    print(f'Source file: {differences_file}')
    print(f'Total differing records: {len(diff_df):,}')
    
    # Filter out rows with differences under 0.5 cents (likely rounding errors)
    def is_meaningful_difference(row):
        """Check if the row has meaningful differences (>= 0.5 cents)"""
        meaningful = False
        
        # Check ValorFace difference
        if pd.notna(row.get('ValorFace_Difference')):
            if abs(row['ValorFace_Difference']) >= 0.5:
                meaningful = True
                
        # Check ValorAquisicao difference  
        if pd.notna(row.get('ValorAquisicao_Difference')):
            if abs(row['ValorAquisicao_Difference']) >= 0.5:
                meaningful = True
                
        return meaningful
    
    # Apply filter
    filtered_df = diff_df[diff_df.apply(is_meaningful_difference, axis=1)]
    
    print(f'Records with meaningful differences (>= 0.5 cents): {len(filtered_df):,}')
    print(f'Filtered out small differences: {len(diff_df) - len(filtered_df):,}')
    print()
    
    # Create the formatted output DataFrame with requested columns
    formatted_data = []
    
    for _, row in filtered_df.iterrows():
        record = {
            'id': row['NumeroContrato'],
            'internal_face_value': row.get('ValorFace_Internal', ''),
            'fund_face_value': row.get('ValorFace_Fund', ''),
            'internal_acquisition_value': row.get('ValorAquisicao_Internal', ''),
            'fund_acquisition_value': row.get('ValorAquisicao_Fund', '')
        }
        formatted_data.append(record)
    
    # Create DataFrame
    export_df = pd.DataFrame(formatted_data)
    
    # Create output directory
    output_dir = Path("reports/formatted_exports")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Export based on format
    if output_format == 'google_sheets':
        success = export_to_google_sheets(export_df, fund_identifier, timestamp, output_dir)
    elif output_format == 'excel':
        success = export_to_excel(export_df, fund_identifier, timestamp, output_dir)
    elif output_format == 'csv':
        success = export_to_csv(export_df, fund_identifier, timestamp, output_dir)
    else:
        print(f"❌ Unsupported output format: {output_format}")
        return None
    
    if success:
        print(f"\n✅ Successfully exported {len(export_df):,} meaningful differences in {output_format} format")
        return export_df
    else:
        print(f"\n❌ Export failed for {output_format} format")
        return None


def export_to_google_sheets(df, fund_identifier, timestamp, output_dir):
    """Export to Google Sheets."""
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        
        # Load credentials
        creds_file = "google_credentials.json"
        if not Path(creds_file).exists():
            print(f"❌ Google credentials file not found: {creds_file}")
            print("   See GOOGLE_SHEETS_SETUP.md for setup instructions")
            return False
        
        # Define the scope
        scope = ['https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive']
        
        # Create credentials object
        creds = Credentials.from_service_account_file(creds_file, scopes=scope)
        client = gspread.authorize(creds)
        
        # Create spreadsheet
        sheet_name = f"Fund Differences {fund_identifier} {timestamp}"
        spreadsheet = client.create(sheet_name)
        worksheet = spreadsheet.sheet1
        
        # Prepare data for upload
        header = list(df.columns)
        values = [header] + df.values.tolist()
        
        # Upload to Google Sheets
        worksheet.update('A1', values)
        
        # Format header row
        worksheet.format('A1:E1', {
            "backgroundColor": {"red": 0.2, "green": 0.6, "blue": 0.8},
            "textFormat": {"foregroundColor": {"red": 1, "green": 1, "blue": 1}, "bold": True}
        })
        
        print(f"✅ Successfully exported to Google Sheets: {spreadsheet.url}")
        
        # Also save the URL locally
        url_file = output_dir / f"google_sheets_url_{fund_identifier}_{timestamp}.txt"
        with open(url_file, 'w') as f:
            f.write(f"Google Sheets URL:\n{spreadsheet.url}\n")
            f.write(f"Sheet Name: {sheet_name}\n")
            f.write(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        return True
        
    except ImportError:
        print("❌ Google Sheets export requires: pip install gspread google-auth")
        return False
    except Exception as e:
        print(f"❌ Google Sheets export failed: {e}")
        return False


def export_to_excel(df, fund_identifier, timestamp, output_dir):
    """Export to Excel file with formatting."""
    try:
        excel_file = output_dir / f"fund_differences_{fund_identifier}_{timestamp}.xlsx"
        
        # Create Excel writer with styling
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Differences', index=False)
            
            # Get the workbook and worksheet for formatting
            workbook = writer.book
            worksheet = writer.sheets['Differences']
            
            # Format headers
            from openpyxl.styles import Font, PatternFill, Alignment
            
            header_font = Font(bold=True, color="FFFFFF")
            header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
            
            for cell in worksheet[1]:
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = Alignment(horizontal="center")
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        print(f"✅ Successfully exported to Excel: {excel_file}")
        return True
        
    except Exception as e:
        print(f"❌ Excel export failed: {e}")
        return False


def export_to_csv(df, fund_identifier, timestamp, output_dir):
    """Export to CSV file."""
    try:
        csv_file = output_dir / f"fund_differences_{fund_identifier}_{timestamp}.csv"
        df.to_csv(csv_file, index=False)
        print(f"✅ Successfully exported to CSV: {csv_file}")
        return True
    except Exception as e:
        print(f"❌ CSV export failed: {e}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Export fund differences in formatted output')
    parser.add_argument('--file', help='Specific differences file to process')
    parser.add_argument('--fund', default='pi', help='Fund identifier (default: pi)')
    parser.add_argument('--format', choices=['google_sheets', 'excel', 'csv'], default='excel', 
                       help='Output format (default: excel)')
    
    args = parser.parse_args()
    
    # Export formatted differences
    export_formatted_differences(args.file, args.fund, args.format) 