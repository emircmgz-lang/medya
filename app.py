import streamlit as st
import os
import json
import re
import tempfile
import time
import math
import pandas as pd
import numpy as np

# ==============================================================================
# 1. SAYFA AYARLARI VE KÜTÜPHANE KONTROLÜ
# ==============================================================================
st.set_page_config(page_title="AI & Data Science Ajansı", layout="wide")

try:
    import google.generativeai as genai
    from PIL import Image
except ModuleNotFoundError:
    st.error("HATA: Kütüphaneler eksik! Lütfen terminale: pip install google-generativeai pandas numpy pillow yazın.")
    st.stop()

# ==============================================================================
# 2. API ANAHTARI YAPILANDIRMASI
# ==============================================================================
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

st.title("Yapay Zeka ve Veri Bilimi Ajansı(made by emircmgz)")

# ==============================================================================
# 3. MEGA SEKMELER
# ==============================================================================
tab_ana, tab_analiz, tab_profil, tab_senaryo, tab_kriz, tab_cogalt, tab_matematik = st.tabs([
    "Ana Sayfa", 
    "İçerik Analizi", 
    "Profil Check-up", 
    "Senaryo Üretici",
    "Kriz Yönetimi",
    "İçerik Çoğaltıcı",
    "Veri Bilimi Laboratuvarı"
])

# ==============================================================================
# SEKME 0: ANA SAYFA
# ==============================================================================
with tab_ana:
    st.subheader("İki Dünyanın Birleşimi: Yaratıcılık ve Matematik")
    st.markdown("""
    Bu platform, içerik üretiminin **kreatif süreçlerini (Yapay Zeka)** ve büyümenin **matematiksel gerçeklerini (Veri Bilimi)** tek bir ekranda birleştirir.
    Sol taraftaki sekmelerle markanızı ve içeriklerinizi tasarlarken, en sağdaki laboratuvar ile istatistiksel olasılıklarınızı hesaplayın.
    """)
    st.divider()
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.info("**AI İçerik & Profil**\nVideolarınızı analiz edin, vitrininizi puanlayın.")
    with c2:
        st.success("**Üretim & Yönetim**\nSenaryo yazın, çoklu içerik çoğaltın, krizleri yönetin.")
    with c3:
        st.warning("**Veri Bilimi Laboratuvarı**\nMarkov Zincirleri, Monte Carlo ve Bollinger bantları ile geleceği hesaplayın.")

# ==============================================================================
# SEKME 1: AI İÇERİK ANALİZİ
# ==============================================================================
with tab_analiz:
    st.info("Videonuzu yapay zekanın algoritmik süzgecinden geçirin.")
    col1, col2 = st.columns(2)
    with col1:
        sektor = st.selectbox("Sektörünüz / Nişiniz", ["Eğitim", "Teknoloji", "Mizah", "Oyun", "Genel", "Finans"])
        takipci = st.number_input("Mevcut Takipçi Sayınız", 0, 10000000, 1000)
    with col2:
        sure = st.number_input("Video Süresi (sn)", 1, 1000, 60)
        hook = st.text_input("Giriş Cümleniz (Hook)", placeholder="Örn: Eğer her gün yorgun uyanıyorsanız...")

    konu = st.text_area("İçerik Konusu / Fikri", placeholder="Videonun ne hakkında olduğunu kısaca yazın...")
    uploaded_video = st.file_uploader("Video Yükle (Opsiyonel)", type=["mp4", "mov"])

    if st.button("Laboratuvar Analizini Başlat", type="primary"):
        prompt = f"Analiz et: Sektör: {sektor}, Takipçi: {takipci}, Süre: {sure}s, İlk Cümle: {hook}, Konu: {konu}. Metinlerde emoji kullanma. JSON formatında 'skor', 'duygu_radari', 'risk_bolgesi', 'hook_elestirisi', 'viral_aciklama' döndür."
        with st.spinner("Yapay Zeka Analiz Ediyor..."):
            contents = [prompt]
            temp_path = None
            if uploaded_video:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
                    tmp.write(uploaded_video.read())
                    temp_path = tmp.name
                f = genai.upload_file(path=temp_path)
                while f.state.name == "PROCESSING": time.sleep(1); f = genai.get_file(f.name)
                contents = [f, prompt]
            
            try:
                res = model.generate_content(contents)
                sonuc = json.loads(re.search(r'\{.*\}', res.text, re.DOTALL).group(0))
                
                st.metric("Tahmini Viral Skor", f"{sonuc.get('skor', 0)} / 100")
                st.info(f"**Duygu Radarı:** {sonuc.get('duygu_radari')}")
                st.warning(f"**Risk Bölgesi:** {sonuc.get('risk_bolgesi')}")
                st.error(f"**Kanca Eleştirisi:** {sonuc.get('hook_elestirisi')}")
                
                rapor = f"--- ANALIZ ---\nSkor: {sonuc.get('skor')}\nDuygu: {sonuc.get('duygu_radari')}\nRisk: {sonuc.get('risk_bolgesi')}"
                st.download_button("📄 Analiz Raporunu İndir", rapor, "Analiz_Raporu.txt")
            except Exception as e:
                st.error("Bir hata oluştu, lütfen tekrar deneyin.")
            finally:
                if temp_path and os.path.exists(temp_path): os.remove(temp_path)

# ==============================================================================
# SEKME 2: PROFİL VE MARKA CHECK-UP
# ==============================================================================
with tab_profil:
    st.subheader("Profil ve Marka Kimliği Check-up")
    c_p1, c_p2 = st.columns(2)
    with c_p1:
        p_bio = st.text_area("Biyografiniz", placeholder="Bio metnini buraya yapıştırın...")
        p_link = st.text_input("Linkinizin Amacı", placeholder="Örn: Ürün satmak")
    with c_p2:
        p_photo = st.file_uploader("1. Profil Fotoğrafı Yükle", type=["jpg", "png"])
        p_grid = st.file_uploader("2. Profil Akışı (Grid) Yükle", type=["jpg", "png"])

    if st.button("Marka Analizini Başlat", type="primary"):
        prompt = f"Profili incele. Bio: {p_bio}, Link Amacı: {p_link}. Metinlerde emoji kullanma. JSON formatında 'profil_skoru', 'biyografi_analizi', 'grid_analizi', 'acil_duzeltmeler' döndür."
        with st.spinner("Profil İnceleniyor..."):
            contents = [prompt]
            if p_photo: contents.append(Image.open(p_photo))
            if p_grid: contents.append(Image.open(p_grid))
            try:
                res = model.generate_content(contents)
                p_sonuc = json.loads(re.search(r'\{.*\}', res.text, re.DOTALL).group(0))
                st.metric("Marka Uyum Skoru", f"% {p_sonuc.get('profil_skoru', 0)}")
                st.write(f"**Bio Analizi:** {p_sonuc.get('biyografi_analizi')}")
                st.write(f"**Vitrin/Grid:** {p_sonuc.get('grid_analizi')}")
                st.error(f"**Acil Düzeltmeler:** {p_sonuc.get('acil_duzeltmeler')}")
                
                rapor = f"--- PROFIL RAPORU ---\nSkor: {p_sonuc.get('profil_skoru')}\nBio: {p_sonuc.get('biyografi_analizi')}\nAcil: {p_sonuc.get('acil_duzeltmeler')}"
                st.download_button("📄 Profil Raporunu İndir", rapor, "Profil_Raporu.txt")
            except: st.error("Analiz tamamlanamadı.")

# ==============================================================================
# SEKME 3: SENARYO ÜRETİCİ
# ==============================================================================
with tab_senaryo:
    st.subheader("Senaryo ve Kurgu Üretici")
    s_konu = st.text_input("Videonun Ana Konusu", placeholder="Örn: Evde spor yapmanın faydaları")
    if st.button("Senaryo Üret", type="primary"):
        with st.spinner("Yönetmen Senaryoyu Yazıyor..."):
            prompt = f"Konu: {s_konu}. Metinlerde emoji kullanma. Saniye saniye video çekim senaryosu hazırla. JSON formatında 'senaryo': [{{'saniye', 'gorsel', 'ses'}}]"
            try:
                res = model.generate_content([prompt])
                s_sonuc = json.loads(re.search(r'\{.*\}', res.text, re.DOTALL).group(0))
                rapor_metni = f"Konu: {s_konu}\n\n"
                for adim in s_sonuc.get("senaryo", []):
                    with st.expander(adim['saniye']):
                        st.markdown(f"**Görsel:** {adim['gorsel']}\n\n**Ses:** {adim['ses']}")
                    rapor_metni += f"[{adim['saniye']}]\nGörsel: {adim['gorsel']}\nSes: {adim['ses']}\n\n"
                st.download_button("📄 Senaryoyu İndir", rapor_metni, "Senaryo.txt")
            except: st.error("Senaryo oluşturulamadı.")

# ==============================================================================
# SEKME 4: KRİZ YÖNETİMİ
# ==============================================================================
with tab_kriz:
    st.subheader("Kriz ve Topluluk Yöneticisi")
    k_yorum = st.text_area("Gelen Zorlu/Linç Edici Yorum", placeholder="Bu ürününüz tamamen para tuzağı!")
    k_ton = st.selectbox("Cevap Tonu", ["Profesyonel", "Mizahi", "Samimi"])
    if st.button("Kriz Yanıtı Üret", type="primary"):
        with st.spinner("Kriz Masası Toplanıyor..."):
            prompt = f"Yorum: '{k_yorum}', Ton: '{k_ton}'. Metinlerde emoji kullanma. JSON: 'risk_seviyesi', 'cevap_1', 'cevap_2' döndür."
            try:
                res = model.generate_content([prompt])
                k_sonuc = json.loads(re.search(r'\{.*\}', res.text, re.DOTALL).group(0))
                st.error(f"**Risk Seviyesi:** {k_sonuc.get('risk_seviyesi')}")
                st.success(f"**Seçenek 1:** {k_sonuc.get('cevap_1')}")
                st.info(f"**Seçenek 2:** {k_sonuc.get('cevap_2')}")
            except: st.error("Yanıt üretilemedi.")

# ==============================================================================
# SEKME 5: İÇERİK ÇOĞALTICI
# ==============================================================================
with tab_cogalt:
    st.subheader("İçerik Çoğaltıcı (Zaman Makinesi)")
    c_fikir = st.text_area("Ana Fikriniz", placeholder="Uzun bir düşüncenizi buraya yazın...")
    if st.button("Fikri 3 Platform İçin Çoğalt", type="primary"):
        with st.spinner("İçerik Uyarlanıyor..."):
            prompt = f"Ana Fikir: '{c_fikir}'. Metinlerde emoji kullanma. JSON formatında 'twitter', 'instagram_carousel', 'tiktok' metinleri üret."
            try:
                res = model.generate_content([prompt])
                c_sonuc = json.loads(re.search(r'\{.*\}', res.text, re.DOTALL).group(0))
                c1, c2, c3 = st.columns(3)
                c1.info(f"**Twitter:**\n{c_sonuc.get('twitter')}")
                c2.success(f"**Instagram:**\n{c_sonuc.get('instagram_carousel')}")
                c3.warning(f"**TikTok:**\n{c_sonuc.get('tiktok')}")
            except: st.error("Çoğaltma başarısız.")

# ==============================================================================
# SEKME 6: İLERİ VERİ BİLİMİ LABORATUVARI (ŞOV KISMI - 7 MODÜL)
# ==============================================================================
with tab_matematik:
    st.subheader("Veri Bilimi ve İstatistik Laboratuvarı")
    secilen_modul = st.selectbox("Kullanılacak Matematiksel Modeli Seçin", [
        "1. Etkileşim (ER) ve Varyans Analizi", 
        "2. İstatistiksel A/B Hipotez Testi (Z-Test)", 
        "3. İçerik Yarı Ömrü (Üstel Sönüm / Exponential Decay)",
        "4. Monte Carlo Simülasyonu (Risk Analizi)",
        "5. Bollinger Bantları (Viral Kırılma Noktası)",
        "6. Markov Zincirleri (Durum Tahmini)",
        "7. Pearson Korelasyonu (Değişken Analizi)"
    ])
    st.divider()

    # MODÜL 1: VARYANS
    if "1." in secilen_modul:
        st.caption("İzlenmelerinizdeki standart sapmayı ve istikrarı hesaplayın.")
        v = [st.number_input(f"Video {i}", value=1000+i*100) for i in range(1, 6)]
        if st.button("Sapmayı Hesapla"):
            avg = np.mean(v); std = np.std(v)
            df = pd.DataFrame({"Videolar": ["V1","V2","V3","V4","V5"], "İzlenmeler": v})
            st.dataframe(df.T)
            st.metric("Ortalama (μ)", f"{int(avg):,}"); st.metric("Standart Sapma (σ)", f"{int(std):,}")

    # MODÜL 2: Z-TEST
    elif "2." in secilen_modul:
        col_ab1, col_ab2 = st.columns(2)
        with col_ab1: n1 = st.number_input("A İzlenme", value=50000); x1 = st.number_input("A Beğeni", value=1200)
        with col_ab2: n2 = st.number_input("B İzlenme", value=52000); x2 = st.number_input("B Beğeni", value=1450)
        if st.button("Z-Test Yap"):
            p1, p2 = x1/n1, x2/n2; p_pool = (x1+x2)/(n1+n2)
            se = math.sqrt(p_pool*(1-p_pool)*(1/n1+1/n2))
            z = abs(p1-p2)/se; p_val = 0.5 * math.erfc(z/math.sqrt(2)) * 2
            st.metric("Z-Skoru", f"{z:.2f}"); st.write(f"**P-Değeri:** {p_val:.5f}")
            if p_val < 0.05: st.success("Sonuç: Fark İstatistiksel Olarak Anlamlıdır! (Tesadüf Değil)")
            else: st.error("Sonuç: Fark Anlamlı Değildir. Tamamen rastgele.")

    # MODÜL 3: ÜSTEL SÖNÜM
    elif "3." in secilen_modul:
        n0 = st.number_input("Başlangıç İzlenmesi", value=10000)
        nt = st.number_input("Şu Anki İzlenme", value=2500)
        t = st.number_input("Geçen Gün", value=4)
        if st.button("Yarı Ömür Hesapla"):
            if nt < n0:
                lam = -math.log(nt/n0)/t; half = math.log(2)/lam
                st.warning(f"⏳ **Videonun Yarı Ömrü:** {half:.1f} Gün.")
                st.line_chart(pd.DataFrame({"Gün": range(15), "İzlenme": [n0*math.exp(-lam*g) for g in range(15)]}).set_index("Gün"))
            else: st.error("Şu anki izlenme başlangıçtan büyük olamaz.")

    # MODÜL 4: MONTE CARLO
    elif "4." in secilen_modul:
        ort = st.number_input("Ortalama İzlenme (μ)", value=15000)
        sap = st.number_input("Sapma (σ)", value=4000)
        hedef = st.number_input("Hedef İzlenme", value=20000)
        if st.button("1000 Simülasyon Başlat"):
            with st.spinner("Zarlar atılıyor..."):
                sims = np.where(np.random.normal(ort, sap, 1000) < 0, 0, np.random.normal(ort, sap, 1000))
                basari = len(sims[sims >= hedef])
                st.line_chart(pd.DataFrame({"Frekans": np.histogram(sims, bins=40)[0]}, index=np.round(np.histogram(sims, bins=40)[1][:-1], 0).astype(int)))
                st.metric("Hedefe Ulaşma İhtimali", f"% {basari/10}")

    # MODÜL 5: BOLLINGER BANTLARI
    elif "5." in secilen_modul:
        data = [st.number_input(f"Video {i}", value=1000+i*50) for i in range(1, 11)]
        if st.button("Bantları Çiz"):
            m = np.mean(data); s = np.std(data)
            st.info(f"🚀 **Viral Kırılma Noktası (Üst Bant): {int(m + 2*s):,}**")
            st.error(f"📉 **Çöküş Sınırı (Alt Bant): {int(max(0, m - 2*s)):,}**")
            st.line_chart(pd.DataFrame({"İzlenme": data, "Ortalama": [m]*10, "Viral": [m+2*s]*10, "Flop": [max(0, m-2*s)]*10}))

    # MODÜL 6: MARKOV ZİNCİRLERİ
    elif "6." in secilen_modul:
        mevcut = st.radio("Son Videonuzun Durumu:", ["Çöküş", "Normal", "Viral"])
        col_m1, col_m2, col_m3 = st.columns(3)
        probs = {"Çöküş": col_m1.slider("Çöküşten Virale %", 0, 100, 10), 
                 "Normal": col_m2.slider("Normalden Virale %", 0, 100, 30), 
                 "Viral": col_m3.slider("Viralden Tekrar Virale %", 0, 100, 20)}
        if st.button("Olasılık Tahmini Yap"):
            st.metric("Bir Sonraki Videonun Viral Olma Olasılığı", f"% {probs[mevcut]}")

    # MODÜL 7: PEARSON KORELASYONU
    elif "7." in secilen_modul:
        c_x, c_y = st.columns(2)
        X = c_x.text_area("X Değişkeni (Örn: Süre - Virgülle ayırın)", "15, 30, 45, 60, 90")
        Y = c_y.text_area("Y Değişkeni (Örn: İzlenme - Virgülle ayırın)", "5000, 12000, 8000, 15000, 20000")
        if st.button("Korelasyon (r) Hesapla"):
            try:
                xl = [float(i) for i in X.split(",")]; yl = [float(i) for i in Y.split(",")]
                r = np.corrcoef(xl, yl)[0, 1]
                st.metric("Korelasyon Katsayısı (r)", f"{r:.3f}")
                st.scatter_chart(pd.DataFrame({"X": xl, "Y": yl}), x="X", y="Y")
            except: st.error("Hatalı veri formatı.")