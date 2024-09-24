import os


def makedirs(path: str, exist_ok: bool = True) -> None:
    if path != '':
        os.makedirs(path, exist_ok=exist_ok)
