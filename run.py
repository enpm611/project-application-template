import argparse
from importlib.metadata import requires
from data_loader import DataLoader
from issue_trend_analysis import IssueTrendAnalysis
from label_activity_analysis import LabelActivityAnalysis
from contributor_activity_analysis import ContributorActivityAnalysis
data_loader = DataLoader()

def parse_args(args=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--feature", "-f", required=True)
    ap.add_argument("--user")
    ap.add_argument("--label")
    return ap.parse_args(args)

def main():
    args = parse_args()

    issues = DataLoader("poetry_issues.json")


    if args.feature == "1":
        analysis = IssueTrendAnalysis()
        analysis.run()

    elif args.feature == "2":
        analysis = LabelActivityAnalysis()
        analysis.run()

    elif args.feature == "3":
        analysis = ContributorActivityAnalysis()
        analysis.run()

    else:
        print("Invalid feature")
def load_data():
    return DataLoader("poetry_issues.json").get_issues()

if __name__ == "__main__":
    main()