import os
import string
import platform
import tempfile
import subprocess


if platform.platform().lower().startswith("win"):
    from ctypes import windll

    def get_drives():
        drives = []
        bitmask = windll.kernel32.GetLogicalDrives()
        for letter in string.ascii_uppercase:
            if bitmask & 1:
                drives.append(letter + ":")
            bitmask >>= 1

        return drives
else:
    def get_drives():
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

vsenvs = {
    "17.0": "VS170COMNTOOLS",
    "16.0": "VS160COMNTOOLS",
    "15.0": "VS150COMNTOOLS",
    "14.0": "VS140COMNTOOLS",
    "12.0": "VS120COMNTOOLS",
    "11.0": "VS110COMNTOOLS",
    "10.0": "VS100COMNTOOLS",
    "9.0": "VS90COMNTOOLS",
    "8.0": "VS80COMNTOOLS",
    "7.1": "VS71COMNTOOLS",
    "7.0": "VS70COMNTOOLS",
    "6.0": "VS60COMNTOOLS",
    "5.0": "VS50COMNTOOLS",
    "4.2": "VS42COMNTOOLS"
}


def _load_vcvarsall(vcvarsall_path, version, architecture):
    tempdir = tempfile.TemporaryDirectory("blazymake")
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

    lines = subprocess.check_output([genvcvars_filepath], encoding="utf-8").split("\n")

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


def find_vcvarsall():
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


def load_msvc_environment(vcvarsall_path: str = None, vcversion: str = "15.0", architecture: str = "x86"):
    if "VCInstallDir" in os.environ:
        return
    if vcvarsall_path is None:
        vcvarsall_path, vcversion = find_vcvarsall()
    if vcvarsall_path is not None:
        env = _load_vcvarsall(vcvarsall_path, vcversion, architecture)
        print(env)
        for key in env:
            os.environ[key] = env[key]
