import streamlit as st
from openai import OpenAI
import os

# OpenAI
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

st.set_page_config(page_title="Viral Analiz", layout="centered")

st.title("Viral Analiz Aracı")

st.info("Bu araç içerik fikrini analiz eder, tahmini performans ve hashtag önerir. Giriş yapmak için sağ üstten kayıt sistemi eklenebilir (ileride geliştirilebilir).")

# Platformlar
video_platformlar = ["TikTok", "Instagram Reels", "YouTube Shorts", "YouTube Video"]
post_platformlar = ["Instagram Post", "Facebook Post", "X (Twitter) Post"]

platform = st.selectbox("Platform", video_platformlar + post_platformlar)

saat = st.slider("Paylaşım Saati", 0, 23, 18)
konu = st.text_input("Video / Post Konusu")

# Takipçi
takipci = st.number_input("Takipçi Sayın", 0, 10000000, 1000)

# Süre sadece video platformlarda
if platform in video_platformlar:
    sure = st.number_input("Video Süresi (sn)", 1, 1000, 60)
else:
    sure = None

# AI ANALİZ
def ai_analiz(text):
    try:
        response = client.responses.create(
            model="gpt-5-mini",
            input=f"""
            Bu içerik fikrini analiz et:
            {text}

            Viral skor, kısa yorum ve 5 hashtag ver.
            """
        )
        return response.output[0].content[0].text
    except:
        return "AI analiz kullanılamıyor (kredi yok olabilir)."

# Fallback analiz
def basic_analiz(text):
    text = text.lower()
    if any(k in text for k in ["şok", "ifşa", "vs", "en iyi", "nasıl"]):
        return "Yüksek potansiyel içerik."
    return "Ortalama içerik."

# Tahmin
def tahmin(skor, takipci):
    like = int((takipci * 0.05) * (skor / 100))
    yorum = int(like * 0.1)
    yeni_takipci = int(like * 0.05)
    return like, yorum, yeni_takipci

# ANALİZ
if st.button("Analiz Et"):

    skor = 50

    # Saat etkisi
    if 18 <= saat <= 22:
        skor += 20
    elif 0 <= saat <= 6:
        skor -= 15

    # Süre etkisi
    if sure:
        if sure < 15:
            skor += 10
        elif sure > 60:
            skor -= 10

    # Takipçi etkisi
    if takipci < 1000:
        skor -= 5
    elif takipci > 10000:
        skor += 10

    skor = max(0, min(100, skor))

    # AI + fallback
    ai_sonuc = ai_analiz(konu)
    basic = basic_analiz(konu)

    like, yorum, yeni = tahmin(skor, takipci)

    st.subheader("Sonuç")
    st.write(f"Viral Skor: {skor}")
    st.write(f"Tahmini Beğeni: {like}")
    st.write(f"Tahmini Yorum: {yorum}")
    st.write(f"Tahmini Yeni Takipçi: {yeni}")

    st.write("Yorum:", basic)
    st.text(ai_sonuc)