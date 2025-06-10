from jinja2 import Template
import json
import os
from datetime import datetime
import pandas as pd
from typing import Dict, Any, Optional
import matplotlib.pyplot as plt
import seaborn as sns
import base64
from io import BytesIO

from ..core.comparator import ComparisonResult, ComparisonType


class HTMLReporter:
    """Generate HTML reports for CSV comparison results."""
    
    def __init__(self):
        self.template = self._get_html_template()
        
    def generate_report(
        self, 
        result: ComparisonResult, 
        output_path: str,
        title: Optional[str] = None,
        include_charts: bool = True
    ) -> str:
        """
        Generate an HTML report from comparison results.
        
        Args:
            result: ComparisonResult object
            output_path: Path to save the HTML report
            title: Custom title for the report
            include_charts: Whether to include visualization charts
            
        Returns:
            Path to the generated HTML file
        """
        # Prepare template data
        template_data = {
            'title': title or f'CSV Comparison Report - {result.comparison_type.value.title()}',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'comparison_type': result.comparison_type.value,
            'summary': self._serialize_for_template(result.summary),
            'differences': self._serialize_for_template(result.differences),
            'statistics': self._serialize_for_template(result.statistics),
            'metadata': self._serialize_for_template(result.metadata),
            'charts': {}
        }
        
        # Generate charts if requested
        if include_charts:
            template_data['charts'] = self._generate_charts(result)
        
        # Render template
        html_content = self.template.render(**template_data)
        
        # Write to file
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path
    
    def _serialize_for_template(self, data):
        """Serialize data for Jinja2 template, handling pandas types."""
        if isinstance(data, dict):
            return {k: self._serialize_for_template(v) for k, v in data.items()}
        elif isinstance(data, (list, tuple)):
            return [self._serialize_for_template(item) for item in data]
        elif hasattr(data, 'dtype'):  # pandas/numpy types
            if pd.isna(data):
                return None
            return data.item() if hasattr(data, 'item') else str(data)
        elif str(type(data)).startswith('<class \'pandas'):
            # Handle all pandas types by converting to string
            return str(data)
        elif hasattr(data, '__dict__') and hasattr(data, '__module__'):
            # Handle complex objects by converting to string
            return str(data)
        else:
            try:
                # Test if it's JSON serializable
                json.dumps(data)
                return data
            except (TypeError, ValueError):
                return str(data)
    
    def _generate_charts(self, result: ComparisonResult) -> Dict[str, str]:
        """Generate base64-encoded chart images."""
        charts = {}
        
        try:
            # Set style
            plt.style.use('seaborn-v0_8')
            
            # Chart 1: Summary statistics
            if result.summary:
                charts['summary'] = self._create_summary_chart(result.summary)
            
            # Chart 2: Column comparison (for schema comparisons)
            if result.comparison_type == ComparisonType.SCHEMA and result.differences:
                charts['schema'] = self._create_schema_chart(result.differences)
            
            # Chart 3: Statistical differences
            if result.statistics and 'numeric_differences' in result.differences:
                charts['statistics'] = self._create_statistics_chart(result.differences['numeric_differences'])
                
        except Exception as e:
            print(f"Warning: Could not generate charts: {e}")
        
        return charts
    
    def _create_summary_chart(self, summary: Dict[str, Any]) -> str:
        """Create a summary statistics chart."""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Extract numeric values for plotting
        numeric_data = {}
        for key, value in summary.items():
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                numeric_data[key] = value
        
        if numeric_data:
            keys = list(numeric_data.keys())
            values = list(numeric_data.values())
            
            bars = ax.bar(keys, values, alpha=0.7, color='steelblue')
            ax.set_title('Summary Metrics', fontsize=14, fontweight='bold')
            ax.set_ylabel('Count/Value')
            
            # Add value labels on bars
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                       f'{value:,.0f}', ha='center', va='bottom')
            
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
        
        return self._fig_to_base64(fig)
    
    def _create_schema_chart(self, differences: Dict[str, Any]) -> str:
        """Create schema comparison chart."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
        
        # Missing columns chart
        missing_df1 = differences.get('missing_in_df1', [])
        missing_df2 = differences.get('missing_in_df2', [])
        
        categories = ['Missing in DF1', 'Missing in DF2']
        counts = [len(missing_df1), len(missing_df2)]
        
        ax1.bar(categories, counts, color=['lightcoral', 'lightblue'])
        ax1.set_title('Missing Columns')
        ax1.set_ylabel('Number of Columns')
        
        # Add count labels
        for i, count in enumerate(counts):
            ax1.text(i, count + 0.1, str(count), ha='center', va='bottom')
        
        # Type mismatches
        type_mismatches = differences.get('type_mismatches', {})
        if type_mismatches:
            ax2.bar(['Type Mismatches'], [len(type_mismatches)], color='orange')
            ax2.set_title('Data Type Mismatches')
            ax2.set_ylabel('Number of Columns')
            ax2.text(0, len(type_mismatches) + 0.1, str(len(type_mismatches)), 
                    ha='center', va='bottom')
        else:
            ax2.text(0.5, 0.5, 'No Type\nMismatches', ha='center', va='center',
                    transform=ax2.transAxes, fontsize=12)
            ax2.set_xlim(0, 1)
            ax2.set_ylim(0, 1)
        
        plt.tight_layout()
        return self._fig_to_base64(fig)
    
    def _create_statistics_chart(self, numeric_diffs: Dict[str, Any]) -> str:
        """Create statistical differences chart."""
        if not numeric_diffs:
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.text(0.5, 0.5, 'No Numeric Differences', ha='center', va='center',
                   transform=ax.transAxes, fontsize=14)
            return self._fig_to_base64(fig)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        columns = []
        mean_diffs = []
        std_diffs = []
        
        for col, stats in numeric_diffs.items():
            if 'mean_difference' in stats and 'std_difference' in stats:
                columns.append(col)
                mean_diffs.append(stats['mean_difference'])
                std_diffs.append(stats['std_difference'])
        
        if columns:
            x = range(len(columns))
            width = 0.35
            
            ax.bar([i - width/2 for i in x], mean_diffs, width, 
                  label='Mean Difference', alpha=0.7)
            ax.bar([i + width/2 for i in x], std_diffs, width, 
                  label='Std Difference', alpha=0.7)
            
            ax.set_xlabel('Columns')
            ax.set_ylabel('Difference Value')
            ax.set_title('Numeric Column Differences')
            ax.set_xticks(x)
            ax.set_xticklabels(columns, rotation=45, ha='right')
            ax.legend()
            
            plt.tight_layout()
        
        return self._fig_to_base64(fig)
    
    def _fig_to_base64(self, fig) -> str:
        """Convert matplotlib figure to base64 string."""
        buffer = BytesIO()
        fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close(fig)
        return f"data:image/png;base64,{image_base64}"
    
    def _get_html_template(self) -> Template:
        """Return the HTML template for the report."""
        template_str = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #e0e0e0;
        }
        .header h1 {
            color: #2c3e50;
            margin: 0;
        }
        .timestamp {
            color: #7f8c8d;
            font-size: 14px;
            margin-top: 5px;
        }
        .section {
            margin: 30px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #3498db;
        }
        .section h2 {
            color: #2c3e50;
            margin-top: 0;
            margin-bottom: 15px;
        }
        .section h3 {
            color: #34495e;
            margin-top: 20px;
            margin-bottom: 10px;
        }
        .metric-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 15px 0;
        }
        .metric {
            background: white;
            padding: 15px;
            border-radius: 6px;
            border: 1px solid #e0e0e0;
            text-align: center;
        }
        .metric-value {
            font-size: 24px;
            font-weight: bold;
            color: #3498db;
        }
        .metric-label {
            font-size: 12px;
            color: #7f8c8d;
            text-transform: uppercase;
            margin-top: 5px;
        }
        .chart-container {
            text-align: center;
            margin: 20px 0;
        }
        .chart-container img {
            max-width: 100%;
            height: auto;
            border-radius: 6px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        }
        .differences-table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }
        .differences-table th,
        .differences-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }
        .differences-table th {
            background-color: #3498db;
            color: white;
            font-weight: 500;
        }
        .differences-table tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        .status-badge {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
        }
        .status-success {
            background-color: #d4edda;
            color: #155724;
        }
        .status-warning {
            background-color: #fff3cd;
            color: #856404;
        }
        .status-error {
            background-color: #f8d7da;
            color: #721c24;
        }
        .json-display {
            background: #2c3e50;
            color: #ecf0f1;
            padding: 15px;
            border-radius: 6px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            overflow-x: auto;
            white-space: pre-wrap;
        }
        .list-item {
            padding: 8px 12px;
            margin: 5px 0;
            background: white;
            border-radius: 4px;
            border-left: 3px solid #e74c3c;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{{ title }}</h1>
            <div class="timestamp">Generated on {{ timestamp }}</div>
        </div>

        <!-- Summary Section -->
        <div class="section">
            <h2>📊 Summary</h2>
            <div class="metric-grid">
                {% for key, value in summary.items() %}
                    <div class="metric">
                        <div class="metric-value">
                            {% if value is sameas true %}
                                <span class="status-badge status-success">✓ YES</span>
                            {% elif value is sameas false %}
                                <span class="status-badge status-error">✗ NO</span>
                            {% else %}
                                {{ value }}
                            {% endif %}
                        </div>
                        <div class="metric-label">{{ key.replace('_', ' ').title() }}</div>
                    </div>
                {% endfor %}
            </div>
            
            {% if charts.summary %}
            <div class="chart-container">
                <img src="{{ charts.summary }}" alt="Summary Chart">
            </div>
            {% endif %}
        </div>

        <!-- Differences Section -->
        {% if differences %}
        <div class="section">
            <h2>🔍 Differences</h2>
            
            {% if differences.missing_in_df1 or differences.missing_in_df2 %}
            <h3>Missing Columns</h3>
            {% if differences.missing_in_df1 %}
            <h4>Missing in First File:</h4>
            {% for col in differences.missing_in_df1 %}
                <div class="list-item">{{ col }}</div>
            {% endfor %}
            {% endif %}
            
            {% if differences.missing_in_df2 %}
            <h4>Missing in Second File:</h4>
            {% for col in differences.missing_in_df2 %}
                <div class="list-item">{{ col }}</div>
            {% endfor %}
            {% endif %}
            {% endif %}
            
            {% if differences.type_mismatches %}
            <h3>Data Type Mismatches</h3>
            <table class="differences-table">
                <thead>
                    <tr>
                        <th>Column</th>
                        <th>First File Type</th>
                        <th>Second File Type</th>
                    </tr>
                </thead>
                <tbody>
                    {% for col, types in differences.type_mismatches.items() %}
                    <tr>
                        <td>{{ col }}</td>
                        <td>{{ types.df1 }}</td>
                        <td>{{ types.df2 }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% endif %}
            
            {% if differences.different_cells %}
            <h3>Data Differences (First 10)</h3>
            <div class="json-display">{{ differences.different_cells | truncate_dict(10) | tojson(indent=2) }}</div>
            {% endif %}
            
            {% if charts.schema %}
            <div class="chart-container">
                <img src="{{ charts.schema }}" alt="Schema Differences Chart">
            </div>
            {% endif %}
        </div>
        {% endif %}

        <!-- Statistics Section -->
        {% if statistics %}
        <div class="section">
            <h2>📈 Statistics</h2>
            {% if charts.statistics %}
            <div class="chart-container">
                <img src="{{ charts.statistics }}" alt="Statistics Chart">
            </div>
            {% endif %}
            
            <h3>Detailed Statistics</h3>
            <div class="json-display">{{ statistics | tojson(indent=2) }}</div>
        </div>
        {% endif %}

        <!-- Metadata Section -->
        <div class="section">
            <h2>ℹ️ Metadata</h2>
            <div class="json-display">{{ metadata | tojson(indent=2) }}</div>
        </div>
    </div>

    <script>
        // Add interactive features
        document.addEventListener('DOMContentLoaded', function() {
            // Add click-to-expand for JSON displays
            const jsonDisplays = document.querySelectorAll('.json-display');
            jsonDisplays.forEach(display => {
                display.style.maxHeight = '200px';
                display.style.overflow = 'hidden';
                display.style.cursor = 'pointer';
                display.title = 'Click to expand/collapse';
                
                display.addEventListener('click', function() {
                    if (this.style.maxHeight === '200px') {
                        this.style.maxHeight = 'none';
                    } else {
                        this.style.maxHeight = '200px';
                    }
                });
            });
        });
        
        // Custom filter for truncating dictionaries
        function truncateDict(dict, maxItems) {
            if (typeof dict !== 'object' || dict === null) return dict;
            
            const entries = Object.entries(dict);
            if (entries.length <= maxItems) return dict;
            
            const truncated = {};
            for (let i = 0; i < maxItems; i++) {
                const [key, value] = entries[i];
                truncated[key] = value;
            }
            truncated[`... and ${entries.length - maxItems} more`] = "...";
            return truncated;
        }
    </script>
</body>
</html>
"""
        
        # Add custom filter
        template = Template(template_str)
        template.environment.filters['truncate_dict'] = lambda d, n: (
            dict(list(d.items())[:n]) if isinstance(d, dict) and len(d) > n 
            else d
        )
        
        return template 