"""Reddit research via the Arctic Shift public archive (complements insane-search's
.rss route, which lacks scores and is heavily rate-limited).
  arc.py posts jobs.json   -> out/arc_posts.jsonl   (jobs: [[sub, title_term, after], ...])
  arc.py trees ids.txt     -> out/arc_trees.jsonl
Polite pacing; retries on 422/429 with backoff; resumable."""
import sys, os, json, time
from curl_cffi import requests as r

HERE = os.path.dirname(os.path.abspath(__file__))
API = "https://arctic-shift.photon-reddit.com/api"
FIELDS = "id,title,score,num_comments,created_utc,subreddit,author,selftext"


def get(url):
    d = 5
    for _ in range(7):
        try:
            x = r.get(url, impersonate="chrome", timeout=90)
            if x.status_code == 200:
                time.sleep(2.5)
                return x.json().get("data")
            print(f"# {x.status_code} {x.text[:80]}", file=sys.stderr)
        except Exception as e:
            print(f"# ERR {type(e).__name__}", file=sys.stderr)
        time.sleep(d); d = min(d * 2, 120)
    return None


def done(path, key):
    s = set()
    if os.path.exists(path):
        for l in open(path):
            s.add(json.loads(l)[key])
    return s


def posts(jobs):
    out = os.path.join(HERE, "out", "arc_posts.jsonl")
    seen = done(out, "job")
    with open(out, "a") as f:
        for sub, term, after in jobs:
            job = f"{sub}|{term}|{after}"
            if job in seen:
                continue
            url = f"{API}/posts/search?subreddit={sub}&title={term.replace(' ', '%20')}&after={after}&limit=100&sort=desc&fields={FIELDS}"
            data = get(url)
            f.write(json.dumps({"job": job, "ok": data is not None, "posts": data or []}, ensure_ascii=False) + "\n"); f.flush()
            print(f"{job}: {len(data or [])}", file=sys.stderr)


def trees(ids):
    out = os.path.join(HERE, "out", "arc_trees.jsonl")
    seen = done(out, "id")
    with open(out, "a") as f:
        for pid in ids:
            if pid in seen:
                continue
            data = get(f"{API}/comments/tree?link_id={pid}&limit=500")
            flat = []

            def walk(n, dep):
                if n.get("kind") == "more":
                    return
                c = n.get("data", n)
                flat.append({"d": dep, "score": c.get("score"), "author": c.get("author"),
                             "t": time.strftime("%Y-%m-%d", time.gmtime(c.get("created_utc") or 0)),
                             "body": c.get("body") or ""})
                rep = c.get("replies")
                if isinstance(rep, dict):
                    for k in rep.get("data", {}).get("children", []):
                        walk(k, dep + 1)
            for n in data or []:
                walk(n, 0)
            f.write(json.dumps({"id": pid, "ok": data is not None, "comments": flat}, ensure_ascii=False) + "\n"); f.flush()
            print(f"tree {pid}: {len(flat)}", file=sys.stderr)


if __name__ == "__main__":
    if sys.argv[1] == "posts":
        posts(json.load(open(sys.argv[2])))
    else:
        trees([l.strip() for l in open(sys.argv[2]) if l.strip()])
