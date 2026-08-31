import json
import re
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://dlstreams.st"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like"
        " Gecko) Chrome/124.0.0.0 Mobile Safari/537.36"
    ),
    "Referer": f"{BASE_URL}/",
}

# Diccionario de clasificación por deportes
DEPORTES_MAP = {
    "Fútbol ⚽": [
        "soccer",
        "football",
        "liga",
        "champions",
        "premier",
        "laliga",
        "serie a",
        "bundesliga",
        "fútbol",
        "futsal",
        "ucl",
        "uel",
        "astro",
        "supersport",
        "bein",
    ],
    "Baloncesto 🏀": [
        "basketball",
        "nba",
        "euroleague",
        "acb",
        "wnba",
        "basket",
    ],
    "Tenis 🎾": [
        "tennis",
        "atp",
        "wta",
        "us open",
        "wimbledon",
        "roland garros",
    ],
    "Motor 🏎️": [
        "f1",
        "formula 1",
        "motogp",
        "nascar",
        "indycar",
        "rally",
        "wrc",
        "motorsport",
    ],
    "Combate / MMA 🥊": ["ufc", "boxing", "wwe", "mma", "boxeo", "aew"],
    "Ciclismo 🚴": ["cycling", "ciclismo", "tour", "vuelta", "giro"],
    "Béisbol ⚾": ["baseball", "mlb"],
}


def clasificar(titulo):
  titulo_low = titulo.lower()
  for dep, kw_list in DEPORTES_MAP.items():
    if any(kw in titulo_low for kw in kw_list):
      return dep
  return "Canales 24/7 y Otros 📺"


def main():
  session = requests.Session()
  dict_grupos = {}

  # 1. Obtener canales masivos mediante la estructura de canales 24/7 / streaming directo
  try:
    res = session.get(f"{BASE_URL}/", headers=HEADERS, timeout=15)
    if res.status_code == 200:
      soup = BeautifulSoup(res.text, "html.parser")

      # Buscamos todos los enlaces de watch.php o stream directos
      for a in soup.find_all("a", href=True):
        href = a.get("href", "")
        if "watch.php?id=" in href or "stream-" in href:
          title = a.get_text(strip=True)
          if not title or len(title) <= 1:
            continue

          match = re.search(r"id=(\d+)", href)
          if match:
            stream_id = match.group(1)
            player_url = f"{BASE_URL}/stream/stream-{stream_id}.php"
          else:
            match_stream = re.search(r"stream-(\d+)", href)
            if match_stream:
              stream_id = match_stream.group(1)
              player_url = f"{BASE_URL}/stream/stream-{stream_id}.php"
            else:
              player_url = (
                  f"{BASE_URL}{href}" if href.startswith("/") else href
              )

          categoria = clasificar(title)

          item = {
              "name": title,
              "image": "",
              "url": player_url,
              "link": player_url,
              "isEmbed": True,
              "embed": True,
              "referer": f"{BASE_URL}/",
              "userAgent": HEADERS["User-Agent"],
              "headers": {
                  "Referer": f"{BASE_URL}/",
                  "User-Agent": HEADERS["User-Agent"],
              },
          }

          if categoria not in dict_grupos:
            dict_grupos[categoria] = []

          # Evitar duplicados exactos por URL
          if not any(x["url"] == player_url for x in dict_grupos[categoria]):
            dict_grupos[categoria].append(item)
  except Exception as e:
    print(f"Error extrayendo canales: {e}")

  # Construir orden de grupos
  groups = []
  for cat in DEPORTES_MAP.keys():
    if cat in dict_grupos:
      groups.append({"name": cat, "stations": dict_grupos[cat]})

  if "Canales 24/7 y Otros 📺" in dict_grupos:
    groups.append({
        "name": "Canales 24/7 y Otros 📺",
        "stations": dict_grupos["Canales 24/7 y Otros 📺"],
    })

  data = {"name": "", "author": "Yecox", "groups": groups}

  with open("dlstreams.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

  print(
      "Lista regenerada con éxito integrando todos los canales disponibles."
  )


if __name__ == "__main__":
  main()
