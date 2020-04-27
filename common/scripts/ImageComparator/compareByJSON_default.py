import os
import json
from CompareMetrics_default import CompareMetrics
import sys
from shutil import copyfile

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir, os.path.pardir)))
import core.config


def get_pixel_difference(work_dir, base_dir, img, baseline_json, tolerance, pix_diff_max):
    if 'render_color_path' in img.keys():
        baseline_img_path = os.path.join(base_dir, baseline_json.get(img.get('file_name', ''), 'not.exist'))
        # if baseline image not found - return
        if not os.path.exists(baseline_img_path):
            core.config.main_logger.warning("Baseline image not found by path: {}".format(baseline_img_path))
            img.update({'baseline_color_path': os.path.relpath(os.path.join(base_dir, 'baseline.png'), work_dir)})
            if img['test_status'] != core.config.TEST_CRASH_STATUS:
                img.update({'test_status': core.config.TEST_DIFF_STATUS})
            return img

        # else add baseline images paths to json
        img.update({'baseline_color_path': os.path.relpath(os.path.join(base_dir, baseline_json[img['file_name']]), work_dir)})
        for thumb in core.config.THUMBNAIL_PREFIXES:
            if thumb + img['file_name'] in baseline_json.keys() and os.path.exists(os.path.join(base_dir, baseline_json[thumb + img['file_name']])):
                img.update({thumb + 'baseline_color_path': os.path.relpath(os.path.join(base_dir, baseline_json[thumb + img['file_name']]), work_dir)})

        # for crushed and non-executed cases only set baseline img src
        if img['test_status'] != core.config.TEST_SUCCESS_STATUS:
            return img

        render_img_path = os.path.join(work_dir, img['render_color_path'])
        if not os.path.exists(render_img_path):
            core.config.main_logger.error("Rendered image not found by path: {}".format(render_img_path))
            return img

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
    if os.path.exists(os.path.join(base_dir, img['test_group'], core.config.BASELINE_REPORT_NAME)):
        render_time = img['render_time']
        with open(os.path.join(base_dir, img['test_group'], core.config.BASELINE_REPORT_NAME), 'r') as file:
            baseline_report_json = json.loads(file.read())
            try:
                baseline_time = [x for x in baseline_report_json if x['test_case'] == img['test_case']][0]['render_time']
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


def main(args):
    render_json_path = os.path.join(args.work_dir, core.config.TEST_REPORT_NAME)
    baseline_json_manifest_path = os.path.join(args.base_dir, core.config.BASELINE_MANIFEST)

    if not os.path.exists(render_json_path):
        core.config.main_logger.error("Render report doesn't exists")
        return 1

    try:
        if not os.path.exists(os.path.join(args.work_dir, 'baseline.png')):
            copyfile(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir, 'img', 'baseline.png'),
                     os.path.join(args.work_dir, 'baseline.png'))
    except (OSError, FileNotFoundError) as err:
        core.config.main_logger.error("Couldn't copy baseline stub: {}".format(str(err)))

    # create report_compared.json before calculation to provide stability
    try:
        with open(render_json_path, 'r') as file:
            render_json = json.loads(file.read())
            for img in render_json:
                img.update({'baseline_render_time': -0.0,
                            'difference_time': -0.0,
                            'baseline_color_path': 'baseline.png'})
    except (FileNotFoundError, OSError) as err:
        core.config.main_logger.error("Can't read report.json: {}".format(str(err)))
    except json.JSONDecodeError as e:
        core.config.main_logger.error("Broken report: {}".format(str(e)))
    else:
        with open(os.path.join(args.work_dir, core.config.TEST_REPORT_NAME_COMPARED), 'w') as file:
            json.dump(render_json, file, indent=4)

    if not os.path.exists(baseline_json_manifest_path):
        core.config.main_logger.warning("Baseline manifest not found by path: {}".format(args.base_dir))
        # "true" is define by Jenkins manual job. if updaterefs - not fail cases without baseline
        if "true" not in os.getenv("UpdateRefs", "false"):
            for img in render_json:
                img.update({'test_status': core.config.TEST_DIFF_STATUS})
        with open(os.path.join(args.work_dir, core.config.TEST_REPORT_NAME_COMPARED), 'w') as file:
            json.dump(render_json, file, indent=4)
        exit(1)

    try:
        with open(render_json_path, 'r') as file:
            render_json = json.loads(file.read())

        with open(baseline_json_manifest_path, 'r') as file:
            baseline_json = json.loads(file.read())

    except (FileNotFoundError, OSError, json.JSONDecodeError) as err:
        core.config.main_logger.error("Can't get input data: {}".format(str(err)))

    core.config.main_logger.info("Began metrics calculation")
    for img in render_json:
        img.update(get_pixel_difference(args.work_dir, args.base_dir, img, baseline_json, args.pix_diff_tolerance,
                                        args.pix_diff_max))
        img.update(get_rendertime_difference(args.base_dir, img, args.time_diff_max))

    with open(os.path.join(args.work_dir, core.config.TEST_REPORT_NAME_COMPARED), 'w') as file:
        json.dump(render_json, file, indent=4)
