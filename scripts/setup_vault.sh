#!/bin/bash

# Vault setup script for configuring database secrets engine
# This script runs vault commands inside the Docker container

set -e

CONTAINER_NAME="secure-database-query-execution-vault-1"

echo "🏛️  Configuring Vault database secrets engine..."

# Function to run vault commands inside the container
vault_exec() {
    docker exec $CONTAINER_NAME vault "$@"
}

# Wait for Vault to be ready
echo "⏳ Waiting for Vault container to be ready..."
until docker exec $CONTAINER_NAME vault status > /dev/null 2>&1; do
    echo "Waiting for Vault..."
    sleep 2
done

echo "✅ Vault is ready!"

# Set environment variables inside container
docker exec $CONTAINER_NAME sh -c 'export VAULT_ADDR=http://127.0.0.1:8200 && export VAULT_TOKEN=root-token'

# Enable database secrets engine
echo "📌 Enabling database secrets engine..."
vault_exec secrets enable -path=database database 2>/dev/null || echo "ℹ️  Database secrets engine already enabled"

# Configure MySQL database connection (use container names for internal communication)
echo "📌 Configuring MySQL database connection..."
vault_exec write database/config/mysql-database \
    plugin_name=mysql-database-plugin \
    connection_url="{{username}}:{{password}}@tcp(mysql:3306)/" \
    allowed_roles="mysql-role" \
    username="root" \
    password="rootpass"

# Create MySQL role
echo "📌 Creating MySQL role..."
vault_exec write database/roles/mysql-role \
    db_name=mysql-database \
    creation_statements="CREATE USER '{{name}}'@'%' IDENTIFIED BY '{{password}}';GRANT SELECT, INSERT, UPDATE, DELETE ON demo.* TO '{{name}}'@'%';" \
    default_ttl="1h" \
    max_ttl="24h"

# Configure MongoDB database connection (use container name)
echo "📌 Configuring MongoDB database connection..."
vault_exec write database/config/mongodb-database \
    plugin_name=mongodb-database-plugin \
    connection_url="mongodb://mongo:27017/demo" \
    allowed_roles="mongodb-role"

# Create MongoDB role
echo "📌 Creating MongoDB role..."
vault_exec write database/roles/mongodb-role \
    db_name=mongodb-database \
    creation_statements='{"db": "demo", "roles": [{"role": "readWrite"}]}' \
    default_ttl="1h" \
    max_ttl="24h"

echo "✅ Vault configuration completed successfully!"

# Test credential generation
echo "🧪 Testing credential generation..."
echo "🐬 MySQL credentials:"
vault_exec read database/creds/mysql-role

echo "🍃 MongoDB credentials:"
vault_exec read database/creds/mongodb-role

echo ""
echo "🎉 Setup complete! Access information:"
echo "🏛️  Vault UI: http://localhost:8200/ui (Token: root-token)"
echo "🐬 MySQL: localhost:3306 (root/rootpass)"
echo "🍃 MongoDB: localhost:27017"
echo ""
echo "You can now run: python request_creds_and_run.py mysql queries/mysql_queries.sql"