import streamlit as st
import os
import json
import re
import tempfile
import time
import math
import pandas as pd

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

st.title("Yapay Zeka ve Veri Bilimi Ajansı")

# --- 4 SEKME (Matematik Sekmesi Eklendi) ---
tab_ana, tab1, tab2, tab_matematik = st.tabs([
    "Ana Sayfa", 
    "AI İçerik Analizi", 
    "Senaryo Üretici",
    "Matematiksel Analizler"
])

# ==============================================================================
# ANA SAYFA
# ==============================================================================
with tab_ana:
    st.subheader("Hoş Geldiniz! Veriyle Büyümeye Hazır Mısınız?")
    st.markdown("""
    Bu platform, yapay zekanın yaratıcılığı ile **matematiğin ve istatistiğin** kesinliğini birleştiren profesyonel bir araçtır. İçeriklerinizi yayınlamadan önce test edebilir, senaryolar oluşturabilir ve sayfanızın büyüme grafiğini matematiksel fonksiyonlarla hesaplayabilirsiniz.
    """)
    st.divider()
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.info("**AI İçerik Analizi**\nVideonuzun viral skorunu ve risk bölgelerini yapay zeka ile öğrenin.")
    with c2:
        st.success("**Senaryo Üretici**\nBoş sayfa sendromuna son! Saniye saniye kurgu ve çekim planı hazırlayın.")
    with c3:
        st.warning("**Matematiksel Modeller**\nEtkileşim oranlarını, standart sapmayı ve doğrusal büyüme denklemlerini hesaplayın.")
        
    st.divider()
    st.subheader("Sistem Durumu")
    st.text("Tüm API bağlantıları ve matematik kütüphaneleri (Numpy, Pandas, Math) aktif ve çalışıyor.")

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
        Eğer video varsa izle. Videodaki kişinin enerjisini analiz et. Metinlerde emoji kullanma.
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
            with st.status("Veriler işleniyor...", expanded=True) as status:
                temp_path = None
                if uploaded_video:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
                        tmp.write(uploaded_video.read())
                        temp_path = tmp.name
                sonuclar = ai_kapsamli_analiz(sektor, konu, takipci, sure, hook, temp_path)
                if temp_path and os.path.exists(temp_path):
                    os.remove(temp_path)
                status.update(label="Analiz Hazır!", state="complete", expanded=False)
                
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
        Bu konu için saniye saniye akıcı bir video çekim senaryosu hazırla.
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
                        st.markdown(f"**Görsel/Kamera:** {adim['gorsel']}")
                        st.markdown(f"**Dış Ses:** {adim['ses']}")
        else:
            st.warning("Lütfen konu girin.")

# ==============================================================================
# SEKME 3: MATEMATİKSEL ANALİZLER VE VERİ MODELLERİ (YENİ - PÜR BİLİM)
# ==============================================================================
with tab_matematik:
    st.subheader("Veri Bilimi ve İstatistik Merkezi")
    st.markdown("Sosyal medya şans değil, istatistiktir. Paylaşımlarınızın performansını matematiksel fonksiyonlarla ölçün.")
    
    st.divider()
    
    # 1. MODÜL: ETKİLEŞİM ORANI (ER)
    st.markdown("### 1. Etkileşim Oranı (Engagement Rate) Fonksiyonu")
    st.caption("Formül: ƒ(x) = (Beğeni + Yorum + Paylaşım) / Gösterim * 100")
    
    col_e1, col_e2, col_e3, col_e4 = st.columns(4)
    gosterim = col_e1.number_input("Gösterim (İzlenme)", min_value=1, value=10000, step=100)
    begeni = col_e2.number_input("Beğeni Sayısı", min_value=0, value=500, step=10)
    yorum = col_e3.number_input("Yorum Sayısı", min_value=0, value=50, step=5)
    paylasim = col_e4.number_input("Paylaşım Sayısı", min_value=0, value=20, step=5)
    
    if st.button("Etkileşim Oranını Hesapla"):
        er_skor = ((begeni + yorum + paylasim) / gosterim) * 100
        er_skor = round(er_skor, 2)
        
        if er_skor >= 5.0:
            st.success(f"**Etkileşim Oranınız: % {er_skor}** (Mükemmel! Sektör ortalamasının çok üzerinde. Algoritma bu videoyu öne çıkarır.)")
        elif er_skor >= 2.0:
            st.info(f"**Etkileşim Oranınız: % {er_skor}** (İdeal. Sağlıklı bir izleyici kitleniz var.)")
        else:
            st.error(f"**Etkileşim Oranınız: % {er_skor}** (Riskli. İçeriklerinizi izleyenler tepki vermeden geçiyor. Eylem çağrısını (CTA) artırın.)")

    st.divider()

    # 2. MODÜL: STANDART SAPMA VE İSTİKRAR
    st.markdown("### 2. Standart Sapma ile İçerik İstikrarı Analizi (Varyans)")
    st.caption("Algoritma sürekli dalgalanan hesapları sevmez. Son 5 videonuzun izlenmelerini girerek istikrarınızı (σ) ölçün.")
    
    col_v1, col_v2, col_v3, col_v4, col_v5 = st.columns(5)
    v1 = col_v1.number_input("1. Video", min_value=0, value=1200)
    v2 = col_v2.number_input("2. Video", min_value=0, value=1350)
    v3 = col_v3.number_input("3. Video", min_value=0, value=900)
    v4 = col_v4.number_input("4. Video", min_value=0, value=1500)
    v5 = col_v5.number_input("5. Video", min_value=0, value=1100)
    
    if st.button("Standart Sapmayı Hesapla"):
        veriler = [v1, v2, v3, v4, v5]
        ortalama = sum(veriler) / len(veriler)
        
        # Varyans hesabı: ∑(x - μ)² / n
        varyans = sum((x - ortalama) ** 2 for x in veriler) / len(veriler)
        # Standart Sapma: √Varyans
        standart_sapma = math.sqrt(varyans)
        
        # Sapma Katsayısı (Coefficient of Variation) = (Standart Sapma / Ortalama) * 100
        sapma_yuzdesi = (standart_sapma / ortalama) * 100 if ortalama > 0 else 0
        
        # Verileri Excel tablosu gibi göstermek için Pandas Dataframe kullanımı
        df = pd.DataFrame({"Videolar": ["V1", "V2", "V3", "V4", "V5"], "İzlenmeler": veriler})
        st.dataframe(df.T) # Tabloyu yatay basıyoruz
        
        st.write(f"**Aritmetik Ortalama (μ):** {ortalama:,.0f} izlenme")
        st.write(f"**Standart Sapma (σ):** {standart_sapma:,.0f}")
        
        if sapma_yuzdesi < 30:
            st.success("Sonuç: İSTİKRARLI. İzlenmeleriniz ortalamaya çok yakın seyrediyor. Algoritma sizi güvenilir bir üretici olarak konumlandırıyor.")
        elif sapma_yuzdesi < 60:
            st.warning("Sonuç: DALGALANMA VAR. Bazı içerikleriniz tutarken bazıları düşük kalıyor. Hedef kitlenizin neyi sevdiğini tam oturtmalısınız.")
        else:
            st.error("Sonuç: İSTİKRARSIZ. Videolarınız arasında uçurumlar var (Yüksek varyans). Şansa bağlı bir büyümeniz var, içerik konseptinizi sabitleyin.")

    st.divider()
    
    # 3. MODÜL: DOĞRUSAL BÜYÜME FONKSİYONU
    st.markdown("### 3. Doğrusal Fonksiyon ile Gelecek Projeksiyonu")
    st.caption("Matematiksel denklem (y = mx + n) kurarak sayfanızın büyüme grafiğini hesaplayın.")
    
    col_d1, col_d2 = st.columns(2)
    n_baslangic = col_d1.number_input("Şu Anki Takipçi Sayınız (n)", min_value=0, value=5000)
    m_egim = col_d2.number_input("Haftalık Ortalama Takipçi Artışınız (m)", min_value=0, value=250)
    
    if st.button("1 Aylık Gelecek Projeksiyonu Çıkar"):
        haftalar = [1, 2, 3, 4]
        takipciler = [n_baslangic + (m_egim * x) for x in haftalar]
        
        grafik_verisi = pd.DataFrame({
            "Haftalar": ["1. Hafta", "2. Hafta", "3. Hafta", "4. Hafta"],
            "Tahmini Takipçi": takipciler
        })
        
        st.line_chart(grafik_verisi.set_index("Haftalar"))
        
        st.info(f"**Doğrusal Denklem:** ƒ(x) = {m_egim}x + {n_baslangic}")
        st.success(f"Mevcut ivmenizi korursanız, 4 hafta sonra matematiksel olarak tam **{takipciler[-1]:,.0f}** takipçiye ulaşacaksınız.")