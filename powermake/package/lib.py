import typing as T
from dataclasses import dataclass
from ..version_parser import Version


@dataclass
class Lib:
    includedir: str
    version: T.Union[Version, None]
    lib_file: str
    soname: T.Union[str, None]
    is_system: bool