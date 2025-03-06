#!/usr/bin/env python
"""
Script to run benchmarks for the knowledge extraction components.

This script runs benchmark tests for the knowledge extraction components
and generates a performance report.
"""

import os
import sys
import time
import argparse
import subprocess
import json
from datetime import datetime


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run benchmarks for knowledge extraction components")
    parser.add_argument("--component", "-c", choices=["document", "entity", "relationship", "knowledge_graph", "all"],
                        default="all", help="Component to benchmark")
    parser.add_argument("--output", "-o", default="benchmark_results",
                        help="Output directory for benchmark results")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Print verbose output")
    parser.add_argument("--quick", "-q", action="store_true",
                        help="Run a quick benchmark with reduced test data")
    return parser.parse_args()


def run_benchmark(component, output_dir, verbose=False, quick=False):
    """Run benchmark tests for the specified component."""
    # Map component to test file
    component_map = {
        "document": "test_document_processing_performance.py",
        "entity": "test_entity_recognition_performance.py",
        "relationship": "test_relationship_extraction_performance.py",
        "knowledge_graph": "test_knowledge_extractor_performance.py"
    }
    
    # If component is 'all', run all components
    if component == "all":
        components = list(component_map.keys())
    else:
        components = [component]
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Run benchmark tests for each component
    results = {}
    for comp in components:
        test_file = component_map[comp]
        print(f"Running benchmark tests for {comp}...")
        
        # Build command
        cmd = ["python", "-m", "pytest", f"tests/research_orchestrator/knowledge_extraction/benchmark/{test_file}"]
        if verbose:
            cmd.append("-v")
        if quick:
            cmd.append("-k")
            cmd.append("not test_scalability and not test_memory_usage")
        
        # Capture output
        start_time = time.time()
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()
        end_time = time.time()
        
        # Save results
        results[comp] = {
            "success": process.returncode == 0,
            "runtime": end_time - start_time,
            "output": stdout,
            "error": stderr if process.returncode != 0 else None
        }
        
        # Print results
        if verbose:
            print(stdout)
            if process.returncode != 0:
                print(stderr, file=sys.stderr)
        else:
            print(f"  {'✓' if process.returncode == 0 else '✗'} {comp}: {end_time - start_time:.2f}s")
    
    return results


def parse_benchmark_results(results):
    """Parse benchmark results to extract timing information."""
    parsed_results = {}
    
    for component, result in results.items():
        if not result["success"]:
            # Include error information for failed components
            parsed_results[component] = {
                "error": True,
                "error_message": result.get("error", "Unknown error")
            }
            continue
        
        # Extract timing information from output
        timings = {}
        memory_usage = {}
        scaling_metrics = {}
        
        # Multiple parsing patterns for different output formats
        for line in result["output"].splitlines():
            # Standard timing pattern
            if ":" in line and "seconds" in line:
                parts = line.split(":", 1)  # Split on first colon only
                if len(parts) >= 2:
                    # Extract test name and timing
                    test_name = parts[0].strip()
                    timing_part = parts[1].strip()
                    if "seconds" in timing_part:
                        try:
                            timing = float(timing_part.split()[0])
                            timings[test_name] = timing
                        except (ValueError, IndexError):
                            pass
            
            # Memory usage pattern
            elif "memory usage:" in line.lower():
                parts = line.split(":", 1)
                if len(parts) >= 2:
                    test_name = parts[0].strip()
                    mem_part = parts[1].strip()
                    try:
                        # Extract memory value and unit
                        mem_parts = mem_part.split()
                        mem_value = float(mem_parts[0])
                        mem_unit = mem_parts[1] if len(mem_parts) > 1 else "MB"
                        memory_usage[test_name] = {
                            "value": mem_value,
                            "unit": mem_unit
                        }
                    except (ValueError, IndexError):
                        pass
            
            # Scaling factor pattern
            elif "scaling factor:" in line.lower():
                parts = line.split(":", 1)
                if len(parts) >= 2:
                    test_name = parts[0].strip()
                    scaling_part = parts[1].strip()
                    try:
                        scaling_value = float(scaling_part.split()[0])
                        scaling_metrics[test_name] = scaling_value
                    except (ValueError, IndexError):
                        pass
        
        parsed_results[component] = {
            "timings": timings,
            "memory_usage": memory_usage,
            "scaling_metrics": scaling_metrics
        }
    
    return parsed_results


def generate_report(results, parsed_results, output_dir, quick=False):
    """Generate a performance report."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create unique timestamp for this report
    timestamp = int(time.time())
    
    # Create report data
    report = {
        "timestamp": datetime.now().isoformat(),
        "quick_mode": quick,
        "components": {},
        "history": get_historical_data(output_dir)
    }
    
    for component, result in results.items():
        if not result["success"]:
            # Handle failed component
            component_report = {
                "success": False,
                "runtime": result["runtime"],
                "error": result.get("error", "Unknown error")
            }
        else:
            # Handle successful component
            if isinstance(parsed_results.get(component, {}), dict) and "error" in parsed_results.get(component, {}):
                # This component had parsing errors
                component_report = {
                    "success": False,
                    "runtime": result["runtime"],
                    "error": parsed_results[component].get("error_message", "Error parsing results")
                }
            else:
                # Successful component with valid results
                component_report = {
                    "success": True,
                    "runtime": result["runtime"],
                    "timings": parsed_results.get(component, {}).get("timings", {}),
                    "memory_usage": parsed_results.get(component, {}).get("memory_usage", {}),
                    "scaling_metrics": parsed_results.get(component, {}).get("scaling_metrics", {})
                }
        
        report["components"][component] = component_report
    
    # Save report to file
    report_file = os.path.join(output_dir, f"benchmark_report_{timestamp}.json")
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)
    
    # Generate HTML report
    html_report = generate_html_report(report)
    html_file = os.path.join(output_dir, f"benchmark_report_{timestamp}.html")
    with open(html_file, "w") as f:
        f.write(html_report)
    
    # Update index.html file that links to all reports
    update_index_html(output_dir, timestamp)
    
    print(f"\nBenchmark report saved to {report_file}")
    print(f"HTML report saved to {html_file}")
    print(f"View all reports at {os.path.join(output_dir, 'index.html')}")
    
    # Clean up old reports (keep last 10)
    cleanup_old_reports(output_dir)
    
    return report_file, html_file


def get_historical_data(output_dir):
    """Get historical benchmark data from previous runs."""
    history = {}
    
    # Look for previous JSON reports
    if not os.path.exists(output_dir):
        return history
    
    json_files = [f for f in os.listdir(output_dir) if f.startswith("benchmark_report_") and f.endswith(".json")]
    
    # Sort by timestamp (newest first)
    json_files.sort(reverse=True)
    
    # Get data from up to 5 previous reports
    for i, json_file in enumerate(json_files[:5]):
        with open(os.path.join(output_dir, json_file), "r") as f:
            try:
                data = json.load(f)
                timestamp = json_file.replace("benchmark_report_", "").replace(".json", "")
                history[timestamp] = {
                    "timestamp": data.get("timestamp", "Unknown"),
                    "components": {}
                }
                
                # Extract runtime data for each component
                for comp, comp_data in data.get("components", {}).items():
                    if comp_data.get("success", False):
                        history[timestamp]["components"][comp] = {
                            "runtime": comp_data.get("runtime", 0)
                        }
            except json.JSONDecodeError:
                continue
    
    return history


def update_index_html(output_dir, current_timestamp):
    """Update the index.html file that links to all reports."""
    # Get all HTML report files
    html_files = [f for f in os.listdir(output_dir) 
                 if f.startswith("benchmark_report_") and f.endswith(".html")]
    
    # Sort by timestamp (newest first)
    html_files.sort(reverse=True)
    
    # Create index HTML
    index_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Knowledge Extraction Benchmark Reports</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            h1 { color: #333; }
            ul { list-style-type: none; padding: 0; }
            li { margin: 10px 0; padding: 10px; background-color: #f9f9f9; border-radius: 5px; }
            li.current { background-color: #e0f7fa; border-left: 5px solid #00bcd4; }
            a { color: #0066cc; text-decoration: none; }
            a:hover { text-decoration: underline; }
            .timestamp { color: #666; font-size: 0.9em; }
        </style>
    </head>
    <body>
        <h1>Knowledge Extraction Benchmark Reports</h1>
        <ul>
    """
    
    # Add links to each report
    for html_file in html_files:
        timestamp = html_file.replace("benchmark_report_", "").replace(".html", "")
        date_str = datetime.fromtimestamp(int(timestamp)).strftime("%Y-%m-%d %H:%M:%S")
        
        # Check if this is the current report
        is_current = str(current_timestamp) == timestamp
        
        index_html += f"""
        <li class="{'current' if is_current else ''}">
            <a href="{html_file}">{date_str}</a>
            <span class="timestamp">(ID: {timestamp})</span>
            {' <strong>Current</strong>' if is_current else ''}
        </li>
        """
    
    index_html += """
        </ul>
    </body>
    </html>
    """
    
    # Write index.html
    with open(os.path.join(output_dir, "index.html"), "w") as f:
        f.write(index_html)


def cleanup_old_reports(output_dir, keep=10):
    """Clean up old benchmark reports, keeping only the most recent ones."""
    # Get all benchmark files
    json_files = [f for f in os.listdir(output_dir) if f.startswith("benchmark_report_") and f.endswith(".json")]
    html_files = [f for f in os.listdir(output_dir) if f.startswith("benchmark_report_") and f.endswith(".html")]
    
    # Sort by timestamp
    json_files.sort(reverse=True)
    html_files.sort(reverse=True)
    
    # Remove old JSON files
    for json_file in json_files[keep:]:
        try:
            os.remove(os.path.join(output_dir, json_file))
        except OSError:
            pass
    
    # Remove old HTML files
    for html_file in html_files[keep:]:
        try:
            os.remove(os.path.join(output_dir, html_file))
        except OSError:
            pass


def generate_html_report(report):
    """Generate an HTML report from the benchmark results."""
    # Start HTML
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Knowledge Extraction Benchmark Report</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
            h1, h2, h3 { color: #333; }
            table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            tr:nth-child(even) { background-color: #f9f9f9; }
            .success { color: green; }
            .failure { color: red; }
            .warning { color: orange; }
            .component { margin-bottom: 30px; }
            .summary { margin-bottom: 30px; }
            .chart-container { height: 300px; margin-bottom: 30px; }
            .tab { overflow: hidden; border: 1px solid #ccc; background-color: #f1f1f1; }
            .tab button { background-color: inherit; float: left; border: none; outline: none; cursor: pointer; padding: 10px 16px; transition: 0.3s; }
            .tab button:hover { background-color: #ddd; }
            .tab button.active { background-color: #ccc; }
            .tabcontent { display: none; padding: 6px 12px; border: 1px solid #ccc; border-top: none; }
            .error-message { background-color: #fff0f0; border-left: 4px solid #f44336; padding: 12px; margin: 10px 0; }
            .offline-message { font-style: italic; color: #888; }
            .scaling-good { color: green; }
            .scaling-warning { color: orange; }
            .scaling-bad { color: red; }
        </style>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body>
        <h1>Knowledge Extraction Benchmark Report</h1>
        <p>Generated: """ + report["timestamp"] + """</p>
        <p>Quick mode: """ + ("Yes" if report["quick_mode"] else "No") + """</p>
        
        <!-- Tab navigation -->
        <div class="tab">
            <button class="tablinks active" onclick="openTab(event, 'Summary')">Summary</button>
            <button class="tablinks" onclick="openTab(event, 'Details')">Component Details</button>
            <button class="tablinks" onclick="openTab(event, 'History')">Historical Data</button>
            <button class="tablinks" onclick="openTab(event, 'Memory')">Memory Usage</button>
            <button class="tablinks" onclick="openTab(event, 'Scaling')">Scaling Metrics</button>
        </div>
        
        <!-- Summary tab -->
        <div id="Summary" class="tabcontent" style="display: block;">
            <div class="summary">
                <h2>Summary</h2>
                <table>
                    <tr>
                        <th>Component</th>
                        <th>Status</th>
                        <th>Runtime (s)</th>
                        <th>Tests</th>
                        <th>Memory Tests</th>
                        <th>Scaling Tests</th>
                    </tr>
    """
    
    # Add summary rows
    for component, data in report["components"].items():
        if not data.get("success", False):
            html += f"""
                <tr>
                    <td>{component}</td>
                    <td class="failure">Failure</td>
                    <td>{data.get('runtime', 0):.2f}</td>
                    <td>-</td>
                    <td>-</td>
                    <td>-</td>
                </tr>
            """
        else:
            html += f"""
                <tr>
                    <td>{component}</td>
                    <td class="success">Success</td>
                    <td>{data.get('runtime', 0):.2f}</td>
                    <td>{len(data.get('timings', {}))}</td>
                    <td>{len(data.get('memory_usage', {}))}</td>
                    <td>{len(data.get('scaling_metrics', {}))}</td>
                </tr>
            """
    
    html += """
                </table>
            </div>
            
            <div class="chart-container">
                <canvas id="runtimeChart"></canvas>
            </div>
            
            <!-- Failed Components -->
    """
    
    # Add failure information
    failed_components = [c for c, d in report["components"].items() if not d.get("success", False)]
    if failed_components:
        html += """
            <div class="component">
                <h2>Failed Components</h2>
        """
        
        for component in failed_components:
            data = report["components"][component]
            html += f"""
                <div class="error-message">
                    <h3>{component}</h3>
                    <pre>{data.get('error', 'Unknown error')}</pre>
                </div>
            """
        
        html += """
            </div>
        """
    
    html += """
        </div>
        
        <!-- Component Details tab -->
        <div id="Details" class="tabcontent">
    """
    
    # Add component details
    for component, data in report["components"].items():
        if not data.get("success", False):
            continue
        
        html += f"""
            <div class="component">
                <h2>{component} Benchmark Results</h2>
                <table>
                    <tr>
                        <th>Test</th>
                        <th>Time (s)</th>
                    </tr>
        """
        
        # Add timing rows
        for test, timing in data.get("timings", {}).items():
            html += f"""
                    <tr>
                        <td>{test}</td>
                        <td>{timing:.4f}</td>
                    </tr>
                """
        
        html += """
                </table>
            </div>
        """
    
    html += """
        </div>
        
        <!-- Historical Data tab -->
        <div id="History" class="tabcontent">
            <div class="component">
                <h2>Historical Runtime Comparison</h2>
                <div class="chart-container">
                    <canvas id="historyChart"></canvas>
                </div>
            </div>
        </div>
        
        <!-- Memory Usage tab -->
        <div id="Memory" class="tabcontent">
            <div class="component">
                <h2>Memory Usage</h2>
    """
    
    # Add memory usage data
    memory_components = [c for c, d in report["components"].items() 
                       if d.get("success", False) and d.get("memory_usage", {})]
                       
    if memory_components:
        html += """
                <div class="chart-container">
                    <canvas id="memoryChart"></canvas>
                </div>
                <table>
                    <tr>
                        <th>Component</th>
                        <th>Test</th>
                        <th>Memory Value</th>
                        <th>Unit</th>
                    </tr>
        """
        
        for component in memory_components:
            data = report["components"][component]
            for test, mem_data in data.get("memory_usage", {}).items():
                html += f"""
                    <tr>
                        <td>{component}</td>
                        <td>{test}</td>
                        <td>{mem_data.get('value', 0):.2f}</td>
                        <td>{mem_data.get('unit', 'MB')}</td>
                    </tr>
                """
        
        html += """
                </table>
        """
    else:
        html += """
                <p class="offline-message">No memory usage data available for this benchmark run.</p>
        """
    
    html += """
            </div>
        </div>
        
        <!-- Scaling Metrics tab -->
        <div id="Scaling" class="tabcontent">
            <div class="component">
                <h2>Scaling Metrics</h2>
    """
    
    # Add scaling metrics data
    scaling_components = [c for c, d in report["components"].items() 
                        if d.get("success", False) and d.get("scaling_metrics", {})]
                        
    if scaling_components:
        html += """
                <p>Scaling factors show how processing time increases with input size:</p>
                <ul>
                    <li><span class="scaling-good">O(1) or O(log n): &lt; 1.1</span> - Excellent scaling</li>
                    <li><span class="scaling-good">O(n): 1.0 to 1.2</span> - Good linear scaling</li>
                    <li><span class="scaling-warning">O(n log n): 1.2 to 1.5</span> - Acceptable scaling</li>
                    <li><span class="scaling-bad">O(n²) or worse: &gt; 1.5</span> - Poor scaling, needs optimization</li>
                </ul>
                <table>
                    <tr>
                        <th>Component</th>
                        <th>Test</th>
                        <th>Scaling Factor</th>
                        <th>Performance</th>
                    </tr>
        """
        
        for component in scaling_components:
            data = report["components"][component]
            for test, scaling in data.get("scaling_metrics", {}).items():
                # Determine scaling category
                scaling_class = "scaling-good"
                performance = "Excellent"
                if scaling > 1.5:
                    scaling_class = "scaling-bad"
                    performance = "Poor"
                elif scaling > 1.2:
                    scaling_class = "scaling-warning"
                    performance = "Acceptable"
                elif scaling > 1.0:
                    scaling_class = "scaling-good"
                    performance = "Good"
                
                html += f"""
                    <tr>
                        <td>{component}</td>
                        <td>{test}</td>
                        <td class="{scaling_class}">{scaling:.3f}</td>
                        <td class="{scaling_class}">{performance}</td>
                    </tr>
                """
        
        html += """
                </table>
                <div class="chart-container">
                    <canvas id="scalingChart"></canvas>
                </div>
        """
    else:
        html += """
                <p class="offline-message">No scaling metrics available for this benchmark run.</p>
        """
    
    html += """
            </div>
        </div>
        
        <script>
            // Tab navigation function
            function openTab(evt, tabName) {
                // Declare all variables
                var i, tabcontent, tablinks;

                // Get all elements with class="tabcontent" and hide them
                tabcontent = document.getElementsByClassName("tabcontent");
                for (i = 0; i < tabcontent.length; i++) {
                    tabcontent[i].style.display = "none";
                }

                // Get all elements with class="tablinks" and remove the class "active"
                tablinks = document.getElementsByClassName("tablinks");
                for (i = 0; i < tablinks.length; i++) {
                    tablinks[i].className = tablinks[i].className.replace(" active", "");
                }

                // Show the current tab, and add an "active" class to the button that opened the tab
                document.getElementById(tabName).style.display = "block";
                evt.currentTarget.className += " active";
            }
            
            // Charts
            document.addEventListener('DOMContentLoaded', function() {
                // Runtime chart
                const runtimeCtx = document.getElementById('runtimeChart').getContext('2d');
                new Chart(runtimeCtx, {
                    type: 'bar',
                    data: {
                        labels: [""" + ", ".join([f"'{component}'" for component in report["components"].keys()]) + """],
                        datasets: [{
                            label: 'Runtime (s)',
                            data: [""" + ", ".join([f"{data.get('runtime', 0):.2f}" for data in report["components"].values()]) + """],
                            backgroundColor: 'rgba(54, 162, 235, 0.5)',
                            borderColor: 'rgba(54, 162, 235, 1)',
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            y: {
                                beginAtZero: true,
                                title: {
                                    display: true,
                                    text: 'Time (seconds)'
                                }
                            }
                        }
                    }
                });
    """
    
    # Add historical data chart if available
    if report.get("history"):
        history_data = report.get("history", {})
        timestamps = []
        datasets = {}
        
        # Collect data for each component across time
        for timestamp, data in history_data.items():
            display_time = datetime.fromtimestamp(int(timestamp)).strftime("%m-%d %H:%M")
            timestamps.append(display_time)
            
            for component, comp_data in data.get("components", {}).items():
                if component not in datasets:
                    datasets[component] = []
                datasets[component].append(comp_data.get("runtime", 0))
        
        # Add current run to the historical data
        current_display_time = datetime.fromisoformat(report["timestamp"]).strftime("%m-%d %H:%M")
        timestamps.append(current_display_time)
        
        for component, data in report["components"].items():
            if component not in datasets:
                datasets[component] = [0] * len(timestamps[:-1])
            datasets[component].append(data.get("runtime", 0))
        
        # Create datasets for Chart.js
        dataset_configs = []
        colors = ['rgba(54, 162, 235, 0.5)', 'rgba(255, 99, 132, 0.5)', 
                  'rgba(75, 192, 192, 0.5)', 'rgba(255, 159, 64, 0.5)', 
                  'rgba(153, 102, 255, 0.5)']
        
        for i, (component, values) in enumerate(datasets.items()):
            color_idx = i % len(colors)
            dataset_configs.append(f"""{{
                label: '{component}',
                data: [{", ".join([f"{v:.2f}" for v in values])}],
                backgroundColor: '{colors[color_idx]}',
                borderColor: '{colors[color_idx].replace("0.5", "1")}',
                borderWidth: 1
            }}""")
        
        html += f"""
                // Historical data chart
                const historyCtx = document.getElementById('historyChart').getContext('2d');
                new Chart(historyCtx, {{
                    type: 'line',
                    data: {{
                        labels: ["{('", "').join(timestamps)}"],
                        datasets: [{", ".join(dataset_configs)}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {{
                            y: {{
                                beginAtZero: true,
                                title: {{
                                    display: true,
                                    text: 'Runtime (seconds)'
                                }}
                            }}
                        }}
                    }}
                }});
        """
    
    # Add memory usage chart if available
    memory_data = {}
    for component, data in report["components"].items():
        if data.get("success", False) and data.get("memory_usage"):
            memory_data[component] = data.get("memory_usage", {})
    
    if memory_data:
        memory_labels = []
        memory_values = []
        memory_colors = []
        
        color_map = {
            "document": 'rgba(54, 162, 235, 0.5)',
            "entity": 'rgba(255, 99, 132, 0.5)',
            "relationship": 'rgba(75, 192, 192, 0.5)',
            "knowledge_graph": 'rgba(255, 159, 64, 0.5)'
        }
        
        for component, tests in memory_data.items():
            for test, mem_data in tests.items():
                memory_labels.append(f"{component}: {test}")
                memory_values.append(mem_data.get("value", 0))
                memory_colors.append(color_map.get(component, 'rgba(153, 102, 255, 0.5)'))
        
        html += f"""
                // Memory usage chart
                const memoryCtx = document.getElementById('memoryChart').getContext('2d');
                new Chart(memoryCtx, {{
                    type: 'bar',
                    data: {{
                        labels: ["{('", "').join(memory_labels)}"],
                        datasets: [{{
                            label: 'Memory Usage (MB)',
                            data: [{", ".join([str(v) for v in memory_values])}],
                            backgroundColor: ["{('", "').join(memory_colors)}"],
                            borderColor: ["{('", "').join([c.replace("0.5", "1") for c in memory_colors])}"],
                            borderWidth: 1
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {{
                            y: {{
                                beginAtZero: true,
                                title: {{
                                    display: true,
                                    text: 'Memory (MB)'
                                }}
                            }}
                        }}
                    }}
                }});
        """
    
    # Add scaling metrics chart if available
    scaling_data = {}
    for component, data in report["components"].items():
        if data.get("success", False) and data.get("scaling_metrics"):
            scaling_data[component] = data.get("scaling_metrics", {})
    
    if scaling_data:
        scaling_labels = []
        scaling_values = []
        scaling_colors = []
        
        for component, tests in scaling_data.items():
            for test, scaling in tests.items():
                scaling_labels.append(f"{component}: {test}")
                scaling_values.append(scaling)
                
                # Color based on scaling value
                if scaling > 1.5:
                    color = 'rgba(255, 99, 132, 0.5)'  # Red for bad scaling
                elif scaling > 1.2:
                    color = 'rgba(255, 159, 64, 0.5)'  # Orange for moderate scaling
                else:
                    color = 'rgba(75, 192, 192, 0.5)'  # Green for good scaling
                
                scaling_colors.append(color)
        
        html += f"""
                // Scaling metrics chart
                const scalingCtx = document.getElementById('scalingChart').getContext('2d');
                new Chart(scalingCtx, {{
                    type: 'bar',
                    data: {{
                        labels: ["{('", "').join(scaling_labels)}"],
                        datasets: [{{
                            label: 'Scaling Factor',
                            data: [{", ".join([str(v) for v in scaling_values])}],
                            backgroundColor: ["{('", "').join(scaling_colors)}"],
                            borderColor: ["{('", "').join([c.replace("0.5", "1") for c in scaling_colors])}"],
                            borderWidth: 1
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {{
                            y: {{
                                beginAtZero: true,
                                suggestedMax: 2.0,
                                title: {{
                                    display: true,
                                    text: 'Scaling Factor'
                                }}
                            }}
                        }}
                    }}
                }});
        """
    
    html += """
            });
        </script>
    </body>
    </html>
    """
    
    return html


def main():
    """Main function."""
    # Parse arguments
    args = parse_args()
    
    # Run benchmarks
    results = run_benchmark(args.component, args.output, args.verbose, args.quick)
    
    # Parse results
    parsed_results = parse_benchmark_results(results)
    
    # Generate report
    generate_report(results, parsed_results, args.output, args.quick)


if __name__ == "__main__":
    main()