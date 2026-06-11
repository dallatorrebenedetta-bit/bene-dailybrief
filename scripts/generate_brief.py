import json
import random
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

FEEDS = [
    {
        "category": "Top Story",
        "source": "Reuters",
        "url": "https://news.google.com/rss/search?q=site:reuters.com+markets+OR+economy+OR+central+banks&hl=en-US&gl=US&ceid=US:en"
    },
    {
        "category": "AI & Technology",
        "source": "Financial Times",
        "url": "https://news.google.com/rss/search?q=site:ft.com+AI+OR+semiconductors+OR+technology&hl=en-US&gl=US&ceid=US:en"
    },
    {
        "category": "Finance",
        "source": "ECB / Fed",
        "url": "https://news.google.com/rss/search?q=ECB+OR+Federal+Reserve+rates+inflation&hl=en-US&gl=US&ceid=US:en"
    },
    {
        "category": "Politics & Geopolitics",
        "source": "Reuters",
        "url": "https://news.google.com/rss/search?q=site:reuters.com+geopolitics+OR+Ukraine+OR+China+OR+Middle+East&hl=en-US&gl=US&ceid=US:en"
    },
    {
        "category": "Business",
        "source": "Wall Street Journal",
        "url": "https://news.google.com/rss/search?q=site:wsj.com+business+earnings+companies&hl=en-US&gl=US&ceid=US:en"
    },
    {
        "category": "Deep Read",
        "source": "The Economist",
        "url": "https://news.google.com/rss/search?q=site:economist.com+economy+technology+markets&hl=en-US&gl=US&ceid=US:en"
    }
]

MARKETS = [
    {"name": "S&P 500", "value": "Market data", "detail": "Check live"},
    {"name": "Nasdaq", "value": "Market data", "detail": "Check live"},
    {"name": "EUR/USD", "value": "FX", "detail": "Check live"},
    {"name": "Gold", "value": "Commodities", "detail": "Check live"},
    {"name": "Brent Oil", "value": "Energy", "detail": "Check live"},
    {"name": "Bitcoin", "value": "Crypto", "detail": "Check live"},
    {"name": "VIX", "value": "Volatility", "detail": "Check live"}
]

def fetch_feed(url):
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            data = response.read()
        root = ET.fromstring(data)
        items = root.findall(".//item")

        stories = []
        for item in items[:5]:
            title = item.findtext("title", default="No title")
            link = item.findtext("link", default="#")
            stories.append({"title": title, "url": link})

        return stories
    except Exception:
        return []

def make_story(feed, fallback_title):
    stories = fetch_feed(feed["url"])
    selected = stories[0] if stories else {"title": fallback_title, "url": "#"}

    return {
        "title": selected["title"],
        "category": feed["category"],
        "source": feed["source"],
        "summary": "Questa notizia è stata selezionata automaticamente da una fonte ritenuta rilevante. Va letta come segnale della giornata per capire il contesto macro, finanziario o tecnologico.",
        "why": "È rilevante perché può influenzare sentiment di mercato, decisioni degli investitori o aspettative su crescita, tassi e rischio globale.",
        "url": selected["url"]
    }

today = datetime.utcnow().strftime("%d %B %Y")

top_story_1 = make_story(FEEDS[0], "Global markets watch central banks and macro risk")
top_story_2 = make_story(FEEDS[1], "AI investment remains a key market theme")

brief = {
    "date": today,
    "theme": {
        "title": "Markets are watching rates, AI investment and geopolitical risk.",
        "text": "Il brief di oggi è generato automaticamente da fonti pubbliche selezionate. Il focus resta su mercati, banche centrali, geopolitica, tecnologia e grandi aziende."
    },
    "topStories": [top_story_1, top_story_2],
    "numbers": MARKETS,
    "ai": make_story(FEEDS[1], "AI infrastructure remains a key technology theme"),
    "finance": make_story(FEEDS[2], "Central banks remain cautious on inflation and rates"),
    "geopolitics": make_story(FEEDS[3], "Geopolitical tensions remain a source of uncertainty"),
    "business": make_story(FEEDS[4], "Companies adapt strategy around AI, rates and supply chains"),
    "deepRead": make_story(FEEDS[5], "One article worth reading today")
}

output_path = Path("data/brief.json")
output_path.parent.mkdir(exist_ok=True)

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(brief, f, ensure_ascii=False, indent=2)

print("Daily brief generated successfully.")
