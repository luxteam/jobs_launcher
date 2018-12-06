import os
import argparse
import json
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir)))
import core.config


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--work_dir')
    args = argparser.parse_args()

    try:
        with open(os.path.join(args.work_dir, core.config.TEST_REPORT_EXPECTED_NAME), 'r') as file:
            expected = json.loads(file.read())

        with open(os.path.join(args.work_dir, core.config.TEST_REPORT_NAME), 'r') as file:
            rendered = json.loads(file.read())
    except Exception as err:
        core.config.main_logger.error("Not found reports: {}".format(str(err)))

    rendered_cases = {x['test_case'] for x in rendered}
    expected_cases = {x for x in expected}

    skipped_cases = expected_cases - rendered_cases

    if skipped_cases:
        core.config.main_logger.error("Some tests were not launched")
        common_info = rendered[0].copy()

        for key in common_info:
            if key not in ['tool', 'render_version', 'test_group', 'core_version', 'render_device']:
                del common_info[key]

        with open(os.path.join(args.work_dir, core.config.NOT_RENDERED_REPORT), 'w') as file:
            json.dump([x for x in skipped_cases], file, indent=4)

        for scase in skipped_cases:
            report_base = core.config.RENDER_REPORT_BASE.copy()
            report_base.update(
                {"test_case": scase,
                 "test_status": "error"}
            )
            report_base.update(common_info)
            rendered.append(report_base)

        with open(os.path.join(args.work_dir, core.config.TEST_REPORT_NAME), 'w') as file:
            json.dump(rendered, file, indent=4)
    else:
        core.config.main_logger.info("No missed tests detected")


if __name__ == '__main__':
    if not main():
        exit(0)
