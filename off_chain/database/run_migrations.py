# pylint: disable= no-name-in-module,
# pylint: disable= import-error
# pylint: disable= line-too-long
# pylint: disable= trailing-whitespace
import sqlite3
import os
from pathlib import Path

def run_migrations(db_path):
    """Run all SQL migration scripts in the migrations directory."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get the migrations directory path
    migrations_dir = Path(__file__).parent / 'migrations'
    
    try:
        # Create migrations table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL UNIQUE,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Get list of applied migrations
        cursor.execute("SELECT filename FROM migrations")
        applied_migrations = {row[0] for row in cursor.fetchall()}
        
        # Get all .sql files from migrations directory
        migration_files = sorted([f for f in os.listdir(migrations_dir) if f.endswith('.sql')])
        
        for filename in migration_files:
            if filename not in applied_migrations:
                print(f"Applying migration: {filename}")
                
                # Read and execute migration file
                with open(migrations_dir / filename, 'r') as f:
                    sql = f.read()
                    cursor.executescript(sql)
                
                # Record the migration
                cursor.execute("INSERT INTO migrations (filename) VALUES (?)", (filename,))
                conn.commit()
                print(f"Successfully applied migration: {filename}")
    
    except Exception as e:
        print(f"Error applying migrations: {e}")
        conn.rollback()
        raise
    
    finally:
        conn.close()

if __name__ == "__main__":
    db_path = Path(__file__).parent / "sfs_chain_database.db"
    run_migrations(db_path)
