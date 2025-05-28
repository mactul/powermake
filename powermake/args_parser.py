# Copyright 2025 Macéo Tuloup

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
import stat
import json
import shutil
import argparse
import subprocess
import typing as T
import __main__ as __makefile__

from .config import Config
from .utils import makedirs
from .cache import get_cache_dir
from .__version__ import __version__
from .interactive_config import InteractiveConfig
from .generation import gnu_makefile, compile_commands, vscode
from .display import print_info, print_debug_info, init_colors, error_text
from .exceptions import PowerMakeException, PowerMakeRuntimeError, print_powermake_traceback


def default_on_clean(config: Config) -> None:
    """
    Remove exe, lib and obj directories

    Parameters
    ----------
    config : powermake.Config
        the object given by `powermake.run`
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

    if config.info_build_directory is not None and os.path.isdir(config.info_build_directory):
        print_debug_info(f"Removing {config.info_build_directory}", config.verbosity)
        shutil.rmtree(config.info_build_directory)


def default_on_install(config: Config, location: T.Union[str, None]) -> None:
    """
    Install binary files, library files and exported headers into the subfolders `bin/`, `lib/` and `include/` of the location provided.

    You can directly give this function as a callback to `powermake.run` (it's the default behavior), but it's even better to call it from your own implementation of the install_callback.
    Like that, you can do work before this function, especially adding exported headers to the config with `config.add_exported_headers`

    If `location` is None, his default value is `./install/`

    For each exported header, if it has been exported with a None subfolder, it is simply copied into `include/`. If it has been exported with a subfolder, it is copied into `include/{subfolder}/`

    Parameters
    ----------
    config : powermake.Config
        The powermake.Config object created by the `powermake.run`. You should have called the method `config.add_exported_headers` on this object before giving it to this function.
    location : str | None
        Where to install `bin/`, `lib/` and `include/` subfolders. Ideally, if the location given to the install_callback by `powermake.run` was not None, you should give that to this function.
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
        if len(lib_files) > 0:
            makedirs(lib_folder, exist_ok=True)
            for file in lib_files:
                src = os.path.join(config.lib_build_directory, file)
                dest = os.path.join(lib_folder, file)
                print_debug_info(f"copying {src} to {dest}", config.verbosity)
                nb_files_installed += 1
                shutil.copy(src, dest)

    if os.path.isdir(config.exe_build_directory):
        bin_files = os.listdir(config.exe_build_directory)
        if len(bin_files) > 0:
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


def default_on_test(config: Config, args: T.List[str]) -> None:
    print_info("Running default test", config.verbosity)
    try:
        files = os.listdir(config.exe_build_directory)
    except FileNotFoundError:
        print("Nothing to run")
        return
    for file in files:
        filepath = os.path.join(config.exe_build_directory, file)
        if os.path.isfile(filepath) and stat.S_IXUSR & os.stat(filepath)[stat.ST_MODE]:
            print_debug_info([filepath, *args], config.verbosity)
            if subprocess.run([filepath, *args]).returncode != 0:
                raise PowerMakeRuntimeError(error_text(f"Unable to run the file {filepath}"))
            return
    print("Nothing to run")


def get_version_str() -> str:
    return f"PowerMake {__version__}\nCopyright (C) 2025 Macéo Tuloup\nLicense Apache-2.0: <http://www.apache.org/licenses/LICENSE-2.0>\nThis is a free software; see the sources for copying conditions: <https://github.com/mactul/powermake>\nThere is NO WARRANTY, to the extent permitted by law."

class ArgumentParser(argparse.ArgumentParser):
    """
    This object is a superset of [argparse.ArgumentParser](https://docs.python.org/3/library/argparse.html), you can read the documentation of argparse, it works exactly the same.

    Warning
    -------
    **Use this object and never argparse.ArgumentParser directly** or you will break some powermake features. Obviously the usual command line options will be broken but you will also break other features like the [powermake.run_another_powermake](#powermakerun_another_powermake) function. This object ensure that none of this is broken.

    """
    def __init__(self, prog: T.Union[str, None] = None, description: T.Union[str, None] = None, **kwargs: T.Any):
        if prog is None:
            prog = "python YOUR_MAKEFILE.py"
        if description is None:
            description = f"PowerMake {__version__}"
        super().__init__(prog=prog, description=description, **kwargs)

        self.add_argument("action", help='Can be "build", "clean", "install", "test" or "config"', nargs='?')
        self.add_argument("install_location", nargs='?', help="Only if the action is set to install, indicate in which folder the installation should be")
        self.add_argument('test_params', nargs='*', help="Only if the action is set to test or if -t (--test) is provided, will be passed to the tested program. You may want to use -- in front of those arguments, like this: python makefile.py -t -- arg1 -option1 arg2 -option2", default=[])
        self.add_argument("--version", help="display PowerMake version", action="store_true")
        self.add_argument("-d", "--debug", help="Trigger the build callback with config.debug set to True.", action="store_true")
        self.add_argument("-b", "--build", help="Trigger the build callback. This is the default but it can be used in combination with --clean or --install", action="store_true")
        self.add_argument("-r", "--rebuild", help="Trigger the build callback with config.rebuild set to True.", action="store_true")
        self.add_argument("-c", "--clean", help="Trigger the clean callback.", action="store_true")
        self.add_argument("-i", help="Trigger the install callback with the location argument set to None.", action="store_true")
        self.add_argument("--install", nargs='?', metavar="LOCATION", help="Trigger the install callback with the location argument set to the location given or None.", default=False)
        self.add_argument("-t", "--test", help="Trigger the test callback", action="store_true")
        self.add_argument("-f", "--config", help="Switch to an interactive mode that helps you editing your configuration files.", action="store_true")
        self.add_argument("-q", "--quiet", help="Disable all messages from the lib.", action="store_true")
        self.add_argument("-v", "--verbose", help="Display every command the lib runs.", action="store_true")
        self.add_argument("-j", "--jobs", help="Set on how many threads the compilation should be parallelized.", default=0, type=int)
        self.add_argument("-l", "--local-config", metavar="LOCAL_CONFIG_PATH", help="Set the path for the local config", default="./powermake_config.json")
        self.add_argument("-g", "--global-config", metavar="GLOBAL_CONFIG_PATH", help="Set the path for the global config", default=None)
        self.add_argument("-s", "--single-file", metavar="FILE", help="Run the compilation but only compile the specified file.", default=None)
        self.add_argument("-o", "--compile-commands-dir", metavar="DIRECTORY", help="Run the compilation and generate a compile_commands.json file in the directory specified.", default=None)
        self.add_argument("-m", "--makefile", help="Run the compilation and generate a GNU Makefile.", action="store_true")
        self.add_argument("--retransmit-colors", help="Let all ANSI color codes intact, even if not in a terminal. This option is especially useful in the configuration of an IDE.", action="store_true")
        self.add_argument("--delete-cache", help="Delete the cache, use this if PowerMake act weirdly", action="store_true")
        self.add_argument("--generate-vscode", nargs='?', metavar="VSCODE_FOLDER_PATH", help="Generate a launch.json and a tasks.json for visual studio code.", default=False)
        self.add_argument("--get-compilation-metadata", nargs='?', metavar="CURRENT_METADATA", help="(Internal option) - Returns a json containing metadata used by run_another_powermake.", default=False)


def generate_config(target_name: str, args_parsed: T.Union[argparse.Namespace, None] = None) -> Config:
    """
    Parse the command line and create a powermake.Config object.

    If you use this function, you should call `powermake.run_callbacks` after.

    Don't use the powermake.Config constructor, use this or powermake.run instead.

    Parameters
    ----------
    target_name : str
        The name of your application. It will be stored in the config and used for default naming.
    args_parsed : argparse.Namespace | optional
        Should be left to None. If set, it should be created by powermake.ArgumentParser().parse_args() to have all the required members for the Namespace
    """
    parser = None
    if args_parsed is None:
        parser = ArgumentParser()
        args_parsed = parser.parse_args()

    if args_parsed.action is None:
        pos_args = []
    else:
        if args_parsed.test:
            pos_args = [args_parsed.action]
        else:
            pos_args = []
        if args_parsed.install_location is not None:
            pos_args += [args_parsed.install_location] + args_parsed.test_params

    if len(pos_args) > 0 and args_parsed.action != "install" and args_parsed.action != "test" and not args_parsed.test:
        print(f"Unexpected positional argument {pos_args[0]} with an action different than 'install' and 'test", file=sys.stderr)
        if parser is not None:
            parser.print_usage(file=sys.stderr)
        exit(1)

    if args_parsed.action == "install" and len(pos_args) > 1:
        print(f"install takes a single argument", file=sys.stderr)
        if parser is not None:
            parser.print_usage(file=sys.stderr)
        exit(1)

    if args_parsed.quiet and args_parsed.verbose:
        print("Passing --quiet and --verbose arguments in the same time doesn't make any sense.", file=sys.stderr)
        if parser is not None:
            parser.print_usage(file=sys.stderr)
        exit(1)

    if args_parsed.version:
        print(get_version_str())
        exit(0)

    if args_parsed.delete_cache:
        print("deleting cache")
        shutil.rmtree(get_cache_dir(), ignore_errors=True)
        print("done")
        exit(0)


    if args_parsed.quiet:
        verbosity = 0
    elif args_parsed.verbose:
        verbosity = 2
    else:
        verbosity = 1

    if args_parsed.makefile:
        args_parsed.rebuild = True

    if not args_parsed.retransmit_colors:
        init_colors()

    if args_parsed.action == "config" or args_parsed.config:
        InteractiveConfig(global_config=args_parsed.global_config, local_config=args_parsed.local_config)

    if args_parsed.get_compilation_metadata:
        cumulated_launched_powermakes = json.loads(args_parsed.get_compilation_metadata)
    else:
        cumulated_launched_powermakes = {}

    config = Config(target_name, cumulated_launched_powermakes=cumulated_launched_powermakes, args_parsed=args_parsed, verbosity=verbosity, debug=args_parsed.debug, rebuild=args_parsed.rebuild, local_config=args_parsed.local_config, global_config=args_parsed.global_config, nb_jobs=args_parsed.jobs, single_file=args_parsed.single_file, compile_commands_dir=args_parsed.compile_commands_dir, pos_args=pos_args)

    return config


def run_callbacks(config: Config, *, build_callback: T.Callable[[Config], None], clean_callback: T.Callable[[Config], None] = default_on_clean, install_callback: T.Callable[[Config, T.Union[str, None]], None] = default_on_install, test_callback: T.Callable[[Config, T.List[str]], None] = default_on_test) -> None:
    """
    From a powermake.Config object generated by `powermake.generate_config` it calls the appropriate callback according to what is specified on the command line.

    If multiples actions are passed trough the command line, like `-cri` (or `--clean --rebuild --install` in the long form), multiple callbacks can be called.  
    Callbacks are always called in this order: clean -> build -> install.

    Warning
    -------
    You shouldn't run anything important after the return of this function, because if `--get-lib-build-folder` is provided on the command line, this function calls `exit(0)`

    Parameters
    ----------
    config : powermake.Config
        The config generated by `powermake.generate_config`
    build_callback : Callable[[Config], None]
        The function that will be called when building or rebuilding. This callback takes a single parameter: config
    clean_callback : Callable[[Config], None], optional
        The function that will be called when cleaning. This callback takes a single parameter: config
    install_callback : T.Callable[[Config, T.Union[str, None]], None], optional
        The function that will be called when installing. This callback takes 2 parameters: config and location.  
        If the location is not provided on the command line, his value is None
    test_callback : Callable[[Config], None], optional
        The function that will be called when testing. This callback takes a single parameter: config
    """

    clean = False
    build = False
    install = False
    interactive_config = False
    test = False
    if config._args_parsed is None:
        raise PowerMakeRuntimeError(error_text("powermake.run_callbacks should only be run with a config generated by powermake.generate_config"))


    if config._args_parsed.generate_vscode is not False:
        print("Generating launch.json and tasks.json")
        vscode_path: str = ""
        if config._args_parsed.generate_vscode is not None:
            vscode_path = config._args_parsed.generate_vscode
        if not vscode_path.endswith(".vscode") and not vscode_path.endswith(".vscode/") and not vscode_path.endswith(".vscode\\"):
            vscode_path = os.path.join(vscode_path, ".vscode")
        vscode.generate_vscode(config, vscode_path)
        print("done")
        exit(0)

    if config._args_parsed.action == "clean" or config._args_parsed.clean:
        clean = True
    if config._args_parsed.action == "build" or config._args_parsed.build or config._args_parsed.rebuild:
        build = True
    if config._args_parsed.action == "install" or config._args_parsed.install is not False or config._args_parsed.i:
        install = True
    if config._args_parsed.action == "config" or config._args_parsed.config:
        interactive_config = True
    if config._args_parsed.action == "test" or config._args_parsed.test:
        test = True

    if clean:
        clean_callback(config)
    if build or (not clean and not install and not interactive_config and not test):
        try:
            build_callback(config)
        except PowerMakeException as e:
            print_powermake_traceback(e)
            exit(1)
    if install:
        if config._args_parsed.action == "install":
            install_callback(config, config._args_parsed.install_location or None)
        else:
            install_callback(config, config._args_parsed.install or None)
    if test:
        test_callback(config, config._pos_args)



    # After doing all compilation, if the argument get-lib-build-folder was given, we print the absolute path of the directory in which all lib have been built and exit.
    # Like that, the last line of the program output will be the requested folder.
    # This is used by the powermake.run_another_powermake function.
    if config._args_parsed.get_compilation_metadata is not False:
        metadata: T.Dict[str, T.Any] = {}
        if config.lib_build_directory is not None and os.path.exists(config.lib_build_directory):
            metadata["lib_build_directory"] = os.path.abspath(config.lib_build_directory)
        else:
            metadata["lib_build_directory"] = ""
        metadata["cumulated_launched_powermakes"] = config._cumulated_launched_powermakes
        print()
        print(json.dumps(metadata))
        exit(0)

    if config._args_parsed.makefile:
        gnu_makefile.generate_makefile(config)
    if config.compile_commands_dir is not None:
        compile_commands.generate_compile_commands(config)


def run(target_name: str, *, build_callback: T.Callable[[Config], None], clean_callback: T.Callable[[Config], None] = default_on_clean, install_callback: T.Callable[[Config, T.Union[str, None]], None] = default_on_install, test_callback: T.Callable[[Config, T.List[str]], None] = default_on_test, args_parsed: T.Union[argparse.Namespace, None] = None) -> None:
    """
    Parse the command line, create a powermake.Config object according to the command line arguments and call the appropriate callback.

    If multiples actions are passed trough the command line, like `-cri` (or `--clean --rebuild --install` in the long form), multiple callbacks can be called.  
    Callbacks are always called in this order: clean -> build -> install -> test.

    Warning
    -------
    You shouldn't run anything important after the return of this function, because if `--get-lib-build-folder` is provided on the command line, this function calls `exit(0)`

    Parameters
    ----------
    target_name : str
        The name of your application. It will be stored in the config and used for default naming.
    build_callback : Callable[[Config], None]
        The function that will be called when building or rebuilding. This callback takes a single parameter: config
    clean_callback : Callable[[Config], None], optional
        The function that will be called when cleaning. This callback takes a single parameter: config
    install_callback : T.Callable[[Config, T.Union[str, None]], None], optional
        The function that will be called when installing. This callback takes 2 parameters: config and location.  
        If the location is not provided on the command line, his value is None
    test_callback : Callable[[Config], None], optional
        The function that will be called when testing. This callback takes a single parameter: config
    args_parsed : argparse.Namespace | optional
        Should be left to None. If set, it should be created by powermake.ArgumentParser().parse_args() to have all the required members for the Namespace
    """

    config = generate_config(target_name, args_parsed)

    run_callbacks(config, build_callback=build_callback, clean_callback=clean_callback, install_callback=install_callback, test_callback=test_callback)
