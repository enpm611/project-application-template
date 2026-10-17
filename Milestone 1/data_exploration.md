# Team 6 — Exploring the Poetry Issues Data

Before choosing any feature, we explored the dataset to learn what it contains, how reliable it is, and which questions it can actually answer. This document walks through that exploration step by step: what we asked, what we found, and what each finding meant for the design.

## How to reproduce

The script `explore_data.py` (in this folder) prints every number in this document. It uses only the Python standard library.

```bash
cd "Milestone 1"
python3 explore_data.py ../poetry_issues_all.json   # full dataset (5,573 issues)
python3 explore_data.py ../poetry_issues.json       # subset (661 issues)
```

Each `STEP` in the script's output matches a section below.

---

## Step 0 — Which file do we trust?

Two data files were provided. Before anything else we compared them.

| | Subset (`poetry_issues.json`) | Full (`poetry_issues_all.json`) |
|---|---|---|
| Issues | 661 | 5,573 |
| Issues from 2024 | 397 (60%) | 455 (8%) |
| Issues from 2018 | 4 | 587 |
| Still open | 39% | 6% |
| Median days to close a bug | 0.9 | 6.4 |

**What it told us:** the subset is heavily skewed toward recent issues, so it is not a representative sample. Its numbers lead to different conclusions.

**Decision:** use the subset only to make development runs fast. Every finding we report comes from the full file.

---

## Step 1 — Size and shape

**Asked:** What does one record look like, and which fields exist?

**Found:**
- 5,573 issues, 75,620 events (about 14 events per issue).
- Issue fields: `url, creator, labels, state, assignees, title, text, number, created_date, updated_date, timeline_url, events`.
- Event fields: `event_type, author, event_date, label, comment`.
- **There is no `closed_date` field on an issue.** Close dates must be derived from `closed` events.

**Decision:** any "time to close" analysis has to find the close event itself, which makes it non-trivial processing (a rubric requirement).

---

## Step 2 — Data quality

**Asked:** Can we trust every field? What is missing or malformed?

| Check | Result | Consequence |
|---|---|---|
| Events with no author | 184 | Must skip or label as unknown |
| Events with no date | 184 (mostly `labeled`, `subscribed`, `mentioned`) | `model.py` silently stores `None`; date arithmetic crashes unless these are skipped |
| Issues whose events are not in date order | 52 | Never assume the first or last list item is the earliest or latest; use `min` / `max` on dates |
| Issues with no labels at all | 909 | Label-based analyses must decide how to treat unlabeled issues |

**What it told us:** the template's `model.py` hides bad dates (`try/except: pass`), so problems only appear later as crashes. Our first exploration script actually crashed on a dateless `closed` event.

**Decision:** every feature must guard against missing dates and must not rely on event order. This logic is shared by all features, so it belongs in one helper module.

---

## Step 3 — What happens to issues

**Asked:** Which kinds of activity does the data record, and how much of each?

| Event type | Count | Event type | Count |
|---|---|---|---|
| commented | 29,461 | locked | 4,761 |
| labeled | 11,089 | unlabeled | 3,651 |
| subscribed | 6,151 | referenced | 1,884 |
| mentioned | 6,114 | renamed | 626 |
| cross-referenced | 6,065 | **assigned** | **151** |
| closed | 5,216 | **reopened** | **123** |

**What it told us:**
- Comments, labels and closes are rich, so they can support analyses on time-to-event and who does what.
- Assignments and reopens are rare, so analyses built on them would rest on too little data.

**Decision:** build on `commented`, `labeled`, `closed`. Drop assignee- and reopen-based ideas.

---

## Step 4 — How issues are categorised

**Asked:** Are labels usable as groups for comparison?

**Found:** labels follow three clean families.

| Family | Meaning | Top values |
|---|---|---|
| `kind/*` | What sort of issue | bug 2,860 · feature 855 · question 268 · enhancement 40 |
| `area/*` | Which part of Poetry | docs 257 · solver 180 · cli 131 · installer 116 · build-system 83 · venv 61 |
| `status/*` | Workflow state | triage 1,058 · duplicate 323 · external-issue 155 · needs-reproduction 67 |

1,553 issues have no `kind/` label.

**What it told us:** `kind/*` and `area/*` are natural dimensions to compare across. `status/*` describes process, not the issue itself.

**Decision:** use `kind/*` and `area/*` as grouping dimensions (Feature 1).

---

## Step 5 — Lifecycle: open vs. closed

**Asked:** How do issues end, and is "closed" always clean?

| State | Has `closed` event | Reopened | Issues |
|---|---|---|---|
| closed | yes | no | 4,943 |
| closed | yes | yes | 108 |
| closed | **no** | no | **205** |
| open | no | no | 308 |
| open | yes | yes | 9 |

Top closers: finswimmer 1,016 · neersighted 717 · sdispater 507 · abn 388. **172 issues were closed by `stale[bot]`** for inactivity.

**What it told us:**
- 205 issues are marked closed but have no close event, so their resolution time is unknown.
- Reopened issues have more than one close date.
- A bot closing an issue for inactivity is not a resolution.

**Decision:** for resolution time, use the last non-bot close date, exclude issues with no close event, and report how many were excluded.

---

## Step 6 — Time coverage

**Asked:** Does the data span enough time to show trends?

| Year | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|---|
| Issues | 587 | 721 | 1,052 | 823 | 1,125 | 810 | 455 |

The latest issue is from 20 October 2024, so **2024 is a partial year**.

**What it told us:** six full years is enough to compare years, but raw counts per year are misleading (2024 looks low only because it is incomplete).

**Decision:** trends over time should use rates or medians (comparable across years), not raw counts (Feature 3).

---

## Step 7 — People

**Asked:** Who is active, and do people behave differently?

**Found:**
- 7,629 distinct event authors. The most active is **`github-actions[bot]` (9,537 events)**, followed by `stale[bot]` (1,040). Bots must be excluded from any "people" analysis.
- Core maintainers have clearly different activity mixes:

| User | Main activities | Role |
|---|---|---|
| dimbleby | 2,803 comments, few labels | Answerer |
| abn | 1,178 unlabels, 388 closes | Triager / closer |
| finswimmer | 1,016 closes, 588 labels | Closer |
| neersighted | 1,006 unlabels, 767 labels, 717 closes | Triager |

- 3,664 people opened issues; **2,839 (77%) opened exactly one**. The top "creator" is `ghost`, GitHub's placeholder for deleted accounts.
- Only **144 issues (2.6%) have an assignee**.

**What it told us:** roles differ in a way that is visible from events alone, which makes a "who does what" analysis meaningful. Creator counts and assignees are not useful.

**Decision:** build a contributor-profile feature on event types (Feature 2), with the user as input. Drop "top creators" and "assignee workload".

---

## Step 8 — Quick checks for candidate features

Before committing, we computed the core number behind each candidate. We kept an idea only if the result varied enough to tell a story.

### A. Median days to close, by label (bot closes excluded, n ≥ 8)

| Label | n | Median days |
|---|---|---|
| area/error-handling | 35 | 692 |
| area/ux | 32 | 503 |
| area/cli | 113 | 248 |
| area/docs | 226 | 15 |
| kind/bug | 2,566 | 6.4 |
| kind/question | 263 | 0.2 |

**Verdict:** a spread of over 1,000× between groups gives a strong finding. **Kept → Feature 1.**

### B. Median hours to first response (non-author, non-bot), by year

| Year | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|---|
| Median hours | 20.9 | 108.2 | 25.3 | 87.2 | 1.5 | 1.0 | 0.9 |
| Never answered | 62 | 100 | 93 | 102 | 85 | 54 | 47 |

**Verdict:** a sharp change in 2022 is a clear trend. **Kept → Feature 3.**

### C. Reopened issues

117 issues (2.1%) were ever reopened.

**Verdict:** too few to compare across labels. **Dropped.**

---

## Summary: from exploration to features

| Exploration finding | Led to |
|---|---|
| No `closed_date`; close dates must be derived; medians differ hugely by label | **Feature 1** — Resolution time by area and kind |
| Maintainers have distinct, measurable event mixes; `--user` input already supported by template | **Feature 2** — Contributor profile |
| Six years of data; response time changes sharply in 2022 | **Feature 3** — Time to first response by year |
| Missing dates, unordered events, bot activity affect every feature | Shared helper module (`issue_utils.py`) |
| Subset is skewed toward 2024 | Report findings from the full dataset only |
| Assignees 2.6%, reopens 2.1%, top creator is `ghost` | Rejected alternatives (see `team_6_features.md`) |
