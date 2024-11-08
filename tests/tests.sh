#!/bin/bash

function failure
{
    echo "Tests failed"
    exit 1
}

cd "$(dirname "$0")"

python3 ./multiplatform/makefile.py -rv || failure
CC=clang python3 ./multiplatform/makefile.py -rv || failure
CC=x86_64-w64-mingw32-gcc python3 ./multiplatform/makefile.py -rv || failure

python3 ./lib_depend/makefile.py -rv || failure
python3 ./lib_depend/makefile.py -rvd || failure
