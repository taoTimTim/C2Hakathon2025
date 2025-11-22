import secrets
import hashlib
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from backend.db import get_connection
from config import Config

class AuthService:
    """Service for handling authentication and session management"""

    def __init__(self):
        self.session_expiry = Config.SESSION_TOKEN_EXPIRY

    def generate_session_token(self, user_id):
        """
        Generate a session token for a user
        Returns: session_token (string)
        """
        # Generate random token
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        # Calculate expiry time
        expires_at = datetime.utcnow() + timedelta(seconds=self.session_expiry)

        # Store in database
        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO session_tokens (user_id, token_hash, expires_at, created_at)
                VALUES (%s, %s, %s, %s)
            """, (user_id, token_hash, expires_at, datetime.utcnow()))

            conn.commit()
            return token

        finally:
            cursor.close()
            conn.close()

    def validate_session_token(self, token):
        """
        Validate a session token
        Returns: user_id if valid, None if invalid/expired
        """
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute("""
                SELECT user_id, expires_at
                FROM session_tokens
                WHERE token_hash = %s
            """, (token_hash,))

            result = cursor.fetchone()

            if not result:
                return None

            # Check if token is expired
            if result['expires_at'] < datetime.utcnow():
                # Delete expired token
                cursor.execute("DELETE FROM session_tokens WHERE token_hash = %s", (token_hash,))
                conn.commit()
                return None

            return result['user_id']

        finally:
            cursor.close()
            conn.close()

    def invalidate_session_token(self, token):
        """
        Invalidate a session token (logout)
        """
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM session_tokens WHERE token_hash = %s", (token_hash,))
            conn.commit()

        finally:
            cursor.close()
            conn.close()

    def cleanup_expired_tokens(self):
        """
        Clean up expired session tokens
        Should be called periodically
        """
        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM session_tokens WHERE expires_at < %s", (datetime.utcnow(),))
            conn.commit()
            return cursor.rowcount

        finally:
            cursor.close()
            conn.close()
