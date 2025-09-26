-- Basic MySQL Examples for Testing
-- These queries demonstrate the secure execution system

-- Create a test table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data
INSERT INTO users (username, email) VALUES
('john_doe', 'john@example.com'),
('jane_smith', 'jane@example.com'),
('bob_wilson', 'bob@example.com');

-- Query to select all users
SELECT * FROM users;

-- Query to count users
SELECT COUNT(*) as total_users FROM users;

-- Update a user's email
UPDATE users SET email = 'john.doe@newdomain.com' WHERE username = 'john_doe';

-- Query to select updated user
SELECT * FROM users WHERE username = 'john_doe';