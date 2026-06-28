import sqlite3
import bcrypt

DB = "empatia.db"

def register(username, email, password):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        avatar_path TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    try:
        cur.execute(
            "INSERT INTO users(full_name, email, password_hash, avatar_path) VALUES(?,?,?,?)",
            (username, email, hashed, None)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def login(email, password):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    try:
        cur.execute(
            "SELECT id, full_name, password_hash FROM users WHERE email=?",
            (email,)
        )
        user = cur.fetchone()
        
        if user and bcrypt.checkpw(password.encode(), user[2].encode()):
            return user
    except sqlite3.OperationalError:
        return None
    finally:
        conn.close()

    return None
