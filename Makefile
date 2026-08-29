VENV := .venv
PIP  := $(VENV)/bin/pip

.PHONY: install clean venv

# Clean caches/build artifacts, then do a fresh editable install.
# Installs pytest directly instead of via [test] extra, as mathema isn't available yet.
install: clean venv
	$(PIP) install --no-cache-dir --force-reinstall -e .
	$(PIP) install "pytest>=7.0"

# Remove tool caches, bytecode, and build artifacts.
clean:
	find . -type d -name "__pycache__" -not -path "./$(VENV)/*" -exec rm -rf {} +
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	rm -rf build dist *.egg-info

# Create the venv only if it doesn't exist yet.
venv:
	test -d $(VENV) || python3 -m venv $(VENV)
