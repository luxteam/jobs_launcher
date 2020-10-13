set PATH=c:\python35\;c:\python35\scripts\;%PATH%
set PYTHONPATH=..\jobs_launcher\;%PYTHONPATH%

set PATH=%1
set PATTERN=%2

python core\\isGroupSkipped.py --path %PATH% --pattern %PATTERN%