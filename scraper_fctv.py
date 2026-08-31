import json
import requests
from bs4 import BeautifulSoup

URLS = ["https://riverlanes.site/fctv33/", "https://riverlanes.site/"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    "Referer": "https://riverlanes.site/",
}


def main():
    data = {"categories": [{"name": "Riverlanes / FCTV ⚽", "items": []}]}

    items = []
    seen_urls = set()
    session = requests.Session()

    for url in URLS:
        try:
            res = session.get(url, headers=HEADERS, timeout=15)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")

                # 1. Extraer enlaces y botones con texto
                for a in soup.find_all("a"):
                    texto = a.get_text(strip=True)
                    link = a.get("href", "")

                    if (
                        link
                        and not link.startswith("#")
                        and not link.startswith("javascript:")
                    ):
                        if link.startswith("/"):
                            link = f"https://riverlanes.site{link}"

                        if link not in seen_urls and len(texto) > 2:
                            seen_urls.add(link)
                            items.append({
                                "name": f"⚽ {texto}",
                                "title": texto,
                                "channel": "FCTV / Riverlanes",
                                "url": link,
                                "poster": "",
                                "headers": {
                                    "User-Agent": HEADERS["User-Agent"],
                                    "Referer": "https://riverlanes.site/",
                                },
                            })

                # 2. Extraer reproductores embebidos (iframes)
                for i, iframe in enumerate(soup.find_all("iframe"), 1):
                    src = iframe.get("src", "")
                    if src and src not in seen_urls:
                        if src.startswith("/"):
                            src = f"https://riverlanes.site{src}"
                        seen_urls.add(src)
                        items.append({
                            "name": f"🔴 Canal Directo FCTV #{i}",
                            "title": f"FCTV Stream {i}",
                            "channel": "FCTV / Riverlanes",
                            "url": src,
                            "poster": "",
                            "headers": {
                                "User-Agent": HEADERS["User-Agent"],
                                "Referer": "https://riverlanes.site/",
                            },
                        })
        except Exception as e:
            print(f"Error procesando {url}: {e}")

    data["categories"][0]["items"] = items

    with open("fctv.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"fctv.json generado exitosamente con {len(items)} items.")


if __name__ == "__main__":
    main()
