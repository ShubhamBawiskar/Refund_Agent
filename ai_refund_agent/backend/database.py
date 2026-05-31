import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'database.db')

def get_db_connection():
    """Returns a connection to the SQLite database with dict-like row access."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn
