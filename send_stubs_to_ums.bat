set PATH=c:\python35\;c:\python35\scripts\;%PATH%
set PYTHONPATH=..\jobs_launcher\;%PYTHONPATH%

set SKIPPED_CASES_PATH=%1
set ERROR_CASES_PATH=%2
set HOST=%3
set OS=%4
set GPU=%5

python core\\isGroupSkipped.py --path_to_skipped_cases %SKIPPED_CASES_PATH% --path_to_error_cases %ERROR_CASES_PATH% --host %HOST% --os %OS% --gpu %GPU%