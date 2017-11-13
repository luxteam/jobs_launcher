# -*- coding: utf-8 -*-
# TODO: fix count of diff results in report
from jinja2 import Environment
from jinja2 import Template
from jinja2 import PackageLoader
from jinja2 import select_autoescape

import argparse
import os
import sys
import json


def main():
    args = argparse.ArgumentParser()
    args.add_argument('--stage_report')
    args.add_argument('--work_dir')

    stage_report = [{'status': 'INIT'}, {'log': []}]

    renderedReport = os.path.join(args.parse_args().work_dir, "report_compare.json")
    notRenderedReport = os.path.join(args.parse_args().work_dir, "NOT_RENDERED.json")

    with open(os.path.abspath(renderedReport), 'r') as file:
        temp = file.read()
        file.close()
    renderedJson = json.loads(temp)

    try:
        with open(os.path.abspath(notRenderedReport), 'r') as file:
            temp = file.read()
            file.close()
        notRenderedJson = json.loads(temp)
    except Exception as e:
        notRenderedJson = {}

    env = Environment(
        loader=PackageLoader('htmlBuilder', 'templates'),
        autoescape=select_autoescape(['html'])
    )

    template = env.get_template('template.html')

    stage_report[1]['log'].append('Starting html template rendering')
    text = template.render(rendered=renderedJson, notRendered=notRenderedJson)

    with open(os.path.join(args.parse_args().work_dir, 'result.html'), 'w') as f:
        f.write(text)
        f.close()

    stage_report[0]['status'] = 'OK'
    with open(os.path.join(args.parse_args().work_dir, args.parse_args().stage_report), 'w') as file:
        json.dump(stage_report, file, indent=' ')


if __name__ == '__main__':
    main()
