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


import abc

from .tools import Tool


class Linker(Tool, abc.ABC):
    exe_extension = None

    def __init__(self, path):
        Tool.__init__(self, path)

    @abc.abstractmethod
    def basic_link_command(self, outputfile: str, objectfiles: set[str], archives: list[str] = [], args: list[str] = []) -> list[str]:
        return []


class LinkerGNU(Linker):
    type = "gnu"
    exe_extension = ""

    def __init__(self, path: str = "cc"):
        super().__init__(path)

    def basic_link_command(self, outputfile: str, objectfiles: set[str], archives: list[str] = [], args: list[str] = []) -> list[str]:
        return [self.path, "-o", outputfile, *objectfiles, *archives, *args]


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

    def __init__(self, path: str = "clang"):
        super().__init__(path)


class LinkerClangPlusPlus(LinkerGNU):
    type = "clang++"

    def __init__(self, path: str = "clang++"):
        super().__init__(path)


class LinkerMSVC(Linker):
    type = "msvc"
    exe_extension = ".exe"

    def __init__(self, path: str = "link"):
        super().__init__(path)

    def basic_link_command(self, outputfile: str, objectfiles: set[str], archives: list[str] = [], args: list[str] = []) -> list[str]:
        return [self.path, "/nologo", *args, "/out:" + outputfile, *objectfiles, *archives]


_linker_types: dict[str, Linker] = {
    "gnu": LinkerGNU,
    "gcc": LinkerGCC,
    "g++": LinkerGPlusPlus,
    "clang": LinkerClang,
    "clang++": LinkerClangPlusPlus,
    "msvc": LinkerMSVC
}


def GenericLinker(linker_type: str) -> Linker:
    if linker_type not in _linker_types:
        return None
    return _linker_types[linker_type]


def get_all_linker_types() -> list[str]:
    return _linker_types.keys()
