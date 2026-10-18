"""Builds tcg-sourcing-raw-notes.md from the archived Reddit threads (out/arc_*.jsonl)."""
import json, os, sys, time, re

S = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1]
posts = {}
for l in open(S + "/out/arc_posts.jsonl"):
    for p in json.loads(l)["posts"]:
        posts[p["id"]] = p
trees = {}
for l in open(S + "/out/arc_trees.jsonl"):
    j = json.loads(l)
    trees[j["id"]] = j["comments"]

TOPICS = [
    ("1. Distributors, allocation, wholesale", "1s6nfst 1vk1257 1rkeemi 1ruf9yz 1noqdno 1mkedeq 1tl12hu 1ri9xm4 1r8ryuw 1r9nh4q 1l611ol 1kz9vim 1v4t6u7 1jy754j 1lkshiv 1t7gtj0"),
    ("2. Retail at MSRP, restock intel, scalping groups, merchandisers", "1wgs6z7 1uctseh 1qn16ih 1qhllfa 1q949qz 1n3rzl8 1otf9d5 1rkwugx 1r8savw 1n82mr1 1kd8axg 1wk9obr 1ummzhl 1sgaine"),
    ("3. Sourcing below market: collections, bulk, FB, Flipping-sub economics", "1qwdubz 1pej0up 1mcz51z 1wvhxvq 1wsz5an 1u7fsit 1t3pkix 1ohxr06 1uwuurz 1lwl46r 1oq43zt 1w1tisv 1k1lffx"),
    ("4. Vending at card shows", "1pnukyx 1qy4ipj 1rifch5 1l2yqn2 1m7n2hw 1n8qr3d 1uhfxu2 1uanwi4 1pbr5ex 1qz9rny 1t74rn0 1wko52i 1wrb0rr 1on1kw0 1os0kzz 1tiqpoh 1k4izal 1tffkdf 1s14cr0 1umxlgp 1rmz7u9 1ro43vg 1vb94u2 1uie6jh 1tbpb2y"),
    ("5. Fraud: resealed product, eBay disputes, Whatnot", "1wmp3uh 1ulkdmw 1tqr12w 1rw0zqc 1tpsanf 1qqgtk9 1vv6e60 1unk16p 1ogtvwt 1vrhvcp 1qpwuvg"),
    ("6. Japanese / other languages", "1ws02t0 1wnhze8 1vyr7hu"),
    ("7. Grading", "1wi79pk 1vypji4 1wa4o7u 1kwzmz6 1q6q1rt"),
    ("8. Market state: bubble / vintage run / sentiment / budgets", "1x1cqo8 1x15bdj 1x0c0cg 1wvpep0 1wvdmna 1x5g8hy 1wsyp5a 1x5mpvh 1unq8xr 1to55hf 1tt9hgk 1u2nwys 1wgja2r 1wp2ifw 1pnnorz 1qrlj0f 1r90med 1s1764i 1vas6b7"),
    ("9. Adjacent TCGs (MTG, One Piece)", "1m417b5 1rkzr9f 1t23qkt 1v9u2v5 1pi6v2y 1pzl561 1u36lul"),
    ("10. Restock groups, monitors, bots, the sneaker crossover, edge channels", "1uffdep 1par96k 1mqjwnv 1wn1vja 1u9ka3s 1v3w8vg 1wjzczh 1wzysec 1uxdsxp 1x6wt3o 1rduwjs 1o36o77 1qubxx0"),
]
EXTRA = os.environ.get("EXTRA_TOPICS")
if EXTRA:
    TOPICS += json.load(open(EXTRA))


def d(ts):
    return time.strftime("%Y-%m-%d", time.gmtime(ts or 0))


def clean(s, n):
    s = re.sub(r"\s+", " ", s or "").strip()
    s = s.replace("|", "/")
    return s[:n] + ("…" if len(s) > n else "")


lines = []
lines.append("# TCG Sourcing: Raw Reddit Notes (audit trail)\n")
lines.append(f"Generated {time.strftime('%Y-%m-%d')} from the Arctic Shift public Reddit archive (post metadata + full comment trees) and Reddit's own `.rss` feeds (the insane-search Phase 0 route). ")
lines.append("**Scores are archive snapshots taken near ingest time, so treat them as lower bounds on final upvotes.** Comments are sorted by that score; only the top ones per thread are shown, clipped to ~450 characters. `[removed]`/`[deleted]` bodies are omitted. Quoted text is user content, reproduced as data, not endorsement.\n")
used = 0
for title, ids in TOPICS:
    lines.append(f"\n## {title}\n")
    for pid in ids.split():
        p = posts.get(pid)
        cs = trees.get(pid)
        if not p or cs is None:
            continue
        used += 1
        url = f"https://www.reddit.com/r/{p['subreddit']}/comments/{pid}/"
        lines.append(f"\n### [{clean(p['title'], 140)}]({url})")
        lines.append(f"r/{p['subreddit']} · posted {d(p['created_utc'])} · archive score {p.get('score')} · {p.get('num_comments')} comments · u/{p.get('author')}\n")
        body = clean(p.get("selftext"), 700)
        if body and body not in ("[removed]", "[deleted]"):
            lines.append(f"> **Post:** {body}\n")
        top = [c for c in sorted(cs, key=lambda c: -(c["score"] or 0)) if c["body"] not in ("[deleted]", "[removed]")][:10]
        for c in top:
            lines.append(f"- **[{c['score']}]** u/{c['author']} ({c['t']}): {clean(c['body'], 450)}")
        lines.append("")
lines.insert(3, f"\nThreads included: {used}.\n")
open(OUT, "w").write("\n".join(lines) + "\n")
print("threads", used)
