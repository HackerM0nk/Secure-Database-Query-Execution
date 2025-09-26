# 📊 Query Repository

This directory contains organized database queries for the secure execution system. All queries here are executed using ephemeral credentials managed by HashiCorp Vault.

## 📁 Directory Structure

```
queries/
├── 📖 README.md                    # This guide
├── 📂 examples/                    # Basic examples for testing
│   ├── mysql_basic.sql             # MySQL fundamentals
│   └── mongodb_basic.json          # MongoDB operations
├── 🗄️ mysql/                       # MySQL-specific queries
│   └── user_management.sql         # User administration
├── 🍃 mongodb/                     # MongoDB-specific queries
│   └── analytics.json              # Data analytics operations
├── 🔄 migrations/                  # Database schema changes
│   └── 001_create_audit_table.sql  # Audit table migration
└── 🏭 production/                  # Production maintenance
    └── health_check.sql            # System health queries
```

## 🚀 Usage Examples

### Execute Example Queries
```bash
# Basic MySQL operations
python request_creds_and_run.py mysql queries/examples/mysql_basic.sql

# Basic MongoDB operations
python request_creds_and_run.py mongodb queries/examples/mongodb_basic.json
```

### Execute Specific Database Operations
```bash
# MySQL user management
python request_creds_and_run.py mysql queries/mysql/user_management.sql

# MongoDB analytics
python request_creds_and_run.py mongodb queries/mongodb/analytics.json
```

### Run Database Migrations
```bash
# Execute schema migration
python request_creds_and_run.py mysql queries/migrations/001_create_audit_table.sql
```

### Production Health Checks
```bash
# Database health monitoring
python request_creds_and_run.py mysql queries/production/health_check.sql
```

## 📝 Query File Formats

### MySQL Queries (`.sql` files)
```sql
-- Comments explain the purpose
CREATE TABLE example (id INT PRIMARY KEY);
INSERT INTO example VALUES (1), (2), (3);
SELECT * FROM example;
```

### MongoDB Queries (`.json` files)
```json
[
  {
    "operation": "insert_one",
    "collection": "example",
    "document": {"name": "test", "value": 123}
  },
  {
    "operation": "find",
    "collection": "example",
    "filter": {"name": "test"}
  }
]
```

## 📋 Supported MongoDB Operations

| Operation | Description | Parameters |
|-----------|-------------|------------|
| `insert_one` | Insert single document | `collection`, `document` |
| `insert_many` | Insert multiple documents | `collection`, `documents` |
| `find` | Query documents | `collection`, `filter` |
| `update_one` | Update single document | `collection`, `filter`, `update` |
| `update_many` | Update multiple documents | `collection`, `filter`, `update` |
| `delete_one` | Delete single document | `collection`, `filter` |
| `delete_many` | Delete multiple documents | `collection`, `filter` |
| `aggregate` | Aggregation pipeline | `collection`, `pipeline` |

## 🔒 Security Notes

- **All queries executed with ephemeral credentials**
- **Automatic credential revocation after execution**
- **Complete audit trail maintained**
- **No persistent database access required**

## 📊 Query Categories

### 🧪 Examples (`examples/`)
- **Purpose**: Learning and testing
- **Audience**: New users, demonstrations
- **Safety**: Safe to run multiple times

### 🔧 Database-Specific (`mysql/`, `mongodb/`)
- **Purpose**: Production operations
- **Audience**: Database administrators
- **Safety**: Review before execution

### 🔄 Migrations (`migrations/`)
- **Purpose**: Schema changes
- **Audience**: Database developers
- **Safety**: Test in staging first
- **Naming**: `###_description.sql` (sequential)

### 🏭 Production (`production/`)
- **Purpose**: Maintenance and monitoring
- **Audience**: Operations teams
- **Safety**: Read-only operations preferred

## ✅ Best Practices

### Query Development
1. **Test in examples first** before moving to production
2. **Use descriptive file names** and comments
3. **Include rollback procedures** for migrations
4. **Validate syntax** before committing

### File Organization
1. **Group by database type** (mysql/, mongodb/)
2. **Use semantic versioning** for migrations
3. **Include metadata** in file headers
4. **Document dependencies** and prerequisites

### Security Guidelines
1. **No hardcoded credentials** anywhere
2. **Parameterize user inputs** when possible
3. **Use least privilege** SQL statements
4. **Review all DDL changes** carefully

## 🚀 Adding New Queries

### Step 1: Choose Directory
```bash
# For testing/learning
touch queries/examples/my_test.sql

# For production use
touch queries/mysql/feature_name.sql
touch queries/mongodb/analytics_update.json

# For schema changes
touch queries/migrations/002_add_new_table.sql
```

### Step 2: Write Query
```sql
-- File: queries/mysql/my_feature.sql
-- Purpose: Add user preferences functionality
-- Author: Your Name
-- Date: 2024-01-15

CREATE TABLE user_preferences (
    user_id INT,
    preference_key VARCHAR(50),
    preference_value TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### Step 3: Test Execution
```bash
# Test the new query
python request_creds_and_run.py mysql queries/mysql/my_feature.sql

# Verify results
cat query_results_mysql_*.json | jq '.queries'
```

### Step 4: Document and Commit
- Add description to this README if needed
- Commit with descriptive message
- Update related documentation

## 📈 Query Execution Monitoring

All query executions generate detailed logs:

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

## 🆘 Troubleshooting

### Common Issues

**Query Syntax Errors:**
```bash
# Check MySQL syntax
mysql -u root -p --help

# Validate JSON format
cat queries/mongodb/file.json | jq '.'
```

**Permission Errors:**
```bash
# Verify Vault configuration
docker exec vault-container vault read database/roles/mysql-role
```

**Connection Issues:**
```bash
# Test database connectivity
python request_creds_and_run.py mysql queries/examples/mysql_basic.sql
```

## 📚 Additional Resources

- [MySQL Documentation](https://dev.mysql.com/doc/)
- [MongoDB Manual](https://docs.mongodb.com/manual/)
- [Vault Database Secrets](https://www.vaultproject.io/docs/secrets/databases)
- [Main Project README](../README.md)