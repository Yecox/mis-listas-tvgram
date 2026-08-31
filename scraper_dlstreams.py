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


def obtener_eventos():
  stations = []
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
            # URL limpia del reproductor sin la interfaz contenedora de la web
            player_url = f"{BASE_URL}/stream/stream-{stream_id}.php"
          else:
            player_url = (
                f"{BASE_URL}{link}" if link.startswith("/") else link
            )

          stations.append({
              "name": f"⚽ {title}",
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
          })
  except Exception as e:
    print(f"Error procesando scraping: {e}")

  return stations


def main():
  stations = obtener_eventos()

  data = {
      "name": "DLStreams Directos",
      "author": "Yecox",
      "groups": [{"name": "DLStreams Events ⚽", "stations": stations}],
  }

  with open("dlstreams.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

  print(f"dlstreams.json generado con {len(stations)} reproducciones.")


if __name__ == "__main__":
  main()
