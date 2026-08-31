import json
import re
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://dlstreams.st"

# -------------------------------------------------------------------
# SI TIENES API KEY: Pon tu clave entre las comillas (ej: API_KEY = "abc123xyz")
# SI NO TIENEN API KEY: Déjala vacía ("") y usará scraping gratuito.
# -------------------------------------------------------------------
API_KEY = ""

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
        " like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Referer": f"{BASE_URL}/",
}


def obtener_canales_api(key):
  """Obtiene los canales desde la API oficial de DaddyLive/DLStreams usando una API Key."""
  stations = []
  url = f"{BASE_URL}/daddyapi.php?key={key}&endpoint=channels"
  try:
    res = requests.get(url, headers=HEADERS, timeout=15)
    if res.status_code == 200:
      channels = res.json()
      for ch in channels:
        ch_name = ch.get("channel_name", "")
        ch_id = ch.get("channel_id", "")
        logo = ch.get("logo_url", "")

        if logo and not logo.startswith("http"):
          logo = f"{BASE_URL}/{logo}"

        if ch_id:
          stream_url = f"{BASE_URL}/stream/stream-{ch_id}.php"
          stations.append({
              "name": ch_name,
              "image": logo,
              "url": stream_url,
              "link": stream_url,
              "isEmbed": "true",
              "referer": f"{BASE_URL}/",
          })
  except Exception as e:
    print(f"Error consultando API de DLStreams: {e}")
  return stations


def obtener_eventos_scraping():
  """Extrae los eventos y transmisiones en vivo mediante web scraping (Gratuito)."""
  event_stations = []
  session = requests.Session()

  try:
    res = session.get(f"{BASE_URL}/", headers=HEADERS, timeout=15)
    if res.status_code == 200:
      soup = BeautifulSoup(res.text, "html.parser")

      for a in soup.find_all("a", href=re.compile(r"watch\.php\?id=")):
        title = a.get_text(strip=True)
        link = a.get("href", "")

        if link and len(title) > 2:
          # Extraer el ID del canal (ejemplo: watch.php?id=491 -> 491)
          match = re.search(r"id=(\d+)", link)
          if match:
            stream_id = match.group(1)
            player_url = f"{BASE_URL}/stream/stream-{stream_id}.php"
          else:
            player_url = (
                f"{BASE_URL}{link}" if link.startswith("/") else link
            )

          event_stations.append({
              "name": f"⚽ {title}",
              "image": "",
              "url": player_url,
              "link": player_url,
              "isEmbed": "true",
              "referer": f"{BASE_URL}/",
          })
  except Exception as e:
    print(f"Error en scraping DLStreams: {e}")

  return event_stations


def main():
  groups = []

  if API_KEY.strip():
    print("Conectando con la API Oficial de DLStreams...")
    api_stations = obtener_canales_api(API_KEY.strip())
    if api_stations:
      groups.append(
          {"name": "DLStreams (API Oficial) 📺", "stations": api_stations}
      )
  else:
    print("Ejecutando modo Scraping Gratuito...")
    event_stations = obtener_eventos_scraping()
    if event_stations:
      groups.append(
          {"name": "DLStreams - Eventos en Directo ⚽", "stations": event_stations}
      )

  data = {
      "name": "DLStreams",
      "author": "Yecox",
      "groups": groups,
  }

  with open("dlstreams.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

  print("dlstreams.json actualizado correctamente.")


if __name__ == "__main__":
  main()
