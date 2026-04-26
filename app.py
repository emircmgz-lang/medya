import streamlit as st
import requests
import os

st.set_page_config(page_title="Viral Analiz", layout="centered")

st.title("Viral Analiz Aracı")

st.info("İçerik fikrini analiz eder, AI destekli yorum + tahmini performans verir.")

# Platformlar
video_platformlar = ["TikTok", "Instagram Reels", "YouTube Shorts", "YouTube Video"]
post_platformlar = ["Instagram Post", "Facebook Post", "X (Twitter) Post"]

platform = st.selectbox("Platform", video_platformlar + post_platformlar)
saat = st.slider("Paylaşım Saati", 0, 23, 18)
konu = st.text_input("İçerik Konusu")
takipci = st.number_input("Takipçi Sayın", 0, 10000000, 1000)

# Süre sadece video platformlarda
if platform in video_platformlar:
    sure = st.number_input("Video Süresi (sn)", 1, 1000, 60)
else:
    sure = None

# GEMINI API (HTTP)
def ai_analiz(text):
    try:
        API_KEY = os.environ.get("GEMINI_API_KEY")

        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": f"""
Bu içerik fikrini analiz et:

{text}

Şu formatta cevap ver:
Viral Skor: (0-100)
İzlenme Potansiyeli: (0-100)
Kısa Yorum:
Hashtagler: #...
"""
                        }
                    ]
                }
            ]
        }

        response = requests.post(url, json=payload)

        if response.status_code != 200:
            return f"AI Hata: {response.status_code} - {response.text}"

        data = response.json()

        return data["candidates"][0]["content"]["parts"][0]["text"]

    except Exception as e:
        return f"AI Exception: {str(e)}"

# Fallback analiz
def basic_analiz(text):
    text = text.lower()
    if any(k in text for k in ["şok", "ifşa", "vs", "en iyi", "nasıl", "trend", "challenge"]):
        return "Yüksek potansiyel içerik"
    return "Ortalama içerik"

# Skor hesaplama
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
    elif takipci < 1000:
        skor -= 5

    return max(0, min(100, skor))

# Tahmin
def tahmin(skor, takipci):
    like = int((takipci * 0.05) * (skor / 100))
    yorum = int(like * 0.1)
    yeni = int(like * 0.05)
    return like, yorum, yeni

# ANALİZ
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