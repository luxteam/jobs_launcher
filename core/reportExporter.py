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


def make_base64_img(session_dir, report):
    os.mkdir(os.path.join(session_dir, 'tmp'))

    for test in report:
        for item in report[test]:
            for img in ['baseline_color_path', 'baseline_opacity_path', 'render_color_path', 'render_opacity_path']:
                try:
                    if not os.path.exists(os.path.abspath(item[img])):
                        item[img] = os.path.join(session_dir, item[img])

                    cur_img = Image.open(os.path.abspath(item[img]))
                    tmp_img = cur_img.resize((64,64), Image.ANTIALIAS)
                    tmp_img.save(os.path.join(session_dir, 'tmp', 'img.jpg'))

                    with open(os.path.join(session_dir, 'tmp', 'img.jpg'), 'rb') as file:
                        code = base64.b64encode(file.read())

                    src = "data:image/jpeg;base64," + str(code)[2:-1]
                    item.update({img: src})
                except:
                    pass

    return report


def build_session_report(report, session_dir):
    total = {'total': 0, 'passed': 0, 'failed': 0, 'skipped': 0, 'duration': 0}

    current_test_report = {}
    current_test_expected = {}
    all_test_summary = {}

    for result in report['results']:
        for item in report['results'][result]:
            with open(os.path.join(session_dir, report['results'][result][item]['result_path'], 'report_compare.json'), 'r') as file:
                current_test_report.update({' '.join([result, item]): json.loads(file.read())})

            for jtem in current_test_report[' '.join([result, item])]:
                jtem.update({'render_color_path': os.path.relpath(os.path.join(session_dir, report['results'][result][item]['result_path'], jtem['render_color_path']), session_dir)})
                if 'render_opacity_path' in jtem.keys():
                    jtem.update({'render_opacity_path': os.path.relpath(os.path.join(session_dir, report['results'][result][item]['result_path'], jtem['render_opacity_path']), session_dir)})

                if 'baseline_opacity_path' in jtem.keys():
                    jtem.update({'baseline_opacity_path': os.path.relpath(os.path.join(session_dir, report['results'][result][item]['result_path'], jtem['baseline_opacity_path']), session_dir)})
                if 'baseline_color_path' in jtem.keys():
                    jtem.update({'baseline_color_path': os.path.relpath(os.path.join(session_dir, report['results'][result][item]['result_path'], jtem['baseline_color_path']), session_dir)})

            all_test_summary.update(current_test_report)

    for result in report['results']:
        for item in report['results'][result]:
            for key in total:
                total[key] += report['results'][result][item][key]

    report.update({'summary': total})

    env = jinja2.Environment(
        loader=jinja2.PackageLoader('core.reportExporter', 'templates'),
        autoescape=jinja2.select_autoescape(['html'])
    )
    template = env.get_template('session_report.html')

    save_json_report(report, session_dir, 'session_report.json')
    save_json_report(all_test_summary, session_dir, 'all_tests_summary.json')

    html_result = template.render(total={'_cur_': total}, results={'_cur_': report['results']}, detail_report={'_cur_': all_test_summary})
    save_html_report(html_result, session_dir, 'session_report.html')

    current_test_report = make_base64_img(session_dir, current_test_report)
    save_json_report(current_test_report, session_dir, 'all_tests_summary_embed_img.json')

    html_result = template.render(total={'_cur_': total}, results={'_cur_': report['results']}, detail_report={'_cur_': current_test_report})
    save_html_report(html_result, session_dir, 'session_report_embed_img.html')


def build_summary_report(work_dir):

    summary_report = {}
    summary_report_all_tests = {}
    summary_report_all_tests_embed_img = {}
    summary_total = {}
    for path, dirs, files in os.walk(os.path.abspath(work_dir)):
        for file in files:
            if file.endswith('session_report.json'):
                with open(os.path.join(path, file), 'r') as file:
                    text = json.loads(file.read())
                execution_name = os.path.basename(path)
                summary_report[execution_name] = text['results']
                for item in summary_report[execution_name]:
                    for jtem in summary_report[execution_name][item]:
                        summary_report[execution_name][item][jtem].update({'reportlink': os.path.relpath(os.path.join(work_dir, execution_name,summary_report[execution_name][item][jtem]['reportlink']), work_dir)})

                summary_total[os.path.basename(path)] = text['summary']
            elif file.endswith('all_tests_summary.json'):
                with open(os.path.join(path, file), 'r') as file:
                    execution_name = os.path.basename(path)
                    summary_report_all_tests[execution_name] = json.loads(file.read())
                    for test in summary_report_all_tests[execution_name]:
                        for jtem in summary_report_all_tests[execution_name][test]:
                            jtem.update({'render_color_path': os.path.join(execution_name, jtem['render_color_path'])})
                            if 'render_opacity_path' in jtem.keys():
                                jtem.update({'render_opacity_path': os.path.join(execution_name, jtem['render_opacity_path'])})

                            if 'baseline_opacity_path' in jtem.keys():
                                jtem.update({'baseline_opacity_path': os.path.relpath(os.path.join(work_dir, execution_name, jtem['baseline_opacity_path']), work_dir)})
                            if 'baseline_color_path' in jtem.keys():
                                jtem.update({'baseline_color_path': os.path.relpath(os.path.join(work_dir, execution_name, jtem['baseline_color_path']), work_dir)})

            elif file.endswith('all_tests_summary_embed_img.json'):
                with open(os.path.join(path, file), 'r') as file:
                    execution_name = os.path.basename(path)
                    summary_report_all_tests_embed_img[execution_name] = json.loads(file.read())

    save_json_report(summary_report, work_dir, 'summary_report.json')
    save_json_report(summary_report_all_tests, work_dir, 'summary_report_all_tests.json')
    save_json_report(summary_report_all_tests_embed_img, work_dir, 'summary_report_all_tests_embed_img.json')

    env = jinja2.Environment(
        loader=jinja2.PackageLoader('core.reportExporter', 'templates'),
        autoescape=jinja2.select_autoescape(['html'])
    )
    template = env.get_template('session_report.html')

    html_result = template.render(total=summary_total, results=summary_report, detail_report=summary_report_all_tests)
    save_html_report(html_result, work_dir, 'summary_report.html')

    html_result = template.render(total=summary_total, results=summary_report, detail_report=summary_report_all_tests_embed_img)
    save_html_report(html_result, work_dir, 'summary_report_embed_img.html')
