import os
import json
import argparse
from core.config import *


def main(work_dir=''):
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument('--work_dir')
    args = args_parser.parse_args()

    status_to_export = ""
    if work_dir:
        args.work_dir = work_dir

    if os.path.exists(os.path.join(args.work_dir, SUMMARY_REPORT)):
        with open(os.path.join(args.work_dir, SUMMARY_REPORT), 'r') as file:
            summary_report = json.load(file)

            for execution in summary_report:
                # status_to_export.update({execution: summary_report[execution]['summary']})
                status_to_export += "_{}:_ `failed: {}` `error: {}` `passed: {}` `skipped: {}`\\n".format(
                    execution, summary_report[execution]['summary']['failed'],
                    summary_report[execution]['summary']['error'],
                    summary_report[execution]['summary']['passed'],
                    summary_report[execution]['summary']['skipped']
                )

    with open(os.path.join(args.work_dir, 'slack_status.json'), 'w') as file:
        json.dump(status_to_export, file, indent=' ')


if __name__ == '__main__':
    exit(main())