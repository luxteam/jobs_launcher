import os
import argparse
import json
import CompareMetrics


def createArgParser():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--stage_report')
    argparser.add_argument('--work_dir')
    argparser.add_argument('--base_dir')
    argparser.add_argument('--report_name')
    argparser.add_argument('--result_name')

    return argparser


def repairJson(jsonReport):
    try:
        jsonReport = json.loads(jsonReport)
    except:
        s = list(jsonReport)
        if s[-1] == ',':
            del s[-1]
        s.append(']')
        try:
            jsonReport = json.loads("".join(s))
        except:
            print("ERROR: can't fix json report")
            return
        else:
            return jsonReport
    else:
        return jsonReport


def compareFoldersWalk(jsonReport, workFolder, baseFolder, suffix, result_report):
    for img in jsonReport:
        file1 = os.path.abspath(os.path.join(workFolder, img['file_name']))
        file2 = os.path.abspath(os.path.join(baseFolder, img['file_name']))

        try:
            metrics = CompareMetrics.CompareMetrics(file1, file2)
            key_diff = ('difference_' + os.path.basename(workFolder)).lower()
            key_src = ('path_' + os.path.basename(workFolder)).lower()
            # key_diff = ('difference_' + suffix + '_' + os.path.basename(workFolder)).lower()
            # key_src = ('path_' + suffix + '_' + os.path.basename(workFolder)).lower()

            diff = {key_diff: metrics.getDiffPixeles()}
            src = {key_src: file2}
        except:
            # print("Diff tool can't find path")
            pass
        else:
            img.update(diff)
            img.update(src)

    with open(result_report, 'w') as file:
        json.dump(jsonReport, file, indent=" ", sort_keys=True)

    return


def main():
    stage_report = [{'status': 'INIT'}, {'log': []}]
    args = createArgParser().parse_args()
    workFolder = args.work_dir
    report = os.path.join(workFolder, args.report_name)

    jsonReport = ""
    try:
        with open(os.path.abspath(report), 'r') as file:
            jsonReport = file.read()
            file.close()
    except OSError:
        print("Not found", os.path.abspath(report))

    jsonReport = repairJson(jsonReport)

    if os.path.exists(os.path.abspath(args.base_dir)):
        for path, dirs, files in os.walk(args.base_dir):
            for dir in dirs:
                # TODO: change key
                s = os.path.split(path)
                key = (os.path.split(s[0])[1])
                if dir == 'Opacity' or dir == 'Color' or dir == 'images':
                    stage_report[1]['log'].append('Comparison: ' + os.path.join(path, dir))
                    compareFoldersWalk(jsonReport, os.path.join(args.work_dir, dir), os.path.join(path, dir), key,
                                       os.path.join(args.work_dir, args.result_name))
    else:
        stage_report[1]['log'].append('Baseline dose not exist')

    stage_report[0]['status'] = 'OK'

    with open(os.path.join(args.work_dir, args.result_name), 'w') as file:
        json.dump(jsonReport, file, indent=" ", sort_keys=True)

    with open(os.path.join(workFolder, args.stage_report), 'w') as file:
        json.dump(stage_report, file, indent=' ')

if __name__ == '__main__':
    main()
