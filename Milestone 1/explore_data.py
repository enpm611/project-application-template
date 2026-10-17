"""
Exploratory data analysis of the Poetry issues dataset.

Run:
    python3 explore_data.py ../poetry_issues_all.json
    python3 explore_data.py ../poetry_issues.json

Uses only the Python standard library, so it runs without the project's venv.
Each STEP matches a section in data_exploration.md.
"""
import json
import statistics as stats
import sys
from collections import Counter, defaultdict
from datetime import datetime


def parse_date(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")) if s else None


def is_bot(author):
    return bool(author) and author.endswith("[bot]")


def header(title):
    print("\n" + "=" * 70 + "\n" + title + "\n" + "=" * 70)


def main(path):
    with open(path) as f:
        issues = json.load(f)
    events = [e for i in issues for e in i.get("events", [])]

    header("STEP 1 - Size and shape")
    print(f"Issues: {len(issues)}   Events: {len(events)}")
    print("Issue fields:", sorted({k for i in issues for k in i}))
    print("Event fields:", sorted({k for e in events for k in e}))

    header("STEP 2 - Data quality")
    print("Events with no author:", sum(1 for e in events if not e.get("author")))
    print("Events with no date:  ", sum(1 for e in events if not e.get("event_date")))
    print("  by type:", Counter(e["event_type"] for e in events if not e.get("event_date")).most_common(5))
    unsorted = sum(
        1 for i in issues
        if [e.get("event_date") or "" for e in i["events"]] != sorted(e.get("event_date") or "" for e in i["events"])
    )
    print("Issues whose events are not in date order:", unsorted)
    print("Issues with no labels:", sum(1 for i in issues if not i.get("labels")))

    header("STEP 3 - What happens to issues (event types)")
    for t, n in Counter(e["event_type"] for e in events).most_common(15):
        print(f"  {t:20s} {n}")

    header("STEP 4 - How issues are categorised (labels)")
    labels = Counter(l for i in issues for l in i.get("labels", []))
    for fam in ("kind/", "area/", "status/"):
        top = [(l, n) for l, n in labels.most_common() if l.startswith(fam)][:8]
        print(f"  {fam:8s}", top)
    print("Issues with no kind/ label:", sum(1 for i in issues if not any(l.startswith("kind/") for l in i["labels"])))

    header("STEP 5 - Lifecycle: open vs closed")
    combo = Counter()
    for i in issues:
        has_close = any(e["event_type"] == "closed" for e in i["events"])
        reopened = any(e["event_type"] == "reopened" for e in i["events"])
        combo[(i["state"], has_close, reopened)] += 1
    for (state, has_close, reopened), n in sorted(combo.items()):
        print(f"  state={state:6s} closed_event={has_close!s:5s} reopened={reopened!s:5s} -> {n}")
    closers = Counter(e.get("author") for e in events if e["event_type"] == "closed")
    print("Top closers:", closers.most_common(6))
    print("Closed by bots:", sum(n for a, n in closers.items() if is_bot(a)))

    header("STEP 6 - Time coverage")
    print("Issues by year:", sorted(Counter(i["created_date"][:4] for i in issues).items()))
    print("Latest issue:", max(i["created_date"] for i in issues))

    header("STEP 7 - People")
    authors = Counter(e.get("author") for e in events)
    print("Distinct event authors:", len(authors))
    print("Most active:", authors.most_common(8))
    print("Bot-like authors:", [(a, n) for a, n in authors.most_common() if is_bot(a)][:5])
    for user, _ in [x for x in authors.most_common(6) if not is_bot(x[0])][:4]:
        mix = Counter(e["event_type"] for e in events if e.get("author") == user).most_common(5)
        print(f"  {user:14s}", mix)
    creators = Counter(i["creator"] for i in issues)
    print("Distinct creators:", len(creators), "| opened exactly 1 issue:", sum(1 for n in creators.values() if n == 1))
    print("Top creators:", creators.most_common(5))
    assigned = sum(1 for i in issues if i.get("assignees"))
    print(f"Issues with any assignee: {assigned} ({100 * assigned / len(issues):.1f}%)")

    header("STEP 8 - Quick checks for candidate features")
    # Candidate A: resolution time by label
    by_label = defaultdict(list)
    for i in issues:
        closes = [e for e in i["events"]
                  if e["event_type"] == "closed" and e.get("event_date") and not is_bot(e.get("author"))]
        if i["state"] != "closed" or not closes:
            continue
        days = (parse_date(max(e["event_date"] for e in closes)) - parse_date(i["created_date"])).total_seconds() / 86400
        for l in i["labels"]:
            if l.startswith(("kind/", "area/")):
                by_label[l].append(days)
    rows = sorted(((l, len(v), stats.median(v)) for l, v in by_label.items() if len(v) >= 8), key=lambda r: -r[2])
    print("A) Median days to close, by label (n >= 8):")
    for l, n, m in rows[:6] + [("...", 0, 0)] + rows[-4:]:
        print(f"  {l:26s} n={n:5d} median={m:7.1f}" if n else "  ...")

    # Candidate B: time to first response by year
    print("B) Median hours to first non-author, non-bot comment, by year:")
    by_year, never = defaultdict(list), Counter()
    for i in issues:
        y = i["created_date"][:4]
        replies = [parse_date(e["event_date"]) for e in i["events"]
                   if e["event_type"] == "commented" and e.get("event_date") and e.get("author")
                   and e["author"] != i["creator"] and not is_bot(e["author"])]
        if replies:
            by_year[y].append((min(replies) - parse_date(i["created_date"])).total_seconds() / 3600)
        else:
            never[y] += 1
    for y in sorted(set(by_year) | set(never)):
        med = f"{stats.median(by_year[y]):7.1f}" if by_year[y] else "    n/a"
        print(f"  {y}: median={med} h   never answered={never[y]}")

    # Candidate C: reopen counts
    reopened = [i for i in issues if any(e["event_type"] == "reopened" for e in i["events"])]
    print(f"C) Reopened issues: {len(reopened)} ({100 * len(reopened) / len(issues):.1f}%)")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "../poetry_issues_all.json")
