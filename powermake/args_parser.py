import shutil
import argparse
from .config import Config


def default_on_clean(config: Config) -> None:
    shutil.rmtree(config.exe_build_directory, ignore_errors=True)
    shutil.rmtree(config.lib_build_directory, ignore_errors=True)
    shutil.rmtree(config.obj_build_directory, ignore_errors=True)


def default_on_install(config: Config, location: str) -> None:
    raise NotImplementedError("This needs to be implemented")


def run(build_callback: callable, clean_callback: callable = default_on_clean, install_callback: callable = default_on_install):
    parser = argparse.ArgumentParser(prog="powermake", description="Makefile Utility")

    parser.add_argument("action", choices=["build", "clean", "install"], nargs='?')
    parser.add_argument("-d", "--debug", help="Trigger the build function with the debug argument set to True.", action="store_true")
    parser.add_argument("-r", "--rebuild", help="Trigger the build function with the rebuilt argument set to True.", action="store_true")
    parser.add_argument("-c", "--clean", help="Trigger the clean function.", action="store_true")
    parser.add_argument("-i", "--install", nargs='?', metavar="location", help="Trigger the install function with the location argument set to the location given or None.", default=False)
    parser.add_argument("-q", "--quiet", help="Disable all messages from the lib.", action="store_true")
    parser.add_argument("-v", "--verbose", help="Display every command the lib runs.", action="store_true")
    parser.add_argument("-l", "--local-config", nargs=1, metavar="local_config_path", help="Set the path for the local config", default="./powermake_config.json")
    parser.add_argument("-g", "--global-config", nargs=1, metavar="global_config_path", help="Set the path for the global config", default=None)

    args = parser.parse_args()

    if args.quiet and args.verbose:
        raise ValueError("Passing --quiet and --verbose arguments in the same time doesn't make any sense.")

    if args.quiet:
        verbosity = 0
    elif args.verbose:
        verbosity = 2
    else:
        verbosity = 1

    config = Config(verbosity=verbosity, debug=args.debug, rebuild=args.rebuild, local_config=args.local_config, global_config=args.global_config)

    if args.action == "clean" or args.clean:
        clean_callback(config)
    elif args.action == "install" or args.install is not False:
        install_callback(config, args.install)
    else:
        build_callback(config)
