import requests
from config import Config
from services.room_service import RoomService
from services.user_service import UserService

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
        Returns: {id: int, name: string, email: string, ...} on success
        Raises: Exception with detailed error message on failure
        """
        try:
            user_data = self._make_request('users/self')
            return {
                'id': user_data['id'],
                'name': user_data.get('name', 'Unknown'),
                'email': user_data.get('email', '')
            }
        except requests.exceptions.HTTPError as e:
            # Handle specific HTTP errors
            if e.response.status_code == 401:
                raise Exception("Invalid Canvas API token. Please check that your token is correct and has not expired.")
            elif e.response.status_code == 403:
                raise Exception("Access forbidden. Your Canvas API token may not have the required permissions.")
            elif e.response.status_code == 404:
                raise Exception(f"Canvas API endpoint not found. Please check if Canvas API URL is configured correctly: {self.base_url}")
            else:
                raise Exception(f"Canvas API returned error {e.response.status_code}: {e.response.text or str(e)}")
        except requests.exceptions.ConnectionError as e:
            raise Exception(f"Could not connect to Canvas API at {self.base_url}. Please check your internet connection and Canvas API URL configuration.")
        except requests.exceptions.Timeout as e:
            raise Exception("Connection to Canvas API timed out. Please try again.")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Canvas API request failed: {str(e)}")
        except Exception as e:
            # Re-raise any other exceptions with context
            raise Exception(f"Failed to get user info from Canvas: {str(e)}")

    def get_user_courses(self):
        """Get all active courses for the current user"""
        return self._make_request('courses?enrollment_state=active&per_page=100')

    def get_course_users(self, course_id):
        """Get all users enrolled in a specific course"""
        try:
            return self._make_request(f'courses/{course_id}/users?per_page=100')
        except Exception as e:
            print(f"Warning: Could not fetch users for course {course_id}: {e}")
            return []

    def get_course_groups(self, course_id):
        """Get all groups for a specific course"""
        return self._make_request(f'courses/{course_id}/groups')

    def get_user_groups(self):
        """Get all groups the user is a member of"""
        return self._make_request('users/self/groups')

    def get_group_members(self, group_id):
        """Get all members of a specific group"""
        return self._make_request(f'groups/{group_id}/users')

    def sync_user_groups(self, user_id, force=False):
        """
        Sync Canvas courses and groups to chat rooms
        Creates rooms from user's Canvas courses (class-wide) and groups
        
        Args:
            user_id: Canvas user ID
            force: If True, sync even if user already has rooms. If False, skip if already synced.
        
        Returns: {synced_courses: int, synced_groups: int, synced_members: int, skipped: bool}
        """
        try:
            room_service = RoomService()
            user_service = UserService()
            
            # Check if user already has rooms synced (quick check to avoid unnecessary API calls)
            if not force:
                existing_rooms = room_service.get_user_rooms(user_id)
                if existing_rooms:
                    print(f"[SYNC] User {user_id} already has {len(existing_rooms)} rooms synced. Skipping sync.")
                    return {
                        'synced_courses': 0,
                        'synced_groups': 0,
                        'synced_members': 0,
                        'skipped': True,
                        'message': 'Sync skipped - user already has rooms'
                    }
            
            synced_courses = 0
            synced_groups = 0
            synced_members = 0

            # Sync Courses (class-wide chats)
            print(f"[SYNC] Fetching courses for user {user_id}...")
            courses = self.get_user_courses()
            print(f"[SYNC] Found {len(courses)} courses")

            for course in courses:
                try:
                    course_id = course.get('id')
                    course_name = course.get('name', f'Course {course_id}')

                    print(f"[SYNC] Processing course: {course_name} (ID: {course_id})")

                    # Create or get room (using Canvas course ID as room ID)
                    room = room_service.get_room_by_id(course_id)

                    if not room:
                        # Create new room with Canvas course ID
                        print(f"[SYNC] Creating room for course {course_id}")
                        room_service.create_room(course_name, created_by=None, room_id=course_id, room_type='class')
                        synced_courses += 1

                        # Only fetch and add users for new rooms
                        course_users = self.get_course_users(course_id)
                        print(f"[SYNC] Found {len(course_users)} users in course {course_id}")

                        # Batch create/update all users
                        user_service.create_or_update_users_batch(course_users)

                        # Batch add all users to room
                        user_ids = [str(user['id']) for user in course_users]
                        room_service.add_users_to_room_batch(user_ids, course_id)
                        synced_members += len(user_ids)
                    else:
                        print(f"[SYNC] Room already exists for course {course_id}, skipping user sync")

                except Exception as e:
                    print(f"[SYNC] Error processing course {course.get('id', 'unknown')}: {e}")

            # Sync Groups (group chats)
            print(f"[SYNC] Fetching groups for user {user_id}...")
            groups = self.get_user_groups()
            print(f"[SYNC] Found {len(groups)} groups")

            for group in groups:
                try:
                    group_id = group['id']
                    group_name = group['name']

                    print(f"[SYNC] Processing group: {group_name} (ID: {group_id})")

                    # Create or get room (using Canvas group ID as room ID)
                    room = room_service.get_room_by_id(group_id)

                    if not room:
                        # Create new room with Canvas group ID
                        print(f"[SYNC] Creating room for group {group_id}")
                        room_service.create_room(group_name, created_by=None, room_id=group_id, room_type='project')
                        synced_groups += 1

                        # Only fetch and add members for new rooms
                        try:
                            members = self.get_group_members(group_id)
                            print(f"[SYNC] Found {len(members)} members in group {group_id}")

                            # Batch create/update all members
                            user_service.create_or_update_users_batch(members)

                            # Batch add all members to room
                            member_ids = [str(member['id']) for member in members]
                            room_service.add_users_to_room_batch(member_ids, group_id)
                            synced_members += len(member_ids)
                        except Exception as e:
                            print(f"[SYNC] Warning: Could not fetch members for group {group_id}: {e}")
                            # Still create the room, just can't add members yet
                            # At minimum, add the current user if they exist in users table
                            try:
                                # Note: user_id here is the logged-in user, may need to ensure they exist
                                room_service.add_user_to_room(str(user_id), group_id)
                                synced_members += 1
                            except Exception as inner_e:
                                print(f"[SYNC] Warning: Could not add current user to group {group_id}: {inner_e}")
                    else:
                        print(f"[SYNC] Room already exists for group {group_id}, skipping member sync")

                except Exception as e:
                    print(f"[SYNC] Error processing group {group.get('id', 'unknown')}: {e}")

            return {
                'synced_courses': synced_courses,
                'synced_groups': synced_groups,
                'synced_members': synced_members,
                'skipped': False
            }

        except Exception as e:
            print(f"Sync failed: {str(e)}")
            raise
