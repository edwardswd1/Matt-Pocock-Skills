"""Public-page fetch using insane-search's Phase 2 approach: curl_cffi TLS impersonation grid."""
import sys, re, html
from curl_cffi import requests as r
url = sys.argv[1]
for imp in ["safari", "chrome", "firefox", "safari_ios"]:
    try:
        x = r.get(url, impersonate=imp, timeout=25, headers={"Referer": "https://www.google.com/"})
    except Exception as e:
        print("#", imp, type(e).__name__, file=sys.stderr); continue
    t = x.text
    bad = any(m in t for m in ["Just a moment...", "cf-chl", "Access Denied", "DataDome"])
    print("#", imp, x.status_code, len(t), "challenge" if bad else "", file=sys.stderr)
    if x.status_code == 200 and not bad:
        t = re.sub(r"(?s)<(script|style|noscript)[^>]*>.*?</\1>", " ", t)
        t = re.sub(r"<[^>]+>", " ", t); t = html.unescape(t)
        print(re.sub(r"\s+", " ", t)); break
