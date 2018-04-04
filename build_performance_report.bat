set PATH=c:\python35\;c:\python35\scripts\;%PATH%
set REPORTS_DIR=%1
python -c "import core.reportExporter; core.reportExporter.build_performance_report('%REPORTS_DIR%')"