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

from .common import Compiler
from .msvc import CompilerMSVC, CompilerClang_CL
from .gnu import CompilerGNU, CompilerGCC, CompilerGPlusPlus, CompilerClang, CompilerClangPlusPlus


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
