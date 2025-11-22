from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..db import get_connection

router = APIRouter()

class ClassCreate(BaseModel):
    id: str
    name: str


class ClassJoin(BaseModel):
    user_id: str


# Get a user's classes (courses from Canvas)
@router.get("/classes")
def get_user_classes(user_id: str):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    sql = """
        SELECT r.id, r.name, r.scope_id, r.created_at
        FROM room_members rm
        JOIN rooms r ON rm.room_id = r.id
        WHERE rm.user_id = %s AND r.room_type = 'class'
        ORDER BY r.name ASC
    """

    cur.execute(sql, (user_id,))
    classes = cur.fetchall()

    cur.close()
    conn.close()

    return classes


# get a classes members (course members from Canvas)
@router.get("/classes/{class_id}/members")
def get_class_members(class_id: str):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    # First find the room for this course (using scope_id which stores Canvas course ID)
    sql_find_room = """
        SELECT id FROM rooms
        WHERE room_type = 'class' AND scope_id = %s
    """
    cur.execute(sql_find_room, (class_id,))
    room_result = cur.fetchone()

    if not room_result:
        cur.close()
        conn.close()
        raise HTTPException(404, "Course not found")

    room_id = room_result["id"]

    # Get members from room_members
    sql = """
        SELECT u.canvas_user_id, u.name, u.role, rm.joined_at
        FROM room_members rm
        JOIN users u ON rm.user_id = u.canvas_user_id
        WHERE rm.room_id = %s
        ORDER BY u.name ASC
    """

    cur.execute(sql, (room_id,))
    members = cur.fetchall()

    cur.close()
    conn.close()

    return members

# get a classes messages (course messages from Canvas)
@router.get("/classes/{class_id}/messages")
def get_class_messages(class_id: str):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    # get room for this course (using scope_id which stores Canvas course ID)
    cur.execute("""
        SELECT id FROM rooms
        WHERE room_type='class' AND scope_id=%s
    """, (class_id,))
    row = cur.fetchone()

    if not row:
        cur.close()
        conn.close()
        raise HTTPException(404, "Course room not found")

    room_id = row["id"]

    # fetch messages from that room
    cur.execute("""
        SELECT * FROM messages
        WHERE room_id=%s
        ORDER BY created_at ASC
    """, (room_id,))
    
    messages = cur.fetchall()

    cur.close()
    conn.close()

    return messages

# get a classes posts (course posts from Canvas)
@router.get("/classes/{class_id}/posts")
def get_class_posts(class_id: str):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    sql = """
        SELECT * FROM posts 
        WHERE scope='class' AND scope_id=%s
        ORDER BY created_at DESC
    """
    cur.execute(sql, (class_id,))
    posts = cur.fetchall()

    cur.close()
    conn.close()

    return posts
