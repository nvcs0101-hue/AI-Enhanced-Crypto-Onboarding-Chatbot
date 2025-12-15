#!/bin/bash

# Database Restore Script
# Usage: ./restore-database.sh <backup_timestamp> [source]
# Example: ./restore-database.sh 20241215_020000 local
#          ./restore-database.sh 20241215_020000 s3

set -e

# Configuration
BACKUP_DIR="${BACKUP_DIR:-/app/backups}"
CHROMA_DIR="${CHROMA_PERSIST_DIRECTORY:-/app/data/chroma_db}"
POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_USER="${POSTGRES_USER:-postgres}"
POSTGRES_DB="${POSTGRES_DB:-chatbot_analytics}"
S3_BUCKET="${S3_BUCKET:-}"

# Parse arguments
TIMESTAMP="$1"
SOURCE="${2:-local}"

if [ -z "$TIMESTAMP" ]; then
    echo "❌ Error: Timestamp required"
    echo "Usage: $0 <backup_timestamp> [local|s3]"
    echo ""
    echo "Available backups:"
    ls -1 "$BACKUP_DIR" | grep -E "backup_[0-9]+_[0-9]+\.(tar\.gz|sql\.gz)" || echo "  (none found)"
    exit 1
fi

echo "=========================================="
echo "🔄 Database Restore - $TIMESTAMP"
echo "=========================================="
echo ""

# Confirmation
read -p "⚠️  WARNING: This will overwrite existing data. Continue? (yes/no): " -r
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "❌ Restore cancelled"
    exit 0
fi
echo ""

# Download from S3 if needed
if [ "$SOURCE" = "s3" ]; then
    if [ -z "$S3_BUCKET" ]; then
        echo "❌ Error: S3_BUCKET not configured"
        exit 1
    fi
    
    echo "☁️  Downloading backups from S3..."
    aws s3 cp "s3://$S3_BUCKET/backups/chroma/chroma_backup_$TIMESTAMP.tar.gz" "$BACKUP_DIR/"
    aws s3 cp "s3://$S3_BUCKET/backups/postgres/postgres_backup_$TIMESTAMP.sql.gz" "$BACKUP_DIR/" || true
    echo "✅ Backups downloaded"
    echo ""
fi

# 1. Restore ChromaDB
CHROMA_BACKUP="$BACKUP_DIR/chroma_backup_$TIMESTAMP.tar.gz"
if [ -f "$CHROMA_BACKUP" ]; then
    echo "📦 Restoring ChromaDB..."
    
    # Backup current data
    if [ -d "$CHROMA_DIR" ]; then
        echo "   Creating safety backup of current data..."
        mv "$CHROMA_DIR" "${CHROMA_DIR}_before_restore_$(date +%Y%m%d_%H%M%S)"
    fi
    
    # Extract backup
    mkdir -p "$(dirname "$CHROMA_DIR")"
    tar -xzf "$CHROMA_BACKUP" -C "$(dirname "$CHROMA_DIR")"
    
    echo "✅ ChromaDB restored successfully"
else
    echo "⚠️  ChromaDB backup not found: $CHROMA_BACKUP"
fi
echo ""

# 2. Restore PostgreSQL
POSTGRES_BACKUP="$BACKUP_DIR/postgres_backup_$TIMESTAMP.sql.gz"
if [ -f "$POSTGRES_BACKUP" ]; then
    echo "📦 Restoring PostgreSQL..."
    
    export PGPASSWORD="$POSTGRES_PASSWORD"
    
    # Drop and recreate database
    echo "   Recreating database..."
    psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d postgres <<EOF
DROP DATABASE IF EXISTS ${POSTGRES_DB}_restore_backup;
CREATE DATABASE ${POSTGRES_DB}_restore_backup WITH TEMPLATE ${POSTGRES_DB};
DROP DATABASE ${POSTGRES_DB};
CREATE DATABASE ${POSTGRES_DB};
EOF
    
    # Restore from backup
    echo "   Restoring data..."
    gunzip < "$POSTGRES_BACKUP" | psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB"
    
    unset PGPASSWORD
    
    echo "✅ PostgreSQL restored successfully"
    echo "   Backup of previous data available as: ${POSTGRES_DB}_restore_backup"
else
    echo "⏭️  PostgreSQL backup not found (skipping)"
fi
echo ""

# 3. Verify restore
echo "🔍 Verifying restore..."

# Check ChromaDB
if [ -d "$CHROMA_DIR" ]; then
    CHROMA_SIZE=$(du -sh "$CHROMA_DIR" | cut -f1)
    echo "✅ ChromaDB directory exists: $CHROMA_SIZE"
else
    echo "❌ ChromaDB directory not found!"
    exit 1
fi

# Check PostgreSQL connection
if command -v psql >/dev/null 2>&1; then
    export PGPASSWORD="$POSTGRES_PASSWORD"
    if psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT 1" > /dev/null 2>&1; then
        echo "✅ PostgreSQL connection successful"
    else
        echo "❌ PostgreSQL connection failed!"
    fi
    unset PGPASSWORD
fi
echo ""

# 4. Restart services
echo "🔄 Restarting services..."
if command -v docker-compose >/dev/null 2>&1; then
    docker-compose restart backend telegram-bot discord-bot
    echo "✅ Services restarted"
else
    echo "⚠️  Please restart services manually"
fi
echo ""

echo "=========================================="
echo "✅ Restore Complete!"
echo "=========================================="
echo ""
echo "📝 Next steps:"
echo "  1. Verify application is working"
echo "  2. Test critical functionality"
echo "  3. Monitor logs for errors"
echo "  4. Remove backup databases if everything works"
echo ""
echo "🗂️  Safety backups created:"
echo "  • ChromaDB: ${CHROMA_DIR}_before_restore_*"
echo "  • PostgreSQL: ${POSTGRES_DB}_restore_backup"
echo ""
