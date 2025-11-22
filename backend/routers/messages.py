from fastapi import APIRouter
from ..db import get_connection
from pydantic import BaseModel

router = APIRouter()

class MessageCreate(BaseModel):
    user_id: str
    content: str

class MessageEdit(BaseModel):
    content: str


# Get all messages for a specific room
@router.get("/rooms/{room_id}/messages")
def get_messages(room_id: int):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    sql = "SELECT * FROM messages WHERE room_id = %s ORDER BY created_at DESC"
    cur.execute(sql, (room_id,))

    messages = cur.fetchall()

    cur.close()
    conn.close()
    return messages


# Insert a message
@router.post("/rooms/{room_id}/messages")
def send_message(room_id: int, message: MessageCreate):
    conn = get_connection()
    cur = conn.cursor()

    sql = """
        INSERT INTO messages (room_id, user_id, content)
        VALUES (%s, %s, %s)
    """

    cur.execute(sql, (room_id, message.user_id, message.content))
    conn.commit()

    message_id = cur.lastrowid

    cur.close()
    conn.close()

    return {
        "status": "success",
        "message_id": message_id,
        "room_id": room_id,
        "user_id": message.user_id,
        "content": message.content
    }

# edit a message
@router.patch("/messages/{message_id}")
def edit_message(message_id: int, new: MessageEdit):
    conn = get_connection()
    cur = conn.cursor()

    sql = """
        UPATE messages SET content = %s, is_edited = TRUE, edited_at = CURRENT_TIMESTAMP WHERE id = %s
    """

    cur.execute(sql, (new.content, message_id))
    conn.commit()

    updated = cur.rowcount

    cur.close()
    conn.close()

    if updated == 0:
        return {"status": "error", "message": "Message not found"}

    return {
        "status": "sucess",
        "message_id": message_id,
        "new_content": new.content
    }

@router.delete("/messages/{message_id}")
def delete_message(message_id: int, user_id: str):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    # Check who owns the message
    cur.execute("SELECT user_id FROM messages WHERE id = %s", (message_id,))
    result = cur.fetchone()

    if result is None:
        cur.close()
        conn.close()
        return {"status": "error", "message": "Message not found"}

    message_owner = result["user_id"]

    # Prevent deleting someone elses message
    if message_owner != user_id:
        cur.close()
        conn.close()
        return {
            "status": "error",
            "message": "Not authorized to delete this message"
        }

    # Delete the message
    cur.execute("DELETE FROM messages WHERE id = %s", (message_id,))
    conn.commit()

    cur.close()
    conn.close()

    return {
        "status": "success",
        "message_id": message_id,
        "deleted_by": user_id
    }
