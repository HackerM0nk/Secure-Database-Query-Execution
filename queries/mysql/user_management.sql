-- MySQL User Management Queries
-- For user administration and profile management

-- Create users table with additional fields
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    role ENUM('admin', 'user', 'viewer') DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_role (role)
);

-- Insert admin user
INSERT INTO users (username, email, first_name, last_name, role) VALUES
('admin', 'admin@company.com', 'System', 'Administrator', 'admin');

-- Insert regular users
INSERT INTO users (username, email, first_name, last_name, role) VALUES
('jdoe', 'john.doe@company.com', 'John', 'Doe', 'user'),
('jsmith', 'jane.smith@company.com', 'Jane', 'Smith', 'user'),
('bwilson', 'bob.wilson@company.com', 'Bob', 'Wilson', 'viewer');

-- Query active users by role
SELECT role, COUNT(*) as user_count
FROM users
WHERE is_active = TRUE
GROUP BY role;

-- Update user role
UPDATE users
SET role = 'admin', updated_at = CURRENT_TIMESTAMP
WHERE username = 'jdoe';

-- Deactivate user
UPDATE users
SET is_active = FALSE, updated_at = CURRENT_TIMESTAMP
WHERE username = 'bwilson';

-- Query user statistics
SELECT
    COUNT(*) as total_users,
    SUM(CASE WHEN is_active = TRUE THEN 1 ELSE 0 END) as active_users,
    SUM(CASE WHEN role = 'admin' THEN 1 ELSE 0 END) as admin_users
FROM users;