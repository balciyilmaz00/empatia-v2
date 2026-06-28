import streamlit as st
from openai import OpenAI
from PIL import Image
import sqlite3
import os
from auth import register, login

# Sayfa ayarları
st.set_page_config(
    page_title="Empatia",
    page_icon="logo.png",
    layout="centered"
)

# --- PREMIUM UI CSS DOKUNUŞLARI ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Buton Yumuşatmaları */
    .stButton>button {
        border-radius: 8px !important;
        font-weight: 500 !important;
    }
    
    /* Giriş/Kayıt Alanı Konteyneri */
    .auth-container {
        background: #ffffff;
        padding: 30px;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.03);
        border: 1px solid #f1f3f5;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Gerekli Klasörlerin Kontrolü
if not os.path.exists("avatars"):
    os.makedirs("avatars")

# Veritabanı Şeması İlklendirme
conn = sqlite3.connect("empatia.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    avatar_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS sohbetler (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    rol TEXT,
    mesaj TEXT,
    tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
""")
conn.commit()
conn.close()

# Groq Bağlantısı
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=st.secrets["GROQ_API_KEY"]
)

# Oturum Durum Yönetimi
if "giris_yapti" not in st.session_state:
    st.session_state.giris_yapti = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "secilen_duygu" not in st.session_state:
    st.session_state.secilen_duygu = None


# --- 1. OTURUM KONTROLÜ (GİRİŞ & KAYIT) ---
if not st.session_state.giris_yapti:
    st.title("Empatia")
    st.caption("Yapay zeka destekli, güvenli ve anonim mentorluk alanı.")
    
    tab_login, tab_register = st.tabs(["🔒 Oturum Aç", "📝 Hesap Oluştur"])
    
    with tab_login:
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        login_email = st.text_input("E-posta Adresiniz", key="login_email_input")
        login_password = st.text_input("Şifreniz", type="password", key="login_pass_input")
        
        if st.button("Giriş Yap", type="primary", use_container_width=True):
            user = login(login_email, login_password)
            if user:
                st.session_state.giris_yapti = True
                st.session_state.user_id = user[0]
                st.session_state.username = user[1]
                st.rerun()
            else:
                st.error("E-posta adresi veya şifre hatalı. Lütfen tekrar deneyin.")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with tab_register:
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        reg_name = st.text_input("Adınız ve Soyadınız", key="reg_name_input")
        reg_email = st.text_input("E-posta Adresiniz", key="reg_email_input")
        reg_password = st.text_input("Güçlü Bir Şifre", type="password", key="reg_pass_input")
        
        if st.button("Kayıt İşlemini Tamamla", type="primary", use_container_width=True):
            if reg_name.strip() == "" or reg_email.strip() == "" or reg_password.strip() == "":
                st.warning("Lütfen tüm alanları eksiksiz doldurun.")
            elif register(reg_name, reg_email, reg_password):
                st.success("Hesabınız başarıyla oluşturuldu! 'Oturum Aç' sekmesinden giriş yapabilirsiniz.")
            else:
                st.error("Bu e-posta adresi zaten sisteme kayıtlı.")
        st.markdown('</div>', unsafe_allow_html=True)
        
    st.stop()


# --- 2. ANA PANEL (OTURUM AÇILDIKTAN SONRASI) ---

# Kullanıcı profil resmi kontrolü
conn = sqlite3.connect("empatia.db")
cursor = conn.cursor()
cursor.execute("SELECT avatar_path FROM users WHERE id = ?", (st.session_state.user_id,))
res = cursor.fetchone()
conn.close()

avatar_resmi = "https://www.w3schools.com/howto/img_avatar.png"
if res and res[0] and os.path.exists(res[0]):
    avatar_resmi = res[0]

# --- SOL MENÜ (SIDEBAR) - ARTIK KAYMA YAPMAZ ---
with st.sidebar:
    st.subheader("👤 Profil")
    st.image(avatar_resmi, width=70)
    st.markdown(f"**{st.session_state.username}**")
    st.caption("🟢 Çevrimiçi")
        
    uploaded_file = st.file_uploader("Profil Fotoğrafını Değiştir", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        file_path = f"avatars/user_{st.session_state.user_id}.png"
        img = Image.open(uploaded_file)
        img.save(file_path)
        
        conn = sqlite3.connect("empatia.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET avatar_path = ? WHERE id = ?", (file_path, st.session_state.user_id))
        conn.commit()
        conn.close()
        st.rerun()

    st.markdown("---")
    st.subheader("🕒 Son Mesajlarınız")
    
    # Güvenli ve kayma yapmayan temiz geçmiş çekme mantığı
    conn = sqlite3.connect("empatia.db")
    cursor = conn.cursor()
    cursor.execute("SELECT mesaj, tarih FROM sohbetler WHERE user_id = ? AND rol = 'user' ORDER BY tarih DESC LIMIT 5", (st.session_state.user_id,))
    gecmis_mesajlar = cursor.fetchall()
    conn.close()
    
    if gecmis_mesajlar:
        for msj, tarih in gecmis_mesajlar:
            kisa_msj = msj if len(msj) <= 25 else msj[:25] + "..."
            # Streamlit'in kendi native bileşenini kullanarak kaymayı engelledik
            st.info(f"⏱️ {tarih[11:16]}\n\n{kisa_msj}")
    else:
        st.caption("Henüz geçmiş mesajınız bulunmuyor.")
        
    st.markdown("---")
    if st.button("🚪 Oturumu Kapat", use_container_width=True, type="secondary"):
        st.session_state.giris_yapti = False
        st.session_state.user_id = None
        st.session_state.username = None
        st.session_state.messages = []
        st.session_state.secilen_duygu = None
        st.rerun()


# --- ANA EKRAN İÇERİĞİ ---
try:
    logo = Image.open("logo.png")
    st.image(logo, width=130)
except:
    pass

# Başlık "Empatia" olarak düzeltildi
st.title("Empatia")

# Üst buton alanı düzenlendi
col_title, col_btn = st.columns([3, 1])
with col_btn:
    if st.button("🔄 Yeni Sohbet", type="secondary", use_container_width=True):
        st.session_state.secilen_duygu = None
        st.session_state.messages = []
        st.rerun()

# Mod Seçim Ekranı
if st.session_state.secilen_duygu is None:
    st.markdown("#### Odaklanmak istediğiniz güncel duygu durumunu seçin:")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Bunalmış / Üzgün", use_container_width=True):
            st.session_state.secilen_duygu = "Üzgün"
            st.rerun()
        if st.button("Öfkeli / Gergin", use_container_width=True):
            st.session_state.secilen_duygu = "Sinirli"
            st.rerun()
    with c2:
        if st.button("Stresli / Kaygılı", use_container_width=True):
            st.session_state.secilen_duygu = "Kaygılı"
            st.rerun()
        if st.button("Kararsız / Belirsiz", use_container_width=True):
            st.session_state.secilen_duygu = "Kararsız"
            st.rerun()
    with c3:
        if st.button("Zihnen Yorgun", use_container_width=True):
            st.session_state.secilen_duygu = "Yorgun"
            st.rerun()
        if st.button("Dengeli / İyi", use_container_width=True):
            st.session_state.secilen_duygu = "İyi"
            st.rerun()
            
    st.stop()

st.info(f"Mevcut Analiz Modu: {st.session_state.secilen_duygu}")

# Chat Akışı
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Kullanıcı Girdisi
prompt = st.chat_input("Paylaşmak istediğiniz düşünceleri buraya yazın...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Veritabanına Yazma
    conn = sqlite3.connect("empatia.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO sohbetler (user_id, rol, mesaj) VALUES (?, ?, ?)",
        (st.session_state.user_id, "user", prompt)
    )
    conn.commit()
    conn.close()

    # System Prompt
    mesajlar = [
        {
            "role": "system",
            "content": f"Sen Empatia adında profesyonel, klinik düzeyde duyarlı, sakin ve empatik bir yapay zeka mentörüsün. Kullanıcı şu an kendini '{st.session_state.secilen_duygu}' olarak tanımladı. Yanıtların sakinleştirici, anlamlı, net ve yargıdan tamamen uzak olmalıdır. Uzun paragraflar yerine öz, derinlikli ve yönlendirici cümleler tercih et."
        }
    ]
    mesajlar.extend(st.session_state.messages)

    # Yanıt Üretimi
    with st.chat_message("assistant"):
        with st.spinner("Analiz ediliyor..."):
            cevap = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=mesajlar
            )
            yanit = cevap.choices[0].message.content
            st.markdown(yanit)

    st.session_state.messages.append({"role": "assistant", "content": yanit})
    
    conn = sqlite3.connect("empatia.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO sohbetler (user_id, rol, mesaj) VALUES (?, ?, ?)",
        (st.session_state.user_id, "assistant", yanit)
    )
    conn.commit()
    conn.close()
    
    st.rerun()

# Alt Bilgi
st.markdown("---")
st.markdown(
    """
    <div style='text-align:center; color:#adb5bd; font-size: 0.85rem;'>
    ❤️ Her zaman yanımda olan, en çok bu başarıyı hak eden<br>
    <b>Annem ve Babama, EMİŞ SULTANIMA ❤️</b>
    </div>
    """,
    unsafe_allow_html=True
)