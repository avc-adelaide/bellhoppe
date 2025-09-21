#!/usr/bin/env python3
"""
Generate a unified coverage index page that links both Fortran and Python coverage reports.
This creates a landing page that provides access to both coverage report types.
"""

import os
import sys
from pathlib import Path

def generate_unified_index(output_dir, fortran_dir="_coverage", python_dir="_coverage_python"):
    """Generate a unified index HTML file linking both Fortran and Python coverage reports."""
    
    output_path = Path(output_dir) / "index.html"
    fortran_index = f"{fortran_dir}/coverage-index.html"
    python_index = f"{python_dir}/index.html"
    
    # Check if both coverage reports exist
    fortran_exists = os.path.exists(fortran_index)
    python_exists = os.path.exists(python_index)
    
    if not fortran_exists and not python_exists:
        print("No coverage reports found. Please run coverage analysis first.")
        return
    
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BELLHOP Coverage Reports</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 40px;
            background-color: #f5f5f5;
            line-height: 1.6;
        }
        .header {
            background-color: #2c3e50;
            color: white;
            padding: 30px;
            border-radius: 8px;
            margin-bottom: 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
        }
        .header p {
            margin: 10px 0 0 0;
            font-size: 1.2em;
            opacity: 0.9;
        }
        .coverage-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 30px;
            margin-bottom: 30px;
        }
        .coverage-card {
            background-color: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .coverage-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        }
        .coverage-card h2 {
            color: #2c3e50;
            margin-top: 0;
            font-size: 1.8em;
        }
        .coverage-card p {
            color: #666;
            margin-bottom: 25px;
        }
        .coverage-button {
            display: inline-block;
            background-color: #3498db;
            color: white;
            padding: 12px 25px;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            transition: background-color 0.2s ease;
        }
        .coverage-button:hover {
            background-color: #2980b9;
        }
        .coverage-button.unavailable {
            background-color: #95a5a6;
            cursor: not-allowed;
        }
        .icon {
            font-size: 3em;
            margin-bottom: 15px;
        }
        .fortran-icon {
            color: #e74c3c;
        }
        .python-icon {
            color: #f39c12;
        }
        .footer {
            text-align: center;
            margin-top: 50px;
            padding: 20px;
            background-color: white;
            border-radius: 8px;
            color: #666;
        }
        .status {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 3px;
            font-size: 0.9em;
            font-weight: bold;
            margin-left: 10px;
        }
        .status.available {
            background-color: #2ecc71;
            color: white;
        }
        .status.unavailable {
            background-color: #e74c3c;
            color: white;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>BELLHOP Coverage Reports</h1>
        <p>Code coverage analysis for BELLHOP underwater acoustic simulator</p>
    </div>

    <div class="coverage-grid">
        <div class="coverage-card">
            <div class="icon fortran-icon">🔧</div>
            <h2>Fortran Coverage</h2>
            <p>Coverage analysis for the core BELLHOP Fortran acoustic simulation engine using GCOV.</p>
"""

    if fortran_exists:
        html_content += f"""            <a href="{fortran_index}" class="coverage-button">View Fortran Coverage</a>
            <span class="status available">Available</span>"""
    else:
        html_content += """            <span class="coverage-button unavailable">Not Available</span>
            <span class="status unavailable">Not Generated</span>"""

    html_content += """
        </div>

        <div class="coverage-card">
            <div class="icon python-icon">🐍</div>
            <h2>Python Coverage</h2>
            <p>Coverage analysis for the BELLHOP Python API and wrapper functions using coverage.py.</p>
"""

    if python_exists:
        html_content += f"""            <a href="{python_index}" class="coverage-button">View Python Coverage</a>
            <span class="status available">Available</span>"""
    else:
        html_content += """            <span class="coverage-button unavailable">Not Available</span>
            <span class="status unavailable">Not Generated</span>"""

    html_content += """
        </div>
    </div>

    <div class="footer">
        <p><strong>About Coverage Reports:</strong></p>
        <ul style="text-align: left; display: inline-block;">
            <li><strong>Fortran Coverage:</strong> Measures execution of the core acoustic simulation algorithms</li>
            <li><strong>Python Coverage:</strong> Measures execution of the Python API, file readers, and plotting utilities</li>
        </ul>
        <p>Coverage reports are generated using GCOV (Fortran) and coverage.py (Python).</p>
    </div>
</body>
</html>"""

    with open(output_path, 'w') as f:
        f.write(html_content)
    
    print(f"Unified coverage index generated: {output_path}")
    
    if fortran_exists:
        print(f"  -> Fortran coverage: {fortran_index}")
    if python_exists:
        print(f"  -> Python coverage: {python_index}")

def main():
    """Main function to generate unified coverage index."""
    if len(sys.argv) != 2:
        print("Usage: python3 generate_unified_coverage.py <output_directory>")
        sys.exit(1)
    
    output_dir = sys.argv[1]
    os.makedirs(output_dir, exist_ok=True)
    
    generate_unified_index(output_dir)

if __name__ == "__main__":
    main()