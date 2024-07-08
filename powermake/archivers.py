import abc

from .tools import Tool


class Archiver(Tool, abc.ABC):
    static_lib_extension = None

    def __init__(self, path):
        Tool.__init__(self, path)

    @abc.abstractmethod
    def basic_archive_command(self, outputfile: str, inputfiles: set[str], args: list[str] = []) -> list[str]:
        return []


class ArchiverGNU(Archiver):
    type = "gnu"
    static_lib_extension = ".a"

    def __init__(self, path: str = "ar"):
        super().__init__(path)

    def basic_archive_command(self, outputfile: str, inputfiles: set[str], args: list[str] = []) -> list[str]:
        return [self.path, "-cr", outputfile, *inputfiles, *args]


class ArchiverAR(ArchiverGNU):
    type = "ar"

    def __init__(self, path: str = "ar"):
        super().__init__(path)


class ArchiverLLVM_AR(ArchiverGNU):
    type = "llvm-ar"

    def __init__(self, path: str = "llvm-ar"):
        super().__init__(path)


class ArchiverMSVC(Archiver):
    type = "msvc"
    static_lib_extension = ".lib"

    def __init__(self, path: str = "lib"):
        super().__init__(path)

    def basic_archive_command(self, outputfile: str, inputfiles: set[str], args: list[str] = []) -> list[str]:
        return [self.path, "/nologo", *args, "/out:"+outputfile, *inputfiles]


_archiver_types: dict[str, Archiver] = {
    "gnu": ArchiverGNU,
    "ar": ArchiverAR,
    "llvm-ar": ArchiverAR,
    "msvc": ArchiverMSVC
}


def GenericArchiver(archiver_type: str) -> Archiver:
    if archiver_type not in _archiver_types:
        return None
    return _archiver_types[archiver_type]


def get_all_archiver_types() -> set[str]:
    return _archiver_types.keys()
