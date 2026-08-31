import json
import re
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://dlstreams.st"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
        " like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Referer": f"{BASE_URL}/",
}


def obtener_eventos():
  grupos_dict = {}
  session = requests.Session()

  try:
    res = session.get(f"{BASE_URL}/", headers=HEADERS, timeout=15)
    if res.status_code == 200:
      soup = BeautifulSoup(res.text, "html.parser")

      # Buscamos cada enlace de partido dentro de su contenedor de evento
      for a in soup.find_all("a", href=re.compile(r"watch\.php\?id=")):
        # Forzar extracción del texto limpio ignorando etiquetas hijas desalineadas
        title = " ".join(a.stripped_strings)
        link = a.get("href", "")

        if not title or title.lower() == "unknown channel":
          # Intentar extraer el título del atributo alt/title si el texto falló
          title = a.get("title") or a.get("alt") or ""

        if link and len(title) > 2:
          match = re.search(r"id=(\d+)", link)
          if match:
            stream_id = match.group(1)
            player_url = f"{BASE_URL}/stream/stream-{stream_id}.php"
          else:
            player_url = (
                f"{BASE_URL}{link}" if link.startswith("/") else link
            )

          # Buscar el encabezado de categoría más cercano hacia arriba
          categoria = "Eventos en Directo ⚽"
          parent = a.find_parent(
              ["div", "table", "section"], class_=re.compile(r"cat|sport|group", re.I)
          )
          if parent:
            header = parent.find(["h2", "h3", "h4", "div", "span"], class_=re.compile(r"cat|title|header", re.I))
            if header:
              cat_text = header.get_text(strip=True)
              if len(cat_text) > 2:
                categoria = cat_text

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

          # Evitar duplicados exactos
          if not any(x["url"] == player_url for x in grupos_dict[categoria]):
            grupos_dict[categoria].append(item)

  except Exception as e:
    print(f"Error extrayendo canales: {e}")

  groups = []
  for cat_name, stations in grupos_dict.items():
    if stations:
      groups.append({"name": cat_name, "stations": stations})

  return groups


def main():
  groups = obtener_eventos()

  data = {
      "name": "DLStreams Agenda",
      "author": "Yecox",
      "groups": groups,
  }

  with open("dlstreams.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

  print(f"dlstreams.json actualizado con {len(groups)} grupos.")


if __name__ == "__main__":
  main()
