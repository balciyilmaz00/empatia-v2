import streamlit as str
import sqlite3
# ... diğer importların (os, groq vs.) ...

# auth dosyasındaki veritabanı adıyla birebir eşitleme
DB_NAME = "empatia_final_v10.db"

# HATA VEREN ESKİ SOHBET ÇEKME ALANINI BU GÜVENLİ KODLA DEĞİŞTİR:
def get_chat_history(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        # Eğer sunucuda tablo bir şekilde uçtuysa çökmesin, anında oluştursun
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sohbetler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                rol TEXT,
                mesaj TEXT,
                tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute("SELECT rol, mesaj FROM sohbetler WHERE user_id = ? ORDER BY tarih ASC", (user_id,))
        history = cursor.fetchall()
        return history
    except sqlite3.OperationalError:
        return []
    finally:
        conn.close()

# Mesaj kaydederken kullanacağın güvenli fonksiyon:
def save_chat_message(user_id, rol, mesaj):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO sohbetler (user_id, rol, mesaj) VALUES (?, ?, ?)", (user_id, rol, mesaj))
    conn.commit()
    conn.close()