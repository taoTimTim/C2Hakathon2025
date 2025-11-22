from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from database.db import get_connection

class UserService:
    """Service for managing users"""

    def create_or_update_user(self, user_info):
        """
        Create or update user from Canvas user info
        user_info: {id: int, name: string, ...}
        Returns: user dict
        """
        user_id = user_info['id']
        username = user_info.get('name', 'Unknown')

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            # Check if user exists
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            existing_user = cursor.fetchone()

            if existing_user:
                # Update existing user
                cursor.execute("""
                    UPDATE users
                    SET username = %s, last_seen = %s
                    WHERE id = %s
                """, (username, datetime.utcnow(), user_id))
            else:
                # Create new user
                cursor.execute("""
                    INSERT INTO users (id, username, last_seen)
                    VALUES (%s, %s, %s)
                """, (user_id, username, datetime.utcnow()))

            conn.commit()

            # Return updated user
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            return cursor.fetchone()

        finally:
            cursor.close()
            conn.close()

    def get_user_by_id(self, user_id):
        """Get user by ID"""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            return cursor.fetchone()

        finally:
            cursor.close()
            conn.close()

    def update_last_seen(self, user_id):
        """Update user's last_seen timestamp"""
        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE users
                SET last_seen = %s
                WHERE id = %s
            """, (datetime.utcnow(), user_id))
            conn.commit()

        finally:
            cursor.close()
            conn.close()

    def get_users_by_ids(self, user_ids):
        """Get multiple users by their IDs"""
        if not user_ids:
            return []

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            placeholders = ','.join(['%s'] * len(user_ids))
            cursor.execute(f"SELECT * FROM users WHERE id IN ({placeholders})", user_ids)
            return cursor.fetchall()

        finally:
            cursor.close()
            conn.close()
