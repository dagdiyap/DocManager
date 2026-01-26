SHELL := /bin/bash

.PHONY: help install install-dev clean test lint format build

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install all dependencies
	@echo "Installing License Server..."
	cd license_server && pip install -e .
	cd license_server/ui && npm ci
	@echo "Installing CA Desktop Backend..."
	cd ca_desktop/backend && pip install -e .
	@echo "Installing CA Desktop Frontend..."
	cd ca_desktop/frontend && npm ci
	@echo "Installing shared..."
	cd shared && pip install -e .

install-dev:  ## Install all dev dependencies
	@echo "Installing dev dependencies..."
	cd license_server && pip install -e .[dev]
	cd ca_desktop/backend && pip install -e .[dev]
	cd shared && pip install -e .[dev]
	pre-commit install

clean:  ## Clean build artifacts and cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true

test:  ## Run all tests
	@echo "Running License Server tests..."
	cd license_server && pytest
	@echo "Running CA Desktop Backend tests..."
	cd ca_desktop/backend && pytest
	@echo "Running CA Desktop Frontend tests..."
	cd ca_desktop/frontend && npm test
	@echo "Running integration tests..."
	cd tests && pytest integration/

lint:  ## Run linters
	@echo "Linting Python code..."
	ruff check .
	black --check .
	@echo "Linting TypeScript code..."
	cd license_server/ui && npm run lint
	cd ca_desktop/frontend && npm run lint

format:  ## Format code
	@echo "Formatting Python code..."
	black .
	ruff check --fix .
	@echo "Formatting TypeScript code..."
	cd license_server/ui && npm run format
	cd ca_desktop/frontend && npm run format

docker-up:  ## Start License Server with Docker
	cd license_server && docker-compose up -d

docker-down:  ## Stop License Server Docker containers
	cd license_server && docker-compose down

docker-logs:  ## View License Server logs
	cd license_server && docker-compose logs -f

build-installer:  ## Build Windows installer
	@echo "Building installer..."
	cd installer && python scripts/build.py

.DEFAULT_GOAL := help
