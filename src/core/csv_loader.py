import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, List, Tuple
import chardet
import os
from pathlib import Path


class CSVLoader:
    """Handles loading and validation of CSV files with auto-detection of encoding and delimiters."""
    
    def __init__(self):
        self.supported_encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        self.supported_delimiters = [',', ';', '\t', '|']
    
    def detect_encoding(self, file_path: str) -> str:
        """Detect file encoding using chardet with fallback options."""
        try:
            with open(file_path, 'rb') as file:
                # Read larger sample for better detection
                raw_data = file.read(100000)  # Read first 100KB
                result = chardet.detect(raw_data)
                detected_encoding = result['encoding']
                confidence = result.get('confidence', 0)
                
                # If confidence is low or encoding is ASCII, try UTF-8 first
                if confidence < 0.7 or detected_encoding == 'ascii':
                    # Try UTF-8 first as it's most common
                    try:
                        with open(file_path, 'r', encoding='utf-8') as test_file:
                            test_file.read(1000)
                        return 'utf-8'
                    except UnicodeDecodeError:
                        pass
                    
                    # Then try latin-1 as it accepts any byte sequence
                    try:
                        with open(file_path, 'r', encoding='latin-1') as test_file:
                            test_file.read(1000)
                        return 'latin-1'
                    except UnicodeDecodeError:
                        pass
                
                return detected_encoding or 'utf-8'
        except Exception:
            return 'utf-8'
    
    def detect_delimiter(self, file_path: str, encoding: str) -> str:
        """Detect delimiter by testing common delimiters."""
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                first_line = file.readline()
                
            delimiter_counts = {}
            for delimiter in self.supported_delimiters:
                delimiter_counts[delimiter] = first_line.count(delimiter)
            
            # Return delimiter with highest count
            return max(delimiter_counts, key=delimiter_counts.get)
        except Exception:
            return ','
    
    def load_csv(self, file_path: str, **kwargs) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Load CSV file with auto-detection of encoding and delimiter.
        
        Args:
            file_path: Path to CSV file
            **kwargs: Additional pandas read_csv parameters
            
        Returns:
            Tuple of (DataFrame, metadata dict)
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Auto-detect encoding and delimiter if not provided
        encoding = kwargs.get('encoding', self.detect_encoding(file_path))
        
        # Try multiple encodings if the detected one fails
        encodings_to_try = [encoding] + [enc for enc in self.supported_encodings if enc != encoding]
        
        last_error = None
        for enc in encodings_to_try:
            try:
                delimiter = kwargs.get('sep', self.detect_delimiter(file_path, enc))
                
                # Set default parameters
                params = {
                    'encoding': enc,
                    'sep': delimiter,
                    'low_memory': False,
                    **kwargs
                }
                
                df = pd.read_csv(file_path, **params)
                
                # Generate metadata
                metadata = {
                    'file_path': file_path,
                    'encoding': enc,
                    'delimiter': delimiter,
                    'shape': df.shape,
                    'columns': list(df.columns),
                    'dtypes': df.dtypes.to_dict(),
                    'memory_usage': df.memory_usage(deep=True).sum(),
                    'file_size': os.path.getsize(file_path),
                    'has_header': True if not df.columns.str.contains('Unnamed').any() else False
                }
                
                return df, metadata
                
            except Exception as e:
                last_error = e
                continue
        
        # If all encodings failed, raise the last error
        raise ValueError(f"Failed to load CSV file {file_path}: {str(last_error)}")
    
    def validate_csv_structure(self, df: pd.DataFrame, metadata: Dict[str, Any]) -> List[str]:
        """Validate CSV structure and return list of issues."""
        issues = []
        
        # Check for empty dataframe
        if df.empty:
            issues.append("CSV file is empty")
        
        # Check for unnamed columns
        unnamed_cols = [col for col in df.columns if 'Unnamed' in str(col)]
        if unnamed_cols:
            issues.append(f"Found unnamed columns: {unnamed_cols}")
        
        # Check for duplicate columns
        duplicate_cols = df.columns[df.columns.duplicated()].tolist()
        if duplicate_cols:
            issues.append(f"Found duplicate column names: {duplicate_cols}")
        
        # Check for excessive missing data
        missing_pct = (df.isnull().sum() / len(df) * 100)
        high_missing = missing_pct[missing_pct > 50].index.tolist()
        if high_missing:
            issues.append(f"Columns with >50% missing data: {high_missing}")
        
        return issues 