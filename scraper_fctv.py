import json
import re
import requests
from bs4 import BeautifulSoup

URL = "https://riverlanes.site/fctv33/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    "Referer": "https://riverlanes.site/",
}


def main():
    data = {"categories": [{"name": "Riverlanes / FCTV ⚽", "items": []}]}

    try:
        session = requests.Session()
        res = session.get(URL, headers=HEADERS, timeout=15)

        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")

            # 1. Buscar enlaces directos
            for a in soup.find_all("a"):
                texto = a.text.strip()
                link = a.get("href", "")
                if (
                    link
                    and not link.startswith("#")
                    and not link.startswith("javascript:")
                ):
                    if link.startswith("/"):
                        link = f"https://riverlanes.site{link}"
                    if len(texto) > 1:
                        data["categories"][0]["items"].append({
                            "name": f"🔴 {texto}",
                            "title": texto,
                            "channel": "FCTV 33",
                            "url": link,
                            "poster": "",
                            "headers": {
                                "User-Agent": HEADERS["User-Agent"],
                                "Referer": "https://riverlanes.site/",
                            },
                        })

            # 2. Si la web usa reproductores embebidos (iframes)
            if not data["categories"][0]["items"]:
                for i, iframe in enumerate(soup.find_all("iframe"), 1):
                    src = iframe.get("src", "")
                    if src:
                        if src.startswith("/"):
                            src = f"https://riverlanes.site{src}"
                        data["categories"][0]["items"].append({
                            "name": f"🔴 Canal Directo FCTV #{i}",
                            "title": f"FCTV Stream {i}",
                            "channel": "FCTV 33",
                            "url": src,
                            "poster": "",
                            "headers": {
                                "User-Agent": HEADERS["User-Agent"],
                                "Referer": "https://riverlanes.site/",
                            },
                        })

    except Exception as e:
        print(f"Error procesando FCTV: {e}")

    # Guardar siempre el archivo JSON
    with open("fctv.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("fctv.json generado exitosamente.")


if __name__ == "__main__":
    main()
