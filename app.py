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
st.set_page_config(page_title="AI Sosyal Medya Ajansı", layout="wide")

try:
    import google.generativeai as genai
    from PIL import Image
except ModuleNotFoundError:
    st.error("HATA: Gerekli kütüphaneler bulunamadı! Lütfen terminale 'pip install google-generativeai pillow' yazın.")
    st.stop()

# ==============================================================================
# 2. API ANAHTARI KONTROLÜ VE YAPILANDIRMA
# ==============================================================================
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except (KeyError, FileNotFoundError):
    API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    st.error("HATA: API Anahtarı bulunamadı! Lütfen .streamlit/secrets.toml dosyanızı kontrol edin.")
    st.stop()
else:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"temperature": 0.5})

st.title("Yapay Zeka ve İleri Veri Bilimi Ajansı")

# ==============================================================================
# 3. SEKMELERİN OLUŞTURULMASI
# ==============================================================================
tab_ana, tab1, tab2, tab_matematik = st.tabs([
    "Ana Sayfa", 
    "AI İçerik Analizi", 
    "Senaryo Üretici",
    "İleri Veri Bilimi Laboratuvarı"
])

# ==============================================================================
# SEKME 0: ANA SAYFA
# ==============================================================================
with tab_ana:
    st.subheader("Hoş Geldiniz! Veriyle Büyümeye Hazır Mısınız?")
    st.markdown("""
    Bu platform, yapay zekanın yaratıcılığı ile **ileri seviye matematiğin ve istatistiğin** kesinliğini birleştiren profesyonel bir veri bilimi aracıdır. Hissiyatla değil, verilerle sosyal medyayı yönetin.
    """)
    st.divider()
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.info("**AI İçerik Analizi**\nVideonuzun viral skorunu ve risk bölgelerini öğrenin.")
    with c2:
        st.success("**Senaryo Üretici**\nBoş sayfa sendromuna son! Saniye saniye kurgu hazırlayın.")
    with c3:
        st.warning("**Veri Bilimi Laboratuvarı**\nA/B Hipotez Testleri, Üstel Sönüm, Monte Carlo ve Bollinger analizleri yapın.")

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
# SEKME 3: İLERİ VERİ BİLİMİ VE İSTATİSTİK LABORATUVARI
# ==============================================================================
with tab_matematik:
    st.subheader("Veri Bilimi ve İstatistik Laboratuvarı")
    st.markdown("Sosyal medya şans değil, ileri matematiktir. Lütfen kullanmak istediğiniz modeli seçin:")
    
    secilen_modul = st.selectbox("Analiz Modeli", [
        "1. Etkileşim (ER) ve Varyans İstikrar Analizi", 
        "2. İstatistiksel A/B Hipotez Testi (Z-Test)", 
        "3. İçerik Yarı Ömrü (Üstel Sönüm / Exponential Decay)",
        "4. Monte Carlo Simülasyonu (Olasılık ve Risk Analizi)",
        "5. İzlenme Dalgalanması ve Kırılma Noktası (Bollinger Bantları)"
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
        st.caption("İki farklı içeriğin etkileşim oranlarını kıyaslayın. Aradaki fark tesadüf mü, yoksa istatistiksel olarak anlamlı mı?")
        
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
            se = math.sqrt(p_pool * (1 - p_pool) * (1/n1 + 1/n2))
            
            if se == 0:
                st.warning("Veriler hesaplama için yetersiz veya hatalı.")
            else:
                z_score = abs(p1 - p2) / se
                p_value = 0.5 * math.erfc(z_score / math.sqrt(2)) * 2 
                
                c_oran1, c_oran2, c_z = st.columns(3)
                c_oran1.metric("A Grubu Etkileşim Oranı", f"% {p1*100:.2f}")
                c_oran2.metric("B Grubu Etkileşim Oranı", f"% {p2*100:.2f}")
                c_z.metric("Hesaplanan Z-Skoru", f"{z_score:.2f}")
                
                st.write(f"**P-Değeri (Olasılık):** {p_value:.5f}")
                
                if p_value < 0.05:
                    st.success(f"🏆 BİLİMSEL SONUÇ: H0 Hipotezi reddedildi! Fark istatistiksel olarak %95 oranında anlamlıdır. (P < 0.05). Bu bir tesadüf değil!")
                else:
                    st.error("📉 BİLİMSEL SONUÇ: Fark istatistiksel olarak anlamlı DEĞİLDİR (P > 0.05). Aradaki fark tamamen rastgeledir.")

    # ---------------------------------------------------------
    # MODÜL 3: Üstel Sönüm (Exponential Decay) Yarı Ömür
    # ---------------------------------------------------------
    elif "3." in secilen_modul:
        st.markdown("### 3. İçerik Yarı Ömrü (Üstel Sönüm / Exponential Decay)")
        st.caption("Matematiksel Formül: N(t) = N₀ * e^(-λt). Viral bir videonun izlenme hızının zamanla nasıl söndüğünü hesaplar.")
        
        col_us1, col_us2, col_us3 = st.columns(3)
        n0 = col_us1.number_input("İlk Gün (Zirve) İzlenme Sayısı (N₀)", min_value=1, value=10000)
        nt = col_us2.number_input("Şu Anki Günlük İzlenme Sayısı (Nₜ)", min_value=1, value=2500)
        t_gecen = col_us3.number_input("Aradan Geçen Gün Sayısı (t)", min_value=1, value=4)
        
        if st.button("Yarı Ömrü ve Çürüme Hızını Hesapla", type="primary"):
            if nt >= n0:
                st.warning("Şu anki izlenme ilk günden büyük olamaz (Sönüm gerçekleşmiyor!)")
            else:
                lambda_sabiti = -math.log(nt / n0) / t_gecen
                yari_omur = math.log(2) / lambda_sabiti
                
                st.info(f"**Sönüm Sabiti (λ):** {lambda_sabiti:.4f} (Videonuz günde % {lambda_sabiti*100:.1f} ivme kaybediyor.)")
                st.warning(f"⏳ **Videonun Yarı Ömrü:** {yari_omur:.1f} Gün. (Bu video her {yari_omur:.1f} günde bir, ivmesinin yarısını kaybedecek.)")
                
                gunler = list(range(0, 15))
                projeksiyon = [n0 * math.exp(-lambda_sabiti * gun) for gun in gunler]
                
                df_grafik = pd.DataFrame({"Günler": gunler, "Günlük İzlenme Beklentisi": projeksiyon})
                st.line_chart(df_grafik.set_index("Günler"))

    # ---------------------------------------------------------
    # MODÜL 4: MONTE CARLO SİMÜLASYONU
    # ---------------------------------------------------------
    elif "4." in secilen_modul:
        st.markdown("### 4. Monte Carlo Simülasyonu (Risk ve İhtimal Analizi)")
        st.caption("Geçmiş verilerinize dayanarak bilgisayar ortamında rastgele 1.000 farklı evren yaratın. Bir sonraki videonuzun viral olma ihtimalini hesaplayın.")

        col_mc1, col_mc2, col_mc3 = st.columns(3)
        mc_ort = col_mc1.number_input("Videolarınızın Ortalama İzlenmesi (μ)", min_value=1, value=15000)
        mc_sapma = col_mc2.number_input("İzlenme Dalgalanması (Standart Sapma - σ)", min_value=1, value=4000)
        mc_hedef = col_mc3.number_input("Viral Hedefiniz (İstenen İzlenme)", min_value=1, value=20000)

        if st.button("1.000 Farklı Senaryoyu Simüle Et", type="primary"):
            with st.spinner("Zarlar atılıyor, 1.000 farklı paralel evren simüle ediliyor..."):
                time.sleep(1)
                sim_sayisi = 1000
                
                simulasyonlar = np.random.normal(mc_ort, mc_sapma, sim_sayisi)
                simulasyonlar = np.where(simulasyonlar < 0, 0, simulasyonlar)
                
                basarili_senaryolar = len(simulasyonlar[simulasyonlar >= mc_hedef])
                ihtimal = (basarili_senaryolar / sim_sayisi) * 100
                
                counts, bins = np.histogram(simulasyonlar, bins=40)
                df_hist = pd.DataFrame({"Senaryo Frekansı": counts}, index=np.round(bins[:-1], 0).astype(int))
                
                st.line_chart(df_hist)
                
                st.subheader("Monte Carlo Simülasyon Sonuçları")
                c_iht, c_min, c_max = st.columns(3)
                c_iht.metric("Hedefe Ulaşma İhtimali", f"% {ihtimal:.1f}")
                c_min.metric("En Kötü Senaryo (Tahmin)", f"{int(np.min(simulasyonlar)):,}")
                c_max.metric("En İyi Senaryo (Tahmin)", f"{int(np.max(simulasyonlar)):,}")

                if ihtimal > 75:
                    st.success(f"BİLİMSEL SONUÇ: Çok Yüksek İhtimal! 1.000 senaryonun {basarili_senaryolar} tanesinde hedefi geçtiniz.")
                elif ihtimal > 30:
                    st.warning(f"BİLİMSEL SONUÇ: Orta İhtimal. 1.000 senaryonun {basarili_senaryolar} tanesinde hedefe ulaştınız.")
                else:
                    st.error(f"BİLİMSEL SONUÇ: Düşük İhtimal. 1.000 senaryonun sadece {basarili_senaryolar} tanesinde hedefe ulaştınız.")

    # ---------------------------------------------------------
    # MODÜL 5: İZLENME DALGALANMASI (BOLLINGER BANTLARI)
    # ---------------------------------------------------------
    elif "5." in secilen_modul:
        st.markdown("### 5. İzlenme Dalgalanması ve Kırılma Noktası (Bollinger Bantları)")
        st.caption("Son 10 videonuzun verisini girerek kanalınızın 'Dalgalanma Katsayısını (CV)' ve bir videonun viral veya çöküş sayılması için gereken sınır değerleri hesaplayın.")

        st.write("**Son 10 Videonuzun İzlenme Sayıları (Eskiden Yeniye):**")
        c1, c2, c3, c4, c5 = st.columns(5)
        d1 = c1.number_input("1. Video", value=1000, min_value=0)
        d2 = c2.number_input("2. Video", value=1200, min_value=0)
        d3 = c3.number_input("3. Video", value=950, min_value=0)
        d4 = c4.number_input("4. Video", value=1100, min_value=0)
        d5 = c5.number_input("5. Video", value=1050, min_value=0)
        
        c6, c7, c8, c9, c10 = st.columns(5)
        d6 = c6.number_input("6. Video", value=1300, min_value=0)
        d7 = c7.number_input("7. Video", value=1150, min_value=0)
        d8 = c8.number_input("8. Video", value=900, min_value=0)
        d9 = c9.number_input("9. Video", value=1400, min_value=0)
        d10 = c10.number_input("10. Video (En Yeni)", value=1250, min_value=0)

        if st.button("Dalgalanma ve Kırılma Analizi Yap", type="primary"):
            veri_seti = [d1, d2, d3, d4, d5, d6, d7, d8, d9, d10]
            ortalama = np.mean(veri_seti)
            standart_sapma = np.std(veri_seti)
            
            cv = (standart_sapma / ortalama) * 100 if ortalama > 0 else 0
            
            ust_bant = ortalama + (2 * standart_sapma)
            alt_bant = ortalama - (2 * standart_sapma)
            if alt_bant < 0: alt_bant = 0

            st.subheader("Matematiksel Kanal Profili")
            col_m1, col_m2, col_m3 = st.columns(3)
            col_m1.metric("Ortalama İzlenme (μ)", f"{int(ortalama):,}")
            col_m2.metric("Dalgalanma Katsayısı (CV)", f"% {cv:.1f}")
            col_m3.metric("Standart Sapma (σ)", f"{int(standart_sapma):,}")

            st.subheader("Viral ve Çöküş (Flop) Sınırları")
            st.info(f"🚀 **Viral Kırılma Noktası (Üst Bant): {int(ust_bant):,}**\n\nBir videonuzun algoritma tarafından 'Viral' olarak algılanıp ekstra öne çıkarılması için izlenmesinin bu rakamı geçmesi gerekir.")
            st.error(f"📉 **Çöküş Sınırı (Alt Bant): {int(alt_bant):,}**\n\nBir videonuz bu rakamın altında kalıyorsa, kancanız (hook) başarısız olmuş demektir.")

            df_dalga = pd.DataFrame({
                "Videolar": [f"V{i}" for i in range(1, 11)],
                "İzlenme": veri_seti,
                "Ortalama": [ortalama] * 10,
                "Viral Sınırı": [ust_bant] * 10,
                "Çöküş Sınırı": [alt_bant] * 10
            })
            
            st.line_chart(df_dalga.set_index("Videolar"))

            if cv < 15:
                st.success("Analiz: Kanalınız İNANILMAZ İSTİKRARLI. İzleyicileriniz çok sadık.")
            elif cv < 40:
                st.warning("Analiz: Kanalınızda NORMAL DALGALANMA var. Sağlıklı bir profil.")
            else:
                st.error("Analiz: Kanalınızda AŞIRI DALGALANMA var. Belirli bir nişe (sektöre) odaklanmalısınız.")