#!/bin/bash
set -e

echo "Running all tests for Threat Detection System..."

# Setup virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run unit tests
echo "Running unit tests..."
python -m pytest tests/ -v --cov=app --cov-report=html --cov-report=xml

# Run integration tests
echo "Running integration tests..."
python -m pytest integration_tests/ -v

# Run security checks
echo "Running security analysis..."
bandit -r app/ -f json -o bandit-report.json || true

# Run code quality checks
echo "Running code quality checks..."
flake8 app/ --max-line-length=100 --exclude=__pycache__ || true

echo "All tests completed!"
