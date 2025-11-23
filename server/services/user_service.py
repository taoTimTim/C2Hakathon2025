from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from backend.db import get_connection

class UserService:
    """Service for managing users"""

    def create_or_update_user(self, user_info):
        """
        Create or update user from Canvas user info
        user_info: {id: int, name: string, ...}
        Returns: user dict
        """
        user_id = str(user_info['id'])  # Canvas user ID as string
        username = user_info.get('name', 'Unknown')

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            # Check if user exists
            cursor.execute("SELECT * FROM users WHERE canvas_user_id = %s", (user_id,))
            existing_user = cursor.fetchone()

            if existing_user:
                # Update existing user
                cursor.execute("""
                    UPDATE users
                    SET name = %s
                    WHERE canvas_user_id = %s
                """, (username, user_id))
            else:
                # Create new user
                cursor.execute("""
                    INSERT INTO users (canvas_user_id, name, role)
                    VALUES (%s, %s, 'student')
                """, (user_id, username))

            conn.commit()

            # Return updated user
            cursor.execute("SELECT * FROM users WHERE canvas_user_id = %s", (user_id,))
            return cursor.fetchone()

        finally:
            cursor.close()
            conn.close()

    def get_user_by_id(self, user_id):
        """Get user by Canvas ID"""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute("SELECT * FROM users WHERE canvas_user_id = %s", (str(user_id),))
            return cursor.fetchone()

        finally:
            cursor.close()
            conn.close()

    def update_last_seen(self, user_id):
        """Update user's last_seen timestamp (not in schema, skipping)"""
        # The current schema doesn't have last_seen field
        # This is a no-op for now
        pass

    def get_users_by_ids(self, user_ids):
        """Get multiple users by their IDs"""
        if not user_ids:
            return []

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            placeholders = ','.join(['%s'] * len(user_ids))
            user_ids_str = [str(uid) for uid in user_ids]
            cursor.execute(f"SELECT * FROM users WHERE canvas_user_id IN ({placeholders})", user_ids_str)
            return cursor.fetchall()

        finally:
            cursor.close()
            conn.close()

    def create_or_update_users_batch(self, users_info):
        """
        Batch create or update users from Canvas user info (for Canvas sync optimization)
        users_info: list of {id: int, name: string, ...}
        """
        if not users_info:
            return

        conn = get_connection()
        cursor = conn.cursor()

        try:
            # Batch insert/update using ON DUPLICATE KEY UPDATE
            values = [(str(user['id']), user.get('name', 'Unknown'), 'student') for user in users_info]

            cursor.executemany("""
                INSERT INTO users (canvas_user_id, name, role)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE name = VALUES(name)
            """, values)

            conn.commit()

        finally:
            cursor.close()
            conn.close()
