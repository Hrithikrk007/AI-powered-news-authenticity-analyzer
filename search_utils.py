# search_utils.py
import os
import requests
import urllib.parse

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")  # set env or leave blank
GOOGLE_CX = os.environ.get("GOOGLE_CX", "")  # set env or leave blank

def google_fact_check(query: str):
    q = (query or "").strip()
    if not q:
        return []
    if not GOOGLE_API_KEY or not GOOGLE_CX:
        # No API available — return empty instead of crashing
        return []
    try:
        url = ("https://www.googleapis.com/customsearch/v1?"
               f"key={urllib.parse.quote(GOOGLE_API_KEY)}&cx={urllib.parse.quote(GOOGLE_CX)}&q={urllib.parse.quote(q)}")
        r = requests.get(url, timeout=8)
        data = r.json()
        items = data.get("items", [])
        results = []
        seen = set()
        for it in items:
            link = it.get("link","")
            if link in seen:
                continue
            seen.add(link)
            results.append({
                "title": it.get("title",""),
                "snippet": it.get("snippet",""),
                "link": link
            })
        return results[:8]
    except Exception:
        return []
