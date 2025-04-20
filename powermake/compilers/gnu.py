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


class CompilerGNU(Compiler):
    type: T.ClassVar = "gnu"
    obj_extension: T.ClassVar = ".o"

    def __init__(self, path: str = "cc"):
        super().__init__(path)

    def format_args(self, defines: T.List[str], includedirs: T.List[str], flags: T.List[str] = []) -> T.List[str]:
        return [f"-D{define}" for define in defines] + [f"-I{includedir}" for includedir in includedirs] + self.translate_flags(flags)

    def basic_compile_command(self, outputfile: str, inputfile: str, args: T.List[str] = []) -> T.List[str]:
        return [self.path, "-c", "-o", outputfile, inputfile, *args]

    def check_if_arg_exists(self, arg: str) -> bool:
        return subprocess.run([self.path, arg, "-E", "-x", "c", get_empty_file()], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL).returncode == 0


class CompilerGNUPlusPlus(CompilerGNU):
    type: T.ClassVar = "gnu++"

    def __init__(self, path: str = "c++"):
        super().__init__(path)
        not_supported = {'-Wjump-misses-init', '-Wmissing-prototypes', '-Wmissing-variable-declarations', '-Wnested-externs', '-Wstrict-prototypes', '-Wunsuffixed-float-constants'}
        self.translation_dict["-Weverything"] = list(filter(lambda x: x not in not_supported, self.translation_dict["-Weverything"]))

    def check_if_arg_exists(self, arg: str) -> bool:
        return subprocess.run([self.path, arg, "-E", "-x", "c++", get_empty_file()], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL).returncode == 0


class CompilerGCC(CompilerGNU):
    type: T.ClassVar = "gcc"

    def __init__(self, path: str = "gcc"):
        super().__init__(path)


class CompilerGPlusPlus(CompilerGNUPlusPlus):
    type: T.ClassVar = "g++"

    def __init__(self, path: str = "g++"):
        super().__init__(path)


class CompilerMinGW(CompilerGNU):
    type: T.ClassVar = "mingw"

    def __init__(self, path: str = "x86_64-w64-mingw32-gcc"):
        super().__init__(path)


class CompilerMinGWPlusPlus(CompilerGNUPlusPlus):
    type: T.ClassVar = "mingw++"

    def __init__(self, path: str = "x86_64-w64-mingw32-g++"):
        super().__init__(path)


class CompilerClang(CompilerGNU):
    type: T.ClassVar = "clang"

    def __init__(self, path: str = "clang"):
        super().__init__(path)

    def check_if_arg_exists(self, arg: str) -> bool:
        return subprocess.run([self.path, arg, "-Werror=unknown-warning-option", "-Werror=unused-command-line-argument", "-E", "-x", "c", get_empty_file()], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL).returncode == 0


class CompilerClangPlusPlus(CompilerGNUPlusPlus):
    type: T.ClassVar = "clang++"

    def __init__(self, path: str = "clang++"):
        super().__init__(path)

    def check_if_arg_exists(self, arg: str) -> bool:
        return subprocess.run([self.path, arg, "-Werror=unknown-warning-option", "-Werror=unused-command-line-argument", "-E", "-x", "c++", get_empty_file()], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL).returncode == 0