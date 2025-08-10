#!/usr/bin/env python3
"""
🔄 DATABASE MIGRATION: Unique Execution IDs
==========================================

Migrate the executions table to support unique execution IDs for scheduled tasks.
This script:
1. Backs up existing execution data
2. Recreates executions table with new schema  
3. Migrates existing data with generated execution IDs
4. Verifies migration success
"""

import sqlite3
import time
import os
import shutil
from pathlib import Path

# Database configuration
DB_FILE = "octopus_server/octopus.db"
BACKUP_FILE = f"octopus_server/octopus.db.backup_{int(time.time())}"

def backup_database():
    """Create a backup of the current database"""
    if os.path.exists(DB_FILE):
        shutil.copy2(DB_FILE, BACKUP_FILE)
        print(f"✅ Database backed up to: {BACKUP_FILE}")
        return True
    else:
        print(f"❌ Database file not found: {DB_FILE}")
        return False

def migrate_executions_table():
    """Migrate executions table to new schema with unique execution IDs"""
    
    print("\n🔄 Starting executions table migration...")
    
    with sqlite3.connect(DB_FILE) as conn:
        # Step 1: Check if executions table exists and get current data
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='executions'")
        if not cursor.fetchone():
            print("ℹ️  No executions table found - creating new one")
            create_new_executions_table(conn)
            return True
        
        # Step 2: Get existing execution data
        print("📊 Reading existing execution data...")
        cursor = conn.execute("SELECT * FROM executions ORDER BY updated_at")
        existing_executions = cursor.fetchall()
        
        # Get column names to handle different schemas
        cursor = conn.execute("PRAGMA table_info(executions)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"📋 Current schema columns: {columns}")
        
        if not existing_executions:
            print("ℹ️  No existing execution data to migrate")
            drop_and_recreate_table(conn)
            return True
        
        print(f"📊 Found {len(existing_executions)} existing execution records")
        
        # Step 3: Drop and recreate table with new schema
        drop_and_recreate_table(conn)
        
        # Step 4: Migrate existing data with generated execution IDs
        print("🔄 Migrating existing data with unique execution IDs...")
        migrated_count = 0
        
        for row in existing_executions:
            try:
                # Handle different possible schemas
                if len(columns) >= 6 and 'task_id' in columns:
                    # Extract data based on current schema
                    if 'execution_id' in columns:
                        # New schema already exists
                        id_val, execution_id, task_id, client, status, result = row[:6]
                        updated_at = row[-1] if len(row) > 6 else time.time()
                        created_at = row[-2] if len(row) > 7 else updated_at
                    else:
                        # Old schema: id, task_id, client, status, result, updated_at
                        id_val, task_id, client, status, result, updated_at = row[:6]
                        created_at = updated_at
                        execution_id = f"{task_id}_{client}_{int(updated_at * 1000)}"
                    
                    # Insert with new schema
                    conn.execute('''
                        INSERT INTO executions (execution_id, task_id, client, status, result, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (execution_id, task_id, client, status, result, created_at, updated_at))
                    
                    migrated_count += 1
                    
            except Exception as e:
                print(f"⚠️  Error migrating row {row}: {e}")
                continue
        
        conn.commit()
        print(f"✅ Successfully migrated {migrated_count} execution records")
        
        # Step 5: Verify migration
        cursor = conn.execute("SELECT COUNT(*) FROM executions")
        new_count = cursor.fetchone()[0]
        print(f"✅ Verification: {new_count} records in new table")
        
        return True

def drop_and_recreate_table(conn):
    """Drop and recreate executions table with new schema"""
    print("🔄 Dropping old executions table...")
    conn.execute("DROP TABLE IF EXISTS executions")
    
    print("🆕 Creating new executions table with unique execution IDs...")
    create_new_executions_table(conn)

def create_new_executions_table(conn):
    """Create the new executions table schema"""
    conn.execute('''
        CREATE TABLE executions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            execution_id TEXT UNIQUE,
            task_id TEXT,
            client TEXT,
            status TEXT,
            result TEXT,
            created_at REAL,
            updated_at REAL
        )
    ''')
    
    # Create indexes
    conn.execute('CREATE INDEX IF NOT EXISTS idx_executions_execution_id ON executions(execution_id)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_executions_task_id ON executions(task_id)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_executions_client ON executions(client)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_executions_created_at ON executions(created_at)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_executions_updated_at ON executions(updated_at)')
    
    conn.commit()
    print("✅ New executions table created successfully")

def verify_migration():
    """Verify the migration was successful"""
    print("\n🔍 Verifying migration...")
    
    with sqlite3.connect(DB_FILE) as conn:
        # Check table schema
        cursor = conn.execute("PRAGMA table_info(executions)")
        columns = [col[1] for col in cursor.fetchall()]
        
        expected_columns = ['id', 'execution_id', 'task_id', 'client', 'status', 'result', 'created_at', 'updated_at']
        missing_columns = set(expected_columns) - set(columns)
        
        if missing_columns:
            print(f"❌ Missing columns: {missing_columns}")
            return False
        
        # Check for execution_id uniqueness
        cursor = conn.execute("SELECT execution_id, COUNT(*) FROM executions GROUP BY execution_id HAVING COUNT(*) > 1")
        duplicates = cursor.fetchall()
        
        if duplicates:
            print(f"⚠️  Found {len(duplicates)} duplicate execution_id values")
            for dup in duplicates[:5]:  # Show first 5
                print(f"   Duplicate: {dup[0]} ({dup[1]} times)")
        else:
            print("✅ All execution_id values are unique")
        
        # Check record count
        cursor = conn.execute("SELECT COUNT(*) FROM executions")
        total_count = cursor.fetchone()[0]
        print(f"✅ Total execution records: {total_count}")
        
        return True

def main():
    """Main migration function"""
    print("🐙 Octopus Database Migration: Unique Execution IDs")
    print("=" * 60)
    
    # Check if database exists
    if not os.path.exists(DB_FILE):
        print(f"❌ Database file not found: {DB_FILE}")
        print("ℹ️  Run the server first to create the initial database")
        return False
    
    # Create backup
    if not backup_database():
        return False
    
    try:
        # Perform migration
        if migrate_executions_table():
            verify_migration()
            print("\n🎉 Migration completed successfully!")
            print(f"💾 Backup saved as: {BACKUP_FILE}")
            print("\nNext steps:")
            print("1. Restart your Octopus server and clients")
            print("2. Monitor logs for execution ID generation")
            print("3. Verify scheduled tasks create multiple execution records")
            return True
        else:
            print("❌ Migration failed")
            return False
            
    except Exception as e:
        print(f"❌ Migration failed with error: {e}")
        print(f"💾 Database backup available at: {BACKUP_FILE}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
