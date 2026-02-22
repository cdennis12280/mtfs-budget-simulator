"""
Excel and Power BI export utilities for MTFS scenarios.
Generate multi-worksheet Excel files and Power BI connector templates.
"""

import os
import pandas as pd
from datetime import datetime
from pathlib import Path
import json


def generate_excel_export(output_path, scenarios_data, council_name, base_budget):
    """
    Generate a comprehensive Excel export with multiple worksheets for all scenarios.
    
    Args:
        output_path: File path to save Excel file
        scenarios_data: Dict of {scenario_name: {'projection': df, 'kpis': dict, 'rag': str}}
        council_name: Name of the council
        base_budget: Base year budget (£m)
    
    Returns:
        Absolute path to generated Excel file
    """
    
    # Create Excel writer
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        
        # ===== METADATA SHEET =====
        metadata = {
            'Export Date': [datetime.now().strftime('%d %B %Y %H:%M:%S')],
            'Council': [council_name],
            'Base Budget (£m)': [base_budget],
            'Scenarios Included': [', '.join(scenarios_data.keys())],
            'Number of Scenarios': [len(scenarios_data)],
            'Report Type': ['MTFS Multi-Scenario Analysis'],
            'Tool Version': ['MTFS Budget Gap Simulator v1.0'],
        }
        metadata_df = pd.DataFrame(metadata)
        metadata_df.to_excel(writer, sheet_name='Metadata', index=False)
        
        # ===== EXECUTIVE SUMMARY SHEET =====
        summary_data = []
        for scenario_name, scenario_info in scenarios_data.items():
            kpis = scenario_info['kpis']
            projection = scenario_info['projection']
            rag = scenario_info['rag']
            
            summary_data.append({
                'Scenario': scenario_name,
                'Total 4-Year Gap (£m)': kpis.get('total_4_year_gap', 0),
                'Gap as % of Budget': (kpis.get('total_4_year_gap', 0) / base_budget * 100),
                'Savings Required (%)': kpis.get('savings_required_pct', 0),
                'Year 1 Reserves (£m)': projection.iloc[0]['Closing_Reserves'],
                'Year 5 Reserves (£m)': projection.iloc[-1]['Closing_Reserves'],
                'RAG Rating': rag,
                'Total Cumulative Gap (£m)': kpis.get('total_4_year_gap', 0),
            })
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Executive Summary', index=False)
        
        # ===== INDIVIDUAL SCENARIO SHEETS =====
        for scenario_name, scenario_info in scenarios_data.items():
            projection = scenario_info['projection'].copy()
            
            # Round numeric columns to 2 decimal places for readability
            numeric_cols = projection.select_dtypes(include=['number']).columns
            for col in numeric_cols:
                projection[col] = projection[col].round(2)
            
            # Create sheet name (Excel max 31 chars, safe characters only)
            safe_name = scenario_name.replace('/', '-').replace('\\', '-').replace(':', '-')[:31]
            
            projection.to_excel(writer, sheet_name=safe_name, index=False)
        
        # ===== TIME SERIES COMPARISON SHEET (ALL YEARS, ALL SCENARIOS) =====
        timeseries_data = []
        
        # Get year columns from first scenario
        first_projection = list(scenarios_data.values())[0]['projection']
        years = [col for col in first_projection.columns if 'Year_' in col or col == 'Year']
        
        # For each year, collect data from all scenarios
        if len(years) > 0:
            # Try to iterate through years
            for idx, row in first_projection.iterrows():
                for scenario_name, scenario_info in scenarios_data.items():
                    scenario_projection = scenario_info['projection']
                    if idx < len(scenario_projection):
                        scenario_row = scenario_projection.iloc[idx]
                        
                        timeseries_data.append({
                            'Scenario': scenario_name,
                            'Period': f'Year {idx + 1}',
                            'Net Revenue Budget (£m)': scenario_row.get('Net_Revenue_Budget', 0),
                            'Total Expenditure (£m)': scenario_row.get('Total_Expenditure', 0),
                            'Budget Gap (£m)': scenario_row.get('Budget_Gap', 0),
                            'Cumulative Gap (£m)': scenario_row.get('Cumulative_Gap', 0),
                            'Closing Reserves (£m)': scenario_row.get('Closing_Reserves', 0),
                        })
            
            if timeseries_data:
                timeseries_df = pd.DataFrame(timeseries_data)
                timeseries_df.to_excel(writer, sheet_name='Time Series Comparison', index=False)
        
        # ===== KEY METRICS SHEET =====
        metrics_data = []
        for scenario_name, scenario_info in scenarios_data.items():
            projection = scenario_info['projection']
            kpis = scenario_info['kpis']
            
            metrics_data.append({
                'Scenario': scenario_name,
                'Year 1 Budget (£m)': projection.iloc[0]['Net_Revenue_Budget'],
                'Year 1 Gap (£m)': projection.iloc[0]['Budget_Gap'],
                'Year 5 Budget (£m)': projection.iloc[-1]['Net_Revenue_Budget'],
                'Year 5 Gap (£m)': projection.iloc[-1]['Budget_Gap'],
                'Avg Annual Gap (£m)': projection['Budget_Gap'].mean(),
                'Total Cumulative Gap (£m)': kpis.get('total_4_year_gap', 0),
                'Reserves at Year 5 (£m)': projection.iloc[-1]['Closing_Reserves'],
                'Reserves % at Year 5': (projection.iloc[-1]['Closing_Reserves'] / projection.iloc[-1]['Net_Revenue_Budget'] * 100),
            })
        
        metrics_df = pd.DataFrame(metrics_data)
        metrics_df.to_excel(writer, sheet_name='Key Metrics', index=False)
        
        # Format the metrics columns to 2 decimal places
        workbook = writer.book
        worksheet = writer.sheets['Key Metrics']
        for row in worksheet.iter_rows(min_row=2, max_row=len(metrics_df)+1, min_col=1, max_col=len(metrics_df.columns)):
            for cell in row:
                if cell.column > 1:  # Skip scenario name column
                    cell.number_format = '0.00'
    
    return os.path.abspath(output_path)


def generate_power_bi_template(output_path, council_name):
    """
    Generate a Power BI template/connector configuration file.
    This provides BI teams with a template for connecting Power BI to MTFS exports.
    
    Args:
        output_path: File path to save template (should be .json)
        council_name: Name of the council
    
    Returns:
        Absolute path to generated template
    """
    
    template = {
        "name": f"MTFS Budget Simulator - {council_name}",
        "version": "1.0",
        "description": "Power BI template for connecting to MTFS Excel exports",
        "created": datetime.now().isoformat(),
        "council": council_name,
        "data_sources": [
            {
                "name": "MTFS Excel Export",
                "type": "Excel",
                "description": "Multi-scenario MTFS Excel file from Budget Simulator",
                "sheets": [
                    {
                        "name": "Metadata",
                        "purpose": "Export metadata and council info",
                        "primary_key": None
                    },
                    {
                        "name": "Executive Summary",
                        "purpose": "High-level scenario comparison",
                        "primary_key": "Scenario"
                    },
                    {
                        "name": "Time Series Comparison",
                        "purpose": "Year-by-year comparison across scenarios",
                        "primary_keys": ["Scenario", "Period"]
                    },
                    {
                        "name": "Key Metrics",
                        "purpose": "Summary financial metrics by scenario",
                        "primary_key": "Scenario"
                    }
                ]
            }
        ],
        "recommended_visuals": [
            {
                "title": "Budget Gap Trend",
                "type": "Line Chart",
                "data_source": "Time Series Comparison",
                "x_axis": "Period",
                "y_axis": "Budget Gap (£m)",
                "legend": "Scenario",
                "description": "Shows how the gap evolves across years for each scenario"
            },
            {
                "title": "Scenario Comparison - Closing Reserves",
                "type": "Clustered Column Chart",
                "data_source": "Key Metrics",
                "x_axis": "Scenario",
                "y_axis": "Reserves at Year 5 (£m)",
                "description": "Compares ending reserves position across scenarios"
            },
            {
                "title": "Budget Gap Summary",
                "type": "Table",
                "data_source": "Executive Summary",
                "columns": ["Scenario", "Total 4-Year Gap (£m)", "Savings Required (%)", "RAG Rating"],
                "description": "Summary table of all scenarios"
            },
            {
                "title": "Reserves Trend",
                "type": "Area Chart",
                "data_source": "Time Series Comparison",
                "x_axis": "Period",
                "y_axis": "Closing Reserves (£m)",
                "legend": "Scenario",
                "description": "Shows reserves position across years and scenarios"
            }
        ],
        "relationships": [
            {
                "from_table": "Executive Summary",
                "from_column": "Scenario",
                "to_table": "Time Series Comparison",
                "to_column": "Scenario",
                "type": "one-to-many"
            },
            {
                "from_table": "Executive Summary",
                "from_column": "Scenario",
                "to_table": "Key Metrics",
                "to_column": "Scenario",
                "type": "one-to-one"
            }
        ],
        "dax_measures": [
            {
                "name": "Total Gap across Scenarios",
                "formula": "SUM('Executive Summary'[Total 4-Year Gap (£m)])"
            },
            {
                "name": "Average Year 5 Reserves",
                "formula": "AVERAGE('Key Metrics'[Reserves at Year 5 (£m)])"
            },
            {
                "name": "Gap as % of Average Budget",
                "formula": "DIVIDE(SUM('Executive Summary'[Total 4-Year Gap (£m)]), AVERAGE('Key Metrics'[Year 1 Budget (£m)]))"
            }
        ],
        "deployment_notes": [
            "1. Export the Excel file from the MTFS Budget Simulator",
            "2. Open Power BI Desktop",
            "3. Click 'Get Data' → 'Excel'",
            "4. Select the exported MTFS Excel file",
            "5. Load the sheets: Metadata, Executive Summary, Time Series Comparison, Key Metrics",
            "6. Use this template to set up relationships and create recommended visuals",
            "7. Configure refresh schedule if using OneDrive or SharePoint for source file",
            "8. Share dashboard with stakeholders via Power BI Service"
        ],
        "best_practices": [
            "Refresh the Excel export regularly (weekly or monthly) to keep Power BI dashboard current",
            "Use the RAG rating in Executive Summary for conditional formatting on scenario cards",
            "Set filters to compare specific scenarios or time periods",
            "Create a dashboard with overview of all scenarios plus drill-down pages per scenario",
            "Track assumptions carefully - consider adding a separate 'Assumptions' sheet to track changes over time",
            "Use Power BI's Q&A feature to allow non-technical users to explore the data"
        ]
    }
    
    with open(output_path, 'w') as f:
        json.dump(template, f, indent=2)
    
    return os.path.abspath(output_path)
