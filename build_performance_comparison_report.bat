set JL_ENGINES_COMPARE="True"
set PATH=c:\python35\;c:\python35\scripts\;%PATH%

python -c "import core.reportExporter; core.reportExporter.generate_reports_for_perf_comparison('%1', '%2', '%3')"