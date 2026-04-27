#############################################
# ███████╗██╗     ██╗   ██╗    ██╗███╗   ██╗
# ██╔════╝██║     ╚██╗ ██╔╝    ██║████╗  ██║
# █████╗  ██║      ╚████╔╝     ██║██╔██╗ ██║
# ██╔══╝  ██║       ╚██╔╝      ██║██║╚██╗██║
# ██║     ███████╗   ██║       ██║██║ ╚████║
# ╚═╝     ╚══════╝   ╚═╝       ╚═╝╚═╝  ╚═══╝
#############################################

# Variables
PYTHON = python3
PIP = pip3
SRC = .
MAIN = main.py
ENV = venv
BIN = $(ENV)/bin/python

# Terminal Colors
GREEN = \033[0;32m
RED = \033[0;31m
RESET = \033[0m
NC = \033[0m

.PHONY: all install run debug clean lint re

all: install lint

# Virtual environment setup and dependency installation
install:
	@echo "$(GREEN)Setting up virtual environment and dependencies...$(NC)"
	$(PYTHON) -m venv $(ENV)
	$(ENV)/bin/$(PIP) install --upgrade pip
	$(ENV)/bin/$(PIP) install flake8 mypy matplotlib

# Main program execution
# Usage: make run MAP=maps/easy_map.txt
run:
	$(BIN) $(MAIN) $(MAP)

# Debug mode (specific flags can be added here)
debug:
	@echo "$(GREEN)Running in debug mode...$(NC)"
	$(BIN) $(MAIN) $(MAP) --debug

# Code quality verification (Mandatory per subject/requirements)
lint:
	@echo "$(GREEN)Running Flake8 check...$(NC)"
	$(ENV)/bin/flake8 .  --exclude=venv,test_env,env,.venv
	@echo "$(GREEN)Running Mypy type check...$(NC)"
	$(ENV)/bin/mypy $(SRC) --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	@echo "$(GREEN)Running Flake8 strict...$(NC)"
	$(ENV)/bin/flake8 . --exclude=venv
	@echo "$(GREEN)Running Mypy strict...$(NC)"
	$(ENV)/bin/mypy . --strict --exclude venv

# Cleanup of temporary files and cache
clean:
	@echo "$(GREEN)Cleaning up...$(NC)"
	rm -rf $(ENV)
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Re-install everything from scratch
re: clean all

.PHONY: all install run debug clean lint lint-strict re
