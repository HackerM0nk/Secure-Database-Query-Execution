# Secure Database Query Execution - Makefile
# Convenient commands for development and operations

.PHONY: help install start stop clean test logs status

# Default target
help:
	@echo "🔐 Secure Database Query Execution - Available Commands:"
	@echo ""
	@echo "📋 Setup & Installation:"
	@echo "  make install     - Install Python dependencies"
	@echo "  make start       - Start all services (Docker Compose)"
	@echo "  make setup       - Configure Vault and initialize databases"
	@echo "  make stop        - Stop all services"
	@echo ""
	@echo "🧪 Testing & Development:"
	@echo "  make test        - Run basic system tests"
	@echo "  make test-mysql  - Test MySQL query execution"
	@echo "  make test-mongo  - Test MongoDB query execution"
	@echo "  make test-access - Test developer access system"
	@echo ""
	@echo "📊 Monitoring & Maintenance:"
	@echo "  make status      - Show service status"
	@echo "  make logs        - Show all service logs"
	@echo "  make audit       - Display audit trail"
	@echo "  make health      - Run health checks"
	@echo ""
	@echo "🧹 Cleanup:"
	@echo "  make clean       - Clean up logs and temporary files"
	@echo "  make reset       - Reset entire environment"

# Installation and setup
install:
	@echo "📦 Installing Python dependencies..."
	pip install -r requirements.txt

start:
	@echo "🚀 Starting all services..."
	docker-compose up -d
	@echo "⏳ Waiting for services to be ready..."
	sleep 30
	@echo "✅ Services started!"

setup: start
	@echo "⚙️ Configuring Vault..."
	./scripts/setup_vault.sh
	@echo "🗄️ Initializing databases..."
	./scripts/setup_databases.sh
	@echo "✅ Setup complete!"

stop:
	@echo "🛑 Stopping all services..."
	docker-compose down

# Testing
test: test-mysql test-mongo test-access
	@echo "✅ All tests completed!"

test-mysql:
	@echo "🐬 Testing MySQL query execution..."
	python request_creds_and_run.py mysql queries/examples/mysql_basic.sql

test-mongo:
	@echo "🍃 Testing MongoDB query execution..."
	python request_creds_and_run.py mongodb queries/examples/mongodb_basic.json

test-access:
	@echo "🔑 Testing developer access system..."
	python developer_access.py mysql "test@makefile.com" "Makefile integration test"

# Monitoring
status:
	@echo "📊 Service Status:"
	docker-compose ps

logs:
	@echo "📋 Service Logs:"
	docker-compose logs --tail=50

audit:
	@echo "🔍 Audit Trail:"
	@if [ -f logs/access_requests_*.log ]; then \
		cat logs/access_requests_*.log | jq -r '. | "🕐 \(.timestamp) | 👤 \(.developer) | 🗄️ \(.database) | 📝 \(.justification)"'; \
	else \
		echo "No audit logs found."; \
	fi

health:
	@echo "🏥 Running health checks..."
	python request_creds_and_run.py mysql queries/production/health_check.sql

# Cleanup
clean:
	@echo "🧹 Cleaning up temporary files..."
	rm -f .lease_id
	rm -rf logs/
	mkdir -p logs
	@echo "✅ Cleanup complete!"

reset: stop clean
	@echo "🔄 Resetting entire environment..."
	docker-compose down -v
	docker system prune -f
	@echo "✅ Environment reset!"

# Development helpers
dev-mysql:
	@echo "🔧 Starting MySQL credential viewer..."
	python src/credential_viewer.py &
	python developer_access.py mysql "dev@local.com" "Development session"

dev-mongo:
	@echo "🔧 Starting MongoDB credential viewer..."
	python src/credential_viewer.py &
	python developer_access.py mongodb "dev@local.com" "Development session"

# Production-like commands
deploy: install start setup test
	@echo "🚀 Deployment complete!"

verify:
	@echo "✅ Running verification checklist..."
	@docker-compose ps | grep -q "Up" && echo "✅ Infrastructure: Running"
	@python request_creds_and_run.py mysql queries/examples/mysql_basic.sql > /dev/null && echo "✅ MySQL: Working"
	@python request_creds_and_run.py mongodb queries/examples/mongodb_basic.json > /dev/null && echo "✅ MongoDB: Working"
	@curl -s http://localhost:8081 | grep -q "Secure Credential Viewer" && echo "✅ Credential Viewer: Running"
	@echo "🎉 All systems verified!"