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

import subprocess
import typing as T

from ..utils import get_empty_file
from .common import SharedLinker
from ..linkers.gnu import _powermake_flags_to_ld_flags


class SharedLinkerGNU(SharedLinker):
    type: T.ClassVar = "gnu"
    shared_lib_extension: T.ClassVar = ".so"

    def __init__(self, path: str = "c++"):
        super().__init__(path)

    def format_args(self, shared_libs: T.List[str], flags: T.List[str]) -> T.List[str]:
        return ["-l" + lib for lib in shared_libs] + self.translate_flags(flags)

    def basic_link_command(self, outputfile: str, objectfiles: T.Iterable[str], archives: T.List[str] = [], args: T.List[str] = []) -> T.List[str]:
        return [self.path, "-shared", "-o", outputfile, *objectfiles, *archives, *args]

    def check_if_arg_exists(self, arg: str) -> bool:
        return subprocess.run([self.path, arg, "-E", get_empty_file()], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL).returncode == 0


class SharedLinkerLD(SharedLinkerGNU):
    type: T.ClassVar = "ld"
    translation_dict = _powermake_flags_to_ld_flags

    def __init__(self, path: str = "ld"):
        super().__init__(path)

    def check_if_arg_exists(self, arg: str) -> bool:
        return subprocess.run([self.path, arg, "-w"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL).returncode == 0


class SharedLinkerGCC(SharedLinkerGNU):
    type: T.ClassVar = "gcc"

    def __init__(self, path: str = "gcc"):
        super().__init__(path)


class SharedLinkerGPlusPlus(SharedLinkerGNU):
    type: T.ClassVar = "g++"

    def __init__(self, path: str = "g++"):
        super().__init__(path)


class SharedLinkerClang(SharedLinkerGNU):
    type: T.ClassVar = "clang"

    def __init__(self, path: str = "clang"):
        super().__init__(path)


class SharedLinkerClangPlusPlus(SharedLinkerGNU):
    type: T.ClassVar = "clang++"

    def __init__(self, path: str = "clang++"):
        super().__init__(path)


class SharedLinkerMinGW(SharedLinkerGNU):
    type: T.ClassVar = "mingw"

    def __init__(self, path: str = "x86_64-w64-mingw32-gcc"):
        super().__init__(path)

class SharedLinkerMinGWPlusPlus(SharedLinkerGNU):
    type: T.ClassVar = "mingw++"

    def __init__(self, path: str = "x86_64-w64-mingw32-g++"):
        super().__init__(path)

class SharedLinkerMinGWLD(SharedLinkerLD):
    type: T.ClassVar = "mingw-ld"

    def __init__(self, path: str = "x86_64-w64-mingw32-ld"):
        super().__init__(path)