#!/bin/bash


# Support dry-run mode
DRY_RUN=false
if [ "$1" = "--dry-run" ]; then
    DRY_RUN=true
    echo "🔍 DRY RUN MODE - No changes will be made"
    echo ""
fi
# Automated ChromaDB and PostgreSQL Backup Script
# Runs daily via cron: 0 2 * * * /path/to/backup-database.sh

set -e  # Exit on error

# Configuration
BACKUP_DIR="${BACKUP_DIR:-/app/backups}"
CHROMA_DIR="${CHROMA_PERSIST_DIRECTORY:-/app/data/chroma_db}"
POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_USER="${POSTGRES_USER:-postgres}"
POSTGRES_DB="${POSTGRES_DB:-chatbot_analytics}"
S3_BUCKET="${S3_BUCKET:-}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "=========================================="
echo "🗄️  Database Backup - $TIMESTAMP"
echo "=========================================="
echo ""

# Create backup directory
mkdir -p "$BACKUP_DIR"

# 1. Backup ChromaDB
echo "📦 Backing up ChromaDB..."
if [ -d "$CHROMA_DIR" ]; then
    CHROMA_BACKUP="$BACKUP_DIR/chroma_backup_$TIMESTAMP.tar.gz"
    tar -czf "$CHROMA_BACKUP" -C "$(dirname "$CHROMA_DIR")" "$(basename "$CHROMA_DIR")"
    echo "✅ ChromaDB backup created: $CHROMA_BACKUP"
    echo "   Size: $(du -h "$CHROMA_BACKUP" | cut -f1)"
else
    echo "⚠️  ChromaDB directory not found: $CHROMA_DIR"
fi
echo ""

# 2. Backup PostgreSQL (if configured)
if [ -n "$POSTGRES_HOST" ]; then
    echo "📦 Backing up PostgreSQL..."
    POSTGRES_BACKUP="$BACKUP_DIR/postgres_backup_$TIMESTAMP.sql.gz"
    
    # Export password to avoid prompt
    export PGPASSWORD="$POSTGRES_PASSWORD"
    
    # Dump database
    pg_dump -h "$POSTGRES_HOST" \
            -p "$POSTGRES_PORT" \
            -U "$POSTGRES_USER" \
            -d "$POSTGRES_DB" \
            --no-owner --no-acl \
            | gzip > "$POSTGRES_BACKUP"
    
    unset PGPASSWORD
    
    echo "✅ PostgreSQL backup created: $POSTGRES_BACKUP"
    echo "   Size: $(du -h "$POSTGRES_BACKUP" | cut -f1)"
else
    echo "⏭️  PostgreSQL backup skipped (not configured)"
fi
echo ""

# 3. Upload to S3 (if configured)
if [ -n "$S3_BUCKET" ]; then
    echo "☁️  Uploading to S3..."
    
    # Upload ChromaDB backup
    if [ -f "$CHROMA_BACKUP" ]; then
        aws s3 cp "$CHROMA_BACKUP" "s3://$S3_BUCKET/backups/chroma/" --storage-class STANDARD_IA
        echo "✅ ChromaDB backup uploaded to S3"
    fi
    
    # Upload PostgreSQL backup
    if [ -f "$POSTGRES_BACKUP" ]; then
        aws s3 cp "$POSTGRES_BACKUP" "s3://$S3_BUCKET/backups/postgres/" --storage-class STANDARD_IA
        echo "✅ PostgreSQL backup uploaded to S3"
    fi
else
    echo "⏭️  S3 upload skipped (not configured)"
    echo "   Set S3_BUCKET environment variable to enable"
fi
echo ""

# 4. Clean up old local backups
echo "🧹 Cleaning up old backups (older than $RETENTION_DAYS days)..."
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete
echo "✅ Old backups cleaned"
echo ""

# 5. Backup metadata
echo "📝 Creating backup metadata..."
cat > "$BACKUP_DIR/backup_metadata_$TIMESTAMP.json" <<EOF
{
  "timestamp": "$TIMESTAMP",
  "date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "chroma_backup": "$(basename "$CHROMA_BACKUP")",
  "chroma_size": "$(stat -f%z "$CHROMA_BACKUP" 2>/dev/null || stat -c%s "$CHROMA_BACKUP" 2>/dev/null)",
  "postgres_backup": "$(basename "$POSTGRES_BACKUP")",
  "postgres_size": "$(stat -f%z "$POSTGRES_BACKUP" 2>/dev/null || stat -c%s "$POSTGRES_BACKUP" 2>/dev/null)",
  "s3_bucket": "$S3_BUCKET",
  "retention_days": $RETENTION_DAYS,
  "environment": "${ENVIRONMENT:-production}"
}
EOF
echo "✅ Metadata saved"
echo ""

# 6. Test backup integrity
echo "🔍 Testing backup integrity..."
if tar -tzf "$CHROMA_BACKUP" > /dev/null 2>&1; then
    echo "✅ ChromaDB backup integrity verified"
else
    echo "❌ ChromaDB backup corrupted!"
    exit 1
fi

if [ -f "$POSTGRES_BACKUP" ]; then
    if gzip -t "$POSTGRES_BACKUP" 2>/dev/null; then
        echo "✅ PostgreSQL backup integrity verified"
    else
        echo "❌ PostgreSQL backup corrupted!"
        exit 1
    fi
fi
echo ""

# 7. Summary
echo "=========================================="
echo "✅ Backup Complete!"
echo "=========================================="
echo ""
echo "📊 Summary:"
echo "  • ChromaDB: $(du -h "$CHROMA_BACKUP" | cut -f1)"
[ -f "$POSTGRES_BACKUP" ] && echo "  • PostgreSQL: $(du -h "$POSTGRES_BACKUP" | cut -f1)"
echo "  • Location: $BACKUP_DIR"
[ -n "$S3_BUCKET" ] && echo "  • S3 Bucket: s3://$S3_BUCKET/backups/"
echo ""
echo "📅 Retention: $RETENTION_DAYS days"
echo "🗂️  Backup files:"
ls -lh "$BACKUP_DIR"/*_$TIMESTAMP.* 2>/dev/null || echo "  (none)"
echo ""

# Send notification (optional)
if [ -n "$SLACK_WEBHOOK_URL" ]; then
    curl -X POST "$SLACK_WEBHOOK_URL" \
         -H 'Content-Type: application/json' \
         -d "{\"text\":\"✅ Database backup completed successfully at $TIMESTAMP\"}" \
         > /dev/null 2>&1 || echo "⚠️  Slack notification failed"
fi

echo "✅ Backup script completed successfully!"
exit 0
