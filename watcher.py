# watcher.py
import json, os, requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
STATE = "state.json"
PARAULES = ("lloguer", "alquiler", "alquileres", "lloguers")

def notify(msg):
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                  data={"chat_id": CHAT_ID, "text": msg}, timeout=30)

def links(url):
    r = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    tots = {urljoin(url, a["href"]).split("#")[0] for a in soup.find_all("a", href=True)}
    return {l for l in tots if any(p in l.lower() for p in PARAULES)}

state = json.load(open(STATE)) if os.path.exists(STATE) else {}
urls = [u.strip() for u in open("urls.txt") if u.strip() and not u.startswith("#")]

for url in urls:
    try:
        now = links(url)
    except Exception as e:
        print("Error", url, e)
        continue
    old = set(state.get(url, []))
    if old:  # la primera vegada només guarda, no avisa
        for l in sorted(now - old):
            notify(f"Nou a {url}\n{l}")
    state[url] = sorted(now)

json.dump(state, open(STATE, "w"), indent=1)