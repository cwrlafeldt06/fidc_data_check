#!/usr/bin/env python3
"""
Analyze the patterns in differences between internal and fund data.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import sys
import glob

def analyze_differences(differences_file=None, fund_alias='pi', save_analysis=True):
    """Analyze the difference patterns."""
    
    # If no specific file provided, find the most recent differences file
    if not differences_file:
        differences_dir = Path("reports/differences")
        if differences_dir.exists():
            # Find most recent differences file for the specified fund
            pattern = f"differences_{fund_alias}_*.csv"
            files = list(differences_dir.glob(pattern))
            if files:
                differences_file = max(files, key=lambda p: p.stat().st_mtime)
                print(f"Using most recent differences file: {differences_file}")
            else:
                print(f"❌ No differences files found for fund '{fund_alias}' in {differences_dir}")
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
    
    print('=== ANALYSIS OF FUND DIFFERENCES ===')
    print(f'File: {differences_file}')
    print(f'Total differing records: {len(diff_df):,}')
    print()
    
    analysis_results = []
    
    # Analyze ValorFace differences
    if 'ValorFace_Difference' in diff_df.columns:
        vf_diffs = diff_df['ValorFace_Difference'].dropna()
        vf_pcts = diff_df['ValorFace_Diff_Percent'].dropna()
        
        if len(vf_diffs) > 0:
            print('📊 VALOR FACE DIFFERENCES:')
            print(f'  Records with ValorFace differences: {len(vf_diffs):,}')
            print(f'  Mean difference: {vf_diffs.mean():.2f}')
            print(f'  Median difference: {vf_diffs.median():.2f}') 
            print(f'  Max difference: {vf_diffs.max():.2f}')
            print(f'  Min difference: {vf_diffs.min():.2f}')
            print(f'  Std deviation: {vf_diffs.std():.2f}')
            print(f'  Mean % difference: {vf_pcts.mean():.3f}%')
            print(f'  Median % difference: {vf_pcts.median():.3f}%')
            print()
            
            analysis_results.append({
                'field': 'ValorFace',
                'records_with_differences': len(vf_diffs),
                'mean_difference': vf_diffs.mean(),
                'median_difference': vf_diffs.median(),
                'max_difference': vf_diffs.max(),
                'min_difference': vf_diffs.min(),
                'std_deviation': vf_diffs.std(),
                'mean_percent_difference': vf_pcts.mean(),
                'median_percent_difference': vf_pcts.median()
            })
    
    # Analyze ValorAquisicao differences  
    if 'ValorAquisicao_Difference' in diff_df.columns:
        va_diffs = diff_df['ValorAquisicao_Difference'].dropna()
        va_pcts = diff_df['ValorAquisicao_Diff_Percent'].dropna()
        
        print('💰 VALOR AQUISICAO DIFFERENCES:')
        print(f'  Records with ValorAquisicao differences: {len(va_diffs):,}')
        print(f'  Mean difference: {va_diffs.mean():.6f}')
        print(f'  Median difference: {va_diffs.median():.6f}')
        print(f'  Max difference: {va_diffs.max():.2f}')
        print(f'  Min difference: {va_diffs.min():.2f}')
        print(f'  Std deviation: {va_diffs.std():.6f}')
        print(f'  Mean % difference: {va_pcts.mean():.6f}%')
        print(f'  Median % difference: {va_pcts.median():.6f}%')
        print()
        
        analysis_results.append({
            'field': 'ValorAquisicao',
            'records_with_differences': len(va_diffs),
            'mean_difference': va_diffs.mean(),
            'median_difference': va_diffs.median(),
            'max_difference': va_diffs.max(),
            'min_difference': va_diffs.min(),
            'std_deviation': va_diffs.std(),
            'mean_percent_difference': va_pcts.mean(),
            'median_percent_difference': va_pcts.median()
        })
        
        # Pattern analysis
        print('🔍 DIFFERENCE PATTERNS:')
        
        # Small differences (likely rounding)
        small_va = va_diffs[abs(va_diffs) <= 0.1]
        medium_va = va_diffs[(abs(va_diffs) > 0.1) & (abs(va_diffs) <= 10)]
        large_va = va_diffs[abs(va_diffs) > 10]
        
        print(f'  ValorAquisicao small differences (≤0.1): {len(small_va):,} ({len(small_va)/len(va_diffs)*100:.1f}%)')
        print(f'  ValorAquisicao medium differences (0.1-10): {len(medium_va):,} ({len(medium_va)/len(va_diffs)*100:.1f}%)')
        print(f'  ValorAquisicao large differences (>10): {len(large_va):,} ({len(large_va)/len(va_diffs)*100:.1f}%)')
        
        pattern_analysis = {
            'small_differences_count': len(small_va),
            'small_differences_percent': len(small_va)/len(va_diffs)*100,
            'medium_differences_count': len(medium_va),
            'medium_differences_percent': len(medium_va)/len(va_diffs)*100,
            'large_differences_count': len(large_va),
            'large_differences_percent': len(large_va)/len(va_diffs)*100
        }
        
        if 'ValorFace_Difference' in diff_df.columns:
            vf_diffs = diff_df['ValorFace_Difference'].dropna()
            if len(vf_diffs) > 0:
                small_vf = vf_diffs[abs(vf_diffs) <= 1]
                medium_vf = vf_diffs[(abs(vf_diffs) > 1) & (abs(vf_diffs) <= 100)]
                large_vf = vf_diffs[abs(vf_diffs) > 100]
                
                print(f'  ValorFace small differences (≤1): {len(small_vf):,} ({len(small_vf)/len(vf_diffs)*100:.1f}%)')
                print(f'  ValorFace medium differences (1-100): {len(medium_vf):,} ({len(medium_vf)/len(vf_diffs)*100:.1f}%)')
                print(f'  ValorFace large differences (>100): {len(large_vf):,} ({len(large_vf)/len(vf_diffs)*100:.1f}%)')
                
                pattern_analysis.update({
                    'vf_small_differences_count': len(small_vf),
                    'vf_small_differences_percent': len(small_vf)/len(vf_diffs)*100,
                    'vf_medium_differences_count': len(medium_vf),
                    'vf_medium_differences_percent': len(medium_vf)/len(vf_diffs)*100,
                    'vf_large_differences_count': len(large_vf),
                    'vf_large_differences_percent': len(large_vf)/len(vf_diffs)*100
                })
        print()
        
        # Show examples of each type
        print('📋 EXAMPLES OF DIFFERENCES:')
        if len(large_va) > 0:
            print('Large ValorAquisicao differences:')
            large_examples = diff_df[diff_df['ValorAquisicao_Difference'].abs() > 10].head(5)
            for _, row in large_examples.iterrows():
                print(f'  {row["NumeroContrato"][:8]}...: Internal={row["ValorAquisicao_Internal"]:.2f}, Fund={row["ValorAquisicao_Fund"]:.2f}, Diff={row["ValorAquisicao_Difference"]:.2f}')
            print()
            
        if 'ValorFace_Difference' in diff_df.columns:
            vf_diffs = diff_df['ValorFace_Difference'].dropna()
            if len(vf_diffs) > 0:
                large_vf = vf_diffs[abs(vf_diffs) > 100]
                if len(large_vf) > 0:
                    print('Large ValorFace differences:')
                    large_vf_examples = diff_df[diff_df['ValorFace_Difference'].abs() > 100].head(5)
                    for _, row in large_vf_examples.iterrows():
                        if pd.notna(row['ValorFace_Internal']):
                            print(f'  {row["NumeroContrato"][:8]}...: Internal={row["ValorFace_Internal"]:.2f}, Fund={row["ValorFace_Fund"]:.2f}, Diff={row["ValorFace_Difference"]:.2f}')
                    print()
        
        # Show small differences (likely rounding errors)
        print('Small ValorAquisicao differences (likely rounding):')
        small_examples = diff_df[diff_df['ValorAquisicao_Difference'].abs() <= 0.1].head(5)
        for _, row in small_examples.iterrows():
            print(f'  {row["NumeroContrato"][:8]}...: Internal={row["ValorAquisicao_Internal"]:.6f}, Fund={row["ValorAquisicao_Fund"]:.6f}, Diff={row["ValorAquisicao_Difference"]:.6f}')
        print()
    
    # Save analysis if requested
    if save_analysis:
        # Create analysis directory
        analysis_dir = Path("reports/analysis")
        analysis_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed analysis as CSV
        if analysis_results:
            analysis_df = pd.DataFrame(analysis_results)
            analysis_file = analysis_dir / f"difference_analysis_{fund_alias}_{timestamp}.csv"
            analysis_df.to_csv(analysis_file, index=False)
            print(f"📊 Analysis summary saved to: {analysis_file}")
        
        # Save pattern analysis
        if 'pattern_analysis' in locals():
            pattern_df = pd.DataFrame([pattern_analysis])
            pattern_file = analysis_dir / f"pattern_analysis_{fund_alias}_{timestamp}.csv"
            pattern_df.to_csv(pattern_file, index=False)
            print(f"🔍 Pattern analysis saved to: {pattern_file}")
    
    return {
        'analysis_results': analysis_results,
        'pattern_analysis': pattern_analysis if 'pattern_analysis' in locals() else None,
        'total_differences': len(diff_df)
    }


if __name__ == "__main__":
    # Parse command line arguments
    differences_file = sys.argv[1] if len(sys.argv) > 1 else None
    fund_alias = sys.argv[2] if len(sys.argv) > 2 else 'pi'
    
    analyze_differences(differences_file, fund_alias) 