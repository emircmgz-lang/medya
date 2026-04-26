import streamlit as st
import os

# 1. Sayfa ayarları her şeyden önce gelmeli
st.set_page_config(page_title="Viral Analiz", layout="centered")
st.title("Viral Analiz Aracı 🚀")

# 2. Kütüphane yükleme kontrolü
try:
    import google.generativeai as genai
except ModuleNotFoundError:
    st.error("🚨 HATA: 'google-generativeai' kütüphanesi bulunamadı! requirements.txt dosyanızı kontrol edin.")
    st.stop()

# 3. API Anahtarı kontrolü
# Streamlit Cloud'da st.secrets kullanmak daha güvenlidir
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except (KeyError, FileNotFoundError):
    API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    st.error("🚨 HATA: API Anahtarı bulunamadı! Lütfen Streamlit Cloud Secrets bölümüne eklediğinizden emin olun.")
    st.stop()
else:
    st.success("✅ Sistem Hazır! API Anahtarı ve Kütüphaneler yüklendi.")

# --- Buradan sonrasına eski kodunuzun geri kalanını (platform seçimi, butonlar vs.) ekleyebilirsiniz ---