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
        SELECT id, name, description, category, contact, image_url, created_at
        FROM clubs
        ORDER BY name ASC
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
        SELECT r.id, r.name, r.description, r.created_at, rm.role
        FROM room_members rm
        JOIN rooms r ON rm.room_id = r.id
        WHERE rm.user_id = %s AND r.room_type = 'club'
        ORDER BY r.name ASC
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

    # Create club room directly (no separate clubs table)
    sql = """
        INSERT INTO rooms (name, description, room_type, max_members, is_system_generated, created_by)
        VALUES (%s, %s, 'club', NULL, FALSE, %s)
    """

    cur.execute(sql, (club.name, club.description, club.created_by))
    conn.commit()
    room_id = cur.lastrowid

    # Auto-add creator to room_members as leader
    sql2 = """
        INSERT INTO room_members (room_id, user_id, role)
        VALUES (%s, %s, 'leader')
    """
    cur.execute(sql2, (room_id, club.created_by))
    conn.commit()

    cur.close()
    conn.close()

    return {
        "status": "success",
        "club_id": room_id,
        "room_id": room_id
    }

# join a club
@router.post("/clubs/{club_id}/join")
def join_club(club_id: int, body: ClubJoin):
    conn = get_connection()
    cur = conn.cursor()

    # Verify club exists
    cur.execute("SELECT id FROM rooms WHERE id = %s AND room_type = 'club'", (club_id,))
    if not cur.fetchone():
        cur.close()
        conn.close()
        raise HTTPException(404, "Club not found")

    # Add user to room_members
    sql = """
        INSERT INTO room_members (room_id, user_id, role, joined_at)
        VALUES (%s, %s, 'member', NOW())
        ON DUPLICATE KEY UPDATE joined_at = NOW()
    """

    try:
        cur.execute(sql, (club_id, body.user_id))
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

    # Remove user from room_members
    sql = """
        DELETE FROM room_members
        WHERE room_id = %s AND user_id = %s
    """

    cur.execute(sql, (club_id, user_id))
    conn.commit()

    removed = cur.rowcount

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
        SELECT users.canvas_user_id, users.name, room_members.role
        FROM room_members
        JOIN users ON room_members.user_id = users.canvas_user_id
        WHERE room_members.room_id = %s
        ORDER BY users.name ASC
    """

    cur.execute(sql, (club_id,))
    members = cur.fetchall()

    cur.close()
    conn.close()

    return members

# get club by id
@router.get("/clubs/{club_id}")
def get_club(club_id: int):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    sql = "SELECT * FROM rooms WHERE id = %s AND room_type = 'club'"
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

    # Verify club exists
    cur.execute("SELECT id FROM rooms WHERE id = %s AND room_type = 'club'", (club_id,))
    if not cur.fetchone():
        cur.close()
        conn.close()
        raise HTTPException(404, "Club not found")

    # Get messages from the club room
    sql = """
        SELECT * FROM messages
        WHERE room_id = %s
        ORDER BY created_at ASC
    """
    cur.execute(sql, (club_id,))
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