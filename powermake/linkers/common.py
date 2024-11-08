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
import typing as T

from ..tools import Tool


class Linker(Tool, abc.ABC):
    def __init__(self, path: str) -> None:
        Tool.__init__(self, path)

    @abc.abstractmethod
    def format_args(self, shared_libs: T.List[str], flags: T.List[str]) -> T.List[str]:
        return []

    @abc.abstractmethod
    def basic_link_command(self, outputfile: str, objectfiles: T.Iterable[str], archives: T.List[str] = [], args: T.List[str] = []) -> T.List[str]:
        return []
