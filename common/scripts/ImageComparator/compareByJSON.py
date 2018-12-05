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
    argparser.add_argument('--work_dir')
    argparser.add_argument('--base_dir')
    argparser.add_argument('--pix_diff_tolerance', required=False, default=core.config.PIX_DIFF_TOLERANCE)
    argparser.add_argument('--pix_diff_max', required=False, default=core.config.PIX_DIFF_MAX)
    argparser.add_argument('--time_diff_max', required=False, default=core.config.TIME_DIFF_MAX)
    return argparser


def get_pixel_difference(work_dir, base_dir, img, baseline_json):

    for key in core.config.POSSIBLE_JSON_IMG_RENDERED_KEYS:
        if key in img.keys():
            render_img_path = os.path.join(work_dir, img[key])

            try:
                baseline_img_path = os.path.join(base_dir, baseline_json[img['file_name']])
            except KeyError as err:
                core.config.main_logger.error("No such file in baseline: {}".format(str(err)))
                continue

            metrics = None
            try:
                metrics = CompareMetrics.CompareMetrics(render_img_path, baseline_img_path)
            except FileNotFoundError as err:
                core.config.main_logger.error(str(err))

            pix_difference = metrics.getDiffPixeles(tolerance=9)
            img.update({'difference_color': pix_difference})
            if type(pix_difference) is str or pix_difference > core.config.PIX_DIFF_MAX:
                img['test_status'] = 'error'
            img.update({'baseline_color_path': os.path.relpath(
                os.path.join(base_dir, baseline_json[img['file_name']]), work_dir)})

    return img


def get_rendertime_difference(base_dir, img):
    render_time = img['render_time']
    with open(os.path.join(base_dir, img['test_group'], core.config.BASELINE_REPORT_NAME), 'r') as file:
        baseline_time = [x for x in json.loads(file.read()) if x['test_case'] == img['test_case']][0]['render_time']

    def get_diff():
        if render_time == baseline_time:
            return 0.0
        try:
            return (abs(render_time - baseline_time) / baseline_time) * 100.0
        except ZeroDivisionError:
            return 0

    img.update({'difference_time': get_diff()})

    return img


def main():
    args = createArgParser().parse_args()

    if not os.path.exists(args.base_dir):
        core.config.main_logger.warning("Baseline not found by path: {}".format(args.base_dir))
        with open(os.path.join(args.work_dir, core.config.TEST_REPORT_NAME), 'r') as file:
            render_json = json.loads(file.read())
            for img in render_json:
                img['baseline_render_time'] = -0.0
        with open(os.path.join(args.work_dir, core.config.TEST_REPORT_NAME_COMPARED), 'w') as file:
            json.dump(render_json, file, indent=4)
        return

    with open(os.path.join(args.work_dir, core.config.TEST_REPORT_NAME), 'r') as file:
        render_json = json.loads(file.read())

    with open(os.path.join(args.base_dir, core.config.BASELINE_MANIFEST), 'r') as file:
        baseline_json = json.loads(file.read())

    for img in render_json:
        # if failed it means tool crash - no sense to compare images
        if img['test_status'] != core.config.TEST_CRASH_STATUS:
            img.update(get_pixel_difference(args.work_dir, args.base_dir, img, baseline_json))

            img.update(get_rendertime_difference(args.base_dir, img))
        else:
            img['difference_color'] = -0.0
            img['difference_time'] = -0.0
            img['baseline_render_time'] = -0.0

    with open(os.path.join(args.work_dir, core.config.TEST_REPORT_NAME_COMPARED), 'w') as file:
        json.dump(render_json, file, indent=4)


if __name__ == '__main__':
    main()
