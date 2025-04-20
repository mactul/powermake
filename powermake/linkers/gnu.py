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
from .common import Linker


_powermake_warning_flags_to_ld_flags: T.Dict[str, T.List[str]] = {
    "-w": [],
    "-Wall": [],
    "-Wextra": [],
    "-Weverything": [],
    "-Wsecurity": [],
    "-Werror": ["--fatal-warnings"],
    "-Wpedantic": [],
    "-pedantic": [],
    "-Wswitch": [],
    "-Wswitch-enum": [],
    "-fanalyzer": [],
    "-ffuzzer": []
}

_powermake_optimization_flags_to_ld_flags: T.Dict[str, T.List[str]] = {
    "-O0": [],
    "-Og": [],
    "-O": ["-O"],
    "-O1": ["-O"],
    "-O2": ["-O"],
    "-O3": ["-O"],
    "-Os": ["-O"],
    "-Oz": ["-O"],
    "-Ofast": ["-O"],
    "-fomit-frame-pointer": [],
}

_powermake_machine_flags_to_ld_flags: T.Dict[str, T.List[str]] = {
    "-m32": [],
    "-m64": [],
    "-march=native": [],
    "-mtune=native": [],
    "-mmmx": [],
    "-msse": [],
    "-msse2": [],
    "-msse3": [],
    "-mavx": [],
    "-mavx2": []
}

_powermake_flags_to_ld_flags: T.Dict[str, T.List[str]] = {
    **_powermake_warning_flags_to_ld_flags,
    **_powermake_optimization_flags_to_ld_flags,
    **_powermake_machine_flags_to_ld_flags,
    "-g": [],
    "-fPIC": [],
    "-fdiagnostics-color": [],
    "-fsecurity=1": [],
    "-fsecurity=2": [],
    "-fsecurity": []
}


class LinkerGNU(Linker):
    type: T.ClassVar = "gnu"

    def __init__(self, path: str = "c++"):
        super().__init__(path)

    def format_args(self, shared_libs: T.List[str], flags: T.List[str]) -> T.List[str]:
        return ["-l" + lib for lib in shared_libs] + self.translate_flags(flags)

    def basic_link_command(self, outputfile: str, objectfiles: T.Iterable[str], archives: T.List[str] = [], args: T.List[str] = []) -> T.List[str]:
        return [self.path, "-o", outputfile, *objectfiles, *archives, *args]

    def check_if_arg_exists(self, arg: str) -> bool:
        return subprocess.run([self.path, arg, "-E", get_empty_file()], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL).returncode == 0



class LinkerLD(LinkerGNU):
    type: T.ClassVar = "ld"
    translation_dict = _powermake_flags_to_ld_flags

    def __init__(self, path: str = "ld"):
        super().__init__(path)

    def check_if_arg_exists(self, arg: str) -> bool:
        return subprocess.run([self.path, arg, "-w"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL).returncode == 0



class LinkerGCC(LinkerGNU):
    type: T.ClassVar = "gcc"

    def __init__(self, path: str = "gcc"):
        super().__init__(path)


class LinkerGPlusPlus(LinkerGNU):
    type: T.ClassVar = "g++"

    def __init__(self, path: str = "g++"):
        super().__init__(path)


class LinkerClang(LinkerGNU):
    type: T.ClassVar = "clang"

    def __init__(self, path: str = "clang"):
        super().__init__(path)


class LinkerClangPlusPlus(LinkerGNU):
    type: T.ClassVar = "clang++"

    def __init__(self, path: str = "clang++"):
        super().__init__(path)


class LinkerMinGW(LinkerGNU):
    type: T.ClassVar = "mingw"

    def __init__(self, path: str = "x86_64-w64-mingw32-gcc"):
        super().__init__(path)

class LinkerMinGWPlusPlus(LinkerGNU):
    type: T.ClassVar = "mingw++"

    def __init__(self, path: str = "x86_64-w64-mingw32-g++"):
        super().__init__(path)

class LinkerMinGWLD(LinkerLD):
    type: T.ClassVar = "mingw-ld"

    def __init__(self, path: str = "x86_64-w64-mingw32-ld"):
        super().__init__(path)