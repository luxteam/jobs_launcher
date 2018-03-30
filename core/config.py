import logging

logging.basicConfig(filename='launcher.engine.log',
                    filemode='w',
                    level=logging.INFO,
                    format=u'%(filename)-21s[LINE:%(lineno)-3d] #%(levelname)-8s in:%(funcName)-23s [%(asctime)s] %(message)s')
main_logger = logging.getLogger('main_logger')

SIMPLE_RENDER_TIMEOUT = 10
TIMEOUT = 3000
TIMEOUT_PAR = 3

TEST_REPORT_NAME = 'report.json'
TEST_REPORT_NAME_COMPARED = 'report_compare.json'

SESSION_REPORT = 'session_report.json'
SESSION_REPORT_EMBED_IMG = 'session_report_embed_img.json'
SESSION_REPORT_HTML = 'session_report.html'
SESSION_REPORT_HTML_EMBED_IMG = 'session_report_embed_img.html'

SUMMARY_REPORT = 'summary_report.json'
SUMMARY_REPORT_EMBED_IMG = 'summary_report_embed_img.json'
SUMMARY_REPORT_HTML = 'summary_report.html'
SUMMARY_REPORT_HTML_EMBED_IMG = 'summary_report_embed_img.html'

POSSIBLE_JSON_IMG_KEYS = ['baseline_color_path', 'baseline_opacity_path', 'render_color_path', 'render_opacity_path']
POSSIBLE_JSON_IMG_RENDERED_KEYS = ['render_color_path', 'render_opacity_path']
BASELINE_MANIFEST = 'baseline_manifest.json'
BASELINE_SESSION_REPORT = 'baseline_session_report.json'

PERFORMANCE_REPORT = 'performance_report.json'
PERFORMANCE_REPORT_HTML = 'performance_report.html'
