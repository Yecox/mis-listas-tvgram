import json
import requests
from bs4 import BeautifulSoup

URL = "https://riverlanes.site/fctv33/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://riverlanes.site/",
}


def main():
    data = {"categories": [{"name": "Riverlanes / FCTV ⚽", "items": []}]}

    try:
        response = requests.get(URL, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")

        for a in soup.find_all("a"):
            texto = a.text.strip()
            link = a.get("href", "")

            if link and len(texto) > 2:
                if link.startswith("/"):
                    link = f"https://riverlanes.site{link}"

                # Estructura Nativa de TVGram Player
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
    except Exception as e:
        print(f"Error procesando FCTV: {e}")

    with open("fctv.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("Archivo fctv.json creado con éxito.")


if __name__ == "__main__":
    main()
