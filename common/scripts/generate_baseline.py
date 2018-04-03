import argparse
import shutil
import os
import json
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir)))
import core.config


def create_args_parser():
    args = argparse.ArgumentParser()
    args.add_argument('--results_root')
    args.add_argument('--baseline_root')
    return args


def main():
    args = create_args_parser()
    args = args.parse_args()

    args.results_root = os.path.abspath(args.results_root)
    args.baseline_root = os.path.abspath(args.baseline_root)

    if os.path.exists(args.baseline_root):
        shutil.rmtree(args.baseline_root)

    report = []
    baseline_manifest = {}
    for path, dirs, files in os.walk(args.results_root):
        for file in files:
            # find report_compare.json
            if file == core.config.TEST_REPORT_NAME_COMPARED:
                with open(os.path.join(path, file), 'r') as json_report:
                    report = json.loads(json_report.read())

                for test in report:
                    for img in core.config.POSSIBLE_JSON_IMG_RENDERED_KEYS:
                        # copy files which described in json
                        if img in test.keys():
                            rendered_img_path = os.path.join(path, test[img])
                            baseline_img_path = os.path.relpath(rendered_img_path, args.results_root)

                            # add img to baseline manifest
                            baseline_manifest.update({test['file_name']: baseline_img_path})
                            # create folder in first step for current folder
                            if not os.path.exists(os.path.join(args.baseline_root, os.path.split(baseline_img_path)[0])):
                                os.makedirs(os.path.join(args.baseline_root, os.path.split(baseline_img_path)[0]))

                            try:
                                shutil.copyfile(rendered_img_path, os.path.join(args.baseline_root, baseline_img_path))
                            except Exception as err:
                                core.config.main_logger.warning("Error baseline copy file: {}".format(str(err)))

                # shutil.copyfile(os.path.join(path, file), os.path.join(args.baseline_root, baseline_name,
                shutil.copyfile(os.path.join(path, file),
                                os.path.join(args.baseline_root, os.path.relpath(os.path.join(path, file),args.results_root))
                                )
            elif file == 'result.html':
                # duplicate folder creation because of results.html can be first file
                if not os.path.exists(os.path.join(args.baseline_root, os.path.relpath(path, args.results_root))):
                    os.makedirs(os.path.join(args.baseline_root, os.path.relpath(path, args.results_root)))
                shutil.copyfile(os.path.join(path,file),
                                os.path.join(args.baseline_root, os.path.relpath(path, args.results_root), file)
                                )

    try:
        with open(os.path.join(args.baseline_root, core.config.BASELINE_MANIFEST), 'w') as file:
            json.dump(baseline_manifest, file, indent=" ")

        report = core.config.SESSION_REPORT
        # copy report to
        shutil.copyfile(os.path.join(args.results_root, report),
            os.path.join(os.path.abspath(args.baseline_root), core.config.BASELINE_SESSION_REPORT)
                        )
    except Exception as err:
        core.config.main_logger.warning("Error copy session report to baseline: {}".format(str(err)))


if __name__ == '__main__':
    main()
