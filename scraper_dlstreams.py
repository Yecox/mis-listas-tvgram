import json
import requests
from bs4 import BeautifulSoup

URL = "https://dlstreams.st/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://dlstreams.st/",
}


def main():
    data = {"categories": [{"name": "DLStreams Sports 🏆", "items": []}]}

    try:
        response = requests.get(URL, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")

        for a in soup.find_all("a"):
            texto = a.text.strip()
            link = a.get("href", "")

            if link and len(texto) > 2:
                if link.startswith("/"):
                    link = f"https://dlstreams.st{link}"

                # Estructura Nativa de TVGram Player
                data["categories"][0]["items"].append({
                    "name": f"⚽ {texto}",
                    "title": texto,
                    "channel": "DLStreams",
                    "url": link,
                    "poster": "",
                    "headers": {
                        "User-Agent": HEADERS["User-Agent"],
                        "Referer": "https://dlstreams.st/",
                    },
                })
    except Exception as e:
        print(f"Error procesando DLStreams: {e}")

    with open("dlstreams.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("Archivo dlstreams.json creado con éxito.")


if __name__ == "__main__":
    main()
