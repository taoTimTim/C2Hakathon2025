from fastapi import APIRouter, HTTPException
from ..db import get_connection
from pydantic import BaseModel

router = APIRouter()

class UserCreate(BaseModel):
    canvas_user_id: str
    name: str
    role: str = "student"

# Create a new user
@router.post("/users")
def create_user(user: UserCreate):
    conn = get_connection()
    cur = conn.cursor()

    try:
        sql = """
            INSERT INTO users (canvas_user_id, name, role)
            VALUES (%s, %s, %s)
        """
        cur.execute(sql, (user.canvas_user_id, user.name, user.role))
        conn.commit()
        
        cur.close()
        conn.close()
        
        return {"status": "success", "user_id": user.canvas_user_id}
    except Exception as e:
        cur.close()
        conn.close()
        raise HTTPException(status_code=400, detail=str(e))

# Get a user by ID
@router.get("/users/{user_id}")
def get_user(user_id: str):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    try:
        cur.execute("SELECT * FROM users WHERE canvas_user_id = %s", (user_id,))
        user = cur.fetchone()

        cur.close()
        conn.close()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return user
    except HTTPException:
        raise
    except Exception as e:
        cur.close()
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))

# Get all users
@router.get("/users")
def get_all_users():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    try:
        cur.execute("SELECT * FROM users")
        users = cur.fetchall()

        cur.close()
        conn.close()

        return users
    except Exception as e:
        cur.close()
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))
