import requests
import json
import time

# GitHub token for authentication (replace with your actual token)
GITHUB_TOKEN = ""

# HTTP headers including authorization and required content type
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# Target repository (owner/repo format)
REPO = "python-poetry/poetry"
BASE_URL = f"https://api.github.com/repos/{REPO}/issues"

def fetch_issue_timeline(issue_number):
    """
    Fetches and filters the event timeline of a specific issue to include only:
    - event_type (e.g., commented, closed, labeled, etc.)
    - author (actor.login)
    - event_date (created_at)
    - optional label (for labeled events)
    - optional comment (for commented events)
    """

    timeline_url = f"https://api.github.com/repos/{REPO}/issues/{issue_number}/timeline"
    headers = HEADERS.copy()
    headers["Accept"] = "application/vnd.github.mockingbird-preview+json"

    response = requests.get(timeline_url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch timeline for issue {issue_number}")
        return []

    try:
        raw_events = response.json()
        filtered_events = []

        for event in raw_events:
            if not isinstance(event, dict):
                continue

            event_type = event.get("event")
            created_at = event.get("created_at")

            actor = event.get("actor", {})
            author = actor.get("login") if isinstance(actor, dict) else None

            filtered_event = {
                "event_type": event_type,
                "author": author,
                "event_date": created_at
            }

            # Optional: keep the label name if it's a labeled event
            if event_type == "labeled":
                label = event.get("label", {})
                if isinstance(label, dict):
                    filtered_event["label"] = label.get("name")

            # Optional: keep the comment body if it's a comment event
            if event_type == "commented":
                filtered_event["comment"] = event.get("body")

            # Add only relevant events for analysis
            if event_type in ["commented", "closed", "reopened", "labeled", "mentioned", "referenced", "subscribed", "assigned"]:
                filtered_events.append(filtered_event)

        return filtered_events

    except Exception as e:
        print(f"Error parsing timeline for issue #{issue_number}: {e}")
        return []


def format_issue(issue):
    """
    Formats a GitHub issue into a dictionary with selected fields.

    Args:
        issue (dict): Raw issue data from the GitHub API.

    Returns:
        dict: Formatted issue with useful fields and timeline events.
    """
    return {
        "url": issue.get("html_url"),
        "creator": issue.get("user", {}).get("login"),
        "labels": [label["name"] for label in issue.get("labels", [])],
        "state": issue.get("state"),
        "assignees": [assignee["login"] for assignee in issue.get("assignees", [])],
        "title": issue.get("title"),
        "text": (issue.get("body") or "").replace("\r", "\n"),
        "number": issue.get("number"),
        "created_date": issue.get("created_at"),
        "updated_date": issue.get("updated_at"),
        "timeline_url": f"https://api.github.com/repos/{REPO}/issues/{issue.get('number')}/timeline",
        "events": fetch_issue_timeline(issue.get("number"))
    }

def fetch_all_issues():
    """
    Fetches all issues from the repository, formats them, and collects timeline events.

    Returns:
        list: List of all formatted issues with timeline events.
    """
    all_issues = []
    page = 1
    per_page = 100  # GitHub API allows up to 100 items per page

    while True:
        print(f"Fetching page {page}...")
        params = {
            "state": "all",         # Fetch both open and closed issues
            "per_page": per_page,   # Number of issues per page
            "page": page
        }

        # Send request to fetch a page of issues
        response = requests.get(BASE_URL, headers=HEADERS, params=params)

        if response.status_code != 200:
            print("Error:", response.status_code, response.text)
            break

        issues = response.json()

        # Filter out pull requests (they also appear in /issues endpoint)
        issues = [i for i in issues if "pull_request" not in i]

        if not issues:
            break  # No more issues to fetch

        for issue in issues:
            try:
                formatted = format_issue(issue)
                all_issues.append(formatted)
                time.sleep(1.0)  # Rate limiting: avoid hitting GitHub API too fast
            except Exception as e:
                print(f"Skipping issue #{issue.get('number')} due to error: {e}")

        page += 1  # Move to next page

    return all_issues

if __name__ == "__main__":
    # Main execution: fetch issues and write to a JSON file
    issues = fetch_all_issues()
    with open("poetry.json", "w", encoding="utf-8") as f:
        json.dump(issues, f, indent=2)
    print(f"Saved {len(issues)} formatted issues to poetry.json")

