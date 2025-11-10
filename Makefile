.PHONY: help setup test lint format build-demo clean install-system-deps

help:
	@echo "ExamKit - Makefile Commands"
	@echo "=============================="
	@echo "setup                - Install Python dependencies and spaCy model"
	@echo "install-system-deps  - Show instructions for installing system dependencies"
	@echo "test                 - Run pytest with coverage"
	@echo "lint                 - Run ruff linter"
	@echo "format               - Format code with black"
	@echo "build-demo           - Run demo pipeline with sample data"
	@echo "clean                - Remove cache, logs, and build artifacts"

setup:
	@echo "Installing Python dependencies..."
	poetry install
	@echo "Installing spaCy model..."
	poetry run python -m spacy download en_core_web_sm
	@echo "Setup complete!"

install-system-deps:
	@echo "System Dependencies (macOS):"
	@echo "=============================="
	@echo "1. Install Homebrew (if not already installed):"
	@echo "   /bin/bash -c \"\$$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
	@echo ""
	@echo "2. Install system packages:"
	@echo "   brew install ffmpeg tesseract graphviz typst"
	@echo ""
	@echo "3. Install Ollama:"
	@echo "   brew install ollama"
	@echo "   ollama serve &"
	@echo "   ollama pull llama3.2:8b"
	@echo ""
	@echo "4. Run 'make setup' to install Python dependencies"

test:
	poetry run pytest -v --cov=examkit --cov-report=term-missing

lint:
	poetry run ruff check examkit/ tests/

format:
	poetry run black examkit/ tests/

build-demo:
	@echo "Building demo with sample data..."
	mkdir -p out cache logs
	poetry run examkit ingest --manifest input/sample/manifest.json
	poetry run examkit build --config config/config.yml --out out/demo.pdf --offline
	poetry run examkit report --session demo
	@echo "Demo build complete! Check out/demo.pdf"

clean:
	rm -rf out/ cache/ logs/
	rm -rf .pytest_cache/ .coverage htmlcov/
	rm -rf .mypy_cache/ .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "Cleanup complete!"
