import typing as T
from threading import Lock

_makefile_targets_mutex = Lock()
_makefile_targets: T.List[T.List[T.Tuple[bool, str, T.Iterable[str], T.Union[str, T.List[str]], str]]] = [] # [[(phony, target, dependencies, command, tool), ], ]
