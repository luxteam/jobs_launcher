import os
import json
import argparse
import time
import random
import shutil

def createArgParser():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--stage_report')
    argparser.add_argument('--terminate_status')
    argparser.add_argument('--output_folder')
    argparser.add_argument('--previous_report')
    argparser.add_argument('--current_report')

    return argparser


def main():

    args = createArgParser().parse_args()
    stage_report = [{'status': 'INIT'}, {'log': ['test_stage.py start; __ ' + args.stage_report]}]
    previous_report = []

    time.sleep(random.randint(1, 3))

    try:
        os.makedirs(os.path.abspath(args.output_folder))
    except:
        pass

    if args.terminate_status == 'OK':
        if args.previous_report:
            try:
                with open(os.path.join(args.output_folder, args.previous_report), 'r') as file:
                    previous_report = json.loads(file.read())
            except OSError as e:
                stage_report[0]['status'] = 'ERROR'
                stage_report[1]['log'].append('Previous stage report not found: ' + str(e))

                with open(os.path.join(args.output_folder, args.stage_report), 'w') as file:
                    json.dump(stage_report, file, indent=' ')
                return

        try:
            chosen_img = random.choice(['u211.jpg', 'u217.jpg'])
            shutil.copy(os.path.join(os.path.split(__file__)[0], chosen_img), os.path.join(args.output_folder, chosen_img))
            with open(os.path.join(args.output_folder, args.current_report), 'w') as file:
                previous_report.append({'stage_name': args.stage_report.replace('.json', ''),
                                        'render_version': '10',
                                        'render_device': random.choice(['smh', 'Nvidia', 'Radeon']),
                                        'render_time': random.choice([2.12903, 4.136912331, 5.62398]),
                                        'difference_color': random.randint(0, 50),
                                        'render_color_path': chosen_img,
                                        'test_case': chosen_img.replace('.jpg', ''),
                                        'file_name': 'file',
                                        'core_version': random.choice(['1.23', '1.24', '1.25']),
                                        'test_status': random.choice(['passed', 'failed', 'skipped']),
                                        'error_title': random.choice(['some error', 'fatal error']),
                                        'tool': random.choice(['Maya', 'Render', 'Ne render', 'Solid works'])
                                        })
                json.dump(previous_report, file, indent=' ')
        except OSError as e:
            stage_report[0]['status'] = 'ERROR'
            stage_report[1]['log'].append('Current report creating error: ' + str(e))

            with open(os.path.join(args.output_folder, args.stage_report), 'w') as file:
                json.dump(stage_report, file, indent=' ')
            return

        stage_report[0]['status'] = 'OK'
        stage_report[1]['log'].append('Finish')

        with open(os.path.join(args.output_folder, 'result.html'), 'w') as file:
            file.write('<html><head><title>Great work</title></head><body><h1>Great work!</h1></body></html>')

        with open(os.path.join(args.output_folder, 'renderTool.log'), 'w') as file:
            file.write('[info] some log')
    else:
        stage_report[0]['status'] = 'FAILED'
        stage_report[1]['log'].append('Some error')

    with open(os.path.join(args.output_folder, args.stage_report), 'w') as file:
        json.dump(stage_report, file, indent=' ')


if __name__ == '__main__':
    main()
