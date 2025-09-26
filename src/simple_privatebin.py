#!/usr/bin/env python3

import json
import base64
import secrets
import os
from datetime import datetime, timedelta
from typing import Dict, Optional

class SimplePrivateBin:
    """
    Simple implementation of secure credential sharing with auto-expiration.
    Creates local files that self-destruct after viewing or time expiration.
    """

    def __init__(self, storage_dir: str = "./privatebin-data"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)

    def create_secure_paste(self, content: str, ttl_hours: int = 1, burn_after_reading: bool = True) -> str:
        """
        Create a secure, self-destructing paste with credentials.

        Returns:
            URL to access the paste once
        """

        # Generate random paste ID
        paste_id = secrets.token_urlsafe(16)

        # Create paste metadata
        paste_data = {
            "content": content,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=ttl_hours)).isoformat(),
            "burn_after_reading": burn_after_reading,
            "accessed": False
        }

        # Store paste
        paste_file = os.path.join(self.storage_dir, f"{paste_id}.json")
        with open(paste_file, 'w') as f:
            json.dump(paste_data, f)

        # Return access URL
        return f"http://localhost:8080/view/{paste_id}"

    def retrieve_paste(self, paste_id: str) -> Optional[Dict]:
        """
        Retrieve and potentially destroy a paste.
        """

        paste_file = os.path.join(self.storage_dir, f"{paste_id}.json")

        if not os.path.exists(paste_file):
            return None

        try:
            with open(paste_file, 'r') as f:
                paste_data = json.load(f)

            # Check expiration
            expires_at = datetime.fromisoformat(paste_data["expires_at"])
            if datetime.now() > expires_at:
                os.remove(paste_file)  # Expired, remove
                return None

            # Check if already accessed and burn_after_reading is true
            if paste_data["accessed"] and paste_data["burn_after_reading"]:
                os.remove(paste_file)  # Already burned
                return None

            # Mark as accessed
            if paste_data["burn_after_reading"]:
                paste_data["accessed"] = True
                if os.path.exists(paste_file):  # Double-check before writing
                    with open(paste_file, 'w') as f:
                        json.dump(paste_data, f)

                    # If burn after reading, delete immediately after marking
                    os.remove(paste_file)

            return {
                "content": paste_data["content"],
                "created_at": paste_data["created_at"],
                "expires_at": paste_data["expires_at"],
                "burned": paste_data["burn_after_reading"]
            }

        except Exception as e:
            # If any error, remove the file for security
            if os.path.exists(paste_file):
                os.remove(paste_file)
            return None

def create_credentials_link(username: str, password: str, database: str, host: str, port: int,
                          lease_id: str, expires_at: datetime) -> str:
    """
    Create a secure link for database credentials using simple PrivateBin.
    """

    # Format credentials nicely
    credentials = {
        "🔐 Database Access Credentials": {
            "database_type": database.upper(),
            "connection_info": {
                "host": host,
                "port": port,
                "database": "demo",
                "username": username,
                "password": password
            },
            "security_info": {
                "vault_lease_id": lease_id,
                "expires_at": expires_at.strftime("%Y-%m-%d %H:%M:%S UTC"),
                "time_remaining": str(expires_at - datetime.now()).split('.')[0],
                "auto_revoked": "Yes - Vault will automatically remove this user"
            },
            "connection_examples": {
                "mysql": f"mysql -h {host} -P {port} -u {username} -p'{password}' demo",
                "mongodb": f"mongodb://{username}:{password}@{host}:{port}/demo"
            },
            "⚠️ SECURITY WARNINGS": [
                "These credentials are TEMPORARY and will expire automatically",
                "This link will self-destruct after you view it",
                "Do NOT save or share these credentials",
                "All database access is logged and audited",
                "Report any suspicious activity immediately"
            ]
        }
    }

    # Create formatted content
    content = json.dumps(credentials, indent=2)

    # Create secure paste
    pb = SimplePrivateBin()
    secure_url = pb.create_secure_paste(
        content=content,
        ttl_hours=1,
        burn_after_reading=True
    )

    return secure_url

if __name__ == "__main__":
    # Test the simple PrivateBin
    pb = SimplePrivateBin()

    test_content = "Test secret content that should self-destruct"
    url = pb.create_secure_paste(test_content)

    print(f"Created secure paste: {url}")

    # Test retrieval
    paste_id = url.split('/')[-1]
    retrieved = pb.retrieve_paste(paste_id)

    if retrieved:
        print("Retrieved content:", retrieved["content"])
        print("Burned:", retrieved["burned"])
    else:
        print("Paste not found or already destroyed")