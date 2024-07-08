import sys
import shutil
import argparse


def default_build(rebuild: bool) -> None:
    message = """Tips: You should register a build function
Syntax:

import powermake

parser = powermake.ArgsParser()

@parser.on_build()
def my_build_function(rebuild: bool) -> None:
    # Your code for the build
    # You may want to create a powermake.Config instance and then call powermake.compile_files

parser.parse_args()
"""
    print(message, file=sys.stderr)


def default_clean() -> None:
    shutil.rmtree("build", ignore_errors=True)


def default_install(location: str) -> None:
    raise NotImplementedError("This needs to be implemented")


class ArgsParser:
    def __init__(self):
        self.on_build_callback = default_build
        self.on_install_callback = default_install
        self.on_clean_callback = default_clean

    def on_build(self):
        def wrapper(func):
            self.on_build_callback = func
            return func
        return wrapper

    def on_install(self):
        def wrapper(func):
            self.on_install_callback = func
            return func
        return wrapper

    def on_clean(self):
        def wrapper(func):
            self.on_clean_callback = func
            return func
        return wrapper

    def parse_args(self):
        parser = argparse.ArgumentParser(prog="powermake", description="Makefile Utility")

        parser.add_argument("-r", "--rebuild", help="Trigger the build function with the rebuilt argument set to True", action="store_true")
        parser.add_argument("-c", "--clean", help="Trigger the clean function", action="store_true")
        parser.add_argument("-i", "--install", nargs='?', metavar="location", help="Install the compiled program/lib to a given location", default=False)

        args = parser.parse_args()

        if args.clean:
            self.on_clean_callback()
        elif args.install is not False:
            self.on_install_callback(args.install)
        elif args.rebuild:
            self.on_build_callback(rebuild=True)
        else:
            self.on_build_callback(rebuild=False)
