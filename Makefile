# Makefile to manage tasks for the project

# Name of the conda environment
ENVNAME := arcpy-hpms

# Directory containing the scripts
SCRIPTDIR := scripts

# Path to the python executable
PYTHON := python

# File name of the requirements
REQUIREMENTS := requirements.txt

# Python scripts to run
SCRIPT1 := download_raw_data.py
SCRIPT2 := clean_data.py
SCRIPT3 := subset_addt.py

.PHONY: check-env install-packages run-scripts

all: check-env install-packages run-scripts

check-env:
	@if [ "${CONDA_DEFAULT_ENV}" != "$(ENVNAME)" ]; then \
		echo "Conda environment $(ENVNAME) is not activated."; \
		exit 1; \
	else \
		echo "Conda environment $(ENVNAME) is activated."; \
	fi

install-packages:
	@echo "Installing packages from $(REQUIREMENTS)..."
	@pip install -r $(REQUIREMENTS)

run-scripts:
	@echo "Running scripts in $(SCRIPTDIR)..."
	@cd $(SCRIPTDIR) && $(PYTHON) $(SCRIPT1)
	@cd $(SCRIPTDIR) && $(PYTHON) $(SCRIPT2)
	@cd $(SCRIPTDIR) && $(PYTHON) $(SCRIPT3)
