set PATH=c:\python35\;c:\python35\scripts\;%PATH%
set REPORTS_DIR=%1
python -c "import core.summary_report; core.summary_report.build_summary_report('%REPORTS_DIR%')"