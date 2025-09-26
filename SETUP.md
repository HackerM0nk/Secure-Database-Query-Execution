# Secure Database Query Execution - Setup Guide

This project implements Job A of a secure database query execution system using HashiCorp Vault for credential management, Docker for local infrastructure, and Buildkite for orchestration.

## Architecture Overview

- **Vault**: Manages ephemeral database credentials using the database secrets engine
- **MySQL & MongoDB**: Target databases running in Docker containers
- **Buildkite**: Orchestrates query execution jobs
- **Python Scripts**: Handle credential requests and query execution

## Prerequisites

- Docker and Docker Compose
- Python 3.8+
- Buildkite CLI (optional, for local testing)
- Vault CLI (for setup)

## Quick Start

### 1. Start Infrastructure

```bash
# Start all services
docker-compose up -d

# Wait for services to be healthy
docker-compose ps
```

### 2. Configure Vault

```bash
# Install Vault CLI if not already installed
# On macOS: brew install vault

# Run the setup script
./setup_vault.sh
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Test Query Execution

```bash
# Test MySQL queries
python request_creds_and_run.py mysql queries/mysql_queries.sql

# Test MongoDB queries
python request_creds_and_run.py mongodb queries/mongodb_queries.json
```

## Project Structure

```
.
├── docker-compose.yml          # Infrastructure setup
├── vault_client.py            # Vault API wrapper
├── request_creds_and_run.py   # Main Job A script
├── setup_vault.sh             # Vault configuration script
├── requirements.txt           # Python dependencies
├── .buildkite/
│   └── pipeline.yml          # Buildkite pipeline configuration
└── queries/
    ├── mysql_queries.sql     # Sample MySQL queries
    └── mongodb_queries.json  # Sample MongoDB queries
```

## Security Features

### Credential Management
- Root database credentials stored only in Vault
- Ephemeral credentials generated per job execution
- Automatic credential revocation after use
- Configurable TTL (default: 1 hour, max: 24 hours)

### Audit Trail
- All credential requests logged by Vault
- Query execution results stored with timestamps
- Lease IDs tracked for credential lifecycle management

### Network Security
- Services isolated in Docker network
- Database access only through ephemeral credentials
- No persistent credential storage in job artifacts

## Usage

### Manual Execution

```bash
# Execute MySQL queries
python request_creds_and_run.py mysql path/to/queries.sql --output results.json

# Execute MongoDB queries
python request_creds_and_run.py mongodb path/to/queries.json --output results.json
```

### Buildkite Integration

The pipeline automatically:
1. Detects query files in the `queries/` directory
2. Requests ephemeral credentials from Vault
3. Executes queries against target databases
4. Stores results as build artifacts
5. Revokes credentials after completion

### Query File Formats

#### MySQL (`.sql` files)
```sql
-- Semicolon-separated SQL statements
CREATE TABLE test (id INT PRIMARY KEY);
INSERT INTO test VALUES (1);
SELECT * FROM test;
```

#### MongoDB (`.json` files)
```json
[
  {
    "operation": "insert_one",
    "collection": "test",
    "document": {"name": "example"}
  },
  {
    "operation": "find",
    "collection": "test",
    "filter": {}
  }
]
```

## Configuration

### Vault Settings
- **URL**: `http://localhost:8200` (development)
- **Token**: `root-token` (development only)
- **Database TTL**: 1 hour default, 24 hour maximum

### Database Connections
- **MySQL**: `localhost:3306`, database: `demo`
- **MongoDB**: `localhost:27017`, database: `demo`

## Troubleshooting

### Common Issues

1. **Vault authentication failed**
   - Ensure Vault is running: `docker-compose ps vault`
   - Check token: `export VAULT_TOKEN=root-token`

2. **Database connection errors**
   - Verify services are healthy: `docker-compose ps`
   - Check credentials: `vault read database/creds/mysql-role`

3. **Python import errors**
   - Install dependencies: `pip install -r requirements.txt`

### Logs and Debugging

```bash
# View service logs
docker-compose logs vault
docker-compose logs mysql
docker-compose logs mongo

# Enable debug logging
export VAULT_LOG_LEVEL=debug
python request_creds_and_run.py --help
```

## Development

### Adding New Database Types

1. Update `vault_client.py` with new database configuration
2. Add database-specific logic to `request_creds_and_run.py`
3. Update Vault setup script with new roles
4. Add corresponding query file format documentation

### Extending Query Support

- Modify query parsing in `execute_*_queries()` methods
- Add new operation types for MongoDB
- Implement transaction support for MySQL

## Security Notes

- This setup is for **development/testing only**
- Production deployment requires:
  - TLS encryption for all services
  - Proper Vault authentication (AppRole, JWT, etc.)
  - Network segmentation
  - Audit log monitoring
  - Credential rotation policies