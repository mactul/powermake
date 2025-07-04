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
import json
import platform
import typing as T

from .utils import makedirs


def get_cache_dir() -> str:
    if platform.system().lower().startswith("darwin"):
        return os.path.expanduser("~/Library/Caches/powermake/")
    if platform.system().lower().startswith("win"):
        return os.path.expandvars("%LOCALAPPDATA%\\powermake\\cache")
    return os.path.expanduser("~/.cache/powermake/")


def load_cache_from_file(filepath: str) -> T.Dict[str, T.Any]:
    try:
        with open(filepath, "r") as file:
            cache = dict(json.load(file))
        if "controls" not in cache:
            return {}
        for control in cache["controls"]:
            control_filepath = control["filepath"]
            if control_filepath is None or max(os.path.getmtime(control_filepath), os.path.getctime(control_filepath)) > control["date"]:
                return {}
        return cache
    except OSError:
        return {}


def store_cache_to_file(filepath: str, cache: T.Dict[str, T.Any], *controls_filepath: str) -> None:
    controls = []
    for control_filepath in controls_filepath:
        controls.append({"filepath": control_filepath, "date": 0.0 if not os.path.exists(control_filepath) else max(os.path.getmtime(control_filepath), os.path.getctime(control_filepath))})
    cache["controls"] = controls
    makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as file:
        json.dump(cache, file, indent=4)
