import os
import sys
import shutil
import argparse
from .config import Config


def default_on_clean(config: Config) -> None:
    if config.verbosity >= 1:
        print("Cleaning")
    shutil.rmtree(config.exe_build_directory, ignore_errors=True)
    shutil.rmtree(config.lib_build_directory, ignore_errors=True)
    shutil.rmtree(config.obj_build_directory, ignore_errors=True)


def default_on_install(config: Config, location: str) -> None:
    if location is None:
        location = "./install/"

    if config.verbosity >= 1:
        print("Installing to", location)

    lib_folder = os.path.join(location, "lib")
    include_folder = os.path.join(location, "include")
    bin_folder = os.path.join(location, "bin")

    if os.path.isdir(config.lib_build_directory):
        lib_files = os.listdir(config.lib_build_directory)
        if lib_files != []:
            os.makedirs(lib_folder, exist_ok=True)
            for file in lib_files:
                shutil.copyfile(os.path.join(config.lib_build_directory, file), os.path.join(lib_folder, file))

    if os.path.isdir(config.exe_build_directory):
        bin_files = os.listdir(config.exe_build_directory)
        if bin_files != []:
            os.makedirs(bin_folder, exist_ok=True)
            for file in bin_files:
                shutil.copyfile(os.path.join(config.exe_build_directory, file), os.path.join(bin_folder, file))

    if config.exported_headers != []:
        os.makedirs(include_folder, exist_ok=True)
        for file in config.exported_headers:
            shutil.copyfile(file, os.path.join(include_folder, os.path.basename(file)))


def run(build_callback: callable, clean_callback: callable = default_on_clean, install_callback: callable = default_on_install):
    parser = argparse.ArgumentParser(prog="powermake", description="Makefile Utility")

    parser.add_argument("action", choices=["build", "clean", "install"], nargs='?')
    parser.add_argument("install_location", nargs='?', help="Only if the action is set to install, indicate in which folder the installation should be")
    parser.add_argument("-d", "--debug", help="Trigger the build function with config.debug set to True.", action="store_true")
    parser.add_argument("-b", "--build", help="Trigger the build function. This is the default but it can be used in combination with --clean or --install", action="store_true")
    parser.add_argument("-r", "--rebuild", help="Trigger the build function with config.rebuild set to True.", action="store_true")
    parser.add_argument("-c", "--clean", help="Trigger the clean function.", action="store_true")
    parser.add_argument("--install", nargs='?', metavar="location", help="Trigger the install function with the location argument set to the location given or None.", default=False)
    parser.add_argument("-q", "--quiet", help="Disable all messages from the lib.", action="store_true")
    parser.add_argument("-v", "--verbose", help="Display every command the lib runs.", action="store_true")
    parser.add_argument("-l", "--local-config", nargs=1, metavar="local_config_path", help="Set the path for the local config", default="./powermake_config.json")
    parser.add_argument("-g", "--global-config", nargs=1, metavar="global_config_path", help="Set the path for the global config", default=None)
    parser.add_argument("--get-lib-build-folder", help="Return the lib build folder path according to the config.", action="store_true")

    args = parser.parse_args()

    if args.install_location is not None and args.action != "install":
        print(f"Unexpected argument {args.install_location} with an action different from 'install'", file=sys.stderr)
        parser.print_usage(file=sys.stderr)
        exit(1)

    if args.quiet and args.verbose:
        print("Passing --quiet and --verbose arguments in the same time doesn't make any sense.", file=sys.stderr)
        parser.print_usage(file=sys.stderr)
        exit(1)

    if args.quiet:
        verbosity = 0
    elif args.verbose:
        verbosity = 2
    else:
        verbosity = 1

    config = Config(verbosity=verbosity, debug=args.debug, rebuild=args.rebuild, local_config=args.local_config, global_config=args.global_config)

    if args.get_lib_build_folder:
        print(os.path.abspath(config.lib_build_directory))
        exit(0)

    clean = False
    build = False
    install = False
    if args.action == "clean" or args.clean:
        clean = True
    if args.action == "build" or args.build or args.rebuild:
        build = True
    if args.action == "install" or args.install is not False:
        install = True

    if clean:
        clean_callback(config)
    if build or (not clean and not install):
        build_callback(config)
    if install:
        if args.action == "install":
            install_callback(config, args.install_location)
        else:
            install_callback(config, args.install)
