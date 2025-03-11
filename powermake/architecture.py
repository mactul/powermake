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

import shutil
import typing as T


def simplify_architecture(architecture: str) -> str:
    """
    Reduce a string representing a specific architecture to either x86, x64, arm32 or arm64

    Parameters
    ----------
    architecture : str
        A precise architecture name.

    Returns
    -------
    simplified_architecture: str
        Either x86, x64, arm32, arm64 or "" if the architecture is unknown.
    """
    arch = architecture.lower()
    if arch in ["x86", "x32", "80x86", "8086", "80386", "i286", "i386", "i486", "i586", "i686", "i786", "amd386", "am386", "amd486", "am486", "amd-k5", "amd-k6", "amd-k7"]:
        return "x86"

    if arch in ["x86_64", "x86-64", "x64", "amd64", "intel64"]:
        return "x64"

    if arch in ["arm32", "arm", "armeabi", "armv4", "armv4t", "armv5", "armv5t", "armv5te", "armv6", "armv6-m", "armv6j", "armv6k", "armv6kz", "armv6t2", "armv6z", "armv6zk", "armv6s-m", "armv7", "armv7a", "armv7s", "armv7m", "armv7r", "armv7l", "armv7-a", "armv7-m", "armv7-r", "armeabi-v7a", "armv7ve", "armv7-r", "armv7-m", "armv7e-m"]:
        return "arm32"

    if arch in ["arm64", "aarch64", "armv8", "armv8-a", "armv8.2-a", "armv8.3-a", "armv8-m", "armv8-r", "armv8.1-a", "armv8.4-a", "armv8.5-a", "armv8.6-a", "armv8-m.base", "armv8-m.main", "armv8.1-m.main", "armv9", "armv9-a", "iwmmxt", "iwmmxt2"]:
        return "arm64"

    return ""

def split_toolchain_architecture(toolchain_name: str) -> T.Tuple[T.Union[str, None], str]:
    if toolchain_name.startswith("x86_64-"):
        return ("x64", toolchain_name[len("x86_64-"):])
    if toolchain_name.startswith("amd64-"):
        return ("x64", toolchain_name[len("amd64-"):])
    if toolchain_name.startswith("i686-"):
        return ("x86", toolchain_name[len("i686-"):])
    if toolchain_name.startswith("i386-"):
        return ("x86", toolchain_name[len("i386-"):])
    if toolchain_name.startswith("aarch64-"):
        return ("arm64", toolchain_name[len("aarch64-"):])
    if toolchain_name.startswith("arm-"):
        return ("arm32", toolchain_name[len("arm-"):])
    return (None, toolchain_name)


def get_toolchain_tool(path: str) -> T.Union[str, None]:
    for tool in ("gcc", "clang", "clang++", "g++", "ar", "ld", "cc", "cpp", "cpp", "windres"):
        if path.endswith(tool):
            return tool

    return None

def search_new_toolchain(toolchain_name: str, host_architecture: str, required_architecture: str) -> T.Union[str, None]:
    """
    Search a new toolchain name that better matches the architecture than the current toolchain.

    Parameters
    ----------
    toolchain_name : str
        The actual name of the toolchain
    host_architecture : str
        the host architecture
    required_architecture : str
        the requested target architecture

    Returns
    -------
    str | None
        A new toolchain or None if none is found.
    """
    arch, toolchain_suffix = split_toolchain_architecture(toolchain_name)
    if arch == required_architecture:
        return toolchain_name

    if arch is None:
        if host_architecture in ("x64", "x86") and required_architecture in ("x64", "x86"):
            return toolchain_name
        if host_architecture == required_architecture:
            return toolchain_name

    if required_architecture == "x64":
        if shutil.which("x86_64-" + toolchain_suffix) is not None:
            return "x86_64-" + toolchain_suffix
        if shutil.which("amd64-" + toolchain_suffix) is not None:
            return "x86_64-" + toolchain_suffix

        tool = get_toolchain_tool(toolchain_suffix)
        if tool is None:
            return None
        if shutil.which("x86_64-linux-gnu-" + tool) is not None:
            return "x86_64-linux-gnu-" + tool

        return None

    if required_architecture == "x86":
        if shutil.which("i686-" + toolchain_suffix) is not None:
            return "i686-" + toolchain_suffix
        if shutil.which("i386-" + toolchain_suffix) is not None:
            return "i386-" + toolchain_suffix

        tool = get_toolchain_tool(toolchain_suffix)
        if tool is None:
            return None
        if shutil.which("i686-linux-gnu-" + tool) is not None:
            return "i686-linux-gnu-" + tool

        return None

    if required_architecture == "arm64":
        if shutil.which("aarch64-" + toolchain_suffix) is not None:
            return "aarch64-" + toolchain_suffix

        tool = get_toolchain_tool(toolchain_suffix)
        if tool is None:
            return None
        if shutil.which("aarch64-linux-gnu-" + tool) is not None:
            return "aarch64-linux-gnu-" + tool

        return None

    if required_architecture == "arm32":
        if shutil.which("arm-" + toolchain_suffix) is not None:
            return "arm-" + toolchain_suffix

        tool = get_toolchain_tool(toolchain_suffix)
        if tool is None:
            return None
        if shutil.which("arm-linux-gnueabi-" + tool) is not None:
            return "arm-linux-gnueabi-" + tool

        return None

    return None