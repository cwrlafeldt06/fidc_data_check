import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
import pandas as pd

from ..core.comparator import ComparisonResult


class JSONReporter:
    """Generate JSON reports for CSV comparison results."""
    
    def __init__(self, indent: int = 2):
        self.indent = indent
    
    def generate_report(
        self, 
        result: ComparisonResult, 
        output_path: str,
        include_metadata: bool = True,
        include_full_differences: bool = False
    ) -> str:
        """
        Generate a JSON report from comparison results.
        
        Args:
            result: ComparisonResult object
            output_path: Path to save the JSON report
            include_metadata: Whether to include file metadata
            include_full_differences: Whether to include all differences (can be large)
            
        Returns:
            Path to the generated JSON file
        """
        # Prepare JSON structure
        report_data = {
            'report_info': {
                'generated_at': datetime.now().isoformat(),
                'comparison_type': result.comparison_type.value,
                'version': '1.0'
            },
            'summary': self._serialize_dict(result.summary),
            'differences': self._prepare_differences(result.differences, include_full_differences),
            'statistics': self._serialize_dict(result.statistics)
        }
        
        # Add metadata if requested
        if include_metadata:
            report_data['metadata'] = self._serialize_dict(result.metadata)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
        
        # Write JSON file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=self.indent, ensure_ascii=False, default=str)
        
        return output_path
    
    def generate_summary_json(self, result: ComparisonResult) -> str:
        """Generate a concise JSON summary (as string) of the comparison."""
        summary_data = {
            'comparison_type': result.comparison_type.value,
            'timestamp': datetime.now().isoformat(),
            'summary': self._serialize_dict(result.summary),
            'key_differences': self._extract_key_differences(result.differences)
        }
        
        return json.dumps(summary_data, indent=self.indent, ensure_ascii=False, default=str)
    
    def _serialize_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Serialize dictionary to JSON-compatible format."""
        if not isinstance(data, dict):
            return data
        
        serialized = {}
        for key, value in data.items():
            if isinstance(value, dict):
                serialized[key] = self._serialize_dict(value)
            elif isinstance(value, (list, tuple)):
                serialized[key] = [
                    self._serialize_dict(item) if isinstance(item, dict) else self._serialize_value(item)
                    for item in value
                ]
            else:
                serialized[key] = self._serialize_value(value)
        
        return serialized
    
    def _serialize_value(self, value: Any) -> Any:
        """Serialize individual values to JSON-compatible types."""
        if isinstance(value, (str, int, float, bool, type(None))):
            return value
        elif isinstance(value, pd.Timestamp):
            return value.isoformat()
        elif hasattr(value, 'dtype'):  # pandas/numpy types
            if pd.isna(value):
                return None
            return value.item() if hasattr(value, 'item') else str(value)
        else:
            return str(value)
    
    def _prepare_differences(self, differences: Dict[str, Any], include_full: bool) -> Dict[str, Any]:
        """Prepare differences data, optionally truncating large datasets."""
        if not differences:
            return {}
        
        prepared = {}
        
        for key, value in differences.items():
            if key == 'different_cells' and not include_full:
                # Limit to first 100 differences for readability
                if isinstance(value, dict):
                    limited_cells = dict(list(value.items())[:100])
                    if len(value) > 100:
                        limited_cells['_truncated'] = f'Showing first 100 of {len(value)} differences'
                    prepared[key] = limited_cells
                else:
                    prepared[key] = value
            else:
                prepared[key] = self._serialize_dict(value) if isinstance(value, dict) else value
        
        return prepared
    
    def _extract_key_differences(self, differences: Dict[str, Any]) -> Dict[str, Any]:
        """Extract the most important differences for summary."""
        key_diffs = {}
        
        # Schema differences
        if 'missing_in_df1' in differences and differences['missing_in_df1']:
            key_diffs['missing_columns_file1'] = len(differences['missing_in_df1'])
        
        if 'missing_in_df2' in differences and differences['missing_in_df2']:
            key_diffs['missing_columns_file2'] = len(differences['missing_in_df2'])
        
        if 'type_mismatches' in differences and differences['type_mismatches']:
            key_diffs['type_mismatches'] = len(differences['type_mismatches'])
        
        # Data differences
        if 'total_different_rows' in differences:
            key_diffs['different_rows'] = differences['total_different_rows']
        
        if 'row_count_mismatch' in differences:
            key_diffs['row_count_mismatch'] = True
        
        # Statistical differences
        if 'numeric_differences' in differences:
            numeric_diffs = differences['numeric_differences']
            if isinstance(numeric_diffs, dict):
                significant_diffs = sum(
                    1 for diff in numeric_diffs.values()
                    if isinstance(diff, dict) and diff.get('significant_difference', False)
                )
                if significant_diffs > 0:
                    key_diffs['significant_numeric_differences'] = significant_diffs
        
        return key_diffs
    
    def export_differences_csv(self, result: ComparisonResult, output_path: str) -> Optional[str]:
        """
        Export row-level differences to a CSV file.
        
        Args:
            result: ComparisonResult object
            output_path: Path to save the CSV file
            
        Returns:
            Path to the generated CSV file or None if no differences
        """
        if 'different_cells' not in result.differences or not result.differences['different_cells']:
            return None
        
        different_cells = result.differences['different_cells']
        
        # Prepare data for CSV
        rows = []
        for row_idx, cell_diffs in different_cells.items():
            for column, values in cell_diffs.items():
                rows.append({
                    'row_index': row_idx,
                    'column': column,
                    'file1_value': values.get('df1', ''),
                    'file2_value': values.get('df2', ''),
                    'difference_type': self._classify_difference(values.get('df1'), values.get('df2'))
                })
        
        if rows:
            df = pd.DataFrame(rows)
            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
            df.to_csv(output_path, index=False)
            return output_path
        
        return None
    
    def _classify_difference(self, val1: Any, val2: Any) -> str:
        """Classify the type of difference between two values."""
        if pd.isna(val1) and not pd.isna(val2):
            return 'missing_in_file1'
        elif not pd.isna(val1) and pd.isna(val2):
            return 'missing_in_file2'
        elif pd.isna(val1) and pd.isna(val2):
            return 'both_null'
        elif isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
            return 'numeric_difference'
        elif isinstance(val1, str) and isinstance(val2, str):
            return 'text_difference'
        else:
            return 'type_difference' 