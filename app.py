import streamlit as st
import os

# 1. Sayfa Ayarları
st.set_page_config(page_title="Viral Analiz", layout="centered", page_icon="🚀")

# 2. Kütüphane Yükleme Kontrolü
try:
    import google.generativeai as genai
except ModuleNotFoundError:
    st.error("🚨 HATA: 'google-generativeai' kütüphanesi bulunamadı! requirements.txt dosyanızı kontrol edin.")
    st.stop()

# 3. API Anahtarı Kontrolü
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except (KeyError, FileNotFoundError):
    API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    st.error("🚨 HATA: API Anahtarı bulunamadı! Lütfen Streamlit Cloud Secrets bölümüne eklediğinizden emin olun.")
    st.stop()
else:
    # API'yi yapılandır (GÜNCEL MODEL)
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')

# -------------------------------------------------------------------
# KULLANICI ARAYÜZÜ VE MANTIK
# -------------------------------------------------------------------

st.title("Viral Analiz Aracı 🚀")
st.info("İçerik fikrini analiz eder, AI destekli yorum + tahmini performans ve süre verir.")

# Platformlar
video_platformlar = ["TikTok", "Instagram Reels", "YouTube Shorts", "YouTube Video"]
post_platformlar = ["Instagram Post", "Facebook Post", "X (Twitter) Post"]

platform = st.selectbox("Platform", video_platformlar + post_platformlar)
saat = st.slider("Paylaşım Saati", 0, 23, 18)
konu = st.text_input("İçerik Konusu")
takipci = st.number_input("Takipçi Sayın", 0, 10000000, 1000)

if platform in video_platformlar:
    sure = st.number_input("Video Süresi (sn)", 1, 1000, 60)
else:
    sure = None

# GEMINI API Fonksiyonu
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
        return f"AI Exception: {str(e)}"

def basic_analiz(text):
    text = text.lower()
    if any(k in text for k in ["şok", "ifşa", "vs", "en iyi", "nasıl", "trend", "challenge"]):
        return "Yüksek potansiyel içerik"
    return "Ortalama içerik"

# Skor hesaplama algoritması
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

# Tahmin algoritması
def tahmin(skor, takipci):
    like = int((takipci * 0.05) * (skor / 100))
    yorum = int(like * 0.1)
    yeni = int(like * 0.05)
    return like, yorum, yeni

# YENİ: Süre Tahmini Algoritması
def zaman_tahmini(skor):
    if skor >= 85:
        return "24 - 48 Saat İçinde (Hızlı Viral) 🚀"
    elif skor >= 70:
        return "3 - 5 Gün İçinde (Güçlü Yükseliş) 📈"
    elif skor >= 50:
        return "1 - 2 Hafta İçinde (Organik Büyüme) 🌱"
    else:
        return "1 Ay ve Üzeri (Uzun Vadeli/Yavaş) 🐢"

# --- ANALİZ BUTONU VE SONUÇ EKRANI ---
if st.button("Analiz Et", type="primary"):
    
    if not konu:
        st.warning("Lütfen analiz etmek için bir içerik konusu girin!")
    else:
        with st.spinner("Yapay Zeka İçeriği Analiz Ediyor..."):
            # Hesaplamalar
            skor = skor_hesapla(konu, saat, sure, takipci)
            like, yorum, yeni = tahmin(skor, takipci)
            hedef_sure = zaman_tahmini(skor) # Zamanı hesapla
            
            ai = ai_analiz(konu)
            basic = basic_analiz(konu)

        st.success("Analiz Tamamlandı!")
        st.divider()

        # Süre tahminini en üste dikkat çekici şekilde koyalım
        st.info(f"⏳ **Tahmini Rakamlara Ulaşma Süresi:** {hedef_sure}")

        st.subheader("📊 Sayısal Tahminler")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric(label="Algoritma Skoru", value=skor)
        col2.metric(label="Beğeni", value=like)
        col3.metric(label="Yorum", value=yorum)
        col4.metric(label="Yeni Takipçi", value=yeni)

        st.subheader("🤖 Gemini Yapay Zeka Yorumu")
        st.write(ai) # st.info yerine düz yazı daha temiz durabilir uzun metinlerde

        st.caption(f"Sistem Fallback Yorumu: {basic}")