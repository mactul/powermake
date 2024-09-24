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

import typing as T

from .common import Compiler
from ..tools import translate_flags


_powermake_flags_to_gcc_flags: T.Dict[str, T.List[str]] = {
    "-Weverything": ["-Wall", "-Wextra", "-fanalyzer"],
    "-ffuzzer": []
}

_powermake_flags_to_clang_flags: T.Dict[str, T.List[str]] = {
    "-fanalyzer": [],
    "-ffuzzer": ["-fsanitize=address,fuzzer"]
}

_powermake_flags_to_gnu_flags: T.Dict[str, T.List[str]] = {
    "-Weverything": ["-Wall", "-Wextra"],
    "-fanalyzer": [],
    "-ffuzzer": []
}


class CompilerGNU(Compiler):
    type: T.ClassVar = "gnu"
    obj_extension: T.ClassVar = ".o"
    translation_dict: T.ClassVar = _powermake_flags_to_gnu_flags

    def __init__(self, path: str = "cc"):
        super().__init__(path)

    @classmethod
    def format_args(self, defines: list, includedirs: list, flags: list = []):
        return [f"-D{define}" for define in defines] + [f"-I{includedir}" for includedir in includedirs] + translate_flags(flags, self.translation_dict)

    def basic_compile_command(self, outputfile: str, inputfile: str, args: list = []) -> list:
        return [self.path, "-c", "-o", outputfile, inputfile, *args]


class CompilerGNUPlusPLus(CompilerGNU):
    type: T.ClassVar = "gnu++"

    def __init__(self, path: str = "c++"):
        super().__init__(path)


class CompilerGCC(CompilerGNU):
    type: T.ClassVar = "gcc"
    translation_dict: T.ClassVar = _powermake_flags_to_gcc_flags

    def __init__(self, path: str = "gcc"):
        super().__init__(path)


class CompilerGPlusPlus(CompilerGNU):
    type: T.ClassVar = "g++"
    translation_dict: T.ClassVar = _powermake_flags_to_gcc_flags

    def __init__(self, path: str = "g++"):
        super().__init__(path)


class CompilerClang(CompilerGNU):
    type: T.ClassVar = "clang"
    translation_dict: T.ClassVar = _powermake_flags_to_clang_flags

    def __init__(self, path: str = "clang"):
        super().__init__(path)


class CompilerClangPlusPlus(CompilerGNU):
    type: T.ClassVar = "clang++"
    translation_dict: T.ClassVar = _powermake_flags_to_clang_flags

    def __init__(self, path: str = "clang++"):
        super().__init__(path)
