import numpy as np
from github import Github
from datetime import datetime


def format_issue(issue):
    issue_data = issue.raw_data
    try:
        issue_text = issue_data.get("body", "").replace("\r", "")
    except:
        issue_text = ''
    return {
        "url": issue_data.get("html_url"),
        "creator": issue_data.get("user", {}).get("login"),
        "labels": [label["name"] for label in issue_data.get("labels", [])],
        "state": issue_data.get("state"),
        "assignees": [assignee["login"] for assignee in issue_data.get("assignees", [])],
        "title": issue_data.get("title"),
        "text": issue_text,  # Preserving newlines and formatting
        "number": issue_data.get("number"),
        "created_date": issue_data.get("created_at"),
        "updated_date": issue_data.get("updated_at"),
        "timeline_url": f"https://api.github.com/repos/python-poetry/poetry/issues/{issue_data.get('number')}/timeline",
        "events": format_issue_events(issue)
    }
def format_issue_events(issue):
    events = issue.get_events() 
    all_event_info = []
    for event in events:
        created_at_dt = event.created_at
        created_at_str = created_at_dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        try:
            actorLogin = event.actor.login
        except:
            actorLogin = ''
        all_event_info.append({
            "event_type": event.event,
            "author": actorLogin,
            "event_date": created_at_str})
    return all_event_info
        

pat = "INSERT Personal access token from github here"
g = Github(pat)
repo = g.get_repo('python-poetry/poetry')

all_issues = repo.get_issues(state='all')

import json
all_info = []
ctr = 0

for issue in all_issues:
    #print(json.dumps(issue.raw_data, indent=2))

    data_dump = format_issue(issue)
    all_info.append(data_dump)
    ctr = ctr + 1
    print(ctr)
    
with open("./poetry.json", "w") as file:
    json.dump(all_info, file, indent=4)

