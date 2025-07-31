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

from .common import Archiver


class ArchiverGNU(Archiver):
    type: T.ClassVar = "gnu"
    static_lib_extension: T.ClassVar = ".a"

    def __init__(self, path: str = "ar"):
        super().__init__(path)

    def basic_archive_command(self, outputfile: str, inputfiles: T.Iterable[str], args: T.List[T.Union[str, T.Tuple[str, ...]]] = []) -> T.List[str]:
        flatten_args: T.List[str] = []
        for arg in args:
            if isinstance(arg, tuple):
                flatten_args.extend(arg)
            else:
                flatten_args.append(arg)
        return [self.path, "-cr", *flatten_args, outputfile, *inputfiles]

    def check_if_arg_exists(self, arg: T.Union[str, T.Tuple[str, ...]]) -> bool:
        if isinstance(arg, tuple):
            return subprocess.run([self.path, *arg, "-h"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL).returncode == 0
        else:
            return subprocess.run([self.path, arg, "-h"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL).returncode == 0


class ArchiverAR(ArchiverGNU):
    type: T.ClassVar = "ar"

    def __init__(self, path: str = "ar"):
        super().__init__(path)


class ArchiverLLVM_AR(ArchiverGNU):
    type: T.ClassVar = "llvm-ar"

    def __init__(self, path: str = "llvm-ar"):
        super().__init__(path)


class ArchiverMinGW(ArchiverGNU):
    type: T.ClassVar = "mingw"

    def __init__(self, path: str = "x86_64-w64-mingw32-gcc-ar"):
        super().__init__(path)