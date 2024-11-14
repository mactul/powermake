#!/bin/bash

function failure
{
    echo "Tests failed"
    exit 1
}

cd "$(dirname "$0")"

export PYTHONPATH=$PYTHONPATH:$(pwd)/../

python3 ./multiplatform/makefile.py --version

echo "Checking typing"
mypy ../powermake --check-untyped-defs --python-version=3.8 --strict || failure

echo "checking multiplatform makefile with default/clang and MinGW toolchains"
python3 ./multiplatform/makefile.py -rv || failure
CC=clang python3 ./multiplatform/makefile.py -rv || failure
CC=x86_64-w64-mingw32-gcc python3 ./multiplatform/makefile.py -rv || failure

echo "testing lib compilation and link accross powermake makefiles, in release and in debug"
python3 ./lib_depend/makefile.py -rv || failure
python3 ./lib_depend/makefile.py -rvd || failure
