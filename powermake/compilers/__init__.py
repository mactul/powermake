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
from .asm import CompilerNASM
from .rc import CompilerWindRes
from .msvc import CompilerMSVC, CompilerClang_CL
from .gnu import CompilerGNU, CompilerGNUPlusPlus, CompilerGCC, CompilerGPlusPlus, CompilerClang, CompilerClangPlusPlus, CompilerMinGW, CompilerMinGWPlusPlus


_c_compiler_types: T.Dict[str, T.Callable[[], Compiler]] = {
    "gnu": CompilerGNU,
    "gcc": CompilerGCC,
    "clang": CompilerClang,
    "msvc": CompilerMSVC,
    "clang-cl": CompilerClang_CL,
    "mingw": CompilerMinGW
}

_cpp_compiler_types: T.Dict[str, T.Callable[[], Compiler]] = {
    "gnu++": CompilerGNUPlusPlus,
    "g++": CompilerGPlusPlus,
    "clang++": CompilerClangPlusPlus,
    "msvc": CompilerMSVC,
    "clang-cl": CompilerClang_CL,
    "mingw++": CompilerMinGWPlusPlus
}


_as_compiler_types: T.Dict[str, T.Callable[[], Compiler]] = {
    "gnu": CompilerGNU,
    "gcc": CompilerGCC,
    "clang": CompilerClang,
    "mingw": CompilerMinGW
}

_asm_compiler_types: T.Dict[str, T.Callable[[], Compiler]] = {
    "nasm": CompilerNASM
}


_rc_compiler_types: T.Dict[str, T.Callable[[], Compiler]] = {
    "windres": CompilerWindRes
}


_compiler_types: T.Dict[str, T.Callable[[], Compiler]] = {
    "default": CompilerGNU,
    **_c_compiler_types,
    **_cpp_compiler_types,
    **_as_compiler_types,
    **_asm_compiler_types,
    **_rc_compiler_types
}


def GenericCompiler(compiler_type: str) -> T.Union[T.Callable[[], Compiler], None]:
    if compiler_type not in _compiler_types:
        return None
    return _compiler_types[compiler_type]


def get_all_compiler_types() -> T.Set[str]:
    return set(_compiler_types.keys())


def get_all_c_compiler_types() -> T.Set[str]:
    return set(_c_compiler_types.keys())


def get_all_cpp_compiler_types() -> T.Set[str]:
    return set(_cpp_compiler_types.keys())


def get_all_as_compiler_types() -> T.Set[str]:
    return set(_as_compiler_types.keys())


def get_all_asm_compiler_types() -> T.Set[str]:
    return set(_asm_compiler_types.keys())

def get_all_rc_compiler_types() -> T.Set[str]:
    return set(_rc_compiler_types.keys())
