-- Test SQL file
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Test query
SELECT u.name, u.email
FROM users u
WHERE u.created_at >= DATE_SUB(CURRENT_DATE, INTERVAL 7 DAY)
ORDER BY u.created_at DESC; 