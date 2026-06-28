import sqlite3
import bcrypt
import os

# Herhangi bir önbellek çakışmasını önlemek için benzersiz bir veritabanı adı
DB_NAME = "empatia_final_v10.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    return conn

def init_db():
    """Veritabanını ve tabloları eksiksiz sütunlarla sıfırdan kurar."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Kullanıcılar Tablosu (Sütunlar eksiksiz)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            password TEXT,
            avatar_path TEXT DEFAULT NULL
        )
    ''')
    
    # 2. Sohbetler Tablosu (Sütunlar eksiksiz)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sohbetler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            rol TEXT,
            mesaj TEXT,
            tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def register(username, email, password):
    init_db()  # Her ihtimale karşı tabloları kontrol et
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Şifreyi güvenli bir şekilde hash'le
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    try:
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username, email, hashed)
        )
        conn.commit()
        return True, "Kayıt başarılı!"
    except sqlite3.IntegrityError:
        return False, "Bu kullanıcı adı veya e-posta zaten kullanımda."
    finally:
        conn.close()

def login(email_or_username, password):
    init_db()  # Her ihtimale karşı tabloları kontrol et
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Hem kullanıcı adı hem de e-posta ile giriş desteği
    cursor.execute("SELECT id, username, password FROM users WHERE email = ? OR username = ?", (email_or_username, email_or_username))
    user = cursor.fetchone()
    conn.close()
    
    if user and bcrypt.checkpw(password.encode('utf-8'), user[2]):
        return True, {"id": user[0], "username": user[1]}
    return False, "E-posta/Kullanıcı adı veya şifre hatalı."