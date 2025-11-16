.PHONY: help install test clean docker-build docker-test docker-up-http docker-up-sse docker-up-stdio docker-down docker-logs server uv-sync uv-install uv-examples uv-example

# Default target
help:
	@echo "pyResToolbox MCP Server - Makefile Commands"
	@echo "============================================"
	@echo ""
	@echo "UV Environment (Recommended):"
	@echo "  make uv-install      - Create venv and install with uv"
	@echo "  make uv-sync         - Sync dependencies with uv"
	@echo "  make uv-server       - Run server with uv"
	@echo "  make uv-test         - Run tests with uv"
	@echo "  make uv-examples     - Run all examples with uv"
	@echo "  make uv-example      - Run a specific example (use EXAMPLE=filename.py)"
	@echo ""
	@echo "Local Development (pip):"
	@echo "  make install         - Install package in development mode"
	@echo "  make test            - Run tests"
	@echo "  make server          - Run MCP server locally (STDIO)"
	@echo "  make clean           - Clean build artifacts"
	@echo ""
	@echo "Docker Operations:"
	@echo "  make docker-build    - Build Docker image"
	@echo "  make docker-test     - Build and test Docker image"
	@echo "  make docker-up-http  - Start HTTP server (port 8000)"
	@echo "  make docker-up-sse   - Start SSE server (port 8001)"
	@echo "  make docker-up-stdio - Start STDIO server"
	@echo "  make docker-down     - Stop all Docker services"
	@echo "  make docker-logs     - View Docker logs"
	@echo ""

# UV environment (recommended)
uv-install:
	uv venv
	uv sync
	@echo "UV environment created. Activate with: source .venv/bin/activate"

uv-sync:
	uv sync

uv-server:
	uv run fastmcp run server.py

uv-test:
	uv run python test_server.py

uv-examples:
	@echo "Running all examples..."
	@cd examples && for example in *.py; do \
		if [ "$$example" != "__init__.py" ]; then \
			echo ""; \
			echo "=========================================="; \
			echo "Running $$example..."; \
			echo "=========================================="; \
			uv run python "$$example" || true; \
		fi; \
	done

uv-example:
	@if [ -z "$(EXAMPLE)" ]; then \
		echo "Usage: make uv-example EXAMPLE=basic_usage.py"; \
		exit 1; \
	fi
	@cd examples && uv run python $(EXAMPLE)

# Local development (pip)
install:
	pip install -e .

test:
	python test_server.py
	@echo "To run pytest tests: pytest"

server:
	fastmcp run server.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .pytest_cache/ .coverage htmlcov/ .venv/

# Docker operations
docker-build:
	docker build -t pyrestoolbox-mcp:latest .

docker-test: docker-build
	@echo "Running Docker build and test..."
	@./docker-build-test.sh

docker-up-http:
	docker-compose --profile http up -d
	@echo "HTTP server started on http://localhost:8000"

docker-up-sse:
	docker-compose --profile sse up -d
	@echo "SSE server started on http://localhost:8001"

docker-up-stdio:
	docker-compose --profile stdio up -d
	@echo "STDIO server started (use: docker exec -it pyrestoolbox-mcp-stdio bash)"

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-restart-http:
	docker-compose restart pyrestoolbox-mcp-http

docker-restart-sse:
	docker-compose restart pyrestoolbox-mcp-sse

docker-clean:
	docker-compose down -v
	docker rmi pyrestoolbox-mcp:latest || true
	docker system prune -f

# Combined targets
all: install test

docker-all: docker-build docker-test docker-up-http
