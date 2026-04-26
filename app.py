import streamlit as st
from openai import OpenAI
import os

# OpenAI client
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

st.set_page_config(page_title="Viral Analiz", layout="centered")

st.title("Viral Analiz Aracı")

# Kullanıcı inputları
platform = st.selectbox("Platform", ["TikTok", "Instagram Reels", "YouTube Shorts", "YouTube Video"])
saat = st.slider("Paylaşım Saati", 0, 23, 18)
konu = st.text_input("Video Konusu")
sure = st.number_input("Video Süresi (sn)", 1, 1000, 60)

# AI analiz fonksiyonu
def ai_analiz(text):
    try:
        response = client.responses.create(
            model="gpt-5-mini",
            input=f"""
            Aşağıdaki video fikrini analiz et:

            {text}

            Şu formatta cevap ver:

            Viral Skor: (0-100)
            İzlenme Potansiyeli: (0-100)
            Kısa Yorum:

            Hashtagler:
            #hashtag1 #hashtag2 #hashtag3 #hashtag4 #hashtag5
            """
        )
        return response.output[0].content[0].text
    except Exception as e:
        return f"Hata: {str(e)}"

# Tahmini metrik
def tahmin_hesapla(skor):
    like = skor * 10
    yorum = skor * 2
    takipci = skor * 1.5
    return int(like), int(yorum), int(takipci)

# Buton
if st.button("Analiz Et"):

    skor = 50

    # Saat etkisi
    if 18 <= saat <= 22:
        skor += 20
    elif 0 <= saat <= 6:
        skor -= 15

    # Süre etkisi
    if sure < 15:
        skor += 10
    elif sure > 60:
        skor -= 10

    skor = max(0, min(100, skor))

    # AI sonucu
    ai_sonuc = ai_analiz(konu)

    # Tahmini metrik
    like, yorum, takipci = tahmin_hesapla(skor)

    # Ekran çıktısı
    st.subheader("Sonuç")
    st.write(f"Viral Skor: {skor}")
    st.write(f"Tahmini Beğeni: {like}")
    st.write(f"Tahmini Yorum: {yorum}")
    st.write(f"Tahmini Takipçi: {takipci}")

    st.text(ai_sonuc)