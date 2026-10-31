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
SET ASM=ml64
py ./lib_depend/makefile.py -rv || goto :failed
SET ASM=

py ./use_zlib/makefile.py -rv --pkg-install-noconfirm || goto :failed
SET CC=cl
py ./use_zlib/makefile.py -rv --pkg-install-noconfirm || goto :failed
SET CC=

py ./mouse_trail/makefile.py -rv --os Android --pkg-install-noconfirm || goto :failed

goto :EOF

:failed
echo "tests failed"
exit /b 1