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

from .common import SharedLinker
from .gnu import SharedLinkerGNU, SharedLinkerGCC, SharedLinkerClang, SharedLinkerGPlusPlus, SharedLinkerClangPlusPlus, SharedLinkerLD, SharedLinkerMinGW, SharedLinkerMinGWPlusPlus, SharedLinkerMinGWLD
from .msvc import SharedLinkerMSVC, SharedLinkerClang_CL


_shared_linker_types: T.Dict[str, T.Callable[[], SharedLinker]] = {
    "default": SharedLinkerGNU,
    "gnu": SharedLinkerGNU,
    "gcc": SharedLinkerGCC,
    "g++": SharedLinkerGPlusPlus,
    "clang": SharedLinkerClang,
    "clang++": SharedLinkerClangPlusPlus,
    "msvc": SharedLinkerMSVC,
    "clang-cl": SharedLinkerClang_CL,
    "ld": SharedLinkerLD,
    "mingw": SharedLinkerMinGW,
    "mingw++": SharedLinkerMinGWPlusPlus,
    "mingw-ld": SharedLinkerMinGWLD
}


def GenericSharedLinker(shared_linker_type: str) -> T.Union[T.Callable[[], SharedLinker], None]:
    if shared_linker_type not in _shared_linker_types:
        return None
    return _shared_linker_types[shared_linker_type]


def get_all_shared_linker_types() -> T.Set[str]:
    return set(_shared_linker_types.keys())
