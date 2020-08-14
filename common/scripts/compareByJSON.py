import sys
import argparse
import os
import json
from shutil import copyfile
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir)))
import core.config
import core.performance_counter as perf_count
import common.scripts.compareByJSON

try:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir, os.path.pardir)))
    from local_config import *
except ImportError:
    core.config.main_logger.critical("local config file not found. Default values will be used.")
    core.config.main_logger.critical("Correct report building isn't guaranteed")
    from core.defaults_local_config import *


def get_pixel_difference(work_dir, base_dir, img, tolerance, pix_diff_max):
    if 'render_color_path' in img.keys():
        if os.path.exists(os.path.join(base_dir, img['test_group'], img['test_case'] + '.json')):
            with open(os.path.join(base_dir, img['test_group'], img['test_case'] + '.json')) as f:
                baseline_json = json.load(f)
        else:
            core.config.main_logger.error('Error while read {}.json'.format(img['test_case']))
            return img
        baseline_img_path = baseline_json['render_color_path']
        # if baseline image not found - return
        if not os.path.exists(baseline_img_path):
            core.config.main_logger.warning("Baseline image not found by path: {}".format(baseline_img_path))
            img.update({'baseline_color_path': os.path.relpath(os.path.join(base_dir, 'baseline.png'), work_dir)})
            if img['test_status'] != core.config.TEST_CRASH_STATUS:
                img.update({'test_status': core.config.TEST_DIFF_STATUS})
            return img

        # else add baseline images paths to json
        img.update({'baseline_color_path': os.path.relpath(baseline_img_path, work_dir)})
        for thumb in core.config.THUMBNAIL_PREFIXES:
            if thumb + baseline_name in baseline_json.keys() and os.path.exists(os.path.join(base_dir, img[thumb + baseline_name])):
                img.update({thumb + 'baseline_color_path': os.path.relpath(os.path.join(base_dir, baseline_json[thumb + baseline_name]), work_dir)})

        # for crushed and non-executed cases only set baseline img src
        if img['test_status'] != core.config.TEST_SUCCESS_STATUS:
            return img

        render_img_path = os.path.join(work_dir, img['render_color_path'])
        if not os.path.exists(render_img_path):
            core.config.main_logger.error("Rendered image not found by path: {}".format(render_img_path))
            for possible_extension in core.config.POSSIBLE_BASELINE_EXTENSIONS:
                if os.path.exists(os.path.join(work_dir, "Color", core.config.TEST_CRASH_STATUS + "." + possible_extension)):
                    img['render_color_path'] = os.path.join("Color", core.config.TEST_CRASH_STATUS + "." + possible_extension)
                    break
            img['test_status'] = core.config.TEST_CRASH_STATUS
            return img

        if core.config.DONT_COMPARE not in img.get('script_info', ''):
            metrics = None
            try:
                metrics = CompareMetrics(render_img_path, baseline_img_path)
            except (FileNotFoundError, OSError) as err:
                core.config.main_logger.error("Error during metrics calculation: {}".format(str(err)))
                return img

            # pix_difference = metrics.getDiffPixeles(tolerance=tolerance)
            # img.update({'difference_color': pix_difference})
            pix_difference_2 = metrics.getPrediction()
            img.update({'difference_color_2': pix_difference_2})
            # if type(pix_difference) is str or pix_difference > float(pix_diff_max):
            if pix_difference_2 != 0:
                img['test_status'] = core.config.TEST_DIFF_STATUS

    return img


def get_rendertime_difference(base_dir, img, time_diff_max):
    if os.path.exists(os.path.join(base_dir, img['test_group'], img['test_case'] + '.json')):
        with open(os.path.join(base_dir, img['test_group'], img['test_case'] + '.json')) as f:
            baseline_json = json.load(f)
        try:
            baseline_time = baseline_json['render_time']
        except IndexError:
            baseline_time = -0.0

            time_diff = render_time - baseline_time

            for threshold in time_diff_max:
                if baseline_time < float(threshold) and time_diff > time_diff_max[threshold]:
                    img.update({'time_diff_status': core.config.TEST_DIFF_STATUS})
                    if img.get('test_status') == core.config.TEST_SUCCESS_STATUS:
                        img.update({'test_status': core.config.TEST_DIFF_STATUS})

            img.update({'difference_time': time_diff})
            img.update({'baseline_render_time': baseline_time})
    else:
        core.config.main_logger.error('Error while read {}.json'.format(img['test_case']))
        img.update({'difference_time': -0.0})
        img.update({'baseline_render_time': -0.0})

    return img


def createArgParser():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--work_dir')
    argparser.add_argument('--base_dir')
    if report_type == 'ct':
        argparser.add_argument('--case_suffix')
    argparser.add_argument('--pix_diff_tolerance', required=False, default=core.config.PIX_DIFF_TOLERANCE)
    if report_type == 'ec':
        argparser.add_argument('--pix_diff_max', required=False, default=core.config.PIX_DIFF_MAX_EC)
    else:
        argparser.add_argument('--pix_diff_max', required=False, default=core.config.PIX_DIFF_MAX)
    argparser.add_argument('--time_diff_max', required=False, default=core.config.TIME_DIFF_TOLERANCE)
    if report_type == 'ec':
        argparser.add_argument('--vram_diff_max', required=False, default=core.config.VRAM_DIFF_MAX)
    return argparser

def main(args):
    perf_count.event_record(args.work_dir, 'Compare', True)
    render_json_path = os.path.join(args.work_dir, core.config.TEST_REPORT_NAME)

    if not os.path.exists(render_json_path):
        core.config.main_logger.error("Render report doesn't exists")
        perf_count.event_record(args.work_dir, 'Compare', False)
        return

    if not os.path.exists(args.base_dir):
        core.config.main_logger.error("Baseline folder doesn't exist. It will be created with baseline stub img.")
        os.makedirs(args.base_dir)

    try:
        if not os.path.exists(os.path.join(args.base_dir, 'baseline.png')):
            copyfile(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir, 'img', 'baseline.png'),
                     os.path.join(args.base_dir, 'baseline.png'))
    except (OSError, FileNotFoundError) as err:
        core.config.main_logger.error("Couldn't copy baseline stub: {}".format(str(err)))

    # create report_compared.json before calculation to provide stability
    try:
        with open(render_json_path, 'r') as file:
            render_json = json.loads(file.read())
            for img in render_json:
                img.update({'baseline_render_time': -0.0,
                            'difference_time': -0.0,
                            'baseline_color_path': os.path.relpath(os.path.join(args.base_dir, 'baseline.png'), args.work_dir)})
    except (FileNotFoundError, OSError) as err:
        core.config.main_logger.error("Can't read report.json: {}".format(str(err)))
    except json.JSONDecodeError as e:
        core.config.main_logger.error("Broken report: {}".format(str(e)))
    else:
        with open(os.path.join(args.work_dir, core.config.TEST_REPORT_NAME_COMPARED), 'w') as file:
            json.dump(render_json, file, indent=4)

    try:
        with open(render_json_path, 'r') as file:
            render_json = json.loads(file.read())

    except (FileNotFoundError, OSError, json.JSONDecodeError) as err:
        core.config.main_logger.error("Can't get input data: {}".format(str(err)))

    core.config.main_logger.info("Began metrics calculation")
    for img in render_json:
        img.update(get_pixel_difference(args.work_dir, args.base_dir, img, args.pix_diff_tolerance,
                                        args.pix_diff_max))
        img.update(get_rendertime_difference(args.base_dir, img, args.time_diff_max))

    with open(os.path.join(args.work_dir, core.config.TEST_REPORT_NAME_COMPARED), 'w') as file:
        json.dump(render_json, file, indent=4)

    perf_count.event_record(args.work_dir, 'Compare', False)


if __name__ == '__main__':
    args = createArgParser().parse_args()
    main(args)
