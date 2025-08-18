#!/usr/bin/env python3
"""
Run database migration to add missing columns to users table
"""

import sys
import os

# Add the octopus_server directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'octopus_server'))

from octopus_server.dbhelper import init_db

def main():
    print("Running database migration...")
    try:
        init_db()
        print("Migration completed successfully!")
    except Exception as e:
        print(f"Migration failed: {e}")
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
