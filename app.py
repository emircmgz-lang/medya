import streamlit as st
from openai import OpenAI
import os, json, bcrypt

# API KEY
os.environ["OPENAI_API_KEY"] = "BURAYA_API_KEY"
client = OpenAI()

# --- USER SYSTEM ---
def load_users():
    with open("users.json", "r") as f:
        return json.load(f)

def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f)

def register(username, password):
    users = load_users()
    if username in users:
        return False
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    users[username] = hashed
    save_users(users)
    return True

def login(username, password):
    users = load_users()
    if username in users:
        return bcrypt.checkpw(password.encode(), users[username].encode())
    return False

# --- AI ANALİZ ---
def ai_analiz(konu):
    response = client.responses.create(
        model="gpt-5-mini",
        input=f"""
        Bu içerik fikrini analiz et:
        {konu}

        Viral skor, kısa yorum ve 5 hashtag ver.
        """
    )
    return response.output[0].content[0].text

# --- METRİK TAHMİN ---
def tahmin_hesapla(skor):
    like = skor * 10
    yorum = skor * 2
    takipci = skor * 1.5
    return int(like), int(yorum), int(takipci)

# --- UI ---
st.title("Viral Analiz Platformu")

menu = st.sidebar.selectbox("Menü", ["Giriş", "Kayıt"])

if "auth" not in st.session_state:
    st.session_state.auth = False

# KAYIT
if menu == "Kayıt":
    u = st.text_input("Kullanıcı adı")
    p = st.text_input("Şifre", type="password")

    if st.button("Kayıt Ol"):
        if register(u, p):
            st.success("Kayıt başarılı")
        else:
            st.error("Kullanıcı var")

# GİRİŞ
if menu == "Giriş":
    u = st.text_input("Kullanıcı adı")
    p = st.text_input("Şifre", type="password")

    if st.button("Giriş Yap"):
        if login(u, p):
            st.session_state.auth = True
            st.success("Giriş başarılı")
        else:
            st.error("Hatalı giriş")

# ANA SİSTEM
if st.session_state.auth:

    platform = st.selectbox("Platform", ["TikTok","Instagram","YouTube"])
    saat = st.slider("Saat", 0, 23, 18)
    konu = st.text_input("Video konusu")
    sure = st.number_input("Süre", 1, 1000, 60)

    if st.button("Analiz Et"):

        skor = 50

        if 18 <= saat <= 22:
            skor += 20
        elif 0 <= saat <= 6:
            skor -= 15

        if sure < 15:
            skor += 10
        elif sure > 60:
            skor -= 10

        skor = max(0, min(100, skor))

        ai = ai_analiz(konu)

        like, yorum, takipci = tahmin_hesapla(skor)

        st.subheader("Sonuç")

        st.write(f"Viral Skor: {skor}")
        st.write(f"Tahmini Beğeni: {like}")
        st.write(f"Tahmini Yorum: {yorum}")
        st.write(f"Tahmini Takipçi: {takipci}")

        st.text(ai)