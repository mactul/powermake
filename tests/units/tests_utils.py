import os
import shutil
import __main__
import powermake
import powermake.utils
from unittest import mock

_count = 0
def fake_input(*answers: str):
    global _count
    _count = 0
    def _input(prompt: str) -> str:
        global _count
        _count += 1
        print(prompt, answers[_count-1], sep="")
        return answers[_count-1]

    return _input

def path_exists_forget_devnull(path: str):
    if path == "/dev/null":
        return False
    return os.path.exists(path)

def run_tests():
    # Testing makedirs
    powermake.utils.makedirs("test_dir_create/foo/bar")
    assert(os.path.exists("test_dir_create/foo/bar"))
    powermake.delete_files_from_disk("test_dir_create")

    # Testing _store_run_path
    powermake.utils._store_run_path("something/foo/bar")
    assert(powermake.utils._get_run_path() == "something/foo/bar")

    # Testing _get_makefile_path and _store_makefile_path
    assert(powermake.utils._get_makefile_path() == __main__.__file__)
    powermake.utils._store_makefile_path("foor/bar.py")
    assert(powermake.utils._get_makefile_path() == "foor/bar.py")

    # Testing handle_filename_conflict
    powermake.delete_files_from_disk("test_file_conflict*")
    assert(not os.path.exists("test_file_conflict"))
    assert(not os.path.exists("test_file_conflict.old"))
    assert(not os.path.exists("test_file_conflict.old.1"))
    file = open("test_file_conflict", "w")
    file.write("hello")
    file.close()
    assert(os.path.exists("test_file_conflict"))
    assert(powermake.utils.handle_filename_conflict("foo/bar.py", force_overwrite=True) == "foo/bar.py")
    assert(powermake.utils.handle_filename_conflict("test_file_conflict", force_overwrite=True) == "test_file_conflict")
    assert(powermake.utils.handle_filename_conflict("foo/bar.py", force_overwrite=False) == "foo/bar.py")
    with mock.patch("powermake.utils.input", new=fake_input("1")):
        assert(powermake.utils.handle_filename_conflict("test_file_conflict", force_overwrite=False) == "test_file_conflict")
    with mock.patch("powermake.utils.input", new=fake_input("2")):
        assert(powermake.utils.handle_filename_conflict("test_file_conflict", force_overwrite=False) == "test_file_conflict")
        assert(not os.path.exists("test_file_conflict"))
        assert(os.path.exists("test_file_conflict.old"))
    shutil.copy2("test_file_conflict.old", "test_file_conflict")
    with mock.patch("powermake.utils.input", new=fake_input("2")):
        assert(powermake.utils.handle_filename_conflict("test_file_conflict", force_overwrite=False) == "test_file_conflict")
        assert(not os.path.exists("test_file_conflict"))
        assert(os.path.exists("test_file_conflict.old"))
        assert(os.path.exists("test_file_conflict.old.1"))
    shutil.copy2("test_file_conflict.old", "test_file_conflict")
    with mock.patch("powermake.utils.input", new=fake_input("2")):
        assert(powermake.utils.handle_filename_conflict("test_file_conflict", force_overwrite=False) == "test_file_conflict")
        assert(not os.path.exists("test_file_conflict"))
        assert(os.path.exists("test_file_conflict.old"))
        assert(os.path.exists("test_file_conflict.old.1"))
        assert(os.path.exists("test_file_conflict.old.2"))
    shutil.copy2("test_file_conflict.old", "test_file_conflict")
    with mock.patch("powermake.utils.input", new=fake_input("3", "test_file_conflict_2")):
        assert(powermake.utils.handle_filename_conflict("test_file_conflict", force_overwrite=False) == "test_file_conflict_2")
        assert(os.path.exists("test_file_conflict"))
    with mock.patch("powermake.utils.input", new=fake_input("3", "")):
        assert(powermake.utils.handle_filename_conflict("test_file_conflict", force_overwrite=False) == "test_file_conflict.1")
        assert(os.path.exists("test_file_conflict"))
    file = open("test_file_conflict.1", "w")
    file.write("hello")
    file.close()
    with mock.patch("powermake.utils.input", new=fake_input("3", "")):
        assert(powermake.utils.handle_filename_conflict("test_file_conflict", force_overwrite=False) == "test_file_conflict.2")
        assert(os.path.exists("test_file_conflict"))
    with mock.patch("powermake.utils.input", new=fake_input("foo", "4")):
        assert(powermake.utils.handle_filename_conflict("test_file_conflict", force_overwrite=False) == "")
        assert(os.path.exists("test_file_conflict"))
    powermake.delete_files_from_disk("test_file_conflict*")

    # Test join_absolute_paths
    assert(powermake.utils.join_absolute_paths("/foo/bar", "/some/thing") == "/foo/bar/some/thing")
    assert(powermake.utils.join_absolute_paths("/foo/bar", "/some/thing/../a/b") == "/foo/bar/some/thing/__/a/b")
    assert(powermake.utils.join_absolute_paths("/foo/bar", "../a/b") == "/foo/bar/__/a/b")
    assert(powermake.utils.join_absolute_paths("/foo/bar", "./a/b") == "/foo/bar/a/b")

    # Test print_bytes
    powermake.utils.print_bytes(b"Arabic character:\n\xd8\x84\n")

    # Test get_empty_file
    filepath = powermake.utils.get_empty_file()
    file = open(filepath, "rb")
    assert(file.read() == b"")
    file.close()
    # Test get_empty_file is /dev/null doesn't exists
    with mock.patch("powermake.utils.os.path.exists", new=path_exists_forget_devnull):
        filepath = powermake.utils.get_empty_file()
        assert(filepath != "/dev/null")
        file = open(filepath, "rb")
        assert(file.read() == b"")
        file.close()