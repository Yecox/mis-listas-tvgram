import json
import requests
from bs4 import BeautifulSoup

URL = "https://livetv.sx/es/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://livetv.sx/",
}


def main():
    data = {"categories": [{"name": "LiveTV SX 📺", "items": []}]}

    try:
        response = requests.get(URL, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")

        for a in soup.find_all("a"):
            texto = a.text.strip()
            link = a.get("href", "")

            if link and len(texto) > 2:
                if link.startswith("/"):
                    link = f"https://livetv.sx{link}"

                # Estructura Nativa de TVGram Player
                data["categories"][0]["items"].append({
                    "name": f"📺 {texto}",
                    "title": texto,
                    "channel": "LiveTV SX",
                    "url": link,
                    "poster": "",
                    "headers": {
                        "User-Agent": HEADERS["User-Agent"],
                        "Referer": "https://livetv.sx/",
                    },
                })
    except Exception as e:
        print(f"Error procesando LiveTV: {e}")

    with open("livetv.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("Archivo livetv.json creado con éxito.")


if __name__ == "__main__":
    main()
