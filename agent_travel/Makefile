SHELL := /bin/bash

.PHONY: install run clean test

install:
	@echo "Creating virtual environment and installing dependencies..."
	@uv venv
	@uv pip install -r requirements.txt
	@echo "Installation complete."

run:
	@echo "Starting the Streamlit application..."
	@uv run streamlit run streamlit_app.py

test:
	@echo "Running all tests..."
	@uv run python evaluate_csv.py
	@uv run python test_generate_csv_itinerary.py

clean:
	@echo "Removing virtual environment..."
	@rm -rf .venv
	@echo "Clean complete."
