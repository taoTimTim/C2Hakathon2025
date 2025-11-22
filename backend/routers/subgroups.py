from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..db import get_connection

router = APIRouter()

class SubgroupCreate(BaseModel):
    name: str
    class_id: str  # Canvas course ID (scope_id of the class room)
    created_by: str  # user_id of creator

class SubgroupJoin(BaseModel):
    user_id: str

# Create a subgroup for a class
@router.post("/classes/{class_id}/subgroups")
def create_subgroup(class_id: str, subgroup: SubgroupCreate):
    conn = get_connection()
    cur = conn.cursor()

    # Verify the class exists
    sql_check_class = """
        SELECT id FROM rooms
        WHERE room_type = 'class' AND scope_id = %s
    """
    cur.execute(sql_check_class, (class_id,))
    class_room = cur.fetchone()

    if not class_room:
        cur.close()
        conn.close()
        raise HTTPException(404, "Class not found")

    # Create the subgroup room
    sql = """
        INSERT INTO rooms (name, scope_id, room_type, is_system_generated, created_by)
        VALUES (%s, %s, 'subgroup', FALSE, %s)
    """
    # Use class_id as scope_id to link subgroup to class
    cur.execute(sql, (subgroup.name, class_id, subgroup.created_by))
    conn.commit()
    subgroup_room_id = cur.lastrowid

    # Add creator to room_members
    sql2 = "INSERT INTO room_members (room_id, user_id) VALUES (%s, %s)"
    cur.execute(sql2, (subgroup_room_id, subgroup.created_by))
    conn.commit()

    cur.close()
    conn.close()

    return {
        "status": "success",
        "subgroup_id": subgroup_room_id,
        "name": subgroup.name
    }

# Get all subgroups for a class
@router.get("/classes/{class_id}/subgroups")
def get_class_subgroups(class_id: str):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    # Get all subgroups (rooms) for this class
    sql = """
        SELECT r.id, r.name, r.created_by, r.created_at,
               COUNT(rm.user_id) as members_count
        FROM rooms r
        LEFT JOIN room_members rm ON r.id = rm.room_id
        WHERE r.room_type = 'subgroup' AND r.scope_id = %s
        GROUP BY r.id, r.name, r.created_by, r.created_at
        ORDER BY r.name ASC
    """

    cur.execute(sql, (class_id,))
    subgroups = cur.fetchall()

    cur.close()
    conn.close()

    return subgroups

# Get subgroup members
@router.get("/subgroups/{subgroup_id}/members")
def get_subgroup_members(subgroup_id: int):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    # Verify it's a subgroup
    sql_check = "SELECT room_type FROM rooms WHERE id = %s"
    cur.execute(sql_check, (subgroup_id,))
    room = cur.fetchone()

    if not room or room["room_type"] != "subgroup":
        cur.close()
        conn.close()
        raise HTTPException(404, "Subgroup not found")

    # Get members
    sql = """
        SELECT u.canvas_user_id, u.name, u.role, rm.joined_at
        FROM room_members rm
        JOIN users u ON rm.user_id = u.canvas_user_id
        WHERE rm.room_id = %s
        ORDER BY u.name ASC
    """

    cur.execute(sql, (subgroup_id,))
    members = cur.fetchall()

    cur.close()
    conn.close()

    return members

# Get subgroup messages (channel)
@router.get("/subgroups/{subgroup_id}/messages")
def get_subgroup_messages(subgroup_id: int):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    # Verify it's a subgroup
    sql_check = "SELECT room_type FROM rooms WHERE id = %s"
    cur.execute(sql_check, (subgroup_id,))
    room = cur.fetchone()

    if not room or room["room_type"] != "subgroup":
        cur.close()
        conn.close()
        raise HTTPException(404, "Subgroup not found")

    # Get messages
    sql = """
        SELECT * FROM messages
        WHERE room_id = %s
        ORDER BY created_at ASC
    """
    cur.execute(sql, (subgroup_id,))
    messages = cur.fetchall()

    cur.close()
    conn.close()

    return messages

# Get subgroup posts (announcements)
@router.get("/subgroups/{subgroup_id}/posts")
def get_subgroup_posts(subgroup_id: int):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    # Verify it's a subgroup
    sql_check = "SELECT room_type FROM rooms WHERE id = %s"
    cur.execute(sql_check, (subgroup_id,))
    room = cur.fetchone()

    if not room or room["room_type"] != "subgroup":
        cur.close()
        conn.close()
        raise HTTPException(404, "Subgroup not found")

    # Get posts - subgroups use scope='subgroup' and scope_id is the subgroup room id
    sql = """
        SELECT * FROM posts 
        WHERE scope='subgroup' AND scope_id=%s
        ORDER BY created_at DESC
    """
    cur.execute(sql, (str(subgroup_id),))
    posts = cur.fetchall()

    cur.close()
    conn.close()

    return posts

# Join a subgroup
@router.post("/subgroups/{subgroup_id}/join")
def join_subgroup(subgroup_id: int, body: SubgroupJoin):
    conn = get_connection()
    cur = conn.cursor()

    # Verify it's a subgroup
    sql_check = "SELECT room_type FROM rooms WHERE id = %s"
    cur.execute(sql_check, (subgroup_id,))
    room = cur.fetchone()

    if not room or room["room_type"] != "subgroup":
        cur.close()
        conn.close()
        raise HTTPException(404, "Subgroup not found")

    # Add user to room_members
    sql = """
        INSERT INTO room_members (room_id, user_id, joined_at)
        VALUES (%s, %s, NOW())
    """

    try:
        cur.execute(sql, (subgroup_id, body.user_id))
        conn.commit()
    except Exception as e:
        cur.close()
        conn.close()
        raise HTTPException(400, "User is already a member or error occurred")

    cur.close()
    conn.close()

    return {
        "status": "success",
        "subgroup_id": subgroup_id,
        "user_id": body.user_id
    }

# Leave a subgroup
@router.delete("/subgroups/{subgroup_id}/leave")
def leave_subgroup(subgroup_id: int, user_id: str):
    conn = get_connection()
    cur = conn.cursor()

    # Verify it's a subgroup
    sql_check = "SELECT room_type FROM rooms WHERE id = %s"
    cur.execute(sql_check, (subgroup_id,))
    room = cur.fetchone()

    if not room or room["room_type"] != "subgroup":
        cur.close()
        conn.close()
        raise HTTPException(404, "Subgroup not found")

    # Remove user from room_members
    sql = """
        DELETE FROM room_members
        WHERE room_id = %s AND user_id = %s
    """

    cur.execute(sql, (subgroup_id, user_id))
    conn.commit()

    removed = cur.rowcount

    cur.close()
    conn.close()

    if removed == 0:
        raise HTTPException(400, "User is not a member of this subgroup")

    return {
        "status": "success",
        "subgroup_id": subgroup_id,
        "user_id": user_id
    }

