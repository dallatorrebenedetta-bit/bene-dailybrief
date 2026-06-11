import json
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

NEWS_FEEDS = [
    ("Top Story", "Reuters", "https://news.google.com/rss/search?q=site:reuters.com+markets+economy+central+banks&hl=it&gl=IT&ceid=IT:it"),
    ("AI & Tecnologia", "Financial Times", "https://news.google.com/rss/search?q=site:ft.com+AI+semiconductors+technology&hl=it&gl=IT&ceid=IT:it"),
    ("Finanza", "ECB / Fed", "https://news.google.com/rss/search?q=ECB+Federal+Reserve+tassi+inflazione&hl=it&gl=IT&ceid=IT:it"),
    ("Politica & Geopolitica", "Reuters", "https://news.google.com/rss/search?q=site:reuters.com+geopolitics+Ukraine+China+Middle+East&hl=it&gl=IT&ceid=IT:it"),
    ("Business", "Wall Street Journal", "https://news.google.com/rss/search?q=site:wsj.com+business+earnings+companies&hl=it&gl=IT&ceid=IT:it"),
    ("Approfondimento", "The Economist", "https://news.google.com/rss/search?q=site:economist.com+economy+technology+markets&hl=it&gl=IT&ceid=IT:it")
]

MARKET_TICKERS = [
    ("S&P 500", "%5EGSPC"),
    ("Nasdaq", "%5EIXIC"),
    ("EUR/USD", "EURUSD%3DX"),
    ("Oro", "GC%3DF"),
    ("Brent", "BZ%3DF"),
    ("Bitcoin", "BTC-USD"),
    ("VIX", "%5EVIX")
]

def get_url(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as response:
        return response.read()

def fetch_feed(url):
    try:
        data = get_url(url)
        root = ET.fromstring(data)
        items = root.findall(".//item")
        results = []

        for item in items[:5]:
            title = item.findtext("title", default="Titolo non disponibile")
            link = item.findtext("link", default="#")
            results.append({"title": title, "url": link})

        return results
    except Exception:
        return []

def clean_title(title):
    title = title.replace(" - Reuters", "")
    title = title.replace(" - Financial Times", "")
    title = title.replace(" - Bloomberg", "")
    title = title.replace(" - WSJ", "")
    title = title.replace(" - The Economist", "")
    return title.strip()

def make_story(category, source, url, fallback):
    stories = fetch_feed(url)
    selected = stories[0] if stories else {"title": fallback, "url": "#"}

    return {
        "title": clean_title(selected["title"]),
        "category": category,
        "source": source,
        "summary": "Questa notizia è stata selezionata automaticamente da fonti pubbliche monitorate. È utile per capire il contesto della giornata tra mercati, economia, tecnologia e geopolitica.",
        "why": "È rilevante perché può influenzare aspettative degli investitori, sentiment di mercato, costo del capitale o percezione del rischio globale.",
        "url": selected["url"]
    }

def fetch_market(symbol):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=2d&interval=1d"
        data = json.loads(get_url(url).decode("utf-8"))

        result = data["chart"]["result"][0]
        meta = result["meta"]
        price = meta.get("regularMarketPrice")

        previous = meta.get("chartPreviousClose")
        if previous is None:
            previous = meta.get("previousClose")

        if price is None or previous is None:
            raise ValueError("Missing price data")

        change_pct = ((price - previous) / previous) * 100

        return price, change_pct

    except Exception:
        return None, None

def format_price(name, price):
    if price is None:
        return "n.d."

    if name in ["EUR/USD"]:
        return f"{price:.4f}"

    if name in ["VIX"]:
        return f"{price:.2f}"

    if name in ["Bitcoin"]:
        return f"${price:,.0f}"

    if name in ["Oro", "Brent"]:
        return f"${price:,.2f}"

    return f"{price:,.0f}"

def build_markets():
    markets = []

    for name, symbol in MARKET_TICKERS:
        price, change_pct = fetch_market(symbol)

        if change_pct is None:
            detail = "n.d."
        else:
            sign = "+" if change_pct >= 0 else ""
            detail = f"{sign}{change_pct:.2f}%"

        markets.append({
            "name": name,
            "value": format_price(name, price),
            "detail": detail
        })

    return markets

today = datetime.utcnow().strftime("%d %B %Y")

top_1 = make_story(*NEWS_FEEDS[0], fallback="I mercati seguono banche centrali e dati macro")
top_2 = make_story(*NEWS_FEEDS[1], fallback="L’intelligenza artificiale resta al centro degli investimenti")

brief = {
    "date": today,
    "theme": {
        "title": "Mercati concentrati su tassi, AI e rischio geopolitico.",
        "text": "Il brief di oggi è generato automaticamente da fonti pubbliche selezionate. Il focus resta su banche centrali, mercati, tecnologia, geopolitica e grandi aziende."
    },
    "topStories": [top_1, top_2],
    "numbers": build_markets(),
    "ai": make_story(*NEWS_FEEDS[1], fallback="L’AI resta un tema centrale per tecnologia e mercati"),
    "finance": make_story(*NEWS_FEEDS[2], fallback="Banche centrali caute su inflazione e tassi"),
    "geopolitics": make_story(*NEWS_FEEDS[3], fallback="La geopolitica resta una fonte di incertezza per i mercati"),
    "business": make_story(*NEWS_FEEDS[4], fallback="Le aziende adattano le strategie tra AI, tassi e supply chain"),
    "deepRead": make_story(*NEWS_FEEDS[5], fallback="Un approfondimento utile per capire il quadro macro")
}

output_path = Path("data/brief.json")
output_path.parent.mkdir(exist_ok=True)

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(brief, f, ensure_ascii=False, indent=2)

print("Daily brief generated with live market data.")
