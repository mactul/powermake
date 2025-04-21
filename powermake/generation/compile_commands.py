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

import os
import json
import typing as T

from ..config import Config
from . import _makefile_targets


def generate_compile_commands(config: Config) -> None:
    if config.compile_commands_dir is None:
        return
    json_commands = []
    cwd = os.getcwd()
    for operations in _makefile_targets:
        # operations = [(phony, target, dependencies, command, tool), ]
        for operation in operations:
            phony, target, dependencies, command, tool = operation

            json_command = {
                "directory": cwd,
                "arguments": command,
            }
            if not phony:
                json_command["output"] = target

            deps = list(dependencies)
            if len(deps) > 0:
                json_command["file"] = deps[0]

            json_commands.append(json_command)

    with open(os.path.join(config.compile_commands_dir, "compile_commands.json"), "w") as fd:
        json.dump(json_commands, fd, indent=4)
