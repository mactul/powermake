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

from .common import Compiler
from ..utils import get_empty_file


_powermake_warning_flags_to_msvc_flags: T.Dict[str, T.List[str]] = {
    "-w": ["/W0"],
    "-Wall": ["/W3"],
    "-Wextra": ["/W4"],
    "-Weverything": ["/Wall"],
    "-Wsecurity": ["/Wall"],
    "-Werror": ["/WX"],
    "-Wpedantic": [],
    "-pedantic": [],
    "-Wswitch": ["/we4062"],
    "-Wswitch-enum": ["/we4061"],
    "-fanalyzer": ["/analyze"],
    "-ffuzzer": ["/fsanitize=address", "/fsanitize=fuzzer"]
}

_powermake_optimization_flags_to_msvc_flags: T.Dict[str, T.List[str]] = {
    "-O0": ["/Od"],
    "-Og": ["/Od"],
    "-O": ["/O1"],
    "-O1": ["/O1"],
    "-O2": ["/O2"],
    "-O3": ["/Ox", "/fp:fast"],
    "-Os": ["/O1", "/GL"],
    "-Oz": ["/O1", "/Oi", "/GL"],
    "-Ofast": ["/Ox", "/fp:fast"],
    "-fomit-frame-pointer": ["/Oy"],
}

_powermake_machine_flags_to_msvc_flags: T.Dict[str, T.List[str]] = {
    "-m32": [],
    "-m64": [],
    "-march=native": [],
    "-mtune=native": [],
    "-mmmx": ["/arch:MMX"],
    "-msse": ["/arch:SSE"],
    "-msse2": ["/arch:SSE2"],
    "-msse3": ["/arch:SSE3"],
    "-mavx": ["/arch:AVX"],
    "-mavx2": ["/arch:AVX2"]
}

_powermake_flags_to_msvc_flags: T.Dict[str, T.List[str]] = {
    **_powermake_warning_flags_to_msvc_flags,
    **_powermake_optimization_flags_to_msvc_flags,
    **_powermake_machine_flags_to_msvc_flags,
    "-g": ["/Z7"],
    "-fPIC": [],
    "-fdiagnostics-color": [],
    "-fsecurity=1": [],
    "-fsecurity=2": [],
    "-fsecurity": []
}


class CompilerMSVC(Compiler):
    type: T.ClassVar = "msvc"
    obj_extension: T.ClassVar = ".obj"
    translation_dict: T.ClassVar = _powermake_flags_to_msvc_flags

    def __init__(self, path: str = "cl") -> None:
        super().__init__(path)

    def format_args(self, defines: T.List[str], includedirs: T.List[str], flags: T.List[str] = []) -> T.List[str]:
        return [f"/D{define}" for define in defines] + [f"/I{includedir}" for includedir in includedirs] + self.translate_flags(flags)

    def basic_compile_command(self, outputfile: str, inputfile: str, args: T.List[str] = []) -> T.List[str]:
        return [self.path, "/c", "/nologo", "/Fo" + outputfile, inputfile, *args]

    def check_if_arg_exists(self, arg: str) -> bool:
        return subprocess.run([self.path, arg, "/E", "/options:strict", get_empty_file()], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL).returncode == 0

class CompilerClang_CL(CompilerMSVC):
    type: T.ClassVar = "clang-cl"

    def __init__(self, path: str = "clang-cl") -> None:
        super().__init__(path)
