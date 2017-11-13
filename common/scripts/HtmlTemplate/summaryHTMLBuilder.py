# -*- coding: utf-8 -*-

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
    args.add_argument('report')
    args.add_argument('outfolder')

    renderedReport = os.path.abspath(args.parse_args().report)

    with open(renderedReport, 'r') as file:
        temp = file.read()
        file.close()
    renderedJson = json.loads(temp)

    env = Environment(
        loader=PackageLoader('htmlBuilder', 'templates'),
        autoescape=select_autoescape(['html'])
    )

    template = env.get_template('summary_template.html')

    text = template.render(results=renderedJson)

    with open(os.path.join(args.parse_args().outfolder, 'summary_results.html'), 'w') as f:
        f.write(text)
        f.close()


if __name__ == '__main__':
    main()
