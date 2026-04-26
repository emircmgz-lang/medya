import streamlit as st
import os
import json
import re
import tempfile
import time

# 1. Sayfa Ayarları (Emojiler kaldırıldı)
st.set_page_config(page_title="AI Sosyal Medya Ajansı", layout="centered")

# 2. Kütüphane Yükleme Kontrolü
try:
    import google.generativeai as genai
    from PIL import Image
except ModuleNotFoundError:
    st.error("HATA: Gerekli kütüphaneler bulunamadı! requirements.txt dosyanızı kontrol edin.")
    st.stop()

# 3. API Anahtarı Kontrolü
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except (KeyError, FileNotFoundError):
    API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    st.error("HATA: API Anahtarı bulunamadı!")
    st.stop()
else:
    genai.configure(api_key=API_KEY)
    # Hızlı ve güncel modelimiz devrede
    model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"temperature": 0.5})

# --- UYGULAMA BAŞLIĞI ---
st.title("Yapay Zeka Sosyal Medya Ajansı")

# --- 4 SEKME ---
tab_ana, tab1, tab2, tab3 = st.tabs([
    "Ana Sayfa", 
    "İçerik Analizi", 
    "Profil Check-up", 
    "Senaryo Üretici"
])

# ==============================================================================
# ANA SAYFA (KARŞILAMA EKRANI VE VİTRİN)
# ==============================================================================
with tab_ana:
    st.subheader("Hoş Geldiniz! Sosyal Medyayı Birlikte Yönetelim.")
    st.markdown("""
    Bu platform, içerik üreticileri ve markalar için özel olarak tasarlanmış **Yapay Zeka Destekli bir Sosyal Medya Asistanıdır.** Arka planda çalışan güçlü algoritma sayesinde videolarınızı yayınlamadan önce test edebilir, marka kimliğinizi oturtabilir ve içerik fikirlerinizi senaryolaştırabilirsiniz.
    """)
    
    st.divider()
    
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.info("### İçerik Analizi\n\nVideonuzu veya içerik fikrinizi yapay zekaya izletin. Size saniyeler içinde tahmini viral skorunu, beğeni sayılarını ve en iyi hashtagleri versin.")
        
    with c2:
        st.success("### Profil Check-up\n\nHedef kitleniz sizi doğru anlıyor mu? Biyografinizi ve profil fotoğrafınızı taratarak marka kimliğinizi optimize edin.")
        
    with c3:
        st.warning("### Senaryo Üretici\n\nBoş sayfa sendromuna son! Konunuzu yazın, sistem size ilk 3 saniye kancalarını (hook) ve çekim senaryosunu saniye saniye hazırlasın.")
        
    st.divider()
    
    st.subheader("Proje Notları ve Hedefler")
    st.text_area("Bu alana sayfanın genel hedeflerini, rakip sayfaların isimlerini veya genel 'Ana Temanızı' not alabilirsiniz:", 
                 placeholder="Örn: Bu ayki hedef 10K takipçi. Rakip sayfa: @ornek_sayfa. Ana renklerim: Siyah ve Sarı...")

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
        takipci = st.number_input("Mevcut Takipçi Sayınız", 0, 10000000, 1000, key="takipci1")
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
        Ayrıca bu içerik için viral olma potansiyeli yüksek, etkileyici ve kancası güçlü bir AÇIKLAMA (Caption) oluştur. Emojileri minimumda tut veya hiç kullanma.

        JSON formatında cevap ver:
        {{
            "skor": 85,
            "begeni": 1250,
            "yorum_sayisi": 120,
            "yeni_takipci": 45,
            "sure_tahmini": "24-48 Saat",
            "kisi_ve_vibe_analizi": "...",
            "ai_yorumu": "...",
            "viral_aciklama": "VİRAL AÇIKLAMA BURAYA GELECEK...",
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

    if st.button("Videoyu Analiz Et ve Açıklama Yaz", type="primary", use_container_width=True):
        if not konu and not uploaded_video:
            st.warning("Lütfen bir konu yazın veya video yükleyin!")
        else:
            with st.status("Yapay Zeka Videonuzu İzliyor...", expanded=True) as status:
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
                
                st.subheader("Önerilen Viral Açıklama")
                st.code(sonuclar.get('viral_aciklama', ''), language=None)
                st.caption(f"Önerilen Hashtagler: {sonuclar.get('hashtagler', '')}")

                st.divider()
                st.info(f"**Ulaşım Süresi:** {sonuclar.get('sure_tahmini', '')}")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Viral Skor", sonuclar.get('skor', 0))
                c2.metric("Beğeni", f"{sonuclar.get('begeni', 0):,}")
                c3.metric("Yorum", f"{sonuclar.get('yorum_sayisi', 0):,}")
                c4.metric("Yeni Takipçi", f"{sonuclar.get('yeni_takipci', 0):,}")

                st.subheader("Enerji ve Vibe Analizi")
                st.write(sonuclar.get('kisi_ve_vibe_analizi', ''))
                st.subheader("Algoritma Yorumu")
                st.write(sonuclar.get('ai_yorumu', ''))

# ==============================================================================
# SEKME 2: PROFİL VE MARKA CHECK-UP
# ==============================================================================
with tab2:
    st.subheader("Profil ve Marka Kimliği Check-up")
    col_p1, col_p2 = st.columns([1, 1])
    
    with col_p1:
        p_bio = st.text_area("Profil Biyografiniz", placeholder="Bio metnini buraya yapıştırın...")
        p_tema = st.text_input("Ana Temanız", placeholder="Örn: Yaşam Tarzı, Teknoloji...")
    
    with col_p2:
        st.write("**Profil Fotoğrafı Analizi**")
        p_photo = st.file_uploader("Profil fotoğrafını yükleyin (Vibe ve Profesyonellik Analizi)", type=["jpg", "png", "jpeg"])

    p_videolar = st.text_area("En Çok İzlenen 3 Videonun Konusu", placeholder="Sizi neyle tanıdılar?")

    def ai_profil_analizi(bio, tema, videolar, photo_file=None):
        prompt = f"""
        Bu profili bir Marka Stratejisti olarak incele:
        Bio: {bio}, Tema: {tema}, En Çok İzlenenler: {videolar}.
        Eğer profil fotoğrafı varsa; ışık, kompozisyon ve yaydığı enerjinin (vibe) marka temasıyla uyumunu analiz et.
        
        JSON formatında cevap ver:
        {{
            "profil_skoru": 75,
            "biyografi_analizi": "...",
            "foto_yorumu": "Profil fotoğrafınız profesyonel/samimi...",
            "marka_stratejisi": "...",
            "acil_duzeltmeler": "1. Şunu yapın, 2. Bunu yapın"
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

    if st.button("Marka Analizini Başlat", type="primary", use_container_width=True):
        if not p_bio or not p_tema:
            st.warning("Lütfen bio ve tema alanlarını doldurun!")
        else:
            with st.spinner("Yapay Zeka Profilinizi İnceliyor..."):
                res = ai_profil_analizi(p_bio, p_tema, p_videolar, p_photo)
            if res:
                st.success("Profil Analizi Tamamlandı!")
                st.metric("Marka Uyum Skoru", f"% {res.get('profil_skoru', 0)}")
                
                st.subheader("Profil Fotoğrafı ve Vibe")
                st.info(res.get('foto_yorumu', 'Fotoğraf yüklenmedi.'))
                
                st.subheader("Biyografi ve Kimlik")
                st.write(res.get('biyografi_analizi', ''))
                
                st.subheader("Yol Haritası")
                st.write(res.get('marka_stratejisi', ''))
                
                st.subheader("Acil Eylem Planı")
                st.error(res.get('acil_duzeltmeler', ''))

# ==============================================================================
# SEKME 3: KANCA (HOOK) VE SENARYO ÜRETİCİSİ
# ==============================================================================
with tab3:
    st.subheader("Boş Sayfa Sendromuna Son: Senaryonuzu Oluşturun")
    st.markdown("Videonun konusunu yazın, yapay zeka size en iyi kancaları ve saniye saniye çekim senaryosunu versin.")
    
    s_konu = st.text_input("Videonun Ana Konusu", placeholder="Örn: Evde spor yapmanın faydaları, Kodlama öğrenme taktikleri...")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        s_ton = st.selectbox("Videonun Duygusu / Tonu", ["Gizemli & Merak Uyandırıcı", "Enerjik & Eğlenceli", "Otoriter & Bilgi Verici", "Samimi & Vlog Tarzı", "Şok Edici / İfşa"])
    with col_s2:
        s_hedef = st.text_input("Hedef Kitle (Kime hitap ediyorsunuz?)", placeholder="Örn: Yeni başlayanlar, İş insanları, Öğrenciler...")

    def ai_senaryo_yazici(konu, ton, hedef):
        prompt = f"""
        Sen TikTok, Reels ve Shorts için viral içerikler üreten usta bir Metin Yazarı ve Yönetmensin.
        Konu: {konu}
        Ton: {ton}
        Hedef Kitle: {hedef}
        
        Bana bu kitleyi ilk 3 saniyede yakalayacak 3 farklı 'Kanca (Hook)' üret ve seçtiğin en iyi kanca üzerinden saniye saniye bir video çekim senaryosu hazırla. Metinlerde emoji kullanma.
        
        SADECE JSON FORMATINDA CEVAP VER:
        {{
            "kancalar": [
                {{"tip": "Merak Kancası", "cumle": "Kimsenin bilmediği X sırrı..."}},
                {{"tip": "Negatif Kanca", "cumle": "Eğer Y yapıyorsan her şeyi yanlış yapıyorsun!"}},
                {{"tip": "Hedef Odaklı", "cumle": "Z olmak isteyenler bu videoyu kaydetsin."}}
            ],
            "senaryo": [
                {{"saniye": "0-3 sn", "gorsel": "Kameraya çok yakın çekim, şaşkın yüz ifadesi.", "ses": "İlk kanca cümlesi okunur."}},
                {{"saniye": "3-10 sn", "gorsel": "Arka planda ürün/konu gösterilir.", "ses": "Sorunun tespiti yapılır..."}},
                {{"saniye": "10-25 sn", "gorsel": "Ekrana maddeler gelir.", "ses": "Çözüm anlatılır..."}},
                {{"saniye": "25-30 sn", "gorsel": "Kamerayı işaret et.", "ses": "Daha fazlası için takip et!"}}
            ],
            "yonetmen_tavsiyesi": "Videoyu çok hızlı kesmelerle kurgula, sessiz boşluk bırakma."
        }}
        """
        try:
            response = model.generate_content([prompt])
            match = re.search(r'\{.*\}', response.text, re.DOTALL)
            return json.loads(match.group(0)) if match else None
        except Exception as e:
            st.error(f"Hata: {str(e)}")
            return None

    if st.button("Kanca ve Senaryo Üret", type="primary", use_container_width=True):
        if not s_konu:
            st.warning("Lütfen videonun konusunu yazın!")
        else:
            with st.spinner("Yönetmen Senaryonuzu Yazıyor..."):
                senaryo_sonuc = ai_senaryo_yazici(s_konu, s_ton, s_hedef)
                
            if senaryo_sonuc:
                st.success("Senaryo Çekime Hazır!")
                
                st.subheader("İlk 3 Saniye Kancaları (Bunlardan birini seçin)")
                k1, k2, k3 = st.columns(3)
                kancalar = senaryo_sonuc.get("kancalar", [])
                if len(kancalar) == 3:
                    k1.info(f"**{kancalar[0]['tip']}**\n\n{kancalar[0]['cumle']}")
                    k2.success(f"**{kancalar[1]['tip']}**\n\n{kancalar[1]['cumle']}")
                    k3.warning(f"**{kancalar[2]['tip']}**\n\n{kancalar[2]['cumle']}")
                
                st.divider()
                
                st.subheader("Saniye Saniye Çekim Planı")
                senaryo_adimlari = senaryo_sonuc.get("senaryo", [])
                for adim in senaryo_adimlari:
                    with st.expander(f"{adim['saniye']}", expanded=True):
                        st.markdown(f"**Ekranda Ne Görünecek:** {adim['gorsel']}")
                        st.markdown(f"**Dış Ses / Konuşma:** {adim['ses']}")
                
                st.subheader("Yönetmenin Notu")
                st.error(senaryo_sonuc.get("yonetmen_tavsiyesi", ""))