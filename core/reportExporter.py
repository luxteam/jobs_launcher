import os
import jinja2
import json
import base64
import shutil
import datetime
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


def build_session_report(report, session_dir, template=None):
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
                        # TODO: count failed - need expected.json
                        report['results'][result][item]['passed'] += 1

                        try:
                            report['machine_info'].update({'render_device': jtem['render_device']})
                            report['machine_info'].update({'tool': jtem['tool']})
                            report['machine_info'].update({'render_version': jtem['render_version']})
                            report['machine_info'].update({'core_version': jtem['core_version']})
                        except Exception as err:
                            pass
                            main_logger.warning(str(err))
                    report['results'][result][item]['total'] = report['results'][result][item]['passed'] + report['results'][result][item]['failed']
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
    report['machine_info'].update({'reporting_date': datetime.date.today().strftime('%m/%d/%Y')})

    if template:
        env = jinja2.Environment(
            loader=jinja2.PackageLoader('core.reportExporter', 'templates'),
            autoescape=True
        )
        template = env.get_template(template)

        save_json_report(report, session_dir, SESSION_REPORT, replace_pathsep=True)

        try:
            shutil.copytree(os.path.join(os.path.split(__file__)[0], REPORT_RESOURCES_PATH),
                            os.path.join(session_dir, 'report_resources'))
        except Exception as err:
            main_logger.error("Failed to copy report resources: {}".format(str(err)))

        try:
            # html_result = template.render(title='Session report', report={'_cur_': report})
            html_result = template.render(title="Session report", report={'_cur_': report}, pageID="summaryA",
                                                   common_info={'reporting_date': report['machine_info']['reporting_date'],
                                                                'core_version': report['machine_info']['core_version'],
                                                                'render_version': report['machine_info']['render_version']
                                                                })

            save_html_report(html_result, session_dir, SESSION_REPORT_HTML, replace_pathsep=True)
        except Exception as e:
            main_logger.error("Error while render html report {}".format(str(e)))
            save_html_report('error', session_dir, SESSION_REPORT_HTML)

        # # make embed_img reports
        # report = make_base64_img(session_dir, report)
        # save_json_report(report, session_dir, SESSION_REPORT_EMBED_IMG, replace_pathsep=True)
        #
        # try:
        #     html_result = template.render(title='Session report', report={'_cur_': report})
        #     save_html_report(html_result, session_dir, SESSION_REPORT_HTML_EMBED_IMG, replace_pathsep=True)
        # except Exception as e:
        #     main_logger.error("Error while render html report {}".format(str(e)))
        #     save_html_report('error', session_dir, SESSION_REPORT_HTML_EMBED_IMG)

    return report


def build_summary_report(work_dir):
    summary_report = {}
    summary_report_embed_img = {}
    common_info = {}
    for path, dirs, files in os.walk(os.path.abspath(work_dir)):
        for file in files:
            # build embeded summary report
            # if file.endswith(SESSION_REPORT_EMBED_IMG):
            #     basename = os.path.basename(path)
            #     basename = os.path.relpath(path, work_dir).split(os.path.sep)[0]
            #     basepath = os.path.relpath(path, work_dir)
            #     with open(os.path.join(path, file), 'r') as report_file:
            #         summary_report_embed_img[os.path.basename(path)] = json.loads(report_file.read())
            #     try:
            #         for test_package in summary_report_embed_img[basename]['results']:
            #             for test_conf in summary_report_embed_img[basename]['results'][test_package]:
            #                 summary_report_embed_img[basename]['results'][test_package][test_conf].update({'result_path': os.path.relpath(os.path.join(work_dir, basepath,summary_report_embed_img[basename]['results'][test_package][test_conf]['result_path']),work_dir)})
            #     except Exception as e:
            #         main_logger.error(str(e))

            # build summary report
            if file.endswith(SESSION_REPORT):
                basename = os.path.basename(path)
                basename = os.path.relpath(path, work_dir).split(os.path.sep)[0]
                basepath = os.path.relpath(path, work_dir)
                with open(os.path.join(path, file), 'r') as report_file:
                    summary_report[basename] = json.loads(report_file.read())

                try:
                    for test_package in summary_report[basename]['results']:
                        for test_conf in summary_report[basename]['results'][test_package]:
                            for jtem in summary_report[basename]['results'][test_package][test_conf]['render_results']:

                                for img in POSSIBLE_JSON_IMG_KEYS:
                                    if img in jtem.keys():
                                        jtem.update({img: os.path.relpath(os.path.join(work_dir, basepath, jtem[img]), work_dir)})

                            summary_report[basename]['results'][test_package][test_conf].update({'result_path': os.path.relpath(os.path.join(work_dir, basepath, summary_report[basename]['results'][test_package][test_conf]['result_path']), work_dir)})

                    if common_info:
                        for key in common_info:
                            if not summary_report[basename]['machine_info'][key] == common_info[key]:
                                main_logger.warning("Different versions in {}: {} vs. {}".format(key, summary_report[basename]['machine_info'][key], common_info[key]))
                                common_info[key] = '! Different values !'
                    else:
                        common_info.update({'reporting_date': summary_report[basename]['machine_info']['reporting_date'],
                                       'render_version': summary_report[basename]['machine_info']['render_version'],
                                       'core_version': summary_report[basename]['machine_info']['core_version']
                                       })

                except Exception as e:
                    main_logger.error(str(e))

    # save_json_report(summary_report, work_dir, SUMMARY_REPORT, replace_pathsep=True)
    # save_json_report(summary_report_embed_img, work_dir, SUMMARY_REPORT_EMBED_IMG, replace_pathsep=True)
    #
    # env = jinja2.Environment(
    #     loader=jinja2.PackageLoader('core.reportExporter', 'templates'),
    #     autoescape=True
    # )
    # template = env.get_template('session_report.html')
    #
    # try:
    #     html_result = template.render(title='Summary report', report=summary_report)
    #     save_html_report(html_result, work_dir, SUMMARY_REPORT_HTML, replace_pathsep=True)
    #
    #     html_result = template.render(title='Summary report', report=summary_report_embed_img)
    #     save_html_report(html_result, work_dir, SUMMARY_REPORT_HTML_EMBED_IMG, replace_pathsep=True)
    # except Exception as e:
    #     main_logger.error("Error while render summary html report: {}".format(str(e)))
    #     save_html_report('error', work_dir, SUMMARY_REPORT_HTML)
    #     save_html_report('error', work_dir, SUMMARY_REPORT_HTML_EMBED_IMG)

    return summary_report, common_info


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

    # env = jinja2.Environment(
    #     loader=jinja2.PackageLoader('core.reportExporter', 'templates'),
    #     autoescape=True
    # )
    # template = env.get_template('performance_compare.html')
    #
    # try:
    #     html_result = template.render(title='Performance report', report=performance_report, hardware=hardware,
    #                                   detail_report=performance_report_detail)
    #     save_html_report(html_result, work_dir, PERFORMANCE_REPORT_HTML, replace_pathsep=True)
    # except Exception as e:
    #     main_logger.error("Error while render performance html report: {}".format(str(e)))
    #     save_html_report('error', work_dir, PERFORMANCE_REPORT_HTML)

    return performance_report, hardware, performance_report_detail


def build_compare_report(work_dir):
    compare_report = AutoDict()
    hardware = []
    for path, dirs, files in os.walk(os.path.abspath(work_dir)):
        for file in files:
            if file == SESSION_REPORT or file == BASELINE_SESSION_REPORT:
                with open(os.path.join(path, file), 'r') as report_file:
                    temp_report = json.loads(report_file.read())

                hw = temp_report['machine_info']['render_device']

                if file == BASELINE_SESSION_REPORT:
                    hw = hw + '[Baseline]'
                hardware.append(hw)

                for test_package in temp_report['results']:
                    for test_config in temp_report['results'][test_package]:
                        for item in temp_report['results'][test_package][test_config]['render_results']:
                            if not compare_report[item['test_case']]:
                                compare_report[item['test_case']] = {}
                            compare_report[item['test_case']].update({item['render_device']: os.path.relpath(os.path.join(path, item['render_color_path']), work_dir) })

    return compare_report, hardware


def build_summary_reports(work_dir):
    try:
        shutil.copytree(os.path.join(os.path.split(__file__)[0], REPORT_RESOURCES_PATH), os.path.join(work_dir, 'report_resources'))
    except Exception as err:
        main_logger.error("Failed to copy report resources: {}".format(str(err)))

    env = jinja2.Environment(
        loader=jinja2.PackageLoader('core.reportExporter', 'templates'),
        autoescape=True
    )

    try:
        summary_template = env.get_template('summary_template.html')
        summary_report, common_info = build_summary_report(work_dir)
        save_json_report(summary_report, work_dir, SUMMARY_REPORT, replace_pathsep=True)
        summary_html = summary_template.render(title="Summary report", report=summary_report, pageID="summaryA", common_info=common_info)
        save_html_report(summary_html, work_dir, SUMMARY_REPORT_HTML, replace_pathsep=True)
    except Exception as err:
        summary_html = "Error while building summary report: {}".format(str(err))
        main_logger.error(summary_html)
        save_html_report("Error while building summary report: {}".format(str(err)), work_dir, SUMMARY_REPORT_HTML, replace_pathsep=True)

    try:
        performance_template = env.get_template('performance_template.html')
        performance_report, hardware, performance_report_detail = build_performance_report(work_dir)
        save_json_report(performance_report, work_dir, PERFORMANCE_REPORT, replace_pathsep=True)
        save_json_report(performance_report_detail, work_dir, 'perf.json', replace_pathsep=True)
        performance_html = performance_template.render(title="Performance", performance_report=performance_report, hardware=hardware, performance_report_detail=performance_report_detail, pageID="performanceA", common_info=common_info)
        save_html_report(performance_html, work_dir, PERFORMANCE_REPORT_HTML, replace_pathsep=True)
    except Exception as err:
        performance_html = "Error while building performance report: {}".format(str(err))
        main_logger.error(performance_html)
        save_html_report(performance_html, work_dir, PERFORMANCE_REPORT_HTML, replace_pathsep=True)

    try:
        compare_template = env.get_template('compare_template.html')
        compare_report, hardware = build_compare_report(work_dir)
        # TODO
        save_json_report(compare_report, work_dir, 'compare.json', True)
        compare_html = compare_template.render(title="Compare", hardware=hardware, compare_report=compare_report, pageID="compareA", common_info=common_info)
        save_html_report(compare_html, work_dir, "compare_report.html", replace_pathsep=True)
    except Exception as err:
        compare_html = "Error while building compare report: {}".format(str(err))
        main_logger.error(compare_html)
        save_html_report(compare_html, work_dir, "compare_report.html", replace_pathsep=True)
