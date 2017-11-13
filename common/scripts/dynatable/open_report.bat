@echo off

for %%G in (%cd%\json\*.json) do (
 set LAST=%%G
)

del cmd_summary_report.json.js

type nul >> cmd_summary_report.json.js
echo data = `[ >> %cd%\cmd_summary_report.json.js

for %%G in (%cd%\json\*.json) do (
 type %%G | findstr /v [ | findstr /v ] >> cmd_summary_report.json.js
 if NOT %%G == %LAST% (
 	echo , >> cmd_summary_report.json.js
 )
)

echo ]`; >> cmd_summary_report.json.js

start chrome "index.html"