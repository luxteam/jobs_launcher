import os
import jinja2
import json
import shutil
import base64
from PIL import Image


def save_json_report(report, session_dir, file_name):
    with open(os.path.join(session_dir, file_name), "w") as file:
        json.dump(report, file, indent=" ", sort_keys=True)


def save_html_report(report, session_dir, file_name):
    with open(os.path.join(session_dir, file_name), "w") as file:
        file.write(report)


def build_session_report(report, session_dir):
    total = {'total': 0, 'passed': 0, 'failed': 0, 'skipped': 0, 'duration': 0}

    current_test_report = {}
    current_test_expected = {}

    for result in report['results']:
        for item in report['results'][result]:
            with open(os.path.join(session_dir, report['results'][result][item]['result_path'], 'report_compare.json'), 'r') as file:
                current_test_report[' '.join([result, item])] = json.loads(file.read())
            #     TODO: fix bug with space "Materials "

            for jtem in current_test_report[' '.join([result, item])]:
                jtem.update({'render_color_path': os.path.relpath(os.path.join(session_dir, report['results'][result][item]['result_path'], jtem['render_color_path']), session_dir)})
                if jtem['render_opacity_path']:
                    jtem.update({'render_opacity_path': os.path.relpath(os.path.join(session_dir, report['results'][result][item]['result_path'], jtem['render_opacity_path']), session_dir)})

    for result in report['results']:
        for item in report['results'][result]:
            for key in total:
                total[key] += report['results'][result][item][key]

    try:
        # report.sort()
        current_test_report = sorted(current_test_report.items())
    except Exception as err:
        print(str(err))

    report.update({'summary': total})
    save_json_report(report, session_dir, 'session_report.json')
    save_json_report(current_test_report, session_dir, 'all_tests_summary.json')

    env = jinja2.Environment(
        loader=jinja2.PackageLoader('core.reportExporter', 'templates'),
        autoescape=jinja2.select_autoescape(['html'])
    )
    template = env.get_template('session_report.html')

    html_result = template.render(results=report['results'], total=total, detail_report=current_test_report)
    save_html_report(html_result, session_dir, 'session_report.html')

    # os.mkdir(os.path.join(session_dir, 'tmp'))
    # for test in current_test_report:
    #     for item in current_test_report[test]:
    #         for img in ['baseline_color_path', 'baseline_opacity_path', 'render_color_path', 'render_opacity_path']:
    #             try:
    #                 if not os.path.exists(os.path.abspath(item[img])):
    #                     item[img] = os.path.join(session_dir, item[img])
    #
    #                 cur_img = Image.open(os.path.abspath(item[img]))
    #                 tmp_img = cur_img.resize((64,64), Image.ANTIALIAS)
    #                 tmp_img.save(os.path.join(session_dir, 'tmp', 'img.jpg'))
    #
    #                 with open(os.path.join(session_dir, 'tmp', 'img.jpg'), 'rb') as file:
    #                     code = base64.b64encode(file.read())
    #
    #                 src = "data:image/jpeg;base64," + str(code)[2:-1]
    #                 item.update({img: src})
    #             except:
    #                 pass
    #
    # html_result = template.render(results=report['results'], total=total, detail_report=current_test_report)
    # save_html_report(html_result, session_dir, 'session_report_embed_img.html')
    # save_json_report(current_test_report, session_dir, 'all_tests_summary_embed_img.json')


def build_summary_report(work_dir):
    # TODO: make simpler
    summary_report = []
    for path, dirs, files in os.walk(os.path.abspath(work_dir)):
        for file in files:
            if file.endswith('session_report.json'):
                with open(os.path.join(path, file), 'r') as file:
                    text = json.loads(file.read())
                    text['execution_info'] = os.path.basename(path)
                    summary_report.append(text)

    details_report = {}
    for execution in summary_report:
        temp_report = []
        for test in execution['results']:
            total = {'total': 0, 'passed': 0, 'failed': 0, 'skipped': 0, 'duration': 0}
            for test_configuration in execution['results'][test]:
                for key in total:
                    total[key] += execution['results'][test][test_configuration][key]
            total.update({'test': test})
            temp_report.append(total)

        details_report[execution['execution_info']] = temp_report

    save_json_report(summary_report, work_dir, 'summary_report.json')

    env = jinja2.Environment(
        loader=jinja2.PackageLoader('core.reportExporter', 'templates'),
        autoescape=jinja2.select_autoescape(['html'])
    )
    template = env.get_template('summary_report.html')

    # print(json.dumps(summary_report, indent=4))
    html_result = template.render(summary_report=summary_report, details_report=details_report)
    save_html_report(html_result, work_dir, 'summary_report.html')


def build_export_reports(server_root, package_name, plugin_version, session_dir):
    # TODO: in future export json and img on different servers
    # TODO: add cheack to unique folder name
    server_path = os.path.abspath(os.path.join(server_root, package_name, plugin_version, os.path.basename(session_dir)))

    shutil.copytree(session_dir, server_path)
