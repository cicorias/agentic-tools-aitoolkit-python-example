#!/bin/bash
set -e

echo "🚀 Initializing PostgreSQL Database..."

# Create the postgres database
echo "📦 Creating '$POSTGRES_DB_INVOICES' database..."
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE $POSTGRES_DB_INVOICES;
    GRANT ALL PRIVILEGES ON DATABASE $POSTGRES_DB_INVOICES TO $POSTGRES_USER;
EOSQL

# Install pgvector extension in the invoices database
echo "🔧 Installing pgvector extension in '$POSTGRES_DB_INVOICES' database..."
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB_INVOICES" <<-EOSQL
    CREATE EXTENSION IF NOT EXISTS vector;
EOSQL

# Load schema into the invoices database
echo "📋 Loading schema into '$POSTGRES_DB_INVOICES' database..."
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB_INVOICES" -f /docker-entrypoint-initdb.d/backups/schema.sql

# Load sample data into the invoices database
echo "📊 Loading sample data into '$POSTGRES_DB_INVOICES' database..."
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB_INVOICES" -f /docker-entrypoint-initdb.d/backups/sample_data.sql

echo "✅ Database initialization complete!"