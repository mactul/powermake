#!/bin/bash

set -x

function failure
{
    echo "Tests failed"
    exit 1
}

cd "$(dirname "$0")"

export PYTHONPATH=$PYTHONPATH:$(pwd)/../

python3 ./multiplatform/makefile.py --delete-cache

coverage run ./units/tests_main.py || failure


if [ "$1" != "weak" ]
then
    echo "Checking typing"
    mypy ../powermake --check-untyped-defs --python-version=3.8 --strict --implicit-reexport || failure
fi

echo "checking multiplatform makefile with default, clang and MinGW toolchains"

coverage run -a ./multiplatform/makefile.py -rv || failure

coverage run -a ./multiplatform/makefile.py -v || failure

coverage run -a ./multiplatform/makefile.py -m --always-overwrite || failure
pushd ./multiplatform/
make rebuild || failure
popd

CC=clang coverage run -a ./multiplatform/makefile.py -rv --assert-cc="clang" || failure

CC=aarch64-linux-gnu-gcc coverage run -a ./multiplatform/makefile.py -rvd --no-prog-test --assert-cc="aarch64-linux-gnu-gcc" || failure

coverage run -a ./multiplatform/makefile.py -rv --l ./linux_config1.json --assert-cc="clang" || failure
coverage run -a ./multiplatform/makefile.py -rv --l ./linux_config2.json --no-prog-test --assert-cc="aarch64-linux-gnu-gcc" || failure

if [ "$1" != "weak" ]
then
NO_PROG_TEST=
else
NO_PROG_TEST="--no-prog-test"
fi
CC=x86_64-w64-mingw32-gcc coverage run -a ./multiplatform/makefile.py -rv --assert-cc="x86_64-w64-mingw32-gcc" $NO_PROG_TEST || failure
coverage run -a ./multiplatform/makefile.py --always-overwrite -mv -l ./windows_config1.json --assert-cc="x86_64-w64-mingw32-gcc" $NO_PROG_TEST || failure
pushd ./multiplatform/
make rebuild || failure
popd
coverage run -a ./multiplatform/makefile.py -rv -l ./windows_config2.json --assert-cc="i686-w64-mingw32-gcc" $NO_PROG_TEST || failure

coverage run -a ./parent/makefile.py -rv || failure

echo "testing lib compilation and link accross powermake makefiles, in release and in debug"
coverage run -a ./lib_depend/makefile.py -rv || failure
CC=x86_64-w64-mingw32-gcc coverage run -a ./lib_depend/makefile.py -rvd --assert-cc="x86_64-w64-mingw32-gcc" $NO_PROG_TEST || failure

coverage run -a ./library/makefile.py || failure

coverage run -a ./multiplatform/makefile.py -c || failure
coverage run -a ./lib_depend/makefile.py -c || failure
coverage run -a ./lib_intermediate/makefile.py -c || failure
coverage run -a ./library/makefile.py -c || failure

coverage report

if [ -f "$GITHUB_ENV" ]
then
    coverage json -o ../coverage.json
fi

if [ "$1" = "strict" ] && COV=$(coverage report | tail -n 1 | awk -F " " '{print $4}' | sed 's/.$//') && [ "$COV" -lt 90 ]
then
    printf "\033[31;1mYou don't have enough test coverage ($COV%% < 90%%) !\033[0m\n"
    which firefox
    if [ $? -eq 0 ]
    then
        coverage html
        firefox htmlcov/index.html
    fi
    failure
fi