import os
import argparse
import json
import CompareMetrics
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir, os.path.pardir)))
import core.config
# TODO: refactor it
# TODO: return difference value for better/worst time & vram diff

def createArgParser():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--work_dir')
    argparser.add_argument('--base_dir')
    argparser.add_argument('--pix_diff_tolerance', required=False, default=core.config.PIX_DIFF_TOLERANCE)
    argparser.add_argument('--pix_diff_max', required=False, default=core.config.PIX_DIFF_MAX)
    argparser.add_argument('--time_diff_max', required=False, default=core.config.TIME_DIFF_MAX)
    argparser.add_argument('--vram_diff_max', required=False, default=core.config.VRAM_DIFF_MAX)

    return argparser


def get_diff(current, base):
    if current == base:
        return 0.0
    try:
        return (current - base) / base * 100.0
    except ZeroDivisionError:
        return 0


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


def main():
    args = createArgParser().parse_args()

    render_json_path = os.path.join(args.work_dir, core.config.TEST_REPORT_NAME)
    render_json = []

    if not os.path.exists(render_json_path):
        core.config.main_logger.error("Render report doesn't exists")
        return

    with open(render_json_path, 'r') as file:
        render_json = json.loads(file.read())

    if not os.path.exists(args.base_dir):
        core.config.main_logger.warning("Baseline was not found: {}".format(args.base_dir))

        for img in render_json:
            img.update({'difference_time': -0.0,
                        'baseline_render_time': -0.0,
                        'baseline_gpu_memory_usage': -0.0,
                        'difference_vram': -0.0})
    else:
        for img in render_json:
            # if failed it means tool crash - no sense to compare images
            if img['test_status'] != core.config.TEST_CRASH_STATUS:
                if os.path.exists(os.path.join(args.base_dir, img['test_group'], core.config.BASELINE_REPORT_NAME)):
                    with open(os.path.join(args.base_dir, img['test_group'], core.config.BASELINE_REPORT_NAME), 'r') as file:
                        try:
                            baseline_item = [x for x in json.loads(file.read()) if x['test_case'] == img['test_case']]
                            baseline_vram = baseline_item[0]['gpu_memory_usage']
                            baseline_time = baseline_item[0]['render_time']
                            img.update({'difference_time': get_diff(img['render_time'], baseline_time)})
                            img.update({'difference_vram': get_diff(img['render_time'], baseline_vram)})
                        except IndexError:
                            core.config.main_logger.error("{} wasn't found in baseline".format(img['test_case']))
                        except KeyError:
                            core.config.main_logger.error()
                else:
                    core.config.main_logger.warning("Baseline for: {} wasn't found".format(img['test_group']))
            else:
                pass

    with open(os.path.join(args.work_dir, core.config.TEST_REPORT_NAME_COMPARED), 'w') as file:
        json.dump(render_json, file, indent=4)


if __name__ == '__main__':
    main()
