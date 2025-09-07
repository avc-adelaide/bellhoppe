#!/usr/bin/env python3
"""
Generate HTML coverage reports from GCOV output for integration with FORD documentation.
This script converts .gcov files into browsable HTML reports that will be accessible
through the FORD documentation system as media files.
"""

import os
import sys
import glob
import re
from pathlib import Path
from html import escape

def parse_gcov_file(gcov_path):
    """
    Parse a Fortran .gcov file and extract line, branch, and call coverage.
    """
    coverage_data = []
    branch_data = []
    call_data = []

    with open(gcov_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    # Parse lines for line coverage
    for line in lines:
        parts = line.split(':', 2)
        if len(parts) < 3:
            continue

        execution_count = parts[0].strip()
        line_number = parts[1].strip()
        source_code = parts[2].rstrip('\n')

        if line_number.isdigit():
            executed = execution_count not in ('#####', '-')
            coverage_data.append({
                'line_number': int(line_number),
                'execution_count': execution_count,
                'source_code': source_code,
                'executed': executed
            })

    # Parse branch coverage
    for line in lines:
        match = re.match(r'branch\s+(\d+)\s+taken\s+(\d+)', line)
        if match:
            branch_data.append({
                'branch_id': int(match.group(1)),
                'taken': int(match.group(2))
            })

    # Parse call coverage
    for line in lines:
        match = re.match(r'call\s+(\d+)\s+returned\s+(\d+)', line)
        if match:
            call_data.append({
                'call_id': int(match.group(1)),
                'executed': int(match.group(2))
            })

    # Compute percentages
    total_lines = sum(1 for d in coverage_data if d['execution_count'] != '-')
    executed_lines = sum(1 for d in coverage_data if d['executed'])
    line_percentage = 100 * executed_lines / total_lines if total_lines > 0 else 0

    total_branches = len(branch_data)
    executed_branches = sum(1 for b in branch_data if b['taken'] > 0)
    branch_percentage = 100 * executed_branches / total_branches if total_branches > 0 else 0

    total_calls = len(call_data)
    executed_calls = sum(1 for c in call_data if c['executed'] > 0)
    call_percentage = 100 * executed_calls / total_calls if total_calls > 0 else 0

    summary_info = {
        'line_percentage': line_percentage,
        'total_lines': total_lines,
        'branch_percentage': branch_percentage,
        'total_branches': total_branches,
        'call_percentage': call_percentage,
        'total_calls': total_calls
    }

    return coverage_data, branch_data, call_data, summary_info

def generate_html_report(gcov_file, output_dir):
    """Generate an HTML report for a single .gcov file."""
    coverage_data, branch_data, call_data, summary_info = parse_gcov_file(gcov_file)
    filename = os.path.basename(gcov_file)
    source_name = filename.replace('.gcov', '')
    
    html_filename = f"{source_name}.coverage.html"
    html_path = os.path.join(output_dir, html_filename)
    
    # Get values
    line_pct = summary_info['line_percentage']
    total_lines = summary_info['total_lines']
    branch_pct = summary_info['branch_percentage']
    total_branches = summary_info['total_branches']
    call_pct = summary_info['call_percentage']
    total_calls = summary_info['total_calls']
    
    # Start building HTML
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Coverage Report: {source_name}</title>
    <style>
        body {{ 
            font-family: 'Courier New', monospace; 
            margin: 20px; 
            background-color: #f9f9f9; 
        }}
        .header {{ 
            background-color: #2c3e50; 
            color: white; 
            padding: 20px; 
            border-radius: 5px; 
            margin-bottom: 20px; 
        }}
        .summary {{ 
            display: flex; 
            gap: 20px; 
            margin-bottom: 20px; 
        }}
        .metric {{ 
            background-color: #ecf0f1; 
            padding: 10px; 
            border-radius: 3px; 
            text-align: center; 
            min-width: 120px; 
        }}
        .metric-value {{ 
            font-size: 1.5em; 
            font-weight: bold; 
            color: #27ae60; 
        }}
        .code-container {{ 
            background-color: white; 
            border: 1px solid #bdc3c7; 
            border-radius: 5px; 
            overflow: auto; 
        }}
        .code-line {{ 
            display: flex; 
            border-bottom: 1px solid #ecf0f1; 
        }}
        .line-number {{ 
            background-color: #f8f9fa; 
            padding: 2px 8px; 
            width: 60px; 
            text-align: right; 
            border-right: 1px solid #dee2e6; 
            color: #6c757d; 
        }}
        .execution-count {{ 
            background-color: #f8f9fa; 
            padding: 2px 8px; 
            width: 80px; 
            text-align: right; 
            border-right: 1px solid #dee2e6; 
            color: #495057; 
        }}
        .source-code {{ 
            padding: 2px 8px; 
            flex: 1; 
            white-space: pre; 
        }}
        .executed {{ background-color: #d4edda; }}
        .not-executed {{ background-color: #f8d7da; }}
        .non-executable {{ background-color: #f8f9fa; }}
        .footer {{ 
            margin-top: 20px; 
            padding: 15px; 
            background-color: #e9ecef; 
            border-radius: 5px; 
            font-size: 0.9em; 
            color: #6c757d; 
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Coverage Report: {source_name}</h1>
        <p>Generated from GCOV analysis of Fortran source code</p>
    </div>
    
    <div class="summary">
        <div class="metric">
            <div class="metric-value">{line_pct:.1f}%</div>
            <div>Lines Executed</div>
            <div>{total_lines} total lines</div>
        </div>
        <div class="metric">
            <div class="metric-value">{branch_pct:.1f}%</div>
            <div>Branches Executed</div>
            <div>{total_branches} total branches</div>
        </div>
        <div class="metric">
            <div class="metric-value">{call_pct:.1f}%</div>
            <div>Calls Executed</div>
            <div>{total_calls} total calls</div>
        </div>
    </div>
    
    <div class="code-container">
"""
    
    for line_data in coverage_data:
        line_class = "non-executable"
        if line_data['execution_count'] == '#####':
            line_class = "not-executed"
        elif line_data['executed'] and line_data['execution_count'].isdigit() and int(line_data['execution_count']) > 0:
            line_class = "executed"
        
        html_content += f"""        <div class="code-line {line_class}">
            <div class="line-number">{line_data['line_number']}</div>
            <div class="execution-count">{line_data['execution_count']}</div>
            <div class="source-code">{escape(line_data['source_code'])}</div>
        </div>
"""
    
    html_content += """    </div>
    
    <div class="footer">
        <p><strong>Legend:</strong></p>
        <ul>
            <li><span style="background-color: #d4edda; padding: 2px 4px;">Green</span> - Executed lines</li>
            <li><span style="background-color: #f8d7da; padding: 2px 4px;">Red</span> - Not executed lines</li>
            <li><span style="background-color: #f8f9fa; padding: 2px 4px;">Gray</span> - Non-executable lines (comments, declarations)</li>
        </ul>
        <p><strong>Execution Count:</strong> Number of times each line was executed. ##### indicates never executed, - indicates non-executable.</p>
    </div>
</body>
</html>"""
    
    with open(html_path, 'w') as f:
        f.write(html_content)
    
    return html_filename, summary_info

def generate_index_html(coverage_reports, output_dir):
    """Generate an index HTML file listing all coverage reports."""
    index_path = os.path.join(output_dir, 'coverage-index.html')
    
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BELLHOP Coverage Reports</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 20px; 
            background-color: #f9f9f9; 
        }
        .header { 
            background-color: #2c3e50; 
            color: white; 
            padding: 20px; 
            border-radius: 5px; 
            margin-bottom: 20px; 
        }
        table { 
            width: 100%; 
            border-collapse: collapse; 
            background-color: white; 
            border-radius: 5px; 
            overflow: hidden; 
            box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
        }
        th, td { 
            padding: 12px; 
            text-align: left; 
            border-bottom: 1px solid #ddd; 
        }
        th { 
            background-color: #34495e; 
            color: white; 
        }
        .percentage { 
            font-weight: bold; 
        }
        .high-coverage { color: #27ae60; }
        .medium-coverage { color: #f39c12; }
        .low-coverage { color: #e74c3c; }
        a { 
            color: #3498db; 
            text-decoration: none; 
        }
        a:hover { 
            text-decoration: underline; 
        }
        .footer { 
            margin-top: 20px; 
            padding: 15px; 
            background-color: #e9ecef; 
            border-radius: 5px; 
            font-size: 0.9em; 
            color: #6c757d; 
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>BELLHOP Coverage Reports</h1>
        <p>Code coverage analysis for BELLHOP Fortran acoustic simulator</p>
    </div>
    
    <table>
        <thead>
            <tr>
                <th>Source File</th>
                <th>Lines Coverage</th>
                <th>Branches Coverage</th>
                <th>Calls Coverage</th>
                <th>Report</th>
            </tr>
        </thead>
        <tbody>
"""
    
    for report_file, summary in coverage_reports:
        source_name = report_file.replace('.coverage.html', '')
        line_pct = summary.get('line_percentage', 0)
        branch_pct = summary.get('branch_percentage', 0)
        call_pct = summary.get('call_percentage', 0)
        
        # Determine CSS class based on line coverage
        line_class = "high-coverage" if line_pct >= 80 else "medium-coverage" if line_pct >= 50 else "low-coverage"
        branch_class = "high-coverage" if branch_pct >= 80 else "medium-coverage" if branch_pct >= 50 else "low-coverage"
        call_class = "high-coverage" if call_pct >= 80 else "medium-coverage" if call_pct >= 50 else "low-coverage"
        
        html_content += f"""            <tr>
                <td><code>{source_name}</code></td>
                <td class="percentage {line_class}">{line_pct:.1f}%</td>
                <td class="percentage {branch_class}">{branch_pct:.1f}%</td>
                <td class="percentage {call_class}">{call_pct:.1f}%</td>
                <td><a href="{report_file}">View Report</a></td>
            </tr>
"""
    
    html_content += """        </tbody>
    </table>
    
    <div class="footer">
        <p><strong>Coverage Thresholds:</strong></p>
        <ul>
            <li><span class="high-coverage">Green</span> - 80% or higher coverage</li>
            <li><span class="medium-coverage">Orange</span> - 50-79% coverage</li>
            <li><span class="low-coverage">Red</span> - Below 50% coverage</li>
        </ul>
        <p>Reports generated using GCOV code coverage analysis of BELLHOP Fortran source code.</p>
    </div>
</body>
</html>"""
    
    with open(index_path, 'w') as f:
        f.write(html_content)

def main():
    """Main function to generate HTML coverage reports."""
    if len(sys.argv) != 2:
        print("Usage: python3 generate_coverage_html.py <output_directory>")
        sys.exit(1)
    
    output_dir = sys.argv[1]
    os.makedirs(output_dir, exist_ok=True)
    
    # Find all .gcov files
    gcov_files = []
    for pattern in ['**/*.gcov', '*/*.gcov', '*.gcov']:
        gcov_files.extend(glob.glob(pattern, recursive=True))
    
    if not gcov_files:
        print("No .gcov files found. Please run coverage analysis first.")
        sys.exit(1)
    
    print(f"Found {len(gcov_files)} .gcov files")
    
    coverage_reports = []
    for gcov_file in gcov_files:
        print(f"Processing {gcov_file}")
        try:
            html_filename, summary_info = generate_html_report(gcov_file, output_dir)
            coverage_reports.append((html_filename, summary_info))
            print(f"  -> Generated {html_filename}")
        except Exception as e:
            print(f"  -> Error processing {gcov_file}: {e}")
    
    if coverage_reports:
        generate_index_html(coverage_reports, output_dir)
        print(f"\nGenerated {len(coverage_reports)} HTML coverage reports in {output_dir}")
        print(f"Index file: {os.path.join(output_dir, 'coverage-index.html')}")
    else:
        print("No coverage reports generated")
        sys.exit(1)

if __name__ == "__main__":
    main()