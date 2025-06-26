#!/usr/bin/env python3
"""
Export differing records from comparison for analysis.
"""

import pandas as pd
import json
import os
import sys
from pathlib import Path
from datetime import datetime
import numpy as np

# Add project root and src to path for imports
project_root = os.path.join(os.path.dirname(__file__), '..')
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, project_root)
sys.path.insert(0, src_path)

from core.csv_loader import CSVLoader
from core.comparator import CSVComparator, ComparisonType
from core.bigquery_loader import extract_internal_data, get_fund_info
from core.fund_config import get_fund_config


def export_differences(fund_alias='', fund_user_id='', reference_date='2025-05-30', 
                      fund_csv_path=None, export_data=True, export_differences=True):
    """Export differing records to CSV for analysis."""
    
    if not fund_alias and not fund_user_id:
        raise ValueError("Either fund_alias or fund_user_id must be provided")
    
    print("🔍 Running comparison and exporting differences...")
    
    # Create timestamp for file naming
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create output directories only if needed
    reports_dir = Path("reports")
    if export_differences:
        differences_dir = reports_dir / "differences"
        differences_dir.mkdir(parents=True, exist_ok=True)
    
    if export_data:
        data_exports_dir = reports_dir / "data_exports"
        data_exports_dir.mkdir(parents=True, exist_ok=True)
    
    # Configuration
    config_dict = {
        "float_tolerance": 0.05,
        "ignore_case": False,
        "ignore_whitespace": True,
        "ignore_columns": [],
        "key_columns": ["NumeroContrato"]
    }
    
    # If using fund_user_id, get fund info first
    fund_name = None
    fund_identifier = fund_alias if fund_alias else fund_user_id
    
    if fund_user_id:
        print(f"📋 Getting fund information for user ID: {fund_user_id}")
        try:
            fund_info_df, _ = get_fund_info(fund_user_id)
            if len(fund_info_df) > 0:
                fund_name = fund_info_df.iloc[0]['fund_name']
                fund_alias = fund_info_df.iloc[0]['fund_alias'] or fund_user_id
                print(f"✅ Found fund: {fund_name} (Alias: {fund_alias})")
            else:
                print(f"⚠️  No fund found for user ID: {fund_user_id}")
                fund_alias = fund_user_id
        except Exception as e:
            print(f"⚠️  Could not get fund info: {e}")
            fund_alias = fund_user_id
    
    # Convert command-line fund alias to database alias if using predefined funds
    database_fund_alias = fund_alias
    if fund_alias and not fund_user_id:
        fund_config = get_fund_config(fund_alias)
        if fund_config:
            database_fund_alias = fund_config['alias']
            print(f"📋 Using database alias '{database_fund_alias}' for fund '{fund_alias}'")
        else:
            print(f"⚠️  Fund '{fund_alias}' not found in predefined configurations")
    
    # Fund CSV file mapping - Only PI and AI have predefined CSV files
    # Other funds (akira1, akira2, bigpicture1, etc.) require CSV file upload
    FUND_CSV_MAPPING = {
        'pi': "/Users/raphaellafeldt/Git/fidc_data_check/data/Posição em carteira cw - 20697244 - 2025_05_30.csv",
        'ai': "/Users/raphaellafeldt/Git/fidc_data_check/data/Posição em carteira cw - 19441218 - 2025_05_30.csv",
    }
    
    # Extract internal data
    print("📊 Extracting internal data...")
    
    # Use the database alias for BigQuery filtering
    internal_df, internal_metadata = extract_internal_data(
        reference_date=reference_date,
        fund_alias=database_fund_alias,
        fund_user_id=fund_user_id
    )
    
    # Export internal data only if requested
    if export_data:
        internal_export_file = data_exports_dir / f"internal_data_{fund_identifier}_{reference_date.replace('-', '')}_{timestamp}.csv"
        internal_df.to_csv(internal_export_file, index=False)
        print(f"💾 Internal data exported to: {internal_export_file}")
    else:
        print("⏭️  Skipping internal data export")
        internal_export_file = None
    
    # Load fund CSV
    print("📄 Loading fund report...")
    
    # Use provided CSV path or try to find from mapping
    if fund_csv_path:
        fund_csv = fund_csv_path
        print(f"Using provided CSV file: {fund_csv}")
    elif fund_alias in FUND_CSV_MAPPING:
        fund_csv = FUND_CSV_MAPPING[fund_alias]
    else:
        raise ValueError(f"No CSV file provided and unknown fund alias '{fund_alias}'. "
                        f"Available predefined options: {list(FUND_CSV_MAPPING.keys())} "
                        f"or provide fund_csv_path parameter.")
    
    loader = CSVLoader()
    fund_df, fund_metadata = loader.load_csv(fund_csv)
    
    # Export processed fund data only if requested
    if export_data:
        fund_export_file = data_exports_dir / f"fund_data_processed_{fund_identifier}_{reference_date.replace('-', '')}_{timestamp}.csv"
        fund_df.to_csv(fund_export_file, index=False)
        print(f"💾 Fund data exported to: {fund_export_file}")
    else:
        print("⏭️  Skipping fund data export")
        fund_export_file = None
    
    # Perform comparison
    print("⚖️  Performing comparison...")
    comparator = CSVComparator(config_dict)
    result = comparator.compare_dataframes(
        internal_df, fund_df, 
        ComparisonType.FULL, 
        internal_metadata, fund_metadata
    )
    
    # Extract differing records
    if result.differences.get('different_records'):
        print(f"📋 Found {len(result.differences['different_records'])} differing records")
        
        # Create detailed differences DataFrame
        diff_data = []
        
        for numero_contrato, differences in result.differences['different_records'].items():
            base_row = {
                'NumeroContrato': numero_contrato,
                'HasDifferences': True
            }
            
            # Add each difference as columns
            for field, values in differences.items():
                base_row[f'{field}_Internal'] = values['internal']
                base_row[f'{field}_Fund'] = values['fund']
                if values['difference'] != 'N/A':
                    base_row[f'{field}_Difference'] = values['difference']
                    base_row[f'{field}_Diff_Percent'] = (
                        abs(values['difference']) / abs(values['fund']) * 100 
                        if values['fund'] != 0 else 'N/A'
                    )
            
            diff_data.append(base_row)
        
        # Create DataFrame and export differences only if requested
        diff_df = pd.DataFrame(diff_data)
        
        if export_differences:
            diff_file = differences_dir / f"differences_{fund_identifier}_{reference_date.replace('-', '')}_{timestamp}.csv"
            diff_df.to_csv(diff_file, index=False)
            print(f"💾 Differences exported to: {diff_file}")
        else:
            print("⏭️  Skipping differences export")
            diff_file = None
        
        # Also export a sample of identical records for verification only if requested
        if export_differences and result.summary.get('identical_records', 0) > 0:
            # Get sample of identical records
            identical_sample_size = min(100, result.summary['identical_records'])
            sample_file = differences_dir / f"identical_sample_{fund_identifier}_{reference_date.replace('-', '')}_{timestamp}.csv"
            
            # Create a sample of identical records for verification
            merged = internal_df.merge(fund_df, on='NumeroContrato', how='inner', suffixes=('_Internal', '_Fund'))
            identical_records = merged[
                (abs(merged.get('ValorFace_Internal', 0) - merged.get('ValorFace_Fund', 0)) <= config_dict['float_tolerance']) &
                (abs(merged.get('ValorAquisicao_Internal', 0) - merged.get('ValorAquisicao_Fund', 0)) <= config_dict['float_tolerance'])
            ]
            
            if len(identical_records) > 0:
                sample_identical = identical_records.sample(n=min(identical_sample_size, len(identical_records)), random_state=42)
                sample_identical.to_csv(sample_file, index=False)
                print(f"💾 Identical records sample exported to: {sample_file}")
            else:
                sample_file = None
                print("⚠️  No identical records found for sample export")
        else:
            print("⏭️  Skipping identical sample export")
            sample_file = None
        
        # Export merged dataset for further analysis only if requested
        if export_data:
            merged_file = data_exports_dir / f"merged_dataset_{fund_identifier}_{reference_date.replace('-', '')}_{timestamp}.csv"
            merged = internal_df.merge(fund_df, on='NumeroContrato', how='outer', suffixes=('_Internal', '_Fund'))
            merged.to_csv(merged_file, index=False)
            print(f"💾 Complete merged dataset exported to: {merged_file}")
        else:
            print("⏭️  Skipping merged dataset export")
            merged_file = None
        
        # Generate summary statistics
        print("\n" + "="*60)
        print("📈 DIFFERENCE ANALYSIS SUMMARY")
        print("="*60)
        
        if fund_name:
            print(f"Fund: {fund_name} ({fund_identifier})")
        else:
            print(f"Fund: {fund_identifier}")
        print(f"Total Fund Records: {len(fund_df):,}")
        print(f"Total Internal Records: {len(internal_df):,}")
        print(f"Common Records: {result.summary.get('common_cession_records', 0):,}")
        print(f"Identical Records: {result.summary.get('identical_records', 0):,}")
        print(f"Different Records: {len(result.differences['different_records']):,}")
        print(f"Match Percentage: {result.summary.get('match_percentage', 0):.1f}%")
        print(f"Coverage Percentage: {result.summary.get('coverage_percentage', 0):.1f}%")
        
        # Analyze difference patterns
        if 'ValorFace_Difference' in diff_df.columns:
            valor_face_diffs = diff_df['ValorFace_Difference'].dropna()
            if len(valor_face_diffs) > 0:
                print(f"\nValorFace Differences:")
                print(f"  Records: {len(valor_face_diffs):,}")
                print(f"  Mean Difference: {valor_face_diffs.mean():.2f}")
                print(f"  Median Difference: {valor_face_diffs.median():.2f}")
                print(f"  Max Difference: {valor_face_diffs.max():.2f}")
                print(f"  Min Difference: {valor_face_diffs.min():.2f}")
            
        if 'ValorAquisicao_Difference' in diff_df.columns:
            valor_aquisicao_diffs = diff_df['ValorAquisicao_Difference'].dropna()
            print(f"\nValorAquisicao Differences:")
            print(f"  Records: {len(valor_aquisicao_diffs):,}")
            print(f"  Mean Difference: {valor_aquisicao_diffs.mean():.6f}")
            print(f"  Median Difference: {valor_aquisicao_diffs.median():.6f}")
            print(f"  Max Difference: {valor_aquisicao_diffs.max():.2f}")
            print(f"  Min Difference: {valor_aquisicao_diffs.min():.2f}")
        
        print(f"\n📁 Files created:")
        if export_differences and diff_file:
            print(f"  📊 Differences: {diff_file}")
        if export_differences and sample_file:
            print(f"  📊 Identical sample: {sample_file}")
        if export_data and internal_export_file:
            print(f"  💾 Internal data: {internal_export_file}")
        if export_data and fund_export_file:
            print(f"  💾 Fund data: {fund_export_file}")
        if export_data and merged_file:
            print(f"  💾 Merged dataset: {merged_file}")
        
        return {
            'differences_file': str(diff_file) if diff_file else None,
            'identical_sample_file': str(sample_file) if sample_file else None,
            'internal_data_file': str(internal_export_file) if internal_export_file else None,
            'fund_data_file': str(fund_export_file) if fund_export_file else None,
            'merged_dataset_file': str(merged_file) if merged_file else None,
            'summary': result.summary,
            'diff_df': diff_df,  # Pass the DataFrame for further processing
            'fund_name': fund_name,
            'fund_identifier': fund_identifier
        }
        
    else:
        print("✅ No differences found!")
        return {
            'summary': result.summary,
            'fund_name': fund_name,
            'fund_identifier': fund_identifier
        }


if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='Export fund differences for analysis')
    parser.add_argument('--fund-alias', help='Fund alias (pi, ai)')
    parser.add_argument('--fund-user-id', help='Fund user ID')
    parser.add_argument('--reference-date', default='2025-05-30', help='Reference date (YYYY-MM-DD)')
    parser.add_argument('--fund-csv', help='Path to fund CSV file')
    parser.add_argument('--no-data-export', action='store_true', help='Skip data export files')
    parser.add_argument('--no-differences-export', action='store_true', help='Skip differences export files')
    
    args = parser.parse_args()
    
    # Ensure at least one fund identifier is provided
    if not args.fund_alias and not args.fund_user_id:
        # Try legacy argument parsing for backward compatibility
        if len(sys.argv) > 1 and sys.argv[1] in ['pi', 'ai']:
            args.fund_alias = sys.argv[1]
            args.reference_date = sys.argv[2] if len(sys.argv) > 2 else '2025-05-30'
        else:
            print("❌ Error: Either --fund-alias or --fund-user-id must be provided")
            parser.print_help()
            sys.exit(1)
    
    export_data = not args.no_data_export
    export_differences = not args.no_differences_export
    
    export_differences(
        fund_alias=args.fund_alias or '',
        fund_user_id=args.fund_user_id or '', 
        reference_date=args.reference_date,
        fund_csv_path=args.fund_csv,
        export_data=export_data,
        export_differences=export_differences
    ) 