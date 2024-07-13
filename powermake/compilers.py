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


class Compiler(Tool, abc.ABC):
    type = None
    obj_extension = None

    def __init__(self, path):
        Tool.__init__(self, path)

    @classmethod
    @abc.abstractmethod
    def format_args(defines: list[str], includedirs: list[str], flags: list[str] = []):
        return []

    @abc.abstractmethod
    def basic_compile_command(self, outputfile: str, inputfile: str, args: list[str] = []) -> list[str]:
        return []


class CompilerGNU(Compiler):
    type = "gnu"
    obj_extension = ".o"

    def __init__(self, path: str = "cc"):
        super().__init__(path)

    @classmethod
    def format_args(self, defines: list[str], includedirs: list[str], flags: list[str] = []):
        return [f"-D{define}" for define in defines] + [f"-I{includedir}" for includedir in includedirs] + flags

    def basic_compile_command(self, outputfile: str, inputfile: str, args: list[str] = []) -> list[str]:
        return [self.path, "-c", "-o", outputfile, inputfile, *args]


class CompilerGCC(CompilerGNU):
    type = "gcc"

    def __init__(self, path: str = "gcc"):
        super().__init__(path)


class CompilerGPlusPlus(CompilerGNU):
    type = "g++"

    def __init__(self, path: str = "g++"):
        super().__init__(path)


class CompilerClang(CompilerGNU):
    type = "clang"

    def __init__(self, path: str = "clang"):
        super().__init__(path)


class CompilerClangPlusPlus(CompilerGNU):
    type = "clang++"

    def __init__(self, path: str = "clang++"):
        super().__init__(path)


class CompilerMSVC(Compiler):
    type = "msvc"
    obj_extension = ".obj"

    def __init__(self, path: str = "cl"):
        super().__init__(path)

    @classmethod
    def format_args(self, defines: list[str], includedirs: list[str], flags: list[str] = []):
        return [f"/D{define}" for define in defines] + [f"/I{includedir}" for includedir in includedirs] + flags

    def basic_compile_command(self, outputfile: str, inputfile: str, args: list[str] = []) -> list[str]:
        return [self.path, "/c", "/nologo", "/Fo" + outputfile, inputfile, *args]


class CompilerClang_CL(CompilerMSVC):
    type = "clang-cl"

    def __init__(self, path: str = "clang-cl"):
        super().__init__(path)


_c_compiler_types: dict[str, Compiler] = {
    "gnu": CompilerGNU,
    "gcc": CompilerGCC,
    "clang": CompilerClang,
    "msvc": CompilerMSVC,
    "clang-cl": CompilerClang_CL
}

_cpp_compiler_types: dict[str, Compiler] = {
    "g++": CompilerGPlusPlus,
    "clang++": CompilerClangPlusPlus,
    "msvc": CompilerMSVC
}

_compiler_types: dict[str, Compiler] = {
    **_c_compiler_types,
    **_cpp_compiler_types
}


def GenericCompiler(compiler_type: str) -> Compiler:
    if compiler_type not in _compiler_types:
        return None
    return _compiler_types[compiler_type]


def get_all_compiler_types() -> list[str]:
    return _compiler_types.keys()


def get_all_c_compiler_types() -> list[str]:
    return _c_compiler_types.keys()


def get_all_cpp_compiler_types() -> list[str]:
    return _cpp_compiler_types.keys()
