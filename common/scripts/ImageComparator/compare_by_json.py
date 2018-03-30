import os
import argparse
import json
import CompareMetrics
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir, os.path.pardir)))
import core.config


def createArgParser():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--renderer_json_path')
    argparser.add_argument('--baseline_json_path')
    argparser.add_argument('--result_json', require=False)

    return argparser


def main():
    args = createArgParser().parse_args()

    render_json = []
    baseline_json = []

    with open(args.renderer_json_path, 'r') as file:
        render_json = json.loads(file.read())

    with open(args.baseline_json_path, 'r') as file:
        baseline_json = json.loads(file.read())

    for img in render_json:
        for key in core.config.POSSIBLE_JSON_IMG_RENDERED_KEYS:
            if img[key]:
                metrics = CompareMetrics.CompareMetrics(img[key], baseline_json[img['file_name']])

                img.update({'pix_difference': metrics.getDiffPixeles()})
                img.update({'baseline_path': os.path.relpath(baseline_json[img['file_name']])})

    if args.result_json:
        with open(os.path.join(os.path.dirname(args.renderer_json_path), args.result_json), 'w') as file:
            json.dump(render_json, file, indent=" ")
    else:
        with open(args.renderer_json_path, 'w') as file:
            json.dump(render_json, file, indent=" ")
    # try:
    #     jsonReport = json.loads(jsonReport)
    # except json.JSONDecodeError:
    #     stage_report[1]['log'].append('Error in json report; Try to fix it;')
    #     s = list(jsonReport)
    #     if s[-1] == ',':
    #         del s[-1]
    #     s.append(']')
    #     try:
    #         jsonReport = json.loads("".join(s))
    #     except json.JSONDecodeError as err:
    #         print(str(err))


if __name__ == '__main__':
    main()
