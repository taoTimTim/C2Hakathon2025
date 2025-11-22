from datetime import datetime

class Message:
    """Message model"""

    def __init__(self, id, user_id, room_id, content, created_at=None, is_edited=False, edited_at=None):
        self.id = id
        self.user_id = user_id
        self.room_id = room_id
        self.content = content
        self.created_at = created_at or datetime.utcnow()
        self.is_edited = is_edited
        self.edited_at = edited_at

    def to_dict(self):
        """Convert message to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'room_id': self.room_id,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_edited': self.is_edited,
            'edited_at': self.edited_at.isoformat() if self.edited_at else None
        }

    @staticmethod
    def from_dict(data):
        """Create message from dictionary"""
        return Message(
            id=data['id'],
            user_id=data['user_id'],
            room_id=data['room_id'],
            content=data['content'],
            created_at=data.get('created_at'),
            is_edited=data.get('is_edited', False),
            edited_at=data.get('edited_at')
        )
