#!/bin/bash
set -e

echo "Running comprehensive security scan..."

# Create reports directory
mkdir -p security-reports

# Bandit - Python security linter
echo "Running Bandit security analysis..."
bandit -r app/ -f json -o security-reports/bandit-report.json || true
bandit -r app/ -f html -o security-reports/bandit-report.html || true

# Safety - Check for known security vulnerabilities in dependencies
echo "Checking for vulnerable dependencies..."
safety check --json --output security-reports/safety-report.json || true

# OWASP Dependency Check
echo "Running OWASP Dependency Check..."
dependency-check --project "Threat Detection System" \
                 --scan . \
                 --format JSON \
                 --format HTML \
                 --out security-reports/dependency-check || true

# Docker image scanning with Trivy
echo "Scanning Docker image for vulnerabilities..."
docker build -t threat-detection-system:latest -f docker/Dockerfile .
trivy image --format json --output security-reports/trivy-report.json threat-detection-system:latest || true

echo "Security scan completed. Reports saved in security-reports/"

# Parse and summarize results
python << EOF
import json
import os

reports_dir = "security-reports"
summary = {"bandit": 0, "safety": 0, "trivy": 0}

# Parse Bandit report
try:
    with open(f"{reports_dir}/bandit-report.json", "r") as f:
        bandit_data = json.load(f)
        summary["bandit"] = len(bandit_data.get("results", []))
        print(f"Bandit found {summary['bandit']} security issues")
except:
    print("Bandit report not found")

# Parse Safety report
try:
    with open(f"{reports_dir}/safety-report.json", "r") as f:
        safety_data = json.load(f)
        summary["safety"] = len(safety_data)
        print(f"Safety found {summary['safety']} vulnerable dependencies")
except:
    print("Safety report not found")

# Parse Trivy report
try:
    with open(f"{reports_dir}/trivy-report.json", "r") as f:
        trivy_data = json.load(f)
        vulns = 0
        for result in trivy_data.get("Results", []):
            vulns += len(result.get("Vulnerabilities", []))
        summary["trivy"] = vulns
        print(f"Trivy found {summary['trivy']} container vulnerabilities")
except:
    print("Trivy report not found")

total_issues = sum(summary.values())
print(f"\nTotal security issues found: {total_issues}")

if total_issues > 0:
    print("Please review security reports and address critical issues before deployment.")
    exit(1)
else:
    print("No critical security issues found!")
EOF
