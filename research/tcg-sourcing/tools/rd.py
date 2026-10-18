"""Reddit reader following insane-search's Phase 0 Reddit route:
Atom .rss feeds via curl_cffi TLS impersonation (unauth .json is WAF-blocked).

usage:
  rd.py search <sub|all> "<query>" [sort=relevance|top|new|comments] [t=year|month|all] [limit]
  rd.py comments <post_url>
  rd.py feed <sub> [hot|new|top]
"""
import sys, os, re, time, json, hashlib, html
import xml.etree.ElementTree as ET
from urllib.parse import quote_plus
from curl_cffi import requests as r

CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rdcache")
os.makedirs(CACHE, exist_ok=True)
NS = {"a": "http://www.w3.org/2005/Atom"}
TLS = ["safari", "chrome", "firefox", "safari_ios"]


def get(url):
    key = os.path.join(CACHE, hashlib.md5(url.encode()).hexdigest() + ".xml")
    if os.path.exists(key):
        return open(key, encoding="utf-8").read()
    delay = 4
    for i in range(8):
        imp = TLS[i % len(TLS)]
        try:
            x = r.get(url, impersonate=imp, timeout=25)
        except Exception as e:
            print(f"# err {type(e).__name__} {imp}", file=sys.stderr)
            time.sleep(delay); delay = min(delay * 2, 60); continue
        if x.status_code == 200 and ("<feed" in x.text or "<rss" in x.text):
            open(key, "w", encoding="utf-8").write(x.text)
            time.sleep(2)
            return x.text
        ra = x.headers.get("retry-after")
        wait = int(ra) if ra and ra.isdigit() else delay
        print(f"# {x.status_code} via {imp}, sleeping {wait}s", file=sys.stderr)
        time.sleep(min(wait, 90)); delay = min(delay * 2, 60)
    return ""


def clean(h):
    h = re.sub(r"<br\s*/?>|</p>|</li>", "\n", h or "")
    h = re.sub(r"<[^>]+>", "", h)
    h = html.unescape(h)
    h = re.sub(r"submitted by\s+/u/\S+.*$", "", h, flags=re.S)
    return re.sub(r"\n{3,}", "\n\n", h).strip()


def entries(xml):
    if not xml:
        return []
    try:
        root = ET.fromstring(xml)
    except ET.ParseError:
        return []
    out = []
    for e in root.findall("a:entry", NS):
        link = e.find("a:link", NS)
        cat = e.find("a:category", NS)
        out.append({
            "title": e.findtext("a:title", "", NS),
            "author": e.findtext("a:author/a:name", "", NS),
            "date": (e.findtext("a:published", "", NS) or e.findtext("a:updated", "", NS))[:10],
            "url": link.get("href") if link is not None else "",
            "sub": cat.get("term") if cat is not None else "",
            "body": clean(e.findtext("a:content", "", NS)),
        })
    return out


def main():
    cmd = sys.argv[1]
    if cmd == "search":
        sub, q = sys.argv[2], sys.argv[3]
        sort = sys.argv[4] if len(sys.argv) > 4 else "relevance"
        t = sys.argv[5] if len(sys.argv) > 5 else "year"
        lim = sys.argv[6] if len(sys.argv) > 6 else "25"
        base = "https://www.reddit.com/search.rss" if sub == "all" else f"https://www.reddit.com/r/{sub}/search.rss"
        url = f"{base}?q={quote_plus(q)}&sort={sort}&t={t}&limit={lim}" + ("" if sub == "all" else "&restrict_sr=1")
        res = entries(get(url))
    elif cmd == "comments":
        u = sys.argv[2].split("?")[0].rstrip("/")
        res = entries(get(u + ".rss?limit=200&sort=top"))
    else:
        sub = sys.argv[2]; s = sys.argv[3] if len(sys.argv) > 3 else "hot"
        res = entries(get(f"https://www.reddit.com/r/{sub}/{s}.rss?limit=25&t=year"))
    for e in res:
        print(json.dumps(e, ensure_ascii=False))


if __name__ == "__main__":
    main()
