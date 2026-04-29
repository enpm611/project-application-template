from typing import List
import matplotlib.pyplot as plt
import pandas as pd

from data_loader import DataLoader
from model import Issue
import config


class ExampleAnalysis:
    """
    Implements an example analysis of GitHub
    issues and outputs the result of that analysis.
    """

    def run(self):
        issues: List[Issue] = DataLoader().get_issues()

        if not issues:
            print("No issues found in dataset.")
            return

        data = []
        for issue in issues:
            data.append({
                "creator": getattr(issue, "creator", None),
                "state": getattr(issue.state, "value", None) if getattr(issue, "state", None) else None,
                "num_events": len(getattr(issue, "events", []) or []),
                "num_labels": len(getattr(issue, "labels", []) or []),
                "created_date": getattr(issue, "created_date", None)
            })

        df = pd.DataFrame(data)

        if df.empty:
            print("No data available for analysis.")
            return

        print("\nBasic Dataset Info:")
        print(df.head())

    
        if "creator" not in df.columns or df["creator"].isna().all():
            print("\nNo valid 'creator' data available.")
            return

        top_n = 10

        print("\nTop issue creators:")
        creator_counts = df["creator"].value_counts().head(top_n)

        for creator, count in creator_counts.items():
            print(f"  {creator}: {count}")

   
        if not creator_counts.empty:
            plt.figure(figsize=(14, 8))
            creator_counts.plot(kind="bar")
            plt.title(f"Top {top_n} Issue Creators")
            plt.xlabel("Creator")
            plt.ylabel("Number of Issues")
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show()
