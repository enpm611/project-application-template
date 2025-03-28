
import json
from typing import List
import os

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
        Loads the issues into memory using a chunked reading approach.
        This allows handling large JSON files without loading the entire file at once.
        """
        issues = []

        # Get file size to determine if we need chunked processing
        file_size = os.path.getsize(self.data_path)

        # If file is small enough, use standard json.load
        if file_size < 10 * 1024 * 1024:  # Less than 10MB
            with open(self.data_path, 'r') as fin:
                return [Issue(i) for i in json.load(fin)]

        # For large files, use chunked reading
        with open(self.data_path, 'r') as fin:
            # Read the opening bracket
            char = fin.read(1)
            if char != '[':
                raise ValueError("JSON file must start with '['")

            # Read the file chunk by chunk
            buffer = ""
            depth = 0
            in_string = False
            escape_next = False

            while True:
                chunk = fin.read(8192)  # Read 8KB at a time
                if not chunk:
                    break

                for char in chunk:
                    buffer += char

                    # Handle string literals
                    if char == '"' and not escape_next:
                        in_string = not in_string
                    elif char == '\\' and in_string and not escape_next:
                        escape_next = True
                        continue

                    if escape_next:
                        escape_next = False
                        continue

                    # Only process structural characters outside of strings
                    if not in_string:
                        if char == '{':
                            depth += 1
                        elif char == '}':
                            depth -= 1
                            # If we've closed an object at the top level, process it
                            if depth == 0:
                                # Remove trailing comma if present
                                if buffer.endswith(','):
                                    buffer = buffer[:-1]

                                try:
                                    # Parse the JSON object
                                    issue_obj = json.loads(buffer)
                                    issues.append(Issue(issue_obj))
                                except json.JSONDecodeError as e:
                                    print(f"Error parsing JSON object: {e}")

                                # Reset buffer for next object
                                buffer = ""
                        elif char == ',' and depth == 0:
                            # Skip commas between top-level objects
                            buffer = ""

        return issues


if __name__ == '__main__':
    # Run the loader for testing
    DataLoader().get_issues()
