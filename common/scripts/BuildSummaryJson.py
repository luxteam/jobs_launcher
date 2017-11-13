import os
import argparse
import json


def create_agrparser():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--work_dir', required=True)
    argparser.add_argument('--result_dir', required=True)
    argparser.add_argument('--report_name', required=False, default='.json')

    return argparser


def main():
    args = create_agrparser().parse_args()
    summary_json = []
    temp_json = []

    for path, dirs, files in os.walk(args.work_dir):
        for file in files:
            if file.endswith(args.report_name):
                # print(os.path.join(path, file))

                with open(os.path.join(path,file), 'r') as json_file:
                    temp_json = json_file.read()
                    json_file.close()

                try:
                    temp_json = json.loads(temp_json)
                except json.JSONDecodeError as e:
                    print('JSONDecodeError in report file', e)
                else:
                    summary_json.extend(temp_json)
                    # listmerge5= lambda ll: [el for lst in ll for el in lst]

    with open(os.path.join(args.result_dir, 'summary_json.json'), 'w') as result_file:
        json.dump(summary_json, result_file, indent=' ')
        result_file.close()


if __name__=="__main__":
    main()
