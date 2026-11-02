

"""
Starting point of the application. This module is invoked from
the command line to run the analyses.
"""

import argparse
import os
import sys

import config


def parse_args():
    """
    Parses the command line arguments that were provided along
    with the python command. The --feature flag must be provided as
    that determines what analysis to run. Optionally, you can pass in
    a user and/or a label to run analysis focusing on specific issues.
    
    You can also add more command line arguments following the pattern
    below.
    """
    ap = argparse.ArgumentParser("run.py")
    
    # Required parameter specifying what analysis to run
    ap.add_argument('--feature', '-f', type=int, required=True,
                    help='Which feature to run: 0 example, 1 label resolution, 2 contributor activity, 3 issue trend')
    
    # Optional parameter for analyses focusing on a specific user (i.e., contributor)
    ap.add_argument('--user', '-u', type=str, required=False,
                    help='Optional parameter for analyses focusing on a specific user')
    
    # Optional parameter for analyses focusing on a specific label
    ap.add_argument('--label', '-l', type=str, required=False,
                    help='Optional parameter for analyses focusing on a specific label')
    
    return ap.parse_args()



# Parse feature to call from command line arguments
args = parse_args()
# Add arguments to config so that they can be accessed in other parts of the application
config.overwrite_from_args(args)
    
def check_data_file():
    """
    Stops with a clear message when the data file is not configured or missing,
    instead of failing with a stack trace inside the analysis.
    """
    data_path = config.get_parameter('ENPM611_PROJECT_DATA_PATH')
    if not data_path or not os.path.isfile(str(data_path)):
        print(f'Data file not found: {data_path}\n'
              'Set ENPM611_PROJECT_DATA_PATH in config.json or as an environment variable '
              '(see README, "Configure the data file").')
        sys.exit(1)


if args.feature in (0, 1, 2, 3):
    check_data_file()

# Run the feature specified in the --feature flag
# Each analysis is imported only when selected, so one feature
# does not depend on the other analysis modules being present.
if args.feature == 0:
    from example_analysis import ExampleAnalysis
    ExampleAnalysis().run()
elif args.feature == 1:
    from label_resolution_analysis import LabelResolutionAnalysis
    LabelResolutionAnalysis().run()
elif args.feature == 2:
    from contributor_activity_analysis import ContributorActivityAnalysis
    ContributorActivityAnalysis().run()
elif args.feature == 3:
    from issue_trend_analysis import IssueTrendAnalysis
    IssueTrendAnalysis().run()
else:
    print('Unknown feature. Use --feature 1, 2 or 3 (or 0 for the template example).')
