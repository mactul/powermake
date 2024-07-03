import abc
import shutil

from .tools import Tool


class Linker(Tool, abc.ABC):
    def __init__(self, linker_path):
        self.linker_path = shutil.which(linker_path)
        self.exe_extension = None

    def is_available(self):
        return self.linker_path is not None

    @abc.abstractmethod
    def basic_link_command(self, outputfile: str, inputfiles: list[str], args: list[str] = []) -> list[str]:
        return []


class LinkerGNU(Linker):
    def __init__(self, linker_path: str = "cc"):
        super().__init__(linker_path)
        self.exe_extension = ""

    def basic_link_command(self, outputfile: str, inputfiles: list[str], args: list[str] = []) -> list[str]:
        return [self.linker_path, "-o", outputfile, *inputfiles, *args]


class LinkerGCC(LinkerGNU):
    def __init__(self, linker_path: str = "gcc"):
        super().__init__(linker_path)


class LinkerGPlusPlus(LinkerGNU):
    def __init__(self, linker_path: str = "g++"):
        super().__init__(linker_path)


class LinkerClang(LinkerGNU):
    def __init__(self, linker_path: str = "clang"):
        super().__init__(linker_path)


class LinkerClangPlusPlus(LinkerGNU):
    def __init__(self, linker_path: str = "clang++"):
        super().__init__(linker_path)


class LinkerMSVC(Linker):
    def __init__(self, archiver_path: str = "link"):
        super().__init__(archiver_path)
        self.exe_extension = ".exe"

    def basic_link_command(self, outputfile: str, inputfiles: list[str], args: list[str] = []) -> list[str]:
        return [self.linker_path, "/nologo", *args, "/out:" + outputfile, *inputfiles]


_linker_types: dict[str, Linker] = {
    "gnu": LinkerGNU,
    "gcc": LinkerGCC,
    "g++": LinkerGPlusPlus,
    "clang": LinkerClang,
    "clang++": LinkerClangPlusPlus,
    "msvc": LinkerMSVC
}


def GenericLinker(linker_type: str) -> Linker:
    if linker_type not in _linker_types:
        return None
    return _linker_types[linker_type]


def get_all_linker_types() -> list[str]:
    return _linker_types.keys()
