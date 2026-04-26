import streamlit as st
import os
import json
import re
import tempfile
import time

# 1. Sayfa Ayarları
st.set_page_config(page_title="Viral Analiz Aracı", layout="centered", page_icon="🚀")

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
    # Model ayarı
    model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"temperature": 0.4})

# -------------------------------------------------------------------
# KULLANICI ARAYÜZÜ
# -------------------------------------------------------------------

st.title("Viral Analiz Aracı 🚀")
st.info("İçerik fikrini yazın veya doğrudan videonuzu yükleyin! Yapay Zeka videoyu izleyip algoritma ve enerji analizi yapsın.")

# Platform ve Metrikler
col1, col2 = st.columns(2)
with col1:
    video_platformlar = ["TikTok", "Instagram Reels", "YouTube Shorts", "YouTube Video"]
    post_platformlar = ["Instagram Post", "Facebook Post", "X (Twitter) Post"]
    platform = st.selectbox("Hedef Platform", video_platformlar + post_platformlar)
    takipci = st.number_input("Mevcut Takipçi Sayın", 0, 10000000, 1000)

with col2:
    saat = st.slider("Paylaşım Saati", 0, 23, 18)
    if platform in video_platformlar:
        sure = st.number_input("Video Süresi (sn)", 1, 1000, 60)
    else:
        sure = None

konu = st.text_area("İçerik Konusu / Açıklaması", placeholder="Örn: 30 günde nasıl İngilizce öğrendim? (Videonun metni veya fikri)")

# Video Yükleme Alanı
st.divider()
st.subheader("🎥 Video Yükle (İsteğe Bağlı)")
uploaded_video = st.file_uploader("Videonuzu yükleyerek yapay zekanın doğrudan görüntü, ses ve VİDEODAKİ KİŞİNİN ENERJİSİNİ analiz etmesini sağlayın.", type=["mp4", "mov", "avi"])

# YAPAY ZEKA TAM KAPSAMLI ANALİZ FONKSİYONU (GİRİNTİLER DÜZELTİLDİ)
def ai_kapsamli_analiz(platform, saat, konu, takipci, sure, video_file_path=None):
    sure_metni = f"{sure} saniye" if sure else "Görsel/Metin içeriği (Süre yok)"
    
    prompt = f"""
    Sen uzman bir sosyal medya algoritma analisti, vücut dili uzmanı ve içerik stratejistisin. 
    Eğer bu isteğe bir video eklendiyse, videoyu BAŞTAN SONA İZLE. 
    1. TEKNİK: Işık, kurgu hızı, ilk 3 saniye (hook), ses kalitesi ve kurgu ritmini analiz et.
    2. PSİKOLOJİK VE KİŞİ ANALİZİ: Videodaki kişiyi (veya dış sesi) derinlemesine analiz et. Vücut dili, ses tonu, mimikleri, enerjisi ve izleyiciye geçirdiği "vibe" (aura) nedir? Özgüvenli mi, samimi mi, otoriter mi yoksa bir şeyleri "manifest" mi ediyor? 
    Kullanıcı açıklamaya belirli kelimeleri (örneğin manifest, motivasyon vb.) yazmasa bile, videonun alt metninde ve kişinin enerjisinde bu varsa BUNU TESPİT ET ve analizine/hashtaglerine yansıt.
    
    [İÇERİK DETAYLARI]
    Platform: {platform}
    Mevcut Takipçi: {takipci}
    Paylaşım Saati: {saat}:00
    Format/Süre: {sure_metni}
    İçerik Fikri/Açıklaması: {konu}

    Lütfen analiz sonucunu AŞAĞIDAKİ GİBİ TAM BİR JSON FORMATINDA döndür. JSON dışında hiçbir metin yazma.

    {{
        "skor": 85,
        "begeni": 1250,
        "yorum_sayisi": 120,
        "yeni_takipci": 45,
        "sure_tahmini": "24 - 48 Saat İçinde (Hızlı Viral) 🚀",
        "kisi_ve_vibe_analizi": "Videodaki kişinin ses tonu çok net ve göz teması mükemmel. Açıklamada belirtilmese bile net bir 'manifesting' ve 'ana karakter' (main character) enerjisi yayıyor...",
        "ai_yorumu": "İlk 3 saniyelik hook çok güçlü. Teknik olarak şu kısımları hızlandırırsan kitleyi daha iyi tutarsın...",
        "hashtagler": "#trend #viral #manifest #ozguven"
    }}
    """
    
    gemini_file = None
    try:
        request_contents = [prompt]

        # Video varsa sisteme yükleyip işlenmesini bekle
        if video_file_path:
            gemini_file = genai.upload_file(path=video_file_path)
            
            while gemini_file.state.name == "PROCESSING":
                time.sleep(2)
                gemini_file = genai.get_file(gemini_file.name)
                
            if gemini_file.state.name == "FAILED":
                raise Exception("Yapay zeka videoyu işleyemedi.")
                
            request_contents = [gemini_file, prompt]

        # Modele gönder ve yanıtı al
        response = model.generate_content(request_contents)
        raw_text = response.text
        
        # Sadece JSON kısmını ayıkla
        match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        else:
            return None
            
    except Exception as e:
        st.error(f"Sistem Hatası: {str(e)}")
        return None
        
    finally:
        # Hata olsa da olmasa da videoyu Google'dan sil
        if gemini_file:
            try:
                genai.delete_file(gemini_file.name)
            except:
                pass

# --- ANALİZ BUTONU VE SONUÇ EKRANI ---
if st.button("🚀 İçeriği Analiz Et", type="primary", use_container_width=True):
    
    if not konu and not uploaded_video:
        st.warning("Lütfen ya bir içerik konusu yazın ya da bir video yükleyin!")
    else:
        with st.status("Yapay Zeka Çalışıyor...", expanded=True) as status:
            temp_path = None
            
            # Video eklendiyse geçici olarak kaydet
            if uploaded_video:
                st.write("📥 Video sisteme yükleniyor...")
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
                    tmp.write(uploaded_video.read())
                    temp_path = tmp.name
                st.write("👀 Gemini videoyu izliyor ve enerjiyi analiz ediyor (Bu işlem 15-30 sn sürebilir)...")
            else:
                st.write("🧠 İçerik fikri algoritmalara göre değerlendiriliyor...")
                
            # Analiz fonksiyonunu çağır
            sonuclar = ai_kapsamli_analiz(platform, saat, konu, takipci, sure, temp_path)
            
            # İşlem bitince bilgisayardaki geçici dosyayı temizle
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
                
            status.update(label="Analiz Tamamlandı!", state="complete", expanded=False)
            
        # Sonuçları ekrana yansıt
        if sonuclar:
            st.success("İşte Yapay Zeka'nın Gözünden Videon/İçeriğin!")
            
            st.info(f"⏳ **Platforma Göre Tahmini Ulaşım Süresi:** {sonuclar.get('sure_tahmini', 'Bilinmiyor')}")

            col1, col2, col3, col4 = st.columns(4)
            col1.metric(label="Viral Skor", value=sonuclar.get('skor', 0))
            col2.metric(label="Tahmini Beğeni", value=f"{sonuclar.get('begeni', 0):,}")
            col3.metric(label="Tahmini Yorum", value=f"{sonuclar.get('yorum_sayisi', 0):,}")
            col4.metric(label="Yeni Takipçi", value=f"{sonuclar.get('yeni_takipci', 0):,}")

            st.subheader("👤 Kişi ve Enerji (Vibe) Analizi")
            st.info(sonuclar.get('kisi_ve_vibe_analizi', 'Kişi veya enerji analizi yapılamadı.'))

            st.subheader("🤖 Teknik ve Stratejik Yorum")
            st.write(sonuclar.get('ai_yorumu', 'Yorum alınamadı.'))
            
            st.caption(f"🎯 Önerilen Hashtagler: {sonuclar.get('hashtagler', '')}")