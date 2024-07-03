import abc

from .tools import Tool


class Compiler(Tool, abc.ABC):
    def __init__(self, path, type):
        Tool.__init__(self, path, type)
        self.type = None
        self.obj_extension = None
        self.add_defines_option = None
        self.add_includedirs_option = None

    @abc.abstractmethod
    def basic_compile_command(self, outputfile: str, inputfiles: list[str], defines: list[str], includedirs: list[str], args: list[str] = []) -> list[str]:
        return []


class CompilerGNU(Compiler):
    def __init__(self, path: str = "cc", type: str = "gnu"):
        super().__init__(path, type)
        self.obj_extension = ".o"
        self.add_defines_option = "-D"
        self.add_includedirs_option = "-I"

    def basic_compile_command(self, outputfile: str, inputfiles: list[str], defines: list[str], includedirs: list[str], args: list[str] = []) -> list[str]:
        return [self.path, "-c", "-o", outputfile, *inputfiles, *args] + [f"-D{define}" for define in defines] + [f"-I{includedir}" for includedir in includedirs]


class CompilerGCC(CompilerGNU):
    def __init__(self, path: str = "gcc"):
        super().__init__(path, "gcc")


class CompilerGPlusPlus(CompilerGNU):
    def __init__(self, path: str = "g++"):
        super().__init__(path, "g++")


class CompilerClang(CompilerGNU):
    def __init__(self, path: str = "clang"):
        super().__init__(path, "clang")


class CompilerClangPlusPlus(CompilerGNU):
    def __init__(self, path: str = "clang++"):
        super().__init__(path, "clang++")


class CompilerMSVC(Compiler):
    def __init__(self, path: str = "cl", type: str = "msvc"):
        super().__init__(path, type)
        self.obj_extension = ".obj"
        self.add_defines_option = "/D"
        self.add_includedirs_option = "/I"

    def basic_compile_command(self, outputfile: str, inputfiles: list[str], defines: list[str], includedirs: list[str], args: list[str] = []) -> list[str]:
        return [self.path, "/c", "/nologo", "/Fo" + outputfile, *inputfiles, *args] + [f"/D{define}" for define in defines] + [f"/I{includedir}" for includedir in includedirs]


class CompilerClang_CL(CompilerMSVC):
    def __init__(self, path: str = "clang-cl"):
        super().__init__(path, "clang-cl")


_c_compiler_types: dict[str, Compiler] = {
    "gnu": CompilerGNU,
    "gcc": CompilerGCC,
    "clang": CompilerClang,
    "msvc": CompilerMSVC,
    "clang-cl": CompilerClang_CL
}

_cpp_compiler_types: dict[str, Compiler] = {
    "g++": CompilerGPlusPlus,
    "clang++": CompilerClangPlusPlus,
    "msvc": CompilerMSVC
}

_compiler_types: dict[str, Compiler] = {
    **_c_compiler_types,
    **_cpp_compiler_types
}


def GenericCompiler(compiler_type: str) -> Compiler:
    if compiler_type not in _compiler_types:
        return None
    return _compiler_types[compiler_type]


def get_all_compiler_types() -> list[str]:
    return _compiler_types.keys()


def get_all_c_compiler_types() -> list[str]:
    return _c_compiler_types.keys()


def get_all_cpp_compiler_types() -> list[str]:
    return _cpp_compiler_types.keys()
