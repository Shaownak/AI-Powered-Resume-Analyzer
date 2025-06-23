-- PostgreSQL initialization script
-- This script runs when the database is first created

-- Create any additional databases or users if needed
-- The main database 'resume_screener' is created automatically

-- Grant all privileges to the postgres user
GRANT ALL PRIVILEGES ON DATABASE resume_screener TO postgres;

-- Create extensions if needed
\c resume_screener;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
