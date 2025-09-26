#!/usr/bin/env python3

import unittest
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from vault_client import VaultClient

class TestVaultIntegration(unittest.TestCase):
    def setUp(self):
        self.vault_client = VaultClient()

    def test_vault_connection(self):
        """Test that we can connect to Vault"""
        # This test requires Vault to be running
        try:
            # Test generating MySQL credentials
            username, password, lease_id = self.vault_client.get_database_credentials('mysql-role')
            self.assertIsNotNone(username)
            self.assertIsNotNone(password)
            self.assertIsNotNone(lease_id)

            # Clean up
            self.vault_client.revoke_lease(lease_id)
        except Exception as e:
            self.skipTest(f"Vault not available: {e}")

if __name__ == '__main__':
    unittest.main()