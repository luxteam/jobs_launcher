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


def check(folder, report_name, stage_report):
    filesColor = set()
    filesOpacity = set()

    # TODO: fix try catch
    try:
        filesColor = {x for x in os.listdir(os.path.join(folder, "Color")) if
                  os.path.isfile(os.path.join(folder, "Color", x))}
        filesOpacity = {x for x in os.listdir(os.path.join(folder, "Opacity")) if
                        os.path.isfile(os.path.join(folder, "Opacity", x))}
    except:
        pass

    try:
        filesColor = {x for x in os.listdir(os.path.join(folder, "images")) if
                  os.path.isfile(os.path.join(folder, "images", x))}
    except:
        pass

    with open(os.path.join(folder, report_name)) as file:
        expected = file.read()
        expected = json.loads(expected)

    expected = {x['file_name'] for x in expected}

    stage_report[1]['log'].append('Checking expected files and rendered files')
    # return ( (filesColor ^ expected) & (filesOpacity ^ expected) )
    return filesColor ^ expected


def main():
    args = createArgParser().parse_args()
    stage_report = [{'status': 'INIT'}, {'log': ['checkExpected.py start']}]

    print(args)
    folder = os.path.abspath(args.work_dir)

    result = check(folder, args.report_name, stage_report)

    if (result):
        resultJson = []
        for item in result:
            pair = {"not_rendered": item}
            resultJson.append(pair)

        with open(os.path.abspath(os.path.join(folder, args.result_name)), 'w') as file:
            json.dump(resultJson, file, indent=" ")

    stage_report[0]['status'] = 'OK'
    with open(os.path.join(folder, args.stage_report), 'w') as file:
        json.dump(stage_report, file, indent=' ')


if __name__ == '__main__':
    main()
