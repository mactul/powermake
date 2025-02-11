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
from threading import Lock

_makefile_targets_mutex = Lock()
_makefile_targets: T.List[T.List[T.Tuple[bool, str, T.Iterable[str], T.Union[str, T.List[str]], str]]] = [] # [[(phony, target, dependencies, command, tool), ], ]
