import os
import argparse
import json
import CompareMetrics
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir, os.path.pardir)))
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
    if 'render_color_path' in img.keys():
        baseline_img_path = os.path.join(base_dir, baseline_json.get(img.get('file_name', ''), ''))
        # if baseline image not found - return
        if not os.path.exists(baseline_img_path):
            core.config.main_logger.error("Baseline image not found by path: {}".format(baseline_img_path))
            return img

        # else add baseline images paths to json
        img.update({'baseline_color_path': os.path.relpath(os.path.join(base_dir, baseline_json[img['file_name']]), work_dir)})
        for thumb in core.config.THUMBNAIL_PREFIXES:
            if thumb + img['file_name'] in baseline_json.keys() and os.path.exists(os.path.join(base_dir, baseline_json[thumb + img['file_name']])):
                img.update({thumb + 'baseline_color_path': os.path.relpath(os.path.join(base_dir, baseline_json[thumb + img['file_name']]), work_dir)})

        render_img_path = os.path.join(work_dir, img['render_color_path'])
        if not os.path.exists(render_img_path):
            core.config.main_logger.error("Rendered image not found by path: {}".format(render_img_path))
            return img

        metrics = None
        try:
            metrics = CompareMetrics.CompareMetrics(render_img_path, baseline_img_path)
        except (FileNotFoundError, OSError) as err:
            core.config.main_logger.error("Error during metrics calculation: {}".format(str(err)))
            return img

        pix_difference = metrics.getDiffPixeles(tolerance=tolerance)
        img.update({'difference_color': pix_difference})
        if type(pix_difference) is str or pix_difference > float(pix_diff_max):
            img['test_status'] = core.config.TEST_DIFF_STATUS

    return img


def get_rendertime_difference(base_dir, img, time_diff_max):
    if os.path.exists(os.path.join(base_dir, img['test_group'], core.config.BASELINE_REPORT_NAME)):
        render_time = img['render_time']
        with open(os.path.join(base_dir, img['test_group'], core.config.BASELINE_REPORT_NAME), 'r') as file:
            try:
                baseline_time = [x for x in json.loads(file.read()) if x['test_case'] == img['test_case']][0][
                    'render_time']
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

    # create report_compared.json before calculation to provide stability
    try:
        with open(render_json_path, 'r') as file:
            render_json = json.loads(file.read())
            for img in render_json:
                img.update({'baseline_render_time' : -0.0})
                img.update({'difference_time': -0.0})
    except (FileNotFoundError, OSError) as err:
        core.config.main_logger.error("Can't read report.json: {}".format(str(err)))
    except json.JSONDecodeError as e:
        core.config.main_logger.error("Broken report: {}".format(str(e)))
    else:
        with open(os.path.join(args.work_dir, core.config.TEST_REPORT_NAME_COMPARED), 'w') as file:
            json.dump(render_json, file, indent=4)

    if not os.path.exists(args.base_dir) or not os.path.exists(baseline_json_path):
        core.config.main_logger.warning("Baseline or manifest not found by path: {}".format(args.base_dir))

    try:
        with open(render_json_path, 'r') as file:
            render_json = json.loads(file.read())

        with open(baseline_json_path, 'r') as file:
            baseline_json = json.loads(file.read())

    except (FileNotFoundError, OSError, json.JSONDecodeError) as err:
        core.config.main_logger.error("Can't get input data: {}".format(str(err)))

    for img in render_json:
        if img['test_status'] != core.config.TEST_IGNORE_STATUS:
            # if tool crash has been occur, we shouldn't change test case status
            test_case_save_crash = None
            if img['test_status'] == core.config.TEST_CRASH_STATUS:
                test_case_save_crash = core.config.TEST_CRASH_STATUS
            img.update(get_pixel_difference(args.work_dir, args.base_dir, img, baseline_json, args.pix_diff_tolerance,
                                        args.pix_diff_max))
            img.update(get_rendertime_difference(args.base_dir, img, args.time_diff_max))

            if test_case_save_crash:
                img.update({'test_status': core.config.TEST_CRASH_STATUS})

    with open(os.path.join(args.work_dir, core.config.TEST_REPORT_NAME_COMPARED), 'w') as file:
        json.dump(render_json, file, indent=4)


if __name__ == '__main__':
    main()
