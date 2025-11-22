from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from backend.db import get_connection

class RoomService:
    """Service for managing chat rooms"""

    def get_user_rooms(self, user_id):
        """Get all rooms that a user is a member of"""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute("""
                SELECT r.*, rm.joined_at
                FROM rooms r
                JOIN room_members rm ON r.id = rm.room_id
                WHERE rm.user_id = %s
                ORDER BY r.name
            """, (user_id,))

            return cursor.fetchall()

        finally:
            cursor.close()
            conn.close()

    def get_room_by_id(self, room_id):
        """Get room by ID"""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute("SELECT * FROM rooms WHERE id = %s", (room_id,))
            return cursor.fetchone()

        finally:
            cursor.close()
            conn.close()

    def is_user_in_room(self, user_id, room_id):
        """Check if user is a member of a room"""
        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM room_members
                WHERE user_id = %s AND room_id = %s
            """, (user_id, room_id))

            result = cursor.fetchone()
            return result[0] > 0

        finally:
            cursor.close()
            conn.close()

    def create_room(self, name, created_by=None):
        """
        Create a new room
        created_by: user_id or None for system-generated rooms
        Returns: room_id
        """
        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO rooms (name, created_by)
                VALUES (%s, %s)
            """, (name, created_by))

            conn.commit()
            return cursor.lastrowid

        finally:
            cursor.close()
            conn.close()

    def add_user_to_room(self, user_id, room_id):
        """Add a user to a room"""
        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO room_members (room_id, user_id, joined_at)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE joined_at = joined_at
            """, (room_id, user_id, datetime.utcnow()))

            conn.commit()

        finally:
            cursor.close()
            conn.close()

    def remove_user_from_room(self, user_id, room_id):
        """Remove a user from a room"""
        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                DELETE FROM room_members
                WHERE user_id = %s AND room_id = %s
            """, (user_id, room_id))

            conn.commit()

        finally:
            cursor.close()
            conn.close()

    def get_room_members(self, room_id):
        """Get all members of a room"""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute("""
                SELECT u.*, rm.joined_at
                FROM users u
                JOIN room_members rm ON u.id = rm.user_id
                WHERE rm.room_id = %s
            """, (room_id,))

            return cursor.fetchall()

        finally:
            cursor.close()
            conn.close()
