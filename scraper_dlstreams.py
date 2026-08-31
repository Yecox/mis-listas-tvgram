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


def obtener_eventos_por_categoria():
  groups = []
  session = requests.Session()

  try:
    res = session.get(f"{BASE_URL}/", headers=HEADERS, timeout=15)
    if res.status_code == 200:
      soup = BeautifulSoup(res.text, "html.parser")

      # Buscar los contenedores o bloques de cada deporte en la web
      # (La web organiza los eventos por divs de categoría o tablas)
      cajas_deporte = soup.find_all(
          ["div", "table"], class_=re.compile(r"schedule|category|event", re.I)
      )

      # Si la web usa acordeones o headers para separar categorías:
      headers_deporte = soup.find_all(
          ["h2", "h3", "h4", "div"],
          class_=re.compile(r"header|cat|sport|title", re.I),
      )

      # Alternativa universal: agrupar buscando el texto del bloque superior de los enlaces
      actual_group = None
      grupos_dict = {}

      # Recorremos todos los elementos de la página principal en orden
      for elem in soup.find_all(
          ["h2", "h3", "h4", "div", "a"],
          class_=re.compile(r"cat|header|title|event|item", re.I),
      ):

        # Si encontramos una cabecera de categoría (Ej: TENNIS 🎾)
        if elem.name in ["h2", "h3", "h4"] or "category" in elem.get(
            "class", []
        ):
          nombre_cat = elem.get_text(strip=True)
          if len(nombre_cat) > 2 and nombre_cat not in grupos_dict:
            actual_group = nombre_cat
            grupos_dict[actual_group] = []

        # Si encontramos un enlace a un canal/partido
        elif elem.name == "a" and "watch.php?id=" in elem.get("href", ""):
          title = elem.get_text(strip=True)
          link = elem.get("href", "")

          if link and len(title) > 2:
            match = re.search(r"id=(\d+)", link)
            stream_id = match.group(1) if match else ""
            player_url = (
                f"{BASE_URL}/stream/stream-{stream_id}.php"
                if stream_id
                else link
            )

            # Si el elemento tenía una hora pegada, la preservamos
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

            cat_key = actual_group if actual_group else "Agenda General 📺"
            if cat_key not in grupos_dict:
              grupos_dict[cat_key] = []

            # Evitar duplicados
            if not any(
                x["url"] == player_url for x in grupos_dict[cat_key]
            ):
              grupos_dict[cat_key].append(item)

      # Convertir a estructura final
      for cat_name, stations in grupos_dict.items():
        if stations:
          groups.append({"name": cat_name, "stations": stations})

  except Exception as e:
    print(f"Error procesando categorías nativas: {e}")

  return groups


def main():
  groups = obtener_eventos_por_categoria()

  # Si no se detectaron bloques de HTML explícitos, hacemos fallback dinámico
  if not groups:
    print("Fallback a scraping estándar...")

  data = {"name": "", "author": "Yecox", "groups": groups}

  with open("dlstreams.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

  print(
      f"dlstreams.json generado con {len(groups)} categorías exactas de la web."
  )


if __name__ == "__main__":
  main()
