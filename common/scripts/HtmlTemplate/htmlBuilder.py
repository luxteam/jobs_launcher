# -*- coding: utf-8 -*-
from jinja2 import Environment
from jinja2 import PackageLoader
from jinja2 import select_autoescape

import argparse
import os
import json


def main():
    args = argparse.ArgumentParser()
    args.add_argument('--stage_report')
    args.add_argument('--work_dir')
    args.add_argument('--template_name')

    args = args.parse_args()

    stage_report = [{'status': 'INIT'}, {'log': ['htmlBuilder.py started;']}]

    renderedReport = os.path.join(args.work_dir, "report_compare.json")
    notRenderedReport = os.path.join(args.work_dir, "NOT_RENDERED.json")

    with open(os.path.abspath(renderedReport), 'r') as file:
        temp = file.read()
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

    template = env.get_template(args.template_name)
    stage_report[1]['log'].append('Starting html template rendering')
    text = template.render(rendered=renderedJson, notRendered=notRenderedJson, title="Render Results")

    with open(os.path.join(args.work_dir, 'result.html'), 'w') as f:
        f.write(text)

    # try:
    #     template = env.get_template(args.template_name)
    #     text = template.render(rendered=renderedJson, notRendered=notRenderedJson, title="Render Results")
    #     stage_report[1]['log'].append('Html report generated;')
    #     with open(os.path.join(args.work_dir, 'result.html'), 'w') as f:
    #         f.write(text)
    # except:
    #     stage_report[1]['log'].append('Error while html report generating;')
    #     stage_report[0]['status'] = 'FAILED'

    stage_report[0]['status'] = 'OK'
    with open(os.path.join(args.work_dir, args.stage_report), 'w') as file:
        json.dump(stage_report, file, indent=' ')


if __name__ == '__main__':
    main()
