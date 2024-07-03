import os
import json
import platform

from .tools import load_tool_tuple_from_file, load_tool_from_tuple, find_tool
from .search_visual_studio import load_msvc_environment
from .compilers import Compiler, CompilerGNU, GenericCompiler, get_all_c_compiler_types, get_all_cpp_compiler_types
from .archivers import Archiver, GenericArchiver, get_all_archiver_types
from .linkers import Linker, GenericLinker, get_all_linker_types


class Config:
    def __init__(self, verbosity: int = 1, local_config: str = "./blazymake_config.json", global_config: str = "/home/user/.blazymake/blazymake_config.json"):
        self.verbosity = verbosity

        self.c_compiler: Compiler = None
        self.cpp_compiler: Compiler = None
        self.archiver: Archiver = None
        self.linker: Linker = None

        self.operating_system: str = None

        self.obj_build_directory: str = None
        self.exe_build_directory: str = None
        self.lib_build_directory: str = None

        self.defines: list[str] = []
        self.additional_includedirs: list[str] = []

        c_compiler_tuple = None
        cpp_compiler_tuple = None
        archiver_tuple = None
        linker_tuple = None

        for path in (local_config, global_config):
            if path is None:
                continue
            try:
                with open(path, "rb") as file:
                    conf: dict = json.load(file)
                    if c_compiler_tuple is None:
                        c_compiler_tuple = load_tool_tuple_from_file(conf, "c_compiler", GenericCompiler, get_all_c_compiler_types)

                    if cpp_compiler_tuple is None:
                        cpp_compiler_tuple = load_tool_tuple_from_file(conf, "cpp_compiler", GenericCompiler, get_all_cpp_compiler_types)

                    if archiver_tuple is None:
                        archiver_tuple = load_tool_tuple_from_file(conf, "archiver", GenericArchiver, get_all_archiver_types)

                    if linker_tuple is None:
                        linker_tuple = load_tool_tuple_from_file(conf, "linker", GenericLinker, get_all_linker_types)

                    if self.operating_system is None and "operating_system" in conf:
                        self.operating_system = conf["operating_system"]

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

            except (OSError, json.JSONDecodeError):
                pass

        if self.operating_system is None:
            self.operating_system = platform.system()

        if self.is_windows():
            load_msvc_environment()

        self.c_compiler = load_tool_from_tuple(c_compiler_tuple, "compiler")
        self.cpp_compiler = load_tool_from_tuple(cpp_compiler_tuple, "compiler")
        self.archiver = load_tool_from_tuple(archiver_tuple, "archiver")
        self.linker = load_tool_from_tuple(linker_tuple, "linker")

        if self.c_compiler is None:
            if self.is_linux():
                self.c_compiler = find_tool(GenericCompiler, "gcc", "clang")
            elif self.is_windows():
                self.c_compiler = find_tool(GenericCompiler, "msvc", "clang-cl", "gcc")

        if self.cpp_compiler is None:
            if self.is_linux():
                self.cpp_compiler = find_tool(GenericCompiler, "g++", "clang++")
            elif self.is_windows():
                self.cpp_compiler = find_tool(GenericCompiler, "msvc", "g++")

        if self.archiver is None:
            if self.is_linux():
                self.archiver = find_tool(GenericArchiver, "ar")
            elif self.is_windows():
                self.archiver = find_tool(GenericArchiver, "msvc")

        if self.linker is None:
            if self.is_linux():
                self.linker = find_tool(GenericLinker, "g++", "clang++", "gcc", "clang")
            elif self.is_windows():
                self.linker = find_tool(GenericLinker, "msvc", "g++", "gcc")

        if self.obj_build_directory is None:
            self.obj_build_directory = os.path.join("build/.objs/", self.operating_system)
        if self.exe_build_directory is None:
            self.exe_build_directory = os.path.join("build", self.operating_system, "bin")
        if self.lib_build_directory is None:
            self.lib_build_directory = os.path.join("build", self.operating_system, "lib")

    def export_json(self):
        return {
            "c_compiler": {
                "type": self.c_compiler.type,
                "path": self.c_compiler.path
            }
        }

    def is_windows(self):
        return self.operating_system.lower().startswith("win")

    def is_linux(self):
        return self.operating_system.lower().startswith("linux")

    def is_mingw(self):
        return self.is_windows() and "gcc" in isinstance(self.c_compiler, CompilerGNU)

    def add_defines(self, *defines: str) -> None:
        for define in defines:
            if define not in self.defines:
                self.defines.append(define)

    def remove_defines(self, *defines: str) -> None:
        for define in defines:
            self.defines.remove(define)

    def add_includedirs(self, *includedirs: str) -> None:
        for includedir in includedirs:
            if includedir not in self.additional_includedirs:
                self.additional_includedirs.append(includedir)

    def remove_includedirs(self, *includedirs: str) -> None:
        for includedir in includedirs:
            self.additional_includedirs.remove(includedir)
