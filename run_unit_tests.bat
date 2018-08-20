rmdir /S /Q UnitTests\\Results
rem call UnitTests\\keys_errors.bat
rem call UnitTests\\full_test.bat
call UnitTests\\full_test.bat
call UnitTests\\full_test_2.bat

call build_reports.bat UnitTests\\Results UnitTests 3021341uiaf=123u0
call get_status.bat UnitTests\\Results