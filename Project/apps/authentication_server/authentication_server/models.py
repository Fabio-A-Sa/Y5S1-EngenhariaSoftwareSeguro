import sqlite3
import os.path

from authentication_server import env

DATABASE_PATH = f"{env.INSTANCE_DIR}/users.db"

def init_db():
    if os.path.exists(DATABASE_PATH):
        return
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        verified BOOLEAN NOT NULL
    )"""
    )
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS nonces (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        nonce TEXT NOT NULL,
        expiry DATETIME NOT NULL,
        FOREIGN KEY (username) REFERENCES users (username)
    )"""
    )
    
    cursor.execute(
        """INSERT INTO users (username, password, email, verified) VALUES (
            "alice",
            "JDJiJDEyJFozZjBKMHNjM0V3dWlBWUZYc29WVWVmdmE1UlZub2VQZDVzb2FENDJMSjh1aGwuTkg1MFNp",
            "admin@example.com",
            1
        )
        """
    )
    conn.commit()
    conn.close()