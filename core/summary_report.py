import jinja2
import json
import os

def save_json_report(report, session_dir, file_name):
    with open(os.path.abspath(os.path.join(session_dir, file_name)), "w") as file:
        json.dump(report, file, indent=" ", sort_keys=True)


def save_html_report(report, session_dir, file_name):
    with open(os.path.abspath(os.path.join(session_dir, file_name)), "w") as file:
        file.write(report)

def build_summary_report(work_dir):

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
        autoescape=True
    )
    template = env.get_template('session_report.html')

    html_result = template.render(title='Summary report', report=summary_report)
    save_html_report(html_result, work_dir, 'summary_report.html')

    html_result = template.render(title='Summary report', report=summary_report_embed_img)
    save_html_report(html_result, work_dir, 'summary_report_embed_img.html')
