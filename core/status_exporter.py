import os
import json
import argparse
from core.config import *


def main(work_dir):
    status_to_export = []

    if os.path.exists(os.path.join(work_dir, SUMMARY_REPORT)):
        with open(os.path.join(work_dir, SUMMARY_REPORT), 'r') as file:
            summary_report = json.load(file.read())

    for execution in summary_report:
        for status in execution['summary'].keys():
            status_to_export[status] += execution['summary'][status]




if __name__ == '__main__':
    exit(main())