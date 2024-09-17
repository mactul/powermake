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

from ..tools import translate_flags
from .common import Linker

_powermake_flags_to_gnu_flags = {
    "-ffuzzer": [],
    "-Weverything": ["-Wall", "-Wextra"],
}

_powermake_flags_to_clang_flags = {
    "-ffuzzer": ["-fsanitize=address,fuzzer"]
}

_powermake_flags_to_ld_flags = {
    "-ffuzzer": [],
    "-Weverything": [],
    "-Wall": [],
    "-Wextra": [],
    "-m32": [],
    "-m64": []
}


class LinkerGNU(Linker):
    type = "gnu"
    exe_extension = ""
    translation_dict = _powermake_flags_to_gnu_flags

    def __init__(self, path: str = "cc"):
        super().__init__(path)

    @classmethod
    def format_args(self, shared_libs: list, flags: list):
        return ["-l"+lib for lib in shared_libs] + translate_flags(flags, self.translation_dict)

    def basic_link_command(self, outputfile: str, objectfiles: set, archives: list = [], args: list = []) -> list:
        return [self.path, "-o", outputfile, *objectfiles, *archives, *args]


class LinkerLD(LinkerGNU):
    type = "ld"
    translation_dict = _powermake_flags_to_ld_flags

    def __init__(self, path: str = "ld"):
        super().__init__(path)


class LinkerGCC(LinkerGNU):
    type = "gcc"

    def __init__(self, path: str = "gcc"):
        super().__init__(path)


class LinkerGPlusPlus(LinkerGNU):
    type = "g++"

    def __init__(self, path: str = "g++"):
        super().__init__(path)


class LinkerClang(LinkerGNU):
    type = "clang"
    translation_dict = _powermake_flags_to_clang_flags

    def __init__(self, path: str = "clang"):
        super().__init__(path)


class LinkerClangPlusPlus(LinkerGNU):
    type = "clang++"
    translation_dict = _powermake_flags_to_clang_flags

    def __init__(self, path: str = "clang++"):
        super().__init__(path)
