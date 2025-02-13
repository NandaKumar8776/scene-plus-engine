"""
Script to run tests and generate coverage reports.
"""
import subprocess
import sys
import os
from datetime import datetime
import json


def run_tests(test_path: str = "tests", markers: list = None) -> bool:
    """
    Run pytest with specified markers and generate coverage reports.
    
    Args:
        test_path: Path to test directory
        markers: List of test markers to run
        
    Returns:
        bool: True if all tests passed
    """
    # Build pytest command
    cmd = ["pytest", test_path]
    
    if markers:
        marker_expr = " or ".join(markers)
        cmd.extend(["-m", marker_expr])
    
    # Add coverage options
    cmd.extend([
        "--cov=src",
        "--cov-report=term-missing",
        "--cov-report=html",
        "--cov-report=json"
    ])
    
    # Run tests
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Print output
    print(result.stdout)
    if result.stderr:
        print("Errors:", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
    
    return result.returncode == 0


def generate_test_report(output_file: str = "test_report.json"):
    """Generate a comprehensive test report."""
    try:
        # Read coverage data
        with open("coverage.json") as f:
            coverage_data = json.load(f)
        
        # Generate report
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_statements": coverage_data["totals"]["total_statements"],
                "covered_statements": coverage_data["totals"]["covered_statements"],
                "coverage_percent": coverage_data["totals"]["percent_covered"],
                "missing_statements": coverage_data["totals"]["missing_statements"]
            },
            "files": {}
        }
        
        # Add per-file metrics
        for file_path, metrics in coverage_data["files"].items():
            report["files"][file_path] = {
                "coverage_percent": metrics["summary"]["percent_covered"],
                "missing_lines": metrics["missing_lines"],
                "excluded_lines": metrics["excluded_lines"]
            }
        
        # Save report
        with open(output_file, "w") as f:
            json.dump(report, f, indent=2)
            
        print(f"\nTest report saved to {output_file}")
        
        # Print summary
        print("\nTest Coverage Summary:")
        print(f"Total Statements: {report['summary']['total_statements']}")
        print(f"Covered Statements: {report['summary']['covered_statements']}")
        print(f"Coverage: {report['summary']['coverage_percent']:.2f}%")
        print(f"Missing Statements: {report['summary']['missing_statements']}")
        
    except Exception as e:
        print(f"Error generating test report: {e}", file=sys.stderr)


def main():
    """Run tests and generate reports."""
    try:
        # Define test markers
        all_markers = ["unit", "integration", "api", "models", "monitoring"]
        
        # Run tests with all markers
        print("Running all tests...")
        success = run_tests(markers=all_markers)
        
        if success:
            print("\nAll tests passed!")
            generate_test_report()
        else:
            print("\nSome tests failed!", file=sys.stderr)
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nTest run interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error running tests: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main() 