"""
Starting point of the application. This module is invoked from
the command line to run the analyses.
"""

import argparse

import config
from example_analysis import ExampleAnalysis
from feature2_contributor_expertise import run_feature_2
from feature3 import feature3


def parse_args():
    ap = argparse.ArgumentParser("run.py")
    ap.add_argument('--feature', '-f', type=int, required=True,
                    help='Which of the three features to run')
    ap.add_argument('--user', '-u', type=str, required=False,
                    help='Optional parameter for analyses focusing on a specific user')
    ap.add_argument('--label', '-l', type=str, required=False,
                    help='Optional parameter for analyses focusing on a specific label')
    return ap.parse_args()


args = parse_args()
config.overwrite_from_args(args)

if args.feature == 0:
    ExampleAnalysis().run()
elif args.feature == 1:
    pass  # TODO
elif args.feature == 2:
    run_feature_2()
elif args.feature == 3:
    feature3()
else:
    print('Need to specify which feature to run with --feature flag.')
