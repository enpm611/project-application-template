
import json
import os
from typing import List

import config
from model import Issue

# Store issues as singleton to avoid reloads
_ISSUES:List[Issue] = None

class DataLoader:
    """
    Loads the issue data into a runtime object.
    """
    
    def __init__(self):
        """
        Constructor
        """
        self.data_path:str = config.get_parameter('ENPM611_PROJECT_DATA_PATH')
        
    def get_issues(self):
        """
        This should be invoked by other parts of the application to get access
        to the issues in the data file.
        """
        global _ISSUES # to access it within the function
        if _ISSUES is None:
            _ISSUES = self._load()
            print(f'Loaded {len(_ISSUES)} issues from {self.data_path}.')
        return _ISSUES
    
    def _load(self):
        """
        Loads the issues into memory.
        """
        if not self.data_path or not os.path.isfile(str(self.data_path)):
            raise FileNotFoundError(
                f'Data file not found: {self.data_path!r}. Set ENPM611_PROJECT_DATA_PATH '
                '(environment variable or config.json) to the path of the issues JSON file.')
        with open(self.data_path,'r') as fin:
            return [Issue(i) for i in json.load(fin)]
    

if __name__ == '__main__':
    # Run the loader for testing
    DataLoader().get_issues()