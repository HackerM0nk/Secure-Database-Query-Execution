# 🧪 Testing Guide: Slack Integration & PrivateBin Credentials

This guide shows you how to test the Slack notifications and view credentials via PrivateBin links.

## 🔧 Setup for Local Testing

### 1. Slack Webhook Setup

To test real Slack notifications, you need a Slack webhook:

#### Option A: Create a Test Slack Workspace (Recommended)
1. Go to https://slack.com/create
2. Create a new workspace (free)
3. Create an Incoming Webhook:
   - Go to https://api.slack.com/apps
   - Click "Create New App" → "From scratch"
   - Choose your test workspace
   - Go to "Incoming Webhooks" → Toggle "On"
   - Click "Add New Webhook to Workspace"
   - Choose a channel and copy the webhook URL

#### Option B: Use Your Existing Slack
1. Ask your Slack admin to create a webhook for testing
2. Or create one in your personal workspace

### 2. Test Slack Integration

```bash
# Set your webhook URL
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

# Test MySQL access request with real Slack notification
python3 developer_access.py mysql "your.email@company.com" "Testing real Slack integration" --slack-webhook "$SLACK_WEBHOOK_URL"
```

You should receive a formatted Slack message with:
- 🔐 Database access header
- Developer details
- Secure PrivateBin link
- Security warnings

## 🔗 PrivateBin Credential Viewing

### Current Issue & Fix

The PrivateBin integration currently uses demo URLs. Let's fix it to work with real credential storage:

#### Check PrivateBin Status
```bash
# Check if PrivateBin is working
curl -s http://localhost:8080 | grep -i privatebin

# Check container status
docker-compose ps privatebin
```

#### Fix PrivateBin Integration

The issue is with the API format. Let me create a working version:

```python
# Test PrivateBin manually
import requests
import json

# Simple text paste
data = {
    "data": "Test credential data",
    "expire": "1hour",
    "formatter": "plaintext",
    "burnafterreading": "1"
}

response = requests.post("http://localhost:8080/", data=data)
print(f"Status: {response.status_code}")
print(f"Response: {response.text[:200]}")
```

### 3. View Credentials in PrivateBin

Once you get a PrivateBin URL from the developer access script:

1. **Copy the URL** from the script output or Slack message
2. **Open in browser**: http://localhost:8080/?paste_id
3. **View once**: The credentials will display with:
   - Database connection details
   - Username/password
   - Expiration time
   - Security warnings
4. **Auto-destruct**: After viewing, the link becomes invalid

Example credential format you'll see:
```json
{
  "database_type": "mysql",
  "connection_details": {
    "host": "localhost",
    "port": 3306,
    "username": "v-token-mysql-role-abc123",
    "password": "temp-password-xyz",
    "database": "demo"
  },
  "security_info": {
    "expires_at": "2024-01-15T11:30:45",
    "auto_revoked": true,
    "vault_lease_id": "database/creds/mysql-role/abc123"
  },
  "usage_instructions": {
    "mysql": "mysql -h localhost -P 3306 -u username -ppassword demo"
  }
}
```

## 🔍 Complete Testing Workflow

### Test 1: End-to-End MySQL Access
```bash
# 1. Request access
python3 developer_access.py mysql "test@company.com" "Bug investigation #123" --slack-webhook "$SLACK_WEBHOOK_URL"

# 2. Check Slack for notification
# 3. Click PrivateBin link to view credentials
# 4. Use credentials to connect to MySQL:
mysql -h localhost -u [USERNAME_FROM_PASTE] -p[PASSWORD_FROM_PASTE] demo

# 5. Verify access works:
mysql> SHOW TABLES;
mysql> SELECT * FROM test_connection;
```

### Test 2: MongoDB Access
```bash
# 1. Request MongoDB access
python3 developer_access.py mongodb "test@company.com" "Data analysis task" --slack-webhook "$SLACK_WEBHOOK_URL"

# 2. Use credentials from PrivateBin link:
mongosh "mongodb://[USERNAME]:[PASSWORD]@localhost:27017/demo"

# 3. Verify access:
> show collections
> db.users.find()
```

### Test 3: Audit Trail Verification
```bash
# Check audit logs
cat access_requests_*.log | jq '.'

# Verify Vault leases
docker exec secure-database-query-execution-vault-1 sh -c 'export VAULT_ADDR=http://127.0.0.1:8200 && export VAULT_TOKEN=root-token && vault list sys/leases/lookup/database/creds'
```

## 🐛 Troubleshooting

### Slack Issues
- **Webhook not working**: Check URL format and workspace permissions
- **No message received**: Verify webhook URL and test with curl:
  ```bash
  curl -X POST -H 'Content-type: application/json' \
    --data '{"text":"Test message"}' \
    "$SLACK_WEBHOOK_URL"
  ```

### PrivateBin Issues
- **Container not running**: `docker-compose up -d privatebin`
- **API errors**: Check logs: `docker-compose logs privatebin`
- **Cannot view paste**: Ensure burn-after-reading hasn't been triggered

### Credential Issues
- **Access denied**: Check Vault lease hasn't expired
- **User not found**: Verify Vault role configuration
- **Connection failed**: Ensure database containers are healthy

## 📱 Mobile Testing

You can also test on your phone:
1. Join your test Slack workspace on mobile
2. Request credentials via the script
3. Tap the PrivateBin link in Slack
4. View credentials securely on mobile
5. Credentials auto-destruct after viewing

## 🔒 Security Verification

### What to Verify:
- ✅ Credentials appear only once in PrivateBin
- ✅ Link becomes invalid after viewing
- ✅ Credentials expire after 1 hour
- ✅ All access logged in audit files
- ✅ Vault automatically revokes users
- ✅ No credentials stored in Slack message history

This testing workflow ensures your zero-trust database access system works end-to-end with real Slack notifications and secure credential viewing! 🚀