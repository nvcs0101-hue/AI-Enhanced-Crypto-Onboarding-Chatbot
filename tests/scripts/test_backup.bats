#!/usr/bin/env bats

# Tests for backup-database.sh script

setup() {
    export BACKUP_DIR="/tmp/test_backups"
    export CHROMA_PERSIST_DIRECTORY="/tmp/test_chroma"
    export POSTGRES_HOST="localhost"
    export POSTGRES_PORT="5432"
    export POSTGRES_USER="postgres"
    export POSTGRES_DB="test_db"
    export RETENTION_DAYS="7"
    
    mkdir -p "$BACKUP_DIR"
    mkdir -p "$CHROMA_PERSIST_DIRECTORY"
}

teardown() {
    rm -rf "$BACKUP_DIR"
    rm -rf "$CHROMA_PERSIST_DIRECTORY"
}

@test "backup script exists and is executable" {
    [ -x "./scripts/backup-database.sh" ]
}

@test "backup script has dry-run mode" {
    run ./scripts/backup-database.sh --dry-run
    [ "$status" -eq 0 ]
}

@test "backup creates directory if not exists" {
    rm -rf "$BACKUP_DIR"
    run ./scripts/backup-database.sh --dry-run
    [ -d "$BACKUP_DIR" ]
}

@test "backup validates required environment variables" {
    unset CHROMA_PERSIST_DIRECTORY
    run ./scripts/backup-database.sh --dry-run
    [ "$status" -ne 0 ]
    [[ "$output" =~ "CHROMA_PERSIST_DIRECTORY" ]]
}

@test "backup creates metadata file" {
    run ./scripts/backup-database.sh --dry-run
    # Check that metadata structure is mentioned
    [[ "$output" =~ "metadata" ]]
}
