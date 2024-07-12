import os
import json
import platform

from .tools import load_tool_tuple_from_file, load_tool_from_tuple, find_tool
from .search_visual_studio import load_msvc_environment
from .architecture import simplify_architecture
from .compilers import Compiler, CompilerGNU, GenericCompiler, get_all_c_compiler_types, get_all_cpp_compiler_types
from .archivers import Archiver, GenericArchiver, get_all_archiver_types
from .linkers import Linker, GenericLinker, get_all_linker_types


class Config:
    def __init__(self, target_name, *, debug: bool = False, rebuild: bool = False, verbosity: int = 1, nb_jobs: int = 8, single_file: str = None, local_config: str = "./powermake_config.json", global_config: str = None):
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
        self.additional_includedirs: list[str] = []
        self.c_flags: list[str] = []
        self.cpp_flags: list[str] = []
        self.c_cpp_flags: list[str] = []
        self.ar_flags: list[str] = []
        self.ld_flags: list[str] = []

        self.exported_headers: list[tuple[str, str]] = []

        c_compiler_tuple = None
        cpp_compiler_tuple = None
        archiver_tuple = None
        linker_tuple = None

        if global_config is None:
            global_config = os.getenv("POWERMAKE_CONFIG")
            if global_config is None:
                global_config = os.path.normpath(os.path.expanduser("~/.powermake/powermake_config.json"))

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

                    if "defines" in conf and isinstance(conf["defines"], list):
                        for define in conf["defines"]:
                            if isinstance(define, str) and define not in self.defines:
                                self.defines.append(define)

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
                            if isinstance(c_cpp_flag, str) and c_cpp_flag not in self.c_cpp_flags:
                                self.c_cpp_flags.append(c_cpp_flag)

                    if "ar_flags" in conf and isinstance(conf["ar_flags"], list):
                        for ar_flag in conf["ar_flags"]:
                            if isinstance(ar_flag, str) and ar_flag not in self.ar_flags:
                                self.ar_flags.append(ar_flag)

                    if "ld_flags" in conf and isinstance(conf["ld_flags"], list):
                        for ld_flag in conf["ld_flags"]:
                            if isinstance(ld_flag, str) and ld_flag not in self.ld_flags:
                                self.ld_flags.append(ld_flag)

                    if "exported_headers" in conf and isinstance(conf["exported_headers"], list):
                        for exported_header in conf["exported_headers"]:
                            if isinstance(exported_header, str) and exported_header not in self.exported_headers:
                                self.exported_headers.append(exported_header)

            except (OSError, json.JSONDecodeError):
                pass

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

        self.c_compiler = load_tool_from_tuple(c_compiler_tuple, "compiler")
        self.cpp_compiler = load_tool_from_tuple(cpp_compiler_tuple, "compiler")
        self.archiver = load_tool_from_tuple(archiver_tuple, "archiver")
        self.linker = load_tool_from_tuple(linker_tuple, "linker")

        if self.c_compiler is None:
            if self.target_is_linux():
                self.c_compiler = find_tool(GenericCompiler, "gcc", "clang")
            elif self.target_is_windows():
                self.c_compiler = find_tool(GenericCompiler, "msvc", "clang-cl", "gcc")

        if self.cpp_compiler is None:
            if self.target_is_linux():
                self.cpp_compiler = find_tool(GenericCompiler, "g++", "clang++")
            elif self.target_is_windows():
                self.cpp_compiler = find_tool(GenericCompiler, "msvc", "g++")

        if self.archiver is None:
            if self.target_is_linux():
                self.archiver = find_tool(GenericArchiver, "ar")
            elif self.target_is_windows():
                self.archiver = find_tool(GenericArchiver, "msvc")

        if self.linker is None:
            if self.target_is_linux():
                self.linker = find_tool(GenericLinker, "g++", "clang++", "gcc", "clang")
            elif self.target_is_windows():
                self.linker = find_tool(GenericLinker, "msvc", "g++", "gcc")

        if self.debug:
            mode = "debug"
        else:
            mode = "release"
        if self.obj_build_directory is None:
            self.obj_build_directory = os.path.join("build/.objs/", self.target_operating_system, self.target_simplified_architecture, mode)
        if self.exe_build_directory is None:
            self.exe_build_directory = os.path.join("build", self.target_operating_system, self.target_simplified_architecture, mode, "bin")
        if self.lib_build_directory is None:
            self.lib_build_directory = os.path.join("build", self.target_operating_system, self.target_simplified_architecture, mode, "lib")

        if self.debug:
            self.add_defines("DEBUG")
            self.add_c_cpp_flags("-g")
        else:
            self.add_defines("NDEBUG")

    def export_json(self):
        return {
            "c_compiler": {
                "type": self.c_compiler.type,
                "path": self.c_compiler.path
            }
        }

    def target_is_windows(self):
        return self.target_operating_system.lower().startswith("win")

    def target_is_linux(self):
        return self.target_operating_system.lower().startswith("linux")

    def target_is_mingw(self):
        return self.target_is_windows() and "gcc" in isinstance(self.c_compiler, CompilerGNU)

    def add_defines(self, *defines: str) -> None:
        for define in defines:
            if define not in self.defines:
                self.defines.append(define)

    def remove_defines(self, *defines: str) -> None:
        for define in defines:
            if define in self.defines:
                self.defines.remove(define)

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
        for c_cpp_flag in c_cpp_flags:
            if c_cpp_flag not in self.c_cpp_flags:
                self.c_cpp_flags.append(c_cpp_flag)

    def remove_c_cpp_flags(self, *c_cpp_flags: str) -> None:
        for c_cpp_flag in c_cpp_flags:
            if c_cpp_flag in self.c_cpp_flags:
                self.c_cpp_flags.remove(c_cpp_flag)

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

    def add_exported_headers(self, *exported_headers: str, subfolder: str = None) -> None:
        for exported_header in exported_headers:
            if (exported_header, subfolder) not in self.exported_headers:
                self.exported_headers.append((exported_header, subfolder))

    def remove_exported_headers(self, *exported_headers: str, subfolder: str = None) -> None:
        for exported_header in exported_headers:
            if (exported_header, subfolder) in self.exported_headers:
                self.exported_headers.remove((exported_header, subfolder))
