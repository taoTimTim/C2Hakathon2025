from fastapi import FastAPI
from .db import init_schema

app = FastAPI()

init_schema()

@app.get("/")
def home():
    return {"status", "Backend running!"}