import os
import glob
import fnmatch
import importlib.util
import __main__ as __makefile__
from threading import Lock
from concurrent.futures import ThreadPoolExecutor

from .config import Config
from .operation import Operation, needs_update
from .args_parser import run, default_on_clean, default_on_install

NB_JOBS = 8

os.chdir(os.path.dirname(os.path.realpath(__makefile__.__file__)))


def import_module(module_name: str, module_path: str = None):
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


def get_files(*patterns: str) -> set[str]:
    files = set()
    for pattern in patterns:
        files.update(glob.glob(pattern, recursive=True))
    return files


def filter_files(files: set[str], *patterns: str) -> set[str]:
    output = set()
    for file in files:
        for pattern in patterns:
            if not fnmatch.fnmatch(file, pattern):
                output.add(file)
    return output


def compile_files(files: set[str], config: Config, force: bool = False) -> set[str]:
    generated_objects: set[str] = set()
    operations: set[Operation] = set()

    for file in files:
        output_file = os.path.normpath(config.obj_build_directory + "/" + file.replace("..", "__") + config.c_compiler.obj_extension)
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        if config.c_compiler is not None:
            c_args = config.c_compiler.format_args(config.defines, config.additional_includedirs, config.c_flags + config.c_cpp_flags)
        else:
            c_args = None

        if config.cpp_compiler is not None:
            cpp_args = config.cpp_compiler.format_args(config.defines, config.additional_includedirs, config.cpp_flags + config.c_cpp_flags)
        else:
            cpp_args = None

        if file.endswith(".c"):
            if config.c_compiler is None:
                raise RuntimeError("No C compiler has been specified and the default config didn't find any")
            command = config.c_compiler.basic_compile_command(output_file, file, c_args)
        elif file.endswith(".cpp"):
            if config.cpp_compiler is None:
                raise RuntimeError("No C++ compiler has been specified and the default config didn't find any")
            command = config.cpp_compiler.basic_compile_command(output_file, file, cpp_args)
        else:
            raise ValueError("The file extension %s can't be compiled", (os.path.splitext(file)[1], ))
        operations.add(Operation(output_file, [file], config, command))

    print_lock = Lock()
    with ThreadPoolExecutor(max_workers=NB_JOBS) as executor:
        generated_objects = set(executor.map(lambda op: op.execute(force, print_lock), operations))

        if False in generated_objects:
            generated_objects = False

    return generated_objects


def archive_files(archive_name: str, object_files: set[str], config: Config):
    if config.archiver is None:
        raise RuntimeError("No archiver has been specified and the default config didn't find any")
    output_file = os.path.normpath(config.lib_build_directory + "/" + archive_name + config.archiver.static_lib_extension)
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    command = config.archiver.basic_archive_command(output_file, object_files)
    return Operation(output_file, object_files, config, command).execute()


def link_files(executable_name: str, object_files: set[str], config: Config):
    if config.linker is None:
        raise RuntimeError("No linker has been specified and the default config didn't find any")
    output_file = os.path.normpath(config.exe_build_directory + "/" + executable_name + config.linker.exe_extension)
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    command = config.linker.basic_link_command(output_file, object_files)
    return Operation(output_file, object_files, config, command).execute()