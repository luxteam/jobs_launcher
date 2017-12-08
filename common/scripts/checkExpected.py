import os
import argparse
import json


def createArgParser():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--stage_report')
    argparser.add_argument('--work_dir')
    argparser.add_argument('--report_name')
    argparser.add_argument('--result_name')

    return argparser


def check(args):
    stage_report = [{'status': 'INIT'}, {'log': ['checkExpected.py start']}]

    folder = os.path.abspath(args.work_dir)

    filesColor = set()
    filesOpacity = set()
    expected = set()

    try:
        filesColor = {x for x in os.listdir(os.path.join(folder, "Color")) if
                      os.path.isfile(os.path.join(folder, "Color", x))}
        # filesOpacity = {x for x in os.listdir(os.path.join(folder, "Opacity")) if
        #                 os.path.isfile(os.path.join(folder, "Opacity", x))}
    except:
        stage_report[0]['status'] = 'FAILED'
        stage_report[1]['log'].append('Error while reading rendered images;')
        return stage_report

    try:
        with open(os.path.join(folder, args.report_name)) as file:
            expected = file.read()
        expected = json.loads(expected)
        expected = {x['file_name'] for x in expected}
    except OSError as err:
        stage_report[0]['status'] = 'FAILED'
        stage_report[1]['log'].append(str(err))
        return stage_report
    except json.JSONDecodeError as err:
        stage_report[0]['status'] = 'FAILED'
        stage_report[1]['log'].append(str(err))
        return stage_report
    else:
        stage_report[1]['log'].append('Checking expected files and rendered files')

    # ( (filesColor ^ expected) & (filesOpacity ^ expected) )
    result = filesColor ^ expected

    if result:
        resultJson = []
        for item in result:
            pair = {"not_rendered": item}
            resultJson.append(pair)

        with open(os.path.abspath(os.path.join(folder, args.result_name)), 'w') as file:
            json.dump(resultJson, file, indent=" ")
        stage_report[1]['log'].append('Image count dose not match;')
    else:
        stage_report[1]['log'].append('Image count matches;')

    stage_report[0]['status'] = 'OK'

    return stage_report


def main():
    args = createArgParser().parse_args()

    stage_report = check(args)

    with open(os.path.join(os.path.abspath(args.work_dir), args.stage_report), 'w') as file:
        json.dump(stage_report, file, indent=' ')


if __name__ == '__main__':
    main()
