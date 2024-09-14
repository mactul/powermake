# Copyright 2024 Macéo Tuloup

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
import shutil
import argparse
from .config import Config
from .utils import makedirs
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
            makedirs(lib_folder, exist_ok=True)
            for file in lib_files:
                src = os.path.join(config.lib_build_directory, file)
                dest = os.path.join(lib_folder, file)
                print_debug_info(f"copying {src} to {dest}", config.verbosity)
                nb_files_installed += 1
                shutil.copy(src, dest)

    if os.path.isdir(config.exe_build_directory):
        bin_files = os.listdir(config.exe_build_directory)
        if bin_files != []:
            makedirs(bin_folder, exist_ok=True)
            for file in bin_files:
                src = os.path.join(config.exe_build_directory, file)
                dest = os.path.join(bin_folder, file)
                print_debug_info(f"copying {src} to {dest}", config.verbosity)
                nb_files_installed += 1
                shutil.copy(src, dest)

    if len(config.exported_headers) != 0:
        makedirs(include_folder, exist_ok=True)
    for (src, subfolder) in config.exported_headers:
        if subfolder is None:
            dest = os.path.join(include_folder, os.path.basename(src))
        else:
            makedirs(os.path.join(include_folder, subfolder), exist_ok=True)
            dest = os.path.join(include_folder, subfolder, os.path.basename(src))
        print_debug_info(f"copying {src} to {dest}", config.verbosity)
        nb_files_installed += 1
        shutil.copy(src, dest)

    print_info(f"{nb_files_installed} files successfully copied", config.verbosity)


class ArgumentParser(argparse.ArgumentParser):
    def __init__(self, prog: str = None, description: str = None):
        if prog is None:
            prog = "powermake"
        if description is None:
            description = "Makefile Utility"
        super().__init__(prog=prog, description=description)

        self.add_argument("action", choices=["build", "clean", "install", "config"], nargs='?')
        self.add_argument("install_location", nargs='?', help="Only if the action is set to install, indicate in which folder the installation should be")
        self.add_argument("-d", "--debug", help="Trigger the build function with config.debug set to True.", action="store_true")
        self.add_argument("-b", "--build", help="Trigger the build function. This is the default but it can be used in combination with --clean or --install", action="store_true")
        self.add_argument("-r", "--rebuild", help="Trigger the build function with config.rebuild set to True.", action="store_true")
        self.add_argument("-c", "--clean", help="Trigger the clean function.", action="store_true")
        self.add_argument("-i", help="Trigger the install function with the location argument set to None.", action="store_true")
        self.add_argument("--install", nargs='?', metavar="LOCATION", help="Trigger the install function with the location argument set to the location given or None.", default=False)
        self.add_argument("-f", "--config", help="Switch to an interactive mode that helps you editing your configuration files.", action="store_true")
        self.add_argument("-q", "--quiet", help="Disable all messages from the lib.", action="store_true")
        self.add_argument("-v", "--verbose", help="Display every command the lib runs.", action="store_true")
        self.add_argument("-j", "--jobs", help="Set on how many threads the compilation should be parallelized.", default=0, type=int)
        self.add_argument("-l", "--local-config", metavar="LOCAL_CONFIG_PATH", help="Set the path for the local config", default="./powermake_config.json")
        self.add_argument("-g", "--global-config", metavar="GLOBAL_CONFIG_PATH", help="Set the path for the global config", default=None)
        self.add_argument("-s", "--single-file", metavar="FILE", help="Run the compilation but only compile the specified file.", default=None)
        self.add_argument("-o", "--compile-commands-dir", metavar="DIRECTORY", help="Run the compilation and generate a compile_commands.json file in the directory specified.", default=None)
        self.add_argument("--get-lib-build-folder", help="(Internal option) - Return the lib build folder path according to the config.", action="store_true")
        self.add_argument("--retransmit-colors", help="(Internal option) - Let all ANSI color codes intact, even if not in a terminal.", action="store_true")


def generate_config(target_name: str, args_parsed: argparse.Namespace = None):
    """Parse the command line and create a powermake.Config object according to the command line arguments."""
    parser = None
    if args_parsed is None:
        parser = ArgumentParser()
        args_parsed = parser.parse_args()

    if args_parsed.install_location is not None and args_parsed.action != "install":
        print(f"Unexpected argument {args_parsed.install_location} with an action different from 'install'", file=sys.stderr)
        if parser is not None:
            parser.print_usage(file=sys.stderr)
        exit(1)

    if args_parsed.quiet and args_parsed.verbose:
        print("Passing --quiet and --verbose arguments in the same time doesn't make any sense.", file=sys.stderr)
        if parser is not None:
            parser.print_usage(file=sys.stderr)
        exit(1)

    if args_parsed.quiet:
        verbosity = 0
    elif args_parsed.verbose:
        verbosity = 2
    else:
        verbosity = 1

    if not args_parsed.retransmit_colors:
        init_colors()

    if args_parsed.action == "config" or args_parsed.config:
        InteractiveConfig(global_config=args_parsed.global_config, local_config=args_parsed.local_config)

    return Config(target_name, args_parsed=args_parsed, verbosity=verbosity, debug=args_parsed.debug, rebuild=args_parsed.rebuild, local_config=args_parsed.local_config, global_config=args_parsed.global_config, nb_jobs=args_parsed.jobs, single_file=args_parsed.single_file, compile_commands_dir=args_parsed.compile_commands_dir)


def run_callbacks(config: Config, *, build_callback: callable, clean_callback: callable = default_on_clean, install_callback: callable = default_on_install):
    """From a config generated by `powermake.generate_config` start each callback according to the command line."""

    clean = False
    build = False
    install = False
    interactive_config = False
    if config._args_parsed.action == "clean" or config._args_parsed.clean:
        clean = True
    if config._args_parsed.action == "build" or config._args_parsed.build or config._args_parsed.rebuild:
        build = True
    if config._args_parsed.action == "install" or config._args_parsed.install is not False or config._args_parsed.i:
        install = True
    if config._args_parsed.action == "config" or config._args_parsed.config:
        interactive_config = True

    if clean:
        clean_callback(config)
    if build or (not clean and not install and not interactive_config):
        build_callback(config)
    if install:
        if config._args_parsed.action == "install":
            install_callback(config, config._args_parsed.install_location)
        else:
            install_callback(config, config._args_parsed.install or None)

    # After doing all compilation, if the argument get-lib-build-folder was given, we print the absolute path of the directory in which all lib have been built and exit.
    # Like that, the last line of the program output will be the requested folder.
    # This is used by the powermake.run_another_powermake function.
    if config._args_parsed.get_lib_build_folder:
        if config.lib_build_directory is not None and os.path.exists(config.lib_build_directory):
            print(os.path.abspath(config.lib_build_directory))
        else:
            print()
        exit(0)


def run(target_name: str, *, build_callback: callable, clean_callback: callable = default_on_clean, install_callback: callable = default_on_install, args_parsed: argparse.Namespace = None):
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
        args_parsed (argparse.Namespace, optional): Should be left to None. If set, it should be created by powermake.ArgumentParser().parse_args() to have all the required members for the Namespace
    """

    config = generate_config(target_name, args_parsed)

    run_callbacks(config, build_callback=build_callback, clean_callback=clean_callback, install_callback=install_callback)
