import os
import argparse
import json
import CompareMetrics
import sys
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


def get_pixel_difference(work_dir, base_dir, img, baseline_json, tolerance, pix_diff_max):

    for key in core.config.POSSIBLE_JSON_IMG_RENDERED_KEYS:
        if key in img.keys():
            render_img_path = os.path.join(work_dir, img[key])

            try:
                baseline_img_path = os.path.join(base_dir, baseline_json[img['file_name']])
            except KeyError as err:
                core.config.main_logger.error("No such file in baseline: {}".format(str(err)))
                continue

            if not os.path.exists(baseline_img_path):
                core.config.main_logger.error("BROKEN BASELINE MANIFEST")
                continue

            metrics = None
            try:
                metrics = CompareMetrics.CompareMetrics(render_img_path, baseline_img_path)
            except (FileNotFoundError, OSError) as err:
                core.config.main_logger.error(str(err))
                return img

            pix_difference = metrics.getDiffPixeles(tolerance=tolerance)
            img.update({'difference_color': pix_difference})
            if type(pix_difference) is str or pix_difference > pix_diff_max:
                # TODO: swap status
                img['test_status'] = 'error'
            img.update({'baseline_color_path': os.path.relpath(
                os.path.join(base_dir, baseline_json[img['file_name']]), work_dir)})

    return img


def get_rendertime_difference(base_dir, img, time_diff_max):
    if os.path.exists(os.path.join(base_dir, img['test_group'], core.config.BASELINE_REPORT_NAME)):
        render_time = img['render_time']
        with open(os.path.join(base_dir, img['test_group'], core.config.BASELINE_REPORT_NAME), 'r') as file:
            try:
                baseline_time = [x for x in json.loads(file.read()) if x['test_case'] == img['test_case']][0]['render_time']
            except IndexError:
                baseline_time = -0.0

        def get_diff():
            if render_time == baseline_time:
                return 0.0
            try:
                return (render_time - baseline_time) / baseline_time * 100.0
            except ZeroDivisionError:
                return 0

        img.update({'difference_time': get_diff()})
        img.update({'baseline_render_time': baseline_time})
    else:
        img.update({'difference_time': -0.0})
        img.update({'baseline_render_time': -0.0})

    return img


def main():
    args = createArgParser().parse_args()

    render_json_path = os.path.join(args.work_dir, core.config.TEST_REPORT_NAME)
    baseline_json_path = os.path.join(args.base_dir, core.config.BASELINE_MANIFEST)

    if not os.path.exists(render_json_path):
        core.config.main_logger.error("Render report doesn't exists")
        return

    if not os.path.exists(args.base_dir) or not os.path.exists(baseline_json_path):
        core.config.main_logger.warning("Baseline or manifest not found by path: {}".format(args.base_dir))

        try:
            with open(render_json_path, 'r') as file:
                render_json = json.loads(file.read())
                for img in render_json:
                    img['baseline_render_time'] = -0.0
                    img['difference_time'] = -0.0
        except Exception as err:
            core.config.main_logger.error("Can't read report.json: {}".format(str(err)))
        else:
            with open(os.path.join(args.work_dir, core.config.TEST_REPORT_NAME_COMPARED), 'w') as file:
                json.dump(render_json, file, indent=4)
        finally:
            return

    with open(render_json_path, 'r') as file:
        render_json = json.loads(file.read())

    with open(baseline_json_path, 'r') as file:
        baseline_json = json.loads(file.read())

    for img in render_json:
        # if failed it means tool crash - no sense to compare images
        if img['test_status'] != core.config.TEST_CRASH_STATUS:
            img.update(get_pixel_difference(args.work_dir, args.base_dir, img, baseline_json, args.pix_diff_tolerance, args.pix_diff_max))

            img.update(get_rendertime_difference(args.base_dir, img, args.time_diff_max))
        else:
            img['difference_time'] = -0.0
            img['baseline_render_time'] = -0.0

    with open(os.path.join(args.work_dir, core.config.TEST_REPORT_NAME_COMPARED), 'w') as file:
        json.dump(render_json, file, indent=4)


if __name__ == '__main__':
    main()
