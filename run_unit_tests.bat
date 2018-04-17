rem call UnitTests\\keys_errors.bat
rem call UnitTests\\full_test.bat
rmdir /S /Q UnitTests\\Results
call UnitTests\\scripts_test.bat
call UnitTests\\full_test.bat