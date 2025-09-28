# Makefile for Ticket-Master project
# AI-powered GitHub issue generator

.PHONY: help install setup test lint format format-check clean dev-install venv docker docker-build docker-run docker-dev docker-shell docker-clean

# Default target
.DEFAULT_GOAL := help

# Python and pip commands
PYTHON := python3
PIP := pip3
PYTEST := python -m pytest
FLAKE8 := flake8
BLACK := black
MYPY := mypy

# Project directories
SRC_DIR := src
TEST_DIR := tests
MAIN_FILE := main.py

# Virtual environment
VENV_DIR := venv
VENV_ACTIVATE := $(VENV_DIR)/bin/activate

# Docker configuration
DOCKER_IMAGE := ticket-master
DOCKER_TAG := latest
DOCKER_CONTAINER := ticket-master
COMPOSE_FILE := docker-compose.yml

help: ## Show this help message
	@echo "Ticket-Master - AI-powered GitHub issue generator"
	@echo ""
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install Python dependencies
	@echo "Installing Python dependencies..."
	$(PIP) install -r requirements.txt || echo "Note: Some dependencies may already be installed or there was a network timeout"
	@echo "Dependencies installation complete!"

dev-install: install ## Install development dependencies (same as install since all deps are in requirements.txt)
	@echo "Development dependencies already included in requirements.txt"

setup: install config ## One-command setup: install dependencies and copy config
	@echo "Setup complete! You can now run the application."
	@echo "Don't forget to set your GITHUB_TOKEN environment variable."

config: ## Copy example configuration file
	@if [ ! -f config.yaml ]; then \
		echo "Copying config.yaml.example to config.yaml..."; \
		cp config.yaml.example config.yaml; \
		echo "Config file created. Please edit config.yaml as needed."; \
	else \
		echo "config.yaml already exists. Skipping copy."; \
	fi

test: ## Run tests with pytest
	@echo "Running tests..."
	$(PYTEST) -v --cov=$(SRC_DIR) --cov-report=term-missing
	@echo "Tests completed!"

test-fast: ## Run tests without coverage
	@echo "Running tests (fast mode)..."
	$(PYTEST) -v
	@echo "Tests completed!"

lint: ## Run linting with flake8
	@echo "Running linting checks..."
	$(FLAKE8) $(SRC_DIR)/ $(MAIN_FILE) --max-line-length=88 --ignore=E203,W503,E402
	@echo "Linting completed!"

typecheck: ## Run type checking with mypy
	@echo "Running type checks..."
	$(MYPY) $(SRC_DIR)/ $(MAIN_FILE)
	@echo "Type checking completed!"

format: ## Format code with black
	@echo "Formatting code with black..."
	$(BLACK) $(SRC_DIR)/ $(MAIN_FILE)
	@echo "Code formatting completed!"

format-check: ## Check if code needs formatting
	@echo "Checking code formatting..."
	$(BLACK) --check $(SRC_DIR)/ $(MAIN_FILE)
	@echo "Format check completed!"

check: format-check lint typecheck test ## Run all checks (format, lint, typecheck, test)
	@echo "All checks completed successfully!"

clean: ## Clean build artifacts and cache files
	@echo "Cleaning build artifacts and cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache/ 2>/dev/null || true
	rm -rf .coverage 2>/dev/null || true
	rm -rf htmlcov/ 2>/dev/null || true
	rm -rf dist/ 2>/dev/null || true
	rm -rf build/ 2>/dev/null || true
	@echo "Cleanup completed!"

venv: ## Create virtual environment
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv $(VENV_DIR)
	@echo "Virtual environment created in $(VENV_DIR)/"
	@echo "Activate it with: source $(VENV_ACTIVATE)"

venv-install: venv ## Create virtual environment and install dependencies
	@echo "Installing dependencies in virtual environment..."
	. $(VENV_ACTIVATE) && pip install -r requirements.txt
	@echo "Virtual environment setup completed!"
	@echo "Activate it with: source $(VENV_ACTIVATE)"

run-help: ## Show application help
	@echo "Running application help..."
	$(PYTHON) $(MAIN_FILE) --help

run-example: ## Run example command (dry run)
	@echo "Running example command (requires GITHUB_TOKEN environment variable):"
	@echo "python main.py . dhodgson615/Ticket-Master --dry-run"
	@if [ -z "$$GITHUB_TOKEN" ]; then \
		echo "Warning: GITHUB_TOKEN environment variable is not set!"; \
		echo "Set it with: export GITHUB_TOKEN='your_token_here'"; \
	else \
		$(PYTHON) $(MAIN_FILE) . dhodgson615/Ticket-Master --dry-run; \
	fi

build: setup ## Alias for setup (build the project)
	@echo "Project built successfully!"

all: clean setup check ## Clean, setup, and run all checks
	@echo "Full build and check completed successfully!"

# Development shortcuts
dev: setup ## Setup development environment
	@echo "Development environment ready!"

# Docker targets
docker-build: ## Build Docker image
	@echo "Building Docker image..."
	docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) .
	@echo "Docker image built successfully!"

docker-run: docker-build ## Build and run Docker container (shows help by default)
	@echo "Running Docker container..."
	docker run --rm --name $(DOCKER_CONTAINER) $(DOCKER_IMAGE):$(DOCKER_TAG)

docker-shell: docker-build ## Build and run Docker container with interactive shell
	@echo "Starting Docker container with shell..."
	docker run -it --rm --name $(DOCKER_CONTAINER) \
		-e GITHUB_TOKEN="$$GITHUB_TOKEN" \
		-v "$(PWD):/workspace:ro" \
		$(DOCKER_IMAGE):$(DOCKER_TAG) /bin/bash

docker-dev: ## Start development environment with Docker Compose
	@echo "Starting development environment with Docker Compose..."
	@if [ -z "$$GITHUB_TOKEN" ]; then \
		echo "Warning: GITHUB_TOKEN environment variable is not set!"; \
		echo "Set it with: export GITHUB_TOKEN='your_token_here'"; \
	fi
	docker compose -f $(COMPOSE_FILE) up -d ticket-master-dev
	@echo "Development container started. Use 'docker compose exec ticket-master-dev bash' to access."

docker-stop: ## Stop Docker Compose services
	@echo "Stopping Docker Compose services..."
	docker compose -f $(COMPOSE_FILE) down

docker-clean: ## Clean Docker images and containers
	@echo "Cleaning Docker resources..."
	-docker compose -f $(COMPOSE_FILE) down --volumes --remove-orphans
	-docker rmi $(DOCKER_IMAGE):$(DOCKER_TAG) 2>/dev/null || true
	@echo "Docker cleanup completed!"

docker: docker-build ## Alias for docker-build

ci: install format-check lint typecheck test ## CI pipeline: install, format-check, lint, typecheck, test
	@echo "CI pipeline completed successfully!"