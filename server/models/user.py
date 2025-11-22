from datetime import datetime

class User:
    """User model"""

    def __init__(self, id, username, last_seen=None):
        self.id = id
        self.username = username
        self.last_seen = last_seen or datetime.utcnow()

    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None
        }

    @staticmethod
    def from_dict(data):
        """Create user from dictionary"""
        return User(
            id=data['id'],
            username=data['username'],
            last_seen=data.get('last_seen')
        )
