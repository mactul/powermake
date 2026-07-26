import os
import shlex
import shutil
import tempfile
import subprocess
import typing as T
from .lib import Lib
from .. import compilers
from ..config import Config
from ..utils import makedirs
from .utils import find_closest_include_dir
from ..exceptions import PowerMakeRuntimeError
from ..operation import run_command

def _set_pkg_environment(config: Config, dependencies: T.Iterable[Lib]) -> T.Tuple[T.Set[str], T.Set[str]]:
    if config.linker is None:
        return set(), set()

    dirs = config.linker.get_lib_dirs(config.ld_flags)
    filtered_dirs: T.Set[str] = set()
    for dir in dirs:
        if config.target_simplified_architecture == "x86" and ("lib32" in dir or os.path.basename(dir) == "32" or "i386" in dir or "i686" in dir):
            filtered_dirs.add(dir)
    if len(filtered_dirs) == 0:
        filtered_dirs = dirs

    filtered_dirs = filtered_dirs.union(os.path.dirname(dep.lib_file) for dep in dependencies)

    prefix_paths: T.Set[str] = set()
    for dep in dependencies:
        lib_dir = os.path.dirname(dep.lib_file)
        if lib_dir.endswith(("lib", "lib/")):
            prefix_paths.add(os.path.join(lib_dir, ".."))

    if len(filtered_dirs) > 0:
        pkg_dir_str = os.pathsep.join(os.path.join(dir, "pkgconfig") for dir in filtered_dirs)
        os.environ["PKG_CONFIG_PATH"] = pkg_dir_str
        os.environ["PKG_CONFIG_LIBDIR"] = pkg_dir_str
    return filtered_dirs, prefix_paths


def run_meson(config: Config, build_dir: str, *additional_args: str, prefer_static: bool = False, dependencies: T.Iterable[Lib] = []) -> None:
    content = "[binaries]\n"
    if config.c_compiler is not None:
        content += f"c = '{config.c_compiler.path}'\n"
    if config.cpp_compiler is not None:
        content += f"cpp = '{config.cpp_compiler.path}'\n"
    if config.rc_compiler is not None and config.target_is_mingw():
        content += f"windres = '{config.rc_compiler.path}'\n"
    if config.archiver is not None and (not config.target_is_windows() or config.target_is_mingw()):
        content += f"ar = '{config.archiver.path}'\n"
    nasm = compilers.CompilerNASM()
    if nasm.is_available():
        content += f"nasm = '{nasm.path}'\n"
    pkg_conf = shutil.which("shutil")
    if pkg_conf is not None:
        content += f"pkg-config = '{pkg_conf}'\n"

    if config.target_simplified_architecture == "x86":
        content += "\n[built-in options]\n"
        if config.c_compiler is not None:
            content += f"c_args = {str(config.c_compiler.translate_flags(["-m32", "-msse2"]))}\n"
        if config.cpp_compiler is not None:
            content += f"cpp_args = {str(config.cpp_compiler.translate_flags(["-m32", "-msse2"]))}\n"
        if config.linker is not None:
            content += f"c_link_args = {str(config.linker.translate_flags(["-m32", "-msse2"]))}\n"
            content += f"cpp_link_args = {str(config.linker.translate_flags(["-m32", "-msse2"]))}\n"

    content += "\n[host_machine]\n"
    if config.target_is_windows():
        system_name = "windows"
    elif config.target_is_linux():
        system_name = "linux"
    elif config.target_is_macos():
        system_name = "darwin"
    else:
        system_name = config.target_operating_system
    content += f"system = '{system_name}'\n"

    arch_map = {
            "x64": "x86_64",
            "arm32": "arm",
            "arm64": "aarch64"
        }
    arch = config.target_simplified_architecture
    if arch in arch_map:
        arch = arch_map[arch]
    content += f"cpu_family = '{arch}'\n"
    content += f"cpu = '{arch}'\n"
    content += "endian = 'little'\n"

    content += "\n[properties]\nneeds_exe_wrapper = true\n"

    print(content)

    _set_pkg_environment(config, dependencies)

    makedirs(build_dir)

    crossfile_path = os.path.join(build_dir, "powermake_meson_crossfile")
    with open(crossfile_path, "w") as file:
        file.write(content)

    ret = run_command(config, ["meson", "setup", build_dir, "--cross-file", crossfile_path, *additional_args])

    if ret != 0:
        raise PowerMakeRuntimeError("Unable to run meson")
    return


def run_cmake(config: Config, path: str, *additional_args: str, prefer_static: bool = False, dependencies: T.Iterable[Lib] = []) -> None:
    cmake_path = shutil.which("cmake")
    if cmake_path is None:
        raise PowerMakeRuntimeError("Unable to found cmake executable")

    args = []
    if config.c_compiler is not None:
        args.append(f"-DCMAKE_C_COMPILER={config.c_compiler.path}")
        if config.target_simplified_architecture == "x86":
            args.append(f"-DCMAKE_C_FLAGS={shlex.join(config.c_compiler.translate_flags(["-m32", "-msse2"]))}")
    if config.cpp_compiler is not None:
        args.append(f"-DCMAKE_CXX_COMPILER={config.cpp_compiler.path}")
        if config.target_simplified_architecture == "x86":
            args.append(f"-DCMAKE_CXX_FLAGS={shlex.join(config.cpp_compiler.translate_flags(["-m32", "-msse2"]))}")

    if config.as_compiler is not None and (not config.target_is_windows() or config.target_is_mingw()):
        args.append(f"-DCMAKE_ASM_COMPILER={config.as_compiler.path}")
        if config.target_simplified_architecture == "x86":
            args.append(f"-DCMAKE_ASM_FLAGS={shlex.join(config.as_compiler.translate_flags(["-m32", "-msse2"]))}")

    nasm = compilers.CompilerNASM()
    if nasm.is_available():
        args.append(f"-DCMAKE_ASM_NASM_COMPILER={nasm.path}")

    masm = compilers.CompilerMASM()
    if masm.is_available():
        args.append(f"-DCMAKE_ASM_MASM_COMPILER={masm.path}")


    if config.target_operating_system != config.host_operating_system or config.target_simplified_architecture != config.host_simplified_architecture:
        if config.target_is_windows():
            system_name = "Windows"
        elif config.target_is_linux():
            system_name = "Linux"
        elif config.target_is_macos():
            system_name = "Darwin"
        else:
            system_name = config.target_operating_system

        arch_map = {
            "x64": "AMD64",
        }
        arch = config.target_simplified_architecture
        if arch in arch_map:
            arch = arch_map[arch]

        args.extend([f"-DCMAKE_SYSTEM_NAME={system_name}", f"-DCMAKE_SYSTEM_PROCESSOR={arch}"])

    if config.target_is_macos():
        xcrun = shutil.which("xcrun")
        if xcrun is not None:
            try:
                sdk = subprocess.check_output([xcrun, "--sdk", "macosx", "--show-sdk-path"], encoding="utf-8").strip()
                args.append(f"-DCMAKE_FRAMEWORK_PATH={os.path.join(sdk, "System/Library/Frameworks")}")
            except subprocess.CalledProcessError:
                pass

    if prefer_static:
        args.append('-DBUILD_SHARED_LIBS=OFF')

    dirs, prefix_paths = _set_pkg_environment(config, dependencies)

    if len(dirs) > 0:
        lib_path_str = ';'.join(dirs)
        include_path_str = ';'.join(find_closest_include_dir(dir) or "" for dir in dirs)
        prefix_path_str = ';'.join(prefix_paths)
        args.extend([
            f"-DCMAKE_INCLUDE_PATH={include_path_str}",
            f"-DCMAKE_LIBRARY_PATH={lib_path_str}",
            f"-DCMAKE_PREFIX_PATH={prefix_path_str}",
            "-DCMAKE_FIND_USE_CMAKE_SYSTEM_PATH=OFF",
            "-DCMAKE_FIND_ROOT_PATH_MODE_INCLUDE=NEVER",
            "-DCMAKE_FIND_ROOT_PATH_MODE_LIBRARY=NEVER",
            "-DCMAKE_FIND_ROOT_PATH_MODE_PACKAGE=NEVER",
        ])

    cmake_generator: T.Tuple[str, ...] = tuple()
    ninja = shutil.which("ninja")
    if ninja is not None:
        cmake_generator = ("-G", "Ninja")

    if run_command(config, [cmake_path, *cmake_generator, path, *args, *additional_args]) != 0:
        raise PowerMakeRuntimeError("Unable to run cmake")