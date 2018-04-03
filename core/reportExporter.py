import os
import jinja2
import json
import base64
from PIL import Image

from core.config import *
from core.auto_dict import AutoDict


def save_json_report(report, session_dir, file_name, replace_pathsep=False):
    with open(os.path.abspath(os.path.join(session_dir, file_name)), "w") as file:
        if replace_pathsep:
            s = json.dumps(report, indent=" ", sort_keys=True)
            file.write(s.replace(os.path.sep, '/'))
        else:
            json.dump(report, file, indent=" ", sort_keys=True)


def save_html_report(report, session_dir, file_name, replace_pathsep=False):
    with open(os.path.abspath(os.path.join(session_dir, file_name)), "w") as file:
        if replace_pathsep:
            file.write(report.replace(os.path.sep, '/'))
        else:
            file.write(report)


def make_base64_img(session_dir, report):
    os.mkdir(os.path.join(session_dir, 'tmp'))

    for test_package in report['results']:
        for test_conf in report['results'][test_package]:
            for test_execution in report['results'][test_package][test_conf]['render_results']:

                for img in POSSIBLE_JSON_IMG_KEYS:
                    if img in test_execution:
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
                        except Exception as err:
                            main_logger.error('Error in base64 encoding: {}'.format(str(err)))

    return report


def build_session_report(report, session_dir):
    total = {'total': 0, 'passed': 0, 'failed': 0, 'skipped': 0, 'duration': 0, 'render_duration': 0}

    current_test_report = {}
    for result in report['results']:
        for item in report['results'][result]:
            try:
                # get report_compare.json by one tests group
                with open(os.path.join(session_dir, report['results'][result][item]['result_path'], TEST_REPORT_NAME_COMPARED), 'r') as file:
                    current_test_report = json.loads(file.read())
                    # all_test_summary.update({' '.join(filter(None, [result, item])): current_test_report})
            except Exception as err:
                main_logger.error("Expected 'report_compare.json' not found: {}".format(str(err)))
                report['results'][result][item].update({'render_results': {}})
                report['results'][result][item].update({'render_duration': -0.0})
            else:
                render_duration = 0.0
                try:
                    for jtem in current_test_report:
                        for img in POSSIBLE_JSON_IMG_KEYS:
                            if img in jtem.keys():
                                jtem.update({img: os.path.relpath(os.path.join(session_dir, report['results'][result][item]['result_path'], jtem[img]), session_dir)})

                        render_duration += jtem['render_time']

                        try:
                            report['machine_info'].update({'render_device': jtem['render_device']})
                            report['machine_info'].update({'tool': jtem['tool']})
                            report['machine_info'].update({'render_version': jtem['render_version']})
                        except:
                            pass

                    # report['results'][result][item].update({'result_path': os.path.relpath(os.path.join(session_dir, report['results'][result][item]['result_path']), session_dir)})
                    # unite launcher report and render report
                except Exception as err:
                    print("Exception while update render report: " + str(err))
                    main_logger.error('Exception while update render report {}'.format(str(err)))
                    render_duration = -0.0

                if current_test_report:
                    report['results'][result][item].update({'render_results': current_test_report})

                report['results'][result][item].update({'render_duration': render_duration})

    # get summary results
    for result in report['results']:
        for item in report['results'][result]:
            for key in total:
                total[key] += report['results'][result][item][key]
    report.update({'summary': total})

    env = jinja2.Environment(
        loader=jinja2.PackageLoader('core.reportExporter', 'templates'),
        autoescape=True
    )
    template = env.get_template('session_report.html')

    save_json_report(report, session_dir, SESSION_REPORT, replace_pathsep=True)

    try:
        html_result = template.render(title='Session report', report={'_cur_': report})
        save_html_report(html_result, session_dir, SESSION_REPORT_HTML, replace_pathsep=True)
    except Exception as e:
        main_logger.error("Error while render html report {}".format(str(e)))
        save_html_report('error', session_dir, SESSION_REPORT_HTML)

    # make embed_img reports
    report = make_base64_img(session_dir, report)
    save_json_report(report, session_dir, SESSION_REPORT_EMBED_IMG, replace_pathsep=True)

    try:
        html_result = template.render(title='Session report', report={'_cur_': report})
        save_html_report(html_result, session_dir, SESSION_REPORT_HTML_EMBED_IMG, replace_pathsep=True)
    except Exception as e:
        main_logger.error("Error while render html report {}".format(str(e)))
        save_html_report('error', session_dir, SESSION_REPORT_HTML_EMBED_IMG)


def build_summary_report(work_dir):

    summary_report = {}
    summary_report_embed_img = {}
    for path, dirs, files in os.walk(os.path.abspath(work_dir)):
        for file in files:
            if file.endswith(SESSION_REPORT_EMBED_IMG):
                with open(os.path.join(path, file), 'r') as report_file:
                    # TODO: basename like session_report
                    summary_report_embed_img[os.path.basename(path)] = json.loads(report_file.read())
            elif file.endswith(SESSION_REPORT):
                basename = os.path.basename(path)
                basename = os.path.relpath(path, work_dir)
                with open(os.path.join(path, file), 'r') as report_file:
                    summary_report[basename] = json.loads(report_file.read())

                try:
                    for test_package in summary_report[basename]['results']:
                        for test_conf in summary_report[basename]['results'][test_package]:
                            for jtem in summary_report[basename]['results'][test_package][test_conf]['render_results']:

                                for img in POSSIBLE_JSON_IMG_KEYS:
                                    if img in jtem.keys():
                                        jtem.update({img: os.path.relpath(os.path.join(work_dir, basename, jtem[img]), work_dir)})

                            summary_report[basename]['results'][test_package][test_conf].update({'result_path': os.path.relpath(os.path.join(work_dir, basename, summary_report[basename]['results'][test_package][test_conf]['result_path']), work_dir)})
                except Exception as e:
                    main_logger.error(str(e))

    save_json_report(summary_report, work_dir, SUMMARY_REPORT, replace_pathsep=True)
    save_json_report(summary_report_embed_img, work_dir, SUMMARY_REPORT_EMBED_IMG, replace_pathsep=True)

    env = jinja2.Environment(
        loader=jinja2.PackageLoader('core.reportExporter', 'templates'),
        autoescape=True
    )
    template = env.get_template('session_report.html')

    try:
        html_result = template.render(title='Summary report', report=summary_report)
        save_html_report(html_result, work_dir, SUMMARY_REPORT_HTML, replace_pathsep=True)

        html_result = template.render(title='Summary report', report=summary_report_embed_img)
        save_html_report(html_result, work_dir, SUMMARY_REPORT_HTML_EMBED_IMG, replace_pathsep=True)
    except Exception as e:
        main_logger.error("Error while render summary html report: {}".format(str(e)))
        save_html_report('error', work_dir, SUMMARY_REPORT_HTML)
        save_html_report('error', work_dir, SUMMARY_REPORT_HTML_EMBED_IMG)


def build_performance_report(work_dir):

    performance_report = AutoDict()
    performance_report_detail = AutoDict()
    hardware = []
    for path, dirs, files in os.walk(os.path.abspath(work_dir)):
        for file in files:
            if file.endswith(SESSION_REPORT):
                with open(os.path.join(path, file), 'r') as report_file:
                    temp_report = json.loads(report_file.read())

                hw = temp_report['machine_info']['render_device']
                if hw not in hardware:
                    hardware.append(hw)
                tool = temp_report['machine_info']['tool']

                results = temp_report.pop('results', None)
                info = temp_report
                for test_package in results:
                    for test_config in results[test_package]:
                        results[test_package][test_config].pop('render_results', None)

                performance_report[tool].update({hw: info})

                for test_package in results:
                    for test_config in results[test_package]:
                        performance_report_detail[tool][test_package][test_config].update({hw: results[test_package][test_config]})

    # save_json_report(performance_report, work_dir, PERFORMANCE_REPORT, replace_pathsep=True)
    # save_json_report(performance_report_detail, work_dir, "re.json", replace_pathsep=True)
        env = jinja2.Environment(
        loader=jinja2.PackageLoader('core.reportExporter', 'templates'),
        autoescape=True
    )
    template = env.get_template('performance_compare.html')

    try:
        html_result = template.render(title='Performance report', report=performance_report, hardware=hardware, detail_report=performance_report_detail)
        save_html_report(html_result, work_dir, PERFORMANCE_REPORT_HTML, replace_pathsep=True)
    except Exception as e:
        main_logger.error("Error while render performance html report: {}".format(str(e)))
        save_html_report('error', work_dir, PERFORMANCE_REPORT_HTML)
