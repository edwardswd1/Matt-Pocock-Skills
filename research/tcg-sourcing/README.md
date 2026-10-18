# TCG sourcing research: data and tools

Everything behind [`../../tcg-sourcing-report.md`](../../tcg-sourcing-report.md) and [`../../tcg-sourcing-raw-notes.md`](../../tcg-sourcing-raw-notes.md), committed so the research can be audited, re-run or extended without scraping Reddit again.

## What's here

| Path | Contents |
|---|---|
| `tools/out/arc_posts.jsonl` | 2,774 Reddit post records (title, sub, date, archive score, comment count, body) from title searches, one line per `sub\|term\|after` job |
| `tools/out/arc_trees.jsonl` | 126 full comment trees (~8,500 comments) |
| `tools/out/subs.jsonl`, `search.jsonl`, `disc.jsonl` | Subreddit liveness checks and results from the Reddit `.rss` and Brave/DuckDuckGo discovery passes |
| `tools/jobs/` | The exact job lists and thread-ID lists used |
| `tools/rd.py` | Reddit reader using the insane-search Phase 0 route: `.rss` feeds via `curl_cffi` TLS impersonation, with 429 backoff and an on-disk cache |
| `tools/arc.py` | Arctic Shift archive client: `posts` (title search) and `trees` (comment trees). Resumable |
| `tools/view.py` | Prints a thread's post plus top comments by score: `python3 view.py <id> [<id>...]` (env `TOP`, `CLIP`) |
| `tools/rawnotes.py` | Rebuilds the raw-notes markdown from `out/` |
| `tools/pf.py`, `tools/pc.py` | Public-page fetch with a TLS-impersonation grid (for 403'd official pages); PriceCharting booster-box price pull |
| `tools/econ.py`, `tools/budget.py` | Unit-economics and budget-scenario models used in report Sections 4 and 6 |

## Re-running or extending

```bash
pip install "curl_cffi>=0.15.0"
cd research/tcg-sourcing/tools

# add threads by ID, then rebuild the notes
printf "%s\n" 1abc123 1def456 > jobs/ids_new.txt
python3 -I arc.py trees jobs/ids_new.txt
python3 -I rawnotes.py ../../../tcg-sourcing-raw-notes.md

# new title searches: a JSON list of [subreddit, title_term, "YYYY-MM-DD"]
python3 -I arc.py posts jobs/arcjobs3.json

# live Reddit (insane-search route), slow: ~1 request/min before 429s
python3 -I rd.py search PokeInvesting "distributor" relevance year 25
python3 -I rd.py comments https://www.reddit.com/r/PokeInvesting/comments/1s6nfst/

# refresh the economics
python3 -I econ.py
python3 -I budget.py
python3 -I pc.py evolving-skies surging-sparks phantasmal-flames
```

New threads only appear in the raw notes once their IDs are added to a topic in `rawnotes.py` (`TOPICS`).

## Notes

- **insane-search** lives at [edwardswd1/insane-search](https://github.com/edwardswd1/insane-search). Its documented Reddit route is `.rss` plus TLS impersonation. Unauthenticated `.json` returns 403, and `.rss` rate-limits hard (about 1 request per minute from a cloud IP), which is why the bulk of the comment data came from the Arctic Shift public archive. PullPush refuses agent scraping and was not used.
- **Archive scores** are snapshots taken near ingest time, so they understate final upvotes.
- **Arctic Shift title search** takes ~1-2 minutes per job and returns `422 Timeout` under load; `arc.py` backs off and resumes. Full-text comment-body search was too slow to be usable.
- **Fees, grading prices and distributor policies** in the report were verified on 2026-10-18; re-check them before relying on the economics later.
