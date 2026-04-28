import streamlit as st
import os
import json
import re
import tempfile
import time
import math
import pandas as pd
import numpy as np

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

st.title("Yapay Zeka ve İleri Veri Bilimi Ajansı")

# --- 4 SEKME ---
tab_ana, tab1, tab2, tab_matematik = st.tabs([
    "Ana Sayfa", 
    "AI İçerik Analizi", 
    "Senaryo Üretici",
    "İleri Veri Bilimi Laboratuvarı"
])

# ==============================================================================
# ANA SAYFA
# ==============================================================================
with tab_ana:
    st.subheader("Hoş Geldiniz! Veriyle Büyümeye Hazır Mısınız?")
    st.markdown("""
    Bu platform, yapay zekanın yaratıcılığı ile **ileri seviye matematiğin ve istatistiğin** kesinliğini birleştiren profesyonel bir veri bilimi aracıdır.
    """)
    st.divider()
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.info("**AI İçerik Analizi**\nVideonuzun viral skorunu ve risk bölgelerini öğrenin.")
    with c2:
        st.success("**Senaryo Üretici**\nBoş sayfa sendromuna son! Saniye saniye kurgu hazırlayın.")
    with c3:
        st.warning("**Veri Bilimi Laboratuvarı**\nA/B Hipotez Testleri, Üstel Sönüm ve Z-Skor analizleri yapın.")

# ==============================================================================
# SEKME 1: AI İÇERİK ANALİZİ
# ==============================================================================
with tab1:
    st.info("Videonuzu yapay zekanın algoritmik süzgecinden geçirin.")
    col1, col2 = st.columns(2)
    with col1:
        sektor = st.selectbox("Sektörünüz / Nişiniz", ["Eğitim", "Teknoloji", "Mizah", "Oyun", "Genel", "Finans"], key="sektor1")
        takipci = st.number_input("Mevcut Takipçi Sayınız", 0, 10000000, 1000, key="takipci1")

    with col2:
        sure = st.number_input("Video Süresi (sn)", 1, 1000, 60, key="sure1")
        hook = st.text_input("Videoya Giriş Cümleniz (Hook)", placeholder="Örn: Eğer her gün yorgun uyanıyorsanız...", key="hook1")

    konu = st.text_area("İçerik Konusu / Fikri", placeholder="Videonun ne hakkında olduğunu kısaca yazın...", key="konu1")
    uploaded_video = st.file_uploader("Analiz için videonuzu yükleyin (Opsiyonel)", type=["mp4", "mov"], key="vid1")

    def ai_kapsamli_analiz(sektor, konu, takipci, sure, hook, video_file_path=None):
        prompt = f"""
        Analiz et: Sektör: {sektor}, Takipçi: {takipci}, Süre: {sure} sn, İlk Cümle: {hook}, Konu: {konu}.
        Metinlerde emoji kullanma.
        1. Duygu Radarı: İzleyicide uyandıracağı baskın duyguları yaz.
        2. Risk Bölgesi (Drop-off): İzleyicinin sıkılma riskini tespit et.
        3. Hook Eleştirisi: '{hook}' cümlesini eleştir.
        JSON formatında cevap ver:
        {{"skor": 85, "duygu_radari": "...", "risk_bolgesi": "...", "hook_elestirisi": "..."}}
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
        except Exception:
            return None
        finally:
            if gemini_file:
                genai.delete_file(gemini_file.name)

    if st.button("Yapay Zeka Analizini Başlat", type="primary", use_container_width=True):
        if not konu and not uploaded_video:
            st.warning("Lütfen bir konu yazın veya video yükleyin!")
        else:
            with st.spinner("Yapay Zeka Verileri İşliyor..."):
                temp_path = None
                if uploaded_video:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
                        tmp.write(uploaded_video.read())
                        temp_path = tmp.name
                sonuclar = ai_kapsamli_analiz(sektor, konu, takipci, sure, hook, temp_path)
                if temp_path and os.path.exists(temp_path):
                    os.remove(temp_path)
                
            if sonuclar:
                st.metric("Tahmini Viral Skor", f"{sonuclar.get('skor', 0)} / 100")
                st.info(f"**Duygu Radarı:** {sonuclar.get('duygu_radari', '')}")
                st.warning(f"**Risk Bölgesi:** {sonuclar.get('risk_bolgesi', '')}")
                st.error(f"**Kanca Eleştirisi:** {sonuclar.get('hook_elestirisi', '')}")

# ==============================================================================
# SEKME 2: SENARYO ÜRETİCİ
# ==============================================================================
with tab2:
    st.subheader("Senaryo ve Kurgu Üretici")
    s_konu = st.text_input("Videonun Ana Konusu", placeholder="Örn: Python ile veri analizi nasıl yapılır?")
    
    def ai_senaryo_yazici(konu):
        prompt = f"""
        Konu: {konu}. Metinlerde emoji kullanma.
        Saniye saniye akıcı bir video çekim senaryosu hazırla.
        JSON formatında cevap ver:
        {{"senaryo": [{{"saniye": "0-3 sn", "gorsel": "...", "ses": "..."}}, {{"saniye": "3-10 sn", "gorsel": "...", "ses": "..."}}]}}
        """
        try:
            response = model.generate_content([prompt])
            match = re.search(r'\{.*\}', response.text, re.DOTALL)
            return json.loads(match.group(0)) if match else None
        except Exception:
            return None

    if st.button("Senaryo Üret", type="primary", use_container_width=True):
        if s_konu:
            with st.spinner("Yönetmen Senaryoyu Yazıyor..."):
                senaryo_sonuc = ai_senaryo_yazici(s_konu)
            if senaryo_sonuc:
                for adim in senaryo_sonuc.get("senaryo", []):
                    with st.expander(f"{adim['saniye']}", expanded=True):
                        st.markdown(f"**Görsel:** {adim['gorsel']}")
                        st.markdown(f"**Ses:** {adim['ses']}")
        else:
            st.warning("Lütfen konu girin.")

# ==============================================================================
# SEKME 3: İLERİ VERİ BİLİMİ VE İSTATİSTİK LABORATUVARI (YENİ)
# ==============================================================================
with tab_matematik:
    st.subheader("Veri Bilimi ve İstatistik Laboratuvarı")
    st.markdown("Sosyal medya şans değil, ileri matematiktir. Lütfen kullanmak istediğiniz matematiksel modeli seçin:")
    
    secilen_modul = st.selectbox("Analiz Modeli", [
        "1. Etkileşim (ER) ve Varyans İstikrar Analizi", 
        "2. İstatistiksel A/B Hipotez Testi (Z-Test)", 
        "3. İçerik Yarı Ömrü (Üstel Sönüm / Exponential Decay)"
    ])
    
    st.divider()
    
    # ---------------------------------------------------------
    # MODÜL 1: Temel Etkileşim ve Varyans
    # ---------------------------------------------------------
    if "1." in secilen_modul:
        st.markdown("### 1. Varyans (σ²) ve Etkileşim Oranı (ER)")
        st.caption("Algoritma dalgalanmayı sevmez. İzlenmelerinizdeki standart sapmayı hesaplayın.")
        
        col_v1, col_v2, col_v3, col_v4, col_v5 = st.columns(5)
        v1 = col_v1.number_input("1. Video", min_value=0, value=1200)
        v2 = col_v2.number_input("2. Video", min_value=0, value=1350)
        v3 = col_v3.number_input("3. Video", min_value=0, value=900)
        v4 = col_v4.number_input("4. Video", min_value=0, value=1500)
        v5 = col_v5.number_input("5. Video", min_value=0, value=1100)
        
        if st.button("Standart Sapmayı Hesapla", type="primary"):
            veriler = [v1, v2, v3, v4, v5]
            ortalama = sum(veriler) / len(veriler)
            varyans = sum((x - ortalama) ** 2 for x in veriler) / len(veriler)
            standart_sapma = math.sqrt(varyans)
            sapma_yuzdesi = (standart_sapma / ortalama) * 100 if ortalama > 0 else 0
            
            df = pd.DataFrame({"Videolar": ["V1", "V2", "V3", "V4", "V5"], "İzlenmeler": veriler})
            st.dataframe(df.T)
            
            c1, c2 = st.columns(2)
            c1.metric("Aritmetik Ortalama (μ)", f"{ortalama:,.0f}")
            c2.metric("Standart Sapma (σ)", f"{standart_sapma:,.0f}")
            
            if sapma_yuzdesi < 30:
                st.success("Sonuç: İSTİKRARLI. İzlenmeleriniz ortalamaya çok yakın seyrediyor.")
            else:
                st.error("Sonuç: İSTİKRARSIZ (Yüksek Varyans). Videolarınız şansa bağlı tutuyor.")

    # ---------------------------------------------------------
    # MODÜL 2: İstatistiksel A/B Hipotez Testi
    # ---------------------------------------------------------
    elif "2." in secilen_modul:
        st.markdown("### 2. İstatistiksel A/B Hipotez Testi (Z-Skoru)")
        st.caption("İki farklı içeriğin etkileşim oranlarını kıyaslayın. Aradaki fark tesadüf mü, yoksa istatistiksel olarak kanıtlanmış mı? (H0 Hipotezi Reddi)")
        
        col_ab1, col_ab2 = st.columns(2)
        with col_ab1:
            st.info("**A Videosu (Kontrol Grubu)**")
            n1 = st.number_input("A Videosu Toplam Gösterim", min_value=1, value=50000)
            x1 = st.number_input("A Videosu Toplam Tıklama/Beğeni", min_value=0, value=1200)
        with col_ab2:
            st.success("**B Videosu (Test Grubu)**")
            n2 = st.number_input("B Videosu Toplam Gösterim", min_value=1, value=52000)
            x2 = st.number_input("B Videosu Toplam Tıklama/Beğeni", min_value=0, value=1450)
            
        if st.button("İstatistiksel Anlamlılığı Test Et", type="primary"):
            p1 = x1 / n1
            p2 = x2 / n2
            p_pool = (x1 + x2) / (n1 + n2)
            # Standart Hata (Standard Error) Formülü
            se = math.sqrt(p_pool * (1 - p_pool) * (1/n1 + 1/n2))
            
            if se == 0:
                st.warning("Veriler hesaplama için yetersiz veya hatalı.")
            else:
                # Z-Skoru
                z_score = abs(p1 - p2) / se
                # P-Değeri hesaplama (math.erfc kullanımı)
                p_value = 0.5 * math.erfc(z_score / math.sqrt(2)) * 2 # Çift kuyruklu test
                
                c_oran1, c_oran2, c_z = st.columns(3)
                c_oran1.metric("A Grubu Etkileşim Oranı", f"% {p1*100:.2f}")
                c_oran2.metric("B Grubu Etkileşim Oranı", f"% {p2*100:.2f}")
                c_z.metric("Hesaplanan Z-Skoru", f"{z_score:.2f}")
                
                st.write(f"**P-Değeri (Olasılık):** {p_value:.5f}")
                
                if p_value < 0.05:
                    st.success(f"🏆 **BİLİMSEL SONUÇ:** H0 Hipotezi reddedildi! Gruplar arasındaki fark **istatistiksel olarak %95 oranında anlamlıdır.** (P < 0.05). Hangi oran yüksekse o videonun kapağını/başlığını güvenle kullanabilirsiniz. Bu bir tesadüf değil!")
                else:
                    st.error("📉 **BİLİMSEL SONUÇ:** Gruplar arasındaki fark istatistiksel olarak **anlamlı DEĞİLDİR** (P > 0.05). Aradaki fark tamamen rastgeledir (Şans eseri). Her iki başlık da benzer performans gösteriyor.")

    # ---------------------------------------------------------
    # MODÜL 3: Üstel Sönüm (Exponential Decay) Yarı Ömür
    # ---------------------------------------------------------
    elif "3." in secilen_modul:
        st.markdown("### 3. İçerik Yarı Ömrü (Üstel Sönüm / Exponential Decay)")
        st.caption("Matematiksel Formül: N(t) = N₀ * e^(-λt). Viral bir videonun izlenme hızının zamanla nasıl söndüğünü (çürüdüğünü) ve ne zaman tamamen öleceğini hesaplar.")
        
        col_us1, col_us2, col_us3 = st.columns(3)
        n0 = col_us1.number_input("İlk Gün (Zirve) İzlenme Sayısı (N₀)", min_value=1, value=10000)
        nt = col_us2.number_input("Şu Anki Günlük İzlenme Sayısı (Nₜ)", min_value=1, value=2500)
        t_gecen = col_us3.number_input("Aradan Geçen Gün Sayısı (t)", min_value=1, value=4)
        
        if st.button("Videonun Yarı Ömrünü ve Çürüme Hızını Hesapla", type="primary"):
            if nt >= n0:
                st.warning("Şu anki izlenme ilk günden büyük olamaz (Sönüm gerçekleşmiyor, tam tersi büyüme var!)")
            else:
                # Lambda (Sönüm Sabiti) = -ln(Nt / N0) / t
                lambda_sabiti = -math.log(nt / n0) / t_gecen
                # Yarı ömür t(1/2) = ln(2) / lambda
                yari_omur = math.log(2) / lambda_sabiti
                
                st.info(f"**Sönüm Sabiti (λ):** {lambda_sabiti:.4f} (Videonuz günde % {lambda_sabiti*100:.1f} ivme kaybediyor.)")
                st.warning(f"⏳ **Videonun Yarı Ömrü:** {yari_omur:.1f} Gün. (Bu video her {yari_omur:.1f} günde bir, günlük izlenme sayısının yarısını kaybedecek.)")
                
                # Grafik Çizimi (Gelecek 14 gün projeksiyonu)
                gunler = list(range(0, 15))
                projeksiyon = [n0 * math.exp(-lambda_sabiti * gun) for gun in gunler]
                
                df_grafik = pd.DataFrame({"Günler": gunler, "Günlük İzlenme Beklentisi": projeksiyon})
                st.line_chart(df_grafik.set_index("Günler"))
                
                st.success("Tavsiye: Algoritmik çürüme (decay) başlamış. Grafik tabana inmeden önce yeni bir içerik yayınlayarak kitleyi tazelemelisiniz.")