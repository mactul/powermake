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
import sys
import glob
import json
import shutil
import fnmatch
import subprocess
import importlib.util
import __main__ as __makefile__
import typing as T
from concurrent.futures import ThreadPoolExecutor

from .config import Config
from .utils import makedirs
from .__version__ import __version__
from . import utils, display, generation
from .display import print_info, print_debug_info
from .exceptions import PowerMakeRuntimeError, PowerMakeValueError
from .operation import Operation, needs_update, run_command, run_command_get_output, run_command_if_needed, CompilationStopper
from .args_parser import run, default_on_clean, default_on_install, default_on_test, ArgumentParser, generate_config, run_callbacks


if hasattr(__makefile__, '__file__'):
    # Change the cwd to the directory of the makefile.
    _cwd = os.path.dirname(os.path.realpath(__makefile__.__file__))
    _use_absolute_path = False
    if not os.path.samefile(_cwd, os.getcwd()):
        _use_absolute_path = True
        os.chdir(_cwd)


def import_module(module_name: str, module_path: T.Union[str, None] = None) -> T.Any:
    """
    Import a custom module from a path

    You can do this instead of a regular `import` and updating the `PYTHONPATH` env variable.

    Parameters
    ----------
    module_name : str
        The name of the module once it will be imported
    module_path : str | None, optional
        The path of the module, if None, it takes the module_name as a path.

    Returns
    -------
    module : module
        A module object, that you can use as a namespace
    """
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


def get_files(*patterns: str) -> T.Set[str]:
    """
    Return all files on the disk that matches one of the patterns given.

    Supported patterns are `*`, like `./*.c` and `**/` like `./**/*.c` to search all .c recursively, starting at `./`

    **Warning**: `**.c` will not return all .c recursively, you have to use `**/*.c` for that.

    Parameters
    ----------
    *patterns : str
        As many patterns as you want to include

    Returns
    -------
    files : set[str]
        A set (unordered list) of files. You can use the methods `add` and `update` to add files to this set.
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


def filter_files(files: T.Set[str], *patterns: str) -> T.Set[str]:
    """
    Create a copy of the set `files` with all elements that matches `pattern` removed.

    This function will equally works if `files` is an iterable but will always returns a set.

    Parameters
    ----------
    files : set[str]
        The set of files to filter.
    *patterns : str
        As many patterns as you want to exclude

    Returns
    -------
    files : set[str]
        the filtered set
    """
    output = set()
    for file in files:
        if not _match_a_pattern(file, patterns):
            output.add(file)
    return output


def _file_in_files_set(file: str, files_set: T.Iterable[str]) -> bool:
    for f in files_set:
        if os.path.samefile(f, file):
            return True
    return False


def compile_files(config: Config, files: T.Union[T.Set[str], T.List[str]], force: T.Union[bool, None] = None) -> T.Union[T.Set[str], T.List[str]]:
    """
    Compile each C/C++/ASM file in the `files` set according to the compiler and options stored in `config`

    The compilation is parallelized with `config.nb_jobs` threads

    If `files` is a list, compile_files will return a list instead of a set, with the order preserved

    Parameters
    ----------
    config : powermake.Config
        A powermake.Config object, containing all directives for the compilation. Either the one given to the build_callback or a modified copy.
    files : set[str] | list[str]
        A set of files that ends by .c, .cpp, .cc, .C, .s, .S, .rc or .asm to compile in .o (or the specified compiler equivalent extension)
    force : bool | None, optional
        Whether the function should verify if a file needs to be recompiled or if it should recompile everything.  
        If not specified, this parameter takes the value of config.rebuild

    Returns
    -------
    set[str] | list[str]
        A set of object filepaths generated by by the compilation

    Raises
    ------
    PowerMakeRuntimeError
        If no compiler is found.
    PowerMakeValueError
        if `files` contains a file that doesn't ends with .c, .cpp, .cc, .C, .s, .S, .rc or .asm.
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
        if not _file_in_files_set(config.single_file, files):
            if isinstance(files, set):
                return set()
            return []
        if isinstance(files, set):
            files = {config.single_file}
        else:
            files = [config.single_file]


    if config.c_compiler is not None:
        c_args = config.c_compiler.format_args(config.defines, config.additional_includedirs, config.c_flags)
    else:
        c_args = []

    if config.cpp_compiler is not None:
        cpp_args = config.cpp_compiler.format_args(config.defines, config.additional_includedirs, config.cpp_flags)
    else:
        cpp_args = []

    if config.as_compiler is not None:
        as_args = config.as_compiler.format_args(config.defines, config.additional_includedirs, config.as_flags)
    else:
        as_args = []

    if config.rc_compiler is not None:
        rc_args = config.rc_compiler.format_args(config.defines, config.additional_includedirs, config.rc_flags)
    else:
        rc_args = []

    if config.asm_compiler is not None:
        asm_args = config.asm_compiler.format_args(config.defines, config.additional_includedirs, config.asm_flags)
    else:
        asm_args = []

    for file in files:
        output_file = utils.join_absolute_paths(config.obj_build_directory, file)
        makedirs(os.path.dirname(output_file), exist_ok=True)

        if _use_absolute_path:
            # if the path of the file is not relative to the shell cwd, the ide might not be able to understand warning messages.
            file = os.path.abspath(file)

        if file.endswith(".c"):
            if config.c_compiler is None:
                raise PowerMakeRuntimeError(display.error_text("No C compiler has been specified and the default config didn't find any"))
            output_file += config.c_compiler.obj_extension
            command = config.c_compiler.basic_compile_command(output_file, file, c_args)
            tool = "CC"
        elif file.endswith((".cpp", ".cc", ".C")):
            if config.cpp_compiler is None:
                raise PowerMakeRuntimeError(display.error_text("No C++ compiler has been specified and the default config didn't find any"))
            output_file += config.cpp_compiler.obj_extension
            command = config.cpp_compiler.basic_compile_command(output_file, file, cpp_args)
            tool = "CXX"
        elif file.endswith((".s", ".S")):
            if config.as_compiler is None:
                raise PowerMakeRuntimeError(display.error_text("No AS compiler has been specified and the default config didn't find any"))
            output_file += config.as_compiler.obj_extension
            command = config.as_compiler.basic_compile_command(output_file, file, as_args)
            tool = "AS"
        elif file.endswith(".asm"):
            if config.asm_compiler is None:
                raise PowerMakeRuntimeError(display.error_text("No ASM compiler has been specified and the default config didn't find any"))
            output_file += config.asm_compiler.obj_extension
            command = config.asm_compiler.basic_compile_command(output_file, file, asm_args)
            tool = "ASM"
        elif file.endswith(".rc"):
            if config.rc_compiler is None:
                raise PowerMakeRuntimeError(display.error_text("No RC compiler has been specified and the default config didn't find any"))
            output_file += config.rc_compiler.obj_extension
            command = config.rc_compiler.basic_compile_command(output_file, file, rc_args)
            tool = "RC"
        else:
            raise PowerMakeValueError(display.error_text(f"The file extension {os.path.splitext(file)[1]} can't be compiled"))
        op = Operation(output_file, {file}, config, command, tool)
        if isinstance(files, set):
            T.cast(T.Set[Operation], operations).add(op)
        else:
            T.cast(T.List[Operation], operations).append(op)

    if config.single_file is not None:
        (op, ) = operations
        op.execute(force)
        exit(0)

    if config._args_parsed is not None and config._args_parsed.makefile or config.compile_commands_dir is not None:
        generation._makefile_targets_mutex.acquire()
        generation._makefile_targets.append([(False, op.outputfile, op.dependencies, op.command, op.tool) for op in operations])
        generation._makefile_targets_mutex.release()

    stopper = CompilationStopper()
    with ThreadPoolExecutor(max_workers=config.nb_jobs) as executor:
        output = executor.map(lambda op: op.execute(force, _generate_makefile=False, stopper=stopper), operations)
        if isinstance(files, set):
            generated_objects = set(output)
        else:
            generated_objects = list(output)

    return generated_objects


def archive_files(config: Config, object_files: T.Iterable[str], archive_name: T.Union[str, None] = None, force: T.Union[bool, None] = None) -> str:
    """
    Create a static library from a set or a list of object files.

    Parameters
    ----------
    config : powermake.Config
        A powermake.Config object, containing all directives for the compilation. Either the one given to the build_callback or a modified copy.
    object_files : Iterable[str]
        A set of object files, potentially the set generated by `powermake.compile_files`. It can be a list if the order matters.
    archive_name : str | None, optional
        The name of the static library you want to create, minus the extension. If None, it will be lib{config.target_name}
    force : bool | None, optional
        Whether the function should verify if the static library needs to be re-archived or if it should re-archive in any case.  
        If not specified, this parameter takes the value of config.rebuild

    Returns
    -------
    path : str
        The path of the archive generated

    Raises
    ------
    PowerMakeRuntimeError
        If no archiver is found.
    """
    if force is None:
        force = config.rebuild

    if archive_name is None:
        archive_name = "lib" + config.target_name

    if config.archiver is None:
        raise PowerMakeRuntimeError(display.error_text("No archiver has been specified and the default config didn't find any"))
    output_file = os.path.join(config.lib_build_directory, archive_name + config.archiver.static_lib_extension)
    makedirs(os.path.dirname(output_file), exist_ok=True)
    command = config.archiver.basic_archive_command(output_file, object_files, config.ar_flags)
    return Operation(output_file, object_files, config, command, "AR").execute(force=force)


def link_files(config: Config, object_files: T.Iterable[str], archives: T.List[str] = [], executable_name: T.Union[str, None] = None, force: T.Union[bool, None] = None) -> str:
    """
    Create an executable from a list of object files and a list of archive files.

    Parameters
    ----------
    config : powermake.Config
        A powermake.Config object, containing all directives for the compilation. Either the one given to the build_callback or a modified copy.
    object_files : Iterable[str]
        A set of object files, potentially the set generated by `powermake.compile_files`. It can be a list if the order matters.
    archives : list[str], optional
        A list of static libraries filepaths.
    executable_name :str | None, optional
        The name of the executable you want to create, minus the extension. If None, it will be config.target_name.
    force : bool | None, optional
        Whether the function should verify if the executable needs to be re-linked or if it should re-link in any case.  
        If not specified, this parameter takes the value of config.rebuild

    Returns
    -------
    path: str
        The path of the executable generated

    Raises
    ------
    PowerMakeRuntimeError
        If no linker is found.
    """
    if force is None:
        force = config.rebuild

    if executable_name is None:
        executable_name = config.target_name

    if config.linker is None:
        raise PowerMakeRuntimeError(display.error_text("No linker has been specified and the default config didn't find any"))
    extension = ""
    if config.target_is_windows():
        extension = ".exe"
    output_file = os.path.join(config.exe_build_directory, executable_name + extension)
    makedirs(os.path.dirname(output_file), exist_ok=True)
    args = config.linker.format_args(shared_libs=config.shared_libs, flags=config.ld_flags)
    command = config.linker.basic_link_command(output_file, object_files, archives, args)
    return Operation(output_file, set(object_files).union(archives), config, command, "LD").execute(force=force)


def link_shared_lib(config: Config, object_files: T.Iterable[str], archives: T.List[str] = [], lib_name: T.Union[str, None] = None, force: T.Union[bool, None] = None) -> str:
    """
    Create a shared library from a list of object files and a list of archive files.

    Parameters
    ----------
    config : powermake.Config
        A powermake.Config object, containing all directives for the compilation. Either the one given to the build_callback or a modified copy.
    object_files : Iterable[str]
        A set of object files, potentially the set generated by `powermake.compile_files`. It can be a list if the order matters.
    archives : list[str], optional
        A list of static libraries filepaths.
    lib_name :str | None, optional
        The name of the library you want to create, minus the extension. If None, it will be lib{config.target_name}.
    force : bool | None, optional
        Whether the function should verify if the library needs to be re-linked or if it should re-link in any case.  
        If not specified, this parameter takes the value of config.rebuild

    Returns
    -------
    path: str
        The path of the library generated

    Raises
    ------
    PowerMakeRuntimeError
        If no shared linker is found.
    """
    if force is None:
        force = config.rebuild

    if lib_name is None:
        lib_name = "lib" + config.target_name

    if config.shared_linker is None:
        raise PowerMakeRuntimeError(display.error_text("No shared linker has been specified and the default config didn't find any"))
    output_file = os.path.join(config.lib_build_directory, lib_name + config.shared_linker.shared_lib_extension)
    makedirs(os.path.dirname(output_file), exist_ok=True)
    args = config.shared_linker.format_args(shared_libs=config.shared_libs, flags=config.shared_linker_flags)
    command = config.shared_linker.basic_link_command(output_file, object_files, archives, args)
    return Operation(output_file, set(object_files).union(archives), config, command, "SHLD").execute(force=force)


def delete_files_from_disk(*patterns: str) -> None:
    """
    Delete files and folders match at least one of the patterns.

    Warning: These files are permanently deleted.
    """
    for pattern in patterns:
        filepaths = get_files(pattern)
        for filepath in filepaths:
            if os.path.isdir(filepath):
                shutil.rmtree(filepath)
            else:
                os.remove(filepath)

def _get_libs_from_folder(lib_build_folder: str) -> T.Union[T.List[str], None]:
    if lib_build_folder != "" and os.path.exists(lib_build_folder):
        return [os.path.join(lib_build_folder, file) for file in os.listdir(lib_build_folder)]
    return None


def run_another_powermake(config: Config, path: str, debug: T.Union[bool, None] = None, rebuild: T.Union[bool, None] = None, verbosity: T.Union[int, None] = None, nb_jobs: T.Union[int, None] = None, command_line_args: T.List[str] = []) -> T.Union[T.List[str], None]:
    """
    Run a powermake from another directory and returns a list of path to all libraries generated

    Parameters
    ----------
    config : powermake.Config
        A powermake.Config object, containing all directives for the compilation. Either the one given to the build_callback or a modified copy.
    path : str
        The path of the powermake to run.
    debug : bool | None, optional
        Whether the other powermake should be run in debug mode.  
        If not specified, this parameter takes the value of config.debug
    rebuild : bool | None, optional
        Whether the other powermake should be run in rebuild mode.  
        If not specified, this parameter takes the value of config.rebuild
    verbosity : int | None, optional
        With which verbosity level the other powermake should be run.  
        If not specified, this parameter takes the value of config.verbosity
    nb_jobs : int | None, optional
        With how many threads the other powermake should be run.  
        If not specified, this parameter takes the value of config.nb_jobs

    Returns
    -------
    paths: list[str] | None
        A list of path to all libraries generated

    Raises
    ------
    PowerMakeRuntimeError
        If the other powermake fails.
    """
    if debug is None:
        debug = config.debug
    if rebuild is None:
        rebuild = config.rebuild
    if verbosity is None:
        verbosity = config.verbosity
    if nb_jobs is None:
        nb_jobs = config.nb_jobs

    print_info(f"Running {path}", config.verbosity)

    inode_nb = str(os.stat(path).st_ino)

    if inode_nb in config._cumulated_launched_powermakes:
        print_debug_info(f"PowerMake already run during this compilation unit - skip", config.verbosity)
        return _get_libs_from_folder(config._cumulated_launched_powermakes[inode_nb])

    command = [sys.executable, path, "--get-compilation-metadata", json.dumps(config._cumulated_launched_powermakes), "--retransmit-colors", "-j", str(nb_jobs)]
    if verbosity == 0:
        command.append("-q")
    elif verbosity >= 2:
        command.append("-v")

    if rebuild:
        command.append("-r")

    if debug:
        command.append("-d")

    command.extend(command_line_args)

    print_debug_info(command, config.verbosity)

    try:
        output: bytes = subprocess.check_output(command, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        utils.print_bytes(e.output)
        raise PowerMakeRuntimeError(display.error_text(f"Failed to run powermake {path}")) from None

    last_line_offset = output[:-1].rfind(ord('\n'))
    if last_line_offset == -1:
        raise RuntimeError("PowerMake corrupted; please verify your installation")

    utils.print_bytes(output[:last_line_offset])

    last_line = output[last_line_offset+1:].decode("utf-8").strip()
    if last_line == "":
        raise RuntimeError("PowerMake corrupted; --get-compilation-metadata doesn't return anything, if you use powermake.generate_config, make sure to also use powermake.run_callbacks")
    metadata = json.loads(last_line)
    if not isinstance(metadata, dict):
        raise RuntimeError("PowerMake corrupted; please verify your installation")
    config._cumulated_launched_powermakes = {**config._cumulated_launched_powermakes, **metadata["cumulated_launched_powermakes"], inode_nb: metadata["lib_build_directory"]}
    return _get_libs_from_folder(metadata["lib_build_directory"])

