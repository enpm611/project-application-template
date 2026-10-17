# Team 6 — Proposed Analyses

All numbers below come from the full dataset (`poetry_issues_all.json`, 5,573 issues), reproducible with `explore_data.py` (see `data_exploration.md`). Resolution times exclude issues closed by bots.

| # | Feature | Question | User input | Scope | Output |
|---|---|---|---|---|---|
| 1 | Resolution time | Which areas and kinds of issue take longest to resolve? | None | Project-wide | Bar chart |
| 2 | Contributor profile | What role does a given contributor play? | `--user` | Subset (one contributor) | Stacked bar chart + console |
| 3 | Response time | How quickly does an issue get its first reply, and is that changing? | None | Project-wide | Line chart (2 series) |

---

## Feature 1 — Resolution time by area and kind

**Run:** `python run.py --feature 1`
**Module:** `resolution_time_analysis.py`

### Question
Which parts of Poetry (`area/*`) and which kinds of issues (`kind/*`) take the longest to resolve?

### Method
1. For each closed issue, compute days from `created_date` to the date it was resolved.
2. Group by label (`area/*` and `kind/*`).
3. Compute the **median** days per group (robust to a few multi-year outliers).
4. Plot a horizontal bar chart, sorted, with the sample size (n) shown per bar.

### Evidence it is worth building

| Group | Closed issues | Median days to close |
|---|---|---|
| area/error-handling | 35 | 692 |
| area/ux | 32 | 503 |
| area/cli | 113 | 248 |
| kind/feature | 682 | 43 |
| area/solver | 145 | 47 |
| area/installer | 76 | 22 |
| area/docs | 226 | 15 |
| kind/bug | 2,566 | 6.4 |
| kind/question | 263 | 0.2 |

**Expected finding:** questions and bugs are closed fast, while UX and error-handling work stays open for 1–2 years.

### Data handling decisions

| Case | Count | Handling |
|---|---|---|
| Issue closed more than once (reopened) | 151 | Use the **last** close date |
| `state=closed` but no `closed` event | 205 | Exclude, and print how many were excluded |
| Closed by `stale[bot]` (inactivity, not resolution) | 172 | Exclude, and print how many were excluded |
| Still open | 317 | Exclude from the median, but print % still open per group |
| Very small groups | — | Show only groups with n ≥ 8 |
| Issue has multiple labels | — | Count it in each of its groups |
| Event with no date | 184 events | Skip that event |

---

## Feature 2 — Contributor profile

**Run:** `python run.py --feature 2 --user <github-username>`
**Module:** `contributor_profile_analysis.py`

### Question
What role does a given contributor play in the project: do they mostly answer, triage, label, or close?

### Method
1. Read the `--user` value from config.
2. Collect every event authored by that user across all issues.
3. Compute their mix of event types (commented, labeled, unlabeled, closed, assigned, …) as percentages.
4. Compare that mix with the **core-maintainer baseline**: the combined mix of the top 10 most active non-bot contributors. (Comparing with the average of all 7,629 contributors would be misleading: most are one-off users who mostly comment, so every maintainer would look different from them.)
5. List the `area/*` labels they work on most.
6. Output a stacked bar chart (user vs. maintainer baseline) plus a console summary.

### Evidence it is worth building

| User | Dominant activity | Role |
|---|---|---|
| dimbleby | 2,803 comments, only 23 labels added, no closes | Answerer |
| abn | 1,178 labels removed, 388 issues closed | Triager / closer |
| finswimmer | 1,016 issues closed, 588 labels added | Closer |
| neersighted | 767 labels added (the most of anyone), 1,006 removed, 717 closed | Triager |
| github-actions[bot] | 4,753 locks, 4,782 comments | Automation (excluded from the baseline) |

Share of each person's events, compared with the baseline:

| Event type | dimbleby | abn | Top-10 maintainer baseline | All non-bot contributors |
|---|---|---|---|---|
| commented | 63% | 24% | 33% | 37% |
| labeled | 1% | 7% | 11% | 17% |
| unlabeled | 0% | 26% | 14% | 5% |
| closed | 0% | 9% | 13% | 8% |

**Expected finding:** core maintainers specialize into distinct roles rather than doing the same kind of work. dimbleby almost only answers; abn removes labels at about twice the maintainer rate.

### Edge cases

| Case | Handling |
|---|---|
| `--user` not provided | Print usage instructions and exit cleanly |
| Unknown user / no activity | Print "no activity found" and suggest the top 5 contributors |
| Numeric username (e.g. `--user 12345`) | Template's `config.convert_to_typed_value` turns it into an `int`; wrap the value in `str()` before comparing |
| `--user null` / `--user true` | Same conversion bug turns these into `None` / `True`; `str()` fixes it |
| Case differences (`ABN` vs `abn`) | Decide on one behavior and document it in the README |
| Bot account given as input | Allowed, but label it as automation in the output |

---

## Feature 3 — Time to first response, by year

**Run:** `python run.py --feature 3`
**Module:** `response_time_analysis.py`

### Question
How long does an issue wait for its first reply from someone other than its author, and has that changed over the years?

### Method
1. For each issue, find the **earliest** comment by someone other than the issue's creator, excluding bots.
2. Compute hours from `created_date` to that comment.
3. Group by the year the issue was created.
4. Per year, compute the **median** response time and the **% of issues never answered**.
5. Plot a line chart with two series (median hours, % never answered) and a legend.
6. In the console, print the top first responder per year, their share of answered issues, and the median response time **with that person excluded**.

### Evidence it is worth building

| Year | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|---|
| Median hours to first response | 21 | 108 | 25 | 87 | 1.5 | 1.0 | 0.9 |
| Issues never answered | 62 | 100 | 93 | 102 | 85 | 54 | 47 |

Who answers first, and what response time would be without them:

| Year | Top first responder | Share of answered issues | Median first response | Median without dimbleby |
|---|---|---|---|---|
| 2022 | dimbleby | 296 / 1,040 (28%) | 1.5 h | 3.6 h |
| 2023 | dimbleby | 553 / 756 (73%) | 1.0 h | **12.4 h** |
| 2024 | dimbleby | 307 / 408 (75%) | 0.9 h | **10.4 h** |

"Share of answered issues" excludes issues that never received a reply (in 2023: 553 of 810 issues overall, or 68%).

First-time issue creators are answered as quickly as repeat creators (2023: median 1.0 h vs 0.9 h).

**Expected finding:** response time dropped from days to about an hour starting in 2022. The 2022 drop was not one person's doing (dimbleby answered only 28% that year), but since 2023 the fast response depends on a single volunteer: without him, the median would be 10–12 hours instead of about 1 hour, a "bus factor" risk.

**Limitation:** the "without dimbleby" figure assumes no one else would have replied sooner in his absence. It shows dependency, not what would actually have happened.

### Edge cases

| Case | Handling |
|---|---|
| Bot comments (e.g. `github-actions[bot]`) | Exclude authors ending in `[bot]` (heuristic; document it) |
| Issue creator replying to themselves | Not counted as a response |
| Issue never answered | Counted in the "% never answered" series, not in the median |
| Events listed out of date order (52 issues) | Use the minimum date, never the first list item |
| Comment with no date | Skip it |

---

## How these features were chosen

1. **Start from the rubric.** At least one analysis with user input, at least one project-wide, at least two charts, and no single ungrouped counts. This points toward the shape *a metric compared across groups*.
2. **Inspect what the data contains.** Count event types, labels, states and dates, and drop ideas the data cannot support.
3. **Ask who would care.** A maintainer ("where does work get stuck?"), a newcomer ("who does what?"), and someone filing an issue ("will anyone answer me, and how fast?").
4. **Combine a metric with a dimension.** Days to close × area/kind (F1). Event-type mix × one contributor (F2). Hours to first reply × year (F3).
5. **Run quick checks on the data before committing.** Keep an idea only if its numbers vary enough to tell a story.

---

## Alternatives considered and rejected

### Rejected 1 — Top issue creators

**Question:** Who opens the most issues?
**Method:** Count issues per `creator`, plot the top N as a bar chart.

**Evidence:**
- 3,664 distinct creators; **2,839 (77%) opened exactly one issue**.
- The #1 "creator" is `ghost` (65 issues), which is GitHub's placeholder for **deleted accounts**, not a real person.
- Next: abn (36), KotlinIsland (28), dimaqq (26), cjw296 (26).

**Why rejected:**
- It is a bare count per person, essentially the template's own `example_analysis.py`, which the assignment classes as too limited.
- The ranking is dominated by `ghost`, so the top bar is an artifact of account deletion.
- Opening issues says little about the project; most creators appear once. There is no clear "so what?".

### Rejected 2 — Issues per year

**Question:** How many issues are opened each year?
**Method:** Group issues by the year of `created_date`, plot a line chart.

**Evidence:**

| Year | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|---|
| Issues opened | 587 | 721 | 1,052 | 823 | 1,125 | 810 | 455 |

**Why rejected:**
- A count over time, one number per year, with no comparison.
- The finding cannot be interpreted: a drop could mean fewer users, fewer bugs, or better docs.
- **2024 is a partial year** (data ends October 2024), so its low value is misleading on its face.
- Feature 3 uses the same time axis but measures something actionable (response speed).

### Rejected 3 — Assignee workload

**Question:** How is work distributed among assigned maintainers?
**Method:** Count and time issues per entry in `assignees`.

**Evidence:**
- Only **144 of 5,573 issues (2.6%) have any assignee**.
- `assignees` holds full GitHub user objects (dicts), not plain usernames as `model.py`'s type hint (`List[str]`) suggests, so extra parsing would be needed.

**Why rejected:**
- Poetry largely does not use assignment, so 97% of issues would be ignored and any conclusion would describe a tiny, unrepresentative slice.
- Feature 2 answers "who does what" from **events**, which cover the whole dataset.

### Rejected 4 — Reopen rate by label

**Question:** Which kinds of issues get reopened most, suggesting incomplete fixes?
**Method:** Per label, the share of issues with a `reopened` event.

**Evidence:**
- Only **117 issues (2.1%) were ever reopened**.
- By label: kind/bug 71, kind/feature 19, and every `area/*` label has 5 or fewer.

**Why rejected:**
- Per-area rates would be computed from 3–5 issues, so one issue changes the result by 20–30 percentage points.
- With so few events, differences between labels are noise rather than a finding.

### Rejected 5 — Comment count vs. resolution time

**Question:** Do issues with more discussion take longer to resolve?
**Method:** For closed issues, compare number of comments (excluding bots) with days to close.

**Evidence:**

| Comments | 0 | 1–2 | 3–5 | 6–10 | 11+ |
|---|---|---|---|---|---|
| Closed issues | 202 | 2,058 | 1,464 | 823 | 324 |
| Median days to close | 4 | 2 | 11 | 40 | 45 |

Rank correlation (Spearman) = 0.24 across 4,871 issues: a real but weak relationship.

**Why rejected:**
- **The cause runs both ways.** Hard issues attract discussion *and* take long, and issues open for a long time accumulate comments simply by existing. The analysis cannot say which drives which, so the finding is "they move together", which is easy to over-claim in a presentation.
- It overlaps with Feature 1 (resolution time), which explains slowness through a clearer lens (area and kind).
- Retained as a possible extension if time allows, but not as one of the three.

### Rejected 6 — Sentiment of comment text

**Question:** Are discussions on some kinds of issues more negative or frustrated?
**Method:** Run a sentiment model over each `comment` and aggregate per label.

**Why rejected:**
- Needs NLP libraries beyond the template's dependencies (`pandas`, `matplotlib`, `python-dateutil`).
- Hard to validate: comments contain code, stack traces and technical terms that general sentiment models misread, and the team cannot check accuracy on thousands of comments.
- It is hard to write meaningful, deterministic unit tests for a model's output, which matters for Milestone 3.
- The course focuses on software design and testing, not NLP.
