import os
import shutil
import tempfile
import subprocess
import typing as T

from .config import Config
from .utils import makedirs
from .display import print_info, print_debug_info
from .architecture import split_toolchain_prefix
from .cache import get_cache_dir, load_cache_from_file, check_cache_controls
from .version_parser import Version, parse_version, remove_version_frills, PreType


def git_get_server_versions(git_url: str) -> T.List[T.Tuple[str, Version]]:
    try:
        output = subprocess.check_output(["git", "ls-remote", "-t", "--refs", "-q", git_url], encoding="utf-8").split("\n")
    except subprocess.CalledProcessError:
        raise RuntimeError(f"Unable to connect to the git repository: {git_url}")

    versions = []
    for line in output:
        if "/" not in line:
            continue
        tag = line.rsplit("/", maxsplit=1)[1]
        v = parse_version(remove_version_frills(tag))
        if v is None:
            continue
        versions.append((tag, v))

    return versions


def pacman_update_db() -> bool:
    dbpath = os.path.join(get_cache_dir(), "packages", "pacman", "db")
    makedirs(dbpath)

    if shutil.which("fakeroot") is None:
        return False

    if shutil.which("pacman") is None:
        return False

    return subprocess.run(["fakeroot", "--", "pacman", "-Fy", "--dbpath", dbpath, "--logfile", "/dev/null"]).returncode == 0


def pacman_get_server_versions(libpath: str) -> T.List[T.Tuple[str, Version]]:
    dbpath = os.path.join(get_cache_dir(), "packages", "pacman", "db")

    try:
        output = subprocess.check_output(["fakeroot", "--", "pacman", "-F", libpath, "--dbpath", dbpath, "--logfile", "/dev/null"], encoding="utf-8").split("\n")
    except subprocess.CalledProcessError:
        return []

    versions = []
    for line in output:
        x = line.find("is owned by")
        if x != -1:
            package, version, *_ = line[x+12:].split(' ')
            v = parse_version(remove_version_frills(version))
            if v is None:
                continue
            versions.append((package, v))
    return versions


def pacman_get_package_installed_version(package_name: str):
    try:
        output = subprocess.check_output(["pacman", "-Qi", package_name], encoding="utf-8", stderr=subprocess.DEVNULL).split("\n")
    except subprocess.CalledProcessError:
        return None

    for line in output:
        if line.startswith("Version"):
            i = 0
            while i < len(line) and not line[i].isdigit():
                i += 1
            version = line[i:].strip()
            return parse_version(remove_version_frills(version))
    return None

def pacman_get_available_versions(libpaths: T.List[str]) -> T.List[T.Tuple[str, str, T.Union[Version, None], T.Union[Version, None]]]:
    output = []
    for libpath in libpaths:
        server_versions = pacman_get_server_versions(libpath)
        for package, server_version in server_versions:
            installed_version = pacman_get_package_installed_version(package.split('/')[-1])
            output.append((libpath, package, installed_version, server_version))
    return output


def filter_versions(versions: T.List[T.Tuple[str, Version]], min_version: T.Union[Version, None] = None, max_version: T.Union[Version, None] = None, allow_prerelease: bool = False) -> T.List[T.Tuple[str, Version]]:
    compatible_versions = []
    for v in versions:
        if (allow_prerelease or v[1].pre_type == PreType.NOT_PRE) and (min_version is None or min_version <= v[1]) and (max_version is None or v[1] <= max_version):
            compatible_versions.append(v)

    compatible_versions.sort(reverse=True, key=lambda x:x[1])
    return compatible_versions


def autocomplete_filename(dir: str, filename: str) -> str:
    files = os.listdir(dir)
    if filename in files:
        return filename
    for file in files:
        if file.startswith(filename):
            return file
    return filename


def get_possible_filepaths(config: Config, libname: str) -> T.List[str]:
    dirs = config.linker.get_lib_dirs(config.ld_flags)
    filtered_dirs = []
    for dir in dirs:
        if config.target_simplified_architecture == "x86" and "lib32" in dir:
            filtered_dirs.append(dir)
    if len(filtered_dirs) == 0:
        filtered_dirs = dirs

    filepaths = []
    for dir in filtered_dirs:
        filepaths.append(os.path.join(dir, autocomplete_filename(dir, f"lib{libname}.so")))

    return filepaths

def create_main_object(config: Config) -> T.Tuple[tempfile.TemporaryDirectory, str]:
    temp_dir = tempfile.TemporaryDirectory("powermake_test_link")
    with open(os.path.join(temp_dir.name, "main.c"), "w") as empty_main:
        empty_main.write("int main() { return 0; }")

    cmd = config.c_compiler.basic_compile_command(os.path.join(temp_dir.name, "main.o"), os.path.join(temp_dir.name, "main.c"), args=config.c_compiler.format_args([], [], config.c_flags))
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    return temp_dir, os.path.join(temp_dir.name, "main.o")

def check_linker_compat(config: Config, tempdir_name: str, main_object_path: str, libpath: str):
    cmd = config.linker.basic_link_command(os.path.join(tempdir_name, "main"), [main_object_path, libpath], args=config.linker.format_args([], config.ld_flags))
    return subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0


def truc(config: Config, libname: str, install_dir: str, min_version: T.Union[str, None] = None, max_version: T.Union[str, None] = None, allow_prerelease: bool = False, strict_post: bool = False) -> T.Tuple[str, str]:
    cache = {
        "system": [
            {
                "version": "1!3.5.2-post1",
                "lib": "/usr/lib/libssl.so",
                "include": "/usr/include/",
                "controls": [
                    {
                        "filepath": "/usr/lib/libssl.so",
                        "date": 1754818240.4226027
                    }
                ]
            },
            {
                "version": "1!3.5.2-post1",
                "lib": "/usr/lib32/libssl.so",
                "include": "/usr/include/",
                "controls": [
                    {
                        "filepath": "/usr/lib32/libssl.so",
                        "date": 1754818240.4226027
                    }
                ]
            }
        ],
        "local": [
            {
                "version": "1!3.5.2-post1",
                "arch": "arm64",
                "toolchain-prefix": "aarch64-linux-gnu-",
                "lib": "/home/mactul/Documents/libs/ssl/1!3.5.2-post1/lib/libssl.so",
                "include": "/home/mactul/Documents/libs/ssl/1!3.5.2-post1/include/",
                "controls": [
                    {
                        "filepath": "/home/mactul/Documents/libs/ssl/1!3.5.2-post1/lib/libssl.so",
                        "date": 1754818240.4226027
                    }
                ]
            }
        ]
    }
    cache = load_cache_from_file(os.path.join(get_cache_dir(), "packages", "installed", f"{libname}.json"))
    if "system" not in cache:
        cache["system"] = []
    if "local" not in cache:
        cache["local"] = []

    min_v = parse_version(min_version) if min_version is not None else None
    max_v = parse_version(max_version) if max_version is not None else None

    if not strict_post and max_v is not None and max_v.post_number is None:
        max_v.post_number = '*'

    tempdir, main_object_path = create_main_object(config)


    possible_filepaths = get_possible_filepaths(config, libname)
    if min_v is None and max_v is None:
        # If we find a compatible file installed, no need to search the version number it will be good in any case.
        for filepath in possible_filepaths:
            if os.path.exists(filepath) and check_linker_compat(config, tempdir.name, main_object_path, filepath):
                return (filepath, os.path.realpath(os.path.join(os.path.dirname(filepath), '..', 'include')))


    for entry in cache["system"]:
        if not check_cache_controls(entry):
            continue
        if entry["lib"] in possible_filepaths:
            v = parse_version(entry["version"])
            if (allow_prerelease or v.pre_type == PreType.NOT_PRE) and (min_v is None or min_v <= v) and (max_v is None or v <= max_v):
                if check_linker_compat(config, tempdir.name, main_object_path, entry["lib"]):
                    return (entry["lib"], entry["include"])

    for entry in cache["local"]:
        if not check_cache_controls(entry):
            continue
        v = parse_version(entry["version"])
        if (allow_prerelease or v.pre_type == PreType.NOT_PRE) and (min_v is None or min_v <= v) and (max_v is None or v <= max_v):
            prefix = split_toolchain_prefix(os.path.basename(config.linker.path))[0]
            if prefix is not None and prefix == entry["toolchain-prefix"] and config.target_simplified_architecture == entry["arch"]:
                if check_linker_compat(config, tempdir.name, main_object_path, entry["lib"]):
                    return (entry["lib"], entry["include"])

    install_path = os.path.join(install_dir, libname)
    if os.path.isdir(install_path):
        files = os.listdir(install_path)
        versions = []
        for filename in files:
            v = parse_version(filename)
            if v is not None:
                versions.append((filename, v))
        compatible_versions = filter_versions(versions, min_v, max_v, allow_prerelease=allow_prerelease)
        for version in compatible_versions:
            lib_dir = os.path.join(install_path, version[0], "lib")
            lib = os.path.join(lib_dir, autocomplete_filename(lib_dir, f"lib{libname}.so"))
            include = os.path.join(install_path, version[0], "include")
            if check_linker_compat(config, tempdir.name, main_object_path, lib):
                # TODO: update cache
                return (lib, include)

    print_info("Updating pacman db in a fakeroot environment", verbosity=config.verbosity)
    pacman_update_db()

    available_versions = pacman_get_available_versions(possible_filepaths)
    found = None
    installable = []
    for libpath, package, installed_version, server_version in available_versions:
        incompatible = False
        if installed_version is not None:
            # TODO: update cache
            if (found is None or found[0] < installed_version) and (allow_prerelease or installed_version.pre_type == PreType.NOT_PRE) and (min_v is None or min_v <= installed_version) and (max_v is None or installed_version <= max_v):
                if check_linker_compat(config, tempdir.name, main_object_path, libpath):
                    found = (installed_version, (libpath, os.path.realpath(os.path.join(os.path.dirname(libpath), '..', 'include'))))
                else:
                    incompatible = True
        if not incompatible and found is None and server_version is not None and (allow_prerelease or server_version.pre_type == PreType.NOT_PRE) and (min_v is None or min_v <= server_version) and (max_v is None or server_version <= max_v):
            # installed_version is not the good version but the server version might be compatible
            installable.append((package, libpath, installed_version))
    if found is not None:
        print_debug_info(f"found {libname} version {found[0]}", config.verbosity)
        return found[1]
    if len(installable) > 0:
        print("Installable packages:")
        print(installable)
        input()

    # Not a single installed or system managed package is compatible.
    # No other choice than to build from sources

    raise RuntimeError("Unable to find any package that meets the requirements.")
