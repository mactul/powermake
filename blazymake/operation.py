import os
import subprocess
from .config import Config


def resolve_path(current_folder: str, additional_includedirs: list[str], filepath: str) -> str:
    path = os.path.join(current_folder, filepath)
    if os.path.exists(path):
        return path
    for folder in additional_includedirs:
        path = os.path.join(folder, filepath)
        if os.path.exists(path):
            return path
    return None


def file_is_uptodate(output_date: float, filename: str, additional_includedirs: list[str], headers_already_found: list[str] = []) -> bool:
    try:
        if os.path.getmtime(filename) >= output_date:
            return False
    except OSError:
        return False

    if not filename.endswith((".c", ".cpp", ".h", ".hpp")):
        return True

    headers_found = []
    file = open(filename, "rb")

    # The four lines under this comment are here for the compatibility with python < 3.8
    # They are equivalent to `while line := file.readline():`
    while True:
        line = file.readline()
        if not line:
            break

        i = 0
        while i < len(line) and (line[i] == ' ' or line[i] == '\t'):
            i += 1
        if i >= len(line):
            continue
        if line[i] != "#":
            continue
        i += 1
        while i < len(line) and (line[i] == ' ' or line[i] == '\t'):
            i += 1
        if i >= len(line):
            continue
        if line[i:].startswith("include"):
            i += len("include")
            if i >= len(line) or (line[i] != ' ' and line[i] != '\t'):
                continue
            i += 1
            while i < len(line) and (line[i] == ' ' or line[i] == '\t'):
                i += 1
            if i >= len(line) or (line[i] != '<' and line[i] != '"'):
                continue
            i += 1
            j = i
            while j < len(line) and line[j] != '>' and line[j] != '"':
                j += 1
            if j >= len(line):
                continue

            if line[i:j] not in headers_found:
                headers_found.append(line[i:j])

    file.close()

    if len(headers_found) == 0:
        return True

    current_folder = os.path.dirname(filename)
    new_paths = []
    for i in range(len(headers_found)):
        path = resolve_path(current_folder, additional_includedirs, headers_found[i])
        if path is not None and path not in headers_already_found:
            headers_already_found.append(path)
            new_paths.append(path)

    for path in new_paths:
        if not file_is_uptodate(path, additional_includedirs, headers_already_found):
            return False

    return True


def needs_update(outputfile: str, dependencies: list[str], additional_includedirs: list[str]):
    try:
        output_date = os.path.getmtime(outputfile)
    except OSError:
        return True
    headers_already_found = []
    for dep in dependencies:
        if not file_is_uptodate(output_date, dep, additional_includedirs, headers_already_found):
            return True

    return False


class Operation:
    def __init__(self, outputfile: str, dependencies: list[str], config: Config, command: list[str]):
        self.outputfile = outputfile
        self.dependencies = dependencies
        self._hidden_dependencies = None
        self.command = command
        self.config = config

    def execute(self, force: bool = False) -> int:
        if force or needs_update(self.outputfile, self.dependencies, self.config.additional_includedirs):
            if self.config.verbosity > 0:
                print(f"Compiling {os.path.basename(self.outputfile)}")
            if self.config.verbosity > 1:
                print(self.command)
            if subprocess.run(self.command).returncode == 0:
                return self.outputfile
            else:
                return False
        return self.outputfile
