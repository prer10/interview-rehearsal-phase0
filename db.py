"""
db.py — persistent session storage via Postgres (Neon). Lives at the
project root, imported directly by main.py.

Deliberately raw psycopg2, not an ORM (SQLAlchemy etc.) — with one table
and a handful of queries, an ORM would add a layer of abstraction
without earning its complexity yet. Worth revisiting if the schema
grows.
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")


def get_connection():
    return psycopg2.connect(DATABASE_URL)


def init_db():
    """
    Creates the sessions table if it doesn't exist yet. Safe to call
    every time the app starts — CREATE TABLE IF NOT EXISTS is a no-op
    if it's already there.
    """
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id UUID PRIMARY KEY,
                role TEXT NOT NULL,
                score INTEGER,
                summary TEXT,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)
    conn.commit()
    conn.close()


def save_session(session_id: str, role: str, score: int, summary: str):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO sessions (id, role, score, summary)
            VALUES (%s, %s, %s, %s)
            """,
            (session_id, role, score, summary),
        )
    conn.commit()
    conn.close()


def get_all_sessions(limit: int = 50):
    """
    Returns most recent sessions first — this is what Score Trends,
    Practice Calendar, and Session Records will all read from.
    """
    conn = get_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            SELECT id, role, score, summary, created_at
            FROM sessions
            ORDER BY created_at DESC
            LIMIT %s
            """,
            (limit,),
        )
        rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


if __name__ == "__main__":
    # Manual test: creates the table, inserts one fake row, reads it back.
    init_db()
    print("Table ready.")
    save_session("11111111-1111-1111-1111-111111111111", "SDE", 7, "Test summary.")
    print("Inserted a test row.")
    for row in get_all_sessions():
        print(row)