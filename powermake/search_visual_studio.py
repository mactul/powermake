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
import ctypes
import string
import shutil
import platform
import tempfile
import subprocess
import typing as T

from .cache import load_cache_from_file, store_cache_to_file


def get_drives() -> T.List[str]:
    if platform.platform().lower().startswith("win") and hasattr(ctypes, 'windll'):
        drives = []
        bitmask = ctypes.windll.kernel32.GetLogicalDrives()
        for letter in string.ascii_uppercase:
            if bitmask & 1:
                drives.append(letter + ":\\")
            bitmask >>= 1

        return drives

    return []


vcvars = [
    "path",
    "lib",
    "libpath",
    "include",
    "DevEnvdir",
    "VSInstallDir",
    "VCInstallDir",
    "WindowsSdkDir",
    "WindowsLibPath",
    "WindowsSDKVersion",
    "WindowsSdkBinPath",
    "WindowsSdkVerBinPath",
    "ExtensionSdkDir",
    "UniversalCRTSdkDir",
    "UCRTVersion",
    "VCToolsVersion",
    "VCIDEInstallDir",
    "VCToolsInstallDir",
    "VCToolsRedistDir",
    "VisualStudioVersion",
    "VSCMD_VER",
    "VSCMD_ARG_app_plat",
    "VSCMD_ARG_HOST_ARCH",
    "VSCMD_ARG_TGT_ARCH"
]


vsvers = {
    "17.0": "2022",
    "16.0": "2019",
    "15.0": "2017",
    "14.0": "2015",
    "12.0": "2013",
    "11.0": "2012",
    "10.0": "2010",
    "9.0": "2008",
    "8.0": "2005",
    "7.1": "2003",
    "7.0": "7.0",
    "6.0": "6.0",
    "5.0": "5.0",
    "4.2": "4.2"
}


def _load_vcvarsall(vcvarsall_path: str, version: str, architecture: str) -> T.Dict[str, str]:
    tempdir = tempfile.TemporaryDirectory("powermake")
    genvcvars_filepath = os.path.join(tempdir.name, "genvcvars.bat")
    file = open(genvcvars_filepath, "w")

    file.write("@echo off\n")
    file.write("chcp 65001 > nul\n")

    if float(version) >= 16:
        file.write("set VSCMD_SKIP_SENDTELEMETRY=yes\n")

    file.write("call \"%s\" %s > nul\n" % (vcvarsall_path, architecture))

    for var in vcvars:
        file.write("echo " + var + " = %" + var + "%\n")

    file.close()

    lines = subprocess.check_output([genvcvars_filepath], encoding="ascii").split("\n")

    tempdir.cleanup()

    variables = {}
    for line in lines:
        if "=" not in line:
            continue
        key, value = line.split("=")
        key = key.strip()
        value = value.strip()

        variables[key] = value

    return variables


def _find_vcvarsall() -> T.Tuple[T.Union[str, None], T.Union[str, None]]:
    for version in vsvers:
        for logical_drive in get_drives():
            paths = []

            for prg_dir in ("Program Files (x86)", "Program Files"):
                temp_path = os.path.join(logical_drive, prg_dir, "Microsoft Visual Studio", vsvers[version])
                if not os.path.isdir(temp_path):
                    continue
                for dirname in os.listdir(temp_path):
                    if os.path.isdir(os.path.join(temp_path, dirname)):
                        paths.append(os.path.join(temp_path, dirname, "VC", "Auxiliary", "Build"))
                paths.append(os.path.join(logical_drive, prg_dir, "Microsoft Visual Studio " + version, "VC"))

            if version == "6.0":
                paths.append(os.path.join(logical_drive, "Program Files", "Microsoft Visual Studio", "VC98", "Bin"))
                paths.append(os.path.join(logical_drive, "Program Files (x86)", "Microsoft Visual Studio", "VC98", "Bin"))

            for path in paths:
                filepath = os.path.join(path, "vcvarsall.bat")
                if os.path.exists(filepath):
                    return filepath, version
                filepath = os.path.join(path, "vcvars32.bat")
                if os.path.exists(filepath):
                    return filepath, version

    return None, None


def is_msvc_loaded_correctly(env: T.Dict[str, str]) -> bool:
    for var in vcvars:
        if var not in env:
            return False
    return True


def load_msvc_environment(storage_path: str, architecture: str = "x86") -> T.Union[T.Dict[str, str], None]:
    envs = load_cache_from_file(storage_path)

    if architecture in envs and is_msvc_loaded_correctly(envs[architecture]):
        return dict(envs[architecture])

    if "vcvarsall_path" not in envs or "vcversion" not in envs:
        vcvarsall_path, vcversion = _find_vcvarsall()
        if vcvarsall_path is None:
            return None
        envs["vcvarsall_path"] = vcvarsall_path
        envs["vcversion"] = vcversion

    env = _load_vcvarsall(envs["vcvarsall_path"], envs["vcversion"], architecture)
    if env is not None:
        envs[architecture] = env
        if "path" in env:
            path = env["path"]
        else:
            path = None
    else:
        path = None

    control_filepath = shutil.which("cl.exe", path=path)
    if control_filepath is None:
        control_filepath = envs["vcvarsall_path"]

    store_cache_to_file(storage_path, envs, control_filepath)

    return env
