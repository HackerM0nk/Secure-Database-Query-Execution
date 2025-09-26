#!/usr/bin/env python3

import requests
import json
import time

def setup_vault_with_api():
    """Configure Vault using HTTP API instead of CLI"""

    base_url = "http://localhost:8200/v1"
    headers = {"X-Vault-Token": "root-token"}

    print("🏛️  Configuring Vault database secrets engine...")

    # 1. Enable database secrets engine
    print("📌 Enabling database secrets engine...")
    response = requests.post(
        f"{base_url}/sys/mounts/database",
        headers=headers,
        json={
            "type": "database",
            "description": "Database secrets engine"
        }
    )
    if response.status_code in [200, 204]:
        print("✅ Database secrets engine enabled")
    else:
        print(f"ℹ️  Database secrets engine already enabled or error: {response.status_code}")

    # 2. Configure MySQL database connection
    print("📌 Configuring MySQL database connection...")
    mysql_config = {
        "plugin_name": "mysql-database-plugin",
        "connection_url": "{{username}}:{{password}}@tcp(mysql:3306)/",
        "allowed_roles": ["mysql-role"],
        "username": "root",
        "password": "rootpass"
    }

    response = requests.post(
        f"{base_url}/database/config/mysql-database",
        headers=headers,
        json=mysql_config
    )

    if response.status_code in [200, 204]:
        print("✅ MySQL database configured")
    else:
        print(f"❌ MySQL config failed: {response.status_code} - {response.text}")

    # 3. Create MySQL role
    print("📌 Creating MySQL role...")
    mysql_role = {
        "db_name": "mysql-database",
        "creation_statements": [
            "CREATE USER '{{name}}'@'%' IDENTIFIED BY '{{password}}';",
            "GRANT SELECT, INSERT, UPDATE, DELETE ON demo.* TO '{{name}}'@'%';"
        ],
        "default_ttl": "1h",
        "max_ttl": "24h"
    }

    response = requests.post(
        f"{base_url}/database/roles/mysql-role",
        headers=headers,
        json=mysql_role
    )

    if response.status_code in [200, 204]:
        print("✅ MySQL role created")
    else:
        print(f"❌ MySQL role failed: {response.status_code} - {response.text}")

    # 4. Configure MongoDB database connection
    print("📌 Configuring MongoDB database connection...")
    mongo_config = {
        "plugin_name": "mongodb-database-plugin",
        "connection_url": "mongodb://mongo:27017/demo",
        "allowed_roles": ["mongodb-role"]
    }

    response = requests.post(
        f"{base_url}/database/config/mongodb-database",
        headers=headers,
        json=mongo_config
    )

    if response.status_code in [200, 204]:
        print("✅ MongoDB database configured")
    else:
        print(f"❌ MongoDB config failed: {response.status_code} - {response.text}")

    # 5. Create MongoDB role
    print("📌 Creating MongoDB role...")
    mongo_role = {
        "db_name": "mongodb-database",
        "creation_statements": ['{"db": "demo", "roles": [{"role": "readWrite"}]}'],
        "default_ttl": "1h",
        "max_ttl": "24h"
    }

    response = requests.post(
        f"{base_url}/database/roles/mongodb-role",
        headers=headers,
        json=mongo_role
    )

    if response.status_code in [200, 204]:
        print("✅ MongoDB role created")
    else:
        print(f"❌ MongoDB role failed: {response.status_code} - {response.text}")

    # 6. Test credential generation
    print("\n🧪 Testing credential generation...")

    # Test MySQL credentials
    response = requests.get(f"{base_url}/database/creds/mysql-role", headers=headers)
    if response.status_code == 200:
        creds = response.json()
        print(f"✅ MySQL test credentials: {creds['data']['username']}")

        # Revoke the test lease
        lease_id = creds['lease_id']
        requests.put(f"{base_url}/sys/leases/revoke", headers=headers, json={"lease_id": lease_id})
    else:
        print(f"❌ MySQL credential test failed: {response.status_code}")

    # Test MongoDB credentials
    response = requests.get(f"{base_url}/database/creds/mongodb-role", headers=headers)
    if response.status_code == 200:
        creds = response.json()
        print(f"✅ MongoDB test credentials: {creds['data']['username']}")

        # Revoke the test lease
        lease_id = creds['lease_id']
        requests.put(f"{base_url}/sys/leases/revoke", headers=headers, json={"lease_id": lease_id})
    else:
        print(f"❌ MongoDB credential test failed: {response.status_code}")

    print("\n🎉 Vault configuration completed!")
    print("\n📊 Access Information:")
    print("🏛️  Vault UI: http://localhost:8200/ui")
    print("   Token: root-token")
    print("🐬 MySQL: localhost:3306 (root/rootpass)")
    print("🍃 MongoDB: localhost:27017")

if __name__ == "__main__":
    setup_vault_with_api()