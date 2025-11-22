class Room:
    """Room model"""

    def __init__(self, id, name, created_by=None):
        self.id = id
        self.name = name
        self.created_by = created_by  # None for system-generated rooms

    def to_dict(self):
        """Convert room to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'created_by': self.created_by,
            'is_system_generated': self.created_by is None
        }

    @staticmethod
    def from_dict(data):
        """Create room from dictionary"""
        return Room(
            id=data['id'],
            name=data['name'],
            created_by=data.get('created_by')
        )
