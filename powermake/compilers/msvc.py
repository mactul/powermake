# Copyright 2024 Macéo Tuloup

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from .common import Compiler
from ..tools import translate_flags


_powermake_warning_flags_to_msvc_flags = {
    "-w": ["/W0"],
    "-Wall": ["/W3"],
    "-Wextra": ["/W4"],
    "-Weverything": ["/Wall"],
    "-Werror": ["/WX"],
    "-Wpedantic": [],
    "-Wswitch": ["/we4062"],
    "-Wswitch-enum": ["/we4061"],
    "-fanalyzer": ["/analyze"],
    "-ffuzzer": ["/fsanitize=address,fuzzer"]
}

_powermake_optimization_flags_to_msvc_flags = {
    "-O0": ["/Od"],
    "-Og": ["/Od"],
    "-O1": ["/O1"],
    "-O2": ["/O2"],
    "-O3": ["/Ox", "/fp:fast"],
    "-Os": ["/O1", "/GL"],
    "-Oz": ["/O1", "/Oi", "/GL"],
    "-Ofast": ["/Ox", "/fp:fast"],
    "-fomit-frame-pointer": ["/Oy"],
}

_powermake_machine_flags_to_msvc_flags = {
    "-m32": [],
    "-m64": [],
    "-mmmx": ["/arch:MMX"],
    "-msse": ["/arch:SSE"],
    "-msse2": ["/arch:SSE2"],
    "-mssse3": ["/arch:SSSE3"],
    "-mavx": ["/arch:AVX"],
    "-mavx2": ["/arch:AVX2"]
}

_powermake_flags_to_msvc_flags = {
    **_powermake_warning_flags_to_msvc_flags,
    **_powermake_optimization_flags_to_msvc_flags,
    **_powermake_machine_flags_to_msvc_flags,
    "-g": ["/Z7"]
}


class CompilerMSVC(Compiler):
    type = "msvc"
    obj_extension = ".obj"
    translation_dict = _powermake_flags_to_msvc_flags

    def __init__(self, path: str = "cl"):
        super().__init__(path)

    @classmethod
    def format_args(self, defines: list, includedirs: list, flags: list = []):
        return [f"/D{define}" for define in defines] + [f"/I{includedir}" for includedir in includedirs] + translate_flags(flags, self.translation_dict)

    def basic_compile_command(self, outputfile: str, inputfile: str, args: list = []) -> list:
        return [self.path, "/c", "/nologo", "/Fo" + outputfile, inputfile, *args]


class CompilerClang_CL(CompilerMSVC):
    type = "clang-cl"

    def __init__(self, path: str = "clang-cl"):
        super().__init__(path)
