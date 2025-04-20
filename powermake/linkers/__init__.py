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

from .common import Linker
from .gnu import LinkerGNU, LinkerLD, LinkerGCC, LinkerClang, LinkerGPlusPlus, LinkerClangPlusPlus, LinkerMinGW, LinkerMinGWPlusPlus, LinkerMinGWLD
from .msvc import LinkerMSVC, LinkerClang_CL


_linker_types: T.Dict[str, T.Callable[[], Linker]] = {
    "default": LinkerGNU,
    "gnu": LinkerGNU,
    "ld": LinkerLD,
    "gcc": LinkerGCC,
    "g++": LinkerGPlusPlus,
    "clang": LinkerClang,
    "clang++": LinkerClangPlusPlus,
    "msvc": LinkerMSVC,
    "clang-cl": LinkerClang_CL,
    "mingw": LinkerMinGW,
    "mingw++": LinkerMinGWPlusPlus,
    "mingw-ld": LinkerMinGWLD
}


def GenericLinker(linker_type: str) -> T.Union[T.Callable[[], Linker], None]:
    if linker_type not in _linker_types:
        return None
    return _linker_types[linker_type]


def get_all_linker_types() -> T.Set[str]:
    return set(_linker_types.keys())
