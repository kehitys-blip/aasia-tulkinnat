# Aasia-Tulkinnat Automatiikka

Automatisoitu Asian uutiset-analyysijärjestelmä: NewsAPI → Claude → Sähköposti.

## Tiedostot

- `main.py` — Flask-sovellus + analyysi-logiikka
- `requirements.txt` — Python-paketit
- `.env.example` — Ympäristömuuttujien malli

## Render.com Setup (ilman GitHub:ia)

### 1. Lataa tiedostot
```
aasia-tulkinnat/
├── main.py
├── requirements.txt
└── .env.example
```

### 2. Pakkaa ZIP:ksi
Valitse kaikki kolme tiedostoa → Pakkaa → `aasia-tulkinnat.zip`

### 3. Render.com:iin
- Avaa https://dashboard.render.com
- **New +** → **Web Service**
- Valitse **"Public Git repository"** → **"Paste your repository URL"**
  - *Tai:* Klikkaa **"Upload files"** → lataa ZIP

### 4. Konfiguraatio
**Settings:**
- Build Command: `pip install -r requirements.txt`
- Start Command: `python main.py`
- Instance Type: **Free**

**Environment Variables** (Settings → Environment):
```
NEWSAPI_KEY = [tuodaan NewsAPI:sta]
ANTHROPIC_API_KEY = [tuodaan Anthropic Consolesta]
TELEGRAM_TOKEN = [tuodaan @BotFather:lta]
TELEGRAM_CHAT_ID = [Telegram-kanavasi ID]
```

### 5. Deploy
Klikkaa **Deploy** → odota ~2–3 min

---

## Telegram Setup

### 1. Luo Telegram-botti
1. Avaa Telegram ja hae **@BotFather**
2. Lähetä komento: `/newbot`
3. Anna botin nimi ja käyttäjänimi
4. BotFather antaa **API Token** → kopioi se → `TELEGRAM_TOKEN`

### 2. Hae Chat ID
1. Lisää botti omaan Telegram-kanavallesi tai yksityisviestiin
2. Lähetä botin testisanoma: `/start`
3. Avaa selaimen osoiteriville:
```
https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates
```
4. Etsi `"chat":{"id":123456789}` → kopioi numero → `TELEGRAM_CHAT_ID`

### 3. Testaa
Testaa API-yhteyttä curl:llä:
```bash
curl -X POST https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage \
  -d "chat_id={TELEGRAM_CHAT_ID}" \
  -d "text=Test: Aasia-Tulkinnat toimii!"
```

---

## Cron-job (Maanantai 07:00 UTC+2)

### Vaihtoehto A: EasyCron (HELPOIN)
1. Avaa https://easycron.com
2. **New Cron Job**
3. URL: `https://your-render-app.onrender.com/run`
4. Cron Expression: `0 5 * * 1` (maanantai 05:00 UTC = 07:00 UTC+2)
5. Save

### Vaihtoehto B: cron-job.org
1. Avaa https://cron-job.org/en/
2. **Create Cronjob**
3. URL: `https://your-render-app.onrender.com/run`
4. Execution time: Every monday at 05:00 UTC

---

## Lokaali testaus ennen Render.com:ia

```bash
# 1. Kloonaa tai lataa tiedostot
# 2. Luo .env-tiedosto (kopioi .env.example, lisää Telegram-avaimet)
# 3. Asenna riippuvuudet
pip install -r requirements.txt

# 4. Testaa API-yhteyttä (ennen ajoa)
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(f'TELEGRAM_TOKEN: {os.getenv(\"TELEGRAM_TOKEN\")}'); print(f'TELEGRAM_CHAT_ID: {os.getenv(\"TELEGRAM_CHAT_ID\")}')"

# 5. Käynnistä
python main.py
```

Tai käytä HTTP-endpointia:
```bash
# Flask-käynnistys
export FLASK_APP=main.py
flask run

# Sitten selaimessa tai curl:llä: http://localhost:5000/run
# Tai: curl http://localhost:5000/health
```

---

## Huomioita

- **Free Tier:** Render.com sammuttaa sovelluksen inaktiivisuuden jälkeen. Cron-kutsu aktivoi sen.
- **Fetch:** Haku on aina englanninkielinen. Analyysi on suomalainen.
- **Email:** HTML-muoto, joka näkyy hyvin puhelimella ja tietokoneella.

---

## Troubleshooting

**"No such file or directory: main.py"**
- Varmista, että main.py on ZIP:n juuressa (ei alikansioissa)

**"NEWSAPI_KEY not found"**
- Tarkista Environment Variables — kirjoitusasu on case-sensitive

**"Telegram-virhe: 401"**
- Tarkista TELEGRAM_TOKEN (copypaste BotFather:lta)

**"Telegram-virhe: 400"**
- Tarkista TELEGRAM_CHAT_ID (pitää olla numero, ei teksti)

**Viestiä ei tule Telegramissa**
- Testaa `/health` endpointia: `https://your-app.onrender.com/health`
- Tarkista Render.com:in logit (Logs-välilehti)
- Varmista, että botti on lisätty kanavallesi/chatissa

---

## Seuraavaksi

Kun automatiikka toimii, voit:
- Muokata Claude-promptia `analyze_with_claude()`-funktiossa
- Lisätä paikallisen suodatuksen (Ollama/LM Studio)
- Laajentaa useammaksi analyysiksi viikossa
