import streamlit as st
import requests
import os

st.set_page_config(page_title="Viral Analiz", layout="centered")

st.title("Viral Analiz Aracı")

st.info("Bu araç içerik fikrini analiz eder ve tahmini performans verir.")

# API KEY
API_KEY = os.environ.get("HF_API_KEY")

# Platformlar
video_platformlar = ["TikTok", "Instagram Reels", "YouTube Shorts", "YouTube Video"]
post_platformlar = ["Instagram Post", "Facebook Post", "X (Twitter) Post"]

platform = st.selectbox("Platform", video_platformlar + post_platformlar)

saat = st.slider("Paylaşım Saati", 0, 23, 18)
konu = st.text_input("İçerik Konusu")
takipci = st.number_input("Takipçi Sayın", 0, 10000000, 1000)

# Süre sadece video ise
if platform in video_platformlar:
    sure = st.number_input("Video Süresi (sn)", 1, 1000, 60)
else:
    sure = None

# Hugging Face API
def hf_analiz(text):
    if not API_KEY:
        return "API key yok"

    try:
        response = requests.post(
            "https://api-inference.huggingface.co/models/google/flan-t5-large",
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={
                "inputs": f"""
                Bu içerik fikrini analiz et:

                {text}

                Viral skor, kısa yorum ve 5 hashtag ver.
                """
            }
        )
        data = response.json()
        return data[0]["generated_text"]
    except:
        return "AI çalışmadı"

# Basit analiz (fallback)
def basic_analiz(text):
    text = text.lower()
    if any(k in text for k in ["şok", "ifşa", "vs", "en iyi", "nasıl"]):
        return "Yüksek potansiyel içerik"
    return "Ortalama içerik"

# Tahmin
def tahmin(skor, takipci):
    like = int((takipci * 0.05) * (skor / 100))
    yorum = int(like * 0.1)
    yeni = int(like * 0.05)
    return like, yorum, yeni

# ANALİZ
if st.button("Analiz Et"):

    skor = 50

    if 18 <= saat <= 22:
        skor += 20
    elif 0 <= saat <= 6:
        skor -= 15

    if sure:
        if sure < 15:
            skor += 10
        elif sure > 60:
            skor -= 10

    if takipci > 10000:
        skor += 10

    skor = max(0, min(100, skor))

    ai = hf_analiz(konu)
    basic = basic_analiz(konu)

    like, yorum, yeni = tahmin(skor, takipci)

    st.subheader("Sonuç")
    st.write(f"Viral Skor: {skor}")
    st.write(f"Tahmini Beğeni: {like}")
    st.write(f"Tahmini Yorum: {yorum}")
    st.write(f"Tahmini Yeni Takipçi: {yeni}")

    st.write("Yorum:", basic)
    st.text(ai)