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
import abc
import json
import shutil
import typing as T

from .utils import join_absolute_paths
from .exceptions import PowerMakeValueError
from .architecture import split_toolchain_prefix
from .display import error_text, warning_text, print_debug_info
from .cache import load_cache_from_file, store_cache_to_file, get_cache_dir


_powermake_flags_to_gnu_flags: T.Dict[str, T.List[str]] = {
    "-Wsecurity": ["-Wall", "-Wextra", "-fanalyzer", "-Wformat-security", "-Wformat", "-Wconversion", "-Wsign-conversion", "-Wtrampolines", "-Wbidi-chars=any,ucn"],
    "-fsecurity=1": ["-Wsecurity", "-fstrict-flex-arrays=2", "-fcf-protection=full", "-mbranch-protection=standard", "-Wl,-z,nodlopen", "-Wl,-z,noexecstack", "-Wl,-z,relro", "-fPIE", "-pie", "-fPIC", "-fno-delete-null-pointer-checks", "-fno-strict-overflow", "-fno-strict-aliasing", "-fexceptions", "-Wl,--as-needed", "-Wl,--no-copy-dt-needed-entries"],
    "-fsecurity=2": ["-fsecurity=1", "-D_FORTIFY_SOURCE=3", "-D_GLIBCXX_ASSERTIONS", "-fstack-clash-protection", "-fstack-protector-strong", "-Wl,-z,now", "-ftrivial-auto-var-init=zero"],
    "-fsecurity": ["-fsecurity=2"],
    "-Weverything": ["-Wsecurity", "-Waggregate-return", "-Walloc-zero", "-Walloca", "-Warith-conversion", "-Wbad-function-cast", "-Wc++-compat", "-Wcast-align=strict", "-Wcast-qual", "-Wdate-time", "-Wdisabled-optimization", "-Wdouble-promotion", "-Wduplicated-branches", "-Wduplicated-cond", "-Wflex-array-member-not-at-end", "-Wfloat-equal", "-Wformat-nonliteral", "-Wformat-signedness", "-Wformat-y2k", "-Winit-self", "-Winline", "-Winvalid-pch", "-Winvalid-utf8", "-Wjump-misses-init", "-Wlogical-op", "-Wmissing-declarations", "-Wmissing-format-attribute", "-Wmissing-include-dirs", "-Wmissing-prototypes", "-Wmissing-variable-declarations", "-Wmultichar", "-Wnested-externs", "-Wnull-dereference", "-Wopenacc-parallelism", "-Wpacked", "-Wpadded", "-Wredundant-decls", "-Wshadow", "-Wstack-protector", "-Wstrict-flex-arrays=3", "-Wstrict-prototypes", "-Wsuggest-attribute=cold", "-Wsuggest-attribute=const", "-Wsuggest-attribute=format", "-Wsuggest-attribute=malloc", "-Wsuggest-attribute=noreturn", "-Wsuggest-attribute=pure", "-Wsuggest-attribute=returns_nonnull", "-Wsuggest-final-methods", "-Wsuggest-final-types", "-Wswitch-default", "-Wswitch-enum", "-Wtrivial-auto-var-init", "-Wundef", "-Wunsuffixed-float-constants", "-Wunused-macros", "-Wuseless-cast", "-Wvector-operation-performance", "-Wwrite-strings", "-Wzero-as-null-pointer-constant", "-pedantic"],
    "-ffuzzer": ["-fsanitize=address,fuzzer"],
    "-m32": ["-m32"],
    "-m64": ["-m64"]
}


class EnforcedFlag(str):
    """
    This should be used with config.add_flags or config.add_XXXX_flags
    It ensure that a flag will not be translated by PowerMake and will be kept even if PowerMake think the compiler doesn't supports it
    Exemple:
    ```
    config.add_flags("-Weverything") # This will be translated on GCC
    config.add_flags(powermake.EnforcedFlag("-Weverything")) # the flag will be kept no matter what

    config.add_flags("-fegrhfevgfter") # This flag will be automatically removed with a warning, so the compilation will not fail entirely
    config.add_flags(powermake.EnforcedFlag("-fegrhfevgfter")) # make sure the flag is given to the compiler (will crash obviously)
    ```
    """
    ...


class EnforcedType(str):
    ...


class Tool(abc.ABC):
    type: T.ClassVar = ""

    def __init__(self, path: T.Union[str, T.List[str]], translation_dict: T.Union[T.Dict[str, T.List[str]], None] = None) -> None:
        if translation_dict is None:
            self.translation_dict = _powermake_flags_to_gnu_flags.copy()
        else:
            self.translation_dict = translation_dict.copy()
        self.verified_translation_dict: T.Dict[str, T.List[str]] = {}
        self.cache: T.Dict[str, T.Any] = {}
        if isinstance(path, str):
            self._name = path
            self.reload()
        else:
            for p in path:
                self._name = p
                self.reload()
                if self.is_available():
                    return

    def is_available(self) -> bool:
        return self.path != ""

    def reload(self, new_path: T.Union[str, None] = None) -> None:
        if new_path is not None:
            self._name = new_path
        path = shutil.which(self._name)
        if path is None:
            self.path = ""
        else:
            self.path = path

        self.cache_file = join_absolute_paths(os.path.join(get_cache_dir(), "compiler_flags", self.type), self.path + ".json")
        self.cache = load_cache_from_file(self.cache_file)
        if "supported_flags" not in self.cache:
            self.cache["supported_flags"] = []
        if "unsupported_flags" not in self.cache:
            self.cache["unsupported_flags"] = []

    @abc.abstractmethod
    def check_if_arg_exists(self, arg: str) -> bool:
        return False

    def _flag_exists(self, f: str) -> T.Tuple[bool, bool]:
        if f in self.cache["unsupported_flags"]:
            return (False, False)
        if f in self.cache["supported_flags"]:
            return (True, False)
        if self.check_if_arg_exists(f):
            self.cache["supported_flags"].append(f)
            return (True, True)
        self.cache["unsupported_flags"].append(f)
        return (False, True)

    def _translate_flag(self, flag: str, output_list: T.List[str], already_translated_flags: T.List[str]) -> bool:
        if isinstance(flag, EnforcedFlag):
            output_list.append(flag)
            return False

        cache_modified = False
        already_translated_flags.append(flag)

        if flag in self.verified_translation_dict:
            output_list.extend([f for f in self.verified_translation_dict[flag] if f not in output_list])
            return False

        if flag not in self.translation_dict or len(self.translation_dict[flag]) >= 2:
            valid, cache_modified = self._flag_exists(flag)
            if valid:
                self.verified_translation_dict[flag] = [flag]
                output_list.append(flag)
                return cache_modified
            elif flag not in self.translation_dict:
                # This flag is not valid and not in any translation table, we must remove it.
                self.verified_translation_dict[flag] = []
                print(warning_text(f"Warning: the flag {flag} doesn't seems supported by {self.__class__.__name__}(\"{self._name}\")\nIt has been removed, to keep it, register it as powermake.EnforcedFlag(\"{flag}\") instead of \"{flag}\""))
                return cache_modified

        self.verified_translation_dict[flag] = []

        for f in self.translation_dict[flag]:
            if f not in already_translated_flags and f in self.translation_dict:
                cache_modified = self._translate_flag(f, output_list, already_translated_flags) or cache_modified
                # after this call, self.verified_translation_dict will contain an entry for the key f, containing all flags flattened.
                self.verified_translation_dict[flag].extend(self.verified_translation_dict[f])
            else:
                valid, _cache_modified = self._flag_exists(f)
                cache_modified = _cache_modified or cache_modified
                if not valid:
                    continue
                # the flag f is valid and is not a combination of flags
                if f not in self.verified_translation_dict[flag]:
                    self.verified_translation_dict[flag].append(f)
                if f not in output_list:
                    output_list.append(f)

        return cache_modified

    def translate_flags(self, flags: T.List[str]) -> T.List[str]:
        translated_flags: T.List[str] = []
        already_translated_flags: T.List[str] = []
        cache_modified = False
        for flag in flags:
            cache_modified = self._translate_flag(flag, translated_flags, already_translated_flags) or cache_modified

        if cache_modified:
            store_cache_to_file(self.cache_file, self.cache, self.path, os.path.abspath(__file__))

        return translated_flags

    def remove_flag(self, flag: str) -> None:
        for k in self.translation_dict:
            if flag in self.translation_dict[k]:
                self.translation_dict[k].remove(flag)
        for k in self.verified_translation_dict:
            if flag in self.verified_translation_dict[k]:
                self.verified_translation_dict[k].remove(flag)

    def __str__(self) -> str:
        return f"<powermake.compilers.{self.__class__.__name__} type={json.dumps(self.type)} path={json.dumps(self.path)}>"


def construct_tool(toolchain_prefix: T.Union[str, None], ObjectConstructor: T.Callable[[], Tool]) -> Tool:
    tool = ObjectConstructor()
    if toolchain_prefix is not None:
        tool_prefixed = T.cast(T.Callable[[str], Tool], ObjectConstructor)(toolchain_prefix + split_toolchain_prefix(os.path.basename(tool._name))[1])
        if tool_prefixed.is_available():
            return tool_prefixed
    return tool


def find_tool(toolchain_prefix: T.Union[str, None], object_getter: T.Callable[[str], T.Union[T.Callable[[], Tool], None]], *tool_types: T.Union[str, None]) -> T.Union[Tool, None]:
    for tool_type in tool_types:
        if tool_type is None:
            continue
        ObjectConstructor = object_getter(tool_type)
        if ObjectConstructor is None:
            continue
        tool = construct_tool(toolchain_prefix, ObjectConstructor)
        if tool.is_available():
            return tool
    return None


class ToolPrimer:
    def __init__(self, tool_name: str, tool_env_var: T.Union[str, None], object_getter: T.Callable[[str], T.Union[T.Callable[[], Tool], None]], tool_list_getter: T.Callable[[], T.Set[str]], verbosity: int):
        self.tool_name = tool_name
        self.tool_env_var = tool_env_var
        self.object_getter = object_getter
        self.tool_list_getter = tool_list_getter
        self.tool_type: T.Union[str, None] = None
        self.tool_path: T.Union[str, None] = None
        self.tool_path_specified = False
        self.tool_type_specified = False

        if self.tool_env_var is not None:
            env_var = os.getenv(self.tool_env_var)
            if env_var is not None:
                print_debug_info(f"Using {self.tool_env_var} environment variable instead of the config", verbosity)
                self.tool_path = env_var
                self.tool_path_specified = True

    def load_conf(self, conf: T.Dict[str, T.Any]) -> None:
        if self.tool_name not in conf:
            return

        if self.tool_path is None and "path" in conf[self.tool_name]:
            self.tool_path = conf[self.tool_name]["path"]
            self.tool_path_specified = True

        if self.tool_type is None and "type" in conf[self.tool_name]:
            self.tool_type = conf[self.tool_name]["type"]
            self.tool_type_specified = True


    def get_tool(self, toolchain_prefix: T.Union[str, None] = None, *tool_types: T.Union[str, None]) -> T.Union[Tool, None]:
        if self.tool_type is None and self.tool_path is None:
            tool = find_tool(toolchain_prefix, self.object_getter, *tool_types)
            if tool is not None:
                self.tool_path = tool.path
                self.tool_type = tool.type
            return tool

        for t in tool_types:
            if t is not None and self.object_getter(t) is not None:
                self.tool_type = t
                break

        if self.tool_type is None:
            self.tool_type = "default"

        ObjectConstructor = self.object_getter(self.tool_type)
        if ObjectConstructor is None:
            raise PowerMakeValueError(error_text("Unsupported %s type: %s\n\nShould be one of them: %s" % (self.tool_name, self.tool_type, " ".join(self.tool_list_getter()))))

        if self.tool_path is None:
            tool = construct_tool(toolchain_prefix, ObjectConstructor)
        else:
            tool = T.cast(T.Callable[[str], Tool], ObjectConstructor)(self.tool_path)

        if tool is None or not tool.is_available():
            if self.tool_path is None:
                tool_path = tool.type
            else:
                tool_path = self.tool_path
            raise PowerMakeValueError(error_text("The %s %s could not be found on your machine" % (self.tool_name, tool_path)))

        return tool
