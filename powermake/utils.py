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
