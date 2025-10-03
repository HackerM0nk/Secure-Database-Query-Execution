# Secure Database Query Execution

A **Zero-Trust Database Access System** that eliminates the need for developers to have permanent database credentials. This project demonstrates how to safely execute database operations in CI/CD pipelines using ephemeral credentials managed by HashiCorp Vault.<img width="1940" height="1312" alt="image" src="https://github.com/user-attachments/assets/81e8481c-14d1-47b4-aac4-094d16f11381" />


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


