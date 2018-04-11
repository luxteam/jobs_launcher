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

    expected = set()
    rendered = set()

    try:
        with open(os.path.join(args.work_dir, core.config.TEST_REPORT_EXPECTED_NAME), 'r') as file:
            expected = json.loads(file.read())

        with open(os.path.join(args.work_dir, core.config.TEST_REPORT_NAME), 'r') as file:
            rendered = json.loads(file.read())
    except Exception as err:
        core.config.main_logger.error("Not found reports: {}".format(str(err)))

    rendered = {x[img] for x in rendered for img in core.config.POSSIBLE_JSON_IMG_RENDERED_KEYS}
    expected = {x['file_path'] for x in expected}

    # TODO: check symmetry?
    result = expected - rendered

    if result:
        result_json = [{"file_path": x} for x in result]

        with open(os.path.join(args.work_dir, args.result_report), 'w') as file:
            json.dump(result_json, file, indent=" ")
    else:
        pass


if __name__ == '__main__':
    main()
