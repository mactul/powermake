import os
import traceback

from .display import error_text, bold_text, dim_text


class PowerMakeException(Exception):
    exc_type: str = "Unknown Error"

class PowerMakeValueError(PowerMakeException):
    exc_type: str = "Value Error"

class PowerMakeRuntimeError(PowerMakeException):
    exc_type: str = "Runtime Error"

class PowerMakeCommandError(PowerMakeRuntimeError):
    exc_type: str = "Command Error"

def print_powermake_traceback(e: PowerMakeException) -> None:
    print(error_text(e.exc_type), ":", e)
    tab = 0
    tb_list = traceback.extract_tb(e.__traceback__)
    index = 0
    while index < len(tb_list) and os.path.samefile(os.path.split(tb_list[index].filename)[0], os.path.split(__file__)[0]):
        index += 1
    for error in tb_list[index:]:
        if os.path.samefile(os.path.split(error.filename)[0], os.path.split(__file__)[0]):
            break
        print(" " * tab + f"From \"{bold_text(error.filename)}\", line {bold_text(error.lineno)} in {bold_text(error.name)}")
        print(" " * tab + dim_text(str(error.lineno) + " | "), error.line)
        tab += 4