# PowerMake

- [PowerMake](#powermake)
  - [Installation](#installation)
  - [Install from Pypi: (RECOMMENDED)](#install-from-pypi-recommended)
  - [install from sources: (NOT RECOMMENDED AT ALL)](#install-from-sources-not-recommended-at-all)
  - [Quick Example](#quick-example)
  - [More examples](#more-examples)
  - [Documentation](#documentation)
    - [Command line arguments](#command-line-arguments)
    - [Toolchain detection](#toolchain-detection)
    - [PowerMake flags translation](#powermake-flags-translation)
    - [powermake.run](#powermakerun)
    - [powermake.Config](#powermakeconfig)
      - [Members](#members)
        - [debug](#debug)
        - [rebuild](#rebuild)
        - [nb\_total\_operations](#nb_total_operations)
        - [target\_name](#target_name)
        - [nb\_jobs](#nb_jobs)
        - [compile\_commands\_dir](#compile_commands_dir)
        - [host\_operating\_system](#host_operating_system)
        - [target\_operating\_system](#target_operating_system)
        - [host\_architecture](#host_architecture)
        - [target\_architecture](#target_architecture)
        - [c\_compiler](#c_compiler)
        - [cpp\_compiler](#cpp_compiler)
        - [as\_compiler](#as_compiler)
        - [asm\_compiler](#asm_compiler)
        - [rc\_compiler](#rc_compiler)
        - [archiver](#archiver)
        - [linker](#linker)
        - [shared\_linker](#shared_linker)
        - [obj\_build\_directory](#obj_build_directory)
        - [lib\_build\_directory](#lib_build_directory)
        - [exe\_build\_directory](#exe_build_directory)
        - [defines](#defines)
        - [additional\_includedirs](#additional_includedirs)
        - [shared\_libs](#shared_libs)
        - [c\_flags](#c_flags)
        - [cpp\_flags](#cpp_flags)
        - [c\_cpp\_flags](#c_cpp_flags)
        - [as\_flags](#as_flags)
        - [asm\_flags](#asm_flags)
        - [rc\_flags](#rc_flags)
        - [c\_cpp\_as\_asm\_flags](#c_cpp_as_asm_flags)
        - [ar\_flags](#ar_flags)
        - [ld\_flags](#ld_flags)
        - [shared\_linker\_flags](#shared_linker_flags)
        - [flags](#flags)
        - [exported\_headers](#exported_headers)
      - [Methods](#methods)
        - [set\_debug()](#set_debug)
        - [set\_optimization()](#set_optimization)
        - [set\_target\_architecture()](#set_target_architecture)
        - [target\_is\_windows()](#target_is_windows)
        - [target\_is\_linux()](#target_is_linux)
        - [target\_is\_mingw()](#target_is_mingw)
        - [target\_is\_macos()](#target_is_macos)
        - [add\_defines()](#add_defines)
        - [remove\_defines()](#remove_defines)
        - [add\_shared\_libs()](#add_shared_libs)
        - [remove\_shared\_libs()](#remove_shared_libs)
        - [add\_includedirs()](#add_includedirs)
        - [remove\_includedirs()](#remove_includedirs)
        - [add\_flags()](#add_flags)
        - [remove\_flags()](#remove_flags)
        - [add\_c\_flags()](#add_c_flags)
        - [remove\_c\_flags()](#remove_c_flags)
        - [add\_cpp\_flags()](#add_cpp_flags)
        - [remove\_cpp\_flags()](#remove_cpp_flags)
        - [add\_c\_cpp\_flags()](#add_c_cpp_flags)
        - [remove\_c\_cpp\_flags()](#remove_c_cpp_flags)
        - [add\_as\_flags()](#add_as_flags)
        - [remove\_as\_flags()](#remove_as_flags)
        - [add\_asm\_flags()](#add_asm_flags)
        - [remove\_asm\_flags()](#remove_asm_flags)
        - [add\_c\_cpp\_as\_asm\_flags()](#add_c_cpp_as_asm_flags)
        - [remove\_c\_cpp\_as\_asm\_flags()](#remove_c_cpp_as_asm_flags)
        - [add\_rc\_flags()](#add_rc_flags)
        - [remove\_rc\_flags()](#remove_rc_flags)
        - [add\_ar\_flags()](#add_ar_flags)
        - [remove\_ar\_flags()](#remove_ar_flags)
        - [add\_ld\_flags()](#add_ld_flags)
        - [remove\_ld\_flags()](#remove_ld_flags)
        - [add\_shared\_linker\_flags()](#add_shared_linker_flags)
        - [remove\_shared\_linker\_flags()](#remove_shared_linker_flags)
        - [add\_exported\_headers()](#add_exported_headers)
        - [remove\_exported\_headers()](#remove_exported_headers)
        - [copy()](#copy)
        - [empty\_copy()](#empty_copy)
    - [powermake.default\_on\_clean](#powermakedefault_on_clean)
    - [powermake.default\_on\_install](#powermakedefault_on_install)
    - [powermake.get\_files](#powermakeget_files)
    - [powermake.filter\_files](#powermakefilter_files)
    - [powermake.compile\_files](#powermakecompile_files)
    - [powermake.archive\_files](#powermakearchive_files)
    - [powermake.link\_files](#powermakelink_files)
    - [powermake.link\_shared\_lib](#powermakelink_shared_lib)
    - [powermake.delete\_files\_from\_disk](#powermakedelete_files_from_disk)
    - [powermake.run\_another\_powermake](#powermakerun_another_powermake)
    - [powermake.run\_command\_if\_needed](#powermakerun_command_if_needed)
    - [powermake.needs\_update](#powermakeneeds_update)
    - [powermake.run\_command](#powermakerun_command)
    - [powermake.Operation (deprecated)](#powermakeoperation-deprecated)
      - [execute()](#execute)
    - [Having more control than what powermake.run offers](#having-more-control-than-what-powermakerun-offers)
      - [powermake.ArgumentParser](#powermakeargumentparser)
        - [add\_argument()](#add_argument)
        - [parse\_args()](#parse_args)
      - [powermake.generate\_config](#powermakegenerate_config)
      - [powermake.run\_callbacks](#powermakerun_callbacks)
  - [Compatibility with other tools](#compatibility-with-other-tools)
    - [Scan-Build](#scan-build)
    - [LLVM libfuzzer](#llvm-libfuzzer)
    - [GNU Make](#gnu-make)
    - [Visual Studio Code](#visual-studio-code)



## Installation

> [!WARNING]  
> In this documentation, the command `python` refers to python >= python 3.7.  
> On old systems, `python` and `pip` can refer to python 2.7, in this case, use `python3` and `pip3`.


## Install from Pypi: (RECOMMENDED)

```sh
pip install -U powermake
```
Don't hesitate to run this command regularly to benefit from new features and bug fixes.


## install from sources: (NOT RECOMMENDED AT ALL)

Version installed from sources might be untested and might not work at all.

```sh
# USE AT YOUR OWN RISKS
pip install -U build twine
git clone https://github.com/mactul/powermake
cd powermake
sed -i "s/{{VERSION_PLACEHOLDER}}/0.0.0/g" pyproject.toml
rm -rf ./dist/
python -m build
pip install -U dist/powermake-*-py3-none-any.whl --force-reinstall
```


## Quick Example

This example compiles all `.c` and `.cpp` files that are recursively in the same folder as the python script and generate an executable named `program_test`

> [!WARNING]  
> PowerMake calculates all paths from its location, not the location where it is run.  
> For example, `python ./folder/makefile.py` will do the same as `cd ./folder && python ./makefile.py`

> [!NOTE]  
> In this documentation, we often assume that your makefile is named `makefile.py`, it makes things easier to explain. Of course, you can name your makefile the name you like the most.

```py
import powermake


def on_build(config: powermake.Config):

    files = powermake.get_files("**/*.c", "**/*.cpp")

    objects = powermake.compile_files(config, files)

    print(powermake.link_files(config, objects))


powermake.run("program_test", build_callback=on_build)
```


## [More examples](./examples.md)


## Documentation

> [!NOTE]  
> This documentation is not complete, if you struggle to do something, do not hesitate to ask a question in the [discussions section](https://github.com/mactul/powermake/discussions/categories/q-a), it may be that the feature you search for is undocumented.


### Command line arguments

To benefit from the command line parser, you have to use the [powermake.run](#powermakerun) function.

If no arguments are passed through the command line, the default behavior is to trigger the build callback.  
You can also write `python makefile.py build`, `python makefile.py clean`, `python makefile.py install [install_location]` or `python makefile.py test` to trigger one of the four different callbacks.

There is also the `python makefile.py config` command, which doesn't trigger a callback but enters into an interactive mode for editing a configuration file.

Alternatively, you can also use the option `-b` or `--build`, `-c` or `--clean`, `-i` or `--install`, `-t` or `--test` and `-f` or `--config`.  
This alternative has a great advantage: you can combine multiple tasks. For example, running `python makefile.py -btci` will first trigger the clean callback, then the build callback, the install callback and finally the test callback.

> [!IMPORTANT]  
> The order will always be config -> clean -> build -> install -> test.

You can also replace the `-b` argument with `-r` (using `-br` does the same as `-r`) and this will force the makefile to recompile everything, without trying to figure out which file needs to be recompiled.

There are many more options you can add such as `-d` (`--debug`), `-q` (`--quiet`), `-v` (`--verbose`), etc...

All these options can be listed by running `python makefile.py -h` or if you haven't created a makefile yet, by directly calling the module `python -m powermake -h` or just `powermake -h` if the pip installation is in your path.

> [!IMPORTANT]  
> While `python makefile.py install` and `python makefile.py --install` takes the `install_location` as an optional argument, this argument has been disabled with the `-i` option, because writing `-bic` would have triggered the install callback with the location `c`


### Toolchain detection

PowerMake infers the various toolchain programs to be used using everything it knows.  
Most of the time, just setting up the C compiler configuration (or the C++ compiler or the linker, etc...) will be sufficient for PowerMake to determinate the whole toolchain.

> [!NOTE]  
> Only the unspecified fields are inferred, the field explicitly assigned in the json configuration (see [powermake.Config](#powermakeconfig)) are left unchanged. The only exception is when CC, CXX or LD env variables are specified (see below)

The environment variables CC, CXX and LD can be used to overwrite the C compiler, C++ compiler and linker tools path.  
For example, the command below will compile using the afl-\* toolchain. The C++ compiler and the linker are inferred from the C compiler (but only if they are not specified in the json configuration).
```sh
CC=afl-gcc python makefile.py -rvd
```

This is especially useful to quickly compile with a different toolchain. For example if you want to exceptionally compile an executable for Windows using Linux:
```sh
CC=x86_64-w64-mingw32-gcc python makefile.py -rvd
```


### PowerMake flags translation

When this is possible, PowerMake tries to translate C/C++/AS/ASM/LD flags.

Most flags are unknown to PowerMake, in this case they are simply transmitted to the compiler and it's your job to ensure the compatibility with the different targets through the use of if/else blocks.

However, the most common flags are automatically translated by PowerMake.  
Their is also some flags that PowerMake defines that doesn't exist in any compiler, these are set of useful flags for a situation.

Here is the list of flags translated by PowerMake:  
> [!NOTE]  
> Only compiler flags are listed, they are also translated for the linker but most of the time this ends up being just the removal of the flag.


| PowerMake Flag |  Description                   |
| :------------: | :----------------------------: |
| -w             | Inhibit all warning messages.  |
| -Werror        | Make all warnings into errors. |
| -Wall          | Activate warnings about all constructs that are unlikely to be intended. |
| -Wextra        | Enable flags that are likely to catch bugs even though they may warn on perfectly valid code. |
| -Wpedantic     | Warn when the code isn't ISO (typically when C/C++ extension are used). |
| -pedantic      | Same a -Wpedantic |
| -Wswitch       | Warn when a switch on an enum lacks a case (enabled by -Wall) |
| -Wswitch-enum  | Like -Wswitch but warns even if their is a default case |
| -fanalyzer     | When supported by the compiler, run the code into a static analyzer to detect some bugs. |
| -Weverything   | Enable as most warning as possible, even the noisy and irrelevant ones. |
| -Wsecurity     | Enable all warnings that have a little chance to catch a security issue. |
| -O0            | Disable all optimizations. |
| -Og            | Enable optimizations that don't interfere with the debugger. This is better than -O0 for debugging because some warnings and analysis require some optimization. |
| -O1            | Enable optimization but try to mitigate compile time. |
| -O             | Same as -O1. |
| -O2            | Performs nearly all supported optimizations. |
| -O3            | Optimize aggressively for speed. |
| -Ofast         | Enable all -O3 optimizations + some some optimization that can brake the program. |
| -Os            | Optimize for size. |
| -Oz            | Optimize aggressively for size rather than speed. |
| -fomit-frame-pointer | Omit the frame pointer in functions that don’t need one. |
| -m32           | If supported, switch to x86 architecture (you should prefer using [config.set_target_architecture](#set_target_architecture)). |
| -m64           | If supported, switch to x64 architecture (you should prefer using [config.set_target_architecture](#set_target_architecture)). |
| -march=native  | Generate a program optimized for CPUs that have the same capabilities of the host. |
| -mtune=native  | Optimize a program for the specific CPU of the host, even if this program will run slower or not at all on any other machine. |
| -mmx           | Enable mmx vectorization. |
| -msse          | Enable sse vectorization. |
| -msse2         | Enable sse2 vectorization. |
| -msse3         | Enable sse3 vectorization. |
| -mavx          | Enable avx vectorization. |
| -mavx2         | Enable avx2 vectorization. |
| -g             | Compile with debug symbols. |
| -fPIC          | Position Independent Code, required when compiling objects that will be bundled in a shared library. |
| -fsecurity=1   | Enable all flags that can mitigate security issues with negligible impact on performance. Warnings included. |
| -fsecurity=2   | Enable all flags that can mitigate security issues. |
| -fsecurity     | same as -fsecurity=2. |
| -ffuzzer       | Enable the address sanitizer and the fuzzer. |


### powermake.run
```py
powermake.run(target_name: str, *, build_callback: callable, clean_callback: callable = default_on_clean, install_callback: callable = default_on_install, test_callback: callable = default_on_test, args_parsed: argparse.Namespace = None)
```
It's the entry point of most programs.  
This function parses the command line and generates a [powermake.Config](#powermakeconfig) object, containing all the information required for the compilation, from the compiler path to the level of verbosity to use.

Then, depending on the command line arguments, this function will call the clean callback, the build callback, the install callback, or all of them.

The `target_name` is a string that will be stored in the config and which will be used for auto-naming. You should set this to the name of your executable or the name of your library.

The `build_callback` and the `clean_callback` only take 1 argument: The [powermake.Config](#powermakeconfig) object generated.

Example:
```py
import powermake


def on_build(config: powermake.Config):
    print("The build callback was called !")
    print(f"Compiling the project {config.target_name}...")

def on_clean(config: powermake.Config):
    print("The clean callback was called !")
    print(f"Erasing the project {config.target_name}...")


powermake.run("my_project", build_callback=on_build, clean_callback=on_clean)
```

The `install_callback` takes 2 arguments: The [powermake.Config](#powermakeconfig) object and a string `location` that can be `None` if the user hasn't specified anything on the command line.

> [!TIP]  
> It's often a very good idea to use the `install_callback` as a "pre-install script" and then call `powermake.default_on_install`.
> 
> Example:
> ```py
> import powermake
> 
> 
> def on_build(config: powermake.Config):
>     print("The build callback was called !")
>     print(f"Compiling the lib {config.target_name}...")
> 
> def on_install(config: powermake.Config, location: str):
>     if location is None:
>         # No location is explicitly provided so we change the default for our convenience.
>         location = "/usr/local/"
>     
>     # This ensures that the file "my_lib.h" will be exported into /usr/local/include/my_lib/my_lib.h
>     # The .so or .a that corresponds will be copied into /usr/local/lib/my_lib.so
>     config.add_exported_headers("my_lib.h", subfolder="my_lib")
> 
>     powermake.default_on_install(config, location)
> 
> 
> powermake.run("my_lib", build_callback=on_build, clean_callback=on_clean)
> ```


The `test_callback` also takes 2 arguments: The [powermake.Config](#powermakeconfig) object and a list of string representing the arguments of the tested program.

Example:
```py
import powermake


def on_build(config: powermake.Config):
    print("The build callback was called !")
    print(f"Compiling the project {config.target_name}...")


def on_test(config: powermake.Config, args: list[str]):
    print("test callback called")
    powermake.default_on_test(config, args)


powermake.run("my_project", build_callback=on_build, test_callback=on_test)
```


The `args_parsed` argument should be left to None in most cases, to understand his purpose, see [powermake.ArgumentsParser.parse_args](#parse_args)

### powermake.Config

This is the most important object of this library.  
It contains everything you need for your compilation journey. For example, it stores the C compiler alongside the path to the build folder.

Most of the time, this object is created by [powermake.run](#powermakerun) and you don't need to worry about the constructor of this object (which is a bit messy...).

But one thing you have to know is that the construction of this object involves 4 steps:
- step 1: It checks the value of the CC and CXX environment variables and if they are set, it sets the path of the C compiler and the C++ compiler with these variables. This makes sure that powermake is compatible with clang `scan-build` utility.
- step 2: It loads the local config file, by default stored at `./powermake_config.json` just next to the `makefile.py` (or whatever name your makefile has)
- step 3: It completes the local config with the global config, by default, stored in your home, at `~/.powermake/powermake_config.json` (If you create an env variable named `POWERMAKE_CONFIG`, you can override this location.).
- step 4: For all fields that are left empty, powermake will try to create a default value from your platform information.
  
In theory, after the end of these 4 steps, all members of the `powermake.Config` object should be set.  
In rare cases, if powermake was enabled to detect a default compiler, the `c_compiler`, `cpp_compiler`, `archiver`, and `linker` members can be None.  
In this situation, it's your responsibility to give them a value before the call to the `powermake.compile_files` function.


If you haven't, we recommend you try compiling your code without setting any `powermake_config.json`. In most cases, the automatic detection of your environment does a good job of finding your compiler/system/etc...

We provide a tool to interactively set your configuration file, you use it either by running `python -m powermake` or `python makefile.py config`, but this tool cannot configure everything, so we provide here an example of a `powermake_config.json`.  
Here, everything is set, but **you should set the bare minimum**, especially, you shouldn't set the "host_architecture", it's way better to let the script find it.  
Please note that this example is incoherent, but it shows as many options as possible.

```json
{
    "nb_jobs": 8,
    "compile_commands_dir": ".vscode/",
    "host_operating_system": "Linux",
    "target_operating_system": "Windows",
    "host_architecture": "x64",
    "target_architecture": "x86",

    "c_compiler": {
        "type": "gcc",
        "path": "/usr/bin/gcc"
    },
    "cpp_compiler": {
        "type": "clang++"
    },
    "as_compiler": {
      "type": "gcc",
      "path": "/usr/bin/gcc"
    },
    "asm_compiler": {
      "type": "nasm",
      "path": "/usr/bin/nasm"
    },
    "archiver": {
        "type": "ar",
        "path": "/usr/bin/ar"
    },
    "linker": {
        "type": "gnu",
        "path": "/usr/bin/cc"
    },
    "shared_linker": {
        "type": "g++",
        "path": "/usr/bin/g++"
    },

    "obj_build_directory": "./build/objects/",
    "lib_build_directory": "./build/lib/",
    "exe_build_directory": "./build/bin/",

    "defines": ["WIN32", "DEBUG"],
    "additional_includedirs": ["/usr/local/include", "../my_lib/"],
    "shared_libs": ["mariadb", "ssl", "crypto"],
    "flags": ["-Wall"],
    "c_flags": ["-fanalyzer", "-O3"],
    "cpp_flags": ["-g", "-O0"],
    "c_cpp_flags": ["-Wswitch"],
    "as_flags": [],
    "asm_flags": ["-s"],
    "rc_flags": [],
    "c_cpp_as_asm_flags": ["-Wall", "-Wextra"],
    "ar_flags": [],
    "ld_flags": ["-static", "-no-pie"],
    "shared_linker_flags": ["-fPIE"],

    "exported_headers": ["my_lib.h", ["my_lib_linux.h", "my_lib/linux"], ["my_lib/windows.h", "my_lib/windows"]]
}
```


#### Members

All fields that can be set in the `powermake_config.json` have the same name in the `powermake.Config` object, so we have grouped them below.

Most of the `powermake.Config` members can be set in the json configuration but there are 4 exceptions: `config.debug`, `config.rebuild`, `config.nb_total_operations` and `config.target_name`.

##### debug
```py
config.debug: bool
```
This member is `True` if the the makefile is ran in debug mode (with the flag -d or the flag --debug).  
Changing this at runtime will not do anything useful, please use [powermake.set_debug](#set_debug).

> [!IMPORTANT]  
> This member is one of the 4 exceptions that can't be set in the json configuration.


##### rebuild
```py
config.rebuild: bool
```
This member is `True` if the the makefile is ran in rebuild mode (with the flag -r or the flag --rebuild).  
If you change its value at runtime, the following steps will change their behavior.

> [!IMPORTANT]  
> This member is one of the 4 exceptions that can't be set in the json configuration.


##### nb_total_operations
```py
config.nb_total_operations: int
```
This member is always 0 after the creation of a new powermake.Config object, if you set a value > 0, if PowerMake is not in quiet mode, it will display a percent of the compilation elapsed at each step, calculated based on the value of this member.

For example, if you compile `len(files)` files and you then link all these files, you should set:
```py
config.nb_total_operations = len(files) + 1
```

> [!IMPORTANT]  
> This member is one of the 4 exceptions that can't be set in the json configuration.


##### target_name
```py
config.target_name: str
```

The name registered by [powermake.run](#powermakerun). It's used to determine the default name of executables and libraries.

> [!IMPORTANT]  
> This member is one of the 4 exceptions that can't be set in the json configuration.


##### nb_jobs
```py
config.nb_jobs: int
```

This number determines how many threads the compilation should be parallelized.  
If non-set or set to zero, this number is chosen according to the number of CPU cores you have.

Set this to 1 to disable multithreading.

This can be overwritten by the command-line with the `-j` option.


##### compile_commands_dir
```py
config.compile_commands_dir: str | None
```
If this is set, [powermake.compile_files](#powermakecompile_files) will generate a `compile_commands.json` in the directory specified by this parameter.


##### host_operating_system
```py
config.host_operating_system: str
```
A string representing the name of your operating system.

> [!TIP]  
> It's not recommended to set this in the json file, the autodetection should do a better job.


##### target_operating_system
```py
config.target_operating_system: str
```

A string representing the name of the operating system for which the executable is for.  
It's used to determine the subfolder of the build folder and for the functions `target_is_linux`, `target_is_windows`, etc...

On Linux, if you set this to "Windows" (or anything that starts win "win"), it will enable mingw as the default toolchain.

- You can write this in the json configuration, but only if you are doing cross-compilation, on the other hand, you should let powermake retrieve this value.
> [!WARNING]  
> Note that if you change this value in the script after the config is loaded, [obj_build_directory](#obj_build_directory), [lib_build_directory](#lib_build_directory) and [exe_build_directory](#exe_build_directory) will not be updated.


##### host_architecture
```py
config.host_architecture: str
```
A string representing the architecture of your system, which can be "amd64", "x64", "x86", "i386", etc...  
If you need an easier string to work with, use `config.host_simplified_architecture` which can only be "x86", "x64", "arm32" or "arm64".

> [!TIP]  
> It's not recommended to set this in the json file, the autodetection should do a better job.


##### target_architecture
```py
config.target_architecture: str
```
A string representing the architecture of the executable, which can be "amd64", "x64", "x86", "i386", etc...  
If you need an easier string to work with, use `config.target_simplified_architecture` which can only be "x86", "x64", "arm32" or "arm64".  
It's used to determine the subfolder of the build folder and to set the compiler architecture (if possible).

- You can write this in the json configuration, but only if you are doing cross-compilation, on the other hand, you should let powermake retrieve this value.
> [!WARNING]  
> Note that if you change this value in the script after the config is loaded, the environment will not be reloaded and the compiler will keep the previous architecture, use [config.set_target_architecture](#set_target_architecture) to reload the environment.


##### c_compiler
```py
config.c_compiler: powermake.compilers.Compiler
```

This one is different in the json config and the loaded config.

In the json config, it's defined as an object with 2 fields, like this:
```json
"c_compiler": {
    "type": "gcc",
    "path": "/usr/bin/gcc"
},
```
If the `"path"` field is omitted, the compiler corresponding to the type is searched in the path. For example if `"type"` is `"msvc"`, the compiler "cl.exe" is searched in the path.

If the `"type"` field is omitted, his value is determined based on the name of the executable and the rest of the toolchain.


- The `"type"` field can have the value `"gnu"`, `"gcc"`, `"clang"`, `"mingw"`, `"msvc"` or `"clang-cl"`.  
  It determines the syntax that should be used. For example, if you are using afl-gcc, the syntax of the compiler is the same as the `gcc` syntax.  
  For mingw on Windows, our compiler should be set like this:
  ```json
  "c_compiler" {
      "type": "gcc",
      "path": "C:\\msys64\\ucrt64\\bin\\gcc.exe"
  }
  ```
> [!NOTE]  
> For mingw on Windows, you should simply set  `C:\msys64\ucrt64\bin` in your PATH and powermake will be able to find it automatically

- The `"path"` field indicates where is the executable of the compiler. Note that PATH searching is always applied, so `"gcc"` work as well as `"/usr/bin/gcc"`  
  For using i386-elf-gcc on Linux, your compiler can be set like this:
  ```json
  "c_compiler" {
      "type": "gcc",
      "path": "i386-elf-gcc"
  }
  ```

When the `powermake.Config` object is loaded, the `c_compiler` member is no longer a `dict`, it's a virtual class that inherits from `powermake.compilers.Compiler` and which can generate compile commands. see [documentation is coming]

##### cpp_compiler
```py
config.cpp_compiler: powermake.compilers.Compiler
```

The cpp_compiler behave exactly like the [c_compiler](#c_compiler) but the possible types are:
- `gnu++`
- `g++`
- `clang++`
- `msvc`
- `mingw++`

You can also use one of the [c_compiler](#c_compiler) types, but in this case you **must** add a path, or the compilers will not be C++ compilers.


##### as_compiler
```py
config.as_compiler: powermake.compilers.Compiler
```

This compiler is used to compile GNU Assembly (.s and .S files)

The as_compiler behave exactly like the [c_compiler](#c_compiler) but the possible types are:
- `gnu`
- `gcc`
- `clang`
- `mingw`

You can also use one of the [asm_compiler](#asm_compiler) types if you have to compile a .s or .S file with `nasm` or something like that.


##### asm_compiler
```py
config.asm_compiler: powermake.compilers.Compiler
```

This compiler is used to compile .asm files (generally Intel asm)

The asm_compiler behave exactly like the [c_compiler](#c_compiler) but the only type currently supported is:
- `nasm`

You can also use one of the [as_compiler](#as_compiler) types if you have to compile a .asm file with a GNU assembler.


##### rc_compiler
```py
config.rc_compiler: powermake.compilers.Compiler
```

This compiler is used to compile .rc files (for now exclusively for mingw)

The rc_compiler behave exactly like the [c_compiler](#c_compiler) but the only type currently supported is:
- `windres`


##### archiver
```py
config.archiver: powermake.archivers.Archiver
```
The archiver is the program used to create a static library.

The configuration in the json behave exactly like the [c_compiler](#c_compiler) but the possible types are:
- `gnu`
- `ar`
- `llvm-ar`
- `msvc`
- `mingw`

Once loaded, the `config.archiver` is a virtual class that inherits from `powermake.archivers.Archiver`.


##### linker
```py
config.linker: powermake.linkers.Linker
```

The configuration in the json behave exactly like the [c_compiler](#c_compiler) but the possible types are:
- `gnu`
- `gnu++`
- `gcc`
- `g++`
- `clang`
- `clang++`
- `ld`
- `msvc`
- `mingw`
- `mingw++`

Once loaded, the `config.linker` is a virtual class that inherits from `powermake.linkers.Linker`.


##### shared_linker
```py
config.shared_linker: powermake.shared_linkers.SharedLinker
```

The configuration in the json behaves exactly like [config.linker](#linker) but is used to link shared libraries.

Once loaded, the `config.shared_linker` is a virtual class that inherits from `powermake.shared_linkers.SharedLinker`.


##### obj_build_directory
```py
config.obj_build_directory: str
```

This is the directory in which all .o (or equivalent) will be stored.

> [!TIP]  
> It's not recommended to set this in the json file, the automatic path generation should do a better job, ensuring that debug/release, windows/Linux, or x86/x64 doesn't have any conflict.


##### lib_build_directory
```py
config.lib_build_directory: str
```

This is the directory in which all .a, .so, .lib, .dll, etc... will be stored.

> [!TIP]  
> It's not recommended to set this in the json file, the automatic path generation should do a better job, ensuring that debug/release, windows/Linux, or x86/x64 doesn't have any conflict.


##### exe_build_directory
```py
config.exe_build_directory: str
```

This is the directory in which the linked executable will be stored.

> [!TIP]  
> It's not recommended to set this in the json file, the automatic path generation should do a better job, ensuring that debug/release, windows/Linux, or x86/x64 doesn't have any conflict.


##### defines
```py
config.defines: list[str]
```

This is a list of some defines that will be used during the compilation process.

- This list is merged from the local and global config
> [!TIP]  
> It's not recommended to set this in the json file, it makes much more sense to add these defines directly in the makefile with [config.add_defines](#add_defines), if needed, in a conditional statement like `if config.target_is_windows():`


##### additional_includedirs
```py
config.additional_includedirs: list[str]
```

This is a list of additional includedirs that will be used during the compilation process.

- This list is merged from the local and global config
> [!TIP]  
> It's not recommended to set this in the json file, it makes much more sense to add these includedirs directly in the makefile with [config.add_includedirs](#add_includedirs), if needed, in a conditional statement like `if config.target_is_windows():`


##### shared_libs
```py
config.shared_libs: list[str]
```

This is a list of shared libraries that will be used for the link.

- This list is merged from the local and global config
> [!TIP]  
> It's not recommended to set this in the json file, it makes much more sense to add these shared libs directly in the makefile with [config.add_shared_libs](#add_shared_libs), if needed, in a conditional statement like `if config.target_is_windows():`


##### c_flags
```py
config.c_flags: list[str]
```

A list of flags that will be passed to the C compiler (not the C++ compiler).

If in the powermake known flags list, these flags are translated for the specific compiler.  
If not, they are simply passed to the compiler.

- This list is merged from the local and global config
> [!TIP]  
> It's not recommended to set this in the json file, it makes much more sense to add these flags directly in the makefile with [config.add_c_flags](#add_c_flags), if needed, in a conditional statement like `if config.target_is_windows():`


##### cpp_flags
```py
config.cpp_flags: list[str]
```

A list of flags that will be passed to the C++ compiler (not the C compiler).

If in the powermake known flags list, these flags are translated for the specific compiler.  
If not, they are simply passed to the compiler.

- This list is merged from the local and global config
> [!TIP]  
> It's not recommended to set this in the json file, it makes much more sense to add these flags directly in the makefile with [config.add_cpp_flags](#add_cpp_flags), if needed, in a conditional statement like `if config.target_is_windows():`


##### c_cpp_flags
```py
config.c_cpp_flags: list[str]
```

A list of flags that will be passed to the C compiler AND the C++ compiler.

If in the powermake known flags list, these flags are translated for the specific compiler.  
If not, they are simply passed to the compiler.

In the `powermake.Config` object, this list doesn't correspond to a real list, it's just a property. You can read the value of `config.c_cpp_flags`, it's just the concatenation of `c_flags` and `cpp_flags`, but you can't edit this property, you have to use [config.add_c_cpp_flags](#add_c_cpp_flags) and [config.remove_c_cpp_flags](#remove_c_cpp_flags)

- This list is merged from the local and global config
> [!TIP]  
> It's not recommended to set this in the json file, it makes much more sense to add these flags directly in the makefile with [config.add_c_cpp_flags](#add_c_cpp_flags), if needed, in a conditional statement like `if config.target_is_windows():`


##### as_flags
```py
config.as_flags: list[str]
```

A list of flags that will be passed to the GNU assembly compiler.

If in the powermake known flags list, these flags are translated for the specific compiler.  
If not, they are simply passed to the compiler.

- This list is merged from the local and global config
> [!TIP]  
> It's not recommended to set this in the json file, it makes much more sense to add these flags directly in the makefile with [config.add_as_flags](#add_as_flags), if needed, in a conditional statement like `if config.target_is_windows():`


##### asm_flags
```py
config.asm_flags: list[str]
```

A list of flags that will be passed to the Intel ASM compiler.

If in the powermake known flags list, these flags are translated for the specific compiler.  
If not, they are simply passed to the compiler.

- This list is merged from the local and global config
> [!TIP]  
> It's not recommended to set this in the json file, it makes much more sense to add these flags directly in the makefile with [config.add_asm_flags](#add_asm_flags), if needed, in a conditional statement like `if config.target_is_windows():`


##### rc_flags
```py
config.rc_flags: list[str]
```

A list of flags that will be passed to the RC compiler (only WindRes on MinGW for now).

- This list is merged from the local and global config
> [!TIP]  
> It's not recommended to set this in the json file, it makes much more sense to add these flags directly in the makefile with [config.add_rc_flags](#add_asm_flags), if needed, in a conditional statement like `if config.target_is_mingw():`


##### c_cpp_as_asm_flags
```py
config.c_cpp_as_asm_flags: list[str]
```

A list of flags that will be passed to the C AND the C++ compiler AND the AS compiler AND the ASM compiler.

This behaves exactly like [config.c_cpp_flags](#c_cpp_flags), with the same limitations.


##### ar_flags
```py
config.ar_flags: list[str]
```

A list of flags that will be passed to the archiver.

If in the powermake known flags list, these flags are translated for the specific archiver.  
If not, they are simply passed to the archiver.

- This list is merged from the local and global config
> [!TIP]  
> It's not recommended to set this in the json file, it makes much more sense to add these flags directly in the makefile with [config.add_ar_flags](#add_ar_flags), if needed, in a conditional statement like `if config.target_is_windows():`


##### ld_flags
```py
config.ld_flags: list[str]
```

A list of flags that will be passed to the linker.

If in the powermake known flags list, these flags are translated for the specific linker.  
If not, they are simply passed to the linker.

- This list is merged from the local and global config
> [!TIP]  
> It's not recommended to set this in the json file, it makes much more sense to add these flags directly in the makefile with [config.add_ld_flags](#add_ld_flags), if needed, in a conditional statement like `if config.target_is_windows():`


##### shared_linker_flags
```py
config.shared_linker_flags: list[str]
```

A list of flags that will be passed to the linker when linking a shared library.

This behaves exactly like [config.ld_flags](#c_cpp_flags), with the same limitations.


##### flags
```py
config.flags: list[str]
```

A list of flags that will be passed to the C AND the C++ compiler AND the AS compiler AND the ASM compiler AND the shared linker AND the the linker

This behaves exactly like [config.c_cpp_flags](#c_cpp_flags), with the same limitations.


##### exported_headers
```py
config.exported_headers: list[str | tuple[str, str | None]]
```

This is a list of .h and .hpp that need to be exported in a `include` folder during the installation process.

This list can directly contain strings, in this case, the file is exported at the root of the `include` folder.  
This list can also contain 2 elements lists. The first element is the file to export and the second element is the subfolder of the `include` folder in which the file should be exported.

- This list is merged from the local and global config
> [!TIP]  
> It's not recommended to set this in the json file, it makes much more sense to add these headers directly in the makefile with [config.add_exported_headers](#add_exported_headers), if needed, in a conditional statement like `if config.target_is_windows():`



#### Methods

These are all the methods you can call from the `powermake.Config` object.  
You can access all members to read them, but you should use these methods if possible to set them, to ensure that everything stays coherent.


##### set_debug()
```py
config.set_debug(debug: bool = True, reset_optimization: bool = False)
```

If `debug` is True, set everything to be in debug mode. It replaces the `NDEBUG` defined by `DEBUG`, adds the `-g` flag and if possible modifies the output dir to change from a release folder to a debug folder.

If `debug` is False, set everything to be in release mode. (does the opposite of what's explained above)

If `reset_optimization` is set to True, then a `debug` to True will put the optimization to `-Og` and a `debug` to False will put the optimization to `-O3`

> [!NOTE]  
> If possible you should prefer using the command-line instead of this function.


##### set_optimization()
```py
config.set_optimization(opt_flag: str)
```

Remove all optimization flags set and add the `opt_flag`.

`opt_flag` should be on the [GCC format](https://gcc.gnu.org/onlinedocs/gcc/Optimize-Options.html)

Possible values are:
```
-O0
-Og (default in debug)
-O
-O1
-O2
-O3 (default in release)
-Os
-Oz
-Ofast
```

<details>
<summary>Example</summary>

```py
def on_build(config: powermake.Config):
    config.set_optimization("-Oz")

    # We can imagine that file1 and file2 must be compiled to optimize the space
    objects = powermake.compile_files(config, {"file1.c", "file2.c"})

    config.set_optimization("-O3")

    # when file3 and file4 must be compiled to be as fast as possible
    objects.update(powermake.compile_files(config, {"file3.c", "file4.c"}))

    powermake.link_files(config, objects)
```

</details>

##### set_target_architecture()
```py
config.set_target_architecture(architecture: str) -> None:
```

Reset the target architecture to the one specified.  
This will reload compilers to produce code for the good architecture.

##### target_is_windows()
```py
config.target_is_windows()
```

Returns `True` if the target operating system is Windows.
This uses the [config.target_operating_system](#target_operating_system) member.

<details>
<summary>Example</summary>

```py
def on_build(config: powermake.Config):
    if config.target_is_windows() or config.target_is_mingw():
        config.add_defines("WIN32")
    elif config.target_is_linux():
        config.add_defines("LINUX")
    elif config.target_is_macos():
        config.add_defines("DARWIN")
    else:
        print("Warning: no define has been set")

    files = powermake.get_files("**/*.c")
    objects = powermake.compile_files(config, files)

    powermake.link_files(config, objects)
```

</details>

##### target_is_linux()
```py
config.target_is_linux()
```

Returns `True` if the target operating system is Linux.
This uses the [config.target_operating_system](#target_operating_system) member.

<details>
<summary>Example</summary>

```py
def on_build(config: powermake.Config):
    if config.target_is_windows() or config.target_is_mingw():
        config.add_defines("WIN32")
    elif config.target_is_linux():
        config.add_defines("LINUX")
    elif config.target_is_macos():
        config.add_defines("DARWIN")
    else:
        print("Warning: no define has been set")

    files = powermake.get_files("**/*.c")
    objects = powermake.compile_files(config, files)

    powermake.link_files(config, objects)
```

</details>


##### target_is_mingw()
```py
config.target_is_mingw()
```

Returns `True` if the target operating system is MinGW
This uses the [config.target_operating_system](#target_operating_system) member and the [config.c_compiler](#c_compiler) member.

<details>
<summary>Example</summary>

```py
def on_build(config: powermake.Config):
    if config.target_is_windows() or config.target_is_mingw():
        config.add_defines("WIN32")
    elif config.target_is_linux():
        config.add_defines("LINUX")
    elif config.target_is_macos():
        config.add_defines("DARWIN")
    else:
        print("Warning: no define has been set")

    files = powermake.get_files("**/*.c")
    objects = powermake.compile_files(config, files)

    powermake.link_files(config, objects)
```

</details>


##### target_is_macos()
```py
config.target_is_macos()
```

Returns `True` if the target operating system is MacOS.
This uses the [config.target_operating_system](#target_operating_system) member.

<details>
<summary>Example</summary>

```py
def on_build(config: powermake.Config):
    if config.target_is_windows() or config.target_is_mingw():
        config.add_defines("WIN32")
    elif config.target_is_linux():
        config.add_defines("LINUX")
    elif config.target_is_macos():
        config.add_defines("DARWIN")
    else:
        print("Warning: no define has been set")

    files = powermake.get_files("**/*.c")
    objects = powermake.compile_files(config, files)

    powermake.link_files(config, objects)
```

</details>


##### add_defines()
```py
config.add_defines(*defines: str)
```

Add new defines to [config.defines](#defines) if they do not exist.  
This method is variadic so you can put as many defines as you want.  
The list order is preserved.

<details>
<summary>Example</summary>

```py
def on_build(config: powermake.Config):
    config.add_defines("LINUX", "_GNU_SOURCE", "PERSONAL_DEFINE")

    files = powermake.get_files("**/*.c")
    objects = powermake.compile_files(config, files)

    powermake.link_files(config, objects)
```

</details>


##### remove_defines()
```py
config.remove_defines(*defines: str)
```

Remove defines from [config.defines](#defines) if they exists.  
This method is variadic so you can put as many defines as you want.

<details>
<summary>Example</summary>

```py
def on_build(config: powermake.Config):
    config.add_defines("LINUX", "_GNU_SOURCE", "PERSONAL_DEFINE")

    objects = powermake.compile_files(config, {"file1.c", "file2.c"})

    config.remove_defines("PERSONAL_DEFINE", "_GNU_SOURCE")

    objects.update(powermake.compile_files(config, {"file3.c", "file4.c"}))

    powermake.link_files(config, objects)
```

</details>


##### add_shared_libs()
```py
config.add_shared_libs(*shared_libs: str)
```

Add shared libraries to [config.shared_libs](#shared_libs) if they do not exist.  
This method is variadic so you can put as many libs as you want.  
The list order is preserved.

<details>
<summary>Example</summary>

```py
def on_build(config: powermake.Config):
    files = powermake.get_files("**/*.c", "**/*.cpp")

    config.add_includedirs("/usr/include/mariadb/")

    # Will add the `-lmariadb` option during link time
    config.add_shared_libs("mariadb")

    objects = powermake.compile_files(config, files)

    powermake.link_files(config, objects)
```

</details>



##### remove_shared_libs()
```py
config.remove_shared_libs(*shared_libs: str)
```

Remove shared libraries from [config.shared_libs](#shared_libs) if they exists.  
This method is variadic so you can put as many libs as you want.


##### add_includedirs()
```py
config.add_includedirs(*includedirs: str)
```

Add additional includedirs to [config.additional_includedirs](#additional_includedirs) if they do not exist.  
This method is variadic so you can put as many includedirs as you want.  
The list order is preserved.


##### remove_includedirs()
```py
config.remove_includedirs(*includedirs: str)
```

Remove additional includedirs from [config.additional_includedirs](#additional_includedirs) if they exists.  
This method is variadic so you can put as many includedirs as you want.  
The list order is preserved.


##### add_flags()
```py
config.add_flags(*flags: str)
```

Add flags to [config.flags](#flags) if they do not exist.  
This method is variadic so you can put as many flags as you want.  
The list order is preserved.


##### remove_flags()
```py
config.remove_flags(*c_flags: str)
```

Remove flags from [config.flags](#flags) if they exists.  
This method is variadic so you can put as many flags as you want.  
The list order is preserved.


##### add_c_flags()
```py
config.add_c_flags(*c_flags: str)
```

Add flags to [config.c_flags](#c_flags) if they do not exist.  
This method is variadic so you can put as many flags as you want.  
The list order is preserved.


##### remove_c_flags()
```py
config.remove_c_flags(*c_flags: str)
```

Remove flags from [config.c_flags](#c_flags) if they exists.  
This method is variadic so you can put as many flags as you want.  
The list order is preserved.


##### add_cpp_flags()
```py
config.add_cpp_flags(*cpp_flags: str)
```

Add flags to [config.cpp_flags](#cpp_flags) if they do not exist.  
This method is variadic so you can put as many flags as you want.  
The list order is preserved.


##### remove_cpp_flags()
```py
config.remove_cpp_flags(*cpp_flags: str)
```

Remove flags from [config.cpp_flags](#cpp_flags) if they exists.  
This method is variadic so you can put as many flags as you want.  
The list order is preserved.


##### add_c_cpp_flags()
```py
config.add_c_cpp_flags(*c_cpp_flags: str)
```

Add flags to [config.c_cpp_flags](#c_cpp_flags) if they do not exist.  
This method is variadic so you can put as many flags as you want.  
The list order is preserved.


##### remove_c_cpp_flags()
```py
config.remove_c_cpp_flags(*c_cpp_flags: str)
```

Remove flags from [config.c_cpp_flags](#c_cpp_flags) if they exists.  
This method is variadic so you can put as many flags as you want.  
The list order is preserved.


##### add_as_flags()
```py
config.add_as_flags(*as_flags: str)
```

Add flags to [config.as_flags](#as_flags) if they do not exist.  
This method is variadic so you can put as many flags as you want.  
The list order is preserved.


##### remove_as_flags()
```py
config.remove_as_flags(*as_flags: str)
```

Remove flags from [config.as_flags](#as_flags) if they exists.  
This method is variadic so you can put as many flags as you want.  
The list order is preserved.


##### add_asm_flags()
```py
config.add_asm_flags(*asm_flags: str)
```

Add flags to [config.asm_flags](#asm_flags) if they do not exist.  
This method is variadic so you can put as many flags as you want.  
The list order is preserved.


##### remove_asm_flags()
```py
config.remove_asm_flags(*asm_flags: str)
```

Remove flags from [config.asm_flags](#asm_flags) if they exists.  
This method is variadic so you can put as many flags as you want.  
The list order is preserved.


##### add_c_cpp_as_asm_flags()
```py
config.add_c_cpp_as_asm_flags(*c_cpp_as_asm_flags: str)
```

Add flags to [config.c_cpp_as_asm_flags](#c_cpp_as_asm_flags) if they do not exist.  
This method is variadic so you can put as many flags as you want.  
The list order is preserved.


##### remove_c_cpp_as_asm_flags()
```py
config.remove_c_cpp_as_asm_flags(*c_cpp_as_asm_flags: str)
```

Remove flags from [config.c_cpp_as_asm_flags](#c_cpp_as_asm_flags) if they exists.  
This method is variadic so you can put as many flags as you want.  
The list order is preserved.

##### add_rc_flags()
```py
config.add_rc_flags(*rc_flags: str)
```

Add flags to [config.rc_flags](#rc_flags) if they do not exist.  
This method is variadic so you can put as many flags as you want.  
The list order is preserved.


##### remove_rc_flags()
```py
config.remove_rc_flags(*rc_flags: str)
```

Remove flags from [config.rc_flags](#rc_flags) if they exists.  
This method is variadic so you can put as many flags as you want.  
The list order is preserved.


##### add_ar_flags()
```py
config.add_ar_flags(*ar_flags: str)
```

Add flags to [config.ar_flags](#ar_flags) if they do not exist.  
This method is variadic so you can put as many flags as you want.  
The list order is preserved.


##### remove_ar_flags()
```py
config.remove_ar_flags(*ar_flags: str)
```

Remove flags from [config.ar_flags](#ar_flags) if they exists.  
This method is variadic so you can put as many flags as you want.  
The list order is preserved.


##### add_ld_flags()
```py
config.add_ld_flags(*ld_flags: str)
```

Add flags to [config.ld_flags](#ld_flags) if they do not exist.  
This method is variadic so you can put as many flags as you want.  
The list order is preserved.


##### remove_ld_flags()
```py
config.remove_ld_flags(*ld_flags: str)
```

Remove flags from [config.ld_flags](#ld_flags) if they exists.  
This method is variadic so you can put as many flags as you want.  
The list order is preserved.


##### add_shared_linker_flags()
```py
config.add_shared_linker_flags(*shared_linker_flags: str)
```

Add flags to [config.shared_linker_flags](#shared_linker_flags) if they do not exist.  
This method is variadic so you can put as many flags as you want.  
The list order is preserved.


##### remove_shared_linker_flags()
```py
config.remove_shared_linker_flags(*shared_linker_flags: str)
```

Remove flags from [config.shared_linker_flags](#shared_linker_flags) if they exists.  
This method is variadic so you can put as many flags as you want.  
The list order is preserved.


##### add_exported_headers()
```py
config.add_exported_headers(*exported_headers: str, subfolder: str = None)
```

Add exported headers to [config.exported_headers](#exported_headers) if they do not exist.  
This method is variadic so you can put as many headers as you want.  
The list order is preserved.

By default, there is no subfolder, but we recommend you use `config.target_name` for the `subfolder` argument.


##### remove_exported_headers()
```py
config.remove_exported_headers(*exported_headers: str, subfolder: str = None)
```

Remove exported headers from [config.exported_headers](#exported_headers) if they exists.  
This method is variadic so you can put as many headers as you want.  
The list order is preserved.


##### copy()
```py
config.copy()
```

Returns a new config object which is a deepcopy of the config. It should be used to compile different set of files with different parameters.


##### empty_copy()
```py
config.empty_copy(local_config: str = None) -> powermake.Config
```

Generate a new fresh config object without anything inside. By default, even the local config file isn't loaded.  
It can be very helpful if you have a local config file specifying a cross compiler but you want to have the default compiler at some point during the compilation step.


### powermake.default_on_clean
```py
powermake.default_on_clean(config: powermake.Config)
```

This is the default callback used by [powermake.run](#powermakerun) if the `clean_callback` is unspecified but you can use it whenever you want.

It cleans the obj, lib, and exe build directories of the `config`


### powermake.default_on_install
```py
powermake.default_on_install(config: Config, location: str)
```

This is the default callback used by [powermake.run](#powermakerun) if the `install_callback` is unspecified but you can use it whenever you want.  
If you overwrite the `install_callback` (which is the normal way of adding exported headers), you should call this function inside your defined callback to have a coherent installation. See the example in [powermake.run](#powermakerun)

Each library compiled is copied and put in a directory named `lib`.
Each header in [config.exported_headers](#exported_headers) is copied and put in a directory named `include`.
Each executable compiled is copied and put in a directory named `bin`.

The final structure is as follows:
```
location
    |_ include
        |_ eventual_subfolders
            |_ my_lib.h
    |_ lib
        |_ my_lib.a
    |_ bin
        |_ my_program
```

If `location` is None, the default is `./install/`.


### powermake.get_files
```py
powermake.get_files(*patterns: str) -> set
```

Returns a set of filepaths that matches at least one of the patterns.

Authorized patterns are:
- `*` to match a filename, for example `"foo/*.c"` will match `"foo/test.c"` but not `"foo/bar/test.c"`
- `**/` to match recursive directories, for example, `"foo/**/test.c"` will match  `"foo/test.c"` and `"foo/bar/test.c"`.  
> [!IMPORTANT]  
> `"**.c"` will not match `"foo/test.c"`, you have to write `"**/*.c"` for that.

This function is variadic.


### powermake.filter_files
```py
powermake.filter_files(files: set, *patterns: str) -> set
```

From a given set of filepaths, remove every file that matches at least one of the patterns.  
Returns a new filepaths set, filtered.

Authorized patterns are:
- `*` to match a filename, for example `"foo/*.c"` will match `"foo/test.c"` but not `"foo/bar/test.c"`
- `**/` to match recursive directories, for example, `"foo/**/test.c"` will match  `"foo/test.c"` and `"foo/bar/test.c"`.  
> [!IMPORTANT]  
> `"**.c"` will not match `"foo/test.c"`, you have to write `"**/*.c"` for that.

This function is variadic.


### powermake.compile_files
```py
powermake.compile_files(config: powermake.Config, files: set, force: bool = None) -> set
```

This function is a wrapper of lower-level powermake functions.

From a set or a list of `.c`, `.cpp`, `.cc`, `.C`, `.s`, `.S`, `.rc` and `.asm` filepaths and a [powermake.Config](#powermakeconfig) object, runs the compilation of each file in parallel, with the appropriate compiler and options found in `config`.

- If `force` is True, all files are recompiled, even if they are up to date.
- If `force` is False, only the files that are not up to date are recompiled
- If `force` is None (default), the value of `config.rebuild` is used.

Returns a set of `.o` (or compiler equivalent) filepaths for the next step.  
If `files` is a list, the function returns a list with the order preserved.


### powermake.archive_files
```py
powermake.archive_files(config: powermake.Config, object_files: set, archive_name: str = None, force: bool = None) -> str
```

This function is a wrapper of lower-level powermake functions.

From a set of `.o` (or compiler equivalent) filepaths, maybe the one returned by [powermake.compile_files](#powermakecompile_files) and a [powermake.Config](#powermakeconfig) object, runs the command to create a static library with the appropriate archiver and options in `config`.

- if `archive_name` is None, the `config.target_name` is concatenated with the prefix `"lib"` so if `config.target_name` is `"XXX"`, the name will be `"libXXX"` and then the extension given by the type of archiver is added.
- if `archiver_name` is not None, only the extension is added, if you want to use this parameter and you want your lib to be `"libXXX"`, you have to explicitly write `"libXXX"`.

- If `force` is True, the archive is re-created, even if it's up to date.
- If `force` is False, the archive is created only if not up to date.
- If `force` is None (default), the value of `config.rebuild` is used.

Returns the path of the static library generated.


### powermake.link_files
```py
powermake.link_files(config: powermake.Config, object_files: set, archives: list = [], executable_name: str = None, force: bool = None) -> str
```

This function is a wrapper of lower-level powermake functions.

From a set of `.o` (or compiler equivalent) filepaths, maybe the one returned by [powermake.compile_files](#powermakecompile_files) and a [powermake.Config](#powermakeconfig) object, it runs the command to create a n executable with the appropriate linker and options in `config`.

- if `executable_name` is None, the `config.target_name` is used with the extension given by the type of linker.
- if `executable_name` is not None, his value is concatenated with the extension.

- If `force` is True, the executable is re-created, even if it's up to date.
- If `force` is False, the executable is created only if not up to date.
- If `force` is None (default), the value of `config.rebuild` is used.

Returns the path of the executable generated.


### powermake.link_shared_lib
```py
powermake.link_shared_lib(config: Config, object_files: set, archives: list = [], lib_name: str = None, force: bool = None) -> str
```

This function is a wrapper of lower-level powermake functions.

From a set of `.o` (or compiler equivalent) filepaths, maybe the one returned by [powermake.compile_files](#powermakecompile_files) and a [powermake.Config](#powermakeconfig) object, runs the command to create a shared library with the appropriate shared linker and options in `config`.

- if `lib_name` is None, the `config.target_name` is concatenated with the prefix `"lib"` so if `config.target_name` is `"XXX"`, the name will be `"libXXX"` and then the extension given by the type of shared linker is added.
- if `lib_name` is not None, only the extension is added, if you want to use this parameter and you want your lib to be `"libXXX"`, you have to explicitly write `"libXXX"`.

- If `force` is True, the lib is re-created, even if it's up to date.
- If `force` is False, the lib is created only if not up to date.
- If `force` is None (default), the value of `config.rebuild` is used.

Returns the path of the shared library generated.

> [!TIP]  
> Don't forget to compile the `object_files` with the flag `-fPIC`.


### powermake.delete_files_from_disk
```py
powermake.delete_files_from_disk(*filepaths: str)
```

Remove each filepath and skip if it doesn't exist.

This function is variadic.


### powermake.run_another_powermake
```py
powermake.run_another_powermake(config: powermake.Config, path: str, debug: bool = None, rebuild: bool = None, verbosity: int = None, nb_jobs: int = None, command_line_args: T.List[str] = []) -> list
```

Run a powermake from another directory and return a list of paths to all libraries generated.

If the parameters `debug`, `rebuild`, `verbosity`, and `nb_jobs` are left to None, the values in `config` are used.  
These parameters are passed to the other powermake.

You can pass any other parameter that you want in the list `command_line_args`.

This function ensure that if a powermake A depends on powermakes B and C and the powermake B and the powermake C both depends on the powermake D, the powermake D will not be ran twice, even if the flag `-r` is provided.

> [!WARNING]  
> This function is not thread safe for now.


### powermake.run_command_if_needed
```py
run_command_if_needed(config: powermake.Config, outputfile: str, dependencies: Iterable[str], command: list[str] | str, shell: bool = False, force: bool | None = None, **kwargs: Any) -> str
```

Run a command generating a file only if this file needs to be re-generated.

Raise a PowerMakeRuntimeError if the command fails.

`outputfile` is the file generated by the command and `dependencies` is an iterable of every file that if changed should trigger the run of the command.

- If `shell` is `False`:
  - `command` should be a list like `argv`. The first element should be an executable and each following element will be distinct parameters.  
  This list is then directly passed to `subprocess.run`

- If `shell` is `False`:
  - `command` should be a string representing the shell command.


- If `force` is True, the command is run anyway.
- If `force` is False, the command is only run if `outputfile` is up to date with its dependencies.
- If `force` is None (default), the value of `config.rebuild` is used.

`**kwargs` is passed to `powermake.run`


### powermake.needs_update
```py
powermake.needs_update(outputfile: str, dependencies: set, additional_includedirs: list) -> bool
```

> [!NOTE]  
> This function is low-level.

Returns whether or not `outputfile` is up to date with all his dependencies.  
If `dependencies` include C/C++ files and headers, all headers these files include recursively will be added as hidden dependencies.

The `additional_includedirs` list is required to discover hidden dependencies. You must set this to the additional includedirs used during the compilation of `outputfile`. You can use [config.additional_includedirs](#additional_includedirs) if needed.


### powermake.run_command
```py
run_command(config: powermake.Config, command: list[str] | str, shell: bool = False, target: str | None = None, output_filter: Callable[[bytes], bytes] | None = None, **kwargs) -> int
```

> [!NOTE]  
> This function is low-level.

Run a command regardless of what it does and if it's needed.

Returns the exit code of the command.

If `shell` is `False`:
- `command` should be a list like `argv`. The first element should be an executable and each following element will be distinct parameters.  
  This list is then directly passed to `subprocess.run`

If `shell` is `False`:
- `command` should be a string representing the shell command.

`target` is currently only been used to print the name of the file generated, but in the future, it might be used to generate a Makefile.

`output_filter` is a callback that can be used to edit the output of the command before it's printed to the screen. Warning, the output of the command is in bytes with no encoding determined. Let this to `None` to just print the output of the command.

`**kwargs` is passed to `powermake.run`


### powermake.Operation (deprecated)
```py
powermake.Operation(outputfile: str, dependencies: set, config: Config, command: list)
```

> [!NOTE]  
> This object is low-level.

This is a simple object to execute a command only if needed.  
It can be used to easily parallelize multiple commands.
> [!TIP]  
> You can use [powermake.compile_files](#powermakecompile_files) which does that for you, but only for C/C++/AS/ASM files.

> [!WARNING]  
> Directly using powermake.Operation is deprecated

The command should be a list like `argv`. The first element should be an executable and each following element will be distinct parameters.  
This list is then directly passed to `subprocess.run`

#### execute()
```py
operation.execute(force: bool = False) -> str
```

Run the `command` if `outputfile` is not up to date.

If `force` is True, the command is run in any case.


### Having more control than what powermake.run offers

> [!NOTE]  
> This section is advanced.

#### powermake.ArgumentParser
```py
powermake.ArgumentParser(prog: str = None, description: str = None, **kwargs)
```

This object is a superset of [argparse.ArgumentParser](https://docs.python.org/3/library/argparse.html), you can read the documentation of argparse, it works exactly the same.
> [!CAUTION]  
> **Use this object and never argparse.ArgumentParser directly** or you will break some powermake features. Obviously the usual command line options will be broken but you will also break other features like the [powermake.run_another_powermake](#powermakerun_another_powermake) function. This object ensure that none of this is broken.

##### add_argument()

See the [argparse documentation](https://docs.python.org/3/library/argparse.html) to understand how to add an argument

##### parse_args()
```py
parser.parse_args()
```

Returns a namespace containing each value parsed from the command line.  
This namespace can be used to take decisions and should then be passed to [powermake.run](#powermakerun) or [powermake.generate_config](#powermakegenerate_config).  
Example:
```py
import powermake

def on_build(config: powermake.Config):
    ...

parser = powermake.ArgumentParser()
parser.add_argument("--foo")

args_parsed = parser.parse_args()

print(args_parsed.foo)

powermake.run("program_test", build_callback=on_build, args_parsed=args_parsed)
```


#### powermake.generate_config
```py
powermake.generate_config(target_name: str, args_parsed: argparse.Namespace = None)
```

This function behave like the first part of [powermake.run](#powermakerun), it generate a config object according to the command line. The difference with [powermake.run](#powermakerun) is that it stop at this point and returns the config generated.  
It can be helpful if you want a global instance of the config.

In most cases you should let `args_parsed` to None, and this function will automatically parse the command line.

> [!CAUTION]  
> You have to call `powermake.run_callback` after the call of this function (but you can obviously do something between these 2 functions)


#### powermake.run_callbacks
```py
run_callbacks(config: Config, *, build_callback: callable, clean_callback: callable = default_on_clean, install_callback: callable = default_on_install, test_callback: callable = default_on_test)
```

This function only make sense after a call of [powermake.generate_config](#powermakegenerate_config).  
It takes a newly generated config and run each callback according to the command line.

> [!CAUTION]  
> If neither this function nor powermake.run is used, the powermake.run_another_powermake function will be partially broken

Example:
```py
import powermake

def on_build(config: powermake.Config):
    ...

config = powermake.generate_config("program_test")

powermake.run_callbacks(config, build_callback=on_build)
```


## Compatibility with other tools

### Scan-Build

Powermake is compatible with clang [scan-build](https://clang.llvm.org/docs/analyzer/user-docs/CommandLineUsage.html#scan-build) utility.  
You can run `scan-build python makefile.py -rd` to compile your code with a static analysis.  
Just remember that scan-build needs your program to be compiled in debug mode, hence the `-d` flag.

We recommend you try compiling your code with different static analyzers to catch as many problems as possible.  
We especially recommend gcc and the `-fanalyzer` option, it's one of the most powerful analyzer we know and PowerMake will ensure that this flag will be removed if unsupported.

> [!TIP]  
> You should set the `-fanalyzer` flag during both compilation **and** link and use the `-flto` flag to enable link time optimization, like this the analyzer can work accros translation units.

### LLVM libfuzzer

Powermake helps you compile with [LLVM libfuzzer](https://llvm.org/docs/LibFuzzer.html).

You can add the `-ffuzzer` argument to your compiler and your linker with [config.add_c_cpp_flags](#add_c_cpp_flags) and [config.add_ld_flags](#add_ld_flags).

If you are using clang or MSVC, this will enable the address sanitizer and fuzzer.
Otherwise, the argument is ignored.


### GNU Make

Since PowerMake 1.20.0, PowerMake is able to generate a GNU Makefile
You just have to run:
```sh
python makefile.py -m
```
This will rebuild the powermake (here in release mode) and will generate a GNU Makefile.
If you want your makefile to be in debug mode, and with a certain toolchain, or with whatever custom argument just run your PowerMake like you would do and add the -m flag.
```sh
CC=x86_64-w64-mingw32-gcc python makefile.py -md
```

> [!WARNING]  
> PowerMake tries its best to generate a valid Makefile, however, because of the [PowerMake philosophy](./README.md#philosophy), PowerMake can't know exactly what you are doing in your Makefile, every function that is not provided by PowerMake can't be translated in the Makefile.  
> To get a good Makefile, you should never use the `subprocess` module but instead use [powermake.run_command](#powermakerun_command) or [powermake.run_command_if_needed](#powermakerun_command_if_needed).
>
> If you are doing conditions and loops, it's not a problem at all, but you will not see any condition in the generated Makefile, what's in the Makefile depends on the commands actually generated during the initial PowerMake compilation. (That's why the -m flag also enable the -r flag, to be sure that every command is ran.)


### Visual Studio Code

VSCode uses 3 important json files:
- `compile_commands.json`: Used to know how each file is compiled, which defines and includedirs are used, etc... Should be generated by PowerMake.
- `tasks.json`: Used to define how to compile the project. In our case, we want to run powermake in this file (PowerMake can help you write this file)
- `launch.json`: Used to launch the debugger (PowerMake can help you write this file)


> [!TIP]  
> If you don't have a .vscode folder, you can start by running
> ```sh
> python makefile.py --generate-vscode
> ```
> This will generate a .vscode folder that should work right out of the box when you press F5.
>
> If your makefile is not at the root of your project, you can specify the destination of the .vscode folder, for example:
> ```sh
> python makefile.py --generate-vscode ../
> ```
> You can also specify the .vscode folder in the path, that doesn't change anything
> ```sh
> python makefile.py --generate-vscode ../.vscode
> ```

> [!NOTE]  
> You need the Microsoft C/C++ Extension Pack for this to work


If the tip above isn't enough to setup vscode, here is more details:

The `compile_commands.json` can easily be generated by powermake with the option `-o` (`--compile-commands-dir`).
```sh
python makefile.py -o .vscode
```
However, we suggest you to just generate this whenever you compile your code with vscode, by putting the `-o` in the tasks.json like explained below.

Here is an example of a functional `.vscode/tasks.json`:
```json
{
    "tasks": [
        {
            "type": "cppbuild",
            "label": "powermake_compile",
            "command": "python",
            "args": [
                "makefile.py",
                "-rvd",  /* We rebuild each time so the warnings doesn't disappear, we build in debug mode and in verbose to verify if the good commands are ran. */
                "-o",
                "${workspaceFolder}/.vscode",  /* We regenerate a new compile_commands.json each time to keep track of new files and modifications in the PowerMake */
                "--retransmit-colors"  /* This is because the vscode task terminal is not a shell but still supports colors, so we have to tell PowerMake to not remove them */
            ],
            "options": {
                "cwd": "${workspaceFolder}"  /* Where to run `python makefile.py ...` */
            }
        },
        {
            /* This is fully optional, this task can be mapped to a shortcut (for example F6) so we can test the compilation of a single file */
            "type": "cppbuild",
            "label": "compile_single_file",
            "command": "python",
            "args": [
                "makefile.py",
                "-r",
                "-s",
                "${file}",
                "--retransmit-colors"
            ],
            "options": {
                "cwd": "${workspaceFolder}"
            }
        },
    ],
    "version": "2.0.0"
}
```
> [!NOTE]  
> You need the Microsoft C/C++ Extension Pack for this to work


Here is an example of a functional `.vscode/launch.json`:
```json
{
    "configurations": [
        {
            "name": "PowerMake Debug",
            "type": "cppdbg",
            "preLaunchTask": "powermake_compile",
            "request": "launch",
            "program": "${workspaceFolder}/build/Linux/x64/debug/bin/YOUR_PROGRAM",  /* Replace this path by the path of your program compiled */
            "args": [],  /* If your program requires arguments, put them here */
            "cwd": "${workspaceFolder}"
        }
    ]
}
```
> [!NOTE]  
> You need the Microsoft C/C++ Extension Pack for this to work

> [!IMPORTANT]  
> Once you have run `python makefile.py --generate-vscode` at least once, you can edit the default vscode template in `~/.powermake/vscode_templates/`.
> 
> If you want to regenerate one of these templates from the default, just delete the file dans run `python makefile.py --generate-vscode`


**documentation in progress...**
