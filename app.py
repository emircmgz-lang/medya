import streamlit as st
import os
import json
import re
import tempfile
import time

# 1. Sayfa Ayarları
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
    model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"temperature": 0.5})

st.title("Yapay Zeka Sosyal Medya Ajansı")

tab_ana, tab1, tab2, tab3 = st.tabs([
    "Ana Sayfa", 
    "İçerik Analizi", 
    "Profil Check-up", 
    "Senaryo Üretici"
])

# ==============================================================================
# ANA SAYFA
# ==============================================================================
with tab_ana:
    st.subheader("Hoş Geldiniz! Sosyal Medyayı Birlikte Yönetelim.")
    st.markdown("""
    Bu platform, içerik üreticileri ve markalar için özel olarak tasarlanmış **Yapay Zeka Destekli bir Sosyal Medya Asistanıdır.** Arka planda çalışan güçlü algoritma sayesinde videolarınızı yayınlamadan önce test edebilir, marka kimliğinizi oturtabilir ve içerik fikirlerinizi senaryolaştırabilirsiniz.
    """)
    st.divider()
    c1, c2, c3 = st.columns(3)
    with c1:
        st.info("### İçerik Analizi\n\nVideonuzu veya içerik fikrinizi analiz edin. Tahmini viral skorunu, duygu radarını ve izleyiciyi kaybetme risk bölgelerini öğrenin.")
    with c2:
        st.success("### Profil Check-up\n\nHedef kitleniz sizi doğru anlıyor mu? Biyografinizi ve profil fotoğrafınızı taratarak marka kimliğinizi optimize edin.")
    with c3:
        st.warning("### Senaryo Üretici\n\nBoş sayfa sendromuna son! Konunuzu yazın, sistem size kancaları ve çekim senaryosunu saniye saniye hazırlasın.")
    st.divider()
    st.subheader("Proje Notları ve Hedefler")
    st.text_area("Sayfanın genel hedeflerini veya rakip analizlerini not alın:", placeholder="Örn: Bu ayki hedef 10K takipçi. Rakip sayfa: @ornek_sayfa...")

# ==============================================================================
# SEKME 1: İÇERİK VE VİDEO ANALİZİ
# ==============================================================================
with tab1:
    st.info("Videonuzu tüm algoritmik ve psikolojik detaylarıyla analiz edin.")
    col1, col2 = st.columns(2)
    with col1:
        video_platformlar = ["TikTok", "Instagram Reels", "YouTube Shorts", "YouTube Video"]
        post_platformlar = ["Instagram Post", "Facebook Post", "X (Twitter) Post"]
        platform = st.selectbox("Hedef Platform", video_platformlar + post_platformlar, key="plat1")
        sektorler = ["Eğitim / Bilgi", "Yazılım / Teknoloji", "Mizah / Eğlence", "Spor / Oyun", "Genel / Yaşam Tarzı", "Güzellik / Moda", "Finans / İş"]
        sektor = st.selectbox("Sektörünüz / Nişiniz", sektorler, key="sektor1")
        takipci = st.number_input("Mevcut Takipçi Sayınız", 0, 10000000, 1000, key="takipci1")
        ses_turu = st.selectbox("Kullanılan Ses/Müzik", ["Trend/Popüler Ses", "Orijinal Ses", "Sadece Konuşma", "Müzik Yok"], key="ses1")

    with col2:
        saat = st.slider("Paylaşım Saati", 0, 23, 18, key="saat1")
        if platform in video_platformlar:
            sure = st.number_input("Video Süresi (sn)", 1, 1000, 60, key="sure1")
        else:
            sure = None
        cta = st.text_input("Eylem Çağrısı (CTA)", placeholder="Örn: Daha fazlası için takip et...", key="cta1")
        hook = st.text_input("Videoya Giriş Cümleniz (Hook)", placeholder="Örn: Eğer her gün yorgun uyanıyorsanız...", key="hook1")

    konu = st.text_area("İçerik Konusu / Fikri", placeholder="Videonun ne hakkında olduğunu kısaca yazın...", key="konu1")

    st.divider()
    uploaded_video = st.file_uploader("Analiz için videonuzu yükleyin", type=["mp4", "mov", "avi"], key="vid1")

    def ai_kapsamli_analiz(platform, sektor, saat, konu, takipci, sure, ses_turu, cta, hook, video_file_path=None):
        sure_metni = f"{sure} saniye" if sure else "Görsel içeriği"
        prompt = f"""
        Analiz et: Platform: {platform}, Sektör: {sektor}, Takipçi: {takipci}, Saat: {saat}:00, Süre: {sure_metni}, Ses: {ses_turu}, CTA: {cta}, İlk Cümle: {hook}, Konu: {konu}.
        Eğer video varsa izle. Videodaki kişinin enerjisini analiz et. Metinlerde emoji kullanma.
        1. Duygu Radarı: İzleyicide uyandıracağı baskın duyguları ve paylaşıma etkisini yaz.
        2. Risk Bölgesi (Drop-off): İzleyicinin sıkılma riskini tespit et ve kurgu taktiği ver.
        3. Hook Eleştirisi: '{hook}' cümlesini eleştir ve daha güçlü alternatif sun.

        JSON formatında cevap ver:
        {{
            "skor": 85,
            "begeni": 1250,
            "yorum_sayisi": 120,
            "yeni_takipci": 45,
            "sure_tahmini": "24-48 Saat",
            "duygu_radari": "...",
            "risk_bolgesi": "...",
            "hook_elestirisi": "...",
            "kisi_ve_vibe_analizi": "...",
            "ai_yorumu": "...",
            "viral_aciklama": "...",
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

    if st.button("Laboratuvar Analizini Başlat", type="primary", use_container_width=True):
        if not konu and not uploaded_video:
            st.warning("Lütfen bir konu yazın veya video yükleyin!")
        else:
            with st.status("Yapay Zeka Derin Analiz Yapıyor...", expanded=True) as status:
                temp_path = None
                if uploaded_video:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
                        tmp.write(uploaded_video.read())
                        temp_path = tmp.name
                sonuclar = ai_kapsamli_analiz(platform, sektor, saat, konu, takipci, sure, ses_turu, cta, hook, temp_path)
                if temp_path and os.path.exists(temp_path):
                    os.remove(temp_path)
                status.update(label="Analiz Hazır!", state="complete", expanded=False)
                
            if sonuclar:
                st.success("Derinlemesine Analiz Tamamlandı!")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Viral Skor", sonuclar.get('skor', 0))
                c2.metric("Beğeni", f"{sonuclar.get('begeni', 0):,}")
                c3.metric("Yorum", f"{sonuclar.get('yorum_sayisi', 0):,}")
                c4.metric("Yeni Takipçi", f"{sonuclar.get('yeni_takipci', 0):,}")
                st.divider()
                st.subheader("Psikolojik ve Yapısal Analiz")
                st.info(f"Duygu Radarı: {sonuclar.get('duygu_radari', '')}")
                st.warning(f"Risk Bölgesi (İzleyici Kaybı): {sonuclar.get('risk_bolgesi', '')}")
                st.error(f"Kanca Eleştirisi: {sonuclar.get('hook_elestirisi', '')}")
                st.divider()
                st.subheader("Önerilen Açıklama ve Etiketler")
                st.code(sonuclar.get('viral_aciklama', ''), language=None)
                st.caption(f"Önerilen Hashtagler: {sonuclar.get('hashtagler', '')}")
                st.subheader("Enerji ve Algoritma Yorumu")
                st.write(sonuclar.get('kisi_ve_vibe_analizi', ''))
                st.write(sonuclar.get('ai_yorumu', ''))
                
                # --- RAPOR İNDİRME BÖLÜMÜ ---
                rapor_icerigi = f"""--- VİRAL İÇERİK ANALİZ RAPORU ---
Platform: {platform}
Sektör: {sektor}
Tahmini Skor: {sonuclar.get('skor', 0)}/100

-- PSİKOLOJİK ANALİZ --
Duygu Radarı: {sonuclar.get('duygu_radari', '')}
Risk Bölgesi: {sonuclar.get('risk_bolgesi', '')}
Kanca Eleştirisi: {sonuclar.get('hook_elestirisi', '')}

-- ALGORİTMA YORUMU --
{sonuclar.get('kisi_ve_vibe_analizi', '')}
{sonuclar.get('ai_yorumu', '')}

-- METİNLER --
Açıklama: {sonuclar.get('viral_aciklama', '')}
Hashtagler: {sonuclar.get('hashtagler', '')}
"""
                st.download_button(label="📄 Bu Raporu İndir (.txt)", data=rapor_icerigi, file_name="Viral_Analiz_Raporu.txt", mime="text/plain")

# ==============================================================================
# SEKME 2: PROFİL VE MARKA CHECK-UP
# ==============================================================================
with tab2:
    st.subheader("Profil ve Marka Kimliği Check-up")
    col_p1, col_p2 = st.columns([1, 1])
    
    with col_p1:
        p_bio = st.text_area("Profil Biyografiniz", placeholder="Bio metnini buraya yapıştırın...")
        p_tema = st.text_input("Ana Temanız", placeholder="Örn: Yaşam Tarzı, Teknoloji, Eğitim...")
        p_link = st.text_input("Bio Linkinizin Amacı (Dönüşüm)", placeholder="Örn: Sitemden ürün satmak, YouTube'a çekmek...")
        p_videolar = st.text_area("En Çok İzlenen 3 Videonun Konusu", placeholder="Sizi neyle tanıdılar?")
    
    with col_p2:
        st.write("**Görsel Analiz Yüklemeleri**")
        p_photo = st.file_uploader("1. Profil fotoğrafını yükleyin", type=["jpg", "png", "jpeg"])
        p_grid = st.file_uploader("2. Profil Akışı (Grid/Feed) Ekran Görüntüsü Yükleyin", type=["jpg", "png", "jpeg"])

    def ai_profil_analizi(bio, tema, videolar, link_amaci, photo_file=None, grid_file=None):
        prompt = f"""
        Bu profili üst düzey bir Marka Stratejisti olarak incele. Metinlerde emoji kullanma.
        Bio: {bio}, Tema: {tema}, En Çok İzlenenler: {videolar}, Link Dönüşüm Amacı: {link_amaci}.
        Sana profil fotoğrafı ve/veya profilin genel grid(akış) görüntüsü de verilmiş olabilir. Görsellerin marka kimliğiyle uyumunu, renk bütünlüğünü ve kapak fotoğraflarındaki okunabilirliği eleştir.
        Ayrıca bio metninin, kullanıcının '{link_amaci}' hedefine ulaşması için yeterli olup olmadığını analiz et.
        
        JSON formatında cevap ver:
        {{
            "profil_skoru": 75,
            "biyografi_analizi": "...",
            "donusum_ve_link_stratejisi": "İnsanları o linke tıklamaya ikna edecek bir Eylem Çağrısı (CTA) eksik...",
            "foto_yorumu": "...",
            "grid_ve_vitrin_analizi": "Kapak fotoğraflarındaki yazılar çok küçük/Karmaşık bir renk paleti var...",
            "marka_stratejisi": "...",
            "acil_duzeltmeler": "1. Şunu yapın, 2. Bunu yapın"
        }}
        """
        try:
            content = [prompt]
            if photo_file:
                content.append(Image.open(photo_file))
            if grid_file:
                content.append(Image.open(grid_file))
                
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
                res = ai_profil_analizi(p_bio, p_tema, p_videolar, p_link, p_photo, p_grid)
            if res:
                st.success("Profil Analizi Tamamlandı!")
                st.metric("Marka Uyum Skoru", f"% {res.get('profil_skoru', 0)}")
                
                c_sol, c_sag = st.columns(2)
                with c_sol:
                    st.subheader("Biyografi ve Kimlik")
                    st.write(res.get('biyografi_analizi', ''))
                    st.subheader("Dönüşüm ve Satış Hunisi")
                    st.info(res.get('donusum_ve_link_stratejisi', ''))
                with c_sag:
                    st.subheader("Profil Fotoğrafı")
                    st.write(res.get('foto_yorumu', 'Fotoğraf yüklenmedi.'))
                    st.subheader("Vitrin ve Akış (Grid) Analizi")
                    st.info(res.get('grid_ve_vitrin_analizi', 'Grid görüntüsü yüklenmedi.'))
                
                st.divider()
                st.subheader("Yol Haritası")
                st.write(res.get('marka_stratejisi', ''))
                st.subheader("Acil Eylem Planı")
                st.error(res.get('acil_duzeltmeler', ''))
                
                # --- RAPOR İNDİRME BÖLÜMÜ ---
                rapor_icerigi = f"""--- MARKA VE PROFIL CHECK-UP RAPORU ---
Tema: {p_tema}
Uyum Skoru: % {res.get('profil_skoru', 0)}

-- KİMLİK VE DÖNÜŞÜM --
Biyografi Analizi: {res.get('biyografi_analizi', '')}
Satış/Link Stratejisi: {res.get('donusum_ve_link_stratejisi', '')}

-- GÖRSEL VİTRİN --
Profil Fotoğrafı: {res.get('foto_yorumu', '')}
Grid/Akış Analizi: {res.get('grid_ve_vitrin_analizi', '')}

-- STRATEJİ --
Yol Haritası: {res.get('marka_stratejisi', '')}
Acil Düzeltmeler: {res.get('acil_duzeltmeler', '')}
"""
                st.download_button(label="📄 Bu Raporu İndir (.txt)", data=rapor_icerigi, file_name="Marka_Checkup_Raporu.txt", mime="text/plain")

# ==============================================================================
# SEKME 3: KANCA (HOOK) VE SENARYO ÜRETİCİSİ
# ==============================================================================
with tab3:
    st.subheader("Senaryonuzu Oluşturun")
    st.markdown("Videonun konusunu yazın, yapay zeka size saniye saniye çekim senaryosu hazırlasın.")
    
    s_konu = st.text_input("Videonun Ana Konusu", placeholder="Örn: Evde spor yapmanın faydaları...")
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        s_ton = st.selectbox("Videonun Duygusu / Tonu", ["Gizemli", "Enerjik", "Otoriter", "Samimi", "Şok Edici"])
    with col_s2:
        s_hedef = st.text_input("Hedef Kitle", placeholder="Örn: Yeni başlayanlar, İş insanları...")

    def ai_senaryo_yazici(konu, ton, hedef):
        prompt = f"""
        Sen viral içerikler üreten bir Metin Yazarı ve Yönetmensin. Metinlerde emoji kullanma.
        Konu: {konu}, Ton: {ton}, Hedef Kitle: {hedef}.
        3 farklı kanca üret ve bir video çekim senaryosu hazırla.
        JSON formatında cevap ver:
        {{
            "kancalar": [
                {{"tip": "Merak Kancası", "cumle": "..."}},
                {{"tip": "Negatif Kanca", "cumle": "..."}},
                {{"tip": "Hedef Odaklı", "cumle": "..."}}
            ],
            "senaryo": [
                {{"saniye": "0-3 sn", "gorsel": "...", "ses": "..."}},
                {{"saniye": "3-10 sn", "gorsel": "...", "ses": "..."}}
            ],
            "yonetmen_tavsiyesi": "..."
        }}
        """
        try:
            response = model.generate_content([prompt])
            match = re.search(r'\{.*\}', response.text, re.DOTALL)
            return json.loads(match.group(0)) if match else None
        except Exception as e:
            return None

    if st.button("Kanca ve Senaryo Üret", type="primary", use_container_width=True):
        if not s_konu:
            st.warning("Lütfen videonun konusunu yazın!")
        else:
            with st.spinner("Yönetmen Senaryonuzu Yazıyor..."):
                senaryo_sonuc = ai_senaryo_yazici(s_konu, s_ton, s_hedef)
            if senaryo_sonuc:
                st.success("Senaryo Çekime Hazır!")
                st.subheader("İlk 3 Saniye Kancaları")
                k1, k2, k3 = st.columns(3)
                kancalar = senaryo_sonuc.get("kancalar", [])
                
                kanca_metni = "" # Rapor için kancaları toplayacağız
                if len(kancalar) == 3:
                    k1.info(f"**{kancalar[0]['tip']}**\n\n{kancalar[0]['cumle']}")
                    k2.success(f"**{kancalar[1]['tip']}**\n\n{kancalar[1]['cumle']}")
                    k3.warning(f"**{kancalar[2]['tip']}**\n\n{kancalar[2]['cumle']}")
                    kanca_metni = f"1. {kancalar[0]['tip']}: {kancalar[0]['cumle']}\n2. {kancalar[1]['tip']}: {kancalar[1]['cumle']}\n3. {kancalar[2]['tip']}: {kancalar[2]['cumle']}"
                
                st.divider()
                st.subheader("Saniye Saniye Çekim Planı")
                
                senaryo_metni = "" # Rapor için senaryoyu toplayacağız
                for adim in senaryo_sonuc.get("senaryo", []):
                    with st.expander(f"{adim['saniye']}", expanded=True):
                        st.markdown(f"**Ekranda Ne Görünecek:** {adim['gorsel']}")
                        st.markdown(f"**Dış Ses / Konuşma:** {adim['ses']}")
                    senaryo_metni += f"[{adim['saniye']}]\nGörsel: {adim['gorsel']}\nSes: {adim['ses']}\n\n"
                        
                st.subheader("Yönetmenin Notu")
                st.error(senaryo_sonuc.get("yonetmen_tavsiyesi", ""))
                
                # --- RAPOR İNDİRME BÖLÜMÜ ---
                rapor_icerigi = f"""--- VİDEO ÇEKİM SENARYOSU ---
Konu: {s_konu}
Ton: {s_ton}
Hedef Kitle: {s_hedef}

-- KANCALAR (HOOKS) --
{kanca_metni}

-- ÇEKİM PLANI --
{senaryo_metni}
-- YÖNETMENİN NOTU --
{senaryo_sonuc.get("yonetmen_tavsiyesi", "")}
"""
                st.download_button(label="📄 Bu Senaryoyu İndir (.txt)", data=rapor_icerigi, file_name="Video_Senaryosu.txt", mime="text/plain")