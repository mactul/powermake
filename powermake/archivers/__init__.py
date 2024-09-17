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


from .common import Archiver
from .gnu import ArchiverGNU, ArchiverAR, ArchiverLLVM_AR
from .msvc import ArchiverMSVC


_archiver_types: dict = {
    "gnu": ArchiverGNU,
    "ar": ArchiverAR,
    "llvm-ar": ArchiverLLVM_AR,
    "msvc": ArchiverMSVC
}


def GenericArchiver(archiver_type: str) -> Archiver:
    if archiver_type not in _archiver_types:
        return None
    return _archiver_types[archiver_type]


def get_all_archiver_types() -> set:
    return _archiver_types.keys()
