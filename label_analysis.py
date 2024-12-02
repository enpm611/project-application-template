from typing import List
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from data_loader import DataLoader
from model import Issue, Event
import config

class LabelAnalysis:
    """
    dd
    """
    
    def __init__(self):
        """
        Constructor
        """
        # Parameter is passed in via command line (--label)
        self.LABEL:str = config.get_parameter('label')
        
    def run(self):
        """
        Run the label analysis
        """
        issues:List[Issue] = DataLoader().get_issues()
        
        # Store the labels in a list, create set of unique labels
        all_labels = [label for issue in issues for label in issue.labels]
        unique_labels = set(all_labels)
        print('\nNumber of unique labels:', len(unique_labels), '\n')

        # Count the number of issues with a specific label
        total_issues:int = len([issue for issue in issues if self.LABEL is None or self.LABEL in issue.labels])
            
        output:str = f'Found {total_issues} issues across {len(issues)} issues'
        output += f' with label {self.LABEL}.' if self.LABEL is not None else '.'
        print(output + '\n')
        
        ### BAR CHART
        # Display a graph of the top 50 labels
        top_num:int = 20
        # Create a dataframe to make statistics a lot easier
        df = pd.DataFrame(all_labels, columns=["label"])
        # Determine the number of issues for each creator and generate a bar chart of the top N
        df_hist = df.groupby(df["label"]).value_counts().nlargest(top_num).plot(kind="bar", figsize=(14,8), title=f"Top {top_num} labels")
        # Set axes labels
        df_hist.set_xlabel("Issue Labels")
        df_hist.set_ylabel("# of issues")
        # Plot the chart
        plt.show()
        
        # Show creation trends over time for user inputted parameter label
        if self.LABEL is None:
            exit()
        
        label_list = [{"date": issue.created_date, "label": label} for issue in issues for label in issue.labels if label == self.LABEL]
                
        df = pd.DataFrame(label_list)
        df["month"] = df["date"].dt.to_period("M")
        label_trends = df.groupby(["month", "label"]).size().unstack(fill_value=0)
        
        # Plot trends
        label_trends.plot(figsize=(12, 6))
        plt.title("Label Trends Over Time")
        plt.xlabel("Month")
        plt.ylabel("Number of Issues")
        plt.legend(title="Labels")
        plt.grid()
        plt.tight_layout()
        plt.show()
        
        
if __name__ == '__main__':
    # Invoke run method when running this module directly
    LabelAnalysis().run()
    
    
"""
Create a bar chart with label usage


"""