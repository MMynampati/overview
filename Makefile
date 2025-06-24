.PHONY: help setup install test run docker-build docker-run clean conda-create conda-activate conda-remove

help: ## Show this help message
	@echo "Manual Pages Search Interface - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

conda-create: ## Create conda environment
	conda env create -f environment.yml

conda-activate: ## Activate conda environment
	@echo "Run: conda activate manual-search"

conda-remove: ## Remove conda environment
	conda env remove -n manual-search

conda-update: ## Update conda environment
	conda env update -f environment.yml

setup: ## Initial setup - create .env file and check dependencies
	python setup.py

install: ## Install Python dependencies (for pip/venv)
	pip install -r requirements.txt

test: ## Run tests to verify setup
	python test_setup.py

run: ## Run the Streamlit application locally
	streamlit run app.py

docker-build: ## Build Docker image
	docker-compose build

docker-run: ## Run with Docker Compose
	docker-compose up

docker-stop: ## Stop Docker containers
	docker-compose down

docker-clean: ## Stop and remove Docker containers and images
	docker-compose down --rmi all --volumes --remove-orphans

clean: ## Clean up generated files
	rm -rf data/
	rm -rf __pycache__/
	rm -rf .streamlit/
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

dev-setup: setup install ## Complete development setup (pip/venv)
	@echo "Development environment ready!"

conda-dev-setup: conda-create setup ## Complete development setup (conda)
	@echo "Conda development environment ready!"
	@echo "Run: conda activate manual-search"

prod-setup: setup install test ## Complete production setup with tests
	@echo "Production environment ready!" 