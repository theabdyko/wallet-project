-- PostgreSQL initialization script for Wallet Project
-- This script runs when the PostgreSQL container starts for the first time

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Set timezone
SET timezone = 'UTC';

-- Create additional databases for different environments
-- Development
CREATE DATABASE wallet_db_dev WITH OWNER = wallet_user ENCODING = 'UTF8' LC_COLLATE = 'C' LC_CTYPE = 'C';

-- Staging
CREATE DATABASE wallet_db_staging WITH OWNER = wallet_user ENCODING = 'UTF8' LC_COLLATE = 'C' LC_CTYPE = 'C';

-- Production (read-only for safety)
CREATE DATABASE wallet_db_prod WITH OWNER = wallet_user ENCODING = 'UTF8' LC_COLLATE = 'C' LC_CTYPE = 'C';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE wallet_db TO wallet_user;
GRANT ALL PRIVILEGES ON DATABASE wallet_db_dev TO wallet_user;
GRANT ALL PRIVILEGES ON DATABASE wallet_db_staging TO wallet_user;
GRANT ALL PRIVILEGES ON DATABASE wallet_db_prod TO wallet_user;

-- Set connection limits and other configurations
ALTER USER wallet_user CONNECTION LIMIT 50;
ALTER USER wallet_user SET default_transaction_isolation = 'read committed';
ALTER USER wallet_user SET default_transaction_read_only = false;
