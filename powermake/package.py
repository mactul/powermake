import os
import re
import shlex
import shutil
import tempfile
import subprocess
import typing as T
from enum import Enum

from .config import Config
from .operation import run_command
from . import run_another_powermake
from .exceptions import PowerMakeRuntimeError
from .utils import makedirs, join_absolute_paths
from .architecture import split_toolchain_prefix
from .display import print_info, print_debug_info
from .version_parser import Version, parse_version, remove_version_frills, PreType
from .cache import get_cache_dir, load_cache_from_file, check_cache_controls, cache_controls_array, store_cache_to_file


class ExtType(Enum):
    LIB_A = "\\.a"
    "Files ending with .a (ex: libssl.a)"
    LIB_SO = "\\.so"
    "Files ending with .so (ex: libssl.so)"
    LIB_SO_NUM = "\\.so(?:\\.[0-9]+)+"
    "Files ending with .so.X.X... (ex: libssl.so.2)"
    LIB_DLL_A = "\\.dll\\.a"
    "Files ending with .dll.a (ex: libssl.dll.a)"
    LIB_LIB = "\\.lib"
    "Files ending with .lib (ex: ssl.lib)"
    LIB_DLL = "\\.dll"
    "Files ending with .dll (ex: ssl.dll)"

DEFAULT_EXT_PREF_ORDER = [ExtType.LIB_A, ExtType.LIB_SO, ExtType.LIB_SO_NUM, ExtType.LIB_DLL_A, ExtType.LIB_LIB, ExtType.LIB_DLL]


class GitRepo:
    def __init__(self, git_url: str, powermake_makefile_path_in_repo: str) -> None:
        self.code_git_url = git_url
        self.dst_makefile_path = powermake_makefile_path_in_repo
        self.src_makefile_path: T.Union[str, None] = None
        self.makefile_git_url: T.Union[str, None] = None
        self.tags_to_exclude: T.Tuple[str, ...] = tuple()

    def set_external_powermake_makefile(self, powermake_makefile_path: str, git_url: T.Union[str, None]) -> None:
        self.src_makefile_path = powermake_makefile_path
        self.makefile_git_url = git_url

    def set_tags_to_exclude(self, *regex: str) -> None:
        self.tags_to_exclude = regex

    def _is_tag_excluded(self, tag: str) -> bool:
        for regex in self.tags_to_exclude:
            if re.fullmatch(regex, tag):
                return True
        return False

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
            if self._is_tag_excluded(tag):
                continue
            v = parse_version(remove_version_frills(tag))
            if v is None:
                continue
            versions.append((tag, v))

        return versions

    def download_build_install(self, config: Config, install_path: str, tag: T.Union[str, None] = None) -> None:
        print(f"Do you want to download {self.code_git_url} ? It will be compiled and installed in: {install_path}")
        answer = "a"
        while answer != "" and answer != "y" and answer != "Y" and answer != "n" and answer != "N":
            answer = input("[Y/n] ")
        if answer != "" and answer != "y" and answer != "Y":
            raise PowerMakeRuntimeError("Unable to find any package that meets the requirements.")

        temp_dir = tempfile.TemporaryDirectory("_powermake_build")
        if tag is None:
            cmd = ["git", "clone", "--progress", "--recursive", "--depth=1", "--single-branch", self.code_git_url, temp_dir.name]
        else:
            cmd = ["git", "clone", "--progress", "--recursive", "--depth=1", "--branch", tag, "--single-branch", self.code_git_url, temp_dir.name]

        if run_command(config, cmd) != 0:
            raise PowerMakeRuntimeError(f"Unable to connect to the git repository: {self.code_git_url}")

        if self.makefile_git_url is not None and self.src_makefile_path is not None:
            makefile_temp_dir = tempfile.TemporaryDirectory("_powermake_makefile_repo")
            if run_command(config, ["git", "clone", "--progress", "--recursive", "--depth=1", "--single-branch", self.makefile_git_url, makefile_temp_dir.name]) != 0:
                raise PowerMakeRuntimeError(f"Unable to connect to the git repository: {self.makefile_git_url}")
            self.src_makefile_path = os.path.join(makefile_temp_dir.name, self.src_makefile_path)

        if self.src_makefile_path is not None:
            makedirs(os.path.join(temp_dir.name, os.path.dirname(self.dst_makefile_path)))
            shutil.copy(self.src_makefile_path, os.path.join(temp_dir.name, self.dst_makefile_path))

        run_another_powermake(config, join_absolute_paths(temp_dir.name, os.path.normpath(os.path.join("/", self.dst_makefile_path))), rebuild=True, debug=False, command_line_args=["--install", install_path])

        lib_path = os.path.join(install_path, "lib")
        if not os.path.exists(lib_path):
            if os.path.exists(os.path.join(install_path, "lib32")):
                os.symlink(os.path.join(install_path, "lib32"), lib_path, target_is_directory=True)
            elif os.path.exists(os.path.join(install_path, "lib64")):
                os.symlink(os.path.join(install_path, "lib64"), lib_path, target_is_directory=True)
            else:
                raise PowerMakeRuntimeError("The library was compiled and installed but no lib folder was found")

        temp_dir.cleanup()
        makefile_temp_dir.cleanup()


class DefaultGitRepos(GitRepo):
    _default_packages = {
        "SDL2": "SDL",
        "SDL3": "SDL",
        "SDL2_ttf": "SDL_ttf",
        "SDL3_ttf": "SDL_ttf",
        "ssl": "openssl",
        "crypto": "openssl",
        "jpeg": "libjpeg-turbo",
        "turbojpeg": "libjpeg-turbo",
        "png": "libpng",
        "zip": "libzip",
        "glfw3": "glfw",
        "mariadb": "mariadb-connector-c"
    }
    _preconfigured_repos: T.Dict[str, T.Tuple[str, str, T.Union[str, None], T.Union[str, None], T.Tuple[str, ...]]] = {
        "SDL": ("https://github.com/libsdl-org/SDL.git", "build/makefile.py", "https://github.com/mactul/powermake-repos.git", "generic/cmake/cmake_makefile.py", tuple()),
        "SDL_ttf": ("https://github.com/libsdl-org/SDL_ttf.git", "build/makefile.py", "https://github.com/mactul/powermake-repos.git", "generic/cmake/cmake_makefile.py", tuple()),
        "boringssl": ("https://boringssl.googlesource.com/boringssl", "build/makefile.py", "https://github.com/mactul/powermake-repos.git", "generic/cmake/cmake_makefile.py", ("fips.*", "version.*")),
        "libressl": ("https://github.com/libressl/portable.git", "build/makefile.py", "https://github.com/mactul/powermake-repos.git", "generic/cmake/autogen_cmake_makefile.py", tuple()),
        "openssl": ("https://github.com/openssl/openssl.git", "makefile.py", "https://github.com/mactul/powermake-repos.git", "o/openssl/openssl_makefile.py", (".*fips.*", ".*FIPS.*", ".*engine.*", ".*SSLeay.*")),
        "libjpeg-turbo": ("https://github.com/libjpeg-turbo/libjpeg-turbo", "build/makefile.py", "https://github.com/mactul/powermake-repos.git", "generic/cmake/cmake_makefile.py", ("jpeg.*", )),
        "libpng": ("https://github.com/pnggroup/libpng", "build/makefile.py", "https://github.com/mactul/powermake-repos.git", "generic/cmake/cmake_makefile.py", (".*png.*", ".*master.*")),
        "libzip": ("https://github.com/nih-at/libzip", "build/makefile.py", "https://github.com/mactul/powermake-repos.git", "generic/cmake/cmake_makefile.py", (".*brian.*", )),
        "glfw": ("https://github.com/glfw/glfw.git", "build/makefile.py", "https://github.com/mactul/powermake-repos.git", "generic/cmake/cmake_makefile.py", tuple()),
        "json-c": ("https://github.com/json-c/json-c.git", "build/makefile.py", "https://github.com/mactul/powermake-repos.git", "j/json-c/json-c_makefile.py", tuple()),
        "mariadb-connector-c": ("https://github.com/mariadb-corporation/mariadb-connector-c.git", "build/makefile.py", "https://github.com/mactul/powermake-repos.git", "m/mariadb/mariadb_makefile.py", (".*MS.*", ".*py.*")),
    }

    def __init__(self) -> None:
        self.libname: T.Union[str, None] = None
        super().__init__("", "")

    def set_libname(self, libname: str, package_name: T.Union[str, None]) -> None:
        if package_name is None:
            if libname in self._default_packages:
                package_name = self._default_packages[libname]
            else:
                package_name = libname

        if package_name not in self._preconfigured_repos:
            self.libname = None
            return

        self.libname = libname
        self.code_git_url, self.dst_makefile_path, self.makefile_git_url, self.src_makefile_path, self.tags_to_exclude = self._preconfigured_repos[package_name]

    def get_server_versions(self) -> T.List[T.Tuple[str, Version]]:
        if self.libname is None:
            raise PowerMakeRuntimeError("Unable to find any package that meets the requirements.")
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


# def autocomplete_filename(dir: str, filename: str) -> str:
#     files = os.listdir(dir)
#     if filename in files:
#         return filename
#     for file in files:
#         if file.startswith(filename):
#             return file
#     return filename


def remove_version_ext(ext: str) -> str:
    i = len(ext) - 1
    while i > 0 and (ext[i].isdigit() or ext[i] == '.'):
        i -= 1
    if i <= 0:
        return ""
    return ext[:i+1]


def search_lib(dir: str, libname: str, get_non_match: bool = True, ext_pref_order: T.List[ExtType] = DEFAULT_EXT_PREF_ORDER) -> T.Tuple[T.List[str], T.Dict[str, T.Set[str]]]:
    chosen_libs: T.List[T.Tuple[bool, int, str]] = []
    non_match: T.Dict[str, T.Set[str]] = {}
    name_references: T.Dict[str, T.Set[str]] = {}
    files_parsed: T.Dict[str, T.Tuple[bool, str, str]] = {}

    try:
        files = os.listdir(dir)
    except FileNotFoundError:
        return [], {}

    regex = re.compile(f"(.+)({'|'.join({x.value for x in ext_pref_order}.union({x.value for x in ExtType}))})", re.IGNORECASE)
    for file in files:
        if file.startswith("lib"):
            lib_prefix = True
            name = file[3:]
        else:
            lib_prefix = False
            name = file
        search = regex.fullmatch(name)
        if search is None:
            # Not a lib
            continue
        name = str(search.group(1))
        ext = str(search.group(2))
        if name.endswith(".dll") and ext == ".a":
            name = name[:-4]
            if len(name) == 0:
                # Not a lib
                continue
            ext = ".dll" + ext

        files_parsed[file] = (lib_prefix, name, ext)

        base_file = os.path.basename(os.path.realpath(os.path.join(dir, file)))
        if base_file in name_references:
            name_references[base_file].add(name)
        else:
            name_references[base_file] = {name}

    for file in files_parsed:
        lib_prefix, name, ext = files_parsed[file]

        if name != libname:
            if get_non_match:
                if name in non_match:
                    non_match[name].add(file)
                else:
                    non_match[name] = {file}
        if name == libname or file in name_references and libname in name_references[file]:
            current_ext = -1
            for i in range(len(ext_pref_order)):
                if re.fullmatch(ext_pref_order[i].value, ext, re.IGNORECASE):
                    current_ext = i
                    break

            if current_ext != -1:
                chosen_libs.append((not lib_prefix, current_ext, file))

    chosen_libs.sort()
    return [lib[2] for lib in chosen_libs], non_match


def get_possible_filepaths(config: Config, libname: str, ext_pref_order: T.List[ExtType]) -> T.List[str]:
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
        libs, _ = search_lib(dir, libname, get_non_match=False, ext_pref_order=ext_pref_order)
        if len(libs) == 0:
            if config.target_is_mingw():
                filename = f"lib{libname}.a"
            elif config.target_is_windows():
                filename = f"{libname}.lib"
            else:
                filename = f"lib{libname}.so"
        else:
            filename = libs[0]
        filepaths.append(os.path.join(dir, filename))

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
    }
    for entry in cache["system"]:
        if "invalid" not in entry:
            new_cache["system"].append(entry)

    store_cache_to_file(cache_filepath, cache)


def _find_lib_with_pacman(possible_filepaths: T.List[str], tempdir_name: str, main_object_path: str, cache: T.Dict[str, T.Any], config: Config, min_version: T.Union[Version, None] = None, max_version: T.Union[Version, None] = None, allow_prerelease: bool = False) -> T.Union[T.Tuple[bool, str, str, T.Union[Version, None]], None]:
    cache_modified = False

    print_info("Updating pacman db in a fakeroot environment", verbosity=config.verbosity)
    pacman_update_db()

    available_versions = pacman_get_available_versions(possible_filepaths)
    found: T.Union[T.Tuple[str, str, Version], None] = None
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


def _find_lib(cache: T.Dict[str, T.Any], config: Config, libname: str, install_dir: str, package_name: T.Union[str, None] = None, git_repo: T.Union[GitRepo, None] = DefaultGitRepos(), min_version: T.Union[Version, None] = None, max_version: T.Union[Version, None] = None, allow_prerelease: bool = False, disable_system_packages: bool = False, ext_pref_order: T.List[ExtType] = DEFAULT_EXT_PREF_ORDER) -> T.Tuple[bool, str, str, T.Union[Version, None]]:
    cache_modified = False

    if "system" not in cache:
        cache["system"] = []

    tempdir, main_object_path = create_main_object(config)


    possible_filepaths = get_possible_filepaths(config, libname, ext_pref_order)
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

    if git_repo is not None:
        if isinstance(git_repo, DefaultGitRepos):
            git_repo.set_libname(libname, package_name)

        if package_name is None:
            package_name = os.path.basename(git_repo.code_git_url.split(':')[-1])
            if package_name.endswith(".git"):
                package_name = package_name[:-4]

    if package_name is None:
        package_folder_name = libname
    else:
        package_folder_name = package_name

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

    install_path = os.path.join(install_dir, config.target_simplified_architecture, current_toolchain_prefix, package_folder_name, libname)
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
            libs, _ = search_lib(lib_dir, libname, get_non_match=False, ext_pref_order=ext_pref_order)
            if len(libs) == 0:
                raise PowerMakeRuntimeError("A folder was found with the good version but no lib in the format you ask for was found")
            include = os.path.join(install_path, version[0], "include")
            for lib in libs:
                libpath = os.path.join(lib_dir, lib)
                if check_linker_compat(config, tempdir.name, main_object_path, libpath):
                    return (cache_modified, libpath, include, version[1])
            raise PowerMakeRuntimeError("A folder was found with the good version and libs in the good format, but none of them is compatible with your linker")

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

    includedir = os.path.join(lib_installed_path, "include")
    libs, non_match = search_lib(lib, libname, get_non_match=True, ext_pref_order=ext_pref_order)
    for name in non_match:
        # We should verify if the directory exists and prompt the user for action to take
        path = os.path.join(install_dir, config.target_simplified_architecture, current_toolchain_prefix, package_folder_name, name, builded_version_str)
        makedirs(os.path.join(path, "lib"))
        for file in non_match[name]:
            full_filepath = os.path.join(lib, file)
            if os.path.islink(full_filepath):
                real_path = os.path.realpath(full_filepath)
                relpath_from_lib = os.path.relpath(real_path, lib)
                shutil.copy(full_filepath, os.path.join(path, "lib", relpath_from_lib), follow_symlinks=True)
    # We use 2 loops to make sure all copies following symlink are done before moving the file referenced
    for name in non_match:
        path = os.path.join(install_dir, config.target_simplified_architecture, current_toolchain_prefix, package_folder_name, name, builded_version_str)
        for file in non_match[name]:
            if file in libs:
                shutil.copy(os.path.join(lib, file), os.path.join(path, "lib", file), follow_symlinks=False)
            else:
                shutil.move(os.path.join(lib, file), os.path.join(path, "lib", file))
        shutil.copytree(includedir, os.path.join(path, "include"), dirs_exist_ok=True)

    if len(libs) == 0:
        raise PowerMakeRuntimeError("Unable to find any package that meets the requirements.")

    return cache_modified, os.path.join(lib, libs[0]), includedir, builded_version



def find_lib(config: Config, libname: str, install_dir: str, *, package_name: T.Union[str, None] = None, git_repo: T.Union[GitRepo, None] = DefaultGitRepos(), min_version: T.Union[str, None] = None, max_version: T.Union[str, None] = None, allow_prerelease: bool = False, strict_post: bool = False, disable_system_packages: bool = False, ext_pref_order: T.List[ExtType] = DEFAULT_EXT_PREF_ORDER) -> T.Tuple[str, str, T.Union[Version, None]]:
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
    # }
    cache_filepath = os.path.join(get_cache_dir(), "packages", "installed", f"{libname}.json")
    cache = load_cache_from_file(cache_filepath)

    min_v = parse_version(min_version) if min_version is not None else None
    max_v = parse_version(max_version) if max_version is not None else None
    if not strict_post and max_v is not None and max_v.post_number is None:
        max_v.post_number = '*'

    cache_modified, lib, include, version = _find_lib(cache, config, libname, install_dir, package_name, git_repo, min_v, max_v, allow_prerelease, disable_system_packages, ext_pref_order=ext_pref_order)
    if cache_modified:
        save_cache(cache_filepath, cache)

    return lib, include, version