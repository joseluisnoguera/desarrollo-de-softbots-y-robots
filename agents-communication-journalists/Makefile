# Makefile for Journalists Discussion Application

# Variables
PYTHON = python3
VENV_PATH = venv
PIP = $(VENV_PATH)/bin/pip
PYTHON_VENV = $(VENV_PATH)/bin/python
STREAMLIT = $(VENV_PATH)/bin/streamlit

# Default target
.PHONY: help
help:
	@echo "Available commands:"
	@echo "  setup      - Create virtual environment and install dependencies"
	@echo "  install    - Install dependencies"
	@echo "  local      - Run the application locally"
	@echo "  test       - Run tests"
	@echo "  lint       - Run linting (ruff)"
	@echo "  format     - Format code (black + isort)"
	@echo "  type-check - Run type checking (mypy)"
	@echo "  clean      - Clean up generated files"
	@echo "  dev        - Setup development environment"

# Setup virtual environment
.PHONY: setup
setup:
	$(PYTHON) -m venv $(VENV_PATH)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

# Install dependencies
.PHONY: install
install:
	$(PIP) install -r requirements.txt

# Run the application locally
.PHONY: local
local:
	$(STREAMLIT) run Home.py --server.port=8502 --server.address=0.0.0.0

# Run tests
.PHONY: test
test:
	$(PYTHON_VENV) -m pytest tests/ -v

# Run tests with coverage
.PHONY: test-cov
test-cov:
	$(PYTHON_VENV) -m pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

# Run linting
.PHONY: lint
lint:
	$(PYTHON_VENV) -m ruff check src/ pages/ Home.py tests/

# Fix linting issues
.PHONY: lint-fix
lint-fix:
	$(PYTHON_VENV) -m ruff check --fix src/ pages/ Home.py tests/

# Format code
.PHONY: format
format:
	$(PYTHON_VENV) -m black src/ pages/ Home.py tests/
	$(PYTHON_VENV) -m isort src/ pages/ Home.py tests/

# Run type checking
.PHONY: type-check
type-check:
	$(PYTHON_VENV) -m mypy src/

# Run all quality checks
.PHONY: quality
quality: lint type-check test

# Development setup
.PHONY: dev
dev: setup
	@echo "Development environment setup complete!"
	@echo "Run 'make local' to start the application"

# Clean up
.PHONY: clean
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -rf .coverage

# Docker commands (optional)
.PHONY: docker-build
docker-build:
	docker build -t journalists-discussion .

.PHONY: docker-run
docker-run:
	docker run -p 8502:8502 journalists-discussion