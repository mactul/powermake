# PowerMake

- [PowerMake](#powermake)
  - [What is PowerMake?](#what-is-powermake)
  - [For which project is PowerMake suitable?](#for-which-project-is-powermake-suitable)
  - [Advantages of PowerMake](#advantages-of-powermake)
  - [Disadvantages of PowerMake](#disadvantages-of-powermake)
  - [Philosophy](#philosophy)
  - [Installation](#installation)
  - [Quick Example](#quick-example)
    - [See more examples](#see-more-examples)
  - [Documentation](#documentation)
    - [Command line arguments](#command-line-arguments)
    - [powermake.run](#powermakerun)
    - [powermake.Config](#powermakeconfig)
      - [Members](#members)
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
        - [c\_cpp\_as\_asm\_flags](#c_cpp_as_asm_flags)
        - [ar\_flags](#ar_flags)
        - [ld\_flags](#ld_flags)
        - [shared\_linker\_flags](#shared_linker_flags)
        - [exported\_headers](#exported_headers)
      - [Methods](#methods)
        - [set\_debug()](#set_debug)
        - [set\_optimization()](#set_optimization)
        - [target\_is\_windows()](#target_is_windows)
        - [target\_is\_linux()](#target_is_linux)
        - [target\_is\_mingw()](#target_is_mingw)
        - [add\_defines()](#add_defines)
        - [remove\_defines()](#remove_defines)
        - [add\_shared\_libs()](#add_shared_libs)
        - [remove\_shared\_libs()](#remove_shared_libs)
        - [add\_includedirs()](#add_includedirs)
        - [remove\_includedirs()](#remove_includedirs)
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
        - [add\_ar\_flags()](#add_ar_flags)
        - [remove\_ar\_flags()](#remove_ar_flags)
        - [add\_ld\_flags()](#add_ld_flags)
        - [remove\_ld\_flags()](#remove_ld_flags)
        - [add\_shared\_linker\_flags()](#add_shared_linker_flags)
        - [remove\_shared\_linker\_flags()](#remove_shared_linker_flags)
        - [add\_exported\_headers()](#add_exported_headers)
        - [remove\_exported\_headers()](#remove_exported_headers)
        - [copy()](#copy)
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
    - [powermake.needs\_update](#powermakeneeds_update)
    - [powermake.Operation](#powermakeoperation)
      - [execute()](#execute)
    - [Compatibility with other tools](#compatibility-with-other-tools)
      - [Scan-Build](#scan-build)
      - [LLVM libfuzzer](#llvm-libfuzzer)


## What is PowerMake?

Powermake is a utility that compiles C/C++/AS/ASM code, just like Make, Ninja, cmake, or xmake.

His goal is to give full power to the user, while being cross-platform, easier to use than Make, and faster than Ninja.

## For which project is PowerMake suitable?

PowerMake was specifically designed for complex projects that have very complicated compilation steps, with a lot of pre-built tasks that need to be compiled on multiple operating systems with different options.

## Advantages of PowerMake

- Extremely fast:
  - PowerMake is faster than Ninja/make/xmake when building a project for the first time.
  - There are still some improvements to do to detect that there is nothing to do for a huge codebase because PowerMake doesn't store hidden dependencies (header files). But with less than 2000 files, this step is almost instant.

- Cross-Platform:
  - PowerMake can detect the compiler installed on your machine and give you an abstraction of the compiler syntax.
    - This currently works well with GCC/G++/Clang/Clang++/Clang-CL/MSVC/NASM, but other compilers will be added.
  - Because it's written in python it works on almost all machines and you can always write the compilation instructions for your machine and your compiler.

- Gives you complete control of what you are doing. Nothing is hidden and any behavior can be overwritten.

## Disadvantages of PowerMake

- PowerMake is very young so it changes a lot with each version and you may have to write some features by yourself (the whole point of PowerMake is that you can write missing features).

- Because PowerMake gives you full control, the tool can't know what you are doing during the compilation step. For example, if we want to import dependencies from another PowerMake, the only thing we can do for you is run the PowerMake where it stands and scan its output directory. This works well but has some limitations...

## Philosophy

All other Make-like utilities that I know parse a file to understand directives from it.

PowerMake does the opposite. You write a python script, you do whatever you like in this script and you call PowerMake functions to help you compile your code.  
This gives you complete control; you can retrieve files from the web, read and write files, and even train a Neural Network if you want, and at any time you can use Powermake functions to help you in your compilation journey.

## Installation

```sh
pip install -U powermake
```

## Quick Example

This example compiles all `.c` and `.cpp` files that are recursively in the same folder as the python script and generate an executable named `program_test`

**Warning !** PowerMake calculates all paths from his location, not the location where it is run.  
For example, `python ./folder/makefile.py` will do the same as `cd ./folder && python ./makefile.py`

**Note:** In this documentation, we often assume that your makefile is named `makefile.py`, it makes things easier to explain. Of course, you can name your makefile the name you like the most.

```py
import powermake


def on_build(config: powermake.Config):

    files = powermake.get_files("**/*.c", "**/*.cpp")

    objects = powermake.compile_files(config, files)

    print(powermake.link_files(config, objects))


powermake.run("program_test", build_callback=on_build)
```

### [See more examples](./examples.md)

## Documentation

**Note:** This documentation is not completed, if you struggle to do something, do not hesitate to ask a question in the [discussions section](https://github.com/mactul/powermake/discussions/categories/q-a), it may be that the feature you search for is undocumented.

### Command line arguments

To benefit from the command line parser, you have to use the [powermake.run](#powermakerun) function.

If no arguments are passed through the command line, the default behavior is to trigger the build callback.  
You can also write `python makefile.py build`, `python makefile.py clean`, or `python makefile.py install [install_location]` to trigger one of the three different callbacks.

There is also the `python makefile.py config` command, which doesn't trigger a callback but enters into an interactive mode for editing a configuration file.

Alternatively, you can also use the option `-b` or `--build`, `-c` or `--clean`, `-i` or `--install`, and `-f` or `--config`.  
This alternative has a great advantage: you can combine multiple tasks. For example, running `python makefile.py -bci` will first trigger the clean callback, then the build callback, and finally the install callback. (The order will always be config -> clean -> build -> install).

You can also replace the `-b` argument with `-r` (using `-br` does the same as `-r`) and this will force the makefile to recompile everything, without trying to figure out which file needs to be recompiled.

There are many more options you can add such as `-d` (`--debug`), `-q` (`--quiet`), `-v` (`--verbose`), etc...

All these options can be listed by running `python makefile.py -h` (or `python makefile.py --help`)

/!\\ Specificity: While `python makefile.py install` and `python makefile.py --install` takes the `install_location` as an optional argument, this argument has been disabled with the `-i` option, because writing `-bic` would have triggered the install callback with the location `c`


### powermake.run
```py
powermake.run(target_name: str, *, build_callback: callable, clean_callback: callable = default_on_clean, install_callback: callable = default_on_install)
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

**NOTE:** It's often a very good idea to use the `install_callback` as a "pre-install script" and then call `powermake.default_on_install`.

Example:

```py
import powermake


def on_build(config: powermake.Config):
    print("The build callback was called !")
    print(f"Compiling the lib {config.target_name}...")

def on_install(config: powermake.Config, location: str):
    if location is None:
        # No location is explicitly provided so we change the default for our convenience.
        location = "/usr/local/"
    
    # This ensures that the file "my_lib.h" will be exported into /usr/local/include/my_lib/my_lib.h
    # The .so or .a that corresponds will be copied into /usr/local/lib/my_lib.so
    config.add_exported_headers("my_lib.h", subfolder="my_lib")

    powermake.default_on_install(config, location)


powermake.run("my_lib", build_callback=on_build, clean_callback=on_clean)
```

### powermake.Config

This is the most important object of this library.  
It contains everything you need for your compilation journey. For example, it stores the C compiler alongside the path to the build folder.

Most of the time, this object is created by [powermake.run](#powermakerun) and you don't need to worry about the constructor of this object (which is a bit messy...).

But one thing you have to know is that the construction of this object involves 4 steps:
- step 1: It checks the value of the CC and CXX environment variables and if they are set, it sets the path of the C compiler and the C++ compiler with these variables. This makes sure that powermake is compatible with clang `scan-build` utility.
- step 2: It loads the local config file, by default stored at `./powermake_config.json` just next to the `makefile.py` (or whatever name your makefile has)
- step 3: It completes the local config with the global config, by default, stored in your home, at `~/.powermake/powermake_config.json` (If you create an env variable named `POWERMAKE_CONFIG`, you can override this location.).
- step 4: For all fields that are left empty, powermake will try to create a default value from your platform information.
  
In theory, after the end of these 3 steps, all members of the `powermake.Config` object should be set.  
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
    "c_flags": ["-fanalyzer", "-O3"],
    "cpp_flags": ["-g", "-O0"],
    "c_cpp_flags": ["-Wswitch"],
    "as_flags": [],
    "asm_flags": ["-s"],
    "c_cpp_as_asm_flags": ["-Wall", "-Wextra"],
    "ar_flags": [],
    "ld_flags": ["-static", "-no-pie"],
    "shared_linker_flags": ["-fPIE"],

    "exported_headers": ["my_lib.h", ["my_lib_linux.h", "my_lib/linux"], ["my_lib/windows.h", "my_lib/windows"]]
}
```


#### Members

All fields have the same name in the `powermake_config.json` and in the `powermake.Config` object, so we have grouped them below.

##### nb_jobs

This number determines how many threads the compilation should be parallelized.  
If non-set or set to zero, this number is chosen according to the number of CPU cores you have.

Set this to 1 to disable multithreading.

This can be overwritten by the command-line.


##### compile_commands_dir

If this is set, [powermake.compile_files](#powermakecompile_files) will generate a `compile_commands.json` in the directory specified by this parameter.


##### host_operating_system

A string representing the name of your operating system. For the moment it doesn't serve any purpose, but you can access it if needed.

- **It's not recommended to set this in the json file, the autodetection should do a better job.**


##### target_operating_system

A string representing the name of the operating system for which the executable is for.  
It's used to determine the subfolder of the build folder and for the functions `target_is_linux`, `target_is_windows`, etc...

- You can write this in the json configuration, but only if you are doing cross-compilation, on the other hand, you should let powermake retrieve this value.
- **Note that if you change this value in the script after the config is loaded, [obj_build_directory](#obj_build_directory), [lib_build_directory](#lib_build_directory) and [exe_build_directory](#exe_build_directory) will not be updated**


##### host_architecture

A string representing the architecture of your system, which can be "amd64", "x64", "x86", "i386", etc...  
If you need an easier string to work with, use `config.host_simplified_architecture` which can only be "x86", "x64", "arm32" or "arm64".  
For the moment it doesn't serve any purpose, but you can access it if needed.

- **It's not recommended to set this in the json file, the autodetection should do a better job.**


##### target_architecture

A string representing the architecture of the executable, which can be "amd64", "x64", "x86", "i386", etc...  
If you need an easier string to work with, use `config.target_simplified_architecture` which can only be "x86", "x64", "arm32" or "arm64".  
It's used to determine the subfolder of the build folder and to set the compiler architecture. However, for the moment, gcc and clang only switch from 64 bits to 32 bits. If you are on x64 and you set the target_architecture to "arm32", you will in reality compile for x86. You have to give the path of a cross-compiler to achieve what you want.

- You can write this in the json configuration, but only if you are doing cross-compilation, on the other hand, you should let powermake retrieve this value.
- **Note that if you change this value in the script after the config is loaded, the environment will not be reloaded and the compiler will keep the previous architecture**


##### c_compiler

This one is different in the json config and the loaded config.

In the json config, it's defined as an object with 2 fields, like this:
```json
"c_compiler": {
    "type": "gcc",
    "path": "/usr/bin/gcc"
},
```
If the `"path"` field is omitted, the compiler corresponding to the type is searched in the path. For example if `"type"` is `"msvc"`, the compiler "cl.exe" is searched in the path.

If the `"type"` field is omitted, his default value is `"gnu"`.


- The `"type"` field can have the value `"gnu"`, `"gcc"`, `"clang"`, `"msvc"` or `"clang-cl"`.  
  It determines the syntax that should be used. For example, if you are using mingw, the syntax of the compiler is the same as the `gcc` syntax, and the default callback used by [powermake.run](#powermakerun) if the `default_callback` is unspecified but you can use it whenever you want.
our compiler should be set like this:
  ```json
  "c_compiler" {
      "type": "gcc",
      "path": "C:\\msys64\\ucrt64\\bin\\gcc.exe"
  }
  ```
  *Note: for mingw on Windows, you should simply set  `C:\msys64\ucrt64\bin` in your PATH and powermake will be able to find it automatically*

- The `"path"` field indicates where is the executable of the compiler. Note that PATH searching is always applied, so `"gcc"` work as well as `"/usr/bin/gcc"`
  For mingw on Linux, your compiler can be set like this:
  ```json
  "c_compiler" {
      "type": "gcc",
      "path": "x86_64-w64-mingw32-gcc"
  }
  ```

When the `powermake.Config` object is loaded, the `c_compiler` member is no longer a `dict`, it's a virtual class that inherits from `powermake.compilers.Compiler` and which can generate compile commands. see [documentation is coming]

##### cpp_compiler

The cpp_compiler behave exactly like the [c_compiler](#c_compiler) but the possible types are:
- `gnu++`
- `g++`
- `clang++`
- `msvc`

You can also use one of the [c_compiler](#c_compiler) types, but in this case you **must** add a path, or the compilers will not be C++ compilers.


##### as_compiler

This compiler is used to compile GNU Assembly (.s and .S files)

The as_compiler behave exactly like the [c_compiler](#c_compiler) but the possible types are:
- `gnu`
- `gcc`
- `clang`

You can also use one of the [asm_compiler](#asm_compiler) types if you have to compile a .s or .S file with `nasm` or something like that.


##### asm_compiler

This compiler is used to compile .asm files (generally Intel asm)

The asm_compiler behave exactly like the [c_compiler](#c_compiler) but the only type currently supported is:
- `nasm`

You can also use one of the [as_compiler](#as_compiler) types if you have to compile a .asm file with a GNU assembler.


##### archiver

The archiver is the program used to create a static library.

The configuration in the json behave exactly like the [c_compiler](#c_compiler) but the possible types are:
- `gnu`
- `ar`
- `llvm-ar`
- `msvc`

Once loaded, the `config.archiver` is a virtual class that inherits from `powermake.archivers.Archiver`.


##### linker

The configuration in the json behave exactly like the [c_compiler](#c_compiler) but the possible types are:
- `gnu`
- `gnu++`
- `gcc`
- `g++`
- `clang`
- `clang++`
- `ld`
- `msvc`

Once loaded, the `config.linker` is a virtual class that inherits from `powermake.linkers.Linker`.


##### shared_linker

The configuration in the json behaves exactly like [config.linker](#linker) but is used to link shared libraries.

Once loaded, the `config.shared_linker` is a virtual class that inherits from `powermake.shared_linkers.SharedLinker`.


##### obj_build_directory

This is the directory in which all .o (or equivalent) will be stored.

- **It's not recommended to set this in the json file, the automatic path generation should do a better job, ensuring that debug/release, windows/Linux, or x86/x64 doesn't have any conflict.**


##### lib_build_directory

This is the directory in which all .a, .so, .lib, .dll, etc... will be stored.

- **It's not recommended to set this in the json file, the automatic path generation should do a better job, ensuring that debug/release, windows/Linux, or x86/x64 doesn't have any conflict.**


##### exe_build_directory

This is the directory in which the linked executable will be stored.

- **It's not recommended to set this in the json file, the automatic path generation should do a better job, ensuring that debug/release, windows/Linux, or x86/x64 doesn't have any conflict.**


##### defines

This is a list of some defines that will be used during the compilation process.

- This list is merged from the local and global config
- **It's not recommended to set this in the json file, it makes much more sense to add these defines directly in the makefile with [config.add_defines](#add_defines), if needed, in a conditional statement like `if config.target_is_windows():`**


##### additional_includedirs

This is a list of additional includedirs that will be used during the compilation process.

- This list is merged from the local and global config
- **It's not recommended to set this in the json file, it makes much more sense to add these includedirs directly in the makefile with [config.add_includedirs](#add_includedirs), if needed, in a conditional statement like `if config.target_is_windows():`**


##### shared_libs

This is a list of shared libraries that will be used for the link.

- This list is merged from the local and global config
- **It's not recommended to set this in the json file, it makes much more sense to add these shared libs directly in the makefile with [config.add_shared_libs](#add_shared_libs), if needed, in a conditional statement like `if config.target_is_windows():`**


##### c_flags

A list of flags that will be passed to the C compiler (not the C++ compiler).

If in the powermake known flags list, these flags are translated for the specific compiler.  
If not, they are simply passed to the compiler.

- This list is merged from the local and global config
- **It's not recommended to set this in the json file, it makes much more sense to add these flags directly in the makefile with [config.add_c_flags](#add_c_flags), if needed, in a conditional statement like `if config.target_is_windows():`**


##### cpp_flags

A list of flags that will be passed to the C++ compiler (not the C compiler).

If in the powermake known flags list, these flags are translated for the specific compiler.  
If not, they are simply passed to the compiler.

- This list is merged from the local and global config
- **It's not recommended to set this in the json file, it makes much more sense to add these flags directly in the makefile with [config.add_cpp_flags](#add_cpp_flags), if needed, in a conditional statement like `if config.target_is_windows():`**


##### c_cpp_flags

A list of flags that will be passed to the C compiler AND the C++ compiler.

If in the powermake known flags list, these flags are translated for the specific compiler.  
If not, they are simply passed to the compiler.

In the `powermake.Config` object, this list doesn't correspond to a real list, it's just a property. You can read the value of `config.c_cpp_flags`, it's just the concatenation of `c_flags` and `cpp_flags`, but you can't edit this property, you have to use [config.add_c_cpp_flags](#add_c_cpp_flags) and [config.remove_c_cpp_flags](#remove_c_cpp_flags)

- This list is merged from the local and global config
- **It's not recommended to set this in the json file, it makes much more sense to add these flags directly in the makefile with [config.add_c_cpp_flags](#add_c_cpp_flags), if needed, in a conditional statement like `if config.target_is_windows():`**


##### as_flags

A list of flags that will be passed to the GNU assembly compiler.

If in the powermake known flags list, these flags are translated for the specific compiler.  
If not, they are simply passed to the compiler.

- This list is merged from the local and global config
- **It's not recommended to set this in the json file, it makes much more sense to add these flags directly in the makefile with [config.add_as_flags](#add_as_flags), if needed, in a conditional statement like `if config.target_is_windows():`**


##### asm_flags

A list of flags that will be passed to the Intel ASM compiler.

If in the powermake known flags list, these flags are translated for the specific compiler.  
If not, they are simply passed to the compiler.

- This list is merged from the local and global config
- **It's not recommended to set this in the json file, it makes much more sense to add these flags directly in the makefile with [config.add_asm_flags](#add_asm_flags), if needed, in a conditional statement like `if config.target_is_windows():`**


##### c_cpp_as_asm_flags

A list of flags that will be passed to the C AND the C++ compiler AND the AS compiler AND the ASM compiler.

This behaves exactly like [config.c_cpp_flags](#c_cpp_flags), with the same limitations.


##### ar_flags

A list of flags that will be passed to the archiver.

If in the powermake known flags list, these flags are translated for the specific archiver.  
If not, they are simply passed to the archiver.

- This list is merged from the local and global config
- **It's not recommended to set this in the json file, it makes much more sense to add these flags directly in the makefile with [config.add_ar_flags](#add_ar_flags), if needed, in a conditional statement like `if config.target_is_windows():`**


##### ld_flags

A list of flags that will be passed to the linker.

If in the powermake known flags list, these flags are translated for the specific linker.  
If not, they are simply passed to the linker.

- This list is merged from the local and global config
- **It's not recommended to set this in the json file, it makes much more sense to add these flags directly in the makefile with [config.add_ld_flags](#add_ld_flags), if needed, in a conditional statement like `if config.target_is_windows():`**


##### shared_linker_flags

A list of flags that will be passed to the linker when linking a shared library.

This behaves exactly like [config.ld_flags](#c_cpp_flags), with the same limitations.


##### exported_headers

This is a list of .h and .hpp that need to be exported in a `include` folder during the installation process.

This list can directly contain strings, in this case, the file is exported at the root of the `include` folder.  
This list can also contain 2 elements lists. The first element is the file to export and the second element is the subfolder of the `include` folder in which the file should be exported.

- This list is merged from the local and global config
- **It's not recommended to set this in the json file, it makes much more sense to add these headers directly in the makefile with [config.add_exported_headers](#add_exported_headers), if needed, in a conditional statement like `if config.target_is_windows():`**



#### Methods

These are all the methods you can call from the `powermake.Config` object.  
You can access all members to read them, but you should use these methods if possible to set them, to ensure that everything stays coherent.


##### set_debug()
```py
config.set_debug(debug: bool = True, reset_optimization: bool = False)
```

If `debug` is True, set everything to be in debug mode. It replaces the `NDEBUG` defined by `DEBUG`, adds the `-g` flag and if possible modifies the output dir to change from a release folder to a debug folder.

If `debug` is False, set everything to be in release mode. (does the opposite of what's explained above)

If `reset_optimization` is set to True, then a `debug` to True will put the optimization to `-O0` and a `debug` to False will put the optimization to `-O3`

- **If possible you should prefer using the command-line instead of this function.**


##### set_optimization()
```py
config.set_optimization(opt_flag: str)
```

Remove all optimization flags set and add the `opt_flag`


##### target_is_windows()
```py
config.target_is_windows()
```

Returns `True` if the target operating system is Windows.
This uses the [config.target_operating_system](#target_operating_system) member.


##### target_is_linux()
```py
config.target_is_linux()
```

Returns `True` if the target operating system is Linux.
This uses the [config.target_operating_system](#target_operating_system) member.


##### target_is_mingw()
```py
config.target_is_mingw()
```

Returns `True` if the target operating system is MinGW
This uses the [config.target_operating_system](#target_operating_system) member and the [config.c_compiler](#c_compiler) member.


##### add_defines()
```py
config.add_defines(*defines: str)
```

Add new defines to [config.defines](#defines) if they do not exist.  
This method is variadic so you can put as many defines as you want.  
The list order is preserved.


##### remove_defines()
```py
config.remove_defines(*defines: str)
```

Remove defines from [config.defines](#defines) if they exists.  
This method is variadic so you can put as many defines as you want.


##### add_shared_libs()
```py
config.add_shared_libs(*shared_libs: str)
```

Add shared libraries to [config.shared_libs](#shared_libs) if they do not exist.  
This method is variadic so you can put as many libs as you want.  
The list order is preserved.


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
  Warning: `"**.c"` will not match `"foo/test.c"`, you have to write `"**/*.c"` for that.

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
  Warning: `"**.c"` will not match `"foo/test.c"`, you have to write `"**/*.c"` for that.

This function is variadic.


### powermake.compile_files
```py
powermake.compile_files(config: powermake.Config, files: set, force: bool = None) -> set
```

This function is a wrapper of lower-level powermake functions.

From a set or a list of `.c`, `.cpp`, `.cc`, `.C`, `.s`, `.S` and `.asm` filepaths and a [powermake.Config](#powermakeconfig) object, runs the compilation of each file in parallel, with the appropriate compiler and options found in `config`.

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


### powermake.delete_files_from_disk
```py
powermake.delete_files_from_disk(*filepaths: str)
```

Remove each filepath and skip if it doesn't exist.

This function is variadic.


### powermake.run_another_powermake
```py
powermake.run_another_powermake(config: powermake.Config, path: str, debug: bool = None, rebuild: bool = None, verbosity: int = None, nb_jobs: int = None) -> list
```

Run a powermake from another directory and return a list of paths to all libraries generated.

If the parameters `debug`, `rebuild`, `verbosity`, and `nb_jobs` are left to None, the values in `config` are used.  
These parameters are passed to the other powermake.


### powermake.needs_update
```py
powermake.needs_update(outputfile: str, dependencies: set, additional_includedirs: list) -> bool
```

This function is low-level.

Returns whether or not `outputfile` is up to date with all his dependencies.  
If `dependencies` include C/C++ files and headers, all headers these files include recursively will be added as hidden dependencies.

The `additional_includedirs` list is required to discover hidden dependencies. You must set this to the additional includedirs used during the compilation of `outputfile`. You can use [config.additional_includedirs](#additional_includedirs) if needed.


### powermake.Operation
```py
powermake.Operation(outputfile: str, dependencies: set, config: Config, command: list)
```

This is a simple object to execute a command only if needed.  
It can be used to easily parallelize multiple commands. Note that you can use [powermake.compile_files](#powermakecompile_files) which does that for you, but only for C/C++/AS/ASM files.

The command should be a list like `argv`. The first element should be an executable and each following element will be distinct parameters.  
This list is then directly passed to `subprocess.run`

#### execute()
```py
execute(self, force: bool = False, print_lock: threading.Lock = None) -> str
```

Run the `command` if `outputfile` is not up to date.

If `force` is True, the command is run in any case.

`print_lock` is a mutex that ensures that debug prints are not mixed.  
If you are parallelizing operations, you should set this mutex to avoid weird debug message behavior.  
If left to None, no mutex is used.

### Compatibility with other tools

#### Scan-Build

Powermake is compatible with clang [scan-build](https://clang.llvm.org/docs/analyzer/user-docs/CommandLineUsage.html#scan-build) utility.  
You can run `scan-build python makefile.py -rd` to compile your code with a static analysis.  
Just remember that scan-build needs your program to be compiled in debug mode, hence the `-d` flag.  
We recommend you try compiling your code with gcc and the `-fanalyzer` option to get the best results possible.

#### LLVM libfuzzer

Powermake helps you compile with [LLVM libfuzzer](https://llvm.org/docs/LibFuzzer.html).

You can add the `-ffuzzer` argument to your compiler and your linker with [config.add_c_cpp_flags](#add_c_cpp_flags) and [config.add_ld_flags](#add_ld_flags).

If you are using clang or MSVC, this will enable the address sanitizer and fuzzer.
Otherwise, the argument is ignored.

**documentation in progress...**
