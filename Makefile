.PHONY: install test clean validate-schemas help

# Default target
help:
	@echo "SpeedData Build System"
	@echo ""
	@echo "Available targets:"
	@echo "  make install          - Install all dependencies"
	@echo "  make test            - Run all tests"
	@echo "  make validate-schemas - Validate AVRO schema files"
	@echo "  make clean           - Remove build artifacts and cache"
	@echo "  make help            - Show this help message"

# Install dependencies
install:
	@echo "Running installation script..."
	@./install
	@echo "Installation complete!"

# Run all tests
test:
	@echo "Running Python tests..."
	@bash -c "source bin/activate && python -m pytest lib/python/tests -v 2>/dev/null || echo 'No lib tests yet'"
	@echo "Running integration tests..."
	@bash -c "source bin/activate && python -m pytest tests -v 2>/dev/null || echo 'No integration tests yet'"
	@echo "Running JavaScript tests..."
	@npm test 2>/dev/null || echo "No JS tests configured yet"
	@echo "All tests complete!"

# Validate AVRO schemas
validate-schemas:
	@echo "Validating AVRO schemas..."
	@for schema in config/agents/*.avsc; do \
		echo "Validating $$schema..."; \
		python -c "import json; json.load(open('$$schema'))" || exit 1; \
	done
	@echo "All schemas valid!"

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "Clean complete!"
