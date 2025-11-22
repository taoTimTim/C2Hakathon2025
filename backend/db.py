import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CA_PATH = os.path.join(BASE_DIR, "database", "ca.pem")
SCHEMA_PATH = os.path.join(BASE_DIR, "database", "schema.sql")

def get_connection():
    return mysql.connector.connect(
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        ssl_ca=CA_PATH,
        ssl_verify_cert=True
    )

def init_schema():
    conn = get_connection()
    cur = conn.cursor()
    print("Intializing database schema...")

    with open(SCHEMA_PATH, "r") as f:
        sql = f.read()

    statements = sql.split(";")

    for statement in statements:
        stmt = statement.strip()
        if stmt:
            cur.execute(stmt + ";")

    conn.commit()
    cur.close()
    conn.close()

    print("Schema intialization complete.")