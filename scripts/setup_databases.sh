#!/bin/bash

# Complete database setup script
# This script ensures both MySQL and MongoDB are properly initialized

set -e

echo "🗄️  Setting up databases for secure query execution..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Setup MySQL
echo -e "${BLUE}📌 Setting up MySQL demo database...${NC}"

# Initialize MySQL with proper structure
docker exec -i secure-database-query-execution-mysql-1 mysql -u root -prootpass << 'EOF'
-- Ensure demo database exists
CREATE DATABASE IF NOT EXISTS demo;
USE demo;

-- Create test table to verify connection
CREATE TABLE IF NOT EXISTS test_connection (
    id INT AUTO_INCREMENT PRIMARY KEY,
    message VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert test record
INSERT INTO test_connection (message) VALUES ('MySQL ready for queries')
ON DUPLICATE KEY UPDATE message = VALUES(message), created_at = CURRENT_TIMESTAMP;

-- Show status
SELECT 'MySQL Demo Database Setup Complete' as status;
SHOW TABLES;
EOF

echo -e "${GREEN}✅ MySQL setup completed${NC}"

# 2. Setup MongoDB
echo -e "${BLUE}📌 Setting up MongoDB demo database...${NC}"

# Initialize MongoDB with test data if needed
docker exec secure-database-query-execution-mongo-1 mongosh demo --quiet --eval "
// Ensure demo database exists and has a test collection
if (db.test_connection.countDocuments() === 0) {
    db.test_connection.insertOne({
        message: 'MongoDB ready for queries',
        created_at: new Date()
    });
}

print('MongoDB Demo Database Setup Complete');
print('Collections:', db.getCollectionNames());
print('Test document count:', db.test_connection.countDocuments());
"

echo -e "${GREEN}✅ MongoDB setup completed${NC}"

# 3. Verify database connections
echo -e "${BLUE}📌 Verifying database connections...${NC}"

# MySQL verification
echo -e "${YELLOW}🐬 MySQL Verification:${NC}"
docker exec secure-database-query-execution-mysql-1 mysql -u root -prootpass demo -e "
SELECT 'MySQL Connection OK' as status, COUNT(*) as test_records FROM test_connection;
SHOW TABLES;
" 2>/dev/null

# MongoDB verification
echo -e "${YELLOW}🍃 MongoDB Verification:${NC}"
docker exec secure-database-query-execution-mongo-1 mongosh demo --quiet --eval "
print('MongoDB Connection OK');
print('Available collections:', db.getCollectionNames().join(', '));
print('Test records:', db.test_connection.countDocuments());
"

echo -e "${GREEN}🎉 Database setup completed successfully!${NC}"
echo ""
echo -e "${BLUE}📊 Quick Access Commands:${NC}"
echo "🐬 MySQL: docker exec -it secure-database-query-execution-mysql-1 mysql -u root -prootpass demo"
echo "🍃 MongoDB: docker exec -it secure-database-query-execution-mongo-1 mongosh demo"
echo ""
echo -e "${BLUE}🧪 Test Your Setup:${NC}"
echo "pip install -r requirements.txt"
echo "python request_creds_and_run.py mysql queries/mysql_queries.sql"
echo "python request_creds_and_run.py mongodb queries/mongodb_queries.json"