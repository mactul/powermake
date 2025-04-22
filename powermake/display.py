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


import colorama
import typing as T


def init_colors() -> None:
    colorama.init()


def print_info(string: T.Any, verbosity: int, step_counter: int = 0, step_total: int = 0) -> None:
    """
    Display a string in Magenta if the verbosity is at least 1.

    Parameters
    ----------
    string : Any
        The printable object we want to display
    verbosity : int
        An integer >= 0, should be config.verbosity.
    step_counter : int, optional
        If non-zero, it's printed before the string in the format [step_counter/step_total]
    step_total : int, optional
        If `step_counter` is non-zero, [step_counter/step_total] is displayed before the string. If `step_total` is 0, it prints [step_counter/-]
    """
    if verbosity >= 1:
        if step_counter == 0:
            print(colorama.Fore.LIGHTMAGENTA_EX + str(string) + colorama.Style.RESET_ALL)
        elif step_total != 0:
            print(colorama.Fore.LIGHTMAGENTA_EX + f"[{step_counter}/{step_total}] {round(100*step_counter/step_total)}% " + str(string) + colorama.Style.RESET_ALL)
        else:
            print(colorama.Fore.LIGHTMAGENTA_EX + f"[{step_counter}/-] " + str(string) + colorama.Style.RESET_ALL)


def print_debug_info(string: T.Any, verbosity: int) -> None:
    """
    Display a string in Grey if the verbosity is at least 2.

    Parameters
    ----------
    string : T.Any
        The printable object we want to display
    verbosity : int
        An integer >= 0, should be config.verbosity.
    """
    if verbosity >= 2:
        print(colorama.Fore.LIGHTBLACK_EX + str(string) + colorama.Style.RESET_ALL)


def error_text(string: str) -> str:
    return colorama.Style.BRIGHT + colorama.Fore.RED + string + colorama.Style.RESET_ALL

def bold_text(string: T.Any) -> str:
    return colorama.Style.BRIGHT + str(string) + colorama.Style.RESET_ALL

def dim_text(string: T.Any) -> str:
    return colorama.Style.DIM + str(string) + colorama.Style.RESET_ALL