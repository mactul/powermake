import os
import tempfile


def makedirs(path: str, exist_ok: bool = True) -> None:
    if path != '':
        os.makedirs(path, exist_ok=exist_ok)


def join_absolute_paths(path1: str, path2: str) -> str:
    return os.path.normpath(path1 + "/" + os.path.splitdrive(path2)[1].replace("..", "__"))


_tempdir = None
_empty_file = None
def get_empty_file() -> str:
    global _empty_file
    global _tempdir
    if os.path.exists("/dev/null"):
        return "/dev/null"
    if _empty_file is None or not os.path.exists(_empty_file):
        _tempdir = tempfile.TemporaryDirectory("powermake_utils")
        _empty_file = os.path.join(_tempdir.name, "emptyfile")
        file = open(_empty_file, "w")
        file.close()

    return _empty_file
