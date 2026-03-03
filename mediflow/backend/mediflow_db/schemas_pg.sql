# ============================================================
#  crimson/mediflow_db/schemas_pg.sql
#  Raw SQL alternative — run this directly in psql if needed
# ============================================================

-- Create database (run as superuser)
CREATE DATABASE "MEDIFLOW_DB";

-- Connect to database then run:
CREATE SCHEMA IF NOT EXISTS organization;
CREATE SCHEMA IF NOT EXISTS users;
CREATE SCHEMA IF NOT EXISTS scheduling;
CREATE SCHEMA IF NOT EXISTS queue;
CREATE SCHEMA IF NOT EXISTS analytics;

-- Create a dedicated role
CREATE ROLE mediflow_user WITH LOGIN PASSWORD 'mediflow_pass';
GRANT ALL PRIVILEGES ON DATABASE "MEDIFLOW_DB" TO mediflow_user;
GRANT ALL ON SCHEMA organization, users, scheduling, queue, analytics TO mediflow_user;
