import abc
import shutil

from .tools import Tool


class Archiver(Tool, abc.ABC):
    def __init__(self, archiver_path):
        self.archiver_path = shutil.which(archiver_path)
        self.static_lib_extension = None

    def is_available(self):
        return self.archiver_path is not None

    @abc.abstractmethod
    def basic_archive_command(self, outputfile: str, inputfiles: list[str], args: list[str] = []) -> list[str]:
        return []


class ArchiverGNU(Archiver):
    def __init__(self, archiver_path: str = "ar"):
        super().__init__(archiver_path)
        self.static_lib_extension = ".a"

    def basic_archive_command(self, outputfile: str, inputfiles: list[str], args: list[str] = []) -> list[str]:
        return [self.archiver_path, "-cr", outputfile, *inputfiles, *args]


class ArchiverAR(ArchiverGNU):
    def __init__(self, archiver_path: str = "ar"):
        super().__init__(archiver_path)


class ArchiverLLVM_AR(ArchiverGNU):
    def __init__(self, archiver_path: str = "llvm-ar"):
        super().__init__(archiver_path)


class ArchiverMSVC(Archiver):
    def __init__(self, archiver_path: str = "lib"):
        super().__init__(archiver_path)
        self.static_lib_extension = ".lib"

    def basic_archive_command(self, outputfile: str, inputfiles: list[str], args: list[str] = []) -> list[str]:
        return [self.archiver_path, "/nologo", *args, "/out:"+outputfile, *inputfiles]


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


def get_all_archiver_types() -> list[str]:
    return _archiver_types.keys()
