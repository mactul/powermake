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


import abc
import shutil
import typing as T


_powermake_flags_to_gnu_flags: T.Dict[str, T.List[str]] = {
    "-Wsecurity": ["-Wall", "-Wextra", "-fanalyzer", "-Wformat-security", "-Wformat", "-Wconversion", "-Wsign-conversion", "-Wtrampolines", "-Wbidi-chars=any,ucn"],
    "-fsecurity=1": ["-Wsecurity", "-fstrict-flex-arrays=2", "-fcf-protection=full", "-mbranch-protection=standard", "-Wl,-z,nodlopen", "-Wl,-z,noexecstack", "-Wl,-z,relro", "-fPIE", "-pie", "-fPIC", "-fno-delete-null-pointer-checks", "-fno-strict-overflow", "-fno-strict-aliasing", "-fexceptions", "-Wl,--as-needed", "-Wl,--no-copy-dt-needed-entries"],
    "-fsecurity=2": ["-fsecurity=1", "-D_FORTIFY_SOURCE=3", "-D_GLIBCXX_ASSERTIONS", "-fstack-clash-protection", "-fstack-protector-strong", "-Wl,-z,now", "-ftrivial-auto-var-init=zero"],
    "-fsecurity": ["-fsecurity=2"],
    "-Weverything": ["-Weverything", "-Wsecurity", "-pedantic", "-Wsuggest-attribute=pure", "-Wsuggest-attribute=const", "-Wsuggest-attribute=noreturn", "-Wsuggest-attribute=malloc", "-Wsuggest-attribute=returns_nonnull", "-Wsuggest-attribute=format", "-Wmissing-format-attribute", "-Wsuggest-attribute=cold", "-Waggregate-return", "-Wduplicated-branches", "-Wduplicated-cond", "-Wflex-array-member-not-at-end", "-Wfloat-equal", "-Wformat-nonliteral", "-Wformat-signedness", "-Wformat-y2k", "-Winit-self", "-Winvalid-utf8", "-Wjump-misses-init", "-Wlogical-op", "-Wmissing-declarations", "-Wmissing-include-dirs", "-Wmissing-prototypes", "-Wmissing-variable-declarations", "-Wmultichar", "-Wnested-externs", "-Wnull-dereference", "-Wopenacc-parallelism", "-Wredundant-decls", "-Wshadow", "-Wstack-protector", "-Wstrict-flex-arrays=3", "-Wstrict-prototypes", "-Wsuggest-final-methods", "-Wsuggest-final-types", "-Wswitch-default", "-Wundef", "-Wunsuffixed-float-constants", "-Wunused-macros", "-Wuseless-cast", "-Wvector-operation-performance", "-Wwrite-strings"],
    "-ffuzzer": ["-fsanitize=address,fuzzer"],
}


class Tool(abc.ABC):
    type: T.ClassVar = ""
    default_path: T.ClassVar = ""
    translation_dict: T.ClassVar[T.Dict[str, T.List[str]]] = _powermake_flags_to_gnu_flags

    def __init__(self, path: str) -> None:
        self._name = path
        self.verified_translation_dict: T.Dict[str, T.List[str]] = {}
        self.reload()

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

    @abc.abstractmethod
    def check_if_arg_exists(self, arg: str) -> bool:
        return False
    
    def _translate_flag(self, flag: str, output_list: T.List[str], already_translated_flags: T.List[str]) -> None:
        already_translated_flags.append(flag)

        if flag in self.verified_translation_dict:
            output_list.extend([f for f in self.verified_translation_dict[flag] if f not in output_list])
            return

        if flag not in self.translation_dict:
            # This flag is not in any translation table, we left it untouched.
            # We don't check if flag is in output_list, that should have been done before and if it's not the case, it's probably that the user enforced that
            output_list.append(flag)
            return

        self.verified_translation_dict[flag] = []

        for f in self.translation_dict[flag]:
            if f not in already_translated_flags and f in self.translation_dict:
                self._translate_flag(f, output_list, already_translated_flags)
                # after this call, self.verified_translation_dict will contain an entry for the key f, containing all flags flattened.
                self.verified_translation_dict[flag].extend(self.verified_translation_dict[f])
            else:
                if self.check_if_arg_exists(f):
                    # the flag f is valid and is not a combination of flags
                    self.verified_translation_dict[flag].append(f)
                    if f not in output_list:
                        output_list.append(f)

    def translate_flags(self, flags: T.List[str]) -> T.List[str]:
        translated_flags: T.List[str] = []
        already_translated_flags: T.List[str] = []
        for flag in flags:
            self._translate_flag(flag, translated_flags, already_translated_flags)

        return translated_flags



def load_tool_tuple_from_file(conf: T.Dict[str, T.Any], tool_name: str, object_getter: T.Callable[[str], T.Union[T.Callable[[], Tool], None]], tool_list_getter: T.Callable[[], T.Set[str]]) -> T.Union[T.Tuple[T.Union[str, None], T.Callable[[], Tool]], None]:
    if tool_name not in conf:
        return None

    if "path" in conf[tool_name] or "type" in conf[tool_name]:
        if "type" in conf[tool_name]:
            tool_type = conf[tool_name]["type"].lower()
        else:
            tool_type = "gnu"

        ObjectConstructor = object_getter(tool_type)
        if ObjectConstructor is None:
            raise ValueError("Unsupported %s type: %s\n\nShould be one of them: %s" % (tool_name, tool_type, " ".join(tool_list_getter())))

        if "path" in conf[tool_name]:
            tool_path = conf[tool_name]["path"]
        else:
            tool_path = None

        return (tool_path, ObjectConstructor)

    return None


def load_tool_from_tuple(tool_tuple: T.Union[T.Tuple[T.Union[str, None], T.Callable[[], Tool]], None], tool_name: str) -> T.Union[Tool, None]:
    if tool_tuple is not None:
        tool: Tool
        if tool_tuple[0] is None:
            tool = tool_tuple[1]()
        else:
            tool = T.cast(T.Callable[[str], Tool], tool_tuple[1])(tool_tuple[0])

        if not tool.is_available():
            if tool_tuple[0] is None:
                tool_path = tool.type
            else:
                tool_path = tool_tuple[0]
            raise ValueError("The %s %s could not be found on your machine" % (tool_name, tool_path))

        return tool
    return None


def find_tool(object_getter: T.Callable[[str], T.Union[T.Callable[[], Tool], None]], *tool_types: str) -> T.Union[Tool, None]:
    for tool_type in tool_types:
        ObjectConstructor = object_getter(tool_type)
        if ObjectConstructor is None:
            continue
        tool: Tool = ObjectConstructor()
        if tool is not None and tool.is_available():
            return tool
    return None
