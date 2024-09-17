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


class ArchiverGNU(Archiver):
    type = "gnu"
    static_lib_extension = ".a"

    def __init__(self, path: str = "ar"):
        super().__init__(path)

    def basic_archive_command(self, outputfile: str, inputfiles: set, args: list = []) -> list:
        return [self.path, "-cr", outputfile, *inputfiles, *args]


class ArchiverAR(ArchiverGNU):
    type = "ar"

    def __init__(self, path: str = "ar"):
        super().__init__(path)


class ArchiverLLVM_AR(ArchiverGNU):
    type = "llvm-ar"

    def __init__(self, path: str = "llvm-ar"):
        super().__init__(path)
