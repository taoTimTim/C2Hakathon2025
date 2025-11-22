from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..db import get_connection

router = APIRouter()

# models
class RoomCreate(BaseModel):
    name: str
    room_type: str # "class", "club", "subgroup", "group", "school"
    scope_id: str | None = None
    created_by: str | None = None # user who created it (None for system)


class RoomJoin(BaseModel):
    user_id: str

# get all rooms a user is in
@router.get("/rooms")
def get_user_rooms(user_id: str):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    sql = """
        SELECT r.id, r.name, r.room_type, r.scope_id, r.created_at
        FROM room_members rm
        JOIN rooms r ON rm.room_id = r.id
        WHERE rm.user_id = %s
        ORDER BY r.created_at DESC
    """

    cur.execute(sql, (user_id,))
    rooms = cur.fetchall()

    cur.close()
    conn.close()

    return rooms

# create a new room

@router.post("/rooms")
def create_room(room: RoomCreate):
    conn = get_connection()
    cur = conn.cursor()

    sql = """
        INSERT INTO rooms (name, scope_id, room_type, is_system_generated, created_by)
        VALUES (%s, %s, %s, %s, %s)
    """

    is_system_generated = room.created_by is None

    cur.execute(sql, (
        room.name,
        room.scope_id,
        room.room_type,
        is_system_generated,
        room.created_by
    ))

    conn.commit()
    room_id = cur.lastrowid

    # If user-created room -> creator joins automatically
    if room.created_by:
        sql2 = "INSERT INTO room_members (room_id, user_id) VALUES (%s, %s)"
        cur.execute(sql2, (room_id, room.created_by))
        conn.commit()

    cur.close()
    conn.close()

    return { "status": "success", "room_id": room_id }

