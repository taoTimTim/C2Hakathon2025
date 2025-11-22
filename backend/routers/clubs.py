from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..db import get_connection

router = APIRouter()

class ClubCreate(BaseModel):
    name: str
    description: str | None = None
    created_by: str   # user_id of creator

class ClubJoin(BaseModel):
    user_id: str


# get all clubs (for search/browsing)
@router.get("/clubs/all")
def get_all_clubs():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    sql = """
        SELECT c.id, c.name, c.description, c.created_at,
               COUNT(cm.user_id) as members_count
        FROM clubs c
        LEFT JOIN club_members cm ON c.id = cm.club_id
        GROUP BY c.id, c.name, c.description, c.created_at
        ORDER BY c.name ASC
    """

    cur.execute(sql)
    clubs = cur.fetchall()

    cur.close()
    conn.close()

    return clubs

# get clubs a user is in
@router.get("/clubs")
def get_user_clubs(user_id: str):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    sql = """
        SELECT c.id, c.name, c.description, c.created_at
        FROM club_members cm
        JOIN clubs c ON cm.club_id = c.id
        WHERE cm.user_id = %s
        ORDER BY c.name ASC
    """

    cur.execute(sql, (user_id,))
    clubs = cur.fetchall()

    cur.close()
    conn.close()

    return clubs

# create a club
@router.post("/clubs")
def create_club(club: ClubCreate):
    conn = get_connection()
    cur = conn.cursor()

    sql = """
        INSERT INTO clubs (name, description, created_by)
        VALUES (%s, %s, %s)
    """

    cur.execute(sql, (club.name, club.description, club.created_by))
    conn.commit()

    club_id = cur.lastrowid

    # Auto-add creator to club_members as leader
    sql2 = """
        INSERT INTO club_members (club_id, user_id, role)
        VALUES (%s, %s, 'leader')
    """
    cur.execute(sql2, (club_id, club.created_by))

    # Create a room for the club (for messaging/channels)
    sql3 = """
        INSERT INTO rooms (name, scope_id, room_type, is_system_generated, created_by)
        VALUES (%s, %s, 'club', FALSE, %s)
    """
    cur.execute(sql3, (club.name, str(club_id), club.created_by))
    conn.commit()
    room_id = cur.lastrowid

    # Add creator to room_members
    sql4 = "INSERT INTO room_members (room_id, user_id) VALUES (%s, %s)"
    cur.execute(sql4, (room_id, club.created_by))

    conn.commit()
    cur.close()
    conn.close()

    return {
        "status": "success",
        "club_id": club_id,
        "room_id": room_id
    }

# join a club
@router.post("/clubs/{club_id}/join")
def join_club(club_id: int, body: ClubJoin):
    conn = get_connection()
    cur = conn.cursor()

    sql = """
        INSERT INTO club_members (club_id, user_id)
        VALUES (%s, %s)
    """

    try:
        cur.execute(sql, (club_id, body.user_id))
        conn.commit()
        
        # Also add user to the club's room (for messaging)
        sql_find_room = """
            SELECT id FROM rooms
            WHERE room_type = 'club' AND scope_id = %s
        """
        cur.execute(sql_find_room, (str(club_id),))
        room_result = cur.fetchone()
        
        if room_result:
            room_id = room_result[0]
            sql_room = """
                INSERT INTO room_members (room_id, user_id, joined_at)
                VALUES (%s, %s, NOW())
                ON DUPLICATE KEY UPDATE joined_at = NOW()
            """
            cur.execute(sql_room, (room_id, body.user_id))
            conn.commit()
    except Exception as e:
        cur.close()
        conn.close()
        raise HTTPException(400, str(e))

    cur.close()
    conn.close()

    return {
        "status": "success",
        "club_id": club_id,
        "user_id": body.user_id
    }

# leave a club
@router.delete("/clubs/{club_id}/leave")
def leave_club(club_id: int, user_id: str):
    conn = get_connection()
    cur = conn.cursor()

    sql = """
        DELETE FROM club_members
        WHERE club_id=%s AND user_id=%s
    """

    cur.execute(sql, (club_id, user_id))
    conn.commit()

    removed = cur.rowcount

    # Also remove user from the club's room
    sql_find_room = """
        SELECT id FROM rooms
        WHERE room_type = 'club' AND scope_id = %s
    """
    cur.execute(sql_find_room, (str(club_id),))
    room_result = cur.fetchone()
    
    if room_result:
        room_id = room_result[0]
        sql_room = "DELETE FROM room_members WHERE room_id = %s AND user_id = %s"
        cur.execute(sql_room, (room_id, user_id))
        conn.commit()

    cur.close()
    conn.close()

    if removed == 0:
        raise HTTPException(400, "User is not a member of this club")

    return {"status": "success", "club_id": club_id, "user_id": user_id}

# get club members
@router.get("/clubs/{club_id}/members")
def get_club_members(club_id: int):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    sql = """
        SELECT users.canvas_user_id, users.name, club_members.role
        FROM club_members
        JOIN users ON club_members.user_id = users.canvas_user_id
        WHERE club_members.club_id = %s
        ORDER BY users.name ASC
    """

    cur.execute(sql, (club_id,))
    members = cur.fetchall()

    cur.close()
    conn.close()

    return members

# get clubs a user is in
@router.get("/clubs/{club_id}")
def get_club(club_id: int):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    sql = "SELECT * FROM clubs WHERE id=%s"
    cur.execute(sql, (club_id,))
    club = cur.fetchone()

    cur.close()
    conn.close()

    if not club:
        raise HTTPException(404, "Club not found")

    return club

# get club messages (channel)
@router.get("/clubs/{club_id}/messages")
def get_club_messages(club_id: int):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    # Find the room for this club
    sql_find_room = """
        SELECT id FROM rooms
        WHERE room_type = 'club' AND scope_id = %s
    """
    cur.execute(sql_find_room, (str(club_id),))
    room_result = cur.fetchone()

    if not room_result:
        cur.close()
        conn.close()
        raise HTTPException(404, "Club room not found")

    room_id = room_result["id"]

    # Get messages from that room
    sql = """
        SELECT * FROM messages
        WHERE room_id = %s
        ORDER BY created_at ASC
    """
    cur.execute(sql, (room_id,))
    messages = cur.fetchall()

    cur.close()
    conn.close()

    return messages

# get club posts (announcements)
@router.get("/clubs/{club_id}/posts")
def get_club_posts(club_id: int):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    sql = """
        SELECT * FROM posts 
        WHERE scope='club' AND scope_id=%s
        ORDER BY created_at DESC
    """
    cur.execute(sql, (str(club_id),))
    posts = cur.fetchall()

    cur.close()
    conn.close()

    return posts