import sys
import argparse
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir, os.path.pardir)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir, os.path.pardir, os.path.pardir)))
import core.config
from local_config import *


def createArgParser():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--work_dir')
    argparser.add_argument('--base_dir')
    if report_type == 'ct':
        argparser.add_argument('--case_suffix')
    argparser.add_argument('--pix_diff_tolerance', required=False, default=core.config.PIX_DIFF_TOLERANCE)
    argparser.add_argument('--pix_diff_max', required=False, default=core.config.PIX_DIFF_MAX)
    argparser.add_argument('--time_diff_max', required=False, default=core.config.TIME_DIFF_MAX)
    if report_type == 'ec':
        argparser.add_argument('--vram_diff_max', required=False, default=core.config.VRAM_DIFF_MAX)
    return argparser


if __name__ == '__main__':
    args = createArgParser().parse_args()
    if report_type == 'default':
        import common.scripts.ImageComparator.compareByJSON_default as compareByJSON
    elif report_type == 'ct':
        import common.scripts.ImageComparator.compareByJSON_ct as compareByJSON
    elif report_type == 'ec':
        import common.scripts.ImageComparator.compareByJSON_ec as compareByJSON
    compareByJSON.main(args)
