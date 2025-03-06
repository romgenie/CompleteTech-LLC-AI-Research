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
        cmd = ["python", "-m", "pytest", f"benchmark/{test_file}"]
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
            continue
        
        # Extract timing information from output
        timings = {}
        for line in result["output"].splitlines():
            if ":" in line and "seconds" in line:
                parts = line.split(":")
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
        
        parsed_results[component] = timings
    
    return parsed_results


def generate_report(results, parsed_results, output_dir, quick=False):
    """Generate a performance report."""
    # Create report data
    report = {
        "timestamp": datetime.now().isoformat(),
        "quick_mode": quick,
        "components": {}
    }
    
    for component, result in results.items():
        component_report = {
            "success": result["success"],
            "runtime": result["runtime"],
            "timings": parsed_results.get(component, {})
        }
        report["components"][component] = component_report
    
    # Save report to file
    report_file = os.path.join(output_dir, f"benchmark_report_{int(time.time())}.json")
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)
    
    # Generate HTML report
    html_report = generate_html_report(report)
    html_file = os.path.join(output_dir, f"benchmark_report_{int(time.time())}.html")
    with open(html_file, "w") as f:
        f.write(html_report)
    
    print(f"\nBenchmark report saved to {report_file}")
    print(f"HTML report saved to {html_file}")
    
    return report_file, html_file


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
            .component { margin-bottom: 30px; }
            .summary { margin-bottom: 30px; }
            .chart-container { height: 300px; margin-bottom: 30px; }
        </style>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body>
        <h1>Knowledge Extraction Benchmark Report</h1>
        <p>Generated: """ + report["timestamp"] + """</p>
        <p>Quick mode: """ + ("Yes" if report["quick_mode"] else "No") + """</p>
        
        <div class="summary">
            <h2>Summary</h2>
            <table>
                <tr>
                    <th>Component</th>
                    <th>Status</th>
                    <th>Runtime (s)</th>
                    <th>Tests</th>
                </tr>
    """
    
    # Add summary rows
    for component, data in report["components"].items():
        html += f"""
                <tr>
                    <td>{component}</td>
                    <td class="{'success' if data['success'] else 'failure'}">{'Success' if data['success'] else 'Failure'}</td>
                    <td>{data['runtime']:.2f}</td>
                    <td>{len(data['timings'])}</td>
                </tr>
        """
    
    html += """
            </table>
        </div>
        
        <div class="chart-container">
            <canvas id="runtimeChart"></canvas>
        </div>
    """
    
    # Add component details
    for component, data in report["components"].items():
        if not data["success"]:
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
        for test, timing in data["timings"].items():
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
    
    # Add charts
    html += """
        <script>
            // Runtime chart
            const runtimeCtx = document.getElementById('runtimeChart').getContext('2d');
            const runtimeChart = new Chart(runtimeCtx, {
                type: 'bar',
                data: {
                    labels: [""" + ", ".join([f"'{component}'" for component in report["components"].keys()]) + """],
                    datasets: [{
                        label: 'Runtime (s)',
                        data: [""" + ", ".join([f"{data['runtime']:.2f}" for data in report["components"].values()]) + """],
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
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Component'
                            }
                        }
                    }
                }
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