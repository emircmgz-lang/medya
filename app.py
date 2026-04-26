import streamlit as st
import os
import json
import re
import tempfile
import time

# 1. Sayfa Ayarları (Uygulamanın genişliğini biraz artırdık ki sekmeler rahat sığsın)
st.set_page_config(page_title="Viral Analiz & Profil Aracı", layout="centered", page_icon="🚀")

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
    model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"temperature": 0.4})

st.title("Sosyal Medya Yapay Zeka Asistanı 🚀")
st.info("İçeriklerini virale hazırla veya profilinin algoritma check-up'ını yap.")

# --- SEKMELERİ (TABS) OLUŞTURMA ---
tab1, tab2 = st.tabs(["🚀 İçerik & Video Analizi", "🔍 Profil & Marka Check-up"])

# ==============================================================================
# SEKME 1: İÇERİK VE VİDEO ANALİZİ
# ==============================================================================
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        video_platformlar = ["TikTok", "Instagram Reels", "YouTube Shorts", "YouTube Video"]
        post_platformlar = ["Instagram Post", "Facebook Post", "X (Twitter) Post"]
        platform = st.selectbox("Hedef Platform", video_platformlar + post_platformlar, key="plat1")
        takipci = st.number_input("Mevcut Takipçi Sayın", 0, 10000000, 1000, key="takipci1")
        
        # YENİ: Algoritmayı tetikleyen ögeler
        ses_turu = st.selectbox("Kullanılan Ses/Müzik", ["Trend/Popüler Ses", "Orijinal Ses", "Sadece Konuşma", "Müzik Yok"], help="Trend sesler algoritmanın seni keşfete çıkarma hızını etkiler.")

    with col2:
        saat = st.slider("Paylaşım Saati", 0, 23, 18, key="saat1")
        if platform in video_platformlar:
            sure = st.number_input("Video Süresi (sn)", 1, 1000, 60, key="sure1")
        else:
            sure = None
        
        # YENİ: Eylem Çağrısı
        cta = st.text_input("Eylem Çağrısı (CTA)", placeholder="Örn: Daha fazlası için takip et, Yorumlara yaz...", help="İzleyiciden ne yapmasını istiyorsun?")

    konu = st.text_area("İçerik Konusu / Açıklaması", placeholder="Örn: 30 günde nasıl İngilizce öğrendim? (Videonun metni veya fikri)", key="konu1")

    st.divider()
    st.subheader("🎥 Video Yükle (İsteğe Bağlı)")
    uploaded_video = st.file_uploader("Videonuzu yükleyerek yapay zekanın doğrudan görüntü, ses ve VİDEODAKİ KİŞİNİN ENERJİSİNİ analiz etmesini sağlayın.", type=["mp4", "mov", "avi"], key="vid1")

    # YAPAY ZEKA VİDEO/İÇERİK FONKSİYONU
    def ai_kapsamli_analiz(platform, saat, konu, takipci, sure, ses_turu, cta, video_file_path=None):
        sure_metni = f"{sure} saniye" if sure else "Görsel/Metin içeriği (Süre yok)"
        
        prompt = f"""
        Sen uzman bir sosyal medya algoritma analisti, vücut dili uzmanı ve içerik stratejistisin. 
        Eğer video eklendiyse BAŞTAN SONA İZLE. 
        1. TEKNİK: Işık, kurgu hızı, ilk 3 sn (hook), ses ve kurgu ritmi.
        2. ALGORİTMA TETİKLEYİCİLERİ: Kullanıcının seçtiği '{ses_turu}' ses türünün ve '{cta}' eylem çağrısının bu platformdaki etkisini skorlamaya dahil et.
        3. PSİKOLOJİ & VİBE: Videodaki kişiyi analiz et. Vücut dili, ses tonu, enerjisi, otoritesi ve "manifesting" (çekim yasası/ana karakter) enerjisi var mı? Varsa hashtaglere yansıt.
        
        [İÇERİK DETAYLARI]
        Platform: {platform}
        Mevcut Takipçi: {takipci}
        Paylaşım Saati: {saat}:00
        Format: {sure_metni}
        Ses Türü: {ses_turu}
        Eylem Çağrısı (CTA): {cta}
        İçerik Fikri/Metni: {konu}

        SADECE AŞAĞIDAKİ JSON FORMATINDA CEVAP VER:
        {{
            "skor": 85,
            "begeni": 1250,
            "yorum_sayisi": 120,
            "yeni_takipci": 45,
            "sure_tahmini": "24 - 48 Saat İçinde (Hızlı Viral) 🚀",
            "kisi_ve_vibe_analizi": "Kişinin ses tonu net. Manifesting ve ana karakter enerjisi var...",
            "ai_yorumu": "CTA çok zayıf, 'yorumlara yaz' yerine 'senin fikrin ne?' diye sor. Müzik seçimi iyi...",
            "hashtagler": "#trend #viral #manifest"
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
                if gemini_file.state.name == "FAILED":
                    raise Exception("Video işlenemedi.")
                request_contents = [gemini_file, prompt]

            response = model.generate_content(request_contents)
            match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            return None
        except Exception as e:
            st.error(f"Sistem Hatası: {str(e)}")
            return None
        finally:
            if gemini_file:
                try:
                    genai.delete_file(gemini_file.name)
                except:
                    pass

    if st.button("🚀 İçeriği Analiz Et", type="primary", use_container_width=True, key="btn1"):
        if not konu and not uploaded_video:
            st.warning("Lütfen ya bir içerik konusu yazın ya da bir video yükleyin!")
        else:
            with st.status("Yapay Zeka Çalışıyor...", expanded=True) as status:
                temp_path = None
                if uploaded_video:
                    st.write("📥 Video yükleniyor...")
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
                        tmp.write(uploaded_video.read())
                        temp_path = tmp.name
                    st.write("👀 Gemini videoyu ve enerjiyi analiz ediyor (15-30 sn)...")
                else:
                    st.write("🧠 İçerik fikri değerlendiriliyor...")
                    
                sonuclar = ai_kapsamli_analiz(platform, saat, konu, takipci, sure, ses_turu, cta, temp_path)
                
                if temp_path and os.path.exists(temp_path):
                    os.remove(temp_path)
                status.update(label="Analiz Tamamlandı!", state="complete", expanded=False)
                
            if sonuclar:
                st.success("İşte Yapay Zeka'nın Gözünden Videon!")
                st.info(f"⏳ **Ulaşım Süresi:** {sonuclar.get('sure_tahmini', '')}")

                col_a, col_b, col_c, col_d = st.columns(4)
                col_a.metric("Viral Skor", sonuclar.get('skor', 0))
                col_b.metric("Tahmini Beğeni", f"{sonuclar.get('begeni', 0):,}")
                col_c.metric("Tahmini Yorum", f"{sonuclar.get('yorum_sayisi', 0):,}")
                col_d.metric("Yeni Takipçi", f"{sonuclar.get('yeni_takipci', 0):,}")

                st.subheader("👤 Kişi ve Enerji (Vibe) Analizi")
                st.info(sonuclar.get('kisi_ve_vibe_analizi', ''))
                st.subheader("🤖 Stratejik Yorum")
                st.write(sonuclar.get('ai_yorumu', ''))
                st.caption(f"🎯 Önerilen Hashtagler: {sonuclar.get('hashtagler', '')}")

# ==============================================================================
# SEKME 2: PROFİL VE MARKA CHECK-UP
# ==============================================================================
with tab2:
    st.subheader("Hedef Kitle ve Profil Uyum Analizi")
    st.markdown("Profilinin mevcut durumunu analiz edelim ve kitleni nasıl büyüteceğini bulalım.")
    
    p_kullanici = st.text_input("Kullanıcı Adın / Hedef Kitlen (Örn: @yazilimci_kiz veya 'Yazılım Öğrenenler')")
    p_bio = st.text_area("Profil Biyografin (Şu an bio'nda ne yazıyor?)", placeholder="Örn: 💻 Kod yazıyorum ☕ Kahve aşığı | DM for collab")
    p_tema = st.text_input("Sayfanın Ana Teması", placeholder="Örn: Teknoloji, Mizah, Günlük Vlog, Motivasyon")
    p_videolar = st.text_area("En Çok İzlenen 3 Videonun Konusu (Kısaca)", placeholder="1- Ofiste ilk günüm\n2- Masa kurulumum\n3- Kullandığım klavye")

    def ai_profil_analizi(kullanici, bio, tema, videolar):
        prompt = f"""
        Sen üst düzey bir Sosyal Medya Marka Stratejisti ve Profil Doktorusun. Aşağıdaki profil detaylarını incele ve sayfanın kimlik analizini yap.
        
        [PROFİL BİLGİLERİ]
        Kullanıcı/Kitle: {kullanici}
        Biyografi: {bio}
        Ana Tema: {tema}
        En Çok İzlenen Videolar: {videolar}

        Biyografi yeterince dikkat çekici mi? Ana tema ile çok izlenen videolar arasında bir uyum veya kopukluk var mı? Kişi marka kimliğini nasıl iyileştirebilir?

        SADECE AŞAĞIDAKİ JSON FORMATINDA CEVAP VER:
        {{
            "profil_skoru": 75,
            "biyografi_elestirisi": "Bio çok klasik, sana özel bir 'değer teklifi' sunmuyor. Şunu yazmalısın...",
            "icerik_stratejisi": "En çok klavyen izlenmiş, demek ki kitle teknolojik ürün seviyor. Vlog yerine ürün incelemeye kaymalısın...",
            "acil_duzeltilecekler": "1. Bio'yu yenile. 2. Profil fotoğrafına renk kat."
        }}
        """
        try:
            response = model.generate_content(prompt)
            match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            return None
        except Exception as e:
            return None

    if st.button("🔍 Profili Check-Up Yap", type="primary", use_container_width=True, key="btn2"):
        if not p_bio or not p_tema:
            st.warning("Lütfen en azından Biyografi ve Ana Tema kısımlarını doldur!")
        else:
            with st.spinner("Marka Stratejisti profilini inceliyor..."):
                p_sonuc = ai_profil_analizi(p_kullanici, p_bio, p_tema, p_videolar)
            
            if p_sonuc:
                st.success("Profil Check-Up Tamamlandı!")
                
                # Profil skoru özel bir şekilde gösterilir
                st.metric("🌟 Profil Optimizasyon Skoru", f"% {p_sonuc.get('profil_skoru', 0)}")
                
                st.subheader("📝 Biyografi Analizi")
                st.info(p_sonuc.get('biyografi_elestirisi', ''))
                
                st.subheader("🗺️ İçerik ve Uyum Stratejisi")
                st.write(p_sonuc.get('icerik_stratejisi', ''))
                
                st.subheader("🚨 Acil Düzeltilmesi Gerekenler")
                st.error(p_sonuc.get('acil_duzeltilecekler', ''))