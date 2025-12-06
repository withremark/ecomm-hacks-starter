.PHONY: help serve serve-frontend serve-backend build kill dev restart test

# Show available commands (default target)
help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Production (no hot reload):"
	@echo "  serve          Build frontend, run both servers (backend :8000, frontend :4173)"
	@echo "  serve-backend  Run only backend"
	@echo "  serve-frontend Build and run only frontend preview"
	@echo ""
	@echo "Development (with hot reload):"
	@echo "  dev            Run both servers with hot reloading"
	@echo ""
	@echo "Testing:"
	@echo "  test           Run e2e image generation test"
	@echo "  test-headed    Run test with visible browser"
	@echo ""
	@echo "Utilities:"
	@echo "  build          Build frontend for production"
	@echo "  kill           Kill all running servers"
	@echo "  restart        Kill servers and restart (kill + serve)"
	@echo "  help           Show this help message"

# Run both frontend and backend without hot reloading
serve: build
	@echo "Starting backend on :8000 and frontend on :4173..."
	@cd backend && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 & \
	npm run preview

# Build frontend for production
build:
	npm run build

# Run just the backend (no hot reload)
serve-backend:
	cd backend && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000

# Run just the frontend preview server
serve-frontend: build
	npm run preview

# Development mode (with hot reloading)
dev:
	@echo "Starting backend on :8000 and frontend on :5173 (dev mode)..."
	@cd backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 & \
	npm run dev

# Kill any running servers
kill:
	@echo "Killing servers on ports 8000 and 4173/5173..."
	@-pkill -f "uvicorn app.main:app" 2>/dev/null || true
	@-lsof -ti :4173 | xargs kill 2>/dev/null || true
	@-lsof -ti :5173 | xargs kill 2>/dev/null || true
	@echo "Done."

# Restart servers (kill + serve)
restart: kill serve

# Run e2e test (headless)
test:
	python test_image_e2e.py

# Run e2e test with visible browser
test-headed:
	HEADED=1 python test_image_e2e.py
