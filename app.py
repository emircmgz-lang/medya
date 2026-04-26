import streamlit as st
import os
import json
import re

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
    st.error("🚨 HATA: API Anahtarı bulunamadı!")
    st.stop()
else:
    genai.configure(api_key=API_KEY)
    # Daha tutarlı JSON çıktıları için sıcaklığı (temperature) biraz düşürüyoruz
    model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"temperature": 0.4})

# -------------------------------------------------------------------
# KULLANICI ARAYÜZÜ
# -------------------------------------------------------------------

st.title("Viral Analiz Aracı 🚀")
st.info("Tüm metrikler ve süre tahminleri platformun algoritmasına göre Yapay Zeka tarafından özel hesaplanır.")

# Platformlar
video_platformlar = ["TikTok", "Instagram Reels", "YouTube Shorts", "YouTube Video"]
post_platformlar = ["Instagram Post", "Facebook Post", "X (Twitter) Post"]

platform = st.selectbox("Platform", video_platformlar + post_platformlar)
saat = st.slider("Paylaşım Saati", 0, 23, 18)
konu = st.text_area("İçerik Konusu", placeholder="Örn: 30 günde nasıl İngilizce öğrendim? (Şok edici taktikler)")
takipci = st.number_input("Mevcut Takipçi Sayın", 0, 10000000, 1000)

if platform in video_platformlar:
    sure = st.number_input("Video Süresi (sn)", 1, 1000, 60)
else:
    sure = None

# YAPAY ZEKA TAM KAPSAMLI ANALİZ FONKSİYONU
def ai_kapsamli_analiz(platform, saat, konu, takipci, sure):
    sure_metni = f"{sure} saniye" if sure else "Görsel/Metin içeriği (Süre yok)"
    
    prompt = f"""
    Sen uzman bir sosyal medya algoritma analistisin. Aşağıdaki içerik detaylarını incele ve platformun kendi dinamiklerine (algoritmasına) göre gerçekçi tahminler yap.
    
    [İÇERİK DETAYLARI]
    Platform: {platform}
    Mevcut Takipçi: {takipci}
    Paylaşım Saati: {saat}:00
    Format/Süre: {sure_metni}
    İçerik Konusu: {konu}

    Lütfen analiz sonucunu AŞAĞIDAKİ GİBİ TAM BİR JSON FORMATINDA döndür. JSON dışında hiçbir başlangıç veya bitiş cümlesi yazma.

    {{
        "skor": 85,
        "begeni": 1250,
        "yorum_sayisi": 120,
        "yeni_takipci": 45,
        "sure_tahmini": "24 - 48 Saat İçinde (Hızlı Viral) 🚀",
        "ai_yorumu": "Buraya içeriğin neden tutacağı veya tutmayacağı ile ilgili stratejik analizini yaz...",
        "hashtagler": "#trend #viral"
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        raw_text = response.text
        
        # Yapay zekanın döndürdüğü metnin içinden sadece JSON kısmını ayıklıyoruz
        match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        if match:
            json_str = match.group(0)
            data = json.loads(json_str)
            return data
        else:
            return None
    except Exception as e:
        return None

# --- ANALİZ BUTONU VE SONUÇ EKRANI ---
if st.button("Analiz Et", type="primary"):
    
    if not konu:
        st.warning("Lütfen analiz etmek için bir içerik konusu girin!")
    else:
        with st.spinner(f"Yapay Zeka {platform} algoritmasını analiz ediyor..."):
            sonuclar = ai_kapsamli_analiz(platform, saat, konu, takipci, sure)
            
        if sonuclar:
            st.success("Yapay Zeka Analizi Tamamlandı!")
            st.divider()

            # AI'den gelen süre tahmini
            st.info(f"⏳ **Platforma Göre Tahmini Ulaşım Süresi:** {sonuclar.get('sure_tahmini', 'Bilinmiyor')}")

            st.subheader("📊 Algoritma Tahminleri")
            col1, col2, col3, col4 = st.columns(4)
            # Sayıları formatlayarak (örn: 1500 -> 1,500) daha şık gösteriyoruz
            col1.metric(label="Viral Skor", value=sonuclar.get('skor', 0))
            col2.metric(label="Tahmini Beğeni", value=f"{sonuclar.get('begeni', 0):,}")
            col3.metric(label="Tahmini Yorum", value=f"{sonuclar.get('yorum_sayisi', 0):,}")
            col4.metric(label="Yeni Takipçi", value=f"{sonuclar.get('yeni_takipci', 0):,}")

            st.subheader("🤖 Stratejik Yapay Zeka Yorumu")
            st.write(sonuclar.get('ai_yorumu', 'Yorum alınamadı.'))
            
            st.caption(f"Önerilen Hashtagler: {sonuclar.get('hashtagler', '')}")
            
        else:
            st.error("Yapay zeka yanıtı işlenirken bir hata oluştu. Lütfen tekrar deneyin.")