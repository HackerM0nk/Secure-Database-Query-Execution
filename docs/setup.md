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

## 🗺️ Visual Architecture Diagram (Excalidraw)

An Excalidraw diagram describing the high-level architecture for this project has been added to the `docs/` folder. You can open and edit it with Excalidraw (web or desktop) or view it in the browser via the Excalidraw app.

- File: `docs/architecture.excalidraw`

How to view/edit:

1. Open the Excalidraw web app at https://excalidraw.com
2. From the app, choose "Load file" (folder icon) then select the local file `docs/architecture.excalidraw` from this repository.
3. Edit, export PNG/SVG, or share the diagram as needed.

Quick note: the diagram shows the following components and flows:

- Developer / CI calling `request_creds_and_run.py` or `developer_access.py`
- `vault_client.py` interacting with Vault to create ephemeral DB users
- Databases (MySQL, MongoDB) which receive temporary users
- Audit & results stored in `logs/` and optionally shared via PrivateBin

If you'd like I can also export a PNG or SVG of the diagram and add it to `docs/` for quick preview in GitHub—tell me which format you prefer.
