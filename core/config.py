import logging

logging.basicConfig(filename='launcher.engine.log', level=logging.INFO, format=u'%(filename)-21s[LINE:%(lineno)d] in:%(funcName)-21s #%(levelname)-8s [%(asctime)s] %(message)s')
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
