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
import subprocess
import typing as T
import __main__ as __makefile__
from threading import Lock

from . import generation
from .config import Config
from .utils import print_bytes
from .exceptions import PowerMakeCommandError
from .display import print_info, print_debug_info, error_text

class CompilationStopper:
    stop = False


def resolve_path(current_folder: str, additional_includedirs: T.List[str], filepath: str) -> T.Union[str, None]:
    path = os.path.join(current_folder, filepath)
    if os.path.exists(path):
        return path
    for folder in additional_includedirs:
        path = os.path.join(folder, filepath)
        if os.path.exists(path):
            return path
    return None


def is_file_uptodate_recursive(output_date: float, filename: str, additional_includedirs: T.List[str], headers_already_found: T.List[str] = []) -> bool:
    try:
        if os.path.getmtime(filename) >= output_date:
            return False
    except OSError:
        return False

    if not filename.endswith((".c", ".cpp", ".cc", ".C", ".h", ".hpp", ".lex", ".y", ".rc")):
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


def needs_update(outputfile: str, dependencies: T.Iterable[str], additional_includedirs: T.List[str]) -> bool:
    """
    Returns whether or not `outputfile` is up to date with all his dependencies

    If `dependencies` includes C/C++ files and headers, all headers these files include recursively will be add as hidden dependencies.

    Parameters
    ----------
    outputfile : str
        The path to the target file.
    dependencies : Iterable[str]
        A set of all files on which `outputfile` depends.
    additional_includedirs : list[str]
        The list of additional includedirs used by the compiler. This is necessary to discover hidden dependencies.

    Returns
    -------
    bool
        True if `outputfile` is **not** up to date with all his dependencies and hidden dependencies.
    """
    try:
        output_date = os.path.getmtime(outputfile)
    except OSError:
        return True

    if hasattr(__makefile__, '__file__') and os.path.getmtime(__makefile__.__file__) >= output_date:
        return True

    headers_already_found: T.List[str] = []
    for dep in dependencies:
        if not is_file_uptodate_recursive(output_date, dep, additional_includedirs, headers_already_found):
            return True

    return False


_print_lock = Lock()
_commands_counter = 0
def run_command_get_output(config: Config, command: T.Union[T.List[str], str], shell: bool = False, target: T.Union[str, None] = None, output_filter: T.Union[T.Callable[[bytes], bytes], None] = None, _dependencies: T.Iterable[str] = [], _generate_makefile: bool = True, _tool: str = "", stderr: T.Union[int, T.IO[T.Any], None] = subprocess.STDOUT, stopper: T.Union[CompilationStopper, None] = None, **kwargs: T.Any) -> T.Tuple[int, bytes]:
    global _commands_counter

    returncode = 0
    try:
        output = subprocess.check_output(command, shell=shell, stderr=stderr, **kwargs)
    except subprocess.CalledProcessError as e:
        output = e.output
        returncode = e.returncode

    if output_filter is not None:
        output = output_filter(output)

    if stopper is not None and stopper.stop:
        return 0, output

    _print_lock.acquire()

    _commands_counter += 1

    print_info(f"Generating {os.path.basename(target)}" if target is not None else "", config.verbosity, _commands_counter, config.nb_total_operations)

    print_debug_info(command, config.verbosity)

    print_bytes(output)

    phony = False
    if target is None:
        target = f"_powermake_auto_target{_commands_counter}"
        phony = True
    _print_lock.release()

    if (config._args_parsed is not None and config._args_parsed.makefile or config.compile_commands_dir is not None) and _generate_makefile:
        generation._makefile_targets_mutex.acquire()
        generation._makefile_targets.append([(phony, target, _dependencies, command, _tool)])
        generation._makefile_targets_mutex.release()

    return returncode, output

def run_command(config: Config, command: T.Union[T.List[str], str], shell: bool = False, target: T.Union[str, None] = None, output_filter: T.Union[T.Callable[[bytes], bytes], None] = None, _dependencies: T.Iterable[str] = [], _generate_makefile: bool = True, _tool: str = "", stopper: T.Union[CompilationStopper, None] = None, **kwargs: T.Any) -> int:
    return run_command_get_output(config, command, shell, target, output_filter, _dependencies, _generate_makefile, _tool, stopper=stopper, **kwargs)[0]

def run_command_if_needed(config: Config, outputfile: str, dependencies: T.Iterable[str], command: T.Union[T.List[str], str], shell: bool = False, force: T.Union[bool, None] = None, _generate_makefile: bool = True, _tool: str = "", stopper: T.Union[CompilationStopper, None] = None, **kwargs: T.Any) -> str:
    """
    Run a command generating a file only if this file needs to be re-generated.

    Parameters
    ----------
    config : powermake.Config
        A powermake.Config object, containing all directives for the compilation. Either the one given to the build_callback or a modified copy.
    outputfile : str
        The file that will be generated by the command
    dependencies : Iterable[str]
        An iterable of every file that if changed should trigger the run of the command.
    command : list[str] | str
        If shell is False, should be a list of arguments, the first one being the executable to run.  
        If shell is True, should be a string representing the shell command.
    shell : bool, optional
        If True, the command is run through a shell
    force : T.Union[bool, None], optional
        Whether the function should verify if the outputfile is up to date or if the command should be run anyway.  
        If not specified, this parameter takes the value of config.rebuild

    Returns
    -------
    str
        The outputfile, for functional programming.

    Raises
    ------
    PowerMakeRuntimeError
        When the command exit with a non-zero status code.
    """
    global _commands_counter

    if force is None:
        force = config.rebuild
    if force or needs_update(outputfile, dependencies, additional_includedirs=config.additional_includedirs):
        if run_command(config, command, shell=shell, target=outputfile, _dependencies=dependencies, _generate_makefile=_generate_makefile, _tool=_tool, stopper=stopper, **kwargs) != 0:
            command_ex = ""
            if isinstance(command, list) and len(command) > 0:
                command_ex = command[0]
            else:
                command_ex = T.cast(str, command)
            if stopper is not None:
                stopper.stop = True
            raise PowerMakeCommandError(error_text(f"Unable to generate {os.path.basename(outputfile)}, {command_ex} returned a non-zero status (see above)"))
    else:
        _print_lock.acquire()
        _commands_counter += 1
        _print_lock.release()
        if config.compile_commands_dir is not None and _generate_makefile:
            generation._makefile_targets_mutex.acquire()
            generation._makefile_targets.append([(False, outputfile, dependencies, command, _tool)])
            generation._makefile_targets_mutex.release()
    return outputfile


class Operation:
    def __init__(self, outputfile: str, dependencies: T.Iterable[str], config: Config, command: T.List[str], tool: str = ""):
        """
        Provide a simple object that can execute a command only if it's needed.

        Parameters
        ----------
        outputfile : str
            The path to the target file.
        dependencies : Iterable[str]
            A set of all files on which `outputfile` depends
        config : powermake.Config
            A powermake.Config object, the additional_includedirs in it should be completed
        command : list[str]
            The command that will be executed by subprocess. It's a list representing the argv that will be passed to the program at the first list position.
        """
        self.outputfile = outputfile
        self.dependencies = dependencies
        self.command = command
        self.config = config
        self.tool = tool

    def execute(self, force: T.Union[bool, None] = None, _generate_makefile: bool = True, stopper: T.Union[CompilationStopper, None] = None) -> str:
        """
        Verify if the outputfile is up to date with his dependencies and if not, execute the command.

        Parameters
        ----------
        force : bool, optional
            If True, this function will always execute the command without verifying if this is needed.

        Returns
        -------
        outputfile: str
            The outputfile, like that we can easily parallelize this method.

        Raises
        ------
        PowerMakeRuntimeError
            If the command fails.
        """

        return run_command_if_needed(self.config, self.outputfile, self.dependencies, self.command, force=force, _generate_makefile=_generate_makefile, _tool=self.tool, stopper=stopper)
