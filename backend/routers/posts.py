from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..db import get_connection

router = APIRouter()

class PostCreate(BaseModel):
    scope: str          # "school", "class" (same as course), "club", "group", "subgroup"
    scope_id: str | None = None
    author: str
    title: str
    content: str
    image_url: str | None = None

# create a post
@router.post("/posts")
def create_post(post: PostCreate):
    conn = get_connection()
    cur = conn.cursor()

    # Treat "course" as equivalent to "class"
    scope = "class" if post.scope == "course" else post.scope

    sql = """
        INSERT INTO posts (scope, scope_id, author, title, content, image_url)
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    cur.execute(sql, (
        scope,
        post.scope_id,
        post.author,
        post.title,
        post.content,
        post.image_url
    ))

    conn.commit()
    post_id = cur.lastrowid

    cur.close()
    conn.close()

    return {
        "status": "success",
        "post_id": post_id
    }

# get all campus (main bulletin board) posts if scope is school
# else, get posts for specific scope (class or club)
@router.get("/posts")
def list_posts(scope: str, scope_id: str | None = None):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    if scope == "school":
        sql = "SELECT * FROM posts WHERE scope='school' ORDER BY created_at DESC"
        cur.execute(sql)

    elif scope in ("class", "club", "group", "subgroup"):
        sql = "SELECT * FROM posts WHERE scope=%s AND scope_id=%s ORDER BY created_at DESC"
        cur.execute(sql, (scope, scope_id))
    
    elif scope == "course":
        # Treat "course" as equivalent to "class"
        sql = "SELECT * FROM posts WHERE scope='class' AND scope_id=%s ORDER BY created_at DESC"
        cur.execute(sql, (scope_id,))

    else:
        raise HTTPException(400, "Invalid scope provided")

    posts = cur.fetchall()

    cur.close()
    conn.close()

    return posts

# delete a post
@router.delete("/posts/{post_id}")
def delete_post(post_id: int):
    conn = get_connection()
    cur = conn.cursor()

    sql = "DELETE FROM posts WHERE id = %s"
    cur.execute(sql, (post_id,))
    conn.commit()

    deleted = cur.rowcount  # number of rows deleted

    cur.close()
    conn.close()

    if deleted == 0:
        return {"status": "error", "message": "Post not found"}

    return {"status": "success", "post_id": post_id}
