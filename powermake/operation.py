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


import os
import subprocess
from threading import Lock

from .config import Config
from .display import print_info, print_debug_info


def resolve_path(current_folder: str, additional_includedirs: list, filepath: str) -> str:
    path = os.path.join(current_folder, filepath)
    if os.path.exists(path):
        return path
    for folder in additional_includedirs:
        path = os.path.join(folder, filepath)
        if os.path.exists(path):
            return path
    return None


def is_file_uptodate_recursive(output_date: float, filename: str, additional_includedirs: list, headers_already_found: list = []) -> bool:
    try:
        if os.path.getmtime(filename) >= output_date:
            return False
    except OSError:
        return False

    if not filename.endswith((".c", ".cpp", ".cc", ".C", ".h", ".hpp")):
        return True

    headers_found = []
    file = open(filename, "r", encoding="latin1")

    # The four lines under this comment are here for the compatibility with python < 3.8
    # They are equivalent to `while line := file.readline():`
    while True:
        line = file.readline()
        if not line:
            break

        i = 0
        while i < len(line) and (line[i] == ' ' or line[i] == '\t'):
            i += 1
        if i >= len(line):
            continue
        if line[i] != '#':
            continue
        i += 1
        while i < len(line) and (line[i] == ' ' or line[i] == '\t'):
            i += 1
        if i >= len(line):
            continue
        if line[i:].startswith("include"):
            i += len("include")
            if i >= len(line) or (line[i] != ' ' and line[i] != '\t'):
                continue
            i += 1
            while i < len(line) and (line[i] == ' ' or line[i] == '\t'):
                i += 1
            if i >= len(line) or line[i] != '"':
                continue
            i += 1
            j = i
            while j < len(line) and line[j] != '"':
                j += 1
            if j >= len(line):
                continue

            if line[i:j] not in headers_found:
                headers_found.append(line[i:j])

    file.close()

    if len(headers_found) == 0:
        return True

    current_folder = os.path.dirname(filename)
    new_paths = []
    for i in range(len(headers_found)):
        path = resolve_path(current_folder, additional_includedirs, headers_found[i])
        if path is not None and path not in headers_already_found:
            headers_already_found.append(path)
            new_paths.append(path)

    del headers_found

    for path in new_paths:
        if not is_file_uptodate_recursive(output_date, path, additional_includedirs, headers_already_found):
            return False

    return True


def needs_update(outputfile: str, dependencies: set, additional_includedirs: list) -> bool:
    """Returns whether or not `outputfile` is up to date with all his dependencies

    If `dependencies` includes C/C++ files and headers, all headers these files include recursively will be add as hidden dependencies.

    Args:
        outputfile (str): the path to the target file
        dependencies (set): a set of all files on which `outputfile` depends
        additional_includedirs (list): The list of additional includedirs used by the compiler. This is necessary to discover hidden dependencies.

    Returns:
        bool: True if `outputfile` is **not** up to date with all his dependencies and hidden dependencies.
    """
    try:
        output_date = os.path.getmtime(outputfile)
    except OSError:
        return True
    headers_already_found = []
    for dep in dependencies:
        if not is_file_uptodate_recursive(output_date, dep, additional_includedirs, headers_already_found):
            return True

    return False


class Operation:
    def __init__(self, outputfile: str, dependencies: set, config: Config, command: list):
        """Provide a simple object that can execute a command only if it's needed.

        Args:
            outputfile (str): the path to the target file
            dependencies (set): a set of all files on which `outputfile` depends
            config (Config): A powermake.Config object, the additional_includedirs in it should be completed
            command (list): The command that will be executed by subprocess. It's a list representing the argv that will be passed to the program at the first list position.
        """
        self.outputfile = outputfile
        self.dependencies = dependencies
        self._hidden_dependencies = None
        self.command = command
        self.config = config

    def execute(self, force: bool = False, print_lock: Lock = None) -> str:
        """Verify if the outputfile is up to date with his dependencies and if not, execute the command.

        Args:
            force (bool, optional): If True, this function will always execute the command without verifying if this is needed.
            print_lock (Lock, optional): A mutex to ensure that no print mixes together when parallelizing Operations.  
                If None, no mutex is used, the compilation will be fine but the output might be a little bit buggy.

        Raises:
            RuntimeError: If the command fails.

        Returns:
            str: The outputfile, like that we can easily parallelize this method.
        """
        if force or needs_update(self.outputfile, self.dependencies, self.config.additional_includedirs):

            if self.config.verbosity > 0:
                if print_lock is not None:
                    print_lock.acquire()

                print_info(f"Generating {os.path.basename(self.outputfile)}", self.config.verbosity)
                print_debug_info(self.command, self.config.verbosity)

                if print_lock is not None:
                    print_lock.release()

            if subprocess.run(self.command).returncode == 0:
                return self.outputfile
            else:
                raise RuntimeError(f"Unable to generate {os.path.basename(self.outputfile)}")
        return self.outputfile

    def get_json_command(self):
        json_command = {
            "directory": os.getcwd(),
            "arguments": self.command,
            "output": self.outputfile
        }
        if len(self.dependencies) > 0:
            json_command["file"] = self.dependencies[0]

        return json_command
