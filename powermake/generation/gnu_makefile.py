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
import shlex
import typing as T

from ..__version__ import __version__
from ..config import Config
from . import _makefile_targets

MKDIR = "@mkdir -p $(@D)\n\t"


def generate_makefile(config: Config) -> None:
    aggregation_operations_counter = 0
    global_targets: T.List[str] = []

    variables = {
        "CC": "" if config.c_compiler is None else config.c_compiler.path,
        "CXX": "" if config.cpp_compiler is None else config.cpp_compiler.path,
        "AS": "" if config.as_compiler is None else config.as_compiler.path,
        "ASM": "" if config.asm_compiler is None else config.asm_compiler.path,
        "LD": "" if config.linker is None else config.linker.path,
        "SHLD": "" if config.shared_linker is None else config.shared_linker.path,
        "CFLAGS": "" if config.c_compiler is None else " ".join(config.c_compiler.format_args(config.defines, config.additional_includedirs, config.c_flags)),
        "CXXFLAGS": "" if config.cpp_compiler is None else " ".join(config.cpp_compiler.format_args(config.defines, config.additional_includedirs, config.cpp_flags)),
        "ASFLAGS": "" if config.as_compiler is None else " ".join(config.as_compiler.format_args(config.defines, config.additional_includedirs, config.as_flags)),
        "ASMFLAGS": "" if config.asm_compiler is None else " ".join(config.asm_compiler.format_args(config.defines, config.additional_includedirs, config.asm_flags)),
        "LDFLAGS": "" if config.linker is None else " ".join(config.linker.format_args(config.shared_libs, config.ld_flags)),
        "SHLDFLAGS": "" if config.shared_linker is None else " ".join(config.shared_linker.format_args(config.shared_libs, config.shared_linker_flags))
    }

    file_content = ""
    for operations in _makefile_targets:
        # operations = [(phony, target, dependencies, command, tool), ]
        target = None
        if len(operations) > 1:
            aggregation_operations_counter += 1
            target = f"_powermake_compile_files{aggregation_operations_counter}"
            global_targets.append(target)
            file_content += f""".PHONY : {target}\n{target}: {" ".join([operation[1] for operation in operations])}\n\n"""
        elif len(operations) != 0:
            global_targets.append(operations[0][1])
        for operation in operations:
            phony, target, dependencies, command, tool = operation
            if phony:
                file_content += f".PHONY : {target}\n"
            if not isinstance(command, str):
                command = shlex.join(command)
            command = command.replace(target, "$@")
            str_dependencies = " ".join(dependencies)
            if len(str_dependencies) > 0:
                command = command.replace(str_dependencies, "$^")

            if tool in variables and command.startswith(variables[tool]+" "):
                command = f"$({tool})"+command[len(variables[tool]):]

            if tool == "CC" and len(variables["CFLAGS"]) > 0:
                command = command.replace(variables["CFLAGS"], "$(CFLAGS)")
            if tool == "CXX" and len(variables["CXXFLAGS"]) > 0:
                command = command.replace(variables["CXXFLAGS"], "$(CXXFLAGS)")
            if tool == "AS" and len(variables["ASFLAGS"]) > 0:
                command = command.replace(variables["ASFLAGS"], "$(ASFLAGS)")
            if tool == "ASM" and len(variables["ASMFLAGS"]) > 0:
                command = command.replace(variables["ASMFLAGS"], "$(ASMFLAGS)")
            if tool == "LD" and len(variables["LDFLAGS"]) > 0:
                command = command.replace(variables["LDFLAGS"], "$(LDFLAGS)")
            if tool == "SHLD" and len(variables["SHLDFLAGS"]) > 0:
                command = command.replace(variables["SHLDFLAGS"], "$(SHLDFLAGS)")

            file_content += f"""{target} :{" " if len(str_dependencies) != 0 else ""}{str_dependencies}\n\t{MKDIR if not phony else ""}{command}\n\n"""

    if "build" not in global_targets:
        build_target_name = "build"
    elif "_powermake_build" not in global_targets:
        build_target_name = "_powermake_build"
    else:
        counter = 1
        while f"_powermake_build{counter}" in global_targets:
            counter += 1
        build_target_name = f"_powermake_build{counter}"

    if "clean" not in global_targets:
        file_content += f""".PHONY : clean\nclean :\n\t@rm -rf {os.path.join(config.obj_build_directory, "*")}\n\t@rm -rf {os.path.join(config.lib_build_directory, "*")}\n\t@rm -rf {os.path.join(config.exe_build_directory, "*")}\n\n"""
        if "rebuild" not in global_targets:
            file_content += f".NOTPARALLEL : rebuild\n.PHONY : rebuild\nrebuild : clean {build_target_name}\n\n"

    file_content += f""".NOTPARALLEL : {build_target_name}\n.PHONY : {build_target_name}\n{build_target_name} : {" ".join(global_targets)}"""

    file = open("Makefile", "w")
    file.write("#" * (44 + len(__version__)))
    file.write(f"\n### GNU Makefile Generated by Powermake {__version__} ###\n")
    file.write("#" * (44 + len(__version__)))
    file.write("\n\n")
    for var in variables:
        if variables[var] != "" and f"$({var})" in file_content:
            file.write(f"{var} := {variables[var]}\n")

    if "all" not in global_targets:
        all_target_name = "all"
    elif "_powermake_all" not in global_targets:
        all_target_name = "_powermake_all"
    else:
        counter = 1
        while f"_powermake_all{counter}" in global_targets:
            counter += 1
        all_target_name = f"_powermake_all{counter}"

    file.write(f"\nMAKEFLAGS += --no-print-directory --no-builtin-rules\n\n.PHONY : {all_target_name}\n{all_target_name}: {build_target_name}\n\n")
    file.write(file_content)
    file.close()