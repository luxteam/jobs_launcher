import os
import sys
import json
import argparse


def get_all_json():
    parser = argparse.ArgumentParser()

    parser.add_argument('--work_dir', required=True)
    parser.add_argument('--result_dir', required=True)
    args = parser.parse_args()

    json_files = []
    dirs = []

    work_dir = args.work_dir
    jsonPath = args.result_dir

    files = os.listdir(work_dir)
    print (files)
    for i in range(len(files)):
        dirs.append(work_dir + "\\" + files[i])
    for i in dirs:
        files = os.listdir(i)
        json_files.append(str(i + "\\" + str(([x for x in files if x.endswith('.json')][0]))))
    final_json = ""
    for i in range(len(json_files)):

        if i == 0:
            with open(os.path.join(os.path.dirname(sys.argv[0]), json_files[i])) as f:
                final_json += f.read()
                f.closed
            final_json= final_json[:-1]
            final_json += ","
            # final_json = final_json.replace("}", "},")

        if i == len(json_files)-1:
            with open(os.path.join(os.path.dirname(sys.argv[0]), json_files[i])) as f:
                json1 = f.read()
                f.closed
            json1 =json1.replace("[","")
            final_json+=json1
            # final_json += "\n]"

        if i != 0 and i != len(json_files)-1:
            with open(os.path.join(os.path.dirname(sys.argv[0]), json_files[i])) as f:
                json1 = f.read()
                f.closed
            json1 =json1.replace("[","")
            json1 = json1.replace("]", "")
            # json1 = json1[:-1]
            json1 += ","
            # json1 = json1.replace("}", "},")
            final_json+=json1

    final_json = final_json.replace("\\", "\/")
    print (final_json)
    final_json = json.loads(final_json)

    with open(jsonPath, 'w') as file:
        json.dump(final_json, file, indent=" ")
        file.close()

if __name__ == "__main__":
    get_all_json()
