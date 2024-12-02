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
        
        all_labels = [label for issue in issues for label in issue.labels]
        print('\nNumber of unique labels:', len(set(all_labels)), '\n')        

        total_issues:int = len([issue for issue in issues if self.LABEL is None or self.LABEL in issue.labels])
            
        output:str = f'Found {total_issues} issues across {len(issues)} issues'
        output += f' with label {self.LABEL}.' if self.LABEL is not None else '.'
        print(output + '\n')
        
        ### BAR CHART
        # Display a graph of the top 50 labels
        top_n:int = 50
        # Create a dataframe to make statistics a lot easier
        df = pd.DataFrame(all_labels, columns=["label"])
        # Determine the number of issues for each creator and generate a bar chart of the top N
        df_hist = df.groupby(df["label"]).value_counts().nlargest(top_n).plot(kind="bar", figsize=(14,8), title=f"Top {top_n} labels")
        # Set axes labels
        df_hist.set_xlabel("Issue Labels")
        df_hist.set_ylabel("# of issues")
        # Plot the chart
        plt.show()
        
         
        
if __name__ == '__main__':
    # Invoke run method when running this module directly
    LabelAnalysis().run()
    
    
"""
Create a bar chart with label usage


"""