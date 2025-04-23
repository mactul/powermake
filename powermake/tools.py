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
import shutil
import typing as T

from .utils import join_absolute_paths
from .exceptions import PowerMakeValueError
from .display import error_text, print_debug_info
from .cache import load_cache_from_file, store_cache_to_file, get_cache_dir


_powermake_flags_to_gnu_flags: T.Dict[str, T.List[str]] = {
    "-Wsecurity": ["-Wall", "-Wextra", "-fanalyzer", "-Wformat-security", "-Wformat", "-Wconversion", "-Wsign-conversion", "-Wtrampolines", "-Wbidi-chars=any,ucn"],
    "-fsecurity=1": ["-Wsecurity", "-fstrict-flex-arrays=2", "-fcf-protection=full", "-mbranch-protection=standard", "-Wl,-z,nodlopen", "-Wl,-z,noexecstack", "-Wl,-z,relro", "-fPIE", "-pie", "-fPIC", "-fno-delete-null-pointer-checks", "-fno-strict-overflow", "-fno-strict-aliasing", "-fexceptions", "-Wl,--as-needed", "-Wl,--no-copy-dt-needed-entries"],
    "-fsecurity=2": ["-fsecurity=1", "-D_FORTIFY_SOURCE=3", "-D_GLIBCXX_ASSERTIONS", "-fstack-clash-protection", "-fstack-protector-strong", "-Wl,-z,now", "-ftrivial-auto-var-init=zero"],
    "-fsecurity": ["-fsecurity=2"],
    "-Weverything": ["-Weverything", "-Wsecurity", "-pedantic", "-Wsuggest-attribute=pure", "-Wsuggest-attribute=const", "-Wsuggest-attribute=noreturn", "-Wsuggest-attribute=malloc", "-Wsuggest-attribute=returns_nonnull", "-Wsuggest-attribute=format", "-Wmissing-format-attribute", "-Wsuggest-attribute=cold", "-Waggregate-return", "-Wduplicated-branches", "-Wduplicated-cond", "-Wflex-array-member-not-at-end", "-Wfloat-equal", "-Wformat-nonliteral", "-Wformat-signedness", "-Wformat-y2k", "-Winit-self", "-Winvalid-utf8", "-Wjump-misses-init", "-Wlogical-op", "-Wmissing-declarations", "-Wmissing-include-dirs", "-Wmissing-prototypes", "-Wmissing-variable-declarations", "-Wmultichar", "-Wnested-externs", "-Wnull-dereference", "-Wopenacc-parallelism", "-Wredundant-decls", "-Wshadow", "-Wstack-protector", "-Wstrict-flex-arrays=3", "-Wstrict-prototypes", "-Wsuggest-final-methods", "-Wsuggest-final-types", "-Wswitch-default", "-Wundef", "-Wunsuffixed-float-constants", "-Wunused-macros", "-Wuseless-cast", "-Wvector-operation-performance", "-Wwrite-strings"],
    "-ffuzzer": ["-fsanitize=address,fuzzer"],
    "-fanalyzer": ["-fanalyzer"],
    "-m32": ["-m32"],
    "-m64": ["-m64"]
}


def split_toolchain_prefix(path: T.Union[str, None]) -> T.Tuple[T.Union[str, None], str]:
    if not path:
        return (None, "")
    if path.endswith("gcc"):
        return (path[:-3], "gcc")
    if path.endswith("clang"):
        return (path[:-5], "clang")
    if path.endswith("clang++"):
        return (path[:-7], "clang++")
    if path.endswith("windres"):
        return (path[:-7], "windres")
    if path.endswith("g++"):
        return (path[:-3], "g++")
    if path.endswith("ar"):
        return (path[:-2], "ar")
    if path.endswith("ld"):
        return (path[:-2], "ld")
    if path.endswith("cc"):
        return (path[:-2], "cc")
    if path.endswith("cpp"):
        return (path[:-3], "cpp")
    if path.endswith("c++"):
        return (path[:-3], "c++")

    return (None, path)

class Tool(abc.ABC):
    type: T.ClassVar = ""
    translation_dict: T.ClassVar[T.Dict[str, T.List[str]]] = _powermake_flags_to_gnu_flags

    def __init__(self, path: T.Union[str, T.List[str]]) -> None:
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

    def _translate_flag(self, flag: str, output_list: T.List[str], already_translated_flags: T.List[str]) -> bool:
        already_translated_flags.append(flag)

        if flag in self.verified_translation_dict:
            output_list.extend([f for f in self.verified_translation_dict[flag] if f not in output_list])
            return False

        if flag not in self.translation_dict:
            # This flag is not in any translation table, we left it untouched.
            # We don't check if flag is in output_list, that should have been done before and if it's not the case, it's probably that the user enforced that
            output_list.append(flag)
            return False

        self.verified_translation_dict[flag] = []

        cache_modified = False
        for f in self.translation_dict[flag]:
            if f not in already_translated_flags and f in self.translation_dict:
                self._translate_flag(f, output_list, already_translated_flags)
                # after this call, self.verified_translation_dict will contain an entry for the key f, containing all flags flattened.
                self.verified_translation_dict[flag].extend(self.verified_translation_dict[f])
            else:
                if f in self.cache["unsupported_flags"]:
                    continue
                if f not in self.cache["supported_flags"]:
                    if self.check_if_arg_exists(f):
                        self.cache["supported_flags"].append(f)
                        cache_modified = True
                    else:
                        self.cache["unsupported_flags"].append(f)
                        cache_modified = True
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
            store_cache_to_file(self.cache_file, self.cache, self.path)

        return translated_flags

    def remove_flag(self, flag: str) -> None:
        for k in self.translation_dict:
            if flag in self.translation_dict[k]:
                self.translation_dict[k].remove(flag)
        for k in self.verified_translation_dict:
            if flag in self.verified_translation_dict[k]:
                self.verified_translation_dict[k].remove(flag)

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

    def get_pref(self) -> T.Union[str, None]:
        if "CCC_ANALYZER_ANALYSIS" in os.environ:
            # This is the signature of scan-build
            # if no toolchain is specified, the auto toolchain should prefer clang
            return "clang"

        if not self.tool_path:
            return None
        if "clang-cl" in self.tool_path:
            return "clang-cl"
        if "clang" in self.tool_path:
            return "clang"
        if "mingw" in self.tool_path and "ld" in self.tool_path:
            return "mingw-ld"
        if "mingw" in self.tool_path:
            return "mingw"
        if "ld" in self.tool_path:
            return "ld"
        if "gcc" in self.tool_path or "g++" in self.tool_path:
            return "gcc"
        if "cl" in self.tool_path:
            return"msvc"
        return None


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


