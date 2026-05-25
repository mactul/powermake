import os
import powermake

def run_tests():
    files = powermake.get_files("tests_main.py", "tests_init.py")
    assert(len(files) == 2)
    for file in files:
        assert(os.path.samefile(file, "tests_main.py") or os.path.samefile(file, "tests_init.py"))
    files_list = list(files)
    assert(not os.path.samefile(files_list[0], files_list[1]))

    files = powermake.get_files("../**/t*ts_init.py")
    assert(len(files) == 1 and os.path.samefile(next(iter(files)), "tests_init.py"))

    files = powermake.filter_files({"foo/bar/file1_windows.c", "foo/bar/file2_windows.h", "foo/bar/file1_linux.c", "foo/bar/file2_linux.h"}, "*_windows.*")
    assert(len(files) == 2)
    for file in files:
        assert("windows" not in file)
