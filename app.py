import streamlit as st
import os
import json
import re
import tempfile
import time

# 1. Sayfa Ayarları
st.set_page_config(page_title="Viral Analiz & Marka Koçu", layout="centered", page_icon="🚀")

# 2. Kütüphane Yükleme Kontrolü
try:
    import google.generativeai as genai
    from PIL import Image
except ModuleNotFoundError:
    st.error("🚨 HATA: Gerekli kütüphaneler bulunamadı! requirements.txt dosyanızı kontrol edin.")
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
    # Model 1.5-flash olarak ayarlandı ve boşluklar düzeltildi
    model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"temperature": 0.4})

st.title("Yapay Zeka Sosyal Medya Ajansı 🚀")

# --- SEKMELER ---
tab1, tab2 = st.tabs(["🚀 İçerik & Video Analizi", "🔍 Profil & Marka Check-up"])

# ==============================================================================
# SEKME 1: İÇERİK VE VİDEO ANALİZİ
# ==============================================================================
with tab1:
    st.info("Videonuzu analiz edin, viral skorunuzu öğrenin ve AI tarafından hazırlanan açıklamayı alın.")
    col1, col2 = st.columns(2)
    with col1:
        video_platformlar = ["TikTok", "Instagram Reels", "YouTube Shorts", "YouTube Video"]
        post_platformlar = ["Instagram Post", "Facebook Post", "X (Twitter) Post"]
        platform = st.selectbox("Hedef Platform", video_platformlar + post_platformlar, key="plat1")
        takipci = st.number_input("Mevcut Takipçi Sayın", 0, 10000000, 1000, key="takipci1")
        ses_turu = st.selectbox("Kullanılan Ses/Müzik", ["Trend/Popüler Ses", "Orijinal Ses", "Sadece Konuşma", "Müzik Yok"], key="ses1")

    with col2:
        saat = st.slider("Paylaşım Saati", 0, 23, 18, key="saat1")
        if platform in video_platformlar:
            sure = st.number_input("Video Süresi (sn)", 1, 1000, 60, key="sure1")
        else:
            sure = None
        cta = st.text_input("Eylem Çağrısı (CTA)", placeholder="Örn: Daha fazlası için takip et...", key="cta1")

    konu = st.text_area("İçerik Konusu / Fikri", placeholder="Videonun ne hakkında olduğunu kısaca yazın...", key="konu1")

    st.divider()
    uploaded_video = st.file_uploader("Analiz için videonuzu yükleyin (Görüntü + Ses + Enerji Analizi)", type=["mp4", "mov", "avi"], key="vid1")

    def ai_kapsamli_analiz(platform, saat, konu, takipci, sure, ses_turu, cta, video_file_path=None):
        sure_metni = f"{sure} saniye" if sure else "Görsel içeriği"
        prompt = f"""
        Analiz et:
        Platform: {platform}, Takipçi: {takipci}, Saat: {saat}:00, Süre: {sure_metni}, Ses: {ses_turu}, CTA: {cta}, Konu: {konu}.
        Eğer video varsa izle; kurgu, hook, enerji ve vibe analiz et.
        Özellikle videodaki kişinin enerjisi manifest/motivasyon gibi alt metinler içeriyor mu bak.
        Ayrıca bu içerik için viral olma potansiyeli yüksek, emojili, kancası güçlü bir AÇIKLAMA (Caption) oluştur.

        JSON formatında cevap ver:
        {{
            "skor": 85,
            "begeni": 1250,
            "yorum_sayisi": 120,
            "yeni_takipci": 45,
            "sure_tahmini": "24-48 Saat",
            "kisi_ve_vibe_analizi": "...",
            "ai_yorumu": "...",
            "viral_aciklama": "🚀 VİRAL AÇIKLAMA BURAYA GELECEK...",
            "hashtagler": "#trend #viral"
        }}
        """
        gemini_file = None
        try:
            request_contents = [prompt]
            if video_file_path:
                gemini_file = genai.upload_file(path=video_file_path)
                while gemini_file.state.name == "PROCESSING":
                    time.sleep(2)
                    gemini_file = genai.get_file(gemini_file.name)
                request_contents = [gemini_file, prompt]
            response = model.generate_content(request_contents)
            match = re.search(r'\{.*\}', response.text, re.DOTALL)
            return json.loads(match.group(0)) if match else None
        except Exception as e:
            st.error(f"Hata: {str(e)}")
            return None
        finally:
            if gemini_file:
                genai.delete_file(gemini_file.name)

    if st.button("🚀 Videoyu Analiz Et ve Açıklama Yaz", type="primary", use_container_width=True):
        if not konu and not uploaded_video:
            st.warning("Lütfen bir konu yazın veya video yükleyin!")
        else:
            with st.status("Yapay Zeka Videonu İzliyor...", expanded=True) as status:
                temp_path = None
                if uploaded_video:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
                        tmp.write(uploaded_video.read())
                        temp_path = tmp.name
                sonuclar = ai_kapsamli_analiz(platform, saat, konu, takipci, sure, ses_turu, cta, temp_path)
                if temp_path and os.path.exists(temp_path):
                    os.remove(temp_path)
                status.update(label="Analiz Hazır!", state="complete", expanded=False)
                
            if sonuclar:
                st.success("Analiz ve Açıklama Oluşturuldu!")
                
                st.subheader("✍️ Önerilen Viral Açıklama")
                st.code(sonuclar.get('viral_aciklama', ''), language=None)
                st.caption(f"Önerilen Hashtagler: {sonuclar.get('hashtagler', '')}")

                st.divider()
                st.info(f"⏳ **Ulaşım Süresi:** {sonuclar.get('sure_tahmini', '')}")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Viral Skor", sonuclar.get('skor', 0))
                c2.metric("Beğeni", f"{sonuclar.get('begeni', 0):,}")
                c3.metric("Yorum", f"{sonuclar.get('yorum_sayisi', 0):,}")
                c4.metric("Yeni Takipçi", f"{sonuclar.get('yeni_takipci', 0):,}")

                st.subheader("👤 Enerji ve Vibe Analizi")
                st.write(sonuclar.get('kisi_ve_vibe_analizi', ''))
                st.subheader("🤖 Algoritma Yorumu")
                st.write(sonuclar.get('ai_yorumu', ''))

# ==============================================================================
# SEKME 2: PROFİL VE MARKA CHECK-UP
# ==============================================================================
with tab2:
    st.subheader("Profil ve Marka Kimliği Check-up")
    col_p1, col_p2 = st.columns([1, 1])
    
    with col_p1:
        p_bio = st.text_area("Profil Biyografin", placeholder="Bio metnini buraya yapıştır...")
        p_tema = st.text_input("Ana Teman", placeholder="Örn: Yaşam Tarzı, Teknoloji...")
    
    with col_p2:
        st.write("🖼️ **Profil Fotoğrafı Analizi**")
        p_photo = st.file_uploader("Profil fotoğrafını yükle (Vibe ve Profesyonellik Analizi)", type=["jpg", "png", "jpeg"])

    p_videolar = st.text_area("En Çok İzlenen 3 Videonun Konusu", placeholder="Seni neyle tanıdılar?")

    def ai_profil_analizi(bio, tema, videolar, photo_file=None):
        prompt = f"""
        Bu profili bir Marka Stratejisti olarak incele:
        Bio: {bio}, Tema: {tema}, En Çok İzlenenler: {videolar}.
        Eğer profil fotoğrafı varsa; ışık, kompozisyon ve yaydığı enerjinin (vibe) marka temasıyla uyumunu analiz et.
        
        JSON formatında cevap ver:
        {{
            "profil_skoru": 75,
            "biyografi_analizi": "...",
            "foto_yorumu": "Profil fotoğrafın çok karanlık/profesyonel/samimi...",
            "marka_stratejisi": "...",
            "acil_duzeltmeler": "1. Şunu yap, 2. Bunu yap"
        }}
        """
        try:
            content = [prompt]
            if photo_file:
                img = Image.open(photo_file)
                content = [img, prompt]
            response = model.generate_content(content)
            match = re.search(r'\{.*\}', response.text, re.DOTALL)
            return json.loads(match.group(0)) if match else None
        except Exception as e:
            return None

    if st.button("🔍 Marka Analizini Başlat", type="primary", use_container_width=True):
        if not p_bio or not p_tema:
            st.warning("Lütfen bio ve tema alanlarını doldurun!")
        else:
            with st.spinner("Yapay Zeka Profilini İnceliyor..."):
                res = ai_profil_analizi(p_bio, p_tema, p_videolar, p_photo)
            if res:
                st.success("Profil Analizi Tamamlandı!")
                st.metric("🌟 Marka Uyum Skoru", f"% {res.get('profil_skoru', 0)}")
                
                st.subheader("🖼️ Profil Fotoğrafı ve Vibe")
                st.info(res.get('foto_yorumu', 'Fotoğraf yüklenmedi.'))
                
                st.subheader("📝 Biyografi ve Kimlik")
                st.write(res.get('biyografi_analizi', ''))
                
                st.subheader("🗺️ Yol Haritası")
                st.write(res.get('marka_stratejisi', ''))
                
                st.subheader("🚨 Acil Eylem Planı")
                st.error(res.get('acil_duzeltmeler', ''))