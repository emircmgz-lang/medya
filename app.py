import google.generativeai as genai
import os

# ai_analiz fonksiyonunu aşağıdaki ile tamamen değiştirebilirsiniz:
def ai_analiz(text):
    try:
        API_KEY = os.environ.get("GEMINI_API_KEY")
        if not API_KEY:
            return "AI Hata: API Anahtarı bulunamadı."
            
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        Bu içerik fikrini analiz et:
        {text}

        Şu formatta cevap ver:
        Viral Skor: (0-100)
        İzlenme Potansiyeli: (0-100)
        Kısa Yorum:
        Hashtagler: #...
        """
        
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        return f"AI Exception: {str(e)}"