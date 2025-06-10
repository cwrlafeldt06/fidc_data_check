import unittest
import pandas as pd
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.comparator import CSVComparator, ComparisonType


class TestCSVComparator(unittest.TestCase):
    
    def setUp(self):
        """Set up test data."""
        self.comparator = CSVComparator()
        
       
    
    def test_identical_dataframes(self):
        """Test comparison of identical dataframes."""
        result = self.comparator.compare_dataframes(self.df1, self.df2, ComparisonType.FULL)
        
        self.assertTrue(result.summary['data_identical'])
        self.assertEqual(result.summary['identical_rows'], 3)
        self.assertEqual(result.summary['difference_percentage'], 0.0)
    
    def test_different_dataframes(self):
        """Test comparison of different dataframes."""
        result = self.comparator.compare_dataframes(self.df1, self.df3, ComparisonType.FULL)
        
        self.assertFalse(result.summary['data_identical'])
        self.assertEqual(result.summary['total_different_rows'], 2)
        self.assertGreater(result.summary['difference_percentage'], 0)
    
    def test_schema_comparison(self):
        """Test schema comparison."""
        result = self.comparator.compare_dataframes(self.df1, self.df2, ComparisonType.SCHEMA)
        
        self.assertTrue(result.summary['columns_match'])
        self.assertTrue(result.summary['types_match'])
        self.assertEqual(len(result.differences['missing_in_df1']), 0)
        self.assertEqual(len(result.differences['missing_in_df2']), 0)


if __name__ == '__main__':
    unittest.main() 