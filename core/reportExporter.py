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

    for test_package in report['results']:
        for test_conf in report['results'][test_package]:
            for test_execution in report['results'][test_package][test_conf]['render_results']:

                for img in ['baseline_color_path', 'baseline_opacity_path', 'render_color_path', 'render_opacity_path']:
                    try:
                        if not os.path.exists(os.path.abspath(test_execution[img])):
                            test_execution[img] = os.path.join(session_dir, test_execution[img])

                        cur_img = Image.open(os.path.abspath(test_execution[img]))
                        tmp_img = cur_img.resize((64,64), Image.ANTIALIAS)
                        tmp_img.save(os.path.join(session_dir, 'tmp', 'img.jpg'))

                        with open(os.path.join(session_dir, 'tmp', 'img.jpg'), 'rb') as file:
                            code = base64.b64encode(file.read())

                        src = "data:image/jpeg;base64," + str(code)[2:-1]
                        test_execution.update({img: src})
                    except:
                        pass

    return report


def build_session_report(report, session_dir):
    total = {'total': 0, 'passed': 0, 'failed': 0, 'skipped': 0, 'duration': 0, 'render_duration': 0}

    current_test_report = {}
    # current_test_expected = {}
    # all_test_summary = {}

    for result in report['results']:
        for item in report['results'][result]:
            try:
                # get report_compare.json by one tests group
                with open(os.path.join(session_dir, report['results'][result][item]['result_path'], 'report_compare.json'), 'r') as file:
                    current_test_report = json.loads(file.read())
                    # all_test_summary.update({' '.join(filter(None, [result, item])): current_test_report})
            except:
                pass
            else:
                render_duration = 0.0
                # for jtem in all_test_summary[' '.join(filter(None, [result, item]))]:
                for jtem in current_test_report:
                    jtem.update({'render_color_path': os.path.relpath(os.path.join(session_dir, report['results'][result][item]['result_path'], jtem['render_color_path']), session_dir)})
                    if 'render_opacity_path' in jtem.keys():
                        jtem.update({'render_opacity_path': os.path.relpath(os.path.join(session_dir, report['results'][result][item]['result_path'], jtem['render_opacity_path']), session_dir)})
                    if 'baseline_opacity_path' in jtem.keys():
                        jtem.update({'baseline_opacity_path': os.path.relpath(os.path.join(session_dir, report['results'][result][item]['result_path'], jtem['baseline_opacity_path']), session_dir)})
                    if 'baseline_color_path' in jtem.keys():
                        jtem.update({'baseline_color_path': os.path.relpath(os.path.join(session_dir, report['results'][result][item]['result_path'], jtem['baseline_color_path']), session_dir)})

                    render_duration += jtem['render_time']
                # unite launcher report and render report
                report['results'][result][item].update({'render_results': current_test_report})
                report['results'][result][item].update({'render_duration': render_duration})

    # get summary results
    # TODO: catch if test failed and render_duration doesn't exist
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
    # save_json_report(all_test_summary, session_dir, 'all_tests_summary.json')

    html_result = template.render(title='Session report', report={'_cur_': report})
    # save_html_report(html_result, session_dir, 'session_report.html')

    # make embed_img reports
    report = make_base64_img(session_dir, report)
    save_json_report(report, session_dir, 'session_report_embed_img.json')

    html_result = template.render(title='Session report', report={'_cur_': report})
    save_html_report(html_result, session_dir, 'session_report_embed_img.html')


def build_summary_report(work_dir):

    summary_report = {}
    summary_report_all_tests = {}
    summary_report_all_tests_embed_img = {}
    summary_total = {}
    # for path, dirs, files in os.walk(os.path.abspath(work_dir)):
    #     for file in files:
    #         # collect all reports with execution info
    #         if file.endswith('session_report.json'):
    #             with open(os.path.join(path, file), 'r') as file:
    #                 text = json.loads(file.read())
    #             execution_name = os.path.basename(path)
    #             # build dict {Folder_name: 'results' }
    #             summary_report[execution_name] = text['results']
    #             for item in summary_report[execution_name]:
    #                 for jtem in summary_report[execution_name][item]:
    #                     # update relative links to local reports
    #                     summary_report[execution_name][item][jtem].update({'reportlink': os.path.relpath(os.path.join(work_dir, execution_name,summary_report[execution_name][item][jtem]['reportlink']), work_dir)})
    #
    #             summary_total[os.path.basename(path)] = text['summary']
    #         # collect all reports with render info
    #         elif file.endswith('all_tests_summary.json'):
    #             with open(os.path.join(path, file), 'r') as file:
    #                 execution_name = os.path.basename(path)
    #                 summary_report_all_tests[execution_name] = json.loads(file.read())
    #                 for test in summary_report_all_tests[execution_name]:
    #                     # update relative links to images
    #                     for jtem in summary_report_all_tests[execution_name][test]:
    #                         jtem.update({'render_color_path': os.path.join(execution_name, jtem['render_color_path'])})
    #                         if 'render_opacity_path' in jtem.keys():
    #                             jtem.update({'render_opacity_path': os.path.join(execution_name, jtem['render_opacity_path'])})
    #
    #                         if 'baseline_opacity_path' in jtem.keys():
    #                             jtem.update({'baseline_opacity_path': os.path.relpath(os.path.join(work_dir, execution_name, jtem['baseline_opacity_path']), work_dir)})
    #                         if 'baseline_color_path' in jtem.keys():
    #                             jtem.update({'baseline_color_path': os.path.relpath(os.path.join(work_dir, execution_name, jtem['baseline_color_path']), work_dir)})
    #
    #         elif file.endswith('all_tests_summary_embed_img.json'):
    #             with open(os.path.join(path, file), 'r') as file:
    #                 execution_name = os.path.basename(path)
    #                 summary_report_all_tests_embed_img[execution_name] = json.loads(file.read())

    summary_report = {}
    summary_report_embed_img = {}
    for path, dirs, files in os.walk(os.path.abspath(work_dir)):
        for file in files:
            if file.endswith('session_report_embed_img.json'):
                with open(os.path.join(path, file), 'r') as report_file:
                    summary_report_embed_img[os.path.basename(path)] = json.loads(report_file.read())
            elif file.endswith('session_report.json'):
                basename = os.path.basename(path)
                with open(os.path.join(path, file), 'r') as report_file:
                    summary_report[basename] = json.loads(report_file.read())

                for test_package in summary_report[basename]['results']:
                    for test_conf in summary_report[basename]['results'][test_package]:
                        for jtem in summary_report[basename]['results'][test_package][test_conf]['render_results']:

                            jtem.update({'render_color_path': os.path.join(basename, jtem['render_color_path'])})
                            if 'render_opacity_path' in jtem.keys():
                                jtem.update({'render_opacity_path': os.path.join(basename, jtem['render_opacity_path'])})

                            if 'baseline_opacity_path' in jtem.keys():
                                jtem.update({'baseline_opacity_path': os.path.relpath(os.path.join(work_dir, basename, jtem['baseline_opacity_path']), work_dir)})
                            if 'baseline_color_path' in jtem.keys():
                                jtem.update({'baseline_color_path': os.path.relpath(os.path.join(work_dir, basename, jtem['baseline_color_path']), work_dir)})



    save_json_report(summary_report, work_dir, 'summary_report.json')
    # save_json_report(summary_report_all_tests, work_dir, 'summary_report_all_tests.json')
    save_json_report(summary_report_embed_img, work_dir, 'summary_report_embed_img.json')

    env = jinja2.Environment(
        loader=jinja2.PackageLoader('core.reportExporter', 'templates'),
        autoescape=jinja2.select_autoescape(['html'])
    )
    template = env.get_template('session_report.html')

    html_result = template.render(title='Summary report', report=summary_report)
    save_html_report(html_result, work_dir, 'summary_report.html')

    html_result = template.render(title='Summary report', report=summary_report_embed_img)
    save_html_report(html_result, work_dir, 'summary_report_embed_img.html')
