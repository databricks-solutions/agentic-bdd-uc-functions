# Compliance BDD — command interface.
#
# Prerequisites: uv, Databricks CLI, a .env file (see .env.example).
#
# Typical first-time setup:
#   make install
#   make setup
#   make test

include .env
export

.PHONY: help install setup test validate deploy-dev deploy-staging clean

help:
	@echo "Local development:"
	@echo "  install        install Python dependencies (uv sync)"
	@echo "  setup          deploy the UC SQL function to BDD_CATALOG.BDD_SCHEMA"
	@echo "  test           run the BDD suite"
	@echo ""
	@echo "Bundle operations:"
	@echo "  validate       databricks bundle validate"
	@echo "  deploy-dev     databricks bundle deploy --target dev"
	@echo "  deploy-staging databricks bundle deploy --target staging"
	@echo ""
	@echo "Utilities:"
	@echo "  clean          drop BDD_SCHEMA and remove generated artifacts"

install:
	uv sync

setup: install
	uv run python -m scripts.deploy_function

test:
	uv run behave

validate:
	databricks bundle validate

deploy-dev:
	databricks bundle deploy --target dev

deploy-staging:
	databricks bundle deploy --target staging

clean:
	databricks sql execute \
		--warehouse-id $(DATABRICKS_WAREHOUSE_ID) \
		"DROP SCHEMA IF EXISTS $(BDD_CATALOG).$(BDD_SCHEMA) CASCADE"
	@echo "Dropped $(BDD_CATALOG).$(BDD_SCHEMA)"
