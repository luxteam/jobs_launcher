import os
import json
import argparse
from core.config import *


def main():
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument('--work_dir')
    args = args_parser.parse_args()

    status_to_export = {}

    if os.path.exists(os.path.join(args.work_dir, SUMMARY_REPORT)):
        with open(os.path.join(args.work_dir, SUMMARY_REPORT), 'r') as file:
            summary_report = json.load(file.read())

            for execution in summary_report:
                status_to_export.update({execution: summary_report[execution]['summary']})



if __name__ == '__main__':
    exit(main())