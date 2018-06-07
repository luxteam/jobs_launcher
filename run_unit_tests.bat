rem call UnitTests\\keys_errors.bat
rem call UnitTests\\full_test.bat
rmdir /S /Q UnitTests\\Results
call UnitTests\\full_test.bat
call UnitTests\\full_test_2.bat

set PATH=c:\python35\;c:\python35\scripts\;%PATH%
set BRANCH_NAME=master
python -c "import core.reportExporter; core.reportExporter.build_summary_reports('UnitTests\\Results')"