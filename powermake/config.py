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


import os
import copy
import json
import argparse
import platform
import typing as T

from .cache import get_cache_dir
from .display import print_debug_info, error_text
from .tools import load_tool_tuple_from_file, load_tool_from_tuple, find_tool
from .search_visual_studio import load_msvc_environment
from .architecture import simplify_architecture, search_new_toolchain
from .compilers import Compiler, CompilerGNU, CompilerGNUPlusPlus, GenericCompiler, get_all_c_compiler_types, get_all_cpp_compiler_types, get_all_as_compiler_types, get_all_asm_compiler_types
from .archivers import Archiver, GenericArchiver, get_all_archiver_types
from .linkers import Linker, LinkerGNU, GenericLinker, get_all_linker_types
from .shared_linkers import SharedLinker, GenericSharedLinker, get_all_shared_linker_types


def get_global_config() -> str:
    global_config = os.getenv("POWERMAKE_CONFIG")
    if global_config is None:
        global_config = os.path.normpath(os.path.expanduser("~/.powermake/powermake_config.json"))
    return global_config


def auto_toolchain(preference: T.Union[str, None], c_compiler: T.Union[Compiler, None], cpp_compiler: T.Union[Compiler, None], as_compiler: T.Union[Compiler, None], asm_compiler: T.Union[Compiler, None], archiver: T.Union[Archiver, None], linker: T.Union[Linker, None], shared_linker: T.Union[SharedLinker, None]) -> T.Tuple[str, str, str, str, str, str, str]:
    all_None = True
    if c_compiler is not None:
        c_compiler_type = c_compiler.type
        all_None = False
    else:
        c_compiler_type = None

    if cpp_compiler is not None:
        cpp_compiler_type = cpp_compiler.type
        all_None = False
    else:
        cpp_compiler_type = None

    if as_compiler is not None:
        as_compiler_type = as_compiler.type
        all_None = False
    else:
        as_compiler_type = None

    if asm_compiler is not None:
        asm_compiler_type = asm_compiler.type
        all_None = False
    else:
        asm_compiler_type = None

    if archiver is not None:
        archiver_type = archiver.type
        all_None = False
    else:
        archiver_type = None

    if linker is not None:
        linker_type = linker.type
        all_None = False
    else:
        linker_type = None

    if shared_linker is not None:
        shared_linker_type = shared_linker.type
        all_None = False
    else:
        shared_linker_type = None

    if all_None and preference == "gnu" or c_compiler_type == "gnu" or cpp_compiler_type == "gnu++" or as_compiler_type == "gnu" or linker_type in ("gnu", "gnu++") or shared_linker_type in ("gnu", "gnu++") or archiver_type == "gnu":
        # GNU toolchain
        c_compiler_type = "gnu"
        cpp_compiler_type = "gnu++"
        as_compiler_type = "gnu"
        archiver_type = "gnu"
        linker_type = "gnu++"
        shared_linker_type = "gnu++"
    elif all_None and preference == "gcc" or c_compiler_type == "gcc" or cpp_compiler_type == "g++" or as_compiler_type == "gcc" or linker_type in ("gcc", "g++") or shared_linker_type in ("gcc", "g++") or archiver_type == "ar":
        # GCC toolchain
        c_compiler_type = "gcc"
        cpp_compiler_type = "g++"
        as_compiler_type = "gcc"
        archiver_type = "ar"
        linker_type = "g++"
        shared_linker_type = "g++"
    elif all_None and preference == "clang" or c_compiler_type == "clang" or cpp_compiler_type == "clang++" or as_compiler_type == "clang" or linker_type in ("clang", "clang++") or shared_linker_type in ("clang", "clang++") or archiver_type == "llvm-ar":
        # clang toolchain
        c_compiler_type = "clang"
        cpp_compiler_type = "clang++"
        as_compiler_type = "clang"
        archiver_type = "llvm-ar"
        linker_type = "clang++"
        shared_linker_type = "clang++"
    elif all_None and preference == "mingw" or c_compiler_type == "mingw" or cpp_compiler_type == "mingw++" or as_compiler_type == "mingw" or linker_type in ("mingw", "mingw++") or shared_linker_type in ("mingw", "mingw++") or archiver_type == "mingw":
        # MinGW toolchain
        c_compiler_type = "mingw"
        cpp_compiler_type = "mingw++"
        as_compiler_type = "mingw"
        archiver_type = "mingw"
        linker_type = "mingw++"
        shared_linker_type = "mingw++"
    elif all_None and preference == "msvc" or c_compiler_type == "msvc" or cpp_compiler_type == "msvc" or linker_type == "msvc" or shared_linker_type == "msvc" or archiver_type == "msvc":
        # MSVC toolchain
        c_compiler_type = "msvc"
        cpp_compiler_type = "msvc"
        as_compiler_type = "clang"
        archiver_type = "msvc"
        linker_type = "msvc"
        shared_linker_type = "msvc"

    return (c_compiler_type, cpp_compiler_type, as_compiler_type, asm_compiler_type, archiver_type, linker_type, shared_linker_type)


def get_toolchain_tuple(path: T.Union[str, None, bool]) -> T.Union[T.Tuple[str, str], None]:
    if not path or path is True:
        return None
    if path.endswith("gcc"):
        return ("gcc", path[:-3])
    if path.endswith("clang"):
        return ("clang", path[:-5])
    if path.endswith("clang++"):
        return ("clang", path[:-7])
    if path.endswith("g++"):
        return ("gcc", path[:-3])
    if path.endswith("ar"):
        return ("gnu", path[:-2])
    if path.endswith("ld"):
        return ("gnu", path[:-2])
    if path.endswith("cc"):
        return ("gnu", path[:-2])
    if path.endswith("cpp"):
        return ("gnu", path[:-3])
    if path.endswith("c++"):
        return ("gnu", path[:-3])

    return None


def replace_architecture(string: str, new_arch: str) -> str:
    new_arch = "/" + new_arch + "/"
    for arch in ("/x86/", "/x64/", "/arm32/", "/arm64/"):
        string = string.replace(arch, new_arch)
    return string


class Config:
    def __init__(self, target_name: str, *, args_parsed: T.Union[argparse.Namespace, None] = None, debug: bool = False, rebuild: bool = False, verbosity: int = 1, nb_jobs: int = 0, single_file: T.Union[str, None] = None, compile_commands_dir: T.Union[str, None] = None, local_config: T.Union[str, None] = "./powermake_config.json", global_config: T.Union[str, None] = None) -> None:
        """
        Create an object that loads all configurations files and search for compilers.

        This objects hold all the configuration for the compilation.

        If you want to compile multiple set of files with different settings, you have to make a copy of this object and modify the copy.
        """
        self.target_name = target_name
        self._args_parsed = args_parsed
        self.verbosity = verbosity
        self.debug = debug
        self.rebuild = rebuild
        self.nb_jobs = nb_jobs
        self.single_file = single_file
        self.compile_commands_dir = compile_commands_dir
        self.nb_total_operations = 0

        self.c_compiler: T.Union[Compiler, None] = None
        self.cpp_compiler: T.Union[Compiler, None] = None
        self.as_compiler: T.Union[Compiler, None] = None
        self.asm_compiler: T.Union[Compiler, None] = None
        self.archiver: T.Union[Archiver, None] = None
        self.linker: T.Union[Linker, None] = None
        self.shared_linker: T.Union[SharedLinker, None] = None

        self.target_operating_system: str = ""
        self.host_operating_system: str = ""

        self.target_architecture: str = ""
        self.target_simplified_architecture: str = ""
        self.host_architecture: str = ""
        self.host_simplified_architecture: str = ""

        self.obj_build_directory: str = ""
        self.exe_build_directory: str = ""
        self.lib_build_directory: str = ""

        self.defines: T.List[str] = []
        self.shared_libs: T.List[str] = []
        self.additional_includedirs: T.List[str] = []
        self.c_flags: T.List[str] = []
        self.cpp_flags: T.List[str] = []
        self.as_flags: T.List[str] = []
        self.asm_flags: T.List[str] = []
        self.ar_flags: T.List[str] = []
        self.ld_flags: T.List[str] = []
        self.shared_linker_flags: T.List[str] = []

        self.exported_headers: T.List[T.Tuple[str, T.Union[str, None]]] = []

        c_compiler_tuple: T.Union[T.Tuple[T.Union[str, None], T.Callable[[], Compiler], bool], None] = None
        cpp_compiler_tuple: T.Union[T.Tuple[T.Union[str, None], T.Callable[[], Compiler], bool], None] = None
        as_compiler_tuple: T.Union[T.Tuple[T.Union[str, None], T.Callable[[], Compiler], bool], None] = None
        asm_compiler_tuple: T.Union[T.Tuple[T.Union[str, None], T.Callable[[], Compiler], bool], None] = None
        archiver_tuple: T.Union[T.Tuple[T.Union[str, None], T.Callable[[], Archiver], bool], None] = None
        linker_tuple: T.Union[T.Tuple[T.Union[str, None], T.Callable[[], Linker], bool], None] = None
        shared_linker_tuple: T.Union[T.Tuple[T.Union[str, None], T.Callable[[], SharedLinker], bool], None] = None

        if global_config is None:
            global_config = get_global_config()

        self.global_config_dir = os.path.dirname(global_config)

        for path in (local_config, global_config):
            if path is None:
                continue
            try:
                with open(path, "r") as file:
                    conf: T.Dict[str, T.Any] = json.load(file)
                    if c_compiler_tuple is None:
                        c_compiler_tuple = T.cast(T.Union[T.Tuple[T.Union[str, None], T.Callable[[], Compiler], bool], None], load_tool_tuple_from_file(conf, "c_compiler", GenericCompiler, get_all_c_compiler_types))

                    if cpp_compiler_tuple is None:
                        cpp_compiler_tuple = T.cast(T.Union[T.Tuple[T.Union[str, None], T.Callable[[], Compiler], bool], None], load_tool_tuple_from_file(conf, "cpp_compiler", GenericCompiler, get_all_cpp_compiler_types))

                    if as_compiler_tuple is None:
                        as_compiler_tuple = T.cast(T.Union[T.Tuple[T.Union[str, None], T.Callable[[], Compiler], bool], None], load_tool_tuple_from_file(conf, "as_compiler", GenericCompiler, get_all_as_compiler_types))

                    if asm_compiler_tuple is None:
                        asm_compiler_tuple = T.cast(T.Union[T.Tuple[T.Union[str, None], T.Callable[[], Compiler], bool], None], load_tool_tuple_from_file(conf, "asm_compiler", GenericCompiler, get_all_asm_compiler_types))

                    if archiver_tuple is None:
                        archiver_tuple = T.cast(T.Union[T.Tuple[T.Union[str, None], T.Callable[[], Archiver], bool], None], load_tool_tuple_from_file(conf, "archiver", GenericArchiver, get_all_archiver_types))

                    if linker_tuple is None:
                        linker_tuple = T.cast(T.Union[T.Tuple[T.Union[str, None], T.Callable[[], Linker], bool], None], load_tool_tuple_from_file(conf, "linker", GenericLinker, get_all_linker_types))

                    if shared_linker_tuple is None:
                        shared_linker_tuple = T.cast(T.Union[T.Tuple[T.Union[str, None], T.Callable[[], SharedLinker], bool], None], load_tool_tuple_from_file(conf, "shared_linker", GenericSharedLinker, get_all_shared_linker_types))

                    if self.target_operating_system == "" and "target_operating_system" in conf:
                        self.target_operating_system = conf["target_operating_system"]
                    if self.host_operating_system == "" and "host_operating_system" in conf:
                        self.host_operating_system = conf["host_operating_system"]

                    if self.target_architecture == "" and "target_architecture" in conf:
                        self.target_architecture = conf["target_architecture"]
                    if self.host_architecture == "" and "host_architecture" in conf:
                        self.host_architecture = conf["host_architecture"]

                    if self.obj_build_directory == "" and "obj_build_directory" in conf:
                        self.obj_build_directory = conf["obj_build_directory"]
                    if self.exe_build_directory == "" and "exe_build_directory" in conf:
                        self.exe_build_directory = conf["exe_build_directory"]
                    if self.lib_build_directory == "" and "lib_build_directory" in conf:
                        self.lib_build_directory = conf["lib_build_directory"]

                    if self.nb_jobs == 0 and "nb_jobs" in conf:
                        self.nb_jobs = conf["nb_jobs"]

                    if self.compile_commands_dir is None and "compile_commands_dir" in conf:
                        self.compile_commands_dir = conf["compile_commands_dir"]

                    if "defines" in conf and isinstance(conf["defines"], list):
                        for define in conf["defines"]:
                            if isinstance(define, str) and define not in self.defines:
                                self.defines.append(define)

                    if "shared_libs" in conf and isinstance(conf["shared_libs"], list):
                        for shared_lib in conf["shared_libs"]:
                            if isinstance(shared_lib, str) and shared_lib not in self.shared_libs:
                                self.shared_libs.append(shared_lib)

                    if "additional_includedirs" in conf and isinstance(conf["additional_includedirs"], list):
                        for includedir in conf["additional_includedirs"]:
                            if isinstance(includedir, str) and includedir not in self.additional_includedirs:
                                self.additional_includedirs.append(includedir)

                    if "c_flags" in conf and isinstance(conf["c_flags"], list):
                        for c_flag in conf["c_flags"]:
                            if isinstance(c_flag, str) and c_flag not in self.c_flags:
                                self.c_flags.append(c_flag)

                    if "cpp_flags" in conf and isinstance(conf["cpp_flags"], list):
                        for cpp_flag in conf["cpp_flags"]:
                            if isinstance(cpp_flag, str) and cpp_flag not in self.cpp_flags:
                                self.cpp_flags.append(cpp_flag)

                    if "c_cpp_flags" in conf and isinstance(conf["c_cpp_flags"], list):
                        for c_cpp_flag in conf["c_cpp_flags"]:
                            if isinstance(c_cpp_flag, str):
                                if c_cpp_flag not in self.c_flags:
                                    self.c_flags.append(c_cpp_flag)
                                if c_cpp_flag not in self.cpp_flags:
                                    self.cpp_flags.append(c_cpp_flag)

                    if "c_cpp_as_asm_flags" in conf and isinstance(conf["c_cpp_as_asm_flags"], list):
                        for c_cpp_as_asm_flag in conf["c_cpp_as_asm_flags"]:
                            if isinstance(c_cpp_as_asm_flag, str):
                                if c_cpp_as_asm_flag not in self.c_flags:
                                    self.c_flags.append(c_cpp_as_asm_flag)
                                if c_cpp_as_asm_flag not in self.cpp_flags:
                                    self.cpp_flags.append(c_cpp_as_asm_flag)
                                if c_cpp_as_asm_flag not in self.as_flags:
                                    self.as_flags.append(c_cpp_as_asm_flag)
                                if c_cpp_as_asm_flag not in self.asm_flags:
                                    self.asm_flags.append(c_cpp_as_asm_flag)

                    if "as_flags" in conf and isinstance(conf["as_flags"], list):
                        for as_flag in conf["as_flags"]:
                            if isinstance(as_flag, str) and as_flag not in self.as_flags:
                                self.as_flags.append(as_flag)

                    if "asm_flags" in conf and isinstance(conf["asm_flags"], list):
                        for asm_flag in conf["asm_flags"]:
                            if isinstance(asm_flag, str) and asm_flag not in self.asm_flags:
                                self.asm_flags.append(asm_flag)

                    if "ar_flags" in conf and isinstance(conf["ar_flags"], list):
                        for ar_flag in conf["ar_flags"]:
                            if isinstance(ar_flag, str) and ar_flag not in self.ar_flags:
                                self.ar_flags.append(ar_flag)

                    if "ld_flags" in conf and isinstance(conf["ld_flags"], list):
                        for ld_flag in conf["ld_flags"]:
                            if isinstance(ld_flag, str) and ld_flag not in self.ld_flags:
                                self.ld_flags.append(ld_flag)

                    if "shared_linker_flags" in conf and isinstance(conf["shared_linker_flags"], list):
                        for shared_linker_flag in conf["shared_linker_flags"]:
                            if isinstance(shared_linker_flag, str) and shared_linker_flag not in self.shared_linker_flags:
                                self.shared_linker_flags.append(shared_linker_flag)

                    if "exported_headers" in conf and isinstance(conf["exported_headers"], list):
                        for exported_header in conf["exported_headers"]:
                            if isinstance(exported_header, str) and (exported_header, None) not in self.exported_headers:
                                self.exported_headers.append((exported_header, None))
                            elif isinstance(exported_header, list) and len(exported_header) == 2 and tuple(exported_header) not in self.exported_headers:
                                self.exported_headers.append((exported_header[0], exported_header[1]))

            except OSError:
                pass

        if self.nb_jobs == 0:
            self.nb_jobs = os.cpu_count() or 8

        target_os_autodetected = False
        if self.target_operating_system == "":
            target_os_autodetected = True
            self.target_operating_system = platform.system()
        if self.host_operating_system == "":
            self.host_operating_system = platform.system()

        if self.target_architecture == "":
            self.target_architecture = platform.machine()
        if self.host_architecture == "":
            self.host_architecture = platform.machine()

        self.c_compiler_path_specified = c_compiler_tuple is not None and c_compiler_tuple[0] is not None
        self.c_compiler_type_specified = c_compiler_tuple is not None and c_compiler_tuple[2]
        self.cpp_compiler_path_specified = cpp_compiler_tuple is not None and cpp_compiler_tuple[0] is not None
        self.cpp_compiler_type_specified = cpp_compiler_tuple is not None and cpp_compiler_tuple[2]
        self.as_compiler_path_specified = as_compiler_tuple is not None and as_compiler_tuple[0] is not None
        self.as_compiler_type_specified = as_compiler_tuple is not None and as_compiler_tuple[2]
        self.archiver_path_specified = archiver_tuple is not None and archiver_tuple[0] is not None
        self.archiver_type_specified = archiver_tuple is not None and archiver_tuple[2]
        self.linker_path_specified = linker_tuple is not None and linker_tuple[0] is not None
        self.linker_type_specified = linker_tuple is not None and linker_tuple[2]
        self.shared_linker_path_specified = shared_linker_tuple is not None and shared_linker_tuple[0] is not None
        self.shared_linker_type_specified = shared_linker_tuple is not None and shared_linker_tuple[2]

        self.set_target_architecture(self.target_architecture, reload_tools_and_build_dir=False)

        self.c_compiler = T.cast(T.Union[Compiler, None], load_tool_from_tuple(c_compiler_tuple, "compiler"))
        self.cpp_compiler = T.cast(T.Union[Compiler, None], load_tool_from_tuple(cpp_compiler_tuple, "compiler"))
        self.as_compiler = T.cast(T.Union[Compiler, None], load_tool_from_tuple(as_compiler_tuple, "compiler"))
        self.asm_compiler = T.cast(T.Union[Compiler, None], load_tool_from_tuple(asm_compiler_tuple, "compiler"))
        self.archiver = T.cast(T.Union[Archiver, None], load_tool_from_tuple(archiver_tuple, "archiver"))
        self.linker = T.cast(T.Union[Linker, None], load_tool_from_tuple(linker_tuple, "linker"))
        self.shared_linker = T.cast(T.Union[SharedLinker, None], load_tool_from_tuple(shared_linker_tuple, "shared_linker"))

        preference = None
        if "CCC_ANALYZER_ANALYSIS" in os.environ:
            # This is the signature of scan-build
            # if no toolchain is specified, the auto toolchain should prefer clang
            preference = "clang"
        else:
            compiler_path = os.getenv("CC") or os.getenv("CXX")
            if compiler_path is not None:
                if "clang" in compiler_path:
                    preference = "clang"
                elif "mingw" in compiler_path:
                    preference = "mingw"
                elif "gcc" in compiler_path or "g++" in compiler_path:
                    preference = "gcc"
                elif "cl" in compiler_path:
                    preference = "msvc"

        toolchain = auto_toolchain(preference, self.c_compiler, self.cpp_compiler, self.as_compiler, self.asm_compiler, self.archiver, self.linker, self.shared_linker)

        if self.c_compiler is None:
            if self.target_is_windows():
                self.c_compiler = T.cast(T.Union[Compiler, None], find_tool(GenericCompiler, toolchain[0], "mingw", "msvc", "gcc", "clang-cl", "clang"))
            else:
                self.c_compiler = T.cast(T.Union[Compiler, None], find_tool(GenericCompiler, toolchain[0], "gcc", "clang"))

        if self.cpp_compiler is None:
            if self.target_is_windows():
                self.cpp_compiler = T.cast(T.Union[Compiler, None], find_tool(GenericCompiler, toolchain[1], "mingw++", "msvc", "g++", "clang-cl", "clang"))
            else:
                self.cpp_compiler = T.cast(T.Union[Compiler, None], find_tool(GenericCompiler, toolchain[1], "g++", "clang++"))

        if self.as_compiler is None:
            if self.target_is_windows():
                self.as_compiler = T.cast(T.Union[Compiler, None], find_tool(GenericCompiler, toolchain[2], "mingw", "gcc", "clang"))
            else:
                self.as_compiler = T.cast(T.Union[Compiler, None], find_tool(GenericCompiler, toolchain[2], "gcc", "clang"))

        if self.asm_compiler is None:
            self.asm_compiler = T.cast(T.Union[Compiler, None], find_tool(GenericCompiler, toolchain[3], "nasm"))

        if self.archiver is None:
            if self.target_is_windows():
                self.archiver = T.cast(T.Union[Archiver, None], find_tool(GenericArchiver, toolchain[4], "mingw", "msvc", "ar", "llvm-ar"))
            else:
                self.archiver = T.cast(T.Union[Archiver, None], find_tool(GenericArchiver, toolchain[4], "ar", "llvm-ar"))

        if self.linker is None:
            if self.target_is_windows():
                self.linker = T.cast(T.Union[Linker, None], find_tool(GenericLinker, toolchain[5], "mingw++", "msvc", "g++", "clang++", "clang-cl", "gcc", "clang"))
            else:
                self.linker = T.cast(T.Union[Linker, None], find_tool(GenericLinker, toolchain[5], "g++", "clang++", "gcc", "clang"))

        if self.shared_linker is None:
            if self.target_is_windows():
                self.shared_linker = T.cast(T.Union[SharedLinker, None], find_tool(GenericSharedLinker, toolchain[6], "mingw++", "msvc", "g++", "clang++", "clang-cl", "gcc", "clang"))
            else:
                self.shared_linker = T.cast(T.Union[SharedLinker, None], find_tool(GenericSharedLinker, toolchain[6], "g++", "clang++", "gcc", "clang"))

        cc_env = os.getenv("CC")
        if cc_env is not None:
            print_debug_info("Using CC environment variable instead of the config", verbosity)
            self.c_compiler_path_specified = True
            if self.c_compiler is not None:
                os.environ["CCC_CC"] = self.c_compiler.path
                self.c_compiler.reload(cc_env)  # We change the path, but we keep the compiler object
            else:
                self.c_compiler = CompilerGNU(cc_env)
            if not self.c_compiler.is_available():
                raise ValueError(error_text(f"The compiler {cc_env} could not be found on your machine"))

        cxx_env = os.getenv("CXX")
        if cxx_env is not None:
            print_debug_info("Using CXX environment variable instead of the config", verbosity)
            self.cpp_compiler_path_specified = True
            if self.cpp_compiler is not None:
                os.environ["CCC_CXX"] = self.cpp_compiler.path
                self.cpp_compiler.reload(cxx_env)  # We change the path, but we keep the compiler object
            else:
                self.cpp_compiler = CompilerGNUPlusPlus(cxx_env)
            if not self.cpp_compiler.is_available():
                raise ValueError(error_text(f"The compiler {cxx_env} could not be found on your machine"))

        ld_env = os.getenv("LD")
        if ld_env is not None:
            print_debug_info("Using LD environment variable instead of the config", verbosity)
            self.linker_path_specified = True
            if self.linker is not None:
                self.linker.reload(ld_env)  # We change the path, but we keep the compiler object
            else:
                self.linker = LinkerGNU(ld_env)
            if not self.linker.is_available():
                raise ValueError(error_text(f"The linker {ld_env} could not be found on your machine"))

        toolchain_tuple = get_toolchain_tuple(
            self.c_compiler_path_specified and self.c_compiler is not None and self.c_compiler.path
            or self.cpp_compiler_path_specified and self.cpp_compiler is not None and self.cpp_compiler.path
            or self.as_compiler_path_specified and self.as_compiler is not None and self.as_compiler.path
            or self.linker_path_specified and self.linker is not None and self.linker.path
            or self.shared_linker_path_specified and self.shared_linker is not None and self.shared_linker.path
            or self.archiver_path_specified and self.archiver is not None and self.archiver.path
        )
        if toolchain_tuple is not None:
            t, toolchain_prefix = toolchain_tuple
            if not self.c_compiler_type_specified:
                if self.c_compiler_path_specified and self.c_compiler is not None:
                    path = self.c_compiler.path
                else:
                    path = None
                if t == "gcc":
                    compiler = T.cast(T.Callable[[str], Compiler], GenericCompiler("gcc"))(path or toolchain_prefix + "gcc")
                elif t == "mingw":
                    compiler = T.cast(T.Callable[[str], Compiler], GenericCompiler("mingw"))(path or toolchain_prefix + "gcc")
                elif t == "clang":
                    compiler = T.cast(T.Callable[[str], Compiler], GenericCompiler("clang"))(path or toolchain_prefix + "clang")
                else:
                    compiler = T.cast(T.Callable[[str], Compiler], GenericCompiler("gnu"))(path or toolchain_prefix + "cc")
                if compiler.is_available():
                    self.c_compiler_path_specified = True
                    self.c_compiler = compiler
            if not self.cpp_compiler_type_specified:
                if self.cpp_compiler_path_specified and self.cpp_compiler is not None:
                    path = self.cpp_compiler.path
                else:
                    path = None
                if t == "gcc":
                    compiler = T.cast(T.Callable[[str], Compiler], GenericCompiler("g++"))(path or toolchain_prefix + "g++")
                elif t == "mingw":
                    compiler = T.cast(T.Callable[[str], Compiler], GenericCompiler("mingw++"))(path or toolchain_prefix + "g++")
                elif t == "clang":
                    compiler = T.cast(T.Callable[[str], Compiler], GenericCompiler("clang++"))(path or toolchain_prefix + "clang++")
                else:
                    compiler = T.cast(T.Callable[[str], Compiler], GenericCompiler("gnu++"))(path or toolchain_prefix + "c++")
                if compiler.is_available():
                    self.cpp_compiler_path_specified = True
                    self.cpp_compiler = compiler
            if not self.as_compiler_type_specified:
                if self.as_compiler_path_specified and self.as_compiler is not None:
                    path = self.as_compiler.path
                else:
                    path = None
                if t == "gcc":
                    compiler = T.cast(T.Callable[[str], Compiler], GenericCompiler("gcc"))(path or toolchain_prefix + "gcc")
                elif t == "mingw":
                    compiler = T.cast(T.Callable[[str], Compiler], GenericCompiler("mingw"))(path or toolchain_prefix + "gcc")
                elif t == "clang":
                    compiler = T.cast(T.Callable[[str], Compiler], GenericCompiler("clang"))(path or toolchain_prefix + "clang")
                else:
                    compiler = T.cast(T.Callable[[str], Compiler], GenericCompiler("gnu"))(path or toolchain_prefix + "cc")
                if compiler.is_available():
                    self.as_compiler_path_specified = True
                    self.as_compiler = compiler
            if not self.linker_type_specified:
                if self.linker_path_specified and self.linker is not None:
                    path = self.linker.path
                else:
                    path = None
                if t == "gcc":
                    ld = T.cast(T.Callable[[str], Linker], GenericLinker("g++"))(path or toolchain_prefix + "g++")
                elif t == "mingw":
                    ld = T.cast(T.Callable[[str], Linker], GenericLinker("mingw++"))(path or toolchain_prefix + "g++")
                elif t == "clang":
                    ld = T.cast(T.Callable[[str], Linker], GenericLinker("clang++"))(path or toolchain_prefix + "clang++")
                else:
                    ld = T.cast(T.Callable[[str], Linker], GenericLinker("gnu++"))(path or toolchain_prefix + "c++")
                if ld.is_available():
                    self.linker_path_specified = True
                    self.linker = ld
            if not self.shared_linker_type_specified:
                if self.shared_linker_path_specified and self.shared_linker is not None:
                    path = self.shared_linker.path
                else:
                    path = None
                if t == "gcc":
                    shared_ld = T.cast(T.Callable[[str], SharedLinker], GenericSharedLinker("g++"))(path or toolchain_prefix + "g++")
                elif t == "mingw":
                    shared_ld = T.cast(T.Callable[[str], SharedLinker], GenericSharedLinker("mingw++"))(path or toolchain_prefix + "g++")
                elif t == "clang":
                    shared_ld = T.cast(T.Callable[[str], SharedLinker], GenericSharedLinker("clang++"))(path or toolchain_prefix + "clang++")
                else:
                    shared_ld = T.cast(T.Callable[[str], SharedLinker], GenericSharedLinker("gnu++"))(path or toolchain_prefix + "c++")
                if shared_ld.is_available():
                    self.shared_linker_type_specified = True
                    self.shared_linker = shared_ld
            if not self.archiver_type_specified:
                if self.archiver_path_specified and self.archiver is not None:
                    path = self.archiver.path
                else:
                    path = None
                if t == "gcc":
                    archiver = T.cast(T.Callable[[str], Archiver], GenericArchiver("ar"))(path or toolchain_prefix + "ar")
                elif t == "mingw":
                    archiver = T.cast(T.Callable[[str], Archiver], GenericArchiver("mingw"))(path or toolchain_prefix + "ar")
                elif t == "clang":
                    archiver = T.cast(T.Callable[[str], Archiver], GenericArchiver("llvm-ar"))(path or toolchain_prefix + "ar")
                else:
                    archiver = T.cast(T.Callable[[str], Archiver], GenericArchiver("gnu"))(path or toolchain_prefix + "ar")
                if archiver.is_available():
                    self.archiver_path_specified = True
                    self.archiver = archiver

        if target_os_autodetected and self.c_compiler is not None and "mingw" in self.c_compiler.path.lower():
            self.target_operating_system = "Windows"


        self.set_debug(self.debug, True)
        self.add_c_cpp_as_asm_flags("-fdiagnostics-color")

        self.reload_tools()
        self.set_target_architecture(self.target_architecture, False)

    @property
    def c_cpp_flags(self) -> T.List[str]:
        return self.c_flags + self.cpp_flags

    @property
    def c_cpp_as_asm_flags(self) -> T.List[str]:
        return self.c_flags + self.cpp_flags + self.as_flags + self.asm_flags

    def reload_env(self) -> None:
        if self.target_architecture == "" or self.host_architecture == "":
            raise RuntimeError(error_text("Unable to load environment because architecture is undetermined"))

        self.target_simplified_architecture = simplify_architecture(self.target_architecture)
        self.host_simplified_architecture = simplify_architecture(self.host_architecture)

        if self.target_simplified_architecture == "":
            self.target_simplified_architecture = self.target_architecture
        if self.host_simplified_architecture == "":
            self.host_simplified_architecture = self.host_architecture

        if self.target_is_windows():
            env = load_msvc_environment(os.path.join(get_cache_dir(), "msvc_envs.json"), architecture=self.target_simplified_architecture)
            if env is not None:
                for var in env:
                    os.environ[var] = env[var]

    def reload_tools(self) -> None:
        self.reload_env()
        for tool, specified in ((self.c_compiler, self.c_compiler_path_specified), (self.cpp_compiler, self.cpp_compiler_path_specified), (self.as_compiler, self.as_compiler_path_specified), (self.archiver, self.archiver_path_specified), (self.linker, self.linker_path_specified), (self.shared_linker, self.shared_linker_path_specified)):
            if tool is not None:
                if not specified:
                    tool_name = os.path.basename(tool.path)
                    path = search_new_toolchain(tool_name, self.host_simplified_architecture, self.target_simplified_architecture)
                    if path is None:
                        tool.path = ""
                        continue
                    tool.reload(path)
                else:
                    tool.reload()

                if not tool.is_available():
                    raise RuntimeError(error_text(f"PowerMake has changed its environment and is unable to find {tool._name}"))

        if self.c_compiler is not None and not self.c_compiler.is_available():
            self.c_compiler = None
        if self.cpp_compiler is not None and not self.cpp_compiler.is_available():
            self.cpp_compiler = None
        if self.as_compiler is not None and not self.as_compiler.is_available():
            self.as_compiler = None
        if self.archiver is not None and not self.archiver.is_available():
            self.archiver = None
        if self.linker is not None and not self.linker.is_available():
            self.linker = None
        if self.shared_linker is not None and not self.shared_linker.is_available():
            self.shared_linker = None

        if self.asm_compiler is not None:
            self.asm_compiler.reload()
            if not self.asm_compiler.is_available():
                raise RuntimeError(error_text(f"PowerMake has changed its environment and is unable to find {self.asm_compiler._name}"))

    def reset_build_directories(self) -> None:
        if self.debug:
            mode = "debug"
            old_mode = "release"
        else:
            mode = "release"
            old_mode = "debug"

        if self.obj_build_directory == "":
            self.obj_build_directory = os.path.join("build/.objs/", self.target_operating_system, self.target_simplified_architecture, mode)
        else:
            self.obj_build_directory = replace_architecture(self.obj_build_directory.replace(old_mode, mode), self.target_simplified_architecture)

        if self.exe_build_directory == "":
            self.exe_build_directory = os.path.join("build", self.target_operating_system, self.target_simplified_architecture, mode, "bin")
        else:
            self.exe_build_directory = replace_architecture(self.exe_build_directory.replace(old_mode, mode), self.target_simplified_architecture)

        if self.lib_build_directory == "":
            self.lib_build_directory = os.path.join("build", self.target_operating_system, self.target_simplified_architecture, mode, "lib")
        else:
            self.lib_build_directory = replace_architecture(self.lib_build_directory.replace(old_mode, mode), self.target_simplified_architecture)

    def export_json(self) -> T.Dict[str, T.Any]:
        output = {}
        if self.c_compiler is not None:
            output["c_compiler"] = {
                "type": self.c_compiler.type,
                "path": self.c_compiler.path
            }
        return output

    def copy(self) -> T.Any:
        return copy.deepcopy(self)

    def empty_copy(self, local_config: T.Union[str, None] = None) -> T.Any:
        """Generate a new fresh config object without anything inside. By default, even the local config file isn't used.  
        It can be very helpful if you have a local config file specifying a cross compiler but you want to have the default compiler at some point during the compilation step.
        """
        return Config(self.target_name, args_parsed=self._args_parsed, debug=self.debug, rebuild=self.rebuild, verbosity=self.verbosity, nb_jobs=self.nb_jobs, single_file=self.single_file, compile_commands_dir=self.compile_commands_dir, local_config=local_config)

    def set_debug(self, debug: bool = True, reset_optimization: bool = False) -> None:
        self.debug = debug

        self.reset_build_directories()

        if self.debug:
            self.add_defines("DEBUG")
            self.remove_defines("NDEBUG")
            self.add_c_cpp_as_asm_flags("-g")
            if reset_optimization:
                self.set_optimization("-Og")
        else:
            self.add_defines("NDEBUG")
            self.remove_defines("DEBUG")
            self.remove_c_cpp_as_asm_flags("-g")
            if reset_optimization:
                self.set_optimization("-O3")

    def set_target_architecture(self, architecture: str, reload_tools_and_build_dir: bool = True) -> None:
        self.target_architecture = architecture
        if reload_tools_and_build_dir:
            self.reload_tools()
            self.reset_build_directories()
        else:
            self.reload_env()

        if self.target_simplified_architecture in ("x86", "x64"):
            if self.target_simplified_architecture == "x86":
                add = "32"
                remove = "64"
            else:
                add = "64"
                remove = "32"

            if self.target_is_windows():
                self.add_asm_flags("-fwin" + add)
                self.remove_asm_flags("-fwin" + remove, "-felf32", "-felf64", "-fmacho32", "-fmacho64")
            elif self.target_is_macos():
                self.add_asm_flags("-fmacho" + add)
                self.remove_asm_flags("-fmacho" + remove, "-felf32", "-felf64", "-fwin32", "-fwin64")
            else:
                self.add_asm_flags("-felf" + add)
                self.remove_asm_flags("-felf" + remove, "-fwin32", "-fwin64", "-fmacho32", "-fmacho64")

            if self.target_simplified_architecture != self.host_simplified_architecture:
                self.add_c_cpp_flags("-m" + add)
                self.add_ld_flags("-m" + add)
                self.add_shared_linker_flags("-m" + add)
                self.add_as_flags("-m" + add)
                self.remove_c_cpp_flags("-m" + remove)
                self.remove_ld_flags("-m" + remove)
                self.remove_shared_linker_flags("-m" + remove)
                self.remove_as_flags("-m" + remove)

    def set_optimization(self, opt_flag: str) -> None:
        self.remove_c_cpp_as_asm_flags("-O0", "-Og", "-O", "-O1", "-O2", "-O3", "-Os", "-Oz", "-Ofast", "-fomit-frame-pointer")
        self.add_c_cpp_as_asm_flags(opt_flag)

    def get_optimization_level(self) -> T.Union[str, None]:
        for flag in reversed(self.c_cpp_flags):
            if flag in ("-O0", "-Og", "-O", "-O1", "-O2", "-O3", "-Os", "-Oz", "-Ofast", "-fomit-frame-pointer"):
                return flag
        return None

    def host_is_windows(self) -> bool:
        return self.host_operating_system.lower().startswith("win")

    def host_is_linux(self) -> bool:
        return self.host_operating_system.lower().startswith("linux")

    def host_is_macos(self) -> bool:
        return self.host_operating_system.lower().startswith("darwin")

    def target_is_windows(self) -> bool:
        return self.target_operating_system.lower().startswith("win")

    def target_is_linux(self) -> bool:
        return self.target_operating_system.lower().startswith("linux")

    def target_is_macos(self) -> bool:
        return self.target_operating_system.lower().startswith("darwin")

    def target_is_mingw(self) -> bool:
        return self.target_is_windows() and isinstance(self.c_compiler, CompilerGNU)

    def add_defines(self, *defines: str) -> None:
        for define in defines:
            if define not in self.defines:
                self.defines.append(define)

    def remove_defines(self, *defines: str) -> None:
        for define in defines:
            if define in self.defines:
                self.defines.remove(define)

    def add_shared_libs(self, *shared_libs: str) -> None:
        for shared_lib in shared_libs:
            if shared_lib not in self.shared_libs:
                self.shared_libs.append(shared_lib)

    def remove_shared_libs(self, *shared_libs: str) -> None:
        for shared_lib in shared_libs:
            if shared_lib in self.shared_libs:
                self.shared_libs.remove(shared_lib)

    def add_includedirs(self, *includedirs: str) -> None:
        for includedir in includedirs:
            if includedir not in self.additional_includedirs:
                self.additional_includedirs.append(includedir)

    def remove_includedirs(self, *includedirs: str) -> None:
        for includedir in includedirs:
            if includedir in self.additional_includedirs:
                self.additional_includedirs.remove(includedir)

    def add_c_flags(self, *c_flags: str) -> None:
        for c_flag in c_flags:
            if c_flag not in self.c_flags:
                self.c_flags.append(c_flag)

    def remove_c_flags(self, *c_flags: str) -> None:
        for c_flag in c_flags:
            if c_flag in self.c_flags:
                self.c_flags.remove(c_flag)
            if self.c_compiler is None:
                continue
            self.c_compiler.remove_flag(c_flag)

    def add_cpp_flags(self, *cpp_flags: str) -> None:
        for cpp_flag in cpp_flags:
            if cpp_flag not in self.cpp_flags:
                self.cpp_flags.append(cpp_flag)

    def remove_cpp_flags(self, *cpp_flags: str) -> None:
        for cpp_flag in cpp_flags:
            if cpp_flag in self.cpp_flags:
                self.cpp_flags.remove(cpp_flag)
            if self.cpp_compiler is None:
                continue
            self.cpp_compiler.remove_flag(cpp_flag)

    def add_c_cpp_flags(self, *c_cpp_flags: str) -> None:
        self.add_c_flags(*c_cpp_flags)
        self.add_cpp_flags(*c_cpp_flags)

    def remove_c_cpp_flags(self, *c_cpp_flags: str) -> None:
        self.remove_c_flags(*c_cpp_flags)
        self.remove_cpp_flags(*c_cpp_flags)

    def add_c_cpp_as_asm_flags(self, *c_cpp_as_asm_flags: str) -> None:
        self.add_c_flags(*c_cpp_as_asm_flags)
        self.add_cpp_flags(*c_cpp_as_asm_flags)
        self.add_as_flags(*c_cpp_as_asm_flags)
        self.add_asm_flags(*c_cpp_as_asm_flags)

    def remove_c_cpp_as_asm_flags(self, *c_cpp_as_asm_flags: str) -> None:
        self.remove_c_flags(*c_cpp_as_asm_flags)
        self.remove_cpp_flags(*c_cpp_as_asm_flags)
        self.remove_as_flags(*c_cpp_as_asm_flags)
        self.remove_asm_flags(*c_cpp_as_asm_flags)

    def add_as_flags(self, *as_flags: str) -> None:
        for as_flag in as_flags:
            if as_flag not in self.as_flags:
                self.as_flags.append(as_flag)

    def remove_as_flags(self, *as_flags: str) -> None:
        for as_flag in as_flags:
            if as_flag in self.as_flags:
                self.as_flags.remove(as_flag)
            if self.as_compiler is None:
                continue
            self.as_compiler.remove_flag(as_flag)

    def add_asm_flags(self, *asm_flags: str) -> None:
        for asm_flag in asm_flags:
            if asm_flag not in self.asm_flags:
                self.asm_flags.append(asm_flag)

    def remove_asm_flags(self, *asm_flags: str) -> None:
        for asm_flag in asm_flags:
            if asm_flag in self.asm_flags:
                self.asm_flags.remove(asm_flag)
            if self.asm_compiler is None:
                continue
            self.asm_compiler.remove_flag(asm_flag)

    def add_ar_flags(self, *ar_flags: str) -> None:
        for ar_flag in ar_flags:
            if ar_flag not in self.ar_flags:
                self.ar_flags.append(ar_flag)

    def remove_ar_flags(self, *ar_flags: str) -> None:
        for ar_flag in ar_flags:
            if ar_flag in self.ar_flags:
                self.ar_flags.remove(ar_flag)
            if self.archiver is None:
                continue
            self.archiver.remove_flag(ar_flag)

    def add_ld_flags(self, *ld_flags: str) -> None:
        for ld_flag in ld_flags:
            if ld_flag not in self.ld_flags:
                self.ld_flags.append(ld_flag)

    def remove_ld_flags(self, *ld_flags: str) -> None:
        for ld_flag in ld_flags:
            if ld_flag in self.ld_flags:
                self.ld_flags.remove(ld_flag)
            if self.linker is None:
                continue
            self.linker.remove_flag(ld_flag)

    def add_shared_linker_flags(self, *shared_linker_flags: str) -> None:
        for shared_linker_flag in shared_linker_flags:
            if shared_linker_flag not in self.shared_linker_flags:
                self.shared_linker_flags.append(shared_linker_flag)

    def remove_shared_linker_flags(self, *shared_linker_flags: str) -> None:
        for shared_linker_flag in shared_linker_flags:
            if shared_linker_flag in self.shared_linker_flags:
                self.shared_linker_flags.remove(shared_linker_flag)
            if self.shared_linker is None:
                continue
            self.shared_linker.remove_flag(shared_linker_flag)

    def add_exported_headers(self, *exported_headers: str, subfolder: T.Union[str, None] = None) -> None:
        for exported_header in exported_headers:
            if (exported_header, subfolder) not in self.exported_headers:
                self.exported_headers.append((exported_header, subfolder))

    def remove_exported_headers(self, *exported_headers: str, subfolder: T.Union[str, None] = None) -> None:
        for exported_header in exported_headers:
            if (exported_header, subfolder) in self.exported_headers:
                self.exported_headers.remove((exported_header, subfolder))
