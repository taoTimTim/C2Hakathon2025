from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..db import get_connection

router = APIRouter()

# Get a user's groups (from Canvas)
@router.get("/groups")
def get_user_groups(user_id: str):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    sql = """
        SELECT r.id, r.name, r.scope_id, r.created_at
        FROM room_members rm
        JOIN rooms r ON rm.room_id = r.id
        WHERE rm.user_id = %s AND r.room_type = 'group'
        ORDER BY r.name ASC
    """

    cur.execute(sql, (user_id,))
    groups = cur.fetchall()

    cur.close()
    conn.close()

    return groups

# get a group's members (from Canvas)
@router.get("/groups/{group_id}/members")
def get_group_members(group_id: str):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    # First find the room for this group (using scope_id which stores Canvas group ID)
    sql_find_room = """
        SELECT id FROM rooms
        WHERE room_type = 'group' AND scope_id = %s
    """
    cur.execute(sql_find_room, (group_id,))
    room_result = cur.fetchone()

    if not room_result:
        cur.close()
        conn.close()
        raise HTTPException(404, "Group not found")

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

# get a group's messages
@router.get("/groups/{group_id}/messages")
def get_group_messages(group_id: str):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    # get room for this group (using scope_id which stores Canvas group ID)
    cur.execute("""
        SELECT id FROM rooms
        WHERE room_type='group' AND scope_id=%s
    """, (group_id,))
    row = cur.fetchone()

    if not row:
        cur.close()
        conn.close()
        raise HTTPException(404, "Group room not found")

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

# get a group's posts
@router.get("/groups/{group_id}/posts")
def get_group_posts(group_id: str):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    sql = """
        SELECT * FROM posts 
        WHERE scope='group' AND scope_id=%s
        ORDER BY created_at DESC
    """
    cur.execute(sql, (group_id,))
    posts = cur.fetchall()

    cur.close()
    conn.close()

    return posts

