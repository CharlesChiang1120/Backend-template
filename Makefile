# Define phony targets to avoid conflict with file names
.PHONY: install run test lint clean

# Install dependencies using Poetry
install:
	pip install poetry && poetry install

# Start the FastAPI server with hot-reload enabled
# Binding to 0.0.0.0 is essential for Docker and remote factory server access
run:
	poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Execute all automated tests using Pytest
test:
	PYTHONPATH=. poetry run pytest -v

# Enforce coding standards (Linting)
# Black handles formatting, iSort organizes imports to maintain global consistency
lint:
	poetry run black . && poetry run isort .

# Clean up temporary Python files and cache
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache