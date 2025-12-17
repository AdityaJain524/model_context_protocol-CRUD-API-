#!/usr/bin/env python3
"""
MCP Server with CRUD Database Operations
Exposes Create, Read, Update, Delete operations as MCP tools
Uses SQLite for data persistence with parameterized queries
"""

import json
import sqlite3
import logging
from pathlib import Path
from typing import Any
from mcp.server import FastMCP

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DB_PATH = Path(__file__).parent / "users.db"
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


class DatabaseManager:
    """Manages SQLite database connections and CRUD operations"""

    def __init__(self, db_path: str = str(DB_PATH)):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize database with schema"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute(SCHEMA_SQL)
            conn.commit()
            conn.close()
            logger.info(f"Database initialized at {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Database initialization failed: {e}")
            raise

    def get_connection(self):
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def create_user(self, name: str, email: str) -> dict[str, Any]:
        """
        Create a new user record
        Uses parameterized query to prevent SQL injection
        """
        # Input validation
        if not name or not isinstance(name, str) or len(name.strip()) == 0:
            raise ValueError("Name must be a non-empty string")
        if not email or not isinstance(email, str) or "@" not in email:
            raise ValueError("Email must be a valid email address")

        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (name, email) VALUES (?, ?)",
                (name.strip(), email.strip())
            )
            conn.commit()
            user_id = cursor.lastrowid

            # Fetch and return the created user
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user = dict(cursor.fetchone())
            conn.close()

            return {"success": True, "data": user, "message": "User created successfully"}
        except sqlite3.IntegrityError as e:
            logger.error(f"Integrity error: {e}")
            raise ValueError("Email already exists")
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            raise

    def read_user(self, user_id: int) -> dict[str, Any]:
        """
        Read a single user by ID
        Uses parameterized query
        """
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("User ID must be a positive integer")

        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            conn.close()

            if not user:
                raise ValueError(f"User with ID {user_id} not found")

            return {"success": True, "data": dict(user)}
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            raise

    def read_all_users(self, limit: int = 100, offset: int = 0) -> dict[str, Any]:
        """
        Read all users with pagination
        """
        if not isinstance(limit, int) or limit <= 0 or limit > 1000:
            limit = 100
        if not isinstance(offset, int) or offset < 0:
            offset = 0

        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM users ORDER BY id DESC LIMIT ? OFFSET ?",
                (limit, offset)
            )
            users = [dict(row) for row in cursor.fetchall()]

            # Get total count
            cursor.execute("SELECT COUNT(*) as count FROM users")
            total = cursor.fetchone()["count"]

            conn.close()
            return {
                "success": True,
                "data": users,
                "pagination": {"total": total, "limit": limit, "offset": offset}
            }
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            raise

    def update_user(self, user_id: int, name: str = None, email: str = None) -> dict[str, Any]:
        """
        Update user record (name and/or email)
        """
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("User ID must be a positive integer")

        if not name and not email:
            raise ValueError("At least one field (name or email) must be provided")

        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Verify user exists
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            if not cursor.fetchone():
                raise ValueError(f"User with ID {user_id} not found")

            # Build update query
            updates = []
            params = []
            if name:
                if not isinstance(name, str) or len(name.strip()) == 0:
                    raise ValueError("Name must be a non-empty string")
                updates.append("name = ?")
                params.append(name.strip())
            if email:
                if not isinstance(email, str) or "@" not in email:
                    raise ValueError("Email must be a valid email address")
                updates.append("email = ?")
                params.append(email.strip())

            params.append(user_id)
            query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            conn.commit()

            # Fetch and return updated user
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user = dict(cursor.fetchone())
            conn.close()

            return {"success": True, "data": user, "message": "User updated successfully"}
        except sqlite3.IntegrityError as e:
            logger.error(f"Integrity error: {e}")
            raise ValueError("Email already exists")
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            raise

    def delete_user(self, user_id: int) -> dict[str, Any]:
        """
        Delete a user record
        """
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("User ID must be a positive integer")

        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Verify user exists
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            if not user:
                raise ValueError(f"User with ID {user_id} not found")

            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            conn.close()

            return {
                "success": True,
                "data": dict(user),
                "message": f"User {user_id} deleted successfully"
            }
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            raise


# Initialize database manager
db = DatabaseManager()

# Initialize FastMCP Server
server = FastMCP("crud-mcp-server", "1.0.0")


@server.tool()
def create_user(name: str, email: str) -> str:
    """
    Create a new user record with name and email
    
    Args:
        name: User's full name
        email: User's email address
    """
    try:
        result = db.create_user(name, email)
        return json.dumps(result, indent=2)
    except (ValueError, sqlite3.Error) as e:
        error_response = {"success": False, "error": str(e)}
        return json.dumps(error_response, indent=2)


@server.tool()
def read_user(user_id: int) -> str:
    """
    Read a specific user by ID
    
    Args:
        user_id: The user's ID
    """
    try:
        result = db.read_user(user_id)
        return json.dumps(result, indent=2)
    except (ValueError, sqlite3.Error) as e:
        error_response = {"success": False, "error": str(e)}
        return json.dumps(error_response, indent=2)


@server.tool()
def read_all_users(limit: int = 100, offset: int = 0) -> str:
    """
    Read all users with pagination support
    
    Args:
        limit: Number of records to return (default: 100, max: 1000)
        offset: Number of records to skip (default: 0)
    """
    try:
        result = db.read_all_users(limit, offset)
        return json.dumps(result, indent=2)
    except (ValueError, sqlite3.Error) as e:
        error_response = {"success": False, "error": str(e)}
        return json.dumps(error_response, indent=2)


@server.tool()
def update_user(user_id: int, name: str = None, email: str = None) -> str:
    """
    Update an existing user's name and/or email
    
    Args:
        user_id: The user's ID (required)
        name: New name (optional)
        email: New email (optional)
    """
    try:
        result = db.update_user(user_id, name, email)
        return json.dumps(result, indent=2)
    except (ValueError, sqlite3.Error) as e:
        error_response = {"success": False, "error": str(e)}
        return json.dumps(error_response, indent=2)


@server.tool()
def delete_user(user_id: int) -> str:
    """
    Delete a user record by ID
    
    Args:
        user_id: The user's ID
    """
    try:
        result = db.delete_user(user_id)
        return json.dumps(result, indent=2)
    except (ValueError, sqlite3.Error) as e:
        error_response = {"success": False, "error": str(e)}
        return json.dumps(error_response, indent=2)


if __name__ == "__main__":
    logger.info("Starting CRUD MCP Server...")
    server.run()
