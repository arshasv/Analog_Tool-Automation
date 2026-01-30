# ============================================================================
# AI-Driven Sky130 ASIC Platform - Makefile
# ============================================================================

# Automation Targets
automate:
	@echo "~~~~Starting Fully Automated EDA~~~~"
	@docker exec -it sky130_eda bash -c "PYTHONPATH=/home/eda python3 /home/eda/circuits/library/custom/runner.py"

optimize:
	@echo "~~~~Starting AI Design Agent (Closed Loop)~~~~"
	@docker exec -it sky130_eda bash -c "PYTHONPATH=/home/eda python3 /home/eda/circuits/library/custom/optimizer.py"

.PHONY: help build up down restart shell logs clean test backend simulate quickstart automate optimize custom

# Default target
help:
	@echo "╔════════════════════════════════════════════════════╗"
	@echo "║  AI-Driven Sky130 ASIC Platform - Commands        ║"
	@echo "╚════════════════════════════════════════════════════╝"
	@echo ""
	@echo "  make build        - Build Docker images"
	@echo "  make up           - Start all services"
	@echo "  make down         - Stop all services"
	@echo "  make restart      - Restart all services"
	@echo "  make shell        - Enter main container shell"
	@echo "  make logs         - View container logs"
	@echo "  make clean        - Clean data and caches"
	@echo "  make test         - Run tests"
	@echo "  make backend      - Start FastAPI backend"
	@echo "  make simulate     - Run example simulations"
	@echo ""

# Build Docker images
build:
	@echo "🔨 Building Docker images (this may take 30-60 minutes)..."
	cd docker && docker compose build

# Start services
up:
	@echo "🚀 Starting platform services..."
	cd docker && docker compose up -d
	@echo "✅ Platform is running!"
	@echo "   - Enter container: make shell"
	@echo "   - View logs: make logs"

# Stop services
down:
	@echo "🛑 Stopping platform services..."
	cd docker && docker compose down

# Restart services
restart: down up

# Enter container shell
shell:
	@echo "🐚 Entering Sky130 EDA container..."
	docker exec -it sky130_eda bash

# View logs
logs:
	cd docker && docker compose logs -f

# Clean data
clean:
	@echo "🧹 Cleaning generated data..."
	rm -rf data/designs/*
	rm -rf data/results/*
	rm -rf data/cache/*
	@echo "✅ Cleanup complete"

# Run tests
test:
	@echo "🧪 Running tests..."
	docker exec -it sky130_eda pytest /home/eda/tests -v

# Start backend
backend:
	@echo "🌐 Starting FastAPI backend..."
	docker exec -it sky130_eda bash -c "cd /home/eda/backend && python3 -m app.main"

# Run example simulations
simulate:
	@echo "⚡ Running Sky130 example simulations..."
	docker exec -it sky130_eda bash -c "\
		cd /home/eda/circuits/library && \
		python3 rc_sky130_example.py && \
		ngspice -b sky130_rc.spice && \
		echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━' && \
		cd current_mirror && \
		python3 sky130_current_mirror.py && \
		ngspice -b sky130_current_mirror.spice \
	"
	@echo "✅ Simulations complete!"

# Quick start (build + up + examples)
quickstart: build up
	@echo "⏳ Waiting for services to be ready..."
	@sleep 5
	@echo "🎯 Running example simulations..."
	@$(MAKE) simulate
	@echo ""
	@echo "╔════════════════════════════════════════════════════╗"
	@echo "║  Platform is ready!                                ║"
	@echo "║  Enter container: make shell                       ║"
	@echo "║  Start backend: make backend                       ║"
	@echo "╚════════════════════════════════════════════════════╝"

# Development mode
dev:
	@echo "🔧 Starting development mode..."
	cd docker && docker compose up

# Check installation
check:
	@echo "🔍 Checking installation..."
	@docker exec -it sky130_eda bash -c "\
		echo 'Ngspice:' && ngspice --version | head -1 && \
		echo 'Sky130 PDK:' && ls /opt/sky130_pdk/sky130A > /dev/null && echo '  ✓ Found' && \
		echo 'Magic:' && magic -noconsole --version 2>&1 | head -1 && \
		echo 'Python libs:' && python3 -c 'from circuits.sky130.devices import nmos; print(\"  ✓ Sky130 library OK\")' \
	"
	@echo "✅ Installation check complete!"
