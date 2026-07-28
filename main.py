import os
import requests
from datetime import datetime
import anthropic
from flask import Flask

app = Flask(__name__)

# Environment variables
NEWSAPI_KEY = os.environ.get("NEWSAPI_KEY")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def fetch_news():
    """Hae Aasian uutiset NewsAPI:sta"""
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": "China OR Vietnam OR Japan OR Thailand OR Korea OR Indonesia",
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 10,
        "apiKey": NEWSAPI_KEY
    }
    
    response = requests.get(url, params=params, timeout=10)
    articles = response.json().get("articles", [])
    return articles

def analyze_with_claude(articles):
    """Analysoi uutiset Claude:lla"""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
    articles_text = "\n".join([
        f"- {a['title']}\n  Lähde: {a['source']['name']}\n  {a['description'] or '(ei kuvausta)'}"
        for a in articles[:5]
    ])
    
    message = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=1500,
        messages=[{
            "role": "user",
            "content": f"""Analysoi nämä viikon Aasian uutiset kriittisesti:

{articles_text}

Anna:
1. **Pääkysymys** — mikä on todella merkittävää?
2. **Konteksti** — historiallinen ja geopoliittinen tausta
3. **Vastakohta** — kenen näkökulmasta argumentit eroaisivat?
4. **Episteeminen kritiikki** — mitä emme tiedä? Mitkä lähteet puuttuvat?
5. **Seuraavat merkit** — mitä seurata ensi viikolla?

Pidä analyysisi tiiviinä mutta terävänä (max 500 sanaa)."""
        }]
    )
    
    return message.content[0].text

def send_telegram(analysis):
    """Lähetä analyysi Telegramissa"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    message_text = f"""🌏 Aasia-Tulkinnat — Viikon analyysi

📅 {datetime.now().strftime('%Y-W%V')} ({datetime.now().strftime('%Y-%m-%d %H:%M UTC+2')})

{analysis}

---
Automatiikka: Aasia-Tulkinnat v1.0"""
    
    try:
        response = requests.post(
            url,
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message_text,
                "parse_mode": "Markdown"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"✓ Telegram-viesti lähetetty")
            return True
        else:
            print(f"❌ Telegram-virhe: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Telegram-lähetys epäonnistui: {e}")
        return False

def run_analysis():
    """Pääfunktio"""
    print(f"[{datetime.now()}] Aasia-Tulkinnat Automatiikka käynnistyy...")
    
    try:
        print("→ Haetaan uutisia...")
        articles = fetch_news()
        
        if not articles:
            print("⚠️ Ei uutisia löytynyt")
            return "Ei uutisia", 204
        
        print(f"→ {len(articles)} uutista löytyi. Analyysissa...")
        analysis = analyze_with_claude(articles)
        
        print("→ Lähetetään Telegramissa...")
        if send_telegram(analysis):
            print("✓ Automatiikka valmis!")
            return "✓ Analyysi valmis ja lähetetty Telegramissa", 200
        else:
            return "⚠️ Analyysi valmis, mutta Telegram-lähetys epäonnistui", 500
        
    except Exception as e:
        print(f"❌ Virhe: {e}")
        return f"❌ Virhe: {e}", 500

@app.route('/run', methods=['GET', 'POST'])
def trigger_analysis():
    """HTTP-endpoint cron-jobille"""
    result, status = run_analysis()
    return result, status

@app.route('/health', methods=['GET'])
def health_check():
    """Health check Render.com:ille"""
    return "✓ OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
