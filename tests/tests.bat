cd /D "%~dp0"


SET PYTHONPATH="%%PYTHONPATH%%:%~dp0/../"


py ./multiplatform/makefile.py --delete-cache
py ./multiplatform/makefile.py -rv
py ./multiplatform/makefile.py -rv

py ./lib_depend/makefile.py -rv