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

import subprocess
import typing as T

from .common import Compiler
from ..utils import get_empty_file


_powermake_flags_to_gnu_flags: T.Dict[str, T.List[str]] = {
    "-Wsecurity": ["-Wall", "-Wextra", "-fanalyzer", "-Wformat", "-Wconversion", "-Wsign-conversion", "-Wtrampolines", "-Wbidi-chars=any,ucn"],
    "-fsecurity=1": ["-Wsecurity", "-fstrict-flex-arrays=2", "-fcf-protection=full", "-mbranch-protection=standard", "-Wl,-z,nodlopen", "-Wl,-z,noexecstack", "-Wl,-z,relro", "-fPIE", "-pie", "-fPIC", "-shared", "-fno-delete-null-pointer-checks", "-fno-strict-overflow", "-fno-strict-aliasing", "-fexceptions", "-Wl,--as-needed", "-Wl,--no-copy-dt-needed-entries"],
    "-fsecurity=2": ["-fsecurity=1", "-D_FORTIFY_SOURCE=3", "-D_GLIBCXX_ASSERTIONS", "-fstack-clash-protection", "-fstack-protector-strong", "-Wl,-z,now", "-ftrivial-auto-var-init=zero"],
    "-fsecurity": ["-fsecurity=2"],
    "-Weverything": ["-Weverything", "-Wsecurity"],
    "-ffuzzer": ["-fsanitize=address,fuzzer"],
}


class CompilerGNU(Compiler):
    type: T.ClassVar = "gnu"
    obj_extension: T.ClassVar = ".o"
    translation_dict = _powermake_flags_to_gnu_flags

    def __init__(self, path: str = "cc"):
        super().__init__(path)

    def format_args(self, defines: T.List[str], includedirs: T.List[str], flags: T.List[str] = []) -> T.List[str]:
        return [f"-D{define}" for define in defines] + [f"-I{includedir}" for includedir in includedirs] + self.translate_flags(flags)

    def basic_compile_command(self, outputfile: str, inputfile: str, args: T.List[str] = []) -> T.List[str]:
        return [self.path, "-c", "-o", outputfile, inputfile, *args]

    def check_if_arg_exists(self, arg: str) -> bool:
        return subprocess.run([self.path, arg, "-E", "-x", "c", get_empty_file()], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL).returncode == 0


class CompilerGNUPlusPLus(CompilerGNU):
    type: T.ClassVar = "gnu++"

    def __init__(self, path: str = "c++"):
        super().__init__(path)

    def check_if_arg_exists(self, arg: str) -> bool:
        return subprocess.run([self.path, arg, "-E", "-x", "c++", get_empty_file()], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL).returncode == 0


class CompilerGCC(CompilerGNU):
    type: T.ClassVar = "gcc"

    def __init__(self, path: str = "gcc"):
        super().__init__(path)


class CompilerGPlusPlus(CompilerGNUPlusPLus):
    type: T.ClassVar = "g++"

    def __init__(self, path: str = "g++"):
        super().__init__(path)


class CompilerClang(CompilerGNU):
    type: T.ClassVar = "clang"

    def __init__(self, path: str = "clang"):
        super().__init__(path)


class CompilerClangPlusPlus(CompilerGNUPlusPLus):
    type: T.ClassVar = "clang++"

    def __init__(self, path: str = "clang++"):
        super().__init__(path)
