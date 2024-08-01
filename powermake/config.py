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
import json
import platform

from .tools import load_tool_tuple_from_file, load_tool_from_tuple, find_tool
from .search_visual_studio import load_msvc_environment
from .architecture import simplify_architecture
from .compilers import Compiler, CompilerGNU, GenericCompiler, get_all_c_compiler_types, get_all_cpp_compiler_types
from .archivers import Archiver, GenericArchiver, get_all_archiver_types
from .linkers import Linker, GenericLinker, get_all_linker_types
from .shared_linkers import SharedLinker, GenericSharedLinker, get_all_shared_linker_types


def get_global_config():
    global_config = os.getenv("POWERMAKE_CONFIG")
    if global_config is None:
        global_config = os.path.normpath(os.path.expanduser("~/.powermake/powermake_config.json"))
    return global_config


class Config:
    def __init__(self, target_name, *, debug: bool = False, rebuild: bool = False, verbosity: int = 1, nb_jobs: int = 0, single_file: str = None, local_config: str = "./powermake_config.json", global_config: str = None):
        """Create an object that loads all configurations files and search for compilers.

        This objects hold all the configuration for the compilation.

        If you want to compile multiple set of files with different settings, you have to make a copy of this object and modify the copy.
        """
        self.target_name = target_name
        self.verbosity = verbosity
        self.debug = debug
        self.rebuild = rebuild
        self.nb_jobs = nb_jobs
        self.single_file = single_file

        self.c_compiler: Compiler = None
        self.cpp_compiler: Compiler = None
        self.archiver: Archiver = None
        self.linker: Linker = None
        self.shared_linker: SharedLinker = None

        self.target_operating_system: str = None
        self.host_operating_system: str = None

        self.target_architecture: str = None
        self.target_simplified_architecture: str = None
        self.host_architecture: str = None
        self.host_simplified_architecture: str = None

        self.obj_build_directory: str = None
        self.exe_build_directory: str = None
        self.lib_build_directory: str = None

        self.defines: list[str] = []
        self.shared_libs: list[str] = []
        self.additional_includedirs: list[str] = []
        self.c_flags: list[str] = []
        self.cpp_flags: list[str] = []
        self.ar_flags: list[str] = []
        self.ld_flags: list[str] = []
        self.shared_linker_flags: list[str] = []

        self.exported_headers: list[tuple[str, str]] = []

        c_compiler_tuple = None
        cpp_compiler_tuple = None
        archiver_tuple = None
        linker_tuple = None
        shared_linker_tuple = None

        if global_config is None:
            global_config = get_global_config()

        for path in (local_config, global_config):
            if path is None:
                continue
            try:
                with open(path, "r") as file:
                    conf: dict = json.load(file)
                    if c_compiler_tuple is None:
                        c_compiler_tuple = load_tool_tuple_from_file(conf, "c_compiler", GenericCompiler, get_all_c_compiler_types)

                    if cpp_compiler_tuple is None:
                        cpp_compiler_tuple = load_tool_tuple_from_file(conf, "cpp_compiler", GenericCompiler, get_all_cpp_compiler_types)

                    if archiver_tuple is None:
                        archiver_tuple = load_tool_tuple_from_file(conf, "archiver", GenericArchiver, get_all_archiver_types)

                    if linker_tuple is None:
                        linker_tuple = load_tool_tuple_from_file(conf, "linker", GenericLinker, get_all_linker_types)

                    if shared_linker_tuple is None:
                        shared_linker_tuple = load_tool_tuple_from_file(conf, "shared_linker", GenericSharedLinker, get_all_shared_linker_types)

                    if self.target_operating_system is None and "target_operating_system" in conf:
                        self.target_operating_system = conf["target_operating_system"]
                    if self.host_operating_system is None and "host_operating_system" in conf:
                        self.host_operating_system = conf["host_operating_system"]

                    if self.target_architecture is None and "target_architecture" in conf:
                        self.target_architecture = conf["target_architecture"]
                    if self.host_architecture is None and "host_architecture" in conf:
                        self.host_architecture = conf["host_architecture"]

                    if self.obj_build_directory is None and "obj_build_directory" in conf:
                        self.obj_build_directory = conf["obj_build_directory"]
                    if self.exe_build_directory is None and "exe_build_directory" in conf:
                        self.exe_build_directory = conf["exe_build_directory"]
                    if self.lib_build_directory is None and "lib_build_directory" in conf:
                        self.lib_build_directory = conf["lib_build_directory"]

                    if self.nb_jobs == 0 and "nb_jobs" in conf:
                        self.nb_jobs = conf["nb_jobs"]

                    if "defines" in conf and isinstance(conf["defines"], list):
                        for define in conf["defines"]:
                            if isinstance(define, str) and define not in self.defines:
                                self.defines.append(define)

                    if "shared_libs" in conf and isinstance(conf["shared_links"], list):
                        for shared_link in conf["shared_links"]:
                            if isinstance(shared_link, str) and shared_link not in self.shared_links:
                                self.shared_links.append(shared_link)

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
                            elif isinstance(exported_header, list) and len(exported_header) == 2 and exported_header not in self.exported_headers:
                                self.exported_headers.append((exported_header[0], exported_header[1]))

            except OSError:
                pass

        if self.nb_jobs == 0:
            self.nb_jobs = os.cpu_count() or 8

        if self.target_operating_system is None:
            self.target_operating_system = platform.system()
        if self.host_operating_system is None:
            self.host_operating_system = platform.system()

        if self.target_architecture is None:
            self.target_architecture = platform.machine()
        if self.host_architecture is None:
            self.host_architecture = platform.machine()

        self.target_simplified_architecture = simplify_architecture(self.target_architecture)
        self.host_simplified_architecture = simplify_architecture(self.host_architecture)

        if self.target_is_windows():
            env = load_msvc_environment(os.path.join(os.path.dirname(global_config), "msvc_envs.json"), architecture=self.target_simplified_architecture)
            if env is not None:
                for var in env:
                    os.environ[var] = env[var]

        if self.target_simplified_architecture == "x86" or self.target_simplified_architecture == "arm32":
            self.add_c_cpp_flags("-m32")
            self.add_ld_flags("-m32")
            self.add_shared_linker_flags("-m32")
        elif self.target_simplified_architecture == "x64" or self.target_simplified_architecture == "arm64":
            self.add_c_cpp_flags("-m64")
            self.add_ld_flags("-m64")
            self.add_shared_linker_flags("-m64")

        self.c_compiler = load_tool_from_tuple(c_compiler_tuple, "compiler")
        self.cpp_compiler = load_tool_from_tuple(cpp_compiler_tuple, "compiler")
        self.archiver = load_tool_from_tuple(archiver_tuple, "archiver")
        self.linker = load_tool_from_tuple(linker_tuple, "linker")

        if self.c_compiler is None and self.cpp_compiler is not None:
            if self.cpp_compiler.type == "g++":
                self.c_compiler = find_tool(GenericCompiler, "gcc")
            elif self.cpp_compiler.type == "clang++":
                self.c_compiler = find_tool(GenericCompiler, "clang")
            elif self.cpp_compiler.type == "clang-cl":
                self.c_compiler = find_tool(GenericCompiler, "clang-cl")
            elif self.cpp_compiler.type == "msvc":
                self.c_compiler = find_tool(GenericCompiler, "msvc")
        if self.c_compiler is None:
            if self.target_is_linux():
                self.c_compiler = find_tool(GenericCompiler, "gcc", "clang")
            elif self.target_is_windows():
                self.c_compiler = find_tool(GenericCompiler, "msvc", "gcc", "clang-cl")
        
        if self.cpp_compiler is None and self.c_compiler is not None:
            if self.c_compiler.type == "gcc":
                self.cpp_compiler = find_tool(GenericCompiler, "g++")
            elif self.c_compiler.type == "clang":
                self.cpp_compiler = find_tool(GenericCompiler, "clang++")
            elif self.c_compiler.type == "clang-cl":
                self.cpp_compiler = find_tool(GenericCompiler, "clang-cl")
            elif self.c_compiler.type == "msvc":
                self.cpp_compiler = find_tool(GenericCompiler, "msvc")
        if self.cpp_compiler is None:
            if self.target_is_linux():
                self.cpp_compiler = find_tool(GenericCompiler, "g++", "clang++")
            elif self.target_is_windows():
                self.cpp_compiler = find_tool(GenericCompiler, "msvc", "g++", "clang-cl")

        if self.archiver is None:
            if self.target_is_linux():
                self.archiver = find_tool(GenericArchiver, "ar", "llvm-ar")
            elif self.target_is_windows():
                self.archiver = find_tool(GenericArchiver, "msvc")

        if self.linker is None and self.cpp_compiler is not None:
            self.linker = find_tool(GenericLinker, self.cpp_compiler.type)
        if self.linker is None and self.c_compiler is not None:
            self.linker = find_tool(GenericLinker, self.c_compiler.type)
        if self.linker is None:
            if self.target_is_linux():
                self.linker = find_tool(GenericLinker, "g++", "clang++", "gcc", "clang")
            elif self.target_is_windows():
                self.linker = find_tool(GenericLinker, "msvc", "g++", "gcc", "clang-cl")
        
        if self.shared_linker is None and self.linker is not None:
            self.shared_linker = find_tool(GenericSharedLinker, self.linker.type)
        if self.shared_linker is None:
            if self.target_is_linux():
                self.shared_linker = find_tool(GenericSharedLinker, "g++", "clang++", "gcc", "clang")
            elif self.target_is_windows():
                self.shared_linker = find_tool(GenericSharedLinker, "msvc", "g++", "gcc", "clang-cl")

        self.set_debug(self.debug, True)

    @property
    def c_cpp_flags(self):
        return self.c_flags + self.cpp_flags

    def export_json(self):
        return {
            "c_compiler": {
                "type": self.c_compiler.type,
                "path": self.c_compiler.path
            }
        }

    def set_debug(self, debug: bool = True, reset_optimization: bool = False):
        self.debug = debug
        if self.debug:
            mode = "debug"
            old_mode = "release"
        else:
            mode = "release"
            old_mode = "debug"

        if self.obj_build_directory is None:
            self.obj_build_directory = os.path.join("build/.objs/", self.target_operating_system, self.target_simplified_architecture, mode)
        else:
            self.obj_build_directory = self.obj_build_directory.replace(old_mode, mode)

        if self.exe_build_directory is None:
            self.exe_build_directory = os.path.join("build", self.target_operating_system, self.target_simplified_architecture, mode, "bin")
        else:
            self.exe_build_directory = self.exe_build_directory.replace(old_mode, mode)

        if self.lib_build_directory is None:
            self.lib_build_directory = os.path.join("build", self.target_operating_system, self.target_simplified_architecture, mode, "lib")
        else:
            self.lib_build_directory = self.lib_build_directory.replace(old_mode, mode)

        if self.debug:
            self.add_defines("DEBUG")
            self.remove_defines("NDEBUG")
            self.add_c_cpp_flags("-g")
            if reset_optimization:
                self.set_optimization("-O0")
        else:
            self.add_defines("NDEBUG")
            self.remove_defines("DEBUG")
            self.remove_c_cpp_flags("-g")
            if reset_optimization:
                self.set_optimization("-O3")

    def set_optimization(self, opt_flag: str):
        self.remove_c_cpp_flags("-O0", "-Og", "-O1", "-O2", "-O3", "-Os", "-Oz", "-Ofast", "-fomit-frame-pointer")
        self.add_c_cpp_flags(opt_flag)

    def get_optimization_level(self):
        for flag in reversed(self.c_cpp_flags):
            if flag in ("-O0", "-Og", "-O1", "-O2", "-O3", "-Os", "-Oz", "-Ofast", "-fomit-frame-pointer"):
                return flag
        return None

    def target_is_windows(self):
        return self.target_operating_system.lower().startswith("win")

    def target_is_linux(self):
        return self.target_operating_system.lower().startswith("linux")

    def target_is_mingw(self):
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

    def add_cpp_flags(self, *cpp_flags: str) -> None:
        for cpp_flag in cpp_flags:
            if cpp_flag not in self.cpp_flags:
                self.cpp_flags.append(cpp_flag)

    def remove_cpp_flags(self, *cpp_flags: str) -> None:
        for cpp_flag in cpp_flags:
            if cpp_flag in self.cpp_flags:
                self.cpp_flags.remove(cpp_flag)

    def add_c_cpp_flags(self, *c_cpp_flags: str) -> None:
        self.add_c_flags(*c_cpp_flags)
        self.add_cpp_flags(*c_cpp_flags)

    def remove_c_cpp_flags(self, *c_cpp_flags: str) -> None:
        self.remove_c_flags(*c_cpp_flags)
        self.remove_cpp_flags(*c_cpp_flags)

    def add_ar_flags(self, *ar_flags: str) -> None:
        for ar_flag in ar_flags:
            if ar_flag not in self.ar_flags:
                self.ar_flags.append(ar_flag)

    def remove_ar_flags(self, *ar_flags: str) -> None:
        for ar_flag in ar_flags:
            if ar_flag in self.ar_flags:
                self.ar_flags.remove(ar_flag)

    def add_ld_flags(self, *ld_flags: str) -> None:
        for ld_flag in ld_flags:
            if ld_flag not in self.ld_flags:
                self.ld_flags.append(ld_flag)

    def remove_ld_flags(self, *ld_flags: str) -> None:
        for ld_flag in ld_flags:
            if ld_flag in self.ld_flags:
                self.ld_flags.remove(ld_flag)
    
    def add_shared_linker_flags(self, *shared_linker_flags: str) -> None:
        for shared_linker_flag in shared_linker_flags:
            if shared_linker_flag not in self.shared_linker_flags:
                self.shared_linker_flags.append(shared_linker_flag)

    def remove_shared_linker_flags(self, *shared_linker_flags: str) -> None:
        for shared_linker_flag in shared_linker_flags:
            if shared_linker_flag in self.shared_linker_flags:
                self.shared_linker_flags.remove(shared_linker_flag)

    def add_exported_headers(self, *exported_headers: str, subfolder: str = None) -> None:
        for exported_header in exported_headers:
            if (exported_header, subfolder) not in self.exported_headers:
                self.exported_headers.append((exported_header, subfolder))

    def remove_exported_headers(self, *exported_headers: str, subfolder: str = None) -> None:
        for exported_header in exported_headers:
            if (exported_header, subfolder) in self.exported_headers:
                self.exported_headers.remove((exported_header, subfolder))
