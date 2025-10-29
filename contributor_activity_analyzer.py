from collections import defaultdict
from typing import List, Dict
import matplotlib.pyplot as plt
from model import Issue, State

class ContributorActivityAnalyzer:
    """
    Analyzer for team engagement and workload distribution.
    """

    @staticmethod
    def get_active_issues_count_per_contributor(issues: List[Issue]) -> Dict[str, int]:
        active_issues_count = defaultdict(int)
        for issue in issues:
            if issue.state == State.open:
                for contributor in issue.assignees:
                    active_issues_count[contributor["login"]] += 1
        return dict(active_issues_count)

    @staticmethod
    def get_issue_type_distribution_per_contributor(issues: List[Issue]) -> Dict[str, Dict[str, int]]:
        contributor_distribution = defaultdict(lambda: defaultdict(int))
        for issue in issues:
            kinds = [label.split('/')[1] for label in issue.labels if label.startswith("kind/")]
            for contributor in issue.assignees:
                for kind in kinds:
                    contributor_distribution[contributor["login"]][kind] += 1
        return {contrib: dict(dist) for contrib, dist in contributor_distribution.items()}

    @staticmethod
    def plot_top_contributors_by_active_issues(issues: List[Issue]):
        counts = ContributorActivityAnalyzer.get_active_issues_count_per_contributor(issues)
        contributors = list(counts.keys())
        active_counts = list(counts.values())
        sorted_data = sorted(zip(contributors, active_counts), key=lambda x: x[1], reverse=True)
        sorted_contributors, sorted_counts = zip(*sorted_data)
        plt.figure(figsize=(10, 6))
        plt.barh(sorted_contributors, sorted_counts, color="skyblue")
        plt.xlabel("Number of Active Issues")
        plt.title("Active Issues per Contributor")
        plt.gca().invert_yaxis()
        plt.show()

    @staticmethod
    def plot_issue_type_distribution_per_contributor(issues: List[Issue]):
        distribution = ContributorActivityAnalyzer.get_issue_type_distribution_per_contributor(issues)
        contributors = list(distribution.keys())
        kinds = set(kind for dist in distribution.values() for kind in dist)
        kinds = sorted(kinds)
        data = {kind: [] for kind in kinds}
        for contributor in contributors:
            for kind in kinds:
                data[kind].append(distribution[contributor].get(kind, 0))
        plt.figure(figsize=(12, 6))
        bottom = [0] * len(contributors)
        colors = plt.cm.tab20.colors
        for i, kind in enumerate(kinds):
            plt.barh(contributors, data[kind], left=bottom, color=colors[i % len(colors)], label=kind)
            bottom = [bottom[j] + data[kind][j] for j in range(len(bottom))]
        plt.xlabel("Number of Issues")
        plt.ylabel("Contributors")
        plt.title("Issue Distribution by Kind per Contributor")
        plt.legend(title="Issue Kind")
        plt.gca().invert_yaxis()
        plt.show()
