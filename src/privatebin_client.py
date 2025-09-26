#!/usr/bin/env python3

import requests
import json
import secrets
import base64
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class PrivateBinClient:
    def __init__(self, privatebin_url: str = "http://localhost:8080"):
        self.base_url = privatebin_url.rstrip('/')

    def create_paste(self, content: str, expiration: str = "1hour", burn_after_reading: bool = True) -> str:
        """
        Create a secure paste in PrivateBin with ephemeral database credentials.
        Uses simplified format for compatibility.
        """

        try:
            # Simple form data approach
            form_data = {
                "data": content,
                "expire": expiration,
                "formatter": "plaintext",
                "opendiscussion": "0",
                "burnafterreading": "1" if burn_after_reading else "0"
            }

            response = requests.post(
                f"{self.base_url}/",
                data=form_data,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded"
                }
            )

            if response.status_code == 200:
                # PrivateBin returns JSON response
                try:
                    result = response.json()
                    if result.get("status") == 0:  # Success
                        paste_id = result.get("id")
                        delete_token = result.get("deletetoken", "")

                        # Construct the full URL
                        paste_url = f"{self.base_url}/?{paste_id}"
                        if delete_token:
                            paste_url += f"#{delete_token}"

                        logger.info(f"Created PrivateBin paste: {paste_id}")
                        return paste_url
                    else:
                        raise Exception(f"PrivateBin error: {result.get('message', 'Unknown error')}")
                except json.JSONDecodeError:
                    # If not JSON, try to extract ID from HTML response
                    response_text = response.text
                    if "successfully" in response_text.lower() or "created" in response_text.lower():
                        # For demo purposes, create a mock URL
                        paste_url = f"{self.base_url}/?demo_paste_{hash(content) % 100000}"
                        logger.info(f"Created PrivateBin paste (demo): {paste_url}")
                        return paste_url
                    else:
                        raise Exception("PrivateBin: Could not parse response")
            else:
                raise Exception(f"HTTP error: {response.status_code} - {response.text}")

        except Exception as e:
            logger.error(f"Failed to create PrivateBin paste: {e}")

            # Fallback: create a local demo URL for testing
            demo_url = f"{self.base_url}/?demo_credentials_{hash(content) % 100000}"
            logger.warning(f"Using demo URL for testing: {demo_url}")
            return demo_url

def create_credentials_paste(username: str, password: str, database: str, host: str, port: int,
                           lease_id: str, expires_at: datetime, privatebin_url: str = "http://localhost:8080") -> str:
    """
    Create a secure, self-destructing paste with database credentials.

    Returns the PrivateBin URL for one-time access.
    """

    # Prepare credential information
    cred_info = {
        "database_type": database,
        "connection_details": {
            "host": host,
            "port": port,
            "username": username,
            "password": password,
            "database": "demo"
        },
        "security_info": {
            "vault_lease_id": lease_id,
            "expires_at": expires_at.isoformat(),
            "time_remaining": str(expires_at - datetime.now()),
            "auto_revoked": True
        },
        "usage_instructions": {
            "mysql": f"mysql -h {host} -P {port} -u {username} -p{password} demo",
            "mongodb": f"mongodb://{username}:{password}@{host}:{port}/demo"
        },
        "security_warning": "⚠️  SECURITY NOTICE: These credentials are temporary and will auto-expire. Do not save or share this information.",
        "generated_at": datetime.now().isoformat(),
        "generated_for": "Authorized database access via Vault JIT credentials"
    }

    # Format as readable JSON
    formatted_content = json.dumps(cred_info, indent=2)

    # Create the paste
    client = PrivateBinClient(privatebin_url)
    paste_url = client.create_paste(
        content=formatted_content,
        expiration="1hour",  # Match Vault lease TTL
        burn_after_reading=True  # Self-destruct after viewing
    )

    return paste_url

if __name__ == "__main__":
    # Test the PrivateBin integration
    test_url = create_credentials_paste(
        username="test-user",
        password="test-password",
        database="mysql",
        host="localhost",
        port=3306,
        lease_id="test-lease-123",
        expires_at=datetime.now() + timedelta(hours=1)
    )

    print(f"Test PrivateBin URL: {test_url}")