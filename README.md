# Poetry Issues

An interactive dashboard for exploring Poetry’s GitHub issues: what remains open, where work is aging, and which issues need attention.

Built from the ENPM611 project template, Poetry Issues combines searchable issue history, visual analytics, and local severity classification.

## Dataset

The application uses `poetry_issues_all.json`. The smaller export is retained for validation; the files are not combined because their issue numbers overlap.

| Metric | Count |
|---|---:|
| Total issues | 5,573 |
| Open / closed | 317 / 5,256 |
| Bug-labeled issues | 2,860 |
| Open bug-labeled issues | 164 |
| Recorded comment events | 29,461 |

## Features

- **Overview:** open, closed, and bug-labeled totals.
- **Issue explorer:** search and filter by state, type, severity, ownership, and age.
- **Backlog aging:** clickable age bands reveal long-waiting issues.
- **Monthly trends:** compare issue creation and final recorded closures.
- **Calendar heat map:** explore daily creation activity by year.
- **Issue details:** descriptions, comments, recorded timelines, and GitHub links.
- **Manual severity:** save Critical, Major, Minor, or Unclassified locally.

All visualizations follow the dashboard filters.

## Interpreting the Data

**Issue type and severity answer different questions.** Type describes the work; severity describes its impact. Types come from explicit labels. The export contains no task/project or severity labels, so these classifications are not inferred.

Manual severity choices update the dashboard, persist across restarts, and remain separate from GitHub labels. They can be removed to restore the original classification.

Three distinctions matter:

- **Closed does not mean fixed.** Issues may be duplicates, invalid reports, or declined requests.
- **Current ownership does not prove who resolved an issue.** Historical assignment evidence is incomplete.
- **Missing dates are not zero durations.** Of the closed issues, 223 lack a usable closure date.

Open-issue age is measured at the historical reference. Closed duration runs from creation to the final recorded closure, including intervening closed periods. Comment counts reflect collected events; completeness is unverified.

## Architecture

| Component | Purpose |
|---|---|
| `analytics.py` | Normalize data, classify issues, and calculate metrics |
| `app.py` | Serve the dashboard and API; manage SQLite storage |
| `web/` | Interface, interactions, and styling |
| `tests/` | Metric, persistence, classification, and calendar checks |

Source JSON remains unchanged. SQLite stores the active snapshot and separate manual severity overrides.

### Diagrams

> **Original template component diagram**  
> Asset: `team_5_component_diagram_before.svg.svg`

> **Proposed template extension**  
> Asset: `team_5_component_diagram_after.svg.svg`

> **Proposed contributor-analysis sequence**  
> Asset: `team_5_sequence_diagram.svg.svg`

The proposed diagrams reference planned command-line modules, not the current dashboard.

> **Current dashboard architecture**  
> JSON import → normalization → SQLite → API → dashboard

## Run Locally

Requires Python 3.10+ and a modern browser. No third-party Python packages are needed.

```sh
python3 app.py \
  --data /path/to/poetry_issues_all.json \
  --observed-at 2024-10-20T17:19:04+00:00
```

Open **http://127.0.0.1:8765/**.

For later sessions, run `python3 app.py` to reuse stored data. Stop with `Ctrl+C`.

## Verification

```sh
python3 -m unittest discover -s tests -v
node tests/test_calendar.cjs
node --check web/app.js
```


