-- Migration: Create audit table for tracking database changes
-- Version: 001
-- Date: 2024-01-15
-- Author: Database Team

-- Create audit log table
CREATE TABLE IF NOT EXISTS audit_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    table_name VARCHAR(64) NOT NULL,
    operation ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
    old_values JSON,
    new_values JSON,
    user_id INT,
    username VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent TEXT,
    INDEX idx_table_operation (table_name, operation),
    INDEX idx_timestamp (timestamp),
    INDEX idx_user_id (user_id)
);

-- Create trigger for users table auditing
DELIMITER //

CREATE TRIGGER users_audit_insert
    AFTER INSERT ON users
    FOR EACH ROW
BEGIN
    INSERT INTO audit_log (table_name, operation, new_values, username)
    VALUES ('users', 'INSERT', JSON_OBJECT(
        'id', NEW.id,
        'username', NEW.username,
        'email', NEW.email,
        'role', NEW.role,
        'is_active', NEW.is_active
    ), USER());
END //

CREATE TRIGGER users_audit_update
    AFTER UPDATE ON users
    FOR EACH ROW
BEGIN
    INSERT INTO audit_log (table_name, operation, old_values, new_values, username)
    VALUES ('users', 'UPDATE',
        JSON_OBJECT(
            'id', OLD.id,
            'username', OLD.username,
            'email', OLD.email,
            'role', OLD.role,
            'is_active', OLD.is_active
        ),
        JSON_OBJECT(
            'id', NEW.id,
            'username', NEW.username,
            'email', NEW.email,
            'role', NEW.role,
            'is_active', NEW.is_active
        ),
        USER());
END //

CREATE TRIGGER users_audit_delete
    AFTER DELETE ON users
    FOR EACH ROW
BEGIN
    INSERT INTO audit_log (table_name, operation, old_values, username)
    VALUES ('users', 'DELETE', JSON_OBJECT(
        'id', OLD.id,
        'username', OLD.username,
        'email', OLD.email,
        'role', OLD.role,
        'is_active', OLD.is_active
    ), USER());
END //

DELIMITER ;

-- Verify audit table creation
SELECT COUNT(*) as audit_table_exists FROM information_schema.tables
WHERE table_schema = DATABASE() AND table_name = 'audit_log';

-- Show triggers created
SHOW TRIGGERS LIKE 'users';