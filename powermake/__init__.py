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
import sys
import glob
import json
import fnmatch
import subprocess
import importlib.util
import __main__ as __makefile__
import typing as T
from threading import Lock
from concurrent.futures import ThreadPoolExecutor

from .config import Config
from .utils import makedirs
from .display import print_info, print_debug_info
from .operation import Operation, needs_update
from .args_parser import run, default_on_clean, default_on_install, ArgumentParser, generate_config, run_callbacks


if hasattr(__makefile__, '__file__'):
    os.chdir(os.path.dirname(os.path.realpath(__makefile__.__file__)))


def run_command(config: Config, command: T.Union[T.List[str], str], shell: bool = False, **kwargs):
    print_debug_info(command, config.verbosity)
    return subprocess.run(command, shell=shell, **kwargs).returncode


def import_module(module_name: str, module_path: T.Union[str, None] = None):
    """Import a custom module from a path

    Args:
        module_name (str): The name of the module once it will be imported
        module_path (str, optional): The path of the module, if None, it takes the module_name as a path.

    Returns:
        module: an module object, that you can use as a namespace
    """
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


def get_files(*patterns: str) -> set:
    """Return all files on the disk that matches one of the patterns given

    Supported patterns are `*`, like `./*.c` and `**/` like `./**/*.c` to search all .c recursively, starting at `./`

    Warning: `**.c` will not return all .c recursively, you have to use `**/*.c` for that.

    Args:
        patterns (str): As many patterns as you want to include

    Returns:
        set: A set (unordered list) of files. You can use the methods `add` and `update` to add files to this set.
    """
    files = set()
    for pattern in patterns:
        files.update(glob.glob(pattern, recursive=True))
    return files


def _match_a_pattern(file: str, patterns: T.Iterable[str]) -> bool:
    for pattern in patterns:
        if fnmatch.fnmatch(file, pattern):
            return True
    return False


def filter_files(files: T.Set[str], *patterns: str) -> set:
    """Create a copy of the set `files` with all elements that matches `pattern` removed.

    This function will equally works if `files` is an iterable but will always returns a set.

    Args:
        files (set): The set of files to filter
        patterns (str): As many patterns as you want to exclude

    Returns:
        set: the filtered set
    """
    output = set()
    for file in files:
        if not _match_a_pattern(file, patterns):
            output.add(file)
    return output


def file_in_files_set(file: str, files_set: T.Iterable[str]) -> bool:
    for f in files_set:
        if os.path.samefile(f, file):
            return True
    return False


def compile_files(config: Config, files: T.Union[T.Set[str], T.List[str]], force: T.Union[bool, None] = None) -> T.Union[T.Set[str], T.List[str]]:
    """Compile each C/C++/ASM file in the `files` set according to the compiler and options stored in `config`

    The compilation is parallelized with `config.nb_jobs` threads

    If `files` is a list, compile_files will return a list instead of a set, with the order preserved

    Args:
        config (Config): A powermake.Config object, containing all directives for the compilation. Either the one given to the build_callback or a modified copy.
        files (set): A set of files that ends by .c, .cpp, .cc, .C, .s, .S or .asm to compile in .o (or the specified compiler equivalent extension)
        force (bool, optional): Whether the function should verify if a file needs to be recompiled or if it should recompile everything.  
            If not specified, this parameter takes the value of config.rebuild

    Raises:
        RuntimeError: if no compiler is found
        ValueError: if `files` contains a file that doesn't ends with .c, .cpp, .cc, .C, .s, .S or .asm

    Returns:
        set: A set of object filepaths generated by by the compilation
    """
    generated_objects: T.Union[T.Set[str], T.List[str]] = set()

    operations: T.Union[T.Set[Operation], T.List[Operation]]

    if isinstance(files, set):
        operations = set()
    else:
        operations = []

    if force is None:
        force = config.rebuild

    if config.single_file is not None:
        if file_in_files_set(config.single_file, files):
            if isinstance(files, set):
                files = {config.single_file}
            else:
                files = [config.single_file]
        else:
            if isinstance(files, set):
                return set()
            return []

    if config.c_compiler is not None:
        c_args = config.c_compiler.format_args(config.defines, config.additional_includedirs, config.c_flags)
    else:
        c_args = None

    if config.cpp_compiler is not None:
        cpp_args = config.cpp_compiler.format_args(config.defines, config.additional_includedirs, config.cpp_flags)
    else:
        cpp_args = None

    if config.as_compiler is not None:
        as_args = config.as_compiler.format_args(config.defines, config.additional_includedirs, config.as_flags)
    else:
        as_args = None

    if config.asm_compiler is not None:
        asm_args = config.asm_compiler.format_args(config.defines, config.additional_includedirs, config.asm_flags)
    else:
        asm_args = None

    for file in files:
        if config.c_compiler is not None:
            obj_extension = config.c_compiler.obj_extension
        elif config.cpp_compiler is not None:
            obj_extension = config.cpp_compiler.obj_extension
        else:
            raise RuntimeError("No C/C++ compiler has been specified and the default config didn't find any")

        output_file = os.path.normpath(config.obj_build_directory + "/" + file.replace("..", "__") + config.c_compiler.obj_extension)
        makedirs(os.path.dirname(output_file), exist_ok=True)

        file = os.path.abspath(file)

        if file.endswith(".c"):
            if config.c_compiler is None:
                raise RuntimeError("No C compiler has been specified and the default config didn't find any")
            command = config.c_compiler.basic_compile_command(output_file, file, c_args)
        elif file.endswith((".cpp", ".cc", ".C")):
            if config.cpp_compiler is None:
                raise RuntimeError("No C++ compiler has been specified and the default config didn't find any")
            command = config.cpp_compiler.basic_compile_command(output_file, file, cpp_args)
        elif file.endswith((".s", ".S")):
            if config.as_compiler is None:
                raise RuntimeError("No AS compiler has been specified and the default config didn't find any")
            command = config.as_compiler.basic_compile_command(output_file, file, as_args)
        elif file.endswith(".asm"):
            if config.asm_compiler is None:
                raise RuntimeError("No ASM compiler has been specified and the default config didn't find any")
            command = config.asm_compiler.basic_compile_command(output_file, file, asm_args)
        else:
            raise ValueError("The file extension %s can't be compiled", (os.path.splitext(file)[1], ))
        op = Operation(output_file, {file}, config, command)
        if isinstance(files, set):
            operations.add(op)
        else:
            operations.append(op)

    if config.compile_commands_dir is not None:
        json_commands = []
        for op in operations:
            json_commands.append(op.get_json_command())

        makedirs(config.compile_commands_dir, exist_ok=True)
        with open(os.path.join(config.compile_commands_dir, "compile_commands.json"), "w") as fd:
            json.dump(json_commands, fd, indent=4)

    if config.single_file is not None:
        (op, ) = operations
        op.execute(force)
        exit(0)

    print_lock = Lock()
    with ThreadPoolExecutor(max_workers=config.nb_jobs) as executor:
        generated_objects = executor.map(lambda op: op.execute(force, print_lock), operations)
        if isinstance(files, set):
            generated_objects = set(generated_objects)
        else:
            generated_objects = list(generated_objects)

    return generated_objects


def archive_files(config: Config, object_files: T.Iterable[str], archive_name: T.Union[str, None] = None, force: T.Union[bool, None] = None) -> str:
    """Create a static library from A set of object files.

    Args:
        config (Config): A powermake.Config object, containing all directives for the compilation. Either the one given to the build_callback or a modified copy.
        object_files (set or list): A set of object files, potentially the set generated by `compile_files`. It can be a list if the order matters.
        archive_name (str, optional): The name of the static library you want to create, minus the extension. If None, it will be lib{config.target_name}
        force (bool, optional): Whether the function should verify if the static library needs to be re-archived or if it should re-archive in any case.  
            If not specified, this parameter takes the value of config.rebuild

    Raises:
        RuntimeError: if no archiver is found

    Returns:
        str: the path of the archive generated
    """
    if force is None:
        force = config.rebuild

    if archive_name is None:
        archive_name = "lib"+config.target_name

    if config.archiver is None:
        raise RuntimeError("No archiver has been specified and the default config didn't find any")
    output_file = os.path.normpath(config.lib_build_directory + "/" + archive_name + config.archiver.static_lib_extension)
    makedirs(os.path.dirname(output_file), exist_ok=True)
    command = config.archiver.basic_archive_command(output_file, object_files, config.ar_flags)
    return Operation(output_file, object_files, config, command).execute(force=force)


def link_files(config: Config, object_files: T.Iterable[str], archives: T.List[str] = [], executable_name: T.Union[str, None] = None, force: T.Union[bool, None] = None) -> str:
    """Create an executable from a list of object files and a list of archive files.

    Args:
        config (Config): A powermake.Config object, containing all directives for the compilation. Either the one given to the build_callback or a modified copy.
        object_files (set or list): A set of object files, potentially the set generated by `compile_files`. It can be a list if the order matters.
        archives (list): A set of static libraries filepaths
        executable_name (str, optional): The name of the executable you want to create, minus the extension. If None, it will be config.target_name
        force (bool, optional): Whether the function should verify if the executable needs to be re-linked or if it should re-link in any case.  
            If not specified, this parameter takes the value of config.rebuild

    Raises:
        RuntimeError: if no linker is found

    Returns:
        str: the path of the executable generated
    """
    if force is None:
        force = config.rebuild

    if executable_name is None:
        executable_name = config.target_name

    if config.linker is None:
        raise RuntimeError("No linker has been specified and the default config didn't find any")
    output_file = os.path.normpath(config.exe_build_directory + "/" + executable_name + config.linker.exe_extension)
    makedirs(os.path.dirname(output_file), exist_ok=True)
    args = config.linker.format_args(shared_libs=config.shared_libs, flags=config.ld_flags)
    command = config.linker.basic_link_command(output_file, object_files, archives, args)
    return Operation(output_file, set(object_files).union(archives), config, command).execute(force=force)


def link_shared_lib(config: Config, object_files: T.Iterable[str], archives: T.List[str] = [], lib_name: T.Union[str, None] = None, force: T.Union[bool, None] = None) -> str:
    """Create a shared library from a list of object files and a list of archive files.

    Args:
        config (Config): A powermake.Config object, containing all directives for the compilation. Either the one given to the build_callback or a modified copy.
        object_files (set): A set of object files, potentially the set generated by `compile_files`
        archives (list): A set of static libraries filepaths
        lib_name (str, optional): The name of the library you want to create, minus the extension. If None, it will be lib{config.target_name}
        force (bool, optional): Whether the function should verify if the library needs to be re-linked or if it should re-link in any case.  
            If not specified, this parameter takes the value of config.rebuild

    Raises:
        RuntimeError: if no shared linker is found

    Returns:
        str: the path of the library generated
    """
    if force is None:
        force = config.rebuild

    if lib_name is None:
        lib_name = "lib"+config.target_name

    if config.shared_linker is None:
        raise RuntimeError("No shared linker has been specified and the default config didn't find any")
    output_file = os.path.normpath(config.lib_build_directory + "/" + lib_name + config.shared_linker.shared_lib_extension)
    makedirs(os.path.dirname(output_file), exist_ok=True)
    args = config.shared_linker.format_args(shared_libs=config.shared_libs, flags=config.ld_flags)
    command = config.shared_linker.basic_link_command(output_file, object_files, archives, args)
    return Operation(output_file, set(object_files).union(archives), config, command).execute(force=force)


def delete_files_from_disk(*filepaths: str) -> None:
    """Delete a set of filepaths from the disk and ignore them if they don't exists
    """
    for filepath in filepaths:
        try:
            os.remove(filepath)
        except OSError:
            pass


def run_another_powermake(config: Config, path: str, debug: T.Union[bool, None] = None, rebuild: T.Union[bool, None] = None, verbosity: T.Union[int, None] = None, nb_jobs: T.Union[int, None] = None) -> T.Union[T.List[str], None]:
    """Run a powermake from another directory and returns a list of path to all libraries generated

    Args:
        config (Config): A powermake.Config object, containing all directives for the compilation. Either the one given to the build_callback or a modified copy.
        path (str): The path of the powermake to run
        debug (bool, optional): Whether the other powermake should be run in debug mode.  
            If not specified, this parameter takes the value of config.debug
        rebuild (bool, optional): Whether the other powermake should be run in rebuild mode.  
            If not specified, this parameter takes the value of config.rebuild
        verbosity (int, optional): With which verbosity level the other powermake should be run.  
            If not specified, this parameter takes the value of config.verbosity
        nb_jobs (int, optional): With how many threads the other powermake should be run.  
            If not specified, this parameter takes the value of config.nb_jobs

    Raises:
        RuntimeError: if the other powermake fails

    Returns:
        list: A list of path to all libraries generated
    """
    if debug is None:
        debug = config.debug
    if rebuild is None:
        rebuild = config.rebuild
    if verbosity is None:
        verbosity = config.verbosity
    if nb_jobs is None:
        nb_jobs = config.nb_jobs

    command = [sys.executable, path, "--get-lib-build-folder", "--retransmit-colors", "-j", str(nb_jobs)]
    if verbosity == 0:
        command.append("-q")
    elif verbosity >= 2:
        command.append("-v")

    if rebuild:
        command.append("-r")

    if debug:
        command.append("-d")

    print_info(f"Running {path}", config.verbosity)
    print_debug_info(command, config.verbosity)

    try:
        output = subprocess.check_output(command, encoding="utf-8").splitlines()
    except OSError:
        raise RuntimeError(f"Failed to run powermake {path}")

    if verbosity != 0:
        for line in output[:-1]:
            print(line)

    path = output[-1]
    if path != "":
        return [os.path.join(path, file) for file in os.listdir(path)]
    return None
