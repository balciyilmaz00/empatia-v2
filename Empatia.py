
import streamlit as st
from openai import OpenAI
from PIL import Image
import sqlite3

# Sayfa ayarları
st.set_page_config(
    page_title="Empatia",
    page_icon="logo.png",
    layout="centered"
)

# Logo
logo = Image.open("logo.png")
st.image(logo, width=180)
if st.button("🔄 Yeni Sohbet"):
    st.session_state.secilen_duygu = None
    st.session_state.messages = []
    st.rerun()
# Başlık
st.title("Empatia")
st.subheader("Yargılamadan dinleyen dijital arkadaşın.")

#veritabanı
import sqlite3

conn = sqlite3.connect("empatia.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS sohbetler (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rol TEXT,
    mesaj TEXT,
    tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
st.write("Veritabanı oluşturuldu")
conn.commit()
conn.close()

# Groq bağlantısı
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=st.secrets["GROQ_API_KEY"]
)

# Sohbet geçmişi
if "messages" not in st.session_state:
    st.session_state.messages = []
# Duygu seçimi
if "secilen_duygu" not in st.session_state:
 st.session_state.secilen_duygu = None

 if st.session_state.secilen_duygu is None:
    col1, col2, col3 = st.columns(3)


    with col1:  
        if st.button("😔 Üzgünüm"):
            st.session_state.secilen_duygu = "Üzgünüm"
            st.rerun()

        if st.button("😴 Yorgunum"):
            st.session_state.secilen_duygu = "Yorgunum"
            st.rerun()

    with col2:
        if st.button("😟 Kaygılıyım"):
            st.session_state.secilen_duygu = "Kaygılıyım"
            st.rerun()

        if st.button("😊 İyiyim"):
            st.session_state.secilen_duygu = "İyiyim"
            st.rerun()

    with col3:
        if st.button("😡 Sinirliyim"):
            st.session_state.secilen_duygu = "Sinirliyim"
            st.rerun()

        if st.button("🤔 Kararsızım"):
            st.session_state.secilen_duygu = "Kararsızım"
            st.rerun()
        if st.session_state.secilen_duygu is not None:


         st.stop()
# Önceki mesajları göster
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Kullanıcı mesajı
prompt = st.chat_input("Bugün nasıl hissediyorsun?")

# Önceki mesajları göster
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


if prompt:

    # Kullanıcı mesajını göster
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )
    conn = sqlite3.connect("empatia.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO sohbetler (rol, mesaj) VALUES (?, ?)",
        ("user", prompt)
    )

    conn.commit()
    conn.close()
    
    with st.chat_message("user"):
        st.markdown(prompt)

    # Sistem promptu
    mesajlar = [
        {
            "role": "system",
            "content": """
Sen Empatia'sın.

İnsanlara eşlik eden dijital bir arkadaşsın.

Kurallar:
- Türkçe konuş.
- Samimi ol.
- Kısa ve anlaşılır cevaplar ver.
- İnsanları yargılama.
- Duygusal destek sun.
- Bilgi sorularına doğru cevap ver.
- Bilmediğin bilgileri uydurma.
- Gereksiz uzun cevaplar verme.
"""
        }
    ]

    mesajlar.extend(st.session_state.messages)

    with st.chat_message("assistant"):

        with st.spinner("Empatia düşünüyor..."):

            cevap = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=mesajlar
            )

            yanit = cevap.choices[0].message.content

            st.markdown(yanit)

    st.session_state.messages.append(
        {"role": "assistant", "content": yanit}
    )

# Alt bilgi
st.markdown("---")

st.markdown(
    """
    <div style='text-align:center; color:gray;'>
    ❤️ Her zaman yanımda olan, en çok bu başarıyı hak eden<br>
    <b>Annem ve Babama, EMİŞ SULTANIMA ❤️</b>
    </div>
    """,
    unsafe_allow_html=True
)

import streamlit as st
from openai import OpenAI
from PIL import Image

# Sayfa ayarları
st.set_page_config(
    page_title="Empatia",
    page_icon="logo.png",
    layout="centered"
)