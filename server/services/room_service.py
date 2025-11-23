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

    def create_room(self, name, created_by=None, room_id=None, room_type=None, description=None, max_members=None):
        """
        Create a new room
        created_by: user_id or None for system-generated rooms
        room_id: specific ID to use (for Canvas sync), or None for auto-increment
        room_type: 'class', 'club', 'project', 'personal', or None
        description: optional description (for clubs, projects)
        max_members: max number of members (10 for personal, None for unlimited)
        Returns: room_id
        """
        conn = get_connection()
        cursor = conn.cursor()

        try:
            if room_id:
                # Insert with specific ID (for Canvas courses/groups)
                cursor.execute("""
                    INSERT INTO rooms (id, name, description, room_type, max_members, is_system_generated, created_by)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (room_id, name, description, room_type, max_members, True, created_by))
                conn.commit()
                return room_id
            else:
                # Auto-increment ID
                cursor.execute("""
                    INSERT INTO rooms (name, description, room_type, max_members, is_system_generated, created_by)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (name, description, room_type, max_members, False, created_by))
                conn.commit()
                return cursor.lastrowid

        finally:
            cursor.close()
            conn.close()

    def add_user_to_room(self, user_id, room_id, role='member'):
        """
        Add a user to a room
        role: 'leader', 'admin', or 'member'
        Raises ValueError if room is at max capacity
        """
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            # Check if room has max_members limit
            cursor.execute("SELECT max_members FROM rooms WHERE id = %s", (room_id,))
            room = cursor.fetchone()

            if room and room['max_members'] is not None:
                # Count current members
                cursor.execute("SELECT COUNT(*) as count FROM room_members WHERE room_id = %s", (room_id,))
                result = cursor.fetchone()
                current_count = result['count']

                if current_count >= room['max_members']:
                    raise ValueError(f"Room is at maximum capacity ({room['max_members']} members)")

            cursor.execute("""
                INSERT INTO room_members (room_id, user_id, role, joined_at)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE role = VALUES(role), joined_at = joined_at
            """, (room_id, user_id, role, datetime.utcnow()))

            conn.commit()

        finally:
            cursor.close()
            conn.close()

    def add_users_to_room_batch(self, user_ids, room_id, role='member'):
        """
        Batch add multiple users to a room (for Canvas sync optimization)
        Skips max_members check as this is for system-generated rooms
        user_ids: list of user IDs
        """
        if not user_ids:
            return

        conn = get_connection()
        cursor = conn.cursor()

        try:
            # Batch insert with ON DUPLICATE KEY to handle existing members
            values = [(room_id, user_id, role, datetime.utcnow()) for user_id in user_ids]

            cursor.executemany("""
                INSERT INTO room_members (room_id, user_id, role, joined_at)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE role = VALUES(role)
            """, values)

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
