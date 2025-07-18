import os
import sys
import powermake
import powermake.exceptions
from unittest import mock

class FakePrint:
    def __init__(self):
        self.full_print_content = ""

    def print(self, *strings: any):
        for string in strings:
            self.full_print_content += str(string) + " "
        self.full_print_content += "\n"

def on_build(config: powermake.Config):
    powermake.compile_files(config, {"non_existing_file.c"})

def fail(_):
    raise NotImplementedError("test")

def will_fail():
    stdout = sys.stdout
    sys.stdout = open(os.devnull, 'w')
    with mock.patch("powermake.args_parser.exit", new=fail):
        try:
            powermake.run("test", build_callback=on_build)
        except NotImplementedError:
            pass
    sys.stdout.close()
    sys.stdout = stdout

def run_tests():
    printer = FakePrint()
    with mock.patch("powermake.exceptions.print", new=printer.print):
        try:
            raise powermake.exceptions.PowerMakeRuntimeError("foo bar")
        except powermake.exceptions.PowerMakeException as e:
            powermake.exceptions.print_powermake_traceback(e)
    assert(printer.full_print_content.count('\n') == 3)
    assert("Runtime Error" in printer.full_print_content)
    assert("foo bar" in printer.full_print_content)

    printer.full_print_content = ""
    with mock.patch("powermake.exceptions.print", new=printer.print):
        will_fail()
    assert(printer.full_print_content.count('\n') == 3)
    assert("Command Error" in printer.full_print_content)
    assert("Unable to generate non_existing_file.c.o" in printer.full_print_content)