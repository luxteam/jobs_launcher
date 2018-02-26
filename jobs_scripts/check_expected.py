import os
import argparse
import json
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

import core.config


def createArgParser():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--work_dir')
    argparser.add_argument('--expected_report')
    argparser.add_argument('--render_report')
    argparser.add_argument('--result_report')

    return argparser


def main():
    args = createArgParser().parse_args()
    args.work_dir = os.path.abspath(args.work_dir)

    expected = set()
    rendered = set()

    # try:
    with open(os.path.join(args.work_dir, args.expected_report), 'r') as file:
        expected = json.loads(file.read())

    with open(os.path.join(args.work_dir, args.render_report), 'r') as file:
        rendered = json.loads(file.read())
    # except Exception as err:
    #     pass

    # TODO: check if img exist?
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
