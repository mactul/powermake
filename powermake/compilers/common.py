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

from ..tools import Tool


class Compiler(Tool, abc.ABC):
    type = None
    obj_extension = None

    def __init__(self, path):
        Tool.__init__(self, path)

    @classmethod
    @abc.abstractmethod
    def format_args(self, defines: list[str], includedirs: list[str], flags: list[str] = []):
        return []

    @abc.abstractmethod
    def basic_compile_command(self, outputfile: str, inputfile: str, args: list[str] = []) -> list[str]:
        return []