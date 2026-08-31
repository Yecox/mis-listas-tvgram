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

# Reglas de clasificación por deporte
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
  return "Otros Deportes 📺"


def main():
  session = requests.Session()
  dict_grupos = {}

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
          dict_grupos[categoria].append(item)
  except Exception as e:
    print(f"Error scraping: {e}")

  # Construir grupos para TVGram
  groups = []
  for cat in DEPORTES_MAP.keys():
    if cat in dict_grupos:
      groups.append({"name": cat, "stations": dict_grupos[cat]})

  if "Otros Deportes 📺" in dict_grupos:
    groups.append(
        {"name": "Otros Deportes 📺", "stations": dict_grupos["Otros Deportes 📺"]}
    )

  data = {"name": "", "author": "Yecox", "groups": groups}

  with open("dlstreams.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

  print(f"Lista generada exitosamente con {len(groups)} secciones.")


if __name__ == "__main__":
  main()
