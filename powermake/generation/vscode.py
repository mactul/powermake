import os
import sys
import json
import __main__ as __makefile__

from .. import Config
from ..utils import makedirs

__default_launch = """{
    "configurations": [
        {
            "name": "PowerMake Debug",
            "type": "cppdbg",
            "preLaunchTask": "powermake_compile",
            "request": "launch",
            "program": "${powermakeProgram}",
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
"""

__default_tasks = """{
    "tasks": [
        {
            "type": "cppbuild",  /* The cppbuild type will tell the C/C++ extension to parse the stderr output of this command to put errors and warnings in the "problems" tab. */
            "label": "powermake_compile",  /* identifies the task in the launch.json file */
            "command": "${powermakePythonPath}",  /* This is the command executed, under Windows it will be "py", under debian 10 it will be "python3". */
            "args": [
                "${powermakeMakefilePath}",
                "-rvd",  /* We activate the debug code, we rebuild everything so the warnings will not disappear and we use the verbose mode so it's easy to see the flags put by PowerMake */
                "-o",  /* This option tells powermake to generate a compile_commands.json in the .vscode folder. */
                "${powermakeVscodeFolderPath}",
                "--retransmit-colors"  /* If the type at the top had been “shell” instead of cppbuild we wouldn't have needed this, but now powermake and GCC detect that they're being executed by a program that parses their output and by default disable color formatting codes. */
            ],
            "options": {
                "cwd": "${workspaceFolder}"
            }
        },
        {
            /* This task should be mapped to a key, like Ctrl+F7 for example */
            "type": "cppbuild",
            "label": "powermake_compile_single_file",
            "command": "${powermakePythonPath}",
            "args": [
                "${powermakeMakefilePath}",
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
"""

def format_json_string(js_str: str, powermake_program: str, vscode_path: str) -> str:
    js_str = js_str.replace("${powermakeProgram}", json.dumps(powermake_program)[1:-1])
    js_str = js_str.replace("${powermakePythonPath}", json.dumps(sys.executable)[1:-1])
    js_str = js_str.replace("${powermakeMakefilePath}", json.dumps(os.path.realpath(__makefile__.__file__))[1:-1])
    js_str = js_str.replace("${powermakeVscodeFolderPath}", json.dumps(vscode_path)[1:-1])
    return js_str

def generate_vscode(config: Config, vscode_path: str) -> None:
    debug = config.debug
    config.set_debug(True)
    makedirs(vscode_path)

    launch_template_path = os.path.join(config.global_config_dir, "vscode_templates", "launch.json")
    tasks_template_path = os.path.join(config.global_config_dir, "vscode_templates", "tasks.json")

    if not os.path.exists(launch_template_path):
        makedirs(os.path.join(config.global_config_dir, "vscode_templates"))
        with open(launch_template_path, "w") as file:
            file.write(__default_launch)
        launch_content = __default_launch
    else:
        with open(launch_template_path, "r") as file:
            launch_content = file.read()

    if not os.path.exists(tasks_template_path):
        with open(tasks_template_path, "w") as file:
            file.write(__default_tasks)
        tasks_content = __default_tasks
    else:
        with open(tasks_template_path, "r") as file:
            tasks_content = file.read()

    with open(os.path.join(vscode_path, "launch.json"), "w") as file:
        file.write(format_json_string(launch_content, os.path.abspath(os.path.join(config.exe_build_directory, config.target_name)), vscode_path))

    with open(os.path.join(vscode_path, "tasks.json"), "w") as file:
        file.write(format_json_string(tasks_content, os.path.abspath(os.path.join(config.exe_build_directory, config.target_name)), vscode_path))

    config.set_debug(debug)