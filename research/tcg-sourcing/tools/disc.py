"""Reddit thread discovery via public search engines (Brave, DuckDuckGo HTML),
mirroring insane-search's free-search discovery lane. Output: out/disc.jsonl"""
import sys, os, re, json, time, random
import urllib.parse as up
from curl_cffi import requests as r

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "disc.jsonl")
LINK = re.compile(r"https://(?:www\.|old\.)?reddit\.com/r/(\w+)/comments/(\w+)/([\w-]*)")


def engines(q):
    qq = up.quote_plus(q)
    return [("brave", f"https://search.brave.com/search?q={qq}"),
            ("ddg", f"https://html.duckduckgo.com/html/?q={qq}")]


def run(queries):
    seen = set()
    if os.path.exists(OUT):
        for l in open(OUT):
            seen.add((json.loads(l)["q"]))
    with open(OUT, "a") as f:
        for q in queries:
            if q in seen:
                continue
            hits = {}
            for name, u in engines("site:reddit.com " + q):
                try:
                    x = r.get(u, impersonate="chrome", timeout=20)
                    t = up.unquote(x.text)
                    for sub, pid, slug in LINK.findall(t):
                        hits.setdefault(pid, {"sub": sub, "id": pid, "slug": slug, "engines": []})
                        if name not in hits[pid]["engines"]:
                            hits[pid]["engines"].append(name)
                    print(f"# {name} {x.status_code} {q}", file=sys.stderr)
                except Exception as e:
                    print(f"# {name} ERR {type(e).__name__} {q}", file=sys.stderr)
                time.sleep(2 + random.random() * 2)
            f.write(json.dumps({"q": q, "hits": list(hits.values())}) + "\n"); f.flush()


if __name__ == "__main__":
    run([l.strip() for l in open(sys.argv[1]) if l.strip()])
