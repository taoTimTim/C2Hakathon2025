import mysql.connector
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CA_PATH = os.path.join(BASE_DIR, "database", "ca.pem")
SCHEMA_PATH = os.path.join(BASE_DIR, "database", "schema.sql")

def get_connection():
    return mysql.connector.connect(
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        ssl_ca=CA_PATH,
        ssl_verify_cert=True
    )

def init_schema():
    conn = get_connection()
    cur = conn.cursor()
    print("Intializing database schema...")

    with open(SCHEMA_PATH, "r") as f:
        sql = f.read()

    statements = sql.split(";")

    for statement in statements:
        stmt = statement.strip()
        if stmt:
            cur.execute(stmt + ";")

    conn.commit()
    cur.close()
    conn.close()

    print("Schema intialization complete.")

# Canvas API Database Functions

def store_user_info(user_data):
    """
    Store user info from Canvas API GET /api/v1/users/self
    Maps: id → users.canvas_user_id, name → users.name
    """
    conn = get_connection()
    cur = conn.cursor()
    
    canvas_user_id = str(user_data["id"])
    name = user_data["name"]
    
    sql = """
        INSERT INTO users (canvas_user_id, name)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE name = %s
    """
    cur.execute(sql, (canvas_user_id, name, name))
    
    conn.commit()
    cur.close()
    conn.close()

def store_course(course_data):
    """
    Store course from Canvas API GET /api/v1/courses
    Maps: id → rooms.scope_id, name → rooms.name, NULL → rooms.created_by
    Returns the room_id (auto-generated)
    Note: Courses are stored with room_type='class' since class and course are equivalent
    """
    conn = get_connection()
    cur = conn.cursor()
    
    course_id = str(course_data["id"])
    name = course_data["name"]
    
    # Check if room already exists for this course
    sql_check = "SELECT id FROM rooms WHERE scope_id = %s AND room_type = 'class'"
    cur.execute(sql_check, (course_id,))
    existing = cur.fetchone()
    
    if existing:
        room_id = existing[0]
    else:
        sql = """
            INSERT INTO rooms (name, scope_id, room_type, is_system_generated, created_by)
            VALUES (%s, %s, 'class', TRUE, NULL)
        """
        cur.execute(sql, (name, course_id))
        conn.commit()
        room_id = cur.lastrowid
    
    cur.close()
    conn.close()
    return room_id

def store_course_users(course_id, users_data):
    """
    Store course users from Canvas API GET /api/v1/courses/:course_id/users
    Maps: id → room_members.user_id, course_id → room_members.room_id, NOW() → room_members.joined_at
    Note: Courses are stored with room_type='class' since class and course are equivalent
    """
    conn = get_connection()
    cur = conn.cursor()
    
    # Find the room_id for this course
    sql_find_room = "SELECT id FROM rooms WHERE scope_id = %s AND room_type = 'class'"
    cur.execute(sql_find_room, (str(course_id),))
    room_result = cur.fetchone()
    
    if not room_result:
        cur.close()
        conn.close()
        return
    
    room_id = room_result[0]
    
    # Ensure users exist before adding them to room_members
    sql_user = """
        INSERT INTO users (canvas_user_id, name)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE name = %s
    """
    
    # Insert/update room members
    sql = """
        INSERT INTO room_members (room_id, user_id, joined_at)
        VALUES (%s, %s, NOW())
        ON DUPLICATE KEY UPDATE joined_at = NOW()
    """
    
    for user in users_data:
        user_id = str(user["id"])
        name = user.get("name", "Unknown User")
        
        # Ensure user exists in users table
        cur.execute(sql_user, (user_id, name, name))
        
        # Add user to room
        cur.execute(sql, (room_id, user_id))
    
    conn.commit()
    cur.close()
    conn.close()

def store_group(group_data):
    """
    Store group from Canvas API GET /api/v1/users/self/groups
    Maps: id → rooms.scope_id, name → rooms.name, NULL → rooms.created_by
    Returns the room_id (auto-generated)
    """
    conn = get_connection()
    cur = conn.cursor()
    
    group_id = str(group_data["id"])
    name = group_data["name"]
    
    # Check if room already exists for this group
    sql_check = "SELECT id FROM rooms WHERE scope_id = %s AND room_type = 'group'"
    cur.execute(sql_check, (group_id,))
    existing = cur.fetchone()
    
    if existing:
        room_id = existing[0]
    else:
        sql = """
            INSERT INTO rooms (name, scope_id, room_type, is_system_generated, created_by)
            VALUES (%s, %s, 'group', TRUE, NULL)
        """
        cur.execute(sql, (name, group_id))
        conn.commit()
        room_id = cur.lastrowid
    
    cur.close()
    conn.close()
    return room_id

def store_group_members(group_id, users_data):
    """
    Store group members from Canvas API GET /api/v1/groups/:group_id/users
    Maps: id → room_members.user_id, group_id → room_members.room_id, NOW() → room_members.joined_at
    """
    conn = get_connection()
    cur = conn.cursor()
    
    # Find the room_id for this group
    sql_find_room = "SELECT id FROM rooms WHERE scope_id = %s AND room_type = 'group'"
    cur.execute(sql_find_room, (str(group_id),))
    room_result = cur.fetchone()
    
    if not room_result:
        cur.close()
        conn.close()
        return
    
    room_id = room_result[0]
    
    # Ensure users exist before adding them to room_members
    sql_user = """
        INSERT INTO users (canvas_user_id, name)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE name = %s
    """
    
    # Insert/update room members
    sql = """
        INSERT INTO room_members (room_id, user_id, joined_at)
        VALUES (%s, %s, NOW())
        ON DUPLICATE KEY UPDATE joined_at = NOW()
    """
    
    for user in users_data:
        user_id = str(user["id"])
        name = user.get("name", "Unknown User")
        
        # Ensure user exists in users table
        cur.execute(sql_user, (user_id, name, name))
        
        # Add user to room
        cur.execute(sql, (room_id, user_id))
    
    conn.commit()
    cur.close()
    conn.close()

