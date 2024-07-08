import shutil
import argparse


def default_on_clean() -> None:
    shutil.rmtree("build", ignore_errors=True)


def default_on_install(location: str) -> None:
    raise NotImplementedError("This needs to be implemented")


def run(build_callback: callable, clean_callback: callable = default_on_clean, install_callback: callable = default_on_install):
    parser = argparse.ArgumentParser(prog="powermake", description="Makefile Utility")

    parser.add_argument("-r", "--rebuild", help="Trigger the build function with the rebuilt argument set to True", action="store_true")
    parser.add_argument("-c", "--clean", help="Trigger the clean function", action="store_true")
    parser.add_argument("-i", "--install", nargs='?', metavar="location", help="Install the compiled program/lib to a given location", default=False)

    args = parser.parse_args()

    if args.clean:
        clean_callback()
    elif args.install is not False:
        install_callback(args.install)
    elif args.rebuild:
        build_callback(rebuild=True)
    else:
        build_callback(rebuild=False)
