import os
import sys
import shutil
import argparse
from .config import Config
from .interactive_config import InteractiveConfig
from .display import print_info, print_debug_info, init_colors


def default_on_clean(config: Config) -> None:
    """Remove exe, lib and obj directories

    Args:
        config (Config): the object given by `powermake.run`
    """
    print_info("Cleaning", config.verbosity)

    if config.exe_build_directory is not None and os.path.isdir(config.exe_build_directory):
        print_debug_info(f"Removing {config.exe_build_directory}", config.verbosity)
        shutil.rmtree(config.exe_build_directory)

    if config.lib_build_directory is not None and os.path.isdir(config.lib_build_directory):
        print_debug_info(f"Removing {config.lib_build_directory}", config.verbosity)
        shutil.rmtree(config.lib_build_directory)

    if config.obj_build_directory is not None and os.path.isdir(config.obj_build_directory):
        print_debug_info(f"Removing {config.obj_build_directory}", config.verbosity)
        shutil.rmtree(config.obj_build_directory)


def default_on_install(config: Config, location: str) -> None:
    """Install binary files, library files and exported headers into the subfolders `bin/`, `lib/` and `include/` of the location provided.

    You can directly give this function as a callback to `powermake.run` (it's the default behavior), but it's even better to call it from your own implementation of the install_callback.
    Like that, you can do work before this function, especially adding exported headers to the config with `config.add_exported_headers`

    If `location` is None, his default value is `./install/`

    For each exported header, if it has been exported with a None subfolder, it is simply copied into `include/`. If it has been exported with a subfolder, it is copied into `include/{subfolder}/`

    Args:
        config (Config): The powermake.Config object created by the `powermake.run`. You should have called the method `config.add_exported_headers` on this object before giving it to this function.
        location (str): Where to install `bin/`, `lib/` and `include/` subfolders. Ideally, if the location given to the install_callback by `powermake.run` was not None, you should give that to this function.
    """
    if location is None:
        location = "./install/"

    print_info(f"Installing to {location}", config.verbosity)

    nb_files_installed = 0

    lib_folder = os.path.join(location, "lib")
    include_folder = os.path.join(location, "include")
    bin_folder = os.path.join(location, "bin")

    if os.path.isdir(config.lib_build_directory):
        lib_files = os.listdir(config.lib_build_directory)
        if lib_files != []:
            os.makedirs(lib_folder, exist_ok=True)
            for file in lib_files:
                src = os.path.join(config.lib_build_directory, file)
                dest = os.path.join(lib_folder, file)
                print_debug_info(f"copying {src} to {dest}", config.verbosity)
                nb_files_installed += 1
                shutil.copy(src, dest)

    if os.path.isdir(config.exe_build_directory):
        bin_files = os.listdir(config.exe_build_directory)
        if bin_files != []:
            os.makedirs(bin_folder, exist_ok=True)
            for file in bin_files:
                src = os.path.join(config.exe_build_directory, file)
                dest = os.path.join(bin_folder, file)
                print_debug_info(f"copying {src} to {dest}", config.verbosity)
                nb_files_installed += 1
                shutil.copy(src, dest)

    if len(config.exported_headers) != 0:
        os.makedirs(include_folder, exist_ok=True)
    for (src, subfolder) in config.exported_headers:
        if subfolder is None:
            dest = os.path.join(include_folder, os.path.basename(src))
        else:
            os.makedirs(os.path.join(include_folder, subfolder), exist_ok=True)
            dest = os.path.join(include_folder, subfolder, os.path.basename(src))
        print_debug_info(f"copying {src} to {dest}", config.verbosity)
        nb_files_installed += 1
        shutil.copy(src, dest)

    print_info(f"{nb_files_installed} files successfully copied", config.verbosity)


def run(target_name: str, *, build_callback: callable, clean_callback: callable = default_on_clean, install_callback: callable = default_on_install):
    """Parse the command line, create a powermake.Config object according to the command line arguments and call the appropriate callback.

    If multiples actions are passed trough the command line, like `-cri` (or `--clean --rebuild --install` in the long form), multiple callbacks can be called.  
    Callbacks are always called in this order: clean -> build -> install.

    Warning: You shouldn't run anything important after the return of this function, because if `--get-lib-build-folder` is provided on the command line, this function call `exit(0)`

    Args:
        target_name (str): The name of your application. It will be stored in the config and used for default naming.
        build_callback (callable): The function that will be called when building or rebuilding. This callback takes a single parameter: config
        clean_callback (callable, optional): The function that will be called when cleaning. This callback takes a single parameter: config
        install_callback (callable, optional): The function that will be called when installing. This callback takes 2 parameters: config and location.  
            If the location is not provided on the command line, his value is None
    """
    default_nb_jobs = os.cpu_count() or 8

    parser = argparse.ArgumentParser(prog="powermake", description="Makefile Utility")

    parser.add_argument("action", choices=["build", "clean", "install", "config"], nargs='?')
    parser.add_argument("install_location", nargs='?', help="Only if the action is set to install, indicate in which folder the installation should be")
    parser.add_argument("-d", "--debug", help="Trigger the build function with config.debug set to True.", action="store_true")
    parser.add_argument("-b", "--build", help="Trigger the build function. This is the default but it can be used in combination with --clean or --install", action="store_true")
    parser.add_argument("-r", "--rebuild", help="Trigger the build function with config.rebuild set to True.", action="store_true")
    parser.add_argument("-c", "--clean", help="Trigger the clean function.", action="store_true")
    parser.add_argument("-i", help="Trigger the install function with the location argument set to None.", action="store_true")
    parser.add_argument("--install", nargs='?', metavar="LOCATION", help="Trigger the install function with the location argument set to the location given or None.", default=False)
    parser.add_argument("-f", "--config", help="Switch to an interactive mode that helps you editing your configuration files.", action="store_true")
    parser.add_argument("-q", "--quiet", help="Disable all messages from the lib.", action="store_true")
    parser.add_argument("-v", "--verbose", help="Display every command the lib runs.", action="store_true")
    parser.add_argument("-j", "--jobs", help=f"Set on how many threads the compilation should be parallelized. (default: {default_nb_jobs})", default=default_nb_jobs, type=int)
    parser.add_argument("-l", "--local-config", metavar="LOCAL_CONFIG_PATH", help="Set the path for the local config", default="./powermake_config.json")
    parser.add_argument("-g", "--global-config", metavar="GLOBAL_CONFIG_PATH", help="Set the path for the global config", default=None)
    parser.add_argument("-s", "--single-file", metavar="FILE", help="Run the compilation but only compile the specified file.", default=None)
    parser.add_argument("--get-lib-build-folder", help="(Internal option) - Return the lib build folder path according to the config.", action="store_true")
    parser.add_argument("--retransmit-colors", help="(Internal option) - Let all ANSI color codes intact, even if not in a terminal.", action="store_true")

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

    if not args.retransmit_colors:
        init_colors()

    clean = False
    build = False
    install = False
    interactive_config = False
    if args.action == "clean" or args.clean:
        clean = True
    if args.action == "build" or args.build or args.rebuild:
        build = True
    if args.action == "install" or args.install is not False or args.i:
        install = True
    if args.action == "config" or args.config:
        interactive_config = True
        InteractiveConfig(global_config=args.global_config, local_config=args.local_config)

    config = Config(target_name, verbosity=verbosity, debug=args.debug, rebuild=args.rebuild, local_config=args.local_config, global_config=args.global_config, nb_jobs=args.jobs, single_file=args.single_file)

    if clean:
        clean_callback(config)
    if build or (not clean and not install and not interactive_config):
        build_callback(config)
    if install:
        if args.action == "install":
            install_callback(config, args.install_location)
        else:
            install_callback(config, args.install or None)

    # After doing all compilation, if the argument get-lib-build-folder was given, we print the absolute path of the directory in which all lib have been built and exit.
    # Like that, the last line of the program output will be the requested folder.
    # This is used by the powermake.run_another_powermake function.
    if args.get_lib_build_folder:
        if config.lib_build_directory is not None and os.path.exists(config.lib_build_directory):
            print(os.path.abspath(config.lib_build_directory))
        else:
            print()
        exit(0)
