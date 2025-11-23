from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..db import get_connection
import pandas as pd
import os

router = APIRouter()

class GroupJoin(BaseModel):
    user_id: str

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

# join a group (from CSV/items)
@router.post("/groups/{group_id}/join")
def join_group(group_id: int, body: GroupJoin):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    # Get group info from CSV
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    groups_path = os.path.join(BASE_DIR, 'groups.csv')
    
    group_info = None
    if os.path.exists(groups_path):
        try:
            df = pd.read_csv(groups_path, keep_default_na=False)
            group_row = df[df['id'] == group_id]
            if not group_row.empty:
                group_info = group_row.iloc[0].to_dict()
        except Exception as e:
            print(f"Error reading groups.csv: {e}")
    
    if not group_info:
        cur.close()
        conn.close()
        raise HTTPException(404, "Group not found")

    # Find or create room for this group
    # Use scope_id to store the CSV group id
    sql_find_room = """
        SELECT id FROM rooms
        WHERE room_type = 'group' AND scope_id = %s
    """
    cur.execute(sql_find_room, (str(group_id),))
    room_result = cur.fetchone()

    if room_result:
        room_id = room_result["id"]
    else:
        # Create new room for this group
        sql_create_room = """
            INSERT INTO rooms (name, description, scope_id, room_type, is_system_generated, created_at)
            VALUES (%s, %s, %s, 'group', TRUE, NOW())
        """
        cur.execute(sql_create_room, (
            group_info.get('name', 'Unnamed Group'),
            group_info.get('description', ''),
            str(group_id)
        ))
        conn.commit()
        room_id = cur.lastrowid

    # Add user to room_members
    sql_join = """
        INSERT INTO room_members (room_id, user_id, role, joined_at)
        VALUES (%s, %s, 'member', NOW())
        ON DUPLICATE KEY UPDATE joined_at = NOW()
    """

    try:
        cur.execute(sql_join, (room_id, body.user_id))
        conn.commit()
    except Exception as e:
        cur.close()
        conn.close()
        raise HTTPException(400, str(e))

    cur.close()
    conn.close()

    return {
        "status": "success",
        "group_id": group_id,
        "room_id": room_id,
        "user_id": body.user_id,
        "group_name": group_info.get('name', '')
    }

