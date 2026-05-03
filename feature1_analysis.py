
from typing import List
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from data_loader import DataLoader
from model import Issue,Event
import config

class analysis_time_commit_hist:
    """
    Implements an example analysis of GitHub
    issues and outputs the result of that analysis.
    """
    
    def __init__(self):
        """
        Constructor
        """
        # Parameter is passed in via command line (--months)
        self.months = config.get_parameter('months', default=6)
    
    def run(self):
        """
        Plots number of commits in the last number of months
        """

        

        issues:List[Issue] = DataLoader().get_issues()

        # Extract created dates from Issue objects
        dates = [issue.created_date for issue in issues if issue.created_date]

        # Convert to DataFrame
        df = pd.DataFrame({"date": pd.to_datetime(dates)})

        # Filter last user specified number of months
        six_months_ago = pd.Timestamp.now(tz="UTC") - pd.DateOffset(months=self.months)
        df = df[df["date"] >= six_months_ago]

        # Group by week
        weekly_counts = df.set_index("date").resample("W").size()

        # Plot
        plt.figure(figsize=(10, 5))
        weekly_counts.plot(kind="line", marker="o")

        plt.title("Commits per Week (Last "+str(self.months) + " Months)")
        plt.xlabel("Week")
        plt.ylabel("Number of Commits")
        plt.grid(True)

        plt.tight_layout()
        plt.show()

    

if __name__ == '__main__':
    # Invoke run method when running this module directly
    analysis_time_commit_hist().run()