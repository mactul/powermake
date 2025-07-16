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


_powermake_warning_flags_to_nasm_flags: T.Dict[str, T.List[str]] = {
    "-Wextra": ["-Wall"],
    "-Weverything": ["-Wall"],
    "-Wsecurity": ["-Wall"],
    "-Wpedantic": [],
    "-pedantic": [],
    "-Wswitch": [],
    "-Wswitch-enum": [],
    "-fanalyzer": ["-Wall"],
    "-ffuzzer": []
}

_powermake_optimization_flags_to_nasm_flags: T.Dict[str, T.List[str]] = {
    "-Og": ["-O1"],
    "-O2": ["-Ox"],
    "-O3": ["-Ox"],
    "-Os": ["-Ox"],
    "-Oz": ["-Ox"],
    "-Ofast": ["-Ox"],
    "-fomit-frame-pointer": [],
}

_powermake_machine_flags_to_nasm_flags: T.Dict[str, T.List[str]] = {
    "-m32": ["-felf32"],
    "-m64": ["-felf64"],
    "-mmmx": [],
    "-msse": [],
    "-msse2": [],
    "-mssse3": [],
    "-mavx": [],
    "-mavx2": []
}

# These flags doesn't inherit from tools._powermake_flags_to_gnu_flags because 
_powermake_flags_to_nasm_flags: T.Dict[str, T.List[str]] = {
    **_powermake_warning_flags_to_nasm_flags,
    **_powermake_optimization_flags_to_nasm_flags,
    **_powermake_machine_flags_to_nasm_flags,
    "-fdiagnostics-color": [],
    "-fsecurity=1": [],
    "-fsecurity=2": [],
    "-fsecurity": []
}


_powermake_warning_flags_to_masm_flags: T.Dict[str, T.List[str]] = {
    "-w": ["/W0"],
    "-Wall": ["/W2"],
    "-Wextra": ["/W3"],
    "-Weverything": ["/W3"],
    "-Wsecurity": ["/W3"],
    "-Werror": ["/WX"],
    "-Wpedantic": [],
    "-pedantic": [],
    "-fanalyzer": [],
    "-ffuzzer": []
}

_powermake_optimization_flags_to_masm_flags: T.Dict[str, T.List[str]] = {
    "-O0": [],
    "-Og": [],
    "-O": [],
    "-O1": [],
    "-O2": [],
    "-O3": [],
    "-Os": [],
    "-Oz": [],
    "-Ofast": [],
    "-fomit-frame-pointer": [],
}

_powermake_machine_flags_to_masm_flags: T.Dict[str, T.List[str]] = {
    "-m32": [],
    "-m64": [],
    "-fwin32": [],
    "-fwin64": [],
    "-felf32": [],
    "-felf64": [],
    "-fmacho32": [],
    "-fmacho64": [],
    "-march=native": [],
    "-mtune=native": [],
    "-mmmx": [],
    "-msse": [],
    "-msse2": [],
    "-msse3": [],
    "-mavx": [],
    "-mavx2": []
}

_powermake_flags_to_masm_flags: T.Dict[str, T.List[str]] = {
    **_powermake_warning_flags_to_masm_flags,
    **_powermake_optimization_flags_to_masm_flags,
    **_powermake_machine_flags_to_masm_flags,
    "-g": ["/Zf"],
    "-fPIC": [],
    "-fdiagnostics-color": [],
    "-fsecurity=1": [],
    "-fsecurity=2": [],
    "-fsecurity": []
}


class CompilerNASM(Compiler):
    type: T.ClassVar = "nasm"
    obj_extension: T.ClassVar = ".o"

    def __init__(self, path: str = "nasm"):
        super().__init__(path, _powermake_flags_to_nasm_flags)

    def format_args(self, defines: T.List[str], includedirs: T.List[str], flags: T.List[str] = []) -> T.List[str]:
        return [f"-d{define}" for define in defines] + [f"-i{includedir}" for includedir in includedirs] + self.translate_flags(flags)

    def basic_compile_command(self, outputfile: str, inputfile: str, args: T.List[str] = []) -> T.List[str]:
        return [self.path, "-o", outputfile, inputfile, *args]

    def check_if_arg_exists(self, arg: str) -> bool:
        return subprocess.run([self.path, arg, get_empty_file(), "-e"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL).returncode == 0

class CompilerMASM(Compiler):
    type: T.ClassVar = "masm"
    obj_extension: T.ClassVar = ".obj"

    def __init__(self, path: str = "ml64"):
        super().__init__(path, _powermake_flags_to_masm_flags)

    def format_args(self, defines: T.List[str], includedirs: T.List[str], flags: T.List[str] = []) -> T.List[str]:
        return [f"/D{define}" for define in defines] + [f"/I{includedir}" for includedir in includedirs] + self.translate_flags(flags)

    def basic_compile_command(self, outputfile: str, inputfile: str, args: T.List[str] = []) -> T.List[str]:
        return [self.path, "/c", "/nologo", "/Fo" + outputfile, inputfile, *args]

    def check_if_arg_exists(self, arg: str) -> bool:
        try:
            return b"A4018:invalid command-line option" not in subprocess.check_output([self.path, "/nologo", arg, "/help"], shell=True, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            return False