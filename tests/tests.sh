#!/bin/bash

set -x

function failure
{
    echo "Tests failed"
    exit 1
}

cd "$(dirname "$0")"

export PYTHONPATH=$PYTHONPATH:$(pwd)/../

coverage run ./multiplatform/makefile.py --delete-cache

coverage run -a ./units/tests_main.py || failure

# coverage report && coverage html && firefox htmlcov/index.html
# exit 0

if [ "$1" != "weak" ]
then
    echo "Checking typing"
    mypy ../powermake --check-untyped-defs --python-version=3.10 --strict --implicit-reexport || failure
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
coverage run -a ./lib_depend/makefile.py -rv --add-flag='-fsanitize=address' --add-flag='-Wsecurity' | grep "ASAN propagated, MAGIC=zJgH_V5s2" || failure
coverage run -a ./lib_depend/makefile.py -rv --add-flag='-fsanitize=address' --add-flag='-Wsecurity' --no-propagate-cmdline-add-flag | grep "ASAN propagated, MAGIC=zJgH_V5s2" && failure

coverage run -a ./library/makefile.py || failure

coverage run -a ./multiplatform/makefile.py -c || failure
coverage run -a ./lib_depend/makefile.py -c || failure
coverage run -a ./lib_intermediate/makefile.py -c || failure
coverage run -a ./library/makefile.py -c || failure

coverage run -a ./library/makefile.py --shared-lib || failure
CC=x86_64-w64-mingw32-gcc coverage run -a ./library/makefile.py --shared-lib || failure

rm -rf ./multiplatform/.vscode
coverage run -a ./multiplatform/makefile.py --generate-vscode || failure
if [ ! -f "./multiplatform/.vscode/launch.json" ] || [ ! -f "./multiplatform/.vscode/tasks.json" ]
then
    failure
fi

rm -rf ./multiplatform/build
coverage run -a ./multiplatform/makefile.py -s test.c || failure
if [ ! -f "./multiplatform/build/.objs/Linux/x64/release/test.c.o" ] || [ -f "./multiplatform/build/.objs/Linux/x64/release/main.cpp.o" ]
then
    failure
fi

rm -rf ./library/install
coverage run -a ./library/makefile.py -cri || failure
if [ ! -f "./library/install/lib/libmy_lib.a" ] || [ ! -f "./library/install/include/my_lib/my_lib.h" ]
then
    failure
fi

rm -rf ./multiplatform/install
coverage run -a ./multiplatform/makefile.py -cri || failure
if [ ! -f "./multiplatform/install/bin/test" ]
then
    failure
fi

coverage run -a ./multiplatform/makefile.py -bvt | grep "Hello" || failure

coverage run -a ./multiplatform/makefile.py test | grep "Hello" || failure

coverage run -a ./multiplatform/makefile.py clean || failure
coverage run -a ./multiplatform/makefile.py test | grep "Nothing to run" || failure

coverage run -a ./multiplatform/makefile.py build -t | grep "Hello" || failure
coverage run -a ./multiplatform/makefile.py build -t | grep "build" && failure
coverage run -a ./multiplatform/makefile.py clean || failure
coverage run -a ./multiplatform/makefile.py -t build | grep "Nothing to run" || failure
coverage run -a ./multiplatform/makefile.py build -t foo bar | grep "build" && failure
coverage run -a ./multiplatform/makefile.py rebuild -t foo bar | grep -Pzo 'foo\nbar' || failure
coverage run -a ./multiplatform/makefile.py -t build | grep "build" || failure
rm -rf ./multiplatform/install
coverage run -a ./multiplatform/makefile.py install ./install -t build | grep "build" || failure
if [ ! -f "./multiplatform/install/bin/test" ]
then
    failure
fi
rm -rf ./multiplatform/install
coverage run -a ./multiplatform/makefile.py --test install ./install build | grep -Pzo 'install\n./install\nbuild' || failure
if [ -f "./multiplatform/install/bin/test" ]
then
    failure
fi

coverage run -a ./multiplatform/makefile.py foo bar something 2>&1 | grep "Unexpected positional argument foo" || failure

coverage run -a ./multiplatform/makefile.py build bar something 2>&1 | grep "Unexpected positional argument bar" || failure

coverage run -a ./multiplatform/makefile.py install ./install something 2>&1 | grep "Unexpected positional argument something" || failure

coverage run -a ./multiplatform/makefile.py test foo bar 2>&1 | grep -Pzo 'foo\nbar' || failure
coverage run -a ./multiplatform/makefile.py test foo bar 2>&1 | grep -E "^test$" && failure

coverage run -a ./multiplatform/makefile.py -qv 2>&1 | grep "Passing --quiet and --verbose arguments in the same time doesn't make any sense." || failure

coverage run -a ./multiplatform/makefile.py --version | grep "Apache-2.0" || failure

coverage report

COV=$(coverage report | tail -n 1 | awk -F " " '{print $4}' | sed 's/.$//')

python generate_badge.py $COV

if [ "$1" = "strict" ] && [ "$COV" -lt 90 ]
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
