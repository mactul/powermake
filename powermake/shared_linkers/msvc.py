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

from ..tools import translate_flags
from .common import SharedLinker

_powermake_flags_to_msvc_flags: T.Dict[str, T.List[str]] = {
    "-m32": [],
    "-m64": [],
    "-ffuzzer": ["/fsanitize=address,fuzzer"]
}


class SharedLinkerMSVC(SharedLinker):
    type: T.ClassVar = "msvc"
    shared_lib_extension: T.ClassVar = ".dll"
    translation_dict: T.ClassVar = _powermake_flags_to_msvc_flags

    def __init__(self, path: str = "link") -> None:
        super().__init__(path)

    @classmethod
    def format_args(self, shared_libs: T.List[str], flags: T.List[str]) -> T.List[str]:
        return [(lib if lib.endswith(".lib") else lib + ".lib") for lib in shared_libs] + translate_flags(flags, self.translation_dict)

    def basic_link_command(self, outputfile: str, objectfiles: T.Iterable[str], archives: T.List[str] = [], args: T.List[str] = []) -> T.List[str]:
        return [self.path, "/DLL", "/nologo", *args, "/out:" + outputfile, *objectfiles, *archives]
    
    def check_if_arg_exists(self, empty_file: str, arg: str) -> bool:
        return subprocess.run([self.path, "/WX", arg], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL).returncode != 4044


class SharedLinkerClang_CL(SharedLinkerMSVC):
    type = "clang-cl"

    def __init__(self, path: str = "clang-cl") -> None:
        super().__init__(path)
