# Copyright 2025 Macéo Tuloup

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
import tempfile
import typing as T
import __main__ as __makefile__


_run_path = "."
def _store_run_path(run_path: str) -> None:
    global _run_path
    _run_path = run_path


def _get_run_path() -> str:
    return _run_path


_makefile_path = None
def _store_makefile_path(makefile_path: str) -> None:
    global _makefile_path
    _makefile_path = makefile_path


def _get_makefile_path() -> T.Union[str, None]:
    return _makefile_path or (__makefile__.__file__ if hasattr(__makefile__, '__file__') else None)


def handle_filename_conflict(filepath: str, force_overwrite: bool) -> str:
    if force_overwrite:
        return filepath

    if os.path.exists(filepath):
        answer = ""
        while answer not in ["1", "2", "3", "4"]:
            answer = input(f"The file {filepath} already exists, what do you want to do ?\n\n1: Overwrite\n2: Rename the old one '{filepath}.old'\n3: Rename this one\n4: Abort\n\n1 2 3 4: ")
        if answer == "1":
            return filepath
        if answer == "2":
            if os.path.exists(filepath + ".old"):
                i = 1
                while os.path.exists(filepath + ".old." + str(i)):
                    i += 1
                os.rename(filepath, filepath + ".old." + str(i))
            else:
                os.rename(filepath, filepath + ".old")
            return filepath
        if answer == "3":
            new_filepath = input("Enter the new filepath (keep empty for auto-renaming): ")
            if new_filepath != "":
                return new_filepath
            else:
                i = 1
                while os.path.exists(filepath + "." + str(i)):
                    i += 1
                return filepath + "." + str(i)
        return ""
    return filepath


def makedirs(path: str, exist_ok: bool = True) -> None:
    """
    Generate directories recursively.
    Equivalent of `mkdir -p $PATH` on Linux.

    The only difference with `os.makedirs` is that this function accept a empty path; it just do nothing in this case.

    Parameters
    ----------
    path : str
        The path of the directory to create recursively.
    exist_ok : bool, optional
        - if `False`, raises an error if the directory already exists.
        - if `True`, an existing directory is just ignored.
    """
    if path != '':
        os.makedirs(path, exist_ok=exist_ok)


def join_absolute_paths(path1: str, path2: str) -> str:
    return os.path.normpath(path1 + "/" + os.path.splitdrive(path2)[1].replace("..", "__"))


def print_bytes(b: bytes) -> None:
    sys.stdout.flush()
    stdout_fd = sys.stdout.fileno()

    written = 0
    while written < len(b):
        written += os.write(stdout_fd, b[written:])
    sys.stdout.flush()


_tempdir = None
_empty_file = None
def get_empty_file() -> str:
    global _empty_file
    global _tempdir
    if os.path.exists("/dev/null"):
        return "/dev/null"
    if _empty_file is None or not os.path.exists(_empty_file):
        _tempdir = tempfile.TemporaryDirectory("powermake_utils")
        _empty_file = os.path.join(_tempdir.name, "emptyfile")
        file = open(_empty_file, "w")
        file.close()

    return _empty_file
