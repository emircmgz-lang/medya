import streamlit as st
import google.generativeai as genai
import os

# API
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-pro")

st.set_page_config(page_title="Viral Analiz", layout="centered")

st.title("Viral Analiz Aracı")

st.info("İçerik fikrini analiz eder, AI + tahmini performans verir.")

# Platformlar
video_platformlar = ["TikTok", "Instagram Reels", "YouTube Shorts", "YouTube Video"]
post_platformlar = ["Instagram Post", "Facebook Post", "X (Twitter) Post"]

platform = st.selectbox("Platform", video_platformlar + post_platformlar)
saat = st.slider("Paylaşım Saati", 0, 23, 18)
konu = st.text_input("İçerik Konusu")
takipci = st.number_input("Takipçi Sayın", 0, 10000000, 1000)

# Süre
if platform in video_platformlar:
    sure = st.number_input("Video Süresi (sn)", 1, 1000, 60)
else:
    sure = None

# AI ANALİZ (GEMINI)
def ai_analiz(text):
    try:
        prompt = f"""
        Bu içerik fikrini analiz et:

        {text}

        Şu formatta cevap ver:

        Viral Skor: (0-100)
        İzlenme Potansiyeli: (0-100)
        Kısa Yorum:
        Hashtagler: #...
        """

        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        return f"AI hata: {str(e)}"

# FALLBACK (AI çalışmazsa)
def basic_analiz(text):
    text = text.lower()
    if any(k in text for k in ["şok", "ifşa", "vs", "en iyi", "nasıl"]):
        return "Yüksek potansiyel içerik"
    return "Ortalama içerik"

# SKOR
def skor_hesapla(text, saat, sure, takipci):
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

    return max(0, min(100, skor))

# TAHMİN
def tahmin(skor, takipci):
    like = int((takipci * 0.05) * (skor / 100))
    yorum = int(like * 0.1)
    yeni = int(like * 0.05)
    return like, yorum, yeni

# BUTON
if st.button("Analiz Et"):

    skor = skor_hesapla(konu, saat, sure, takipci)
    like, yorum, yeni = tahmin(skor, takipci)

    ai = ai_analiz(konu)
    basic = basic_analiz(konu)

    st.subheader("Sonuç")

    st.write(f"Viral Skor: {skor}")
    st.write(f"Tahmini Beğeni: {like}")
    st.write(f"Tahmini Yorum: {yorum}")
    st.write(f"Tahmini Yeni Takipçi: {yeni}")

    st.write("Fallback Yorum:", basic)
    st.text(ai)