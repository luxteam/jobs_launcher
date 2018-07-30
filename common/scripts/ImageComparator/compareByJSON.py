import os
import argparse
import json
import CompareMetrics
import sys
import shutil
from PIL import Image
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir, os.path.pardir)))
import core.config


def createArgParser():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--work_dir')
    argparser.add_argument('--base_dir')
    return argparser


def main():
    args = createArgParser().parse_args()

    if not os.path.exists(args.base_dir):
        core.config.main_logger.info("Baseline not found by path: {}".format(args.base_dir))
        shutil.copyfile(os.path.join(args.work_dir, core.config.TEST_REPORT_NAME), os.path.join(args.work_dir, core.config.TEST_REPORT_NAME_COMPARED))
        return

    render_json = []
    baseline_json = []

    with open(os.path.join(args.work_dir, core.config.TEST_REPORT_NAME), 'r') as file:
        render_json = json.loads(file.read())

    with open(os.path.join(args.base_dir, core.config.BASELINE_MANIFEST), 'r') as file:
        baseline_json = json.loads(file.read())

    for img in render_json:
        for key in core.config.POSSIBLE_JSON_IMG_RENDERED_KEYS:
            if key in img.keys():
                render_img_path = os.path.join(args.work_dir, img[key])

                try:
                    baseline_img_path = os.path.join(args.base_dir, baseline_json[img['file_name']])
                except KeyError as err:
                    core.config.main_logger.error("No such file in baseline: {}".format(str(err)))
                    continue

                metrics = None
                try:
                    metrics = CompareMetrics.CompareMetrics(render_img_path, baseline_img_path)
                except FileNotFoundError as err:
                    core.config.main_logger.error(str(err))

                pix_difference = metrics.getDiffPixeles()
                img.update({'difference_color': pix_difference})
                if type(pix_difference) is not str and pix_difference > core.config.PIX_DIFF_MAX:
                    img['test_status'] = 'failed'
                img.update({'baseline_color_path': os.path.relpath(os.path.join(args.base_dir, baseline_json[img['file_name']]), args.work_dir)})


    with open(os.path.join(args.work_dir, core.config.TEST_REPORT_NAME_COMPARED), 'w') as file:
        json.dump(render_json, file, indent=" ")


if __name__ == '__main__':
    main()
