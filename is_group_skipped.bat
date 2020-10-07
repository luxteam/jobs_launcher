set PATH=c:\python35\;c:\python35\scripts\;%PATH%
set PYTHONPATH=..\jobs_launcher\;%PYTHONPATH%

set GPU=%1
set OS=%2
set ENGINE=%3
set TESTS_PATH=%4

python is_group_skipped.py --gpu %GPU% --os %OS% --engine %ENGINE% --tests_path %TESTS_PATH%