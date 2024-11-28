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

if [[ $# -ne 1 && $1 != "weak" ]]
then
    echo "Checking typing"
    mypy ../powermake --check-untyped-defs --python-version=3.8 --strict --implicit-reexport || failure
fi

echo "checking multiplatform makefile with default, clang and MinGW toolchains"

python3 ./multiplatform/makefile.py -rv || failure

python3 ./multiplatform/makefile.py -m || failure
pushd ./multiplatform/
make rebuild || failure
popd

CC=clang python3 ./multiplatform/makefile.py -rv --assert-cc="clang" || failure

CC=aarch64-linux-gnu-gcc python3 ./multiplatform/makefile.py -rvd --no-prog-test --assert-cc="aarch64-linux-gnu-gcc" || failure

python3 ./multiplatform/makefile.py -rv --l ./linux_config1.json --assert-cc="clang" || failure
python3 ./multiplatform/makefile.py -rv --l ./linux_config2.json --no-prog-test --assert-cc="aarch64-linux-gnu-gcc" || failure

if [[ $# -ne 1 && $1 != "weak" ]]
then
NO_PROG_TEST=
else
NO_PROG_TEST="--no-prog-test"
fi
CC=x86_64-w64-mingw32-gcc python3 ./multiplatform/makefile.py -rv --assert-cc="x86_64-w64-mingw32-gcc" $NO_PROG_TEST || failure
python3 ./multiplatform/makefile.py -mv -l ./windows_config1.json --assert-cc="x86_64-w64-mingw32-gcc" $NO_PROG_TEST || failure
pushd ./multiplatform/
make rebuild || failure
popd
python3 ./multiplatform/makefile.py -rv -l ./windows_config2.json --assert-cc="i686-w64-mingw32-gcc" $NO_PROG_TEST || failure

echo "testing lib compilation and link accross powermake makefiles, in release and in debug"
python3 ./lib_depend/makefile.py -rv || failure
CC=x86_64-w64-mingw32-gcc python3 ./lib_depend/makefile.py -rvd --assert-cc="x86_64-w64-mingw32-gcc" $NO_PROG_TEST || failure
