from fastapi import FastAPI
from .db import init_schema
from .routers import messages, users, rooms, classes, groups, clubs, posts

app = FastAPI()

# Include all routers
app.include_router(messages.router)
app.include_router(users.router)
app.include_router(rooms.router)
app.include_router(classes.router)
app.include_router(groups.router)
app.include_router(clubs.router)
app.include_router(posts.router)

init_schema()

@app.get("/")
def home():
    return {"status": "Backend running!"}