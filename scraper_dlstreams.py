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

# Diccionario para clasificar deportes por palabras clave y asignar emojis
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
        "australian open",
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
    "Fútbol Americano 🏈": ["nfl", "american football"],
    "Hockey 🏒": ["hockey", "nhl"],
    "Rugby 🏉": ["rugby", "six nations"],
}


def clasificar_deporte(titulo):
  """Detecta la categoría analizando el nombre del evento."""
  titulo_lower = titulo.lower()
  for deporte, keywords in DEPORTES_MAP.items():
    for kw in keywords:
      if kw in titulo_lower:
        return deporte
  return "Otros Deportes 📺"


def obtener_eventos_organizados():
  grupos_dict = {}
  session = requests.Session()

  try:
    res = session.get(f"{BASE_URL}/", headers=HEADERS, timeout=15)
    if res.status_code == 200:
      soup = BeautifulSoup(res.text, "html.parser")

      for a in soup.find_all("a", href=re.compile(r"watch\.php\?id=")):
        title = a.get_text(strip=True)
        link = a.get("href", "")

        if link and len(title) > 2:
          match = re.search(r"id=(\d+)", link)
          if match:
            stream_id = match.group(1)
            player_url = f"{BASE_URL}/stream/stream-{stream_id}.php"
          else:
            player_url = (
                f"{BASE_URL}{link}" if link.startswith("/") else link
            )

          categoria = clasificar_deporte(title)

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

          if categoria not in grupos_dict:
            grupos_dict[categoria] = []
          grupos_dict[categoria].append(item)
  except Exception as e:
    print(f"Error durante el scraping: {e}")

  groups = []
  for cat_name, stations in grupos_dict.items():
    groups.append({"name": cat_name, "stations": stations})

  return groups


def main():
  groups = obtener_eventos_organizados()

  data = {"name": "DLStreams por Deportes", "author": "Yecox", "groups": groups}

  with open("dlstreams.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

  print(f"dlstreams.json generado con {len(groups)} categorías.")


if __name__ == "__main__":
  main()
