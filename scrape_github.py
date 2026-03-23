import numpy as np
from github import Github

#pat = # INSERT PAT HERE
g = Github(pat)
repo = g.get_repo('python-poetry/poetry')

all_issues = repo.get_issues(state='all')

import json
for issue in all_issues:
    print(json.dumps(issue.raw_data, indent=2))

    breakpoint()
    # In Progress
