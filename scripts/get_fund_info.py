#!/usr/bin/env python3
"""
Get fund information by user ID.
"""

import sys
import json
import os
from pathlib import Path

# Add project root and src to path for imports
project_root = os.path.join(os.path.dirname(__file__), '..')
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, project_root)
sys.path.insert(0, src_path)

from core.bigquery_loader import get_fund_info


def main():
    """Get fund information by user ID and return as JSON."""
    
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "Fund user ID is required",
            "usage": "python get_fund_info.py <fund_user_id>"
        }))
        sys.exit(1)
    
    fund_user_id = sys.argv[1].strip()
    
    try:
        # Get fund information
        fund_info_df, metadata = get_fund_info(fund_user_id)
        
        if len(fund_info_df) == 0:
            print(json.dumps({
                "error": "Fund not found",
                "fund_user_id": fund_user_id
            }))
            sys.exit(1)
        
        # Convert to dictionary
        fund_info = fund_info_df.iloc[0].to_dict()
        
        # Convert any numpy/pandas types to Python native types
        result = {}
        for key, value in fund_info.items():
            if hasattr(value, 'item'):  # numpy scalar
                result[key] = value.item()
            elif value is None or (hasattr(value, 'isna') and value.isna()):
                result[key] = None
            else:
                result[key] = str(value) if value else None
        
        # Add metadata
        result['metadata'] = {
            'query_executed': True,
            'bytes_processed': metadata.get('bytes_processed', 0),
            'rows_returned': len(fund_info_df)
        }
        
        print(json.dumps(result))
        
    except Exception as e:
        print(json.dumps({
            "error": str(e),
            "fund_user_id": fund_user_id
        }))
        sys.exit(1)


if __name__ == "__main__":
    main() 