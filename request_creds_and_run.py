#!/usr/bin/env python3

import sys
import os
import json
import logging
import argparse
from datetime import datetime
import mysql.connector
import pymongo
from vault_client import VaultClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseQueryExecutor:
    def __init__(self, vault_client: VaultClient):
        self.vault = vault_client
        self.lease_id = None
        self.results = {}

    def execute_mysql_queries(self, query_file: str) -> dict:
        """
        Execute MySQL queries using ephemeral credentials from Vault.
        """
        username, password, self.lease_id = self.vault.get_database_credentials('mysql-role')

        results = {
            'database': 'mysql',
            'timestamp': datetime.now().isoformat(),
            'lease_id': self.lease_id,
            'queries': []
        }

        try:
            connection = mysql.connector.connect(
                host='localhost',
                port=3306,
                user=username,
                password=password,
                database='demo'
            )

            cursor = connection.cursor(dictionary=True)

            with open(query_file, 'r') as f:
                queries = f.read().strip().split(';')

            for i, query in enumerate(queries):
                query = query.strip()
                if not query:
                    continue

                query_result = {
                    'query_index': i,
                    'query': query,
                    'status': 'success',
                    'rows_affected': 0,
                    'data': []
                }

                try:
                    cursor.execute(query)

                    if cursor.description:
                        query_result['data'] = cursor.fetchall()
                        query_result['rows_affected'] = cursor.rowcount
                    else:
                        query_result['rows_affected'] = cursor.rowcount

                    connection.commit()
                    logger.info(f"MySQL query {i} executed successfully")

                except Exception as e:
                    query_result['status'] = 'error'
                    query_result['error'] = str(e)
                    logger.error(f"MySQL query {i} failed: {e}")

                results['queries'].append(query_result)

        except Exception as e:
            logger.error(f"MySQL connection failed: {e}")
            results['connection_error'] = str(e)
            raise
        finally:
            if 'connection' in locals():
                connection.close()

        return results

    def execute_mongodb_queries(self, query_file: str) -> dict:
        """
        Execute MongoDB queries using ephemeral credentials from Vault.
        """
        username, password, self.lease_id = self.vault.get_database_credentials('mongodb-role')

        results = {
            'database': 'mongodb',
            'timestamp': datetime.now().isoformat(),
            'lease_id': self.lease_id,
            'queries': []
        }

        try:
            connection_string = f"mongodb://{username}:{password}@localhost:27017/demo"
            client = pymongo.MongoClient(connection_string)
            db = client.demo

            with open(query_file, 'r') as f:
                queries = json.load(f)

            for i, query_def in enumerate(queries):
                query_result = {
                    'query_index': i,
                    'operation': query_def.get('operation'),
                    'collection': query_def.get('collection'),
                    'status': 'success',
                    'data': []
                }

                try:
                    collection = db[query_def['collection']]
                    operation = query_def['operation']

                    if operation == 'find':
                        filter_query = query_def.get('filter', {})
                        cursor = collection.find(filter_query)
                        query_result['data'] = list(cursor)

                    elif operation == 'insert_one':
                        document = query_def['document']
                        result = collection.insert_one(document)
                        query_result['inserted_id'] = str(result.inserted_id)

                    elif operation == 'update_one':
                        filter_query = query_def['filter']
                        update_doc = query_def['update']
                        result = collection.update_one(filter_query, update_doc)
                        query_result['modified_count'] = result.modified_count

                    elif operation == 'delete_one':
                        filter_query = query_def['filter']
                        result = collection.delete_one(filter_query)
                        query_result['deleted_count'] = result.deleted_count

                    logger.info(f"MongoDB query {i} executed successfully")

                except Exception as e:
                    query_result['status'] = 'error'
                    query_result['error'] = str(e)
                    logger.error(f"MongoDB query {i} failed: {e}")

                results['queries'].append(query_result)

        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
            results['connection_error'] = str(e)
            raise
        finally:
            if 'client' in locals():
                client.close()

        return results

    def save_results(self, results: dict, output_file: str = None):
        """
        Save query execution results to file.
        """
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"query_results_{results['database']}_{timestamp}.json"

        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        logger.info(f"Results saved to {output_file}")
        return output_file

    def cleanup(self):
        """
        Revoke Vault lease to clean up ephemeral credentials.
        """
        if self.lease_id:
            success = self.vault.revoke_lease(self.lease_id)
            if success:
                logger.info("Vault lease revoked successfully")
            else:
                logger.warning("Failed to revoke Vault lease")

def main():
    parser = argparse.ArgumentParser(description='Execute database queries using Vault ephemeral credentials')
    parser.add_argument('target_db', choices=['mysql', 'mongodb'], help='Target database type')
    parser.add_argument('query_file', help='Path to query file')
    parser.add_argument('--vault-url', default='http://localhost:8200', help='Vault URL')
    parser.add_argument('--output', help='Output file for results')

    args = parser.parse_args()

    executor = None
    exit_code = 0

    try:
        vault_client = VaultClient(vault_url=args.vault_url)
        executor = DatabaseQueryExecutor(vault_client)

        if args.target_db == 'mysql':
            results = executor.execute_mysql_queries(args.query_file)
        elif args.target_db == 'mongodb':
            results = executor.execute_mongodb_queries(args.query_file)

        output_file = executor.save_results(results, args.output)

        # Check if any queries failed
        failed_queries = [q for q in results['queries'] if q['status'] == 'error']
        if failed_queries:
            logger.error(f"{len(failed_queries)} queries failed")
            exit_code = 1
        else:
            logger.info("All queries executed successfully")

        # Store lease_id in environment for potential use by subsequent jobs
        if executor.lease_id:
            os.environ['VAULT_LEASE_ID'] = executor.lease_id
            with open('.lease_id', 'w') as f:
                f.write(executor.lease_id)

    except Exception as e:
        logger.error(f"Job failed: {e}")
        exit_code = 1
    finally:
        if executor:
            executor.cleanup()

    sys.exit(exit_code)

if __name__ == "__main__":
    main()