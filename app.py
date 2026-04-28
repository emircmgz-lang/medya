import streamlit as st
import os
import json
import re
import tempfile
import time

# 1. Sayfa Ayarları
st.set_page_config(page_title="AI Sosyal Medya Ajansı", layout="wide")

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

# --- 6 SEKME (Ana Sayfa + 5 Araç) ---
tab_ana, tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Ana Sayfa", 
    "İçerik Analizi", 
    "Profil Check-up", 
    "Senaryo Üretici",
    "Kriz Yönetimi",
    "İçerik Çoğaltıcı"
])

# ==============================================================================
# ANA SAYFA
# ==============================================================================
with tab_ana:
    st.subheader("Hoş Geldiniz! Sosyal Medyayı Birlikte Yönetelim.")
    st.markdown("""
    Bu platform, içerik üreticileri ve markalar için özel olarak tasarlanmış **Yapay Zeka Destekli bir Sosyal Medya Asistanıdır.** Arka planda çalışan güçlü algoritma sayesinde videolarınızı yayınlamadan önce test edebilir, marka kimliğinizi oturtabilir, kriz anlarını yönetebilir ve tek bir fikri tüm platformlar için çoğaltabilirsiniz.
    """)
    st.divider()
    
    # 5 Özelliği şık kolonlarla tanıtıyoruz (Üstte 3, altta 2)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.info("**İçerik Analizi**\nVideonuzun viral skorunu ve risk bölgelerini öğrenin.")
    with c2:
        st.success("**Profil Check-up**\nBio ve Grid (Akış) analiziyle marka kimliğinizi optimize edin.")
    with c3:
        st.warning("**Senaryo Üretici**\nBoş sayfa sendromuna son! Saniye saniye çekim planı hazırlayın.")
        
    c4, c5 = st.columns(2)
    with c4:
        st.error("**Kriz Yönetimi**\nZorlu yorumlara ve linç girişimlerine karşı zekice cevaplar üretin.")
    with c5:
        st.info("**İçerik Çoğaltıcı**\nTek bir fikri Twitter, Insta ve TikTok için anında 3'e katlayın.")
        
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
                
                kanca_metni = "" 
                if len(kancalar) == 3:
                    k1.info(f"**{kancalar[0]['tip']}**\n\n{kancalar[0]['cumle']}")
                    k2.success(f"**{kancalar[1]['tip']}**\n\n{kancalar[1]['cumle']}")
                    k3.warning(f"**{kancalar[2]['tip']}**\n\n{kancalar[2]['cumle']}")
                    kanca_metni = f"1. {kancalar[0]['tip']}: {kancalar[0]['cumle']}\n2. {kancalar[1]['tip']}: {kancalar[1]['cumle']}\n3. {kancalar[2]['tip']}: {kancalar[2]['cumle']}"
                
                st.divider()
                st.subheader("Saniye Saniye Çekim Planı")
                
                senaryo_metni = "" 
                for adim in senaryo_sonuc.get("senaryo", []):
                    with st.expander(f"{adim['saniye']}", expanded=True):
                        st.markdown(f"**Ekranda Ne Görünecek:** {adim['gorsel']}")
                        st.markdown(f"**Dış Ses / Konuşma:** {adim['ses']}")
                    senaryo_metni += f"[{adim['saniye']}]\nGörsel: {adim['gorsel']}\nSes: {adim['ses']}\n\n"
                        
                st.subheader("Yönetmenin Notu")
                st.error(senaryo_sonuc.get("yonetmen_tavsiyesi", ""))
                
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

# ==============================================================================
# SEKME 4: KRİZ VE TOPLULUK YÖNETİCİSİ
# ==============================================================================
with tab4:
    st.subheader("Kriz ve Topluluk Yöneticisi")
    st.markdown("Videonuzun altına gelen sert, linç edici veya zorlayıcı yorumları buraya yapıştırın. Yapay zeka markanızın tonuna uygun stratejik cevaplar üretsin.")
    
    k_yorum = st.text_area("Gelen Zorlu/Linç Edici Yorum", placeholder="Örn: Bu ürününüz tamamen para tuzağı, asla çalışmıyor!")
    k_ton = st.selectbox("Cevap Verirken Markanızın Tonu Nasıl Olmalı?", ["Profesyonel ve Kurumsal (Güven Verici)", "Mizahi ve Esprili (Buz Kırıcı)", "Açıklayıcı ve Samimi (Eğitici)", "Etkileşim Odaklı (Soru ile Karşılık Veren)"])

    def ai_kriz_yonetimi(yorum, ton):
        prompt = f"""
        Sen üst düzey bir Kriz İletişimi ve Topluluk Yöneticisisin. Metinlerde emoji kullanma.
        Gelen Yorum: "{yorum}"
        İstenen Marka Tonu: "{ton}"
        
        Bu yorumun markaya verebileceği zararı analiz et ve belirtilen tona ağırlık vererek 3 farklı cevap stratejisi oluştur. Amacımız linci durdurmak, durumu lehimize çevirmek veya etkileşimi artırmak.
        
        JSON formatında cevap ver:
        {{
            "risk_seviyesi": "Yüksek (Linç Potansiyeli) / Orta / Düşük",
            "yorum_analizi": "Kullanıcı hayal kırıklığı yaşıyor ve güvensizlik duyuyor...",
            "cevap_1": {{"strateji": "Mizahi/Buz Kırıcı", "metin": "..."}},
            "cevap_2": {{"strateji": "Kurumsal/Güven Verici", "metin": "..."}},
            "cevap_3": {{"strateji": "Soru Sorarak Etkileşim Artırma", "metin": "..."}}
        }}
        """
        try:
            response = model.generate_content([prompt])
            match = re.search(r'\{.*\}', response.text, re.DOTALL)
            return json.loads(match.group(0)) if match else None
        except Exception as e:
            return None

    if st.button("Kriz Yanıtı Üret", type="primary", use_container_width=True):
        if not k_yorum:
            st.warning("Lütfen analiz edilecek yorumu yapıştırın!")
        else:
            with st.spinner("Kriz Masası Toplanıyor..."):
                kriz_sonuc = ai_kriz_yonetimi(k_yorum, k_ton)
            if kriz_sonuc:
                st.success("Kriz Stratejisi Hazır!")
                
                st.error(f"**Risk Seviyesi:** {kriz_sonuc.get('risk_seviyesi', '')}")
                st.write(f"**Yorumun Psikolojik Analizi:** {kriz_sonuc.get('yorum_analizi', '')}")
                st.divider()
                
                st.subheader("Stratejik Cevap Seçenekleri")
                c1, c2, c3 = kriz_sonuc.get('cevap_1', {}), kriz_sonuc.get('cevap_2', {}), kriz_sonuc.get('cevap_3', {})
                
                st.info(f"**Strateji 1 ({c1.get('strateji', '')}):**\n\n{c1.get('metin', '')}")
                st.success(f"**Strateji 2 ({c2.get('strateji', '')}):**\n\n{c2.get('metin', '')}")
                st.warning(f"**Strateji 3 ({c3.get('strateji', '')}):**\n\n{c3.get('metin', '')}")
                
                rapor_icerigi = f"""--- KRİZ YÖNETİMİ VE TOPLULUK RAPORU ---
Gelen Yorum: {k_yorum}
Seçilen Ton: {k_ton}

-- DURUM ANALİZİ --
Risk Seviyesi: {kriz_sonuc.get('risk_seviyesi', '')}
Psikolojik Analiz: {kriz_sonuc.get('yorum_analizi', '')}

-- YANIT SEÇENEKLERİ --
1. {c1.get('strateji', '')}: {c1.get('metin', '')}
2. {c2.get('strateji', '')}: {c2.get('metin', '')}
3. {c3.get('strateji', '')}: {c3.get('metin', '')}
"""
                st.download_button(label="📄 Bu Kriz Raporunu İndir (.txt)", data=rapor_icerigi, file_name="Kriz_Yonetim_Raporu.txt", mime="text/plain")

# ==============================================================================
# SEKME 5: İÇERİK ÇOĞALTICI (ZAMAN MAKİNESİ) (YENİ)
# ==============================================================================
with tab5:
    st.subheader("İçerik Çoğaltıcı (Zaman Makinesi)")
    st.markdown("Uzun uzun düşündüğünüz tek bir fikri buraya yazın. Yapay zeka bu fikri X (Twitter), Instagram ve TikTok için en uygun formata dönüştürerek sizi 3 kat fazla iş yükünden kurtarsın.")
    
    cogalt_fikir = st.text_area("Ana Fikriniz / Anlatmak İstediğiniz Konu", placeholder="Örn: Yapay zekanın eğitime etkileri hakkında uzun bir yazı...", height=150)
    
    def ai_icerik_cogalt(fikir):
        prompt = f"""
        Sen bir dijital pazarlama uzmanısın. Metinlerde emoji kullanma.
        Aşağıdaki ana fikri al ve 3 farklı platformun dinamiğine göre yeniden yaz.
        Ana Fikir: "{fikir}"
        
        İstenen Formatlar:
        1. X (Twitter) Flood: Bilgi veren, teknik, madde madde giden 3 tweetlik bir zincir.
        2. Instagram Carousel (Kaydırmalı Post): Her slaytta ne yazacağını belirten 3-4 slaytlık bir metin.
        3. TikTok / Shorts: Enerjik, 30 saniyelik bir kısa video senaryosu.
        
        JSON formatında cevap ver:
        {{
            "twitter_flood": "Tweet 1: ...\n\nTweet 2: ...\n\nTweet 3: ...",
            "instagram_carousel": "Slayt 1 (Kapak): ...\nSlayt 2: ...\nSlayt 3: ...",
            "tiktok_senaryo": "0-3 sn (Kanca): ...\n3-15 sn: ...\n15-30 sn: ..."
        }}
        """
        try:
            response = model.generate_content([prompt])
            match = re.search(r'\{.*\}', response.text, re.DOTALL)
            return json.loads(match.group(0)) if match else None
        except Exception as e:
            return None

    if st.button("Fikri 3 Platform İçin Çoğalt", type="primary", use_container_width=True):
        if not cogalt_fikir:
            st.warning("Lütfen çoğaltılacak ana fikri girin!")
        else:
            with st.spinner("İçerik Çoğaltıcı Çalışıyor..."):
                cogalt_sonuc = ai_icerik_cogalt(cogalt_fikir)
            
            if cogalt_sonuc:
                st.success("İçeriğiniz 3 farklı platform için başarıyla dönüştürüldü!")
                
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.info("**X (Twitter) Flood**")
                    st.write(cogalt_sonuc.get("twitter_flood", ""))
                with c2:
                    st.success("**Instagram Carousel**")
                    st.write(cogalt_sonuc.get("instagram_carousel", ""))
                with c3:
                    st.warning("**TikTok / Shorts**")
                    st.write(cogalt_sonuc.get("tiktok_senaryo", ""))
                
                rapor_icerigi = f"""--- İÇERİK ÇOĞALTICI RAPORU ---
Ana Fikir: {cogalt_fikir}

-- X (TWITTER) FLOOD --
{cogalt_sonuc.get("twitter_flood", "")}

-- INSTAGRAM CAROUSEL --
{cogalt_sonuc.get("instagram_carousel", "")}

-- TIKTOK / SHORTS SENARYOSU --
{cogalt_sonuc.get("tiktok_senaryo", "")}
"""
                st.download_button(label="📄 Bu Çoklu İçerik Raporunu İndir (.txt)", data=rapor_icerigi, file_name="Coklu_Icerik_Raporu.txt", mime="text/plain")