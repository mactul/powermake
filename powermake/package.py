import os
import shlex
import shutil
import tempfile
import subprocess
import typing as T

from .config import Config
from . import run_another_powermake
from .exceptions import PowerMakeRuntimeError
from .utils import makedirs, join_absolute_paths
from .architecture import split_toolchain_prefix
from .display import print_info, print_debug_info
from .version_parser import Version, parse_version, remove_version_frills, PreType
from .cache import get_cache_dir, load_cache_from_file, check_cache_controls, cache_controls_array, store_cache_to_file


class GitRepo:
    def __init__(self, git_url: str, powermake_makefile_path_in_repo: str) -> None:
        self.code_git_url = git_url
        self.dst_makefile_path = powermake_makefile_path_in_repo
        self.src_makefile_path: T.Union[str, None] = None
        self.makefile_git_url: T.Union[str, None] = None

    def set_external_powermake_makefile(self, powermake_makefile_path: str, git_url: T.Union[str, None]) -> None:
        self.src_makefile_path = powermake_makefile_path
        self.makefile_git_url = git_url

    def get_server_versions(self) -> T.List[T.Tuple[str, Version]]:
        try:
            output = subprocess.check_output(["git", "ls-remote", "-t", "--refs", "-q", self.code_git_url], encoding="utf-8").split("\n")
        except subprocess.CalledProcessError:
            raise PowerMakeRuntimeError(f"Unable to connect to the git repository: {self.code_git_url}")

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

    def download_build_install(self, config: Config, install_path: str, tag: T.Union[str, None] = None) -> None:
        temp_dir = tempfile.TemporaryDirectory("_powermake_build")
        if tag is None:
            cmd = ["git", "clone", "--progress", "--recursive", "--depth=1", "--single-branch", self.code_git_url, temp_dir.name]
        else:
            cmd = ["git", "clone", "--progress", "--recursive", "--depth=1", "--branch", tag, "--single-branch", self.code_git_url, temp_dir.name]

        if subprocess.run(cmd).returncode != 0:
            raise PowerMakeRuntimeError(f"Unable to connect to the git repository: {self.code_git_url}")

        if self.src_makefile_path is not None:
            makedirs(os.path.join(temp_dir.name, os.path.dirname(self.dst_makefile_path)))
            shutil.copy(self.src_makefile_path, os.path.join(temp_dir.name, self.dst_makefile_path))

        run_another_powermake(config, join_absolute_paths(temp_dir.name, os.path.normpath(os.path.join("/", self.dst_makefile_path))), rebuild=True, command_line_args=["--install", install_path])

        temp_dir.cleanup()


class DefaultGitRepos(GitRepo):
    _preconfigured_repos: T.Dict[str, T.Tuple[str, str, T.Union[str, None], T.Union[str, None]]] = {
        "SDL3": ("https://github.com/libsdl-org/SDL.git", "build/makefile.py", "https://github.com/mactul/powermake-repos.git", "generic/cmake/cmake_makefile.py")
    }
    def __init__(self) -> None:
        self.libname: T.Union[str, None] = None
        super().__init__("", "")

    def set_libname(self, libname: str) -> None:
        if libname not in self._preconfigured_repos:
            self.libname = None
            return
        self.libname = libname
        self.code_git_url, self.dst_makefile_path, self.makefile_git_url, self.src_makefile_path = self._preconfigured_repos[libname]

    def get_server_versions(self) -> T.List[T.Tuple[str, Version]]:
        if self.libname is None:
            return []
        return super().get_server_versions()


_privilege_escalator: T.Union[None, T.List[str]] = None
def escalate_command(command: T.List[str], pref: T.Union[None, T.List[str]] = None) -> T.Union[None, T.List[str]]:
    global _privilege_escalator

    if os.getuid() == 0:
        return []

    if _privilege_escalator is None:
        for auth in (pref, ["pkexec"], ["run0", "--background="], ["sudo"], ["doas"], ["su", "-c"]):
            if auth is None:
                continue
            if shutil.which(auth[0]) is not None:
                _privilege_escalator = auth
                break

    if _privilege_escalator is None:
        return None

    if _privilege_escalator[0] == "su":
        return [*_privilege_escalator, shlex.join(command)]
    return [*_privilege_escalator, *command]



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


def pacman_get_package_installed_version(package_name: str) -> T.Union[Version, None]:
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

def pacman_get_available_versions(libpaths: T.List[str]) -> T.List[T.Tuple[str, str, T.Union[Version, None], Version]]:
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
    if config.linker is None:
        return []
    dirs = config.linker.get_lib_dirs(config.ld_flags)
    filtered_dirs: T.Set[str] = set()
    for dir in dirs:
        if config.target_simplified_architecture == "x86" and "lib32" in dir:
            filtered_dirs.add(dir)
    if len(filtered_dirs) == 0:
        filtered_dirs = dirs

    filepaths = []
    for dir in filtered_dirs:
        filepaths.append(os.path.join(dir, autocomplete_filename(dir, f"lib{libname}.so")))

    return filepaths

def create_main_object(config: Config) -> T.Tuple[tempfile.TemporaryDirectory[str], str]:
    compiler = None
    flags: T.List[T.Union[str, T.Tuple[str, ...]]] = []
    if config.c_compiler is not None:
        compiler = config.c_compiler
        flags = config.c_flags
    elif config.cpp_compiler is not None:
        compiler = config.cpp_compiler
        flags = config.cpp_flags

    if compiler is None:
        raise PowerMakeRuntimeError("No C or C++ compiler were found, we need one to check a lib compatibility")

    temp_dir = tempfile.TemporaryDirectory("_powermake_test_link")
    with open(os.path.join(temp_dir.name, "main.c"), "w") as empty_main:
        empty_main.write("int main() { return 0; }")

    cmd = compiler.basic_compile_command(os.path.join(temp_dir.name, "main.o"), os.path.join(temp_dir.name, "main.c"), args=compiler.format_args([], [], flags))
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    return temp_dir, os.path.join(temp_dir.name, "main.o")

def check_linker_compat(config: Config, tempdir_name: str, main_object_path: str, libpath: str) -> bool:
    if config.linker is None:
        raise PowerMakeRuntimeError("No linker was found, we need one to check a lib compatibility")
    cmd = config.linker.basic_link_command(os.path.join(tempdir_name, "main"), [main_object_path, libpath], args=config.linker.format_args([], config.ld_flags))
    return subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0


def save_cache(cache_filepath: str, cache: T.Dict[str, T.Any]) -> None:
    new_cache: T.Dict[str, T.Any] = {
        "system": [],
        "local": []
    }
    for entry in cache["system"]:
        if "invalid" not in entry:
            new_cache["system"].append(entry)

    for entry in cache["local"]:
        if "invalid" not in entry:
            new_cache["local"].append(entry)

    store_cache_to_file(cache_filepath, cache)


def _find_lib_with_pacman(possible_filepaths: T.List[str], tempdir_name: str, main_object_path: str, cache: T.Dict[str, T.Any], config: Config, min_version: T.Union[Version, None] = None, max_version: T.Union[Version, None] = None, allow_prerelease: bool = False) -> T.Union[T.Tuple[bool, str, str, T.Union[Version, None]], None]:
    cache_modified = False

    print_info("Updating pacman db in a fakeroot environment", verbosity=config.verbosity)
    pacman_update_db()

    available_versions = pacman_get_available_versions(possible_filepaths)
    found = None
    installable = []
    upgradable = []
    for libpath, package, installed_version, server_version in available_versions:
        incompatible = False
        if installed_version is not None:
            include = os.path.realpath(os.path.join(os.path.dirname(libpath), '..', 'include'))
            # update cache
            cache["system"].append({
                "version": str(installed_version),
                "lib": libpath,
                "include": include,
                "controls": cache_controls_array(libpath)
            })
            cache_modified = True
            if (found is None or found[2] < installed_version) and (allow_prerelease or installed_version.pre_type == PreType.NOT_PRE) and (min_version is None or min_version <= installed_version) and (max_version is None or installed_version <= max_version):
                if check_linker_compat(config, tempdir_name, main_object_path, libpath):
                    found = (libpath, include, installed_version)
                else:
                    incompatible = True
        if not incompatible and found is None and server_version is not None and (allow_prerelease or server_version.pre_type == PreType.NOT_PRE) and (min_version is None or min_version <= server_version) and (max_version is None or server_version <= max_version):
            # installed_version is not the good version but the server version might be compatible
            if installed_version is None:
                installable.append((package, libpath, server_version))
            else:
                upgradable.append((package, libpath, installed_version, server_version))

    if found is not None:
        return (cache_modified, *found)

    cmd = None
    if len(installable) > 0 or len(upgradable) > 0:
        if len(upgradable) > 0:
            if len(upgradable) > 1:
                text = "The packages "
                for u in upgradable[:-1]:
                    text += u[0] + ", "
                text = text[:-2] + " and " + upgradable[-1][0]
                print(text, "are upgradable to a version that will satisfy your requirements.")
            else:
                print(f"The package {upgradable[0][0]} is installed with the incompatible version {upgradable[0][2]} but can be upgraded to the version {upgradable[0][3]}")
            print("Do you want to upgrade your entire system ? (will run `pacman -Syu` as root)")
            answer = input("[Y/n] ")
            if answer == "" or answer == "y" or answer == "Y":
                cmd = escalate_command(["pacman", "-Syu"])
            else:
                cmd = []
        else:
            if len(installable) > 1:
                print("Multiple packages that might be compatible were found.")
                print("Do you want to install one of them ? (will run `pacman -S <package>` as root)")
                print("0: None of them")
                for i in range(len(installable)):
                    print(f"{i+1}: {installable[i][0]}, version {installable[i][2]}, providing {installable[i][1]}")
                answer = ""
                while not answer.isdigit() or int(answer) < 0 or int(answer) > len(installable):
                    answer = input(f"[0-{len(installable)}] ")
                if answer != "0":
                    cmd = escalate_command(["pacman", "-S", installable[int(answer)-1][0]])
                else:
                    cmd = []
            else:
                print(f"The package {installable[0][0]}, version {installable[0][2]}, providing {installable[0][1]} might be compatible.")
                print(f"Do you want to install it ? (will run `pacman -S {shlex.quote(installable[0][0])}` as root)")
                answer = input("[Y/n] ")
                if answer == "" or answer == "y" or answer == "Y":
                    cmd = escalate_command(["pacman", "-S", installable[0][0]])
                else:
                    cmd = []

        if cmd is None:
            print("No tool was found to escalate to root.")
            print("If you have a root access, install the package mentioned above manually and then enter 1.")
            print("If you don't have a root access, enter 2.")
            print("1: You have installed the package manually, proceed as if it's installed.")
            print("2: Continue without root access and install from sources.")
            answer = ""
            while answer not in ("1", "2"):
                answer = input("[1/2] ")
            # if answer is 1, cmd will be left to None and the lib will be checked for installation later
            if answer == "2":
                cmd = []

        if cmd is not None and len(cmd) > 0:
            print_info("Running pacman as root", verbosity=config.verbosity)
            print_debug_info(cmd, verbosity=config.verbosity)
            if subprocess.run(cmd).returncode != 0:
                raise PowerMakeRuntimeError("Unable to run pacman as root")

        if cmd is None or len(cmd) > 0:
            found = None
            available_versions = pacman_get_available_versions(possible_filepaths)
            found = None
            for libpath, package, installed_version, server_version in available_versions:
                if installed_version is not None:
                    include = os.path.realpath(os.path.join(os.path.dirname(libpath), '..', 'include'))
                    # update cache
                    already_in_cache = False
                    for entry in cache["system"]:
                        if "invalid" not in entry and parse_version(entry["version"]) == installed_version and entry["lib"] == libpath:
                            already_in_cache = True
                            break
                    if not already_in_cache:
                        cache["system"].append({
                            "version": str(installed_version),
                            "lib": libpath,
                            "include": include,
                            "controls": cache_controls_array(libpath)
                        })
                        cache_modified = True
                    if (found is None or found[2] < installed_version) and (allow_prerelease or installed_version.pre_type == PreType.NOT_PRE) and (min_version is None or min_version <= installed_version) and (max_version is None or installed_version <= max_version):
                        if check_linker_compat(config, tempdir_name, main_object_path, libpath):
                            found = (libpath, include, installed_version)
            if found is not None:
                return (cache_modified, *found)

    return None


def _find_lib(cache: T.Dict[str, T.Any], config: Config, libname: str, install_dir: str, git_repo: T.Union[GitRepo, None] = DefaultGitRepos(), min_version: T.Union[Version, None] = None, max_version: T.Union[Version, None] = None, allow_prerelease: bool = False, disable_system_packages: bool = False) -> T.Tuple[bool, str, str, T.Union[Version, None]]:
    cache_modified = False

    if "system" not in cache:
        cache["system"] = []
    if "local" not in cache:
        cache["local"] = []

    tempdir, main_object_path = create_main_object(config)


    possible_filepaths = get_possible_filepaths(config, libname)
    if not disable_system_packages and min_version is None and max_version is None:
        # If we find a compatible file installed, no need to search the version number it will be good in any case.
        for filepath in possible_filepaths:
            if os.path.exists(filepath) and check_linker_compat(config, tempdir.name, main_object_path, filepath):
                return (cache_modified, filepath, os.path.realpath(os.path.join(os.path.dirname(filepath), '..', 'include')), None)

    if config.linker is None:
        raise PowerMakeRuntimeError("No linker was found, we need one to check a lib compatibility")

    current_toolchain_prefix = split_toolchain_prefix(os.path.basename(config.linker.path))[0]
    if current_toolchain_prefix is None:
        current_toolchain_prefix = os.path.basename(config.linker.path)

    if len(current_toolchain_prefix) == 0:
        current_toolchain_prefix = "generic"

    if not disable_system_packages:
        for entry in cache["system"]:
            if not check_cache_controls(entry):
                entry["invalid"] = True
                cache_modified = True
                continue
            if entry["lib"] in possible_filepaths:
                v = parse_version(entry["version"])
                if v is None:
                    continue
                if (allow_prerelease or v.pre_type == PreType.NOT_PRE) and (min_version is None or min_version <= v) and (max_version is None or v <= max_version):
                    if check_linker_compat(config, tempdir.name, main_object_path, entry["lib"]):
                        return (cache_modified, entry["lib"], entry["include"], v)

    for entry in cache["local"]:
        if not check_cache_controls(entry):
            entry["invalid"] = True
            cache_modified = True
            continue
        v = parse_version(entry["version"])
        if v is None:
            continue
        if (allow_prerelease or v.pre_type == PreType.NOT_PRE) and (min_version is None or min_version <= v) and (max_version is None or v <= max_version):
            if current_toolchain_prefix is not None and current_toolchain_prefix == entry["toolchain-prefix"] and config.target_simplified_architecture == entry["arch"]:
                if check_linker_compat(config, tempdir.name, main_object_path, entry["lib"]):
                    return (cache_modified, entry["lib"], entry["include"], v)

    install_path = os.path.join(install_dir, config.target_simplified_architecture, current_toolchain_prefix, libname)
    if os.path.isdir(install_path):
        files = os.listdir(install_path)
        versions = []
        for filename in files:
            v = parse_version(filename)
            if v is not None:
                versions.append((filename, v))
        compatible_versions = filter_versions(versions, min_version, max_version, allow_prerelease=allow_prerelease)
        for version in compatible_versions:
            lib_dir = os.path.join(install_path, version[0], "lib")
            if not os.path.exists(lib_dir):
                continue
            lib = os.path.join(lib_dir, autocomplete_filename(lib_dir, f"lib{libname}.so"))
            include = os.path.join(install_path, version[0], "include")
            if check_linker_compat(config, tempdir.name, main_object_path, lib):
                # update cache
                cache["local"].append({
                    "version": str(version[1]),
                    "arch": config.target_simplified_architecture,
                    "toolchain-prefix": current_toolchain_prefix,
                    "lib": lib,
                    "include": include,
                    "controls": cache_controls_array(lib)
                })
                return (True, lib, include, version[1])

    if not disable_system_packages:
        pacman_result = _find_lib_with_pacman(possible_filepaths, tempdir.name, main_object_path, cache, config, min_version, max_version, allow_prerelease)
        if pacman_result is not None:
            cache_modified_by_pacman, lib, include, lib_version = pacman_result
            if cache_modified_by_pacman:
                cache_modified = True
            return cache_modified, lib, include, lib_version

    # Not a single installed or system managed package is compatible.
    # No other choice than to build from sources

    if git_repo is None:
        raise PowerMakeRuntimeError("Unable to find any package that meets the requirements.")

    if isinstance(git_repo, DefaultGitRepos):
        git_repo.set_libname(libname)

    compatible_versions = filter_versions(git_repo.get_server_versions(), min_version, max_version, allow_prerelease)
    if len(compatible_versions) > 0:
        builded_version = compatible_versions[0][1]
        builded_version_str = str(compatible_versions[0][1])
        lib_installed_path = os.path.join(install_path, builded_version_str)
        git_repo.download_build_install(config, lib_installed_path, compatible_versions[0][0])
    elif min_version is None and max_version is None:
        builded_version = None
        builded_version_str = "no_version"
        lib_installed_path = os.path.join(install_path, builded_version_str)
        git_repo.download_build_install(config, lib_installed_path)
    else:
        raise PowerMakeRuntimeError("Unable to find any package that meets the requirements.")

    lib = os.path.join(lib_installed_path, "lib")
    if not os.path.isdir(lib):
        raise PowerMakeRuntimeError("Unable to find any package that meets the requirements.")
    files = os.listdir(lib)
    includedirs_to_copy = set()
    includedir = os.path.join(lib_installed_path, "include")
    chosen_lib = ""
    for file in files:
        name = file.split('.')[0]
        if name.startswith("lib"):
            name = name[3:]
        if name != libname:
            if os.path.isfile(os.path.join(lib, file)):
                path = os.path.join(install_dir, config.target_simplified_architecture, current_toolchain_prefix, name, builded_version_str)
                makedirs(os.path.join(path, "lib"))
                includedirs_to_copy.add(os.path.join(path, "include"))
                shutil.move(os.path.join(lib, file), os.path.join(path, "lib", file))
        else:
            if chosen_lib == "":
                chosen_lib = file
            elif file == f"lib{libname}.a":
                chosen_lib = file
            elif chosen_lib != f"lib{libname}.a" and file == f"lib{libname}.so":
                chosen_lib = file
    for dir in includedirs_to_copy:
        shutil.copytree(includedir, dir, dirs_exist_ok=True)

    if chosen_lib == "":
        files = os.listdir(lib)
        if len(files) == 0:
            raise PowerMakeRuntimeError("Unable to find any package that meets the requirements.")
        chosen_lib = files[0]

    return cache_modified, os.path.join(lib, chosen_lib), includedir, builded_version



def find_lib(config: Config, libname: str, install_dir: str, git_repo: T.Union[GitRepo, None] = DefaultGitRepos(), min_version: T.Union[str, None] = None, max_version: T.Union[str, None] = None, allow_prerelease: bool = False, strict_post: bool = False, disable_system_packages: bool = False) -> T.Tuple[str, str, T.Union[Version, None]]:
    # Cache structure example:
    # =======================================================
    # cache = {
    #     "system": [
    #         {
    #             "version": "1!3.5.2-post1",
    #             "lib": "/usr/lib/libssl.so",
    #             "include": "/usr/include/",
    #             "controls": [
    #                 {
    #                     "filepath": "/usr/lib/libssl.so",
    #                     "date": 1754818240.4226027
    #                 }
    #             ]
    #         },
    #         {
    #             "version": "1!3.5.2-post1",
    #             "lib": "/usr/lib32/libssl.so",
    #             "include": "/usr/include/",
    #             "controls": [
    #                 {
    #                     "filepath": "/usr/lib32/libssl.so",
    #                     "date": 1754818240.4226027
    #                 }
    #             ]
    #         }
    #     ],
    #     "local": [
    #         {
    #             "version": "1!3.5.2-post1",
    #             "arch": "arm64",
    #             "toolchain-prefix": "aarch64-linux-gnu-",
    #             "lib": "/home/mactul/Documents/libs/arm64/aarch64-linux-gnu-/ssl/1!3.5.2-post1/lib/libssl.so",
    #             "include": "/home/mactul/Documents/libs/arm64/aarch64-linux-gnu-/ssl/1!3.5.2-post1/include/",
    #             "controls": [
    #                 {
    #                     "filepath": "/home/mactul/Documents/libs/arm64/aarch64-linux-gnu-/ssl/1!3.5.2-post1/lib/libssl.so",
    #                     "date": 1754818240.4226027
    #                 }
    #             ]
    #         }
    #     ]
    # }
    cache_filepath = os.path.join(get_cache_dir(), "packages", "installed", f"{libname}.json")
    cache = load_cache_from_file(cache_filepath)

    min_v = parse_version(min_version) if min_version is not None else None
    max_v = parse_version(max_version) if max_version is not None else None
    if not strict_post and max_v is not None and max_v.post_number is None:
        max_v.post_number = '*'

    cache_modified, lib, include, version = _find_lib(cache, config, libname, install_dir, git_repo, min_v, max_v, allow_prerelease, disable_system_packages)
    if cache_modified:
        save_cache(cache_filepath, cache)

    return lib, include, version