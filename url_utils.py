# url_utils.py
from newspaper import Article
from goose3 import Goose
from readability import Document
import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/119 Safari/537.36"}

def extract_newspaper(url):
    try:
        a = Article(url)
        a.download()
        a.parse()
        return (a.text or "").strip()
    except Exception:
        return ""

def extract_goose(url):
    try:
        g = Goose()
        art = g.extract(url=url)
        return (art.cleaned_text or "").strip()
    except Exception:
        return ""

def extract_readability(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        doc = Document(r.text)
        soup = BeautifulSoup(doc.summary(), "html.parser")
        return soup.get_text(separator=" ").strip()
    except Exception:
        return ""

def extract_text_from_url(url: str):
    # try newspaper
    t = extract_newspaper(url)
    if len(t) >= 200:
        return t
    t2 = extract_goose(url)
    if len(t2) >= 200:
        return t2
    t3 = extract_readability(url)
    if len(t3) >= 200:
        return t3
    # final: return the longest we got (may be short)
    return max([t,t2,t3], key=len)
