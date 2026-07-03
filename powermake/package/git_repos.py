import os
import re
import shutil
import tempfile
import subprocess
import typing as T

from ..config import Config
from ..operation import run_command
from ..run_another import run_another_powermake
from ..exceptions import PowerMakeRuntimeError
from ..utils import makedirs, join_absolute_paths
from ..version_parser import Version, parse_version, remove_version_frills

class GitRepo:
    def __init__(self, git_url: str, powermake_makefile_path_in_repo: str) -> None:
        self.code_git_url = git_url
        self.dst_makefile_path = powermake_makefile_path_in_repo
        self.src_makefile_path: T.Union[str, None] = None
        self.makefile_git_url: T.Union[str, None] = None
        self.tags_to_exclude: T.Tuple[str, ...] = tuple()
        self.additional_cmdline: T.Tuple[str, ...] = tuple()
        self.version_add_cmdline: T.Tuple[str, ...] = tuple()

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
        makefile_temp_dir: tempfile.TemporaryDirectory[str] | None = None

        if not config._args_parsed.pkg_install_noconfirm:
            print(f"Do you want to download {self.code_git_url} ? It will be compiled and installed in: '{install_path}'")
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

        run_another_powermake(config, join_absolute_paths(temp_dir.name, os.path.normpath(os.path.join("/", self.dst_makefile_path))), rebuild=True, debug=False, command_line_args=["--install", install_path, *self.additional_cmdline, *self.version_add_cmdline])

        lib_path = os.path.join(install_path, "lib")
        if not os.path.exists(lib_path):
            if os.path.exists(os.path.join(install_path, "lib32")):
                try:
                    os.symlink(os.path.join(install_path, "lib32"), lib_path, target_is_directory=True)
                except OSError:
                    # On Winslop, symlink requires admin rights or dev mode
                    os.rename(os.path.join(install_path, "lib32"), lib_path)
            elif os.path.exists(os.path.join(install_path, "lib64")):
                try:
                    os.symlink(os.path.join(install_path, "lib64"), lib_path, target_is_directory=True)
                except OSError:
                    # On Winslop, symlink requires admin rights or dev mode
                    os.rename(os.path.join(install_path, "lib64"), lib_path)
            else:
                raise PowerMakeRuntimeError("The library was compiled and installed but no lib folder was found")

        temp_dir.cleanup()
        if makefile_temp_dir is not None:
            makefile_temp_dir.cleanup()

    def suggested_min_ver(self) -> T.Union[Version | None]:
        return None

    def suggested_max_ver(self) -> T.Union[Version | None]:
        return None


class DefaultGitRepos(GitRepo):
    _default_packages = {
        "SDL2": ("SDL", tuple(), ("2.0", "2.*")),
        "SDL3": ("SDL", tuple(), ("3.0", "3.*")),
        "SDL2_ttf": ("SDL_ttf", ("--dependency=SDL2,2.0,2.*", "--dependency=freetype,None,None"), ("2.0", "2.*")),
        "SDL3_ttf": ("SDL_ttf", ("--dependency=SDL3,3.0,3.*", "--dependency=freetype,None,None"), ("3.0", "3.*")),
        "SDL2_image": ("SDL_image", ("--dependency=SDL2,2.0,2.*", ), ("2.0", "2.*")),
        "SDL3_image": ("SDL_image", ("--dependency=SDL3,3.0,3.*", ), ("3.0", "3.*")),
        "ssl": ("openssl", tuple(), None),
        "crypto": ("openssl", tuple(), None),
        "jpeg": ("libjpeg-turbo", tuple(), None),
        "turbojpeg": ("libjpeg-turbo", tuple(), None),
        "png": ("libpng", ("--dependency=z,None,None", ), None),
        "zip": ("libzip", ("--dependency=z,None,None", ), None),
        "glfw3": ("glfw", tuple(), ("3.0", "3.*")),
        "mariadb": ("mariadb-connector-c", tuple(), None),
        "z": ("zlib", tuple(), None),
        "zs": ("zlib", tuple(), None)
    }
    _preconfigured_repos: T.Dict[str, T.Tuple[str, str, T.Union[str, None], T.Union[str, None], T.Tuple[str, ...], T.Tuple[str, ...]]] = {
        "SDL": ("https://github.com/libsdl-org/SDL.git", "build/makefile.py", "https://github.com/mactul/powermake-repos.git", "generic/cmake/cmake_makefile.py", tuple(), ("--cmake-static", )),
        "SDL_ttf": ("https://github.com/libsdl-org/SDL_ttf.git", "build/makefile.py", "https://github.com/mactul/powermake-repos.git", "generic/cmake/cmake_makefile.py", tuple(), ("--cmake-static", )),
        "SDL_image": ("https://github.com/libsdl-org/SDL_image.git", "build/makefile.py", "https://github.com/mactul/powermake-repos.git", "generic/cmake/cmake_makefile.py", tuple(), ("--cmake-static", )),
        "boringssl": ("https://boringssl.googlesource.com/boringssl", "build/makefile.py", "https://github.com/mactul/powermake-repos.git", "generic/cmake/cmake_makefile.py", ("fips.*", "version.*"), ("--cmake-static", )),
        "libressl": ("https://github.com/libressl/portable.git", "build/makefile.py", "https://github.com/mactul/powermake-repos.git", "generic/cmake/autogen_cmake_makefile.py", tuple(), tuple()),
        "openssl": ("https://github.com/openssl/openssl.git", "makefile.py", "https://github.com/mactul/powermake-repos.git", "o/openssl/openssl_makefile.py", (".*fips.*", ".*FIPS.*", ".*engine.*", ".*SSLeay.*"), tuple()),
        "libjpeg-turbo": ("https://github.com/libjpeg-turbo/libjpeg-turbo", "build/makefile.py", "https://github.com/mactul/powermake-repos.git", "generic/cmake/cmake_makefile.py", ("jpeg.*", ), tuple()),
        "libpng": ("https://github.com/pnggroup/libpng", "build/makefile.py", "https://github.com/mactul/powermake-repos.git", "generic/cmake/cmake_makefile.py", (".*png.*", ".*master.*"), ("--cmake-static", )),
        "libzip": ("https://github.com/nih-at/libzip", "build/makefile.py", "https://github.com/mactul/powermake-repos.git", "generic/cmake/cmake_makefile.py", (".*brian.*", ), tuple()),
        "glfw": ("https://github.com/glfw/glfw.git", "build/makefile.py", "https://github.com/mactul/powermake-repos.git", "generic/cmake/cmake_makefile.py", tuple(), ("--cmake-static", )),
        "json-c": ("https://github.com/json-c/json-c.git", "build/makefile.py", "https://github.com/mactul/powermake-repos.git", "generic/cmake/cmake_makefile.py", tuple(), ("--cmake-flag=-DBUILD_APPS=off", "--cmake-flag=-DBUILD_TESTING=off", "--cmake-flag=-DDISABLE_WERROR=on")),
        "mariadb-connector-c": ("https://github.com/mariadb-corporation/mariadb-connector-c.git", "build/makefile.py", "https://github.com/mactul/powermake-repos.git", "m/mariadb/mariadb_makefile.py", (".*MS.*", ".*py.*"), tuple()),
        "freetype": ("https://gitlab.freedesktop.org/freetype/freetype.git", "build/makefile.py", "https://github.com/mactul/powermake-repos.git", "generic/cmake/cmake_makefile.py", ('CACHE.*', 'DATE.*'), ("--cmake-static", )),
        "zlib": ("https://github.com/madler/zlib.git", "build/makefile.py", "https://github.com/mactul/powermake-repos.git", "generic/cmake/cmake_makefile.py", tuple(), ("--cmake-static", "--cmake-flag=-DZLIB_BUILD_TESTING=OFF"))
    }

    def __init__(self) -> None:
        self.libname: T.Union[str, None] = None
        super().__init__("", "")

    def set_libname(self, libname: str, package_name: T.Union[str, None]) -> None:
        if package_name is None:
            if libname in self._default_packages:
                package_name, self.version_add_cmdline, _ = self._default_packages[libname]
            else:
                package_name = libname

        if package_name not in self._preconfigured_repos:
            self.libname = None
            return

        self.libname = libname
        self.code_git_url, self.dst_makefile_path, self.makefile_git_url, self.src_makefile_path, self.tags_to_exclude, self.additional_cmdline = self._preconfigured_repos[package_name]

    def get_server_versions(self) -> T.List[T.Tuple[str, Version]]:
        if self.libname is None:
            raise PowerMakeRuntimeError("Unable to find any package that meets the requirements.")
        return super().get_server_versions()

    def suggested_min_ver(self) -> T.Union[Version | None]:
        if self.libname in self._default_packages:
            range = self._default_packages[self.libname][2]
            if range is None:
                return None
            return parse_version(range[0])
        return None

    def suggested_max_ver(self) -> T.Union[Version | None]:
        if self.libname in self._default_packages:
            range = self._default_packages[self.libname][2]
            if range is None:
                return None
            return parse_version(range[1])
        return None
