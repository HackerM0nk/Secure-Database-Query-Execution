# Secure Database Query Execution

A **Zero-Trust Database Access System** that eliminates the need for developers to have permanent database credentials. This project demonstrates how to safely execute database operations in CI/CD pipelines using ephemeral credentials managed by HashiCorp Vault.

## 🎯 What This System Solves

Instead of developers hardcoding database credentials or storing them in `.env` files, this system:

1. **Stores admin credentials securely** in HashiCorp Vault only
2. **Generates ephemeral database users** on-demand (1-hour TTL)
3. **Executes queries** using temporary credentials that auto-expire
4. **Automatically revokes access** when jobs complete
5. **Provides complete audit trails** for compliance (SOX, HIPAA, PCI-DSS)

## 🏗️ Architecture: Zero-Trust Database Access

### 🔄 Two Core Security Flows

#### 1️⃣ **Automated Query Execution Flow (CI/CD Pipeline)**

```mermaid
sequenceDiagram
    participant Dev as 👨‍💻 Developer
    participant Git as 📁 Git Repository
    participant BK as 🚀 Buildkite CI
    participant App as 🔧 Query Engine
    participant Vault as 🔐 HashiCorp Vault
    participant DB as 🗄️ Database (MySQL/MongoDB)
    participant Audit as 📊 Audit Logs

    Note over Dev,Audit: 🛡️ AUTOMATED QUERY EXECUTION PIPELINE

    Dev->>Git: 1. Push queries to queries/ folder
    Note right of Dev: queries/mysql/analytics.sql<br/>queries/migrations/schema.sql

    Git->>Git: 2. Code Review & Approval ✅
    Git->>BK: 3. Trigger CI job after merge

    BK->>App: 4. Execute: request_creds_and_run.py mysql query.sql

    App->>Vault: 5. Request ephemeral credentials
    Note right of Vault: 🔒 Only Vault has admin access<br/>No credentials in code/config

    Vault->>DB: 6. CREATE USER 'v-token-abc123'@'%'
    Note over Vault,DB: 🕐 1-hour TTL set automatically

    Vault-->>App: 7. Return temp credentials + lease_id
    Note left of App: username: v-token-mysql-abc123<br/>password: temp-secure-xyz<br/>lease: database/creds/mysql-role/abc123

    App->>DB: 8. Execute SQL queries with ephemeral user
    DB-->>App: 9. Return query results

    App->>Audit: 10. Log complete execution details
    Note right of Audit: 📝 Query content, results, timing<br/>Complete compliance trail

    App->>Vault: 11. Revoke lease immediately (cleanup)
    Vault->>DB: 12. DROP USER 'v-token-abc123'@'%'

    Note over App,DB: 🗑️ Zero credential persistence<br/>✅ Query executed securely
```

#### 2️⃣ **Developer JIT Access Flow (PrivateBin Secure Sharing)**

```mermaid
sequenceDiagram
    participant Dev as 👨‍💻 Developer
    participant App as 🔧 Access System
    participant Vault as 🔐 HashiCorp Vault
    participant DB as 🗄️ Database
    participant PB as 🔗 PrivateBin Web
    participant Slack as 📱 Slack
    participant Audit as 📊 Audit Logs

    Note over Dev,Audit: 🔓 DEVELOPER JIT ACCESS SYSTEM

    Dev->>App: 1. Request access: developer_access.py
    Note right of Dev: python developer_access.py mysql<br/>"bug-investigation@company.com"<br/>"Debugging user login issue #456"

    App->>Vault: 2. Generate ephemeral credentials
    Vault->>DB: 3. CREATE USER 'v-token-dev789'@'%'
    Note over Vault,DB: 🕐 1-hour TTL for manual access

    Vault-->>App: 4. Return dev credentials + lease_id

    App->>PB: 5. Create secure credential page
    Note right of PB: 🔗 Self-destructing page<br/>Burns after 30 seconds<br/>Or after 1 view

    PB-->>App: 6. Return secure URL
    Note left of App: http://localhost:8081/view/ABC123XYZ

    App->>Slack: 7. Send DM with secure link
    Note right of Slack: 📱 "Database access granted!<br/>🔗 [secure-link] (expires in 30s)<br/>⏰ Credentials valid for 1 hour"

    App->>Audit: 8. Log access request
    Note right of Audit: 📋 Developer email, justification<br/>Database type, timestamp

    Dev->>PB: 9. Click secure link from Slack
    PB-->>Dev: 10. Display credentials (one-time only)
    Note left of Dev: 💻 Connection details shown:<br/>Host: localhost:3306<br/>Username: v-token-dev789<br/>Password: [temp-password]

    Note over PB: 🔥 Page self-destructs after viewing

    Dev->>DB: 11. Manual database connection
    Note right of Dev: mysql -h localhost -P 3306<br/>-u v-token-dev789 -p[password] demo

    DB-->>Dev: 12. Direct database access for debugging

    Note over Vault,DB: ⏰ After 1 hour: Auto-revocation
    Vault->>DB: 13. DROP USER 'v-token-dev789'@'%'

    Note over Dev,DB: 🛡️ Zero persistent access<br/>✅ Complete audit trail maintained
```

### 🔄 Vault Credential Engine Mechanism

**How Vault Creates Ephemeral Database Users:**

1. **Admin Storage**: Only Vault stores database admin credentials (root/admin users)
2. **JIT Generation**: When access needed, Vault creates temporary database users:
   ```sql
   -- Vault executes this on MySQL:
   CREATE USER 'v-token-mysql-role-abc123'@'%' IDENTIFIED BY 'temp-password-xyz';
   GRANT SELECT, INSERT, UPDATE ON demo.* TO 'v-token-mysql-role-abc123'@'%';
   ```
3. **Lease Management**: Each credential has a lease_id and TTL (1 hour default)
4. **Auto-Revocation**: Vault automatically drops users when lease expires:
   ```sql
   -- Vault executes this after TTL:
   DROP USER 'v-token-mysql-role-abc123'@'%';
   ```

## 📁 Optimized Project Structure

```
.
├── 📖 README.md                    # This comprehensive guide
├── 🐳 docker-compose.yml           # Infrastructure setup
├── ⚙️ requirements.txt             # Python dependencies
├── 🛠️ Makefile                     # Convenient commands for all operations
├── 🚫 .gitignore                   # Git ignore patterns
├── 📜 scripts/                     # Setup and utility scripts
│   ├── setup_vault.sh              # Vault configuration
│   ├── setup_databases.sh          # Database initialization
│   └── setup_mysql.sql             # MySQL schema
├── 🔧 src/                         # Core application code
│   ├── vault_client.py             # Vault API integration
│   ├── request_creds_and_run.py    # Query execution engine
│   ├── developer_access.py         # JIT access management
│   ├── simple_privatebin.py        # Secure credential sharing
│   └── credential_viewer.py        # Web-based credential viewer
├── 📊 queries/                     # Organized query repository
│   ├── README.md                   # Query documentation
│   ├── examples/                   # Basic examples for testing
│   │   ├── mysql_basic.sql         # MySQL fundamentals
│   │   └── mongodb_basic.json      # MongoDB operations
│   ├── mysql/                      # MySQL-specific queries
│   │   └── user_management.sql     # User administration
│   ├── mongodb/                    # MongoDB-specific queries
│   │   └── analytics.json          # Data analytics operations
│   ├── migrations/                 # Database schema changes
│   │   └── 001_create_audit_table.sql
│   └── production/                 # Production maintenance
│       └── health_check.sql        # System health queries
├── 📋 config/                      # Configuration files
│   └── .buildkite/                 # CI/CD pipeline
│       └── pipeline.yml
├── 📚 docs/                        # Documentation
│   ├── TESTING_GUIDE.md            # Slack and credential testing
│   └── SUMMARY.md                  # Implementation summary
├── 🧪 tests/                       # Test files
│   └── test_vault_integration.py   # Integration tests
├── 📊 logs/                        # Runtime logs and results
│   ├── access_requests_*.log       # Audit trails
│   └── query_results_*.json        # Execution results
├── developer_access.py             # Convenient wrapper script
└── request_creds_and_run.py        # Convenient wrapper script
```

---

# 🚀 Complete Setup Guide: Build from Scratch

Follow these commands to build and test the entire system locally.

## Prerequisites

Ensure you have these installed:
- **Docker & Docker Compose**
- **Python 3.8+**
- **Git**

## 🚀 Quick Start with Makefile

For convenience, use the provided Makefile commands:

```bash
# Clone the repository
git clone <repository-url>
cd Secure-Database-Query-Execution

# One-command setup (installs deps, starts services, configures everything)
make deploy
```

## Step-by-Step Manual Setup

### Step 1: Install Dependencies and Start Services

```bash
# Install Python dependencies
make install

# Start all services (Vault, MySQL, MongoDB, PrivateBin)
make start
```

**Expected Output:**
```
📦 Installing Python dependencies...
🚀 Starting all services...
⏳ Waiting for services to be ready...
✅ Services started!
```

### Step 2: Configure System

```bash
# Configure Vault and initialize databases
make setup
```

**Expected Output:**
```
⚙️ Configuring Vault...
🏛️  Configuring Vault database secrets engine...
✅ Vault is ready!
📌 Enabling database secrets engine...
Success! Data written to: database/config/mysql-database
Success! Data written to: database/roles/mysql-role
🗄️ Initializing databases...
🎉 Database setup completed successfully!
✅ Setup complete!
```

### Step 3: Verify Installation

```bash
# Run all tests
make test

# Or run individual tests
make test-mysql    # Test MySQL functionality
make test-mongo    # Test MongoDB functionality
make test-access   # Test developer access system
```

## Step 5: Verify Core System - Query Execution

### Test MySQL Query Execution

```bash
# Execute sample MySQL queries using ephemeral credentials
python request_creds_and_run.py mysql queries/examples/mysql_basic.sql
```

**Expected Output:**
```
2025-XX-XX XX:XX:XX,XXX - INFO - Generated credentials for role mysql-role, lease_id: database/creds/mysql-role/abc123
2025-XX-XX XX:XX:XX,XXX - INFO - MySQL query 0 executed successfully
2025-XX-XX XX:XX:XX,XXX - INFO - All queries executed successfully
2025-XX-XX XX:XX:XX,XXX - INFO - Results saved to query_results_mysql_XXXXXXX_XXXXXX.json
2025-XX-XX XX:XX:XX,XXX - INFO - Vault lease revoked successfully
```

### Test MongoDB Query Execution

```bash
# Execute sample MongoDB queries using ephemeral credentials
python request_creds_and_run.py mongodb queries/examples/mongodb_basic.json
```

**Expected Output:**
```
2025-XX-XX XX:XX:XX,XXX - INFO - Generated credentials for role mongodb-role, lease_id: database/creds/mongodb-role/xyz789
2025-XX-XX XX:XX:XX,XXX - INFO - MongoDB query 0 executed successfully
2025-XX-XX XX:XX:XX,XXX - INFO - All queries executed successfully
2025-XX-XX XX:XX:XX,XXX - INFO - Results saved to query_results_mongodb_XXXXXXX_XXXXXX.json
2025-XX-XX XX:XX:XX,XXX - INFO - Vault lease revoked successfully
```

### Verify Query Results

```bash
# Check the generated result files
ls -la query_results_*.json

# View MySQL results
cat query_results_mysql_*.json | jq '.queries[0].data'

# View MongoDB results
cat query_results_mongodb_*.json | jq '.queries[0].data'
```

## Step 6: Test Developer Access System

### Start Credential Viewer

```bash
# Start the secure credential viewer (in background)
python src/credential_viewer.py &

# Verify it's running
curl -s http://localhost:8081 | grep "Secure Credential Viewer"
```

### Request Developer Database Access

```bash
# Request temporary MySQL access for a developer
python developer_access.py mysql "developer@company.com" "Bug investigation for ticket #123"
```

**Expected Output:**
```json
{
  "status": "success",
  "access_granted": true,
  "database_type": "mysql",
  "developer_email": "developer@company.com",
  "privatebin_url": "http://localhost:8081/view/ABC123XYZ789",
  "expires_at": "2025-XX-XXTXX:XX:XX.XXXXXX",
  "slack_notified": true,
  "vault_lease_id": "database/creds/mysql-role/temp123"
}
```

### View Secure Credentials

```bash
# Copy the privatebin_url from above output and open in browser
# Or test with curl:
PASTE_ID="ABC123XYZ789"  # Replace with actual ID from output
curl -s "http://localhost:8081/view/${PASTE_ID}" | grep -A 10 "username"
```

**The secure credential page will display:**
- Database connection details (host, port, username, password)
- Expiration time and security warnings
- Auto-destruct after 30 seconds or after viewing

## Step 7: Test Slack Integration (Optional)

### Setup Slack Webhook

1. **Create Slack Webhook:**
   - Go to https://api.slack.com/apps
   - Create new app → Incoming Webhooks
   - Copy webhook URL

2. **Test Slack Notifications:**
```bash
# Set your Slack webhook URL
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

# Request access with Slack notification
python developer_access.py mysql "test@company.com" "Testing Slack integration" --slack-webhook "$SLACK_WEBHOOK_URL"
```

**Expected Result:** Formatted Slack message with secure credential link.

## Step 8: Verify Security Features

### Check Audit Trail

```bash
# View complete audit trail of all access requests
echo "📋 Audit Trail:"
cat access_requests_*.log | jq -r '. | "🕐 \(.timestamp) | 👤 \(.developer) | 🗄️ \(.database) | 📝 \(.justification)"'
```

### Verify Ephemeral Users in Databases

```bash
# Check current ephemeral MySQL users (should be empty after jobs complete)
docker exec secure-database-query-execution-mysql-1 mysql -u root -prootpass -e "SELECT user, host FROM mysql.user WHERE user LIKE 'v-token%';" 2>/dev/null

# Check MongoDB users
docker exec secure-database-query-execution-mongo-1 mongosh admin --quiet --eval "db.getUsers()"
```

### Test Credential Auto-Expiration

```bash
# Request access and note the lease_id
python developer_access.py mysql "test@company.com" "Expiration test" | jq -r '.vault_lease_id'

# Check Vault leases (should show active lease)
docker exec secure-database-query-execution-vault-1 sh -c 'export VAULT_ADDR=http://127.0.0.1:8200 && export VAULT_TOKEN=root-token && vault write sys/leases/lookup lease_id="LEASE_ID_FROM_ABOVE"'

# Wait 1 hour or manually revoke
# docker exec secure-database-query-execution-vault-1 sh -c 'export VAULT_ADDR=http://127.0.0.1:8200 && export VAULT_TOKEN=root-token && vault write sys/leases/revoke lease_id="LEASE_ID"'
```

## Step 9: Test Advanced Features

### Manual Database Connection with Ephemeral Credentials

```bash
# 1. Request credentials and extract connection info
python developer_access.py mysql "manual-test@company.com" "Manual connection test" > access_result.json

# 2. Get the secure link and visit it to get credentials
SECURE_LINK=$(cat access_result.json | jq -r '.privatebin_url')
echo "Visit this link to get credentials: $SECURE_LINK"

# 3. Use the displayed credentials to connect manually:
# mysql -h localhost -P 3306 -u v-token-mysql-role-XXXXX -pPASSWORD demo
```

### MongoDB Access Test

```bash
# Request MongoDB access
python developer_access.py mongodb "mongo-test@company.com" "MongoDB data analysis"

# Use credentials from secure link:
# mongosh "mongodb://USERNAME:PASSWORD@localhost:27017/demo"
```

### Test Query File Formats

**MySQL Query File (`test_mysql.sql`):**
```sql
-- Create and test a simple table
CREATE TABLE test_users (id INT PRIMARY KEY, name VARCHAR(50));
INSERT INTO test_users VALUES (1, 'Alice'), (2, 'Bob');
SELECT * FROM test_users;
DROP TABLE test_users;
```

**MongoDB Query File (`test_mongodb.json`):**
```json
[
  {
    "operation": "insert_one",
    "collection": "test_collection",
    "document": {"name": "test_document", "value": 42}
  },
  {
    "operation": "find",
    "collection": "test_collection",
    "filter": {"name": "test_document"}
  }
]
```

```bash
# Test custom query files
echo "CREATE TABLE test (id INT); INSERT INTO test VALUES (1); SELECT * FROM test;" > test_mysql.sql
python request_creds_and_run.py mysql test_mysql.sql

echo '[{"operation": "insert_one", "collection": "test", "document": {"x": 1}}]' > test_mongo.json
python request_creds_and_run.py mongodb test_mongo.json
```

---

# 🔧 Service URLs & Access

| Service | URL | Credentials |
|---------|-----|-------------|
| **Vault UI** | http://localhost:8200/ui | Token: `root-token` |
| **Credential Viewer** | http://localhost:8081 | No auth required |
| **MySQL Direct** | localhost:3306 | root/rootpass |
| **MongoDB Direct** | localhost:27017 | No auth |
| **PrivateBin** | http://localhost:8080 | No auth |

---

# 🧪 Verification Checklist

Run these commands to verify everything works:

```bash
# ✅ Infrastructure Check
docker-compose ps | grep "Up"

# ✅ Vault Configuration Check
docker exec secure-database-query-execution-vault-1 sh -c 'export VAULT_ADDR=http://127.0.0.1:8200 && export VAULT_TOKEN=root-token && vault read database/roles/mysql-role'

# ✅ MySQL Query Execution Check
python request_creds_and_run.py mysql examples/queries/mysql_queries.sql | grep "successfully"

# ✅ MongoDB Query Execution Check
python request_creds_and_run.py mongodb examples/queries/mongodb_queries.json | grep "successfully"

# ✅ Developer Access Check
python developer_access.py mysql test@company.com "verification test" | jq '.status'

# ✅ Audit Trail Check
cat access_requests_*.log | wc -l

# ✅ Credential Viewer Check
curl -s http://localhost:8081 | grep "Secure Credential Viewer"

echo "🎉 All systems verified and working!"
```

---

# 🔒 Security Features Verified

- ✅ **Zero Persistent Credentials**: No passwords stored in code/config
- ✅ **Ephemeral Users**: Temporary database users created on-demand
- ✅ **Auto-Expiration**: 1-hour TTL with automatic cleanup
- ✅ **Complete Audit**: Every access logged with justification
- ✅ **Secure Sharing**: Self-destructing credential links
- ✅ **Code Review**: All queries go through Git workflow
- ✅ **Compliance Ready**: SOX, HIPAA, PCI-DSS audit trails

---

# 🛠️ Troubleshooting

### Common Issues & Solutions

**Docker Issues:**
```bash
# Restart all services
docker-compose down && docker-compose up -d

# Check logs
docker-compose logs vault
docker-compose logs mysql
docker-compose logs mongo
```

**Vault Issues:**
```bash
# Check Vault status
docker exec secure-database-query-execution-vault-1 sh -c 'export VAULT_ADDR=http://127.0.0.1:8200 && export VAULT_TOKEN=root-token && vault status'

# Reconfigure if needed
./scripts/setup_vault.sh
```

**Python Issues:**
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Check Python path
export PYTHONPATH="${PWD}/src:${PYTHONPATH}"
```

**Database Connection Issues:**
```bash
# Test MySQL connection
docker exec secure-database-query-execution-mysql-1 mysql -u root -prootpass -e "SHOW DATABASES;"

# Test MongoDB connection
docker exec secure-database-query-execution-mongo-1 mongosh --eval "db.adminCommand('ping')"
```

---

# 🚀 Production Deployment

For production use, implement these security measures:

1. **Replace dev tokens** with proper Vault authentication (AppRole, JWT)
2. **Enable TLS encryption** for all services
3. **Implement network segmentation** and firewalls
4. **Set up log monitoring** and alerting
5. **Use managed Vault service** (Vault Enterprise, HCP Vault)
6. **Configure proper backup** and disaster recovery

---

**🎉 Congratulations!** You now have a fully functional Zero-Trust Database Access System that eliminates credential sprawl and provides complete audit trails for all database operations.

For questions or issues, see the [troubleshooting guide](docs/TESTING_GUIDE.md) or create an issue in this repository.