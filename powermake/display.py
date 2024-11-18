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


import colorama
import typing as T


def init_colors() -> None:
    colorama.init()


def print_info(string: T.Any, verbosity: int, counter: int = 0, total: int = 0) -> None:
    if verbosity >= 1:
        if counter == 0:
            print(colorama.Fore.LIGHTMAGENTA_EX + str(string) + colorama.Style.RESET_ALL)
        elif total != 0:
            print(colorama.Fore.LIGHTMAGENTA_EX + f"[{counter}/{total}] {round(100*counter/total)}% " + str(string) + colorama.Style.RESET_ALL)
        else:
            print(colorama.Fore.LIGHTMAGENTA_EX + f"[{counter}/-] " + str(string) + colorama.Style.RESET_ALL)


def print_debug_info(string: T.Any, verbosity: int) -> None:
    if verbosity >= 2:
        print(colorama.Fore.LIGHTBLACK_EX + str(string) + colorama.Style.RESET_ALL)


def error_text(string: str) -> str:
    return colorama.Style.BRIGHT + colorama.Fore.RED + string + colorama.Style.RESET_ALL