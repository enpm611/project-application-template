
import json
from typing import List
from model import Issue


class DataLoader:
    def __init__(self, filepath: str = None):
        self.filepath = filepath

    def get_issues(self) -> List[Issue]:
        if not self.filepath:
            return []

        try:
            with open(self.filepath, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            return []

        issues = []
        for item in data:
            issues.append(Issue(item))

        return issues

    def load_data(self):
        return self.get_issues()
