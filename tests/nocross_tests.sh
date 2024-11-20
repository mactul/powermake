#!/bin/bash

set -x

function failure
{
    echo "Tests failed"
    exit 1
}

cd "$(dirname "$0")"

export PYTHONPATH=$PYTHONPATH:$(pwd)/../

python3 ./multiplatform/makefile.py --version

python3 ./multiplatform/makefile.py -rv || failure

CC=clang python3 ./multiplatform/makefile.py -rv --assert-cc="clang" || failure

python3 ./multiplatform/makefile.py -rv --l ./linux_config3.json --assert-cc="clang" || failure

echo "testing lib compilation and link accross powermake makefiles, in release and in debug"
python3 ./lib_depend/makefile.py -rvd || failure
