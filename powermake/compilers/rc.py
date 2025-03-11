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

import typing as T

from .common import Compiler


class CompilerWindRes(Compiler):
    type: T.ClassVar = "windres"
    obj_extension: T.ClassVar = ".res"

    def __init__(self, path: T.Union[str, T.List[str]] = ["x86_64-w64-mingw32-windres", "windres"]):
        super().__init__(path)

    def format_args(self, defines: T.List[str], includedirs: T.List[str], flags: T.List[str] = []) -> T.List[str]:
        return [f"-D{define}" for define in defines] + [f"-I{includedir}" for includedir in includedirs] + flags

    def basic_compile_command(self, outputfile: str, inputfile: str, args: T.List[str] = []) -> T.List[str]:
        return [self.path, inputfile, "-O", "coff", "-o", outputfile, *args]

    def check_if_arg_exists(self, arg: str) -> bool:
        return False
