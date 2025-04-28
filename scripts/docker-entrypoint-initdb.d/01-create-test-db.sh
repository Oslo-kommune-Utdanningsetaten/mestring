#!/bin/bash
set -e

echo "Creating test database and granting permissions..."

# Create test database
mysql -u root -p"$MARIADB_ROOT_PASSWORD" <<-EOSQL
CREATE DATABASE IF NOT EXISTS test_mastery CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
GRANT ALL PRIVILEGES ON test_mastery.* TO '$MYSQL_USER'@'%';
GRANT CREATE, ALTER, DROP ON *.* TO '$MYSQL_USER'@'%';
FLUSH PRIVILEGES;
EOSQL

echo "Test database setup complete!"
