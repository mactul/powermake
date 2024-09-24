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

from ..tools import translate_flags
from .common import SharedLinker

_powermake_flags_to_gnu_flags: T.Dict[str, T.List[str]] = {
    "-ffuzzer": []
}

_powermake_flags_to_clang_flags: T.Dict[str, T.List[str]] = {
    "-ffuzzer": ["-fsanitize=address,fuzzer"]
}


class SharedLinkerGNU(SharedLinker):
    type: T.ClassVar = "gnu"
    shared_lib_extension: T.ClassVar = ".so"
    translation_dict: T.ClassVar = _powermake_flags_to_gnu_flags

    def __init__(self, path: str = "cc"):
        super().__init__(path)

    @classmethod
    def format_args(self, shared_libs: T.List[str], flags: T.List[str]) -> T.List[str]:
        return ["-l" + lib for lib in shared_libs] + translate_flags(flags, self.translation_dict)

    def basic_link_command(self, outputfile: str, objectfiles: T.Iterable[str], archives: T.List[str] = [], args: T.List[str] = []) -> T.List[str]:
        return [self.path, "-shared", "-o", outputfile, *objectfiles, *archives, *args]


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
    translation_dict: T.ClassVar = _powermake_flags_to_clang_flags

    def __init__(self, path: str = "clang"):
        super().__init__(path)


class SharedLinkerClangPlusPlus(SharedLinkerGNU):
    type: T.ClassVar = "clang++"
    translation_dict: T.ClassVar = _powermake_flags_to_clang_flags

    def __init__(self, path: str = "clang++"):
        super().__init__(path)
