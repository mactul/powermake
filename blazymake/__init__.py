import os
import glob
import fnmatch
from threading import Lock
from concurrent.futures import ThreadPoolExecutor

from .config import Config
from .operation import Operation, needs_update

NB_JOBS = 8


def get_files(*patterns: str) -> list:
    files = []
    for pattern in patterns:
        files.extend(glob.glob(pattern, recursive=True))
    return files


def filter_files(files: list[str], *patterns: str) -> list:
    output = []
    for file in files:
        for pattern in patterns:
            if not fnmatch.fnmatch(file, pattern):
                output.append(file)
    return output


def compile_files(files: list[str], config: Config, force: bool = False) -> bool:
    generated_objects: list[str] | bool = []
    operations: list[Operation] = []

    for file in files:
        output_file = os.path.normpath(config.obj_build_directory + "/" + file + config.c_compiler.obj_extension)
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        if file.endswith(".c"):
            if config.c_compiler is None:
                raise RuntimeError("No C compiler has been specified and the default config didn't find any")
            command = config.c_compiler.basic_compile_command(output_file, [file], config.defines, config.additional_includedirs)
        elif file.endswith(".cpp"):
            if config.cpp_compiler is None:
                raise RuntimeError("No C++ compiler has been specified and the default config didn't find any")
            command = config.cpp_compiler.basic_compile_command(output_file, [file], config.defines, config.additional_includedirs)
        else:
            raise ValueError("The file extension %s can't be compiled", (os.path.splitext(file)[1], ))
        operations.append(Operation(output_file, [file], config, command))

    print_lock = Lock()
    with ThreadPoolExecutor(max_workers=NB_JOBS) as executor:
        generated_objects = list(executor.map(lambda op: op.execute(force, print_lock), operations))

        if False in generated_objects:
            generated_objects = False

    return generated_objects


def archive_files(archive_name: str, object_files: list[str], config: Config):
    if config.archiver is None:
        raise RuntimeError("No archiver has been specified and the default config didn't find any")
    output_file = os.path.normpath(config.lib_build_directory + "/" + archive_name + config.archiver.static_lib_extension)
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    command = config.archiver.basic_archive_command(output_file, object_files)
    return Operation(output_file, object_files, config, command).execute()


def link_files(executable_name: str, object_files: list[str], config: Config):
    if config.linker is None:
        raise RuntimeError("No linker has been specified and the default config didn't find any")
    output_file = os.path.normpath(config.exe_build_directory + "/" + executable_name + config.linker.exe_extension)
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    command = config.linker.basic_link_command(output_file, object_files)
    return Operation(output_file, object_files, config, command).execute()
