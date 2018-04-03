import os
import argparse
import json
import CompareMetrics
import sys
import shutil
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir, os.path.pardir)))
import core.config


def createArgParser():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--render_path')
    argparser.add_argument('--baseline_path')
    argparser.add_argument('--result_json', required=False)

    return argparser


def main():
    args = createArgParser().parse_args()

    if not os.path.exists(args.baseline_path):
        core.config.main_logger.info("Baseline not found by path: {}".format(args.baseline_path))
        shutil.copyfile(os.path.join(args.render_path, core.config.TEST_REPORT_NAME), os.path.join(args.render_path, core.config.TEST_REPORT_NAME_COMPARED))
        return

    render_json = []
    baseline_json = []

    with open(os.path.join(args.render_path, core.config.TEST_REPORT_NAME), 'r') as file:
        render_json = json.loads(file.read())

    with open(os.path.join(args.baseline_path, core.config.BASELINE_MANIFEST), 'r') as file:
        baseline_json = json.loads(file.read())

    for img in render_json:
        for key in core.config.POSSIBLE_JSON_IMG_RENDERED_KEYS:
            if key in img.keys():
                render_img_path = os.path.join(args.render_path, img[key])
                try:
                    baseline_img_path = os.path.join(args.baseline_path, baseline_json[img['file_name']])
                except KeyError as err:
                    core.config.main_logger.error("No such file in baseline: {}".format(str(err)))
                    continue

                metrics = CompareMetrics.CompareMetrics(render_img_path, baseline_img_path)

                img.update({'pix_difference': metrics.getDiffPixeles()})
                img.update({'baseline_path': os.path.relpath(os.path.join(args.baseline_path, baseline_json[img['file_name']]), args.render_path)
                            })

    with open(os.path.join(args.render_path, core.config.TEST_REPORT_NAME_COMPARED), 'w') as file:
        json.dump(render_json, file, indent=" ")


if __name__ == '__main__':
    main()
