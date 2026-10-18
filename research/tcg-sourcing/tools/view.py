import json, sys, time, os
S = os.path.dirname(os.path.abspath(__file__))
posts = {}
for l in open(S + "/out/arc_posts.jsonl"):
    for p in json.loads(l)["posts"]:
        posts[p["id"]] = p
trees = {}
for l in open(S + "/out/arc_trees.jsonl"):
    j = json.loads(l); trees[j["id"]] = j["comments"]
top = int(os.environ.get("TOP", "18")); clip = int(os.environ.get("CLIP", "420"))
for pid in sys.argv[1:]:
    p = posts.get(pid, {})
    print(f"\n##### {pid} r/{p.get('subreddit')} {time.strftime('%Y-%m-%d', time.gmtime(p.get('created_utc', 0)))} score={p.get('score')} n={p.get('num_comments')} :: {p.get('title')}")
    print("POST:", (p.get("selftext") or "")[:900].replace("\n", " "))
    cs = sorted(trees.get(pid, []), key=lambda c: -(c["score"] or 0))[:top]
    for c in cs:
        if c["body"] in ("[deleted]", "[removed]"): continue
        print(f" [{c['score']}|d{c['d']}|{c['t']}|{c['author']}] {c['body'][:clip].replace(chr(10), ' ')}")
