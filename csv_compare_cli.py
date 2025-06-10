#!/usr/bin/env python3
"""
CSV Comparison Tool - Command Line Interface

A comprehensive tool for comparing CSV files with various comparison modes,
output formats, and configuration options.
"""

import click
import os
import sys
import json
from pathlib import Path
from colorama import Fore, Style, init
from tabulate import tabulate

# Initialize colorama for cross-platform colored output
init(autoreset=True)

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.csv_loader import CSVLoader
from src.core.comparator import CSVComparator, ComparisonType
from src.core.bigquery_loader import BigQueryLoader, extract_internal_data
from src.reports.html_reporter import HTMLReporter
from src.reports.json_reporter import JSONReporter


def print_colored(message: str, color: str = Fore.WHITE):
    """Print colored message to console."""
    click.echo(f"{color}{message}{Style.RESET_ALL}")


def print_error(message: str):
    """Print error message in red."""
    print_colored(f"❌ Error: {message}", Fore.RED)


def print_success(message: str):
    """Print success message in green."""
    print_colored(f"✅ {message}", Fore.GREEN)


def print_warning(message: str):
    """Print warning message in yellow."""
    print_colored(f"⚠️  {message}", Fore.YELLOW)


def print_info(message: str):
    """Print info message in blue."""
    print_colored(f"ℹ️  {message}", Fore.BLUE)


@click.group()
@click.version_option(version='1.0.0', prog_name='CSV Compare Tool')
def cli():
    """
    CSV Comparison Tool - Compare two CSV files and generate detailed reports.
    
    This tool can perform different types of comparisons:
    - Full: Complete row-by-row and schema comparison
    - Schema: Compare only column names and data types
    - Statistical: Compare statistical properties
    - Subset: Check if one file is a subset of another
    """
    pass


@cli.command()
@click.argument('file1', type=click.Path(exists=True))
@click.argument('file2', type=click.Path(exists=True))
@click.option('--type', 'comparison_type', 
              type=click.Choice(['full', 'schema', 'statistical', 'subset']),
              default='full',
              help='Type of comparison to perform')
@click.option('--output', '-o', 
              type=click.Path(),
              help='Output file path (auto-detects format from extension)')
@click.option('--format', 'output_format',
              type=click.Choice(['html', 'json', 'console']),
              default='console',
              help='Output format')
@click.option('--config', '-c',
              type=click.Path(exists=True),
              help='Configuration file (JSON)')
@click.option('--ignore-case', is_flag=True,
              help='Ignore case differences in text')
@click.option('--ignore-whitespace', is_flag=True, default=True,
              help='Ignore leading/trailing whitespace')
@click.option('--tolerance', type=float, default=1e-10,
              help='Tolerance for floating point comparisons')
@click.option('--ignore-columns', 
              help='Comma-separated list of columns to ignore')
@click.option('--encoding1', 
              help='Encoding for first file (auto-detected if not specified)')
@click.option('--encoding2',
              help='Encoding for second file (auto-detected if not specified)')
@click.option('--delimiter1',
              help='Delimiter for first file (auto-detected if not specified)')
@click.option('--delimiter2',
              help='Delimiter for second file (auto-detected if not specified)')
@click.option('--no-charts', is_flag=True,
              help='Disable chart generation in HTML reports')
@click.option('--title',
              help='Custom title for the report')
@click.option('--verbose', '-v', is_flag=True,
              help='Verbose output')
def compare(file1, file2, comparison_type, output, output_format, config,
           ignore_case, ignore_whitespace, tolerance, ignore_columns,
           encoding1, encoding2, delimiter1, delimiter2, no_charts, title, verbose):
    """
    Compare two CSV files and generate a comparison report.
    
    FILE1: Path to the first CSV file
    FILE2: Path to the second CSV file
    
    Examples:
    \b
        # Basic comparison with console output
        csv-compare compare file1.csv file2.csv
        
        # Full comparison with HTML report
        csv-compare compare file1.csv file2.csv --format html --output report.html
        
        # Schema comparison only
        csv-compare compare file1.csv file2.csv --type schema
        
        # Ignore specific columns and case differences
        csv-compare compare file1.csv file2.csv --ignore-columns "id,timestamp" --ignore-case
    """
    try:
        print_info(f"Starting {comparison_type} comparison...")
        print_info(f"File 1: {file1}")
        print_info(f"File 2: {file2}")
        
        # Load configuration
        config_dict = {}
        if config:
            with open(config, 'r') as f:
                config_dict = json.load(f)
        
        # Override config with command line options
        if ignore_case:
            config_dict['ignore_case'] = True
        if ignore_whitespace:
            config_dict['ignore_whitespace'] = True
        if tolerance:
            config_dict['float_tolerance'] = tolerance
        if ignore_columns:
            config_dict['ignore_columns'] = [col.strip() for col in ignore_columns.split(',')]
        
        # Initialize components
        loader = CSVLoader()
        comparator = CSVComparator(config_dict)
        
        # Load CSV files
        print_info("Loading first CSV file...")
        loader_kwargs1 = {}
        if encoding1:
            loader_kwargs1['encoding'] = encoding1
        if delimiter1:
            loader_kwargs1['sep'] = delimiter1
            
        df1, metadata1 = loader.load_csv(file1, **loader_kwargs1)
        
        print_info("Loading second CSV file...")
        loader_kwargs2 = {}
        if encoding2:
            loader_kwargs2['encoding'] = encoding2
        if delimiter2:
            loader_kwargs2['sep'] = delimiter2
            
        df2, metadata2 = loader.load_csv(file2, **loader_kwargs2)
        
        if verbose:
            print_info(f"File 1: {metadata1['shape'][0]} rows, {metadata1['shape'][1]} columns")
            print_info(f"File 2: {metadata2['shape'][0]} rows, {metadata2['shape'][1]} columns")
        
        # Validate CSV structures
        issues1 = loader.validate_csv_structure(df1, metadata1)
        issues2 = loader.validate_csv_structure(df2, metadata2)
        
        if issues1:
            print_warning(f"Issues in file 1: {'; '.join(issues1)}")
        if issues2:
            print_warning(f"Issues in file 2: {'; '.join(issues2)}")
        
        # Perform comparison
        print_info("Performing comparison...")
        # Find the ComparisonType by value
        comp_type = None
        for ct in ComparisonType:
            if ct.value == comparison_type:
                comp_type = ct
                break
        
        if comp_type is None:
            raise ValueError(f"Invalid comparison type: {comparison_type}")
            
        result = comparator.compare_dataframes(df1, df2, comp_type, metadata1, metadata2)
        
        # Generate output
        if output_format == 'console' or (not output and output_format == 'console'):
            _print_console_report(result, verbose)
        else:
            # Determine output format and path
            if output:
                if output.endswith('.html'):
                    output_format = 'html'
                elif output.endswith('.json'):
                    output_format = 'json'
            else:
                # Generate default filename
                base_name = f"comparison_{comparison_type}_{Path(file1).stem}_vs_{Path(file2).stem}"
                output = f"{base_name}.{output_format}"
            
            # Generate report
            if output_format == 'html':
                reporter = HTMLReporter()
                output_path = reporter.generate_report(
                    result, output, title=title, include_charts=not no_charts
                )
                print_success(f"HTML report generated: {output_path}")
            elif output_format == 'json':
                reporter = JSONReporter()
                output_path = reporter.generate_report(result, output)
                print_success(f"JSON report generated: {output_path}")
        
        # Print summary to console regardless of output format
        _print_summary(result)
        
    except Exception as e:
        print_error(f"Comparison failed: {str(e)}")
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def _print_console_report(result, verbose=False):
    """Print detailed comparison results to console."""
    print("\n" + "="*80)
    print_colored(f"CSV COMPARISON REPORT - {result.comparison_type.value.upper()}", Fore.CYAN)
    print("="*80)
    
    # Summary section
    print_colored("\n📊 SUMMARY", Fore.YELLOW)
    print("-" * 40)
    
    summary_table = []
    for key, value in result.summary.items():
        display_key = key.replace('_', ' ').title()
        if isinstance(value, bool):
            display_value = f"{Fore.GREEN}✓ YES{Style.RESET_ALL}" if value else f"{Fore.RED}✗ NO{Style.RESET_ALL}"
        else:
            display_value = str(value)
        summary_table.append([display_key, display_value])
    
    print(tabulate(summary_table, headers=['Metric', 'Value'], tablefmt='grid'))
    
    # Differences section
    if result.differences:
        print_colored("\n🔍 DIFFERENCES", Fore.YELLOW)
        print("-" * 40)
        
        # Missing columns
        if result.differences.get('missing_in_df1') or result.differences.get('missing_in_df2'):
            print_colored("\nMissing Columns:", Fore.RED)
            if result.differences.get('missing_in_df1'):
                print(f"  Missing in File 1: {', '.join(result.differences['missing_in_df1'])}")
            if result.differences.get('missing_in_df2'):
                print(f"  Missing in File 2: {', '.join(result.differences['missing_in_df2'])}")
        
        # Type mismatches
        if result.differences.get('type_mismatches'):
            print_colored("\nData Type Mismatches:", Fore.RED)
            type_table = []
            for col, types in result.differences['type_mismatches'].items():
                type_table.append([col, types['df1'], types['df2']])
            print(tabulate(type_table, headers=['Column', 'File 1 Type', 'File 2 Type'], tablefmt='grid'))
        
        # Row differences (limited display)
        if result.differences.get('different_cells'):
            different_count = len(result.differences['different_cells'])
            print_colored(f"\nData Differences: {different_count} rows with differences", Fore.RED)
            
            if verbose and different_count <= 10:
                print("Sample differences:")
                for row_idx, diffs in list(result.differences['different_cells'].items())[:5]:
                    print(f"  Row {row_idx}:")
                    for col, vals in diffs.items():
                        print(f"    {col}: '{vals['df1']}' → '{vals['df2']}'")
    
    # Statistics section (if available)
    if result.statistics and verbose:
        print_colored("\n📈 STATISTICS", Fore.YELLOW)
        print("-" * 40)
        print("Detailed statistics available in JSON/HTML reports")


def _print_summary(result):
    """Print a concise summary of the comparison."""
    print("\n" + "="*50)
    print_colored("COMPARISON SUMMARY", Fore.CYAN)
    print("="*50)
    
    # Overall result
    if result.comparison_type == ComparisonType.FULL:
        is_identical = result.summary.get('data_identical', False)
        if is_identical:
            print_success("Files are identical!")
        else:
            diff_pct = result.summary.get('difference_percentage', 0)
            print_warning(f"Files differ ({diff_pct:.2f}% different rows)")
    
    elif result.comparison_type == ComparisonType.SCHEMA:
        schema_match = (result.summary.get('columns_match', False) and 
                       result.summary.get('types_match', False))
        if schema_match:
            print_success("Schemas are identical!")
        else:
            print_warning("Schema differences found")
    
    elif result.comparison_type == ComparisonType.SUBSET:
        is_subset = result.summary.get('is_subset', False)
        if is_subset:
            print_success("First file is a subset of the second!")
        else:
            print_warning("First file is NOT a subset of the second")
    
    elif result.comparison_type == ComparisonType.STATISTICAL:
        shape_match = result.summary.get('shape_match', False)
        if shape_match:
            print_success("Files have identical dimensions!")
        else:
            print_warning("Files have different dimensions")


@cli.command()
@click.argument('fund_csv', type=click.Path(exists=True))
@click.option('--reference-date', default='2025-05-30',
              help='Reference date for BigQuery data extraction')
@click.option('--fund', 
              type=click.Choice(['ai', 'pi']),
              help='Fund alias to compare with (ai or pi). If not specified, attempts to detect from filename.')
@click.option('--credentials', 
              type=click.Path(exists=True),
              help='Path to Google Cloud service account JSON file')
@click.option('--export-internal', 
              type=click.Path(),
              help='Export internal data to CSV file (default: reports/data_exports/)')
@click.option('--output', '-o', 
              type=click.Path(),
              help='Output file path for comparison report (default: reports/comparisons/)')
@click.option('--format', 'output_format',
              type=click.Choice(['html', 'json', 'console']),
              default='console',
              help='Output format for the report')
@click.option('--config', 
              type=click.Path(exists=True),
              help='Path to comparison configuration JSON file')
@click.option('--verbose', '-v', is_flag=True,
              help='Enable verbose output')
def compare_with_internal(fund_csv, reference_date, fund, credentials, export_internal, 
                         output, output_format, config, verbose):
    """
    Compare fund CSV report with internal BigQuery data.
    
    FUND_CSV: Path to the fund's CSV report file
    
    Examples:
    \b
        # Compare fund report with internal data (auto-detect fund)
        csv-compare compare-with-internal fund_report.csv
        
        # Specify fund explicitly  
        csv-compare compare-with-internal fund_report.csv --fund pi
        
        # Export internal data to CSV and generate HTML report
        csv-compare compare-with-internal fund_report.csv --export-internal --format html
        
        # Use specific reference date and credentials
        csv-compare compare-with-internal fund_report.csv --reference-date 2025-05-30 --credentials gcp-key.json
    """
    try:
        from datetime import datetime
        from pathlib import Path
        
        # Create timestamp for file naming
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create output directories
        reports_dir = Path("reports")
        comparisons_dir = reports_dir / "comparisons"
        data_exports_dir = reports_dir / "data_exports"
        
        # Ensure directories exist
        comparisons_dir.mkdir(parents=True, exist_ok=True)
        data_exports_dir.mkdir(parents=True, exist_ok=True)
        
        # Auto-detect fund if not specified
        if not fund:
            if '20697244' in fund_csv:
                fund = 'pi'
                if verbose:
                    click.echo(f"ℹ️  Detected fund: PI (20697244)")
            elif '19441218' in fund_csv:
                fund = 'ai'
                if verbose:
                    click.echo(f"ℹ️  Detected fund: AI (19441218)")
            else:
                fund = 'pi'  # default
                if verbose:
                    click.echo(f"⚠️  Could not detect fund from filename, defaulting to PI")
        
        if verbose:
            click.echo(f"ℹ️  Comparing fund report with internal BigQuery data...")
            click.echo(f"ℹ️  Fund report: {fund_csv}")
            click.echo(f"ℹ️  Reference date: {reference_date}")
        
        # Extract internal data
        if verbose:
            click.echo(f"ℹ️  Extracting internal data from BigQuery for fund '{fund}'...")
        
        from src.core.bigquery_loader import extract_internal_data
        
        # Set default export path if requested
        if export_internal is True:
            export_internal = data_exports_dir / f"internal_data_{fund}_{reference_date.replace('-', '')}_{timestamp}.csv"
        elif export_internal and not Path(export_internal).is_absolute():
            export_internal = data_exports_dir / export_internal
            
        internal_df, internal_metadata = extract_internal_data(
            reference_date=reference_date,
            fund_alias=fund,
            output_csv=str(export_internal) if export_internal else None,
            credentials_path=credentials
        )
        
        # Load fund CSV
        if verbose:
            click.echo(f"ℹ️  Loading fund CSV report...")
        
        from src.core.csv_loader import CSVLoader
        loader = CSVLoader()
        fund_df, fund_metadata = loader.load_csv(fund_csv)
        
        # Load configuration
        config_dict = {}
        if config:
            with open(config, 'r') as f:
                config_dict = json.load(f)
        
        # Perform comparison
        if verbose:
            click.echo(f"ℹ️  Performing comparison...")
        
        from src.core.comparator import CSVComparator, ComparisonType
        comparator = CSVComparator(config_dict)
        result = comparator.compare_dataframes(
            internal_df, fund_df, 
            ComparisonType.FULL, 
            internal_metadata, fund_metadata
        )
        
        # Generate output
        if output_format == 'console':
            from src.reporting.console_reporter import ConsoleReporter
            reporter = ConsoleReporter()
            report = reporter.generate_report(result)
            click.echo(report)
            
        elif output_format == 'html':
            # Set default output path
            if not output:
                output = comparisons_dir / f"comparison_{fund}_{reference_date.replace('-', '')}_{timestamp}.html"
            elif not Path(output).is_absolute():
                output = comparisons_dir / output
                
            from src.reporting.html_reporter import HTMLReporter
            reporter = HTMLReporter()
            report = reporter.generate_report(result, str(output))
            if verbose:
                click.echo(f"✅ HTML report generated: {output}")
                
        elif output_format == 'json':
            # Set default output path
            if not output:
                output = comparisons_dir / f"comparison_{fund}_{reference_date.replace('-', '')}_{timestamp}.json"
            elif not Path(output).is_absolute():
                output = comparisons_dir / output
                
            from src.reporting.json_reporter import JSONReporter
            reporter = JSONReporter()
            report = reporter.generate_report(result, str(output))
            if verbose:
                click.echo(f"✅ JSON report generated: {output}")
        
        if verbose:
            summary = result.summary
            click.echo(f"\n📊 Comparison Summary:")
            click.echo(f"   Common records: {summary.get('common_cession_records', 0):,}")
            click.echo(f"   Identical records: {summary.get('identical_records', 0):,}")
            click.echo(f"   Different records: {summary.get('different_records', 0):,}")
            click.echo(f"   Match percentage: {summary.get('match_percentage', 0):.1f}%")
            click.echo(f"   Coverage percentage: {summary.get('coverage_percentage', 0):.1f}%")
        
    except Exception as e:
        if verbose:
            click.echo(f"❌ Error: {str(e)}", err=True)
            import traceback
            click.echo(traceback.format_exc(), err=True)
        else:
            click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('config_path', type=click.Path())
def create_config(config_path):
    """Create a sample configuration file."""
    sample_config = {
        "float_tolerance": 1e-10,
        "ignore_case": False,
        "ignore_whitespace": True,
        "ignore_columns": [],
        "key_columns": [],
        "description": "Sample configuration for CSV comparison"
    }
    
    try:
        with open(config_path, 'w') as f:
            json.dump(sample_config, f, indent=2)
        print_success(f"Configuration file created: {config_path}")
        print_info("Edit the file to customize comparison settings")
    except Exception as e:
        print_error(f"Failed to create configuration file: {e}")
        sys.exit(1)


@cli.command()
@click.argument('csv_file', type=click.Path(exists=True))
def info(csv_file):
    """Display information about a CSV file."""
    try:
        print_info(f"Analyzing CSV file: {csv_file}")
        
        loader = CSVLoader()
        df, metadata = loader.load_csv(csv_file)
        issues = loader.validate_csv_structure(df, metadata)
        
        print(f"\n{'='*60}")
        print_colored(f"CSV FILE INFORMATION", Fore.CYAN)
        print(f"{'='*60}")
        
        # Basic info
        info_table = [
            ['File Path', metadata['file_path']],
            ['File Size', f"{metadata['file_size']:,} bytes"],
            ['Encoding', metadata['encoding']],
            ['Delimiter', repr(metadata['delimiter'])],
            ['Rows', f"{metadata['shape'][0]:,}"],
            ['Columns', f"{metadata['shape'][1]:,}"],
            ['Memory Usage', f"{metadata['memory_usage']:,} bytes"],
            ['Has Header', 'Yes' if metadata['has_header'] else 'No']
        ]
        
        print(tabulate(info_table, headers=['Property', 'Value'], tablefmt='grid'))
        
        # Column information
        print_colored(f"\nCOLUMN INFORMATION", Fore.YELLOW)
        col_table = []
        for col in metadata['columns']:
            dtype = metadata['dtypes'][col]
            null_count = df[col].isnull().sum()
            null_pct = (null_count / len(df)) * 100 if len(df) > 0 else 0
            col_table.append([col, str(dtype), f"{null_count:,}", f"{null_pct:.1f}%"])
        
        print(tabulate(col_table, 
                      headers=['Column', 'Data Type', 'Null Count', 'Null %'], 
                      tablefmt='grid'))
        
        # Issues
        if issues:
            print_colored(f"\nISSUES FOUND", Fore.RED)
            for i, issue in enumerate(issues, 1):
                print(f"{i}. {issue}")
        else:
            print_colored(f"\n✅ No issues found!", Fore.GREEN)
            
    except Exception as e:
        print_error(f"Failed to analyze file: {e}")
        sys.exit(1)


if __name__ == '__main__':
    cli() 