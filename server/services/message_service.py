from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from backend.db import get_connection

class MessageService:
    """Service for managing messages"""

    def create_message(self, user_id, room_id, content):
        """
        Create a new message
        Returns: message dict
        """
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            created_at = datetime.utcnow()

            cursor.execute("""
                INSERT INTO messages (user_id, room_id, content, created_at, is_edited)
                VALUES (%s, %s, %s, %s, %s)
            """, (user_id, room_id, content, created_at, False))

            message_id = cursor.lastrowid
            conn.commit()

            # Return the created message
            cursor.execute("""
                SELECT m.*, u.username
                FROM messages m
                JOIN users u ON m.user_id = u.id
                WHERE m.id = %s
            """, (message_id,))

            return cursor.fetchone()

        finally:
            cursor.close()
            conn.close()

    def get_room_messages(self, room_id, limit=50, offset=0):
        """
        Get messages for a room
        Returns: list of message dicts
        """
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute("""
                SELECT m.*, u.username
                FROM messages m
                JOIN users u ON m.user_id = u.id
                WHERE m.room_id = %s
                ORDER BY m.created_at DESC
                LIMIT %s OFFSET %s
            """, (room_id, limit, offset))

            messages = cursor.fetchall()

            # Reverse to get chronological order
            return list(reversed(messages))

        finally:
            cursor.close()
            conn.close()

    def get_message_by_id(self, message_id):
        """Get a single message by ID"""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute("""
                SELECT m.*, u.username
                FROM messages m
                JOIN users u ON m.user_id = u.id
                WHERE m.id = %s
            """, (message_id,))

            return cursor.fetchone()

        finally:
            cursor.close()
            conn.close()

    def edit_message(self, message_id, new_content):
        """
        Edit a message
        Returns: updated message dict
        """
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            edited_at = datetime.utcnow()

            cursor.execute("""
                UPDATE messages
                SET content = %s, is_edited = %s, edited_at = %s
                WHERE id = %s
            """, (new_content, True, edited_at, message_id))

            conn.commit()

            # Return the updated message
            cursor.execute("""
                SELECT m.*, u.username
                FROM messages m
                JOIN users u ON m.user_id = u.id
                WHERE m.id = %s
            """, (message_id,))

            return cursor.fetchone()

        finally:
            cursor.close()
            conn.close()

    def delete_message(self, message_id):
        """Delete a message"""
        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM messages WHERE id = %s", (message_id,))
            conn.commit()

        finally:
            cursor.close()
            conn.close()
