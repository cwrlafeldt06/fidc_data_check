import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum


class ComparisonType(Enum):
    SCHEMA = "schema"
    FULL = "full"
    STATISTICAL = "statistical"
    SUBSET = "subset"


@dataclass
class ComparisonResult:
    """Container for comparison results."""
    comparison_type: ComparisonType
    summary: Dict[str, Any]
    differences: Dict[str, Any]
    statistics: Dict[str, Any]
    metadata: Dict[str, Any]


class CSVComparator:
    """Main class for comparing two CSV datasets."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.float_tolerance = self.config.get('float_tolerance', 1e-10)
        self.ignore_case = self.config.get('ignore_case', False)
        self.ignore_whitespace = self.config.get('ignore_whitespace', True)
        self.ignore_columns = set(self.config.get('ignore_columns', []))
        self.key_columns = self.config.get('key_columns', [])
    
    def compare_dataframes(
        self, 
        df1: pd.DataFrame, 
        df2: pd.DataFrame,
        comparison_type: ComparisonType = ComparisonType.FULL,
        metadata1: Optional[Dict] = None,
        metadata2: Optional[Dict] = None
    ) -> ComparisonResult:
        """
        Compare two dataframes based on the specified comparison type.
        
        Args:
            df1: First dataframe
            df2: Second dataframe
            comparison_type: Type of comparison to perform
            metadata1: Metadata for first dataframe
            metadata2: Metadata for second dataframe
            
        Returns:
            ComparisonResult object with detailed comparison results
        """
        # Pre-process dataframes
        df1_clean = self._preprocess_dataframe(df1.copy())
        df2_clean = self._preprocess_dataframe(df2.copy())
        
        # Initialize result structure
        result = ComparisonResult(
            comparison_type=comparison_type,
            summary={},
            differences={},
            statistics={},
            metadata={
                'df1_metadata': metadata1 or {},
                'df2_metadata': metadata2 or {},
                'comparison_config': self.config
            }
        )
        
        # Perform comparison based on type
        if comparison_type == ComparisonType.SCHEMA:
            self._compare_schema(df1_clean, df2_clean, result)
        elif comparison_type == ComparisonType.STATISTICAL:
            self._compare_statistics(df1_clean, df2_clean, result)
        elif comparison_type == ComparisonType.SUBSET:
            self._compare_subset(df1_clean, df2_clean, result)
        else:  # FULL comparison
            self._compare_full(df1_clean, df2_clean, result)
        
        return result
    
    def _preprocess_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply preprocessing based on configuration."""
        # Remove ignored columns
        if self.ignore_columns:
            df = df.drop(columns=[col for col in self.ignore_columns if col in df.columns])
        
        # Handle whitespace
        if self.ignore_whitespace:
            string_columns = df.select_dtypes(include=['object']).columns
            df[string_columns] = df[string_columns].apply(lambda x: x.str.strip() if x.name in string_columns else x)
        
        # Handle case sensitivity
        if self.ignore_case:
            string_columns = df.select_dtypes(include=['object']).columns
            df[string_columns] = df[string_columns].apply(lambda x: x.str.lower() if x.name in string_columns else x)
        
        return df
    
    def _compare_schema(self, df1: pd.DataFrame, df2: pd.DataFrame, result: ComparisonResult):
        """Compare schema (columns and data types) between dataframes."""
        cols1, cols2 = set(df1.columns), set(df2.columns)
        types1, types2 = df1.dtypes.to_dict(), df2.dtypes.to_dict()
        
        # Column differences
        missing_in_df2 = cols1 - cols2
        missing_in_df1 = cols2 - cols1
        common_columns = cols1 & cols2
        
        # Data type differences
        type_mismatches = {}
        for col in common_columns:
            if types1[col] != types2[col]:
                type_mismatches[col] = {'df1': str(types1[col]), 'df2': str(types2[col])}
        
        result.summary = {
            'columns_match': len(missing_in_df1) == 0 and len(missing_in_df2) == 0,
            'types_match': len(type_mismatches) == 0,
            'total_columns_df1': len(cols1),
            'total_columns_df2': len(cols2),
            'common_columns': len(common_columns)
        }
        
        result.differences = {
            'missing_in_df2': list(missing_in_df2),
            'missing_in_df1': list(missing_in_df1),
            'type_mismatches': type_mismatches
        }
    
    def _compare_statistics(self, df1: pd.DataFrame, df2: pd.DataFrame, result: ComparisonResult):
        """Compare statistical properties of the dataframes."""
        # Basic statistics
        stats1 = df1.describe(include='all').to_dict()
        stats2 = df2.describe(include='all').to_dict()
        
        # Shape comparison
        shape_match = df1.shape == df2.shape
        
        # Null value comparison
        nulls1 = df1.isnull().sum().to_dict()
        nulls2 = df2.isnull().sum().to_dict()
        
        result.summary = {
            'shape_match': shape_match,
            'rows_df1': df1.shape[0],
            'rows_df2': df2.shape[0],
            'columns_df1': df1.shape[1],
            'columns_df2': df2.shape[1]
        }
        
        result.statistics = {
            'df1_stats': stats1,
            'df2_stats': stats2,
            'df1_nulls': nulls1,
            'df2_nulls': nulls2
        }
        
        # Compare numerical columns
        numeric_cols = df1.select_dtypes(include=[np.number]).columns
        numeric_diffs = {}
        
        for col in numeric_cols:
            if col in df2.columns:
                try:
                    mean_diff = abs(df1[col].mean() - df2[col].mean())
                    std_diff = abs(df1[col].std() - df2[col].std())
                    numeric_diffs[col] = {
                        'mean_difference': mean_diff,
                        'std_difference': std_diff,
                        'significant_difference': mean_diff > self.float_tolerance
                    }
                except Exception:
                    numeric_diffs[col] = {'error': 'Could not compare numeric values'}
        
        result.differences = {'numeric_differences': numeric_diffs}
    
    def _compare_subset(self, df1: pd.DataFrame, df2: pd.DataFrame, result: ComparisonResult):
        """Compare if one dataframe is a subset of another."""
        # This is a simplified subset comparison
        common_cols = list(set(df1.columns) & set(df2.columns))
        
        if not common_cols:
            result.summary = {'is_subset': False, 'reason': 'No common columns'}
            return
        
        df1_subset = df1[common_cols].drop_duplicates()
        df2_subset = df2[common_cols].drop_duplicates()
        
        # Check if df1 is subset of df2
        merged = pd.merge(df1_subset, df2_subset, how='inner', on=common_cols)
        is_subset = len(merged) == len(df1_subset)
        
        result.summary = {
            'is_subset': is_subset,
            'common_columns': len(common_cols),
            'unique_rows_df1': len(df1_subset),
            'unique_rows_df2': len(df2_subset),
            'matching_rows': len(merged)
        }
    
    def _compare_full(self, df1: pd.DataFrame, df2: pd.DataFrame, result: ComparisonResult):
        """Perform cession-focused comparison."""
        # Get common columns for data comparison
        common_cols = list(set(df1.columns) & set(df2.columns))
        
        if not common_cols:
            result.summary.update({
                'data_identical': False,
                'reason': 'No common columns for comparison'
            })
            return
        
        # Use key-based comparison (cession matching)
        if self.key_columns and all(col in common_cols for col in self.key_columns):
            self._compare_by_key(df1, df2, result, common_cols)
        else:
            result.summary.update({
                'data_identical': False,
                'reason': 'Key columns (NumeroContrato) required for cession comparison'
            })
    
    def _compare_by_key(self, df1: pd.DataFrame, df2: pd.DataFrame, result: ComparisonResult, common_cols: List[str]):
        """Compare dataframes by matching records using key columns (cession-focused)."""
        # Get key columns that exist in both dataframes
        valid_keys = [col for col in self.key_columns if col in common_cols]
        
        if not valid_keys:
            result.summary.update({
                'data_identical': False,
                'reason': 'Key columns not found in both files'
            })
            return
        
        # Create comparison datasets - only use common columns for comparison
        df1_common = df1[common_cols].copy().reset_index(drop=True)
        df2_common = df2[common_cols].copy().reset_index(drop=True)
        
        print("🔍 Finding matching cession records...")
        
        # Inner join to find common records (cessions that exist in both datasets)
        merged_inner = pd.merge(
            df1_common, df2_common, 
            on=valid_keys, 
            how='inner', 
            suffixes=('_internal', '_fund')
        )
        
        print(f"📊 Found {len(merged_inner)} common cession records to compare")
        
        # Compare values for matching cessions
        different_records = {}
        identical_records = 0
        
        if len(merged_inner) > 0:
            print("⚖️  Comparing cession values...")
            
            # Compare each value column (skip key columns)
            value_columns = [col for col in common_cols if col not in valid_keys]
            
            for col in value_columns:
                col_internal = f"{col}_internal"
                col_fund = f"{col}_fund"
                
                if col_internal in merged_inner.columns and col_fund in merged_inner.columns:
                    # Handle numeric comparisons with tolerance
                    if merged_inner[col_internal].dtype in ['int64', 'float64'] and merged_inner[col_fund].dtype in ['int64', 'float64']:
                        diff_mask = abs(merged_inner[col_internal] - merged_inner[col_fund]) > self.float_tolerance
                    else:
                        # Handle NaN and string comparisons
                        diff_mask = ~(
                            (merged_inner[col_internal].isna() & merged_inner[col_fund].isna()) |
                            (merged_inner[col_internal] == merged_inner[col_fund])
                        )
                    
                    # Store differences
                    if diff_mask.any():
                        diff_rows = merged_inner[diff_mask]
                        for idx, row in diff_rows.iterrows():
                            key_str = "_".join(str(row[k]) for k in valid_keys)
                            if key_str not in different_records:
                                different_records[key_str] = {}
                            different_records[key_str][col] = {
                                'internal': row[col_internal], 
                                'fund': row[col_fund],
                                'difference': row[col_internal] - row[col_fund] if pd.notna(row[col_internal]) and pd.notna(row[col_fund]) else 'N/A'
                            }
            
            # Count identical records
            identical_records = len(merged_inner) - len(different_records)
        
        print(f"✅ Comparison complete: {identical_records} identical, {len(different_records)} different")
        
        # Update result with cession-focused comparison
        result.differences.update({
            'different_records': different_records,
            'total_different_records': len(different_records),
            'comparison_method': 'cession_matching',
            'key_columns_used': valid_keys,
            'value_columns_compared': [col for col in common_cols if col not in valid_keys]
        })
        
        total_internal_records = len(df1_common)
        total_fund_records = len(df2_common)
        common_records = len(merged_inner)
        
        result.summary.update({
            'data_identical': len(different_records) == 0,
            'identical_records': identical_records,
            'total_internal_records': total_internal_records,
            'total_fund_records': total_fund_records,
            'common_cession_records': common_records,
            'different_records': len(different_records),
            'match_percentage': (identical_records / common_records * 100) if common_records > 0 else 0,
            'coverage_percentage': (common_records / total_fund_records * 100) if total_fund_records > 0 else 0
        })
    
    def _compare_by_position(self, df1: pd.DataFrame, df2: pd.DataFrame, result: ComparisonResult, common_cols: List[str]):
        """Compare dataframes by row position (original method)."""
        # Compare data in common columns
        df1_common = df1[common_cols].copy()
        df2_common = df2[common_cols].copy()
        
        # Handle different row counts
        min_rows = min(len(df1_common), len(df2_common))
        if len(df1_common) != len(df2_common):
            result.differences['row_count_mismatch'] = {
                'df1_rows': len(df1_common),
                'df2_rows': len(df2_common),
                'comparing_first': min_rows
            }
        
        # Compare data row by row for the minimum number of rows
        if min_rows > 0:
            df1_subset = df1_common.iloc[:min_rows].reset_index(drop=True)
            df2_subset = df2_common.iloc[:min_rows].reset_index(drop=True)
            
            # Find differences
            different_cells = {}
            identical_rows = 0
            
            for idx in range(min_rows):
                row_diffs = {}
                row_identical = True
                
                for col in common_cols:
                    val1, val2 = df1_subset.iloc[idx][col], df2_subset.iloc[idx][col]
                    
                    # Handle NaN values
                    if pd.isna(val1) and pd.isna(val2):
                        continue
                    elif pd.isna(val1) or pd.isna(val2):
                        row_diffs[col] = {'df1': val1, 'df2': val2}
                        row_identical = False
                    # Handle numeric values with tolerance
                    elif isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                        if abs(val1 - val2) > self.float_tolerance:
                            row_diffs[col] = {'df1': val1, 'df2': val2}
                            row_identical = False
                    # Handle other values
                    elif val1 != val2:
                        row_diffs[col] = {'df1': val1, 'df2': val2}
                        row_identical = False
                
                if row_identical:
                    identical_rows += 1
                elif row_diffs:
                    different_cells[idx] = row_diffs
            
            result.differences.update({
                'different_cells': different_cells,
                'total_different_rows': len(different_cells)
            })
            
            result.summary.update({
                'data_identical': len(different_cells) == 0 and len(df1_common) == len(df2_common),
                'identical_rows': identical_rows,
                'total_rows_compared': min_rows,
                'difference_percentage': (len(different_cells) / min_rows * 100) if min_rows > 0 else 0
            })
        else:
            result.summary.update({
                'data_identical': len(df1_common) == len(df2_common) == 0,
                'identical_rows': 0,
                'total_rows_compared': 0
            }) 