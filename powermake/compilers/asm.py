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


_powermake_warning_flags_to_nasm_flags = {
    "-Wextra": ["-Wall"],
    "-Weverything": ["-Wall"],
    "-Wpedantic": [],
    "-Wswitch": [],
    "-Wswitch-enum": [],
    "-fanalyzer": ["-Wall"],
    "-ffuzzer": []
}

_powermake_optimization_flags_to_nasm_flags = {
    "-Og": ["-O1"],
    "-O2": ["-Ox"],
    "-O3": ["-Ox"],
    "-Os": ["-Ox"],
    "-Oz": ["-Ox"],
    "-Ofast": ["-Ox"],
    "-fomit-frame-pointer": [],
}

_powermake_machine_flags_to_nasm_flags = {
    "-m32": ["-felf32"],
    "-m64": ["-felf64"],
    "-mmmx": [],
    "-msse": [],
    "-msse2": [],
    "-mssse3": [],
    "-mavx": [],
    "-mavx2": []
}

_powermake_flags_to_nasm_flags = {
    **_powermake_warning_flags_to_nasm_flags,
    **_powermake_optimization_flags_to_nasm_flags,
    **_powermake_machine_flags_to_nasm_flags,
}


class CompilerNASM(Compiler):
    type = "nasm"
    obj_extension = ".o"
    translation_dict = _powermake_flags_to_nasm_flags

    def __init__(self, path: str = "nasm"):
        super().__init__(path)

    @classmethod
    def format_args(self, defines: list, includedirs: list, flags: list = []):
        return [f"-d{define}" for define in defines] + [f"-i{includedir}" for includedir in includedirs] + translate_flags(flags, self.translation_dict)

    def basic_compile_command(self, outputfile: str, inputfile: str, args: list = []) -> list:
        return [self.path, "-o", outputfile, inputfile, *args]
