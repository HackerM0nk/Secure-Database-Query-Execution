# Secure Database Query Execution

A secure, automated system for executing database queries using ephemeral credentials managed by HashiCorp Vault. This project demonstrates how to safely run database operations in CI/CD pipelines without exposing long-lived credentials.

## 🎯 What This Repository Does

This system solves the problem of **secure database access in production environments**. Instead of hardcoding database credentials or storing them in CI/CD variables or granting engineers access to DB credentials it:

1. **Stores Datastore's admin credentials securely** in HashiCorp Vault
2. **Generates ephemeral database users** on-demand for each job
3. **Executes queries** using temporary credentials
4. **Automatically revokes access** when the job completes
5. **Provides audit trails** for all database operations

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Buildkite     │    │   Vault Server  │    │   Databases     │
│   Pipeline      │    │                 │    │                 │
│                 │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ ┌─────────────┐ │    │ │   Admin     │ │    │ │   MySQL     │ │
│ │   Job A     │◄┼────┤ │ Credentials │ │    │ │             │ │
│ │             │ │    │ │             │ │    │ │             │ │
│ │ Query Exec  │ │    │ └─────────────┘ │    │ └─────────────┘ │
│ └─────────────┘ │    │                 │    │                 │
│                 │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│                 │    │ │ Ephemeral   │ │    │ │  MongoDB    │ │
│                 │    │ │ User Gen    │ │    │ │             │ │
│                 │    │ └─────────────┘ │    │ └─────────────┘ │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Key Features

### 🔐 Security First
- **Zero persistent credentials** in CI/CD environment
- **Ephemeral database users** with configurable TTL (1-24 hours)
- **Automatic credential revocation** after job completion
- **Audit logging** of all credential requests and database operations

### 🎯 Multi-Database Support
- **MySQL**: Execute SQL queries with proper transaction handling
- **MongoDB**: Support for CRUD operations via JSON configuration
- **Extensible**: Easy to add support for PostgreSQL, Redis, etc.

### 🔄 CI/CD Integration
- **Buildkite pipeline** for automated execution
- **Git-based workflow**: Queries stored in version control
- **Artifact management**: Results stored as build artifacts
- **Failure handling**: Proper error reporting and rollback

### 🐳 Local Development
- **Docker Compose** setup for complete local testing
- **Hot reload** capability for development
- **Health checks** and service dependencies

## 📋 Use Cases

### 1. Database Migrations
```sql
-- queries/migration_001.sql
ALTER TABLE users ADD COLUMN last_login TIMESTAMP;
UPDATE users SET last_login = NOW() WHERE active = 1;
```

### 2. Data Analytics
```json
// queries/user_analytics.json
[
  {
    "operation": "find",
    "collection": "users",
    "filter": {"created_at": {"$gte": "2024-01-01"}}
  }
]
```

### 3. Maintenance Tasks
```sql
-- queries/cleanup.sql
DELETE FROM logs WHERE created_at < DATE_SUB(NOW(), INTERVAL 30 DAY);
OPTIMIZE TABLE logs;
```

### 4. Data Validation
```sql
-- queries/data_integrity_check.sql
SELECT COUNT(*) as orphaned_records
FROM orders o
LEFT JOIN users u ON o.user_id = u.id
WHERE u.id IS NULL;
```

## 🛠️ Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.8+
- Vault CLI (optional)

### 1. Clone and Start
```bash
git clone <repository-url>
cd Secure-Database-Query-Execution

# Start all services
docker-compose up -d

# Configure Vault
./setup_vault.sh

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Test the System
```bash
# Test MySQL queries
python request_creds_and_run.py mysql queries/mysql_queries.sql

# Test MongoDB queries
python request_creds_and_run.py mongodb queries/mongodb_queries.json
```

### 3. View Results
Query results are saved as JSON files with detailed execution information:
```json
{
  "database": "mysql",
  "timestamp": "2024-01-15T10:30:45",
  "lease_id": "database/creds/mysql-role/abc123",
  "queries": [
    {
      "query_index": 0,
      "query": "SELECT COUNT(*) FROM users",
      "status": "success",
      "rows_affected": 1,
      "data": [{"COUNT(*)": 42}]
    }
  ]
}
```

## 🔧 Configuration

### Vault Setup
- **Database Secrets Engine**: Manages ephemeral credentials
- **MySQL Role**: Creates temporary users with specific permissions
- **MongoDB Role**: Generates time-limited access tokens

### Database Permissions
- **MySQL**: `SELECT, INSERT, UPDATE, DELETE` on target database
- **MongoDB**: `readWrite` role on target database
- **Configurable**: Easily modify permissions per role

### TTL Configuration
```bash
# Default: 1 hour, Maximum: 24 hours
vault write database/roles/mysql-role \
    default_ttl="1h" \
    max_ttl="24h"
```

## 🏢 Production Considerations

### Security Hardening
- Replace dev tokens with proper authentication (AppRole, JWT)
- Enable TLS encryption for all services
- Implement network segmentation
- Set up log monitoring and alerting

### Scalability
- Use managed Vault service (Vault Enterprise, HCP Vault)
- Implement database connection pooling
- Add query timeout and resource limits
- Consider read replicas for read-only operations

### Monitoring
- Vault audit logs for credential lifecycle
- Database query performance metrics
- Failed query alerting
- Credential leak detection

## 📁 Project Structure

```
.
├── README.md                   # This file
├── SETUP.md                   # Detailed setup instructions
├── docker-compose.yml         # Local infrastructure
├── requirements.txt           # Python dependencies
├── vault_client.py           # Vault API wrapper
├── request_creds_and_run.py  # Main execution script
├── setup_vault.sh            # Vault configuration
├── .buildkite/
│   └── pipeline.yml          # CI/CD pipeline
└── queries/                  # Sample query files
    ├── mysql_queries.sql
    └── mongodb_queries.json
```

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Add** your database type or enhancement
4. **Test** locally using Docker Compose
5. **Submit** a pull request

### Adding New Database Types
1. Update `vault_client.py` with database configuration
2. Add execution logic to `request_creds_and_run.py`
3. Create sample queries in `queries/` directory
4. Update documentation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋 Support

- **Issues**: Report bugs or request features via GitHub Issues
- **Documentation**: See [SETUP.md](SETUP.md) for detailed configuration
- **Security**: For security-related issues, please email [security@yourcompany.com]

---

**Built with ❤️ for secure database operations**