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

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.csv_loader import CSVLoader
from src.core.comparator import CSVComparator, ComparisonType
from src.core.bigquery_loader import extract_internal_data


def export_differences(fund_alias='pi', reference_date='2025-05-30', export_data=True, export_differences=True):
    """Export differing records to CSV for analysis."""
    
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
    
    # Fund CSV file mapping - Add new fund aliases and their corresponding file paths here
    FUND_CSV_MAPPING = {
        'pi': "/Users/raphaellafeldt/Git/fidc_data_check/data/Posição em carteira cw - 20697244 - 2025_05_30.csv",
        'ai': "/Users/raphaellafeldt/Git/fidc_data_check/data/Posição em carteira cw - 19441218 - 2025_05_30.csv",
        # 'new_fund_alias': "/path/to/new/fund/file.csv",
        # 'another_fund': "/path/to/another/fund/file.csv",
    }
    
    # Extract internal data
    print("📊 Extracting internal data...")
    internal_df, internal_metadata = extract_internal_data(
        reference_date=reference_date,
        fund_alias=fund_alias
    )
    
    # Export internal data only if requested
    if export_data:
        internal_export_file = data_exports_dir / f"internal_data_{fund_alias}_{reference_date.replace('-', '')}_{timestamp}.csv"
        internal_df.to_csv(internal_export_file, index=False)
        print(f"💾 Internal data exported to: {internal_export_file}")
    else:
        print("⏭️  Skipping internal data export")
        internal_export_file = None
    
    # Load fund CSV
    print("📄 Loading fund report...")
    if fund_alias not in FUND_CSV_MAPPING:
        raise ValueError(f"Unknown fund alias '{fund_alias}'. Available options: {list(FUND_CSV_MAPPING.keys())}")
    
    fund_csv = FUND_CSV_MAPPING[fund_alias]
    
    loader = CSVLoader()
    fund_df, fund_metadata = loader.load_csv(fund_csv)
    
    # Export processed fund data only if requested
    if export_data:
        fund_export_file = data_exports_dir / f"fund_data_processed_{fund_alias}_{reference_date.replace('-', '')}_{timestamp}.csv"
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
            # Export differences with organized naming
            diff_file = differences_dir / f"differences_{fund_alias}_{reference_date.replace('-', '')}_{timestamp}.csv"
            diff_df.to_csv(diff_file, index=False)
            print(f"✅ Differences exported to: {diff_file}")
            
            # Export sample of matching records for comparison
            print("📊 Creating sample of identical records...")
            
            # Get common columns
            common_cols = list(set(internal_df.columns) & set(fund_df.columns))
            
            # Merge to get identical records
            merged = pd.merge(
                internal_df, fund_df,
                on=['NumeroContrato'],
                how='inner',
                suffixes=('_internal', '_fund')
            )
            
            # Filter for identical records (not in differences)
            diff_contratos = set(result.differences['different_records'].keys())
            identical_records = merged[~merged['NumeroContrato'].astype(str).isin(diff_contratos)]
            
            # Sample 100 identical records
            sample_identical = identical_records.head(100)
            sample_file = differences_dir / f"identical_sample_{fund_alias}_{reference_date.replace('-', '')}_{timestamp}.csv"
            sample_identical.to_csv(sample_file, index=False)
            print(f"✅ Sample identical records exported to: {sample_file}")
        else:
            print("⏭️  Skipping differences export")
            diff_file = None
            sample_file = None
        
        # Export merged dataset for further analysis only if requested
        if export_data:
            merged_file = data_exports_dir / f"merged_dataset_{fund_alias}_{reference_date.replace('-', '')}_{timestamp}.csv"
            merged.to_csv(merged_file, index=False)
            print(f"💾 Complete merged dataset exported to: {merged_file}")
        else:
            print("⏭️  Skipping merged dataset export")
            merged_file = None
        
        # Generate summary statistics
        print("\n" + "="*60)
        print("📈 DIFFERENCE ANALYSIS SUMMARY")
        print("="*60)
        
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
            'diff_df': diff_df  # Pass the DataFrame for further processing
        }
        
    else:
        print("✅ No differences found!")
        return {'summary': result.summary}


if __name__ == "__main__":
    import sys
    fund_alias = sys.argv[1] if len(sys.argv) > 1 else 'pi'
    reference_date = sys.argv[2] if len(sys.argv) > 2 else '2025-05-30'
    export_data = '--no-data-export' not in sys.argv
    export_differences = '--no-differences-export' not in sys.argv
    export_differences(fund_alias, reference_date, export_data, export_differences) 