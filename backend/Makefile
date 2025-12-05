.PHONY: serve kill restart install test lint

# Backend port
PORT ?= 8000

serve:
	@echo "Starting Gemini backend on port $(PORT)..."
	cd $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST)))) && \
	uv run uvicorn app.main:app --host 0.0.0.0 --port $(PORT) &
	@echo "Backend started. Use 'make kill' to stop."

serve-reload:
	@echo "Starting Gemini backend with reload on port $(PORT)..."
	cd $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST)))) && \
	uv run uvicorn app.main:app --host 0.0.0.0 --port $(PORT) --reload

kill:
	@echo "Stopping backend server..."
	@-pkill -f "uvicorn app.main:app" 2>/dev/null || true
	@echo "Backend stopped."

restart: kill serve
	@echo "Backend restarted."

install:
	@echo "Installing dependencies with uv..."
	cd $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST)))) && \
	uv sync
	@echo "Dependencies installed."

test:
	@echo "Running tests..."
	cd $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST)))) && \
	uv run pytest -v
	@echo "Tests complete."

lint:
	@echo "Running linter..."
	cd $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST)))) && \
	uv run ruff check .
	@echo "Linting complete."

format:
	@echo "Formatting code..."
	cd $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST)))) && \
	uv run ruff format .
	@echo "Formatting complete."
