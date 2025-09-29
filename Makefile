.PHONY: help install install-dev test test-cov lint format security clean build docs serve-docs
.DEFAULT_GOAL := help

PYTHON := python
PIP := pip
PYTEST := pytest
PACKAGE_NAME := log_analyzer

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install package dependencies
	$(PIP) install -r requirements.txt

install-dev: ## Install development dependencies
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-dev.txt
	pre-commit install

test: ## Run tests
	$(PYTEST) tests/ -v

test-cov: ## Run tests with coverage
	$(PYTEST) tests/ -v --cov=src --cov-report=term-missing --cov-report=html

test-fast: ## Run tests in parallel
	$(PYTEST) tests/ -v -n auto

lint: ## Run all linting tools
	black --check src/ tests/
	isort --check-only src/ tests/
	flake8 src/ tests/
	mypy src/

format: ## Format code with black and isort
	black src/ tests/
	isort src/ tests/

security: ## Run security checks
	bandit -r src/
	safety check
	pip-audit

quality: ## Run all quality checks
	make lint
	make security
	make test-cov

# API related commands
api-dev: ## Start API server in development mode
	$(PYTHON) run_api.py --reload --debug

api-prod: ## Start API server in production mode
	$(PYTHON) run_api.py --prod --host 0.0.0.0

api-test: ## Test API endpoints
	$(PYTHON) examples/api_client_example.py --test-status

api-demo: ## Create sample data and run API demo
	$(PYTHON) examples/api_client_example.py --create-samples
	$(PYTHON) examples/api_client_example.py --analyze data/sample_firewall.csv data/sample_auth.csv

api-info: ## Show API information
	$(PYTHON) examples/api_client_example.py --info

api-install: ## Install API dependencies
	$(PIP) install fastapi uvicorn[standard] requests

api-docs: ## Open API documentation in browser
	@echo "API Documentation available at:"
	@echo "  Swagger UI: http://127.0.0.1:8000/docs"
	@echo "  ReDoc:      http://127.0.0.1:8000/redoc"

pre-commit: ## Run pre-commit hooks
	pre-commit run --all-files

clean: ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	rm -rf .tox/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build: ## Build package
	$(PYTHON) -m build

build-check: ## Build and check package
	make build
	twine check dist/*

docs: ## Build documentation
	sphinx-build -b html docs/ docs/_build/html

serve-docs: ## Serve documentation locally
	cd docs/_build/html && $(PYTHON) -m http.server 8000

release-test: ## Test release process
	make clean
	make quality
	make build-check

dev-setup: ## Complete development setup
	make install-dev
	make pre-commit
	@echo "Development environment setup complete!"
	@echo "Run 'make test' to verify everything works."

ci: ## Run CI pipeline locally
	make clean
	make quality
	make test-cov
	make build-check

# Docker targets
docker-build: ## Build Docker image
	docker build -t log-analyzer:latest .

docker-test: ## Run tests in Docker
	docker run --rm log-analyzer:latest make test

# Maintenance targets
update-deps: ## Update dependencies
	$(PIP) install --upgrade pip
	$(PIP) install --upgrade -r requirements.txt
	$(PIP) install --upgrade -r requirements-dev.txt

check-deps: ## Check for security vulnerabilities in dependencies
	safety check
	pip-audit

bump-version: ## Bump version (requires VERSION=x.y.z)
	@if [ -z "$(VERSION)" ]; then echo "Usage: make bump-version VERSION=x.y.z"; exit 1; fi
	sed -i 's/version = ".*"/version = "$(VERSION)"/' pyproject.toml
	@echo "Version bumped to $(VERSION)"