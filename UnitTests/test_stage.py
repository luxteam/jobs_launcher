import os
import json
import argparse
import time
import random

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
            with open(os.path.join(args.output_folder, args.current_report), 'w') as file:
                previous_report.append({'stage_name': args.stage_report.replace('.json', ''),
                                        'render_version': 10,
                                        'render_device': 'smh',
                                        'render_time': 10,
                                        'difference_color': 10,
                                        'render_color_path': 'img.jpg',
                                        'file_name': 'file'
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
    else:
        stage_report[0]['status'] = 'FAILED'
        stage_report[1]['log'].append('Some error')

    with open(os.path.join(args.output_folder, args.stage_report), 'w') as file:
        json.dump(stage_report, file, indent=' ')


if __name__ == '__main__':
    main()
