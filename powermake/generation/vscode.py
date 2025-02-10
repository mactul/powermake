import os
import sys
import json
import __main__ as __makefile__

from .. import Config
from ..utils import makedirs

def generate_vscode(config: Config, vscode_path: str) -> None:
    debug = config.debug
    config.set_debug(True)
    makedirs(vscode_path)
    with open(os.path.join(vscode_path, "launch.json"), "w") as file:
        file.write("""{
    "configurations": [
        {
            "name": "PowerMake Debug",
            "type": "cppdbg",
            "preLaunchTask": "powermake_compile",
            "request": "launch",
            "program": %s,
            "args": [],
            "cwd": "${workspaceFolder}"
        },
        {
            "name": "Python Debug",
            "type": "debugpy",
            "request": "launch",
            "program": "${file}",
            "args": [],
            "justMyCode": false
        }
    ]
}
""" % (json.dumps(os.path.abspath(os.path.join(config.exe_build_directory, config.target_name))), ))

    with open(os.path.join(vscode_path, "tasks.json"), "w") as file:
        file.write("""{
    "tasks": [
        {
            "type": "cppbuild",  /* The cppbuild type will tell the C/C++ extension to parse the stderr output of this command to put errors and warnings in the "problems" tab. */
            "label": "powermake_compile",  /* identifies the task in the launch.json file */
            "command": %s,  /* This is the command executed, under Windows it will be "py", under debian 10 it will be "python3". */
            "args": [
                %s,
                "-d",  /* We activate the debug code */
                "-o",  /* This option tells powermake to generate a compile_commands.json in the .vscode folder. */
                %s,
                "--retransmit-colors"  /* If the type at the top had been “shell” instead of cppbuild we wouldn't have needed this, but now powermake and GCC detect that they're being executed by a program that parses their output and by default disable color formatting codes. */
            ],
            "options": {
                "cwd": "${workspaceFolder}"
            }
        },
        {
            /* This task should be mapped to a key, like F6 for example */
            "type": "cppbuild",
            "label": "powermake_compile_single_file",
            "command": %s,
            "args": [
                %s,
                "-rd",
                "--single-file",  /* We only compile the current file */
                "${file}",
                "--retransmit-colors"
            ],
            "options": {
                "cwd": "${workspaceFolder}",
            }
        }
    ],
    "version": "2.0.0"
}
""" % (json.dumps(sys.executable), json.dumps(os.path.realpath(__makefile__.__file__)), json.dumps(vscode_path), json.dumps(sys.executable), json.dumps(os.path.realpath(__makefile__.__file__))))
    config.set_debug(debug)