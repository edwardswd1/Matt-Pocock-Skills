"""Batch harvester on top of rd.py. Reads jobs from a JSON file:
  {"subs_check": [...], "searches": [[sub, query, sort, t], ...], "threads": [url, ...]}
Writes JSONL to out/<name>.jsonl. Resumable (rd.py caches every feed)."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rd

jobs = json.load(open(sys.argv[1]))
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(out, exist_ok=True)

with open(os.path.join(out, "subs.jsonl"), "a") as f:
    for s in jobs.get("subs_check", []):
        es = rd.entries(rd.get(f"https://www.reddit.com/r/{s}/new.rss?limit=25"))
        dates = sorted(e["date"] for e in es)
        f.write(json.dumps({"sub": s, "n": len(es), "newest": dates[-1] if dates else None,
                            "oldest_of_25": dates[0] if dates else None}) + "\n"); f.flush()

with open(os.path.join(out, "search.jsonl"), "a") as f:
    for sub, q, sort, t in jobs.get("searches", []):
        base = "https://www.reddit.com/search.rss" if sub == "all" else f"https://www.reddit.com/r/{sub}/search.rss"
        url = f"{base}?q={rd.quote_plus(q)}&sort={sort}&t={t}&limit=25" + ("" if sub == "all" else "&restrict_sr=1")
        for e in rd.entries(rd.get(url)):
            e["q"] = q; e["qsub"] = sub
            e["body"] = e["body"][:1500]
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
        f.flush()

with open(os.path.join(out, "threads.jsonl"), "a") as f:
    for u in jobs.get("threads", []):
        es = rd.entries(rd.get(u.split("?")[0].rstrip("/") + ".rss?limit=200&sort=top"))
        f.write(json.dumps({"thread": u, "entries": es}, ensure_ascii=False) + "\n"); f.flush()
print("done")
