import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup


def fetch_favicon(url, x=None):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
    except Exception as ex:
        print(ex)
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    icon_link = soup.find("link", rel=lambda x: x and "icon" in x.lower())

    if icon_link and icon_link.get("href"):
        href = icon_link["href"]
        return urljoin(url, href)
    else:
        return "https://img.icons8.com/3d-fluency/94/globe.png"