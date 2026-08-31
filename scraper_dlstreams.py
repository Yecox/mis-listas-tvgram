import json
import re
import requests
from bs4 import BeautifulSoup

URL = "https://dlstreams.st/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "https://dlstreams.st/",
}


def main():
    stations = []
    try:
        res = requests.get(URL, headers=HEADERS, timeout=15)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            for a in soup.find_all("a", href=re.compile(r"watch\.php\?id=")):
                title = a.get_text(strip=True)
                link = a.get("href", "")

                if link and len(title) > 2:
                    if link.startswith("/"):
                        link = f"https://dlstreams.st{link}"

                    stations.append({
                        "name": title,
                        "image": "",
                        "url": link,
                        "isEmbed": "true",
                        "referer": "https://dlstreams.st/",
                    })
    except Exception as e:
        print(f"Error en DLStreams: {e}")

    data = {
        "name": "DLStreams",
        "author": "Yecox",
        "groups": [{"name": "DLStreams Events ⚽", "stations": stations}],
    }

    with open("dlstreams.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
