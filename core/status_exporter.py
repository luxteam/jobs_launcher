import os
import json
import argparse
from core.config import *


def main(work_dir):
    if os.path.exists(os.path.join(work_dir, SUMMARY_REPORT)):
        with open(os.path.join(work_dir, SUMMARY_REPORT), 'r') as file:
            summary_report = json.load(file.read())

    for execution in summary_report:
        pass


if __name__ == '__main__':
    exit(main())