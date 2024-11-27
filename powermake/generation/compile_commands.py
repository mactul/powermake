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
