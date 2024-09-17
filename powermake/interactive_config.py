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
import json

from .utils import makedirs
from .config import get_global_config
from .linkers import get_all_linker_types
from .archivers import get_all_archiver_types
from .shared_linkers import get_all_shared_linker_types
from .compilers import get_all_c_compiler_types, get_all_cpp_compiler_types, get_all_as_compiler_types, get_all_asm_compiler_types


def dp(string: str):
    if string is None:
        return "Let the program decide"
    return string


def add_tool_dict(dictionary, tool, tool_name):
    if tool[0] is not None:
        if tool_name not in dictionary:
            dictionary[tool_name] = {}
        dictionary[tool_name]["type"] = tool[0]
    if tool[1] is not None:
        if tool_name not in dictionary:
            dictionary[tool_name] = {}
        dictionary[tool_name]["path"] = tool[1]


def multiple_choices(question: str, choices: list, values: list = None):
    if values is None:
        values = choices
    assert len(choices) == len(values)

    answer = None
    while answer not in range(1, len(choices)+1):
        print("\033[H\033[2J", end="")
        print(question)
        for i in range(1, len(choices)+1):
            print(f"[{i}]: {dp(choices[i-1])}")
        answer = input(f"{' '.join([str(i) for i in range(1, len(choices)+1)])}: ")
        if answer.isnumeric():
            answer = int(answer)

    return values[answer-1]


class InteractiveConfig:
    target_architecture = None
    target_operating_system = None
    c_compiler = [None, None]
    cpp_compiler = [None, None]
    as_compiler = [None, None]
    asm_compiler = [None, None]
    archiver = [None, None]
    linker = [None, None]
    shared_linker = [None, None]

    def __init__(self, global_config: str = None, local_config: str = "./powermake_config"):
        self.global_config = global_config
        self.local_config = local_config
        answer = 0
        while answer != 4:
            choices = [
                f"Target operating system ({dp(self.target_operating_system)})",
                f"Target architecture ({dp(self.target_architecture)})",
                "Toolchain\n",
                "Save configuration"
            ]
            answer = multiple_choices("What do you want to configure ?", choices, range(1, len(choices)+1))

            if answer == 1:
                self.target_operating_system = multiple_choices("Select the target operating system", [None, "Linux", "Windows", "MacOS", "Write my own string"])
                if self.target_operating_system == "Write my own string":
                    self.target_operating_system = input("Operating System: ")
            elif answer == 2:
                self.target_architecture = multiple_choices("Select the target architecture", [None, "x86", "x64", "arm32", "arm64"])
            elif answer == 3:
                self.toolchain_menu()

        answer = multiple_choices("In which configuration do you want to write this ?", ["Local config", "Global config"], [1, 2])
        if answer == 1:
            self.save_config(local_config)
        else:
            self.save_config(global_config or get_global_config())

    def toolchain_menu(self):
        answer = 0
        choices = [
            "C compiler",
            "C++ compiler",
            "AS compiler (.s and .S files)",
            "ASM compiler (.asm files)",
            "Archiver (to make static libraries)",
            "Shared Linker (to make shared libraries)",
            "Linker\n",
            "Back to main menu"
        ]
        while answer != len(choices):
            answer = multiple_choices("What do you want to configure ?", choices, range(1, len(choices)+1))

            if answer == 1:
                self.tool_menu(self.c_compiler, "C compiler", get_all_c_compiler_types())
            elif answer == 2:
                self.tool_menu(self.cpp_compiler, "C++ compiler", get_all_cpp_compiler_types())
            elif answer == 3:
                self.tool_menu(self.as_compiler, "AS compiler", get_all_as_compiler_types())
            elif answer == 4:
                self.tool_menu(self.asm_compiler, "ASM compiler", get_all_asm_compiler_types())
            elif answer == 5:
                self.tool_menu(self.archiver, "Archiver", get_all_archiver_types())
            elif answer == 6:
                self.tool_menu(self.shared_linker, "Shared Linker", get_all_shared_linker_types())
            elif answer == 7:
                self.tool_menu(self.linker, "Linker", get_all_linker_types())

    def tool_menu(self, tool: list, tool_name: str, tool_types: list):
        answer = 0
        while answer != 3:
            choices = [
                f"{tool_name} type (what syntax) ({dp(tool[0])})",
                f"{tool_name} path ({dp(tool[1])})\n",
                "Back to toolchain menu"
            ]
            answer = multiple_choices("What do you want to configure ?", choices, range(1, len(choices)+1))

            if answer == 1:
                tool[0] = multiple_choices(f"Select the {tool_name} type", [None] + list(tool_types))
            elif answer == 2:
                print(f"Enter the path of the {tool_name} (Empty to let the program decide)")
                tool[1] = input("Path: ")
                if tool[1] == "":
                    tool[1] = None

    def save_config(self, filepath):
        config = {}
        if os.path.isfile(filepath):
            verif = 'n'
            while verif == 'n':
                answer = multiple_choices(f"Their is already a file at {filepath}\nWhat should we do ?", ["Merge", "Overwrite"], [1, 2])
                if answer == 2:
                    verif = None
                    while verif != 'y' and verif != 'n':
                        verif = input("Are you sure you want to erase all your precedent configuration ?\ny/n: ").lower()
                else:
                    verif = 'y'
            if answer == 1:
                with open(filepath, "r") as file:
                    config = json.load(file)

        if self.target_operating_system is not None:
            config["target_operating_system"] = self.target_operating_system

        if self.target_architecture is not None:
            config["target_architecture"] = self.target_architecture

        add_tool_dict(config, self.c_compiler, "c_compiler")
        add_tool_dict(config, self.cpp_compiler, "cpp_compiler")
        add_tool_dict(config, self.as_compiler, "as_compiler")
        add_tool_dict(config, self.asm_compiler, "asm_compiler")
        add_tool_dict(config, self.archiver, "archiver")
        add_tool_dict(config, self.shared_linker, "shared_linker")
        add_tool_dict(config, self.linker, "linker")

        makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as file:
            json.dump(config, file, indent=4)

        print("Configuration saved at", filepath)
