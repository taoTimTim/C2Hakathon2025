"""
Simple database connection and query test
Run with: python backend/test_db.py
"""

from db import get_connection, store_user_info, store_course, store_course_users, store_group, store_group_members
import sys

def test_connection():
    """Test database connection"""
    print("=" * 50)
    print("Testing Database Connection...")
    print("=" * 50)
    
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        result = cur.fetchone()
        cur.close()
        conn.close()
        
        if result:
            print("Database connection successful!")
            return True
        else:
            print("Database connection failed!")
            return False
    except Exception as e:
        print(f"Database connection error: {e}")
        return False

def test_schema():
    """Test that tables exist"""
    print("\n" + "=" * 50)
    print("Testing Database Schema...")
    print("=" * 50)
    
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        tables = ['users', 'rooms', 'room_members', 'messages', 'posts', 'clubs', 'club_members']
        
        for table in tables:
            cur.execute(f"SHOW TABLES LIKE '{table}'")
            result = cur.fetchone()
            if result:
                print(f"Table '{table}' exists")
            else:
                print(f"Table '{table}' NOT found")
        
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Schema test error: {e}")
        return False

def test_store_user_info():
    """Test storing user info"""
    print("\n" + "=" * 50)
    print("Testing store_user_info()...")
    print("=" * 50)
    
    try:
        test_user = {
            "id": 99999,
            "name": "Test User",
            "email": "test@example.com"
        }
        
        store_user_info(test_user)
        print(f"Successfully stored user: {test_user['name']} (ID: {test_user['id']})")
        
        # Verify it was stored
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE canvas_user_id = %s", (str(test_user["id"]),))
        result = cur.fetchone()
        cur.close()
        conn.close()
        
        if result:
            print(f"Verified user in database: {result['name']}")
            return True
        else:
            print("User not found in database after storing")
            return False
    except Exception as e:
        print(f"store_user_info() error: {e}")
        return False

def test_store_course():
    """Test storing a course"""
    print("\n" + "=" * 50)
    print("Testing store_course()...")
    print("=" * 50)
    
    try:
        test_course = {
            "id": 88888,
            "name": "Test Course 101",
            "course_code": "TEST101"
        }
        
        room_id = store_course(test_course)
        print(f"Successfully stored course: {test_course['name']} (Room ID: {room_id})")
        
        # Verify it was stored
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM rooms WHERE scope_id = %s AND room_type = 'class'", (str(test_course["id"]),))
        result = cur.fetchone()
        cur.close()
        conn.close()
        
        if result:
            print(f"Verified course room in database: {result['name']}")
            return True, room_id
        else:
            print("Course room not found in database after storing")
            return False, None
    except Exception as e:
        print(f"store_course() error: {e}")
        return False, None

def test_store_course_users():
    """Test storing course users"""
    print("\n" + "=" * 50)
    print("Testing store_course_users()...")
    print("=" * 50)
    
    try:
        course_id = 88888
        test_users = [
            {"id": 99999, "name": "Test User"},
            {"id": 99998, "name": "Test User 2"}
        ]
        
        store_course_users(course_id, test_users)
        print(f"Successfully stored {len(test_users)} users for course {course_id}")
        
        # Verify users were added to room
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT COUNT(*) as count
            FROM room_members rm
            JOIN rooms r ON rm.room_id = r.id
            WHERE r.scope_id = %s AND r.room_type = 'class'
        """, (str(course_id),))
        result = cur.fetchone()
        cur.close()
        conn.close()
        
        if result and result[0] > 0:
            print(f"Verified {result[0]} users in course room")
            return True
        else:
            print("No users found in course room")
            return False
    except Exception as e:
        print(f"store_course_users() error: {e}")
        return False

def test_store_group():
    """Test storing a group"""
    print("\n" + "=" * 50)
    print("Testing store_group()...")
    print("=" * 50)
    
    try:
        test_group = {
            "id": 77777,
            "name": "Test Group",
            "description": "A test group"
        }
        
        room_id = store_group(test_group)
        print(f"Successfully stored group: {test_group['name']} (Room ID: {room_id})")
        
        # Verify it was stored
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM rooms WHERE scope_id = %s AND room_type = 'group'", (str(test_group["id"]),))
        result = cur.fetchone()
        cur.close()
        conn.close()
        
        if result:
            print(f"Verified group room in database: {result['name']}")
            return True
        else:
            print("Group room not found in database after storing")
            return False
    except Exception as e:
        print(f"store_group() error: {e}")
        return False

def test_store_group_members():
    """Test storing group members"""
    print("\n" + "=" * 50)
    print("Testing store_group_members()...")
    print("=" * 50)
    
    try:
        group_id = 77777
        test_users = [
            {"id": 99999, "name": "Test User"},
            {"id": 99998, "name": "Test User 2"}
        ]
        
        store_group_members(group_id, test_users)
        print(f"Successfully stored {len(test_users)} users for group {group_id}")
        
        # Verify users were added to room
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT COUNT(*) as count
            FROM room_members rm
            JOIN rooms r ON rm.room_id = r.id
            WHERE r.scope_id = %s AND r.room_type = 'group'
        """, (str(group_id),))
        result = cur.fetchone()
        cur.close()
        conn.close()
        
        if result and result[0] > 0:
            print(f"Verified {result[0]} users in group room")
            return True
        else:
            print("No users found in group room")
            return False
    except Exception as e:
        print(f"store_group_members() error: {e}")
        return False

def test_queries():
    """Test some basic queries"""
    print("\n" + "=" * 50)
    print("Testing Database Queries...")
    print("=" * 50)
    
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        
        # Test: Get all users
        print("\n1. Getting all users...")
        cur.execute("SELECT canvas_user_id, name FROM users LIMIT 5")
        users = cur.fetchall()
        print(f"   Found {len(users)} users")
        for user in users[:3]:
            print(f"      - {user['name']} (ID: {user['canvas_user_id']})")
        
        # Test: Get all rooms
        print("\n2. Getting all rooms...")
        cur.execute("SELECT id, name, room_type, scope_id FROM rooms LIMIT 5")
        rooms = cur.fetchall()
        print(f"   Found {len(rooms)} rooms")
        for room in rooms[:3]:
            print(f"      - {room['name']} (Type: {room['room_type']}, ID: {room['id']})")
        
        # Test: Get room members
        print("\n3. Getting room members...")
        cur.execute("""
            SELECT COUNT(*) as count
            FROM room_members
        """)
        result = cur.fetchone()
        print(f"   Found {result['count']} room memberships")
        
        # Test: Get messages
        print("\n4. Getting messages...")
        cur.execute("SELECT COUNT(*) as count FROM messages")
        result = cur.fetchone()
        print(f"   Found {result['count']} messages")
        
        # Test: Get posts
        print("\n5. Getting posts...")
        cur.execute("SELECT COUNT(*) as count FROM posts")
        result = cur.fetchone()
        print(f"   Found {result['count']} posts")
        
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Query test error: {e}")
        return False

def cleanup_test_data():
    """Clean up test data"""
    print("\n" + "=" * 50)
    print("Cleaning up test data...")
    print("=" * 50)
    
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Delete test data
        test_ids = ['99999', '99998', '88888', '77777']
        
        cur.execute("DELETE FROM room_members WHERE user_id IN (%s, %s)", ('99999', '99998'))
        cur.execute("DELETE FROM rooms WHERE scope_id IN (%s, %s)", ('88888', '77777'))
        cur.execute("DELETE FROM users WHERE canvas_user_id IN (%s, %s)", ('99999', '99998'))
        
        conn.commit()
        cur.close()
        conn.close()
        
        print("Test data cleaned up")
        return True
    except Exception as e:
        print(f"⚠️  Cleanup error (non-critical): {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 50)
    print("DATABASE CONNECTION AND QUERY TEST")
    print("=" * 50)
    
    results = []
    
    # Run tests
    results.append(("Connection", test_connection()))
    results.append(("Schema", test_schema()))
    results.append(("Store User Info", test_store_user_info()))
    results.append(("Store Course", test_store_course()[0]))
    results.append(("Store Course Users", test_store_course_users()))
    results.append(("Store Group", test_store_group()))
    results.append(("Store Group Members", test_store_group_members()))
    results.append(("Queries", test_queries()))
    
    # Cleanup
    cleanup_test_data()
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())

