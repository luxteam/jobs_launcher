import argparse
import shutil
import os


def create_args_parser():
    args = argparse.ArgumentParser()
    args.add_argument('--results_path')
    args.add_argument('--baseline_path')
    args.add_argument('--tool_name')
    args.add_argument('--device_name')

    return args


def main():
    args = create_args_parser()
    args = args.parse_args()

    args.results_path = os.path.abspath(args.results_path)
    baseline_path = os.path.join(args.baseline_path, args.tool_name + 'Baseline.' + args.device_name)

    for path, dirs, files in os.walk(args.results_path):
        for dir in dirs:
            if dir == 'Tests':
                for test in os.listdir(os.path.join(path, dir)):

                    try:
                        shutil.copytree(os.path.join(path, dir, test), os.path.join(baseline_path, test),
                                        ignore=shutil.ignore_patterns('*.json', '*.html', '*.txt', '*.bat', '*.mel', '*.ms', '*.log', '*.py', '*.pyc', 'error_screenshot.jpg'))
                    except Exception as err:
                        print("Copy error", str(err))

                return


if __name__ == '__main__':
    main()