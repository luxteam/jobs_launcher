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

    summary_report = {}
    total = {'total': 0, 'passed': 0, 'failed': 0, 'error': 0, 'skipped': 0, 'duration': 0, 'render_duration': 0}

    if os.path.exists(os.path.join(args.work_dir, SUMMARY_REPORT)):
        with open(os.path.join(args.work_dir, SUMMARY_REPORT), 'r') as file:
            summary_report = json.load(file)

            for execution in summary_report:
                # status_to_export.update({execution: summary_report[execution]['summary']})
                status_to_export += "_{}:_ `total: {}` `passed: {}` `failed: {}` `pixel difference: {}` `skipped: {}`\n".format(
                    execution,
                    summary_report[execution]['summary']['total'],
                    summary_report[execution]['summary']['passed'],
                    summary_report[execution]['summary']['failed'],
                    summary_report[execution]['summary']['error'],
                    summary_report[execution]['summary']['skipped']
                )

    # get summary results
    for execution in summary_report:
        for key in total:
            total[key] += summary_report[execution]['summary'][key]

    with open(os.path.join(args.work_dir, 'summary_status.json'), 'w') as file:
        json.dump(total, file, indent=' ')

    with open(os.path.join(args.work_dir, 'slack_status.json'), 'w') as file:
        json.dump(status_to_export, file, indent=' ')

    exit_code = sum([int(summary_report[x]['summary']['failed']) + int(summary_report[x]['summary']['error']) for x in summary_report])
    # exit_code = [x for x in summary_report]
    return exit_code


if __name__ == '__main__':
    if main():
        exit(-1)
