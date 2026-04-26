import streamlit as st

st.set_page_config(page_title="Viral Analiz", layout="centered")

st.title("Viral Analiz Aracı")

st.info("İçerik fikrini analiz eder, tahmini performans ve hashtag önerir. Giriş sistemi yakında eklenecek.")

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

# AKILLI ANALİZ
def analiz_et(text, saat, sure, takipci):

    skor = 50

    text = text.lower()

    # 🔥 viral kelimeler
    viral_kelimeler = [
        "şok", "ifşa", "vs", "en iyi", "en kötü",
        "nasıl", "denedim", "challenge", "trend",
        "bedava", "hızlı", "inanılmaz", "gizli"
    ]

    if any(k in text for k in viral_kelimeler):
        skor += 15

    # saat
    if 18 <= saat <= 22:
        skor += 20
    elif 0 <= saat <= 6:
        skor -= 15

    # süre
    if sure:
        if sure < 15:
            skor += 10
        elif sure > 60:
            skor -= 10

    # takipçi etkisi
    if takipci < 1000:
        skor -= 5
    elif takipci > 10000:
        skor += 10

    skor = max(0, min(100, skor))

    return skor

# HASHTAG
def hashtag_uret(text):
    words = text.lower().split()

    base_tags = ["#keşfet", "#viral", "#trend"]

    extra = []
    for w in words:
        if len(w) > 3:
            extra.append("#" + w)

    return " ".join(base_tags + extra[:5])

# TAHMİN
def tahmin(skor, takipci):
    like = int((takipci * 0.05) * (skor / 100))
    yorum = int(like * 0.1)
    yeni = int(like * 0.05)
    return like, yorum, yeni

# YORUM
def yorumla(skor):
    if skor >= 75:
        return "Yüksek viral potansiyel"
    elif skor >= 50:
        return "Ortalama performans beklenir"
    else:
        return "Düşük performans, içerik geliştirilmeli"

# ANALİZ BUTONU
if st.button("Analiz Et"):

    skor = analiz_et(konu, saat, sure, takipci)
    like, yorum, yeni = tahmin(skor, takipci)
    tags = hashtag_uret(konu)
    yorum_text = yorumla(skor)

    st.subheader("Sonuç")

    st.write(f"Viral Skor: {skor}")
    st.write(f"Tahmini Beğeni: {like}")
    st.write(f"Tahmini Yorum: {yorum}")
    st.write(f"Tahmini Yeni Takipçi: {yeni}")

    st.write("Yorum:", yorum_text)
    st.write("Hashtagler:", tags)