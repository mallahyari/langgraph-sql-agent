import sqlite3
from pathlib import Path
from typing import List, Dict, Any

# Configure DB Path
# Assuming running from backend/ or root, careful with path
# Current file is backend/app/tools/sql.py
# Database is backend/app/data/chinook.db
DB_PATH = Path(__file__).parents[1] / "data" / "chinook.db"

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    try:
        if not DB_PATH.exists():
            raise FileNotFoundError(f"Database not found at {DB_PATH}")
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Return rows as dict-like objects
        return conn
    except Exception as e:
        raise ConnectionError(f"Failed to connect to database: {e}")

def execute_read_query(query: str, parameters: tuple = ()) -> List[Dict[str, Any]]:
    """Executes a read-only SQL query."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, parameters)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        raise Exception(f"Query execution failed: {e}")
    finally:
        conn.close()

def get_table_names() -> List[str]:
    """Retrieves all table names from the database."""
    query = "SELECT name FROM sqlite_master WHERE type='table';"
    results = execute_read_query(query)
    return [row['name'] for row in results]

def get_table_schema(table_name: str) -> str:
    """Retrieves the schema CREATE statement for a specific table."""
    query = "SELECT sql FROM sqlite_master WHERE type='table' AND name=?;"
    results = execute_read_query(query, (table_name,))
    if results:
        return results[0]['sql']
    return ""
