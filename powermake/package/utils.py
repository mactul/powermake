import os
import typing as T

def find_closest_include_dir(dir: str) -> T.Union[str, None]:
    dir = os.path.abspath(dir)
    while len(dir) > 1:
        include = os.path.join(dir, "include")
        if os.path.isdir(include):
            return include
        dir = os.path.dirname(dir)
    return None