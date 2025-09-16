from bs4 import BeautifulSoup

def read_html_bytes(b: bytes) -> str:
    soup = BeautifulSoup(b, "html.parser")
    for t in soup(["script","style","noscript"]):
        t.decompose()
    return soup.get_text("\n", strip=True)

