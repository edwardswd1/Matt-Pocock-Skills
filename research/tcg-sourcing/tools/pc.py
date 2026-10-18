import sys, re, time
from curl_cffi import requests as r
sets = sys.argv[1:]
for s in sets:
    u = f"https://www.pricecharting.com/game/pokemon-{s}/booster-box"
    try:
        t = r.get(u, impersonate="safari", timeout=25).text
        m = re.search(r'id="used_price".*?\$([0-9,]+\.[0-9]{2})', t, re.S)
        m2 = re.search(r'Ungraded[^$]{0,80}\$([0-9,]+\.[0-9]{2})', re.sub(r"<[^>]+>", " ", t))
        print(s, (m or m2).group(1) if (m or m2) else "NA")
    except Exception as e:
        print(s, "ERR", type(e).__name__)
    time.sleep(1.5)
