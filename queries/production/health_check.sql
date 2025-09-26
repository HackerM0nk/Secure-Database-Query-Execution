-- Production Health Check Queries
-- Run these to verify database health and performance

-- Check database connection and basic info
SELECT
    'Database Health Check' as check_type,
    DATABASE() as current_database,
    VERSION() as mysql_version,
    NOW() as current_time,
    CONNECTION_ID() as connection_id;

-- Check table sizes and row counts
SELECT
    table_name,
    table_rows,
    ROUND(((data_length + index_length) / 1024 / 1024), 2) as size_mb
FROM information_schema.tables
WHERE table_schema = DATABASE()
ORDER BY (data_length + index_length) DESC;

-- Check active processes
SELECT
    COUNT(*) as active_connections,
    SUM(CASE WHEN command != 'Sleep' THEN 1 ELSE 0 END) as active_queries
FROM information_schema.processlist;

-- Check for long-running queries
SELECT
    id,
    user,
    host,
    db,
    command,
    time as duration_seconds,
    LEFT(info, 50) as query_preview
FROM information_schema.processlist
WHERE command != 'Sleep' AND time > 30
ORDER BY time DESC;

-- Check InnoDB status
SELECT
    'InnoDB Buffer Pool' as metric,
    VARIABLE_VALUE as value
FROM information_schema.global_status
WHERE VARIABLE_NAME IN (
    'INNODB_BUFFER_POOL_PAGES_TOTAL',
    'INNODB_BUFFER_POOL_PAGES_FREE',
    'INNODB_BUFFER_POOL_PAGES_DATA'
);

-- Check error log for recent issues (last 100 entries)
SELECT
    'Recent Errors Check' as check_type,
    'Check MySQL error log manually' as recommendation;

-- Performance metrics
SELECT
    'Performance Metrics' as metric_group,
    'Queries per second' as metric,
    ROUND(
        (SELECT VARIABLE_VALUE FROM information_schema.global_status WHERE VARIABLE_NAME = 'Queries') /
        (SELECT VARIABLE_VALUE FROM information_schema.global_status WHERE VARIABLE_NAME = 'Uptime'),
        2
    ) as value;

-- Check replication status (if applicable)
SHOW SLAVE STATUS;