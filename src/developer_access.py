#!/usr/bin/env python3

import sys
import os
import json
import argparse
import logging
from datetime import datetime, timedelta
from vault_client import VaultClient
from simple_privatebin import create_credentials_link

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DeveloperAccessManager:
    def __init__(self, vault_client: VaultClient, privatebin_url: str = "http://localhost:8080"):
        self.vault = vault_client
        self.privatebin_url = privatebin_url

    def request_database_access(self, database_type: str, developer_email: str, justification: str) -> dict:
        """
        Generate ephemeral database credentials for developer access.

        Args:
            database_type: "mysql" or "mongodb"
            developer_email: Email of requesting developer
            justification: Business justification for access

        Returns:
            Dictionary with access details and PrivateBin URL
        """

        # Determine the Vault role based on database type
        role_mapping = {
            "mysql": "mysql-role",
            "mongodb": "mongodb-role"
        }

        if database_type not in role_mapping:
            raise ValueError(f"Unsupported database type: {database_type}")

        vault_role = role_mapping[database_type]

        try:
            # Request ephemeral credentials from Vault
            logger.info(f"Requesting {database_type} credentials for {developer_email}")
            username, password, lease_id = self.vault.get_database_credentials(vault_role)

            # Calculate expiration time (1 hour from now)
            expires_at = datetime.now() + timedelta(hours=1)

            # Determine connection details
            connection_details = {
                "mysql": {"host": "localhost", "port": 3306},
                "mongodb": {"host": "localhost", "port": 27017}
            }

            host = connection_details[database_type]["host"]
            port = connection_details[database_type]["port"]

            # Create secure credential link
            logger.info("Creating secure credential link")
            privatebin_url = create_credentials_link(
                username=username,
                password=password,
                database=database_type,
                host=host,
                port=port,
                lease_id=lease_id,
                expires_at=expires_at
            )

            # Prepare access record
            access_record = {
                "request_id": f"access-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                "developer_email": developer_email,
                "database_type": database_type,
                "justification": justification,
                "vault_lease_id": lease_id,
                "expires_at": expires_at.isoformat(),
                "privatebin_url": privatebin_url,
                "requested_at": datetime.now().isoformat(),
                "security_notes": {
                    "burn_after_reading": True,
                    "auto_expires": "1 hour",
                    "vault_revocation": "automatic",
                    "audit_logged": True
                }
            }

            # Log the access request for audit
            with open(f"access_requests_{datetime.now().strftime('%Y%m%d')}.log", "a") as f:
                audit_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "action": "credential_request",
                    "developer": developer_email,
                    "database": database_type,
                    "lease_id": lease_id,
                    "justification": justification,
                    "expires_at": expires_at.isoformat()
                }
                f.write(json.dumps(audit_entry) + "\n")

            logger.info(f"Access granted to {developer_email} for {database_type}")
            return access_record

        except Exception as e:
            logger.error(f"Failed to grant database access: {e}")
            raise

def send_slack_notification(access_record: dict, slack_webhook_url: str = None, slack_token: str = None) -> bool:
    """
    Send Slack DM with secure credential access link.

    Args:
        access_record: Dictionary with access details
        slack_webhook_url: Optional webhook URL for notifications
        slack_token: Optional Slack bot token for DMs

    Returns:
        Boolean indicating success
    """

    import requests

    # Extract key information
    developer_email = access_record["developer_email"]
    database_type = access_record["database_type"]
    privatebin_url = access_record["privatebin_url"]
    expires_at = access_record["expires_at"]

    # Format Slack message
    slack_message = {
        "text": f"🔐 Database Access Granted: {database_type}",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🔐 Secure Database Access - {database_type.upper()}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Developer:* {developer_email}\n*Database:* {database_type}\n*Expires:* {expires_at}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"🔗 *Secure Access Link:* <{privatebin_url}|Click here for one-time credentials>"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "⚠️ *Security Notice:*\n• Link self-destructs after viewing\n• Credentials auto-expire in 1 hour\n• All access is audited and logged"
                }
            }
        ]
    }

    try:
        if slack_webhook_url:
            # Send via webhook
            response = requests.post(slack_webhook_url, json=slack_message)
            if response.status_code == 200:
                logger.info(f"Slack notification sent to {developer_email}")
                return True
            else:
                logger.error(f"Slack webhook failed: {response.status_code}")
                return False

        elif slack_token:
            # Send via Slack API (would need user ID lookup)
            logger.warning("Slack API integration not implemented - use webhook URL")
            return False

        else:
            # For demo purposes, just log the message
            logger.info("=== SLACK MESSAGE (Demo Mode) ===")
            logger.info(json.dumps(slack_message, indent=2))
            logger.info("=== END SLACK MESSAGE ===")
            return True

    except Exception as e:
        logger.error(f"Failed to send Slack notification: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Request ephemeral database access for developers')
    parser.add_argument('database_type', choices=['mysql', 'mongodb'], help='Database type to access')
    parser.add_argument('developer_email', help='Email of requesting developer')
    parser.add_argument('justification', help='Business justification for access')
    parser.add_argument('--vault-url', default='http://localhost:8200', help='Vault URL')
    parser.add_argument('--privatebin-url', default='http://localhost:8080', help='PrivateBin URL')
    parser.add_argument('--slack-webhook', help='Slack webhook URL for notifications')

    args = parser.parse_args()

    try:
        # Initialize Vault client
        vault_client = VaultClient(vault_url=args.vault_url)
        access_manager = DeveloperAccessManager(vault_client, args.privatebin_url)

        # Request database access
        access_record = access_manager.request_database_access(
            database_type=args.database_type,
            developer_email=args.developer_email,
            justification=args.justification
        )

        # Send Slack notification
        slack_success = send_slack_notification(
            access_record=access_record,
            slack_webhook_url=args.slack_webhook
        )

        # Output summary
        print(json.dumps({
            "status": "success",
            "access_granted": True,
            "database_type": args.database_type,
            "developer_email": args.developer_email,
            "privatebin_url": access_record["privatebin_url"],
            "expires_at": access_record["expires_at"],
            "slack_notified": slack_success,
            "vault_lease_id": access_record["vault_lease_id"]
        }, indent=2))

    except Exception as e:
        logger.error(f"Access request failed: {e}")
        print(json.dumps({
            "status": "error",
            "error": str(e),
            "access_granted": False
        }, indent=2))
        sys.exit(1)

if __name__ == "__main__":
    main()