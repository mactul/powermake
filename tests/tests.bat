cd /D "%~dp0"


SET PYTHONPATH=%~dp0..\


py ./multiplatform/makefile.py -rv || goto :failed
SET CC=cl
py ./multiplatform/makefile.py -rvd || goto :failed
SET CC=

py ./multiplatform/makefile.py -rvd -l windows_config3.json || goto :failed
py ./multiplatform/makefile.py -rvd -l windows_config4.json || goto :failed

py ./lib_depend/makefile.py -rv || goto :failed
SET CC=cl
py ./lib_depend/makefile.py -rv || goto :failed
SET CC=

goto :EOF

:failed
echo "tests failed"
exit /b 1