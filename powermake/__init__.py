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
import fnmatch
import subprocess
import importlib.util
import __main__ as __makefile__
from threading import Lock
from concurrent.futures import ThreadPoolExecutor

from .config import Config
from .display import print_info, print_debug_info
from .operation import Operation, needs_update
from .args_parser import run, default_on_clean, default_on_install

if hasattr(__makefile__, '__file__'):
    os.chdir(os.path.dirname(os.path.realpath(__makefile__.__file__)))


def import_module(module_name: str, module_path: str = None):
    """Import a custom module from a path

    Args:
        module_name (str): The name of the module once it will be imported
        module_path (str, optional): The path of the module, if None, it takes the module_name as a path.

    Returns:
        module: an module object, that you can use as a namespace
    """
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


def get_files(*patterns: str) -> set[str]:
    """Return all files on the disk that matches one of the patterns given

    Supported patterns are `*`, like `./*.c` and `**/` like `./**/*.c` to search all .c recursively, starting at `./`

    Warning: `**.c` will not return all .c recursively, you have to use `**/*.c` for that.

    Args:
        patterns (str): As many patterns as you want to include

    Returns:
        set[str]: A set (unordered list) of files. You can use the methods `add` and `update` to add files to this set.
    """
    files = set()
    for pattern in patterns:
        files.update(glob.glob(pattern, recursive=True))
    return files


def filter_files(files: set[str], *patterns: str) -> set[str]:
    """Create a copy of the set `files` with all elements that matches `pattern` removed.

    This function will equally works if `files` is an iterable but will always returns a set.

    Args:
        files (set[str]): The set of files to filter
        patterns (str): As many patterns as you want to exclude

    Returns:
        set[str]: the filtered set
    """
    output = set()
    for file in files:
        for pattern in patterns:
            if not fnmatch.fnmatch(file, pattern):
                output.add(file)
    return output


def file_in_files_set(file: str, files_set: set[str]) -> bool:
    for f in files_set:
        if os.path.samefile(f, file):
            return True
    return False


def compile_files(config: Config, files: set[str], force: bool = None) -> set[str]:
    """Compile each C/C++/ASM file in the `files` set according to the compiler and options stored in `config`

    The compilation is parallelized with `config.nb_jobs` threads

    This function will equally works if `files` is an iterable but will always returns a set.

    Args:
        config (Config): A powermake.Config object, containing all directives for the compilation. Either the one given to the build_callback or a modified copy.
        files (set[str]): A set of files that ends by .c, .cpp, .cc, .C, .s, .S or .asm to compile in .o (or the specified compiler equivalent extension)
        force (bool, optional): Whether the function should verify if a file needs to be recompiled or if it should recompile everything.  
            If not specified, this parameter takes the value of config.rebuild

    Raises:
        RuntimeError: if no compiler is found
        ValueError: if `files` contains a file that doesn't ends with .c, .cpp, .cc, .C, .s, .S or .asm

    Returns:
        set[str]: A set of object filepaths generated by by the compilation
    """
    generated_objects: set[str] = set()
    operations: set[Operation] = set()

    if force is None:
        force = config.rebuild

    if config.single_file is not None:
        if file_in_files_set(config.single_file, files):
            files = {config.single_file}
        else:
            return set()

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
        output_file = os.path.normpath(config.obj_build_directory + "/" + file.replace("..", "__") + config.c_compiler.obj_extension)
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

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
        operations.add(Operation(output_file, [file], config, command))

    if config.single_file is not None:
        (op, ) = operations
        op.execute(force)
        exit(0)

    print_lock = Lock()
    with ThreadPoolExecutor(max_workers=config.nb_jobs) as executor:
        generated_objects = set(executor.map(lambda op: op.execute(force, print_lock), operations))

        if False in generated_objects:
            generated_objects = False

    return generated_objects


def archive_files(config: Config, object_files: set[str], archive_name: str = None, force: bool = None) -> str:
    """Create a static library from A set of object files.

    Args:
        config (Config): A powermake.Config object, containing all directives for the compilation. Either the one given to the build_callback or a modified copy.
        object_files (set[str]): A set of object files, potentially the set generated by `compile_files`
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
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    command = config.archiver.basic_archive_command(output_file, object_files, config.ar_flags)
    return Operation(output_file, object_files, config, command).execute(force=force)


def link_files(config: Config, object_files: set[str], archives: list[str] = [], executable_name: str = None, force: bool = None) -> str:
    """Create an executable from a list of object files and a list of archive files.

    Args:
        config (Config): A powermake.Config object, containing all directives for the compilation. Either the one given to the build_callback or a modified copy.
        object_files (set[str]): A set of object files, potentially the set generated by `compile_files`
        archives (list[str]): A set of static libraries filepaths
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
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    args = config.linker.format_args(shared_libs=config.shared_libs, flags=config.ld_flags)
    command = config.linker.basic_link_command(output_file, object_files, archives, args)
    return Operation(output_file, object_files.union(archives), config, command).execute(force=force)


def link_shared_lib(config: Config, object_files: set[str], archives: list[str] = [], lib_name: str = None, force: bool = None) -> str:
    """Create a shared library from a list of object files and a list of archive files.

    Args:
        config (Config): A powermake.Config object, containing all directives for the compilation. Either the one given to the build_callback or a modified copy.
        object_files (set[str]): A set of object files, potentially the set generated by `compile_files`
        archives (list[str]): A set of static libraries filepaths
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
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    args = config.shared_linker.format_args(shared_libs=config.shared_libs, flags=config.ld_flags)
    command = config.shared_linker.basic_link_command(output_file, object_files, archives, args)
    return Operation(output_file, object_files.union(archives), config, command).execute(force=force)


def delete_files_from_disk(*filepaths: str) -> None:
    """Delete a set of filepaths from the disk and ignore them if they don't exists
    """
    for filepath in filepaths:
        try:
            os.remove(filepath)
        except OSError:
            pass


def run_another_powermake(config: Config, path: str, debug: bool = None, rebuild: bool = None, verbosity: int = None, nb_jobs: int = None) -> list[str]:
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
        list[str]: A list of path to all libraries generated
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
