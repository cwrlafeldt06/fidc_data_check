import pandas as pd
import os
from typing import Dict, Any, Tuple, Optional
from pathlib import Path


class BigQueryLoader:
    """Handles loading data from BigQuery for comparison with CSV files."""
    
    def __init__(self, credentials_path: Optional[str] = None, project_id: str = "infinitepay-production"):
        """
        Initialize BigQuery loader.
        
        Args:
            credentials_path: Path to service account JSON file (optional)
            project_id: Google Cloud project ID (defaults to infinitepay-production)
        """
        self.credentials_path = credentials_path
        self.project_id = project_id
        self.client = None
        
    def _initialize_client(self):
        """Initialize BigQuery client with authentication."""
        try:
            from google.cloud import bigquery
            from google.oauth2 import service_account
            
            if self.credentials_path and os.path.exists(self.credentials_path):
                # Use service account credentials
                credentials = service_account.Credentials.from_service_account_file(
                    self.credentials_path
                )
                self.client = bigquery.Client(credentials=credentials, project=self.project_id)
            else:
                # Use default credentials (ADC) with explicit project
                self.client = bigquery.Client(project=self.project_id)
                
        except ImportError:
            raise ImportError(
                "google-cloud-bigquery is required. Install with: pip install google-cloud-bigquery"
            )
    
    def load_from_query_file(self, query_file_path: str, **params) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Load data from BigQuery using a SQL file.
        
        Args:
            query_file_path: Path to SQL file containing the query
            **params: Parameters to substitute in the query
            
        Returns:
            Tuple of (DataFrame, metadata dict)
        """
        if not os.path.exists(query_file_path):
            raise FileNotFoundError(f"Query file not found: {query_file_path}")
        
        # Read SQL query from file
        with open(query_file_path, 'r', encoding='utf-8') as f:
            query = f.read()
        
        # Substitute parameters if provided
        if params:
            query = query.format(**params)
        
        return self.load_from_query(query)
    
    def load_from_query(self, query: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Load data from BigQuery using a SQL query.
        
        Args:
            query: SQL query string
            
        Returns:
            Tuple of (DataFrame, metadata dict)
        """
        if self.client is None:
            self._initialize_client()
        
        try:
            # Execute query and convert to DataFrame
            print("Executing BigQuery query...")
            query_job = self.client.query(query)
            df = query_job.to_dataframe()
            
            # Generate metadata
            metadata = {
                'source': 'BigQuery',
                'query': query,
                'shape': df.shape,
                'columns': list(df.columns),
                'dtypes': df.dtypes.to_dict(),
                'memory_usage': df.memory_usage(deep=True).sum(),
                'job_id': query_job.job_id,
                'bytes_processed': query_job.total_bytes_processed,
                'bytes_billed': query_job.total_bytes_billed,
                'has_header': True
            }
            
            print(f"Query completed. Loaded {df.shape[0]:,} rows and {df.shape[1]} columns")
            print(f"Bytes processed: {metadata['bytes_processed']:,}")
            
            return df, metadata
            
        except Exception as e:
            raise ValueError(f"Failed to execute BigQuery query: {str(e)}")
    
    def save_to_csv(self, df: pd.DataFrame, output_path: str) -> str:
        """
        Save DataFrame to CSV file.
        
        Args:
            df: DataFrame to save
            output_path: Path to save CSV file
            
        Returns:
            Path to saved file
        """
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
        df.to_csv(output_path, index=False)
        return output_path


def extract_internal_data(
    reference_date: str = '2025-05-30',
    fund_alias: str = 'pi',
    output_csv: Optional[str] = None,
    credentials_path: Optional[str] = None,
    project_id: str = "infinitepay-production"
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Convenience function to extract internal cession orders data.
    
    Args:
        reference_date: Reference date for filtering data
        fund_alias: Fund alias ('ai' or 'pi') to filter data
        output_csv: Optional path to save CSV file
        credentials_path: Optional path to service account credentials
        project_id: Google Cloud project ID (defaults to infinitepay-production)
        
    Returns:
        Tuple of (DataFrame, metadata dict)
    """
    loader = BigQueryLoader(credentials_path, project_id)
    
    # Use the SQL query file
    query_file = Path(__file__).parent.parent.parent / 'sql' / 'extract_cession_orders.sql'
    
    # Load data with parameters
    df, metadata = loader.load_from_query_file(
        str(query_file),
        reference_date=reference_date,
        fund_alias=fund_alias
    )
    
    # Save to CSV if requested
    if output_csv:
        saved_path = loader.save_to_csv(df, output_csv)
        metadata['csv_export'] = saved_path
        print(f"Data exported to: {saved_path}")
    
    return df, metadata 