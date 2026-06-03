"""
db/connection.py - SQLite connection management

Provides a shared connection function for all database operations.
"""
import sqlite3

DB_PATH = 'database.db'


def get_conn() -> sqlite3.Connection:
    """Get a new SQLite connection. Caller must close."""
    return sqlite3.connect(DB_PATH)