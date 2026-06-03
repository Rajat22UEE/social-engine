"""
db/__init__.py - Database package exports

Exposes all database helper functions for use by route handlers.
"""
from db.connection import get_conn, DB_PATH
from db.schema import init_db
from db.users import get_or_create_user
from db.templates import get_template
from db.posts import create_post, get_post, increment_download_count
from db.categories import get_categories