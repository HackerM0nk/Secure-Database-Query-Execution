-- MySQL initialization script
-- This ensures the demo database and proper permissions are set up

-- Create demo database if it doesn't exist
CREATE DATABASE IF NOT EXISTS demo;

-- Use the demo database
USE demo;

-- Create a sample table for testing
CREATE TABLE IF NOT EXISTS test_connection (
    id INT AUTO_INCREMENT PRIMARY KEY,
    message VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert a test record
INSERT INTO test_connection (message) VALUES ('MySQL setup completed successfully')
ON DUPLICATE KEY UPDATE message = VALUES(message);

-- Show the setup result
SELECT 'MySQL demo database initialized' as status, COUNT(*) as test_records FROM test_connection;