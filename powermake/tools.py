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


class Tool(abc.ABC):
    type: T.ClassVar = ""

    def __init__(self, path: str) -> None:
        self._name = path
        self.reload()

    def is_available(self) -> bool:
        return self.path is not None

    def reload(self) -> None:
        path = shutil.which(self._name)
        if path is None:
            self.path = ""
        else:
            self.path = path


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


def translate_flags(flags: T.List[str], translation_dict: T.Dict[str, T.List[str]]) -> T.List[str]:
    translated_flags = []
    for flag in flags:
        if flag in translation_dict:
            translated_flags.extend(translation_dict[flag])
        else:
            translated_flags.append(flag)

    return translated_flags
