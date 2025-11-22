import requests
from config import Config
from services.room_service import RoomService

class CanvasAPI:
    """Service for interacting with Canvas API"""

    def __init__(self, api_token):
        self.api_token = api_token
        self.base_url = Config.CANVAS_API_URL
        self.headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }

    def _make_request(self, endpoint, method='GET', data=None):
        """Make a request to Canvas API"""
        url = f"{self.base_url}/{endpoint}"

        try:
            if method == 'GET':
                response = requests.get(url, headers=self.headers)
            elif method == 'POST':
                response = requests.post(url, headers=self.headers, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Canvas API request failed: {str(e)}")
            raise

    def get_user_info(self):
        """
        Get current user information from Canvas
        Returns: {id: int, name: string, email: string, ...}
        """
        try:
            user_data = self._make_request('users/self')
            return {
                'id': user_data['id'],
                'name': user_data.get('name', 'Unknown'),
                'email': user_data.get('email', '')
            }
        except Exception as e:
            print(f"Failed to get user info: {str(e)}")
            return None

    def get_user_courses(self):
        """Get all courses for the current user"""
        return self._make_request('courses')

    def get_course_groups(self, course_id):
        """Get all groups for a specific course"""
        return self._make_request(f'courses/{course_id}/groups')

    def get_user_groups(self):
        """Get all groups the user is a member of"""
        return self._make_request('users/self/groups')

    def get_group_members(self, group_id):
        """Get all members of a specific group"""
        return self._make_request(f'groups/{group_id}/users')

    def sync_user_groups(self, user_id):
        """
        Sync Canvas groups to chat rooms
        Creates rooms from user's Canvas groups and adds members
        Returns: {synced_groups: int, synced_members: int}
        """
        try:
            # Get user's Canvas groups
            groups = self.get_user_groups()

            room_service = RoomService()
            synced_groups = 0
            synced_members = 0

            for group in groups:
                group_id = group['id']
                group_name = group['name']

                # Create or get room (using Canvas group ID as room ID)
                room = room_service.get_room_by_id(group_id)

                if not room:
                    # Create new room (system-generated)
                    room_service.create_room(group_name, created_by=None)
                    synced_groups += 1

                # Get group members from Canvas
                members = self.get_group_members(group_id)

                # Add members to room
                for member in members:
                    member_id = member['id']
                    room_service.add_user_to_room(member_id, group_id)
                    synced_members += 1

            return {
                'synced_groups': synced_groups,
                'synced_members': synced_members
            }

        except Exception as e:
            print(f"Group sync failed: {str(e)}")
            raise
