import json
import re
import requests
from bs4 import BeautifulSoup

URL = "https://livetv.sx/esx/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    "Referer": "https://livetv.sx/",
}


def main():
    data = {"categories": [{"name": "LiveTV SX 📺", "items": []}]}

    try:
        session = requests.Session()
        res = session.get(URL, headers=HEADERS, timeout=15)

        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")

            # Buscar todos los eventos deportivos en directo
            event_links = soup.find_all("a", href=re.compile(r"/eventinfo/"))
            seen = set()

            for a in event_links:
                title = a.text.strip()
                link = a.get("href", "")

                if link and link not in seen and len(title) > 2:
                    seen.add(link)
                    if link.startswith("/"):
                        link = f"https://livetv.sx{link}"

                    data["categories"][0]["items"].append({
                        "name": f"⚽ {title}",
                        "title": title,
                        "channel": "LiveTV",
                        "url": link,
                        "poster": "",
                        "headers": {
                            "User-Agent": HEADERS["User-Agent"],
                            "Referer": "https://livetv.sx/",
                        },
                    })

    except Exception as e:
        print(f"Error procesando LiveTV: {e}")

    # Guardar siempre el archivo JSON
    with open("livetv.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("livetv.json generado exitosamente.")


if __name__ == "__main__":
    main()
