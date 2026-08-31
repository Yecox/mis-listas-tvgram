import json
import requests
from bs4 import BeautifulSoup

URLS = ["https://riverlanes.site/fctv33/", "https://www.fctv33.com/"]
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "https://www.fctv33.com/",
}


def main():
    stations = []
    seen = set()

    for url in URLS:
        try:
            res = requests.get(url, headers=HEADERS, timeout=15)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")

                for a in soup.find_all("a"):
                    link = a.get("href", "")
                    texto = a.get_text(strip=True)

                    if (
                        link
                        and not link.startswith("#")
                        and not link.startswith("javascript:")
                    ):
                        if link.startswith("/"):
                            link = f"https://www.fctv33.com{link}"

                        if link not in seen and len(texto) > 2:
                            seen.add(link)
                            stations.append({
                                "name": texto,
                                "image": "",
                                "url": link,
                                "isEmbed": "true",
                                "referer": "https://www.fctv33.com/",
                            })

                for i, iframe in enumerate(soup.find_all("iframe"), 1):
                    src = iframe.get("src", "")
                    if src and src not in seen:
                        if src.startswith("/"):
                            src = f"https://www.fctv33.com{src}"
                        seen.add(src)
                        stations.append({
                            "name": f"Directo FCTV #{i}",
                            "image": "",
                            "url": src,
                            "isEmbed": "true",
                            "referer": "https://www.fctv33.com/",
                        })
        except Exception as e:
            print(f"Error en FCTV: {e}")

    data = {
        "name": "FCTV / Riverlanes",
        "author": "Yecox",
        "groups": [{"name": "FCTV / Riverlanes ⚽", "stations": stations}],
    }

    with open("fctv.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
