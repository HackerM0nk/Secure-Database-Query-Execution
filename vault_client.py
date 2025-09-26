import hvac
import os
import logging
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)

class VaultClient:
    def __init__(self, vault_url: str = "http://localhost:8200", token: str = None):
        self.vault_url = vault_url
        self.token = token or os.getenv("VAULT_TOKEN", "root-token")
        self.client = hvac.Client(url=vault_url, token=self.token)

        if not self.client.is_authenticated():
            raise Exception("Failed to authenticate with Vault")

    def get_database_credentials(self, role_name: str) -> Tuple[str, str, str]:
        """
        Request ephemeral database credentials from Vault.
        Returns: (username, password, lease_id)
        """
        try:
            response = self.client.secrets.database.generate_credentials(name=role_name)

            username = response['data']['username']
            password = response['data']['password']
            lease_id = response['lease_id']

            logger.info(f"Generated credentials for role {role_name}, lease_id: {lease_id}")
            return username, password, lease_id

        except Exception as e:
            logger.error(f"Failed to get credentials for role {role_name}: {e}")
            raise

    def revoke_lease(self, lease_id: str) -> bool:
        """
        Revoke a Vault lease to clean up ephemeral credentials.
        """
        try:
            self.client.sys.revoke_lease(lease_id=lease_id)
            logger.info(f"Successfully revoked lease: {lease_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to revoke lease {lease_id}: {e}")
            return False

    def configure_mysql_database(self, connection_url: str, username: str, password: str):
        """
        Configure MySQL database connection in Vault.
        """
        try:
            # Enable database secrets engine if not already enabled
            self.client.sys.enable_secrets_engine(backend_type='database')

            # Configure MySQL connection
            self.client.secrets.database.configure(
                name='mysql-database',
                plugin_name='mysql-database-plugin',
                connection_url=connection_url,
                allowed_roles=['mysql-role'],
                username=username,
                password=password
            )

            # Create role for MySQL
            self.client.secrets.database.create_role(
                name='mysql-role',
                db_name='mysql-database',
                creation_statements=[
                    "CREATE USER '{{name}}'@'%' IDENTIFIED BY '{{password}}';",
                    "GRANT SELECT, INSERT, UPDATE, DELETE ON demo.* TO '{{name}}'@'%';"
                ],
                default_ttl='1h',
                max_ttl='24h'
            )

            logger.info("MySQL database configured successfully in Vault")

        except Exception as e:
            logger.error(f"Failed to configure MySQL database: {e}")
            raise

    def configure_mongodb_database(self, connection_url: str, username: str = None, password: str = None):
        """
        Configure MongoDB database connection in Vault.
        """
        try:
            # Configure MongoDB connection
            self.client.secrets.database.configure(
                name='mongodb-database',
                plugin_name='mongodb-database-plugin',
                connection_url=connection_url,
                allowed_roles=['mongodb-role'],
                username=username,
                password=password
            )

            # Create role for MongoDB
            self.client.secrets.database.create_role(
                name='mongodb-role',
                db_name='mongodb-database',
                creation_statements=[
                    '{"db": "demo", "roles": [{"role": "readWrite"}]}'
                ],
                default_ttl='1h',
                max_ttl='24h'
            )

            logger.info("MongoDB database configured successfully in Vault")

        except Exception as e:
            logger.error(f"Failed to configure MongoDB database: {e}")
            raise