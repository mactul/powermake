# PowerMake

- [PowerMake](#powermake)
  - [What is PowerMake ?](#what-is-powermake-)
  - [For which project is PowerMake suitable ?](#for-which-project-is-powermake-suitable-)
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
      - [host\_operating\_system](#host_operating_system)
      - [target\_operating\_system](#target_operating_system)
      - [host\_architecture](#host_architecture)
      - [target\_architecture](#target_architecture)
      - [c\_compiler](#c_compiler)
      - [cpp\_compiler](#cpp_compiler)


## What is PowerMake ?

Powermake is an utility to compile C/C++ code, just like Make, Ninja, cmake or xmake.

His goal is to give full power to the user, while being cross-platform, easier to use than Make and faster than Ninja.

## For which project is PowerMake suitable ?

PowerMake was specifically designed for complex projects that have very complicated compilation steps, with a lot of pre-built tasks and which need to be compiled on multiple operating systems with different options.

## Advantages of PowerMake

- Extremely fast:
  - PowerMake is faster than Ninja/make/xmake when building a project for the first time.
  - Their is still some improvements to do for detecting that their is nothing to do for very large codebase because PowerMake doesn't actually store hidden dependencies (headers files). But with less than 2000 files, this step is almost instant.

- Cross-Platform:
  - PowerMake is able to detect the compiler installed on your machine and give you an abstraction of the compiler syntax.
    - This currently works well with GCC/G++/Clang/Clang++/MSVC, but other compilers will be add.
  - Because it's written in python it works in almost all machine and you can always write the compilation instructions for your machine and for your compiler.

- Gives you complete control of what you are doing. Nothing is hidden and any behavior can be overwritten.

## Disadvantages of PowerMake

- PowerMake is very young so it changes a lot at each version and you may have to write some features by yourself (the whole point of PowerMake is that you can write missing features).

- Because PowerMake gives you full control, the tool can't really know what you are doing during the compilation step. For example, if we want to import dependencies from another PowerMake, the only thing we can do for you is running the PowerMake where it stands and scanning his output directory. This works well but has some limitations...

## Philosophy

All other Make-like utilities that I know parse a file to understand directives from it.

PowerMake does the opposite. You write a python script, you do whatever you like in this script and you call PowerMake functions to help you compiling your code.  
This gives you a complete control; you can retrieve files from the web, read an write files, even train a Neural Network if you want and at any time you can use Powermake functions to help you in your compilation journey.

## Installation

```sh
pip install -U powermake
```

## Quick Example

This example compile all `.c` and `.cpp` files that are recursively in the same folder as the python script and generate an executable named `program_test`

**Warning !** PowerMake calculate all paths from his own location, not the location where it is run.  
For example, `python ./folder/makefile.py` will do the same as `cd ./folder && python ./makefile.py`

**Note:** In this documentation, we often assume that your makefile is named `makefile.py`, it makes thing easier to explain. Of course, you can name your makefile the name you like the most.

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

### Command line arguments

To benefit from the command line parser, you have to use the [powermake.run](#powermakerun) function.

If no arguments are passed trough the command line, the default behavior is to trigger the build callback.  
You can also write `python makefile.py build`, `python makefile.py clean` or `python makefile.py install [install_location]` to trigger one of the three different callbacks.

Their is also the `python makefile.py config` command, that doesn't trigger a callback but enter into an interactive mode for editing a configuration file.

Alternatively, you can also use the option `-b` or `--build`, `-c` or `--clean`, `-i` or `--install` and `-f` or `--config`.  
This alternative has a great advantages: you can combine multiple tasks. For example, running `python makefile.py -bci` will first trigger the clean callback, then the build callback and finally the install callback. (The order will always be config -> clean -> build -> install).

You can also replace the `-b` argument with `-r` (using `-br` does the same as `-r`) and this will force the makefile to recompile everything, without trying to figure out which file needs to be recompiled.

There is many more options you can add such as `-d` (`--debug`), `-q` (`--quiet`), `-v` (`--verbose`), etc...

All these options can be listed by running `python makefile.py -h` (or `python makefile.py --help`)

/!\\ Specificity: While `python makefile.py install` and `python makefile.py --install` takes the `install_location` has an optional argument, this argument has been disabled with the `-i` option, because writing `-bic` would have trigger the install callback with the location `c`


### powermake.run
```py
powermake.run(target_name: str, *, build_callback: callable, clean_callback: callable = default_on_clean, install_callback: callable = default_on_install)
```
It's the entry point of most programs.  
This function parse the command line and generate a [powermake.Config](#powermakeconfig) object, containing all the information required for the compilation, from the compiler path to the level of verbosity to use.

Then, depending on the command line arguments, this function will call the clean callback, the build callback, the install callback or all of them.

The `target_name` is a string that will be stored in the config and which will be used for auto-naming. You should set this to the name of your executable or the name of your library.

The `build_callback` and the `clean_callback` only takes 1 argument: The [powermake.Config](#powermakeconfig) object generated.

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

**NOTE:** It's often a very good idea to use the `install_callback` has a "pre-install script" and then call `powermake.default_on_install`.

Example:

```py
import powermake


def on_build(config: powermake.Config):
    print("The build callback was called !")
    print(f"Compiling the lib {config.target_name}...")

def on_install(config: powermake.Config, location: str):
    if location is None:
        # No location is explicitly provided so we change the default for our convenance.
        location = "/usr/local/"
    
    # This ensure that the file "my_lib.h" will be exported into /usr/local/include/my_lib/my_lib.h
    # The .so or .a that corresponds will be copied into /usr/local/lib/my_lib.so
    config.add_exported_headers("my_lib.h", subfolder="my_lib")

    powermake.default_on_install(config, location)


powermake.run("my_lib", build_callback=on_build, clean_callback=on_clean)
```

### powermake.Config

This is the most important object of this library.  
It contains everything you need for your compilation journey. For example, it stores the C compiler alongside with the path to the build folder.

Most of the time, this object is created by [powermake.run](#powermakerun) and you don't need to worry about the constructor of this object (which is a bit messy...).

But one thing you have to know is that the construction of this object involve 3 steps:
- step 1: It loads the local config file, by default stored at `./powermake_config.json` just next to the `makefile.py` (or whatever name your makefile have)
- step 2: It complete the local config with the global config, by default, stored in your home, at `~/.powermake/powermake_config.json` (If you create an env variable named `POWERMAKE_CONFIG`, you can override this location.).
- step 3: For all fields that are left empty, powermake will try to create a default value from your platform information.
  
In theory, after the end of these 3 steps, all members of the `powermake.Config` object should be set.  
In rare case, if powermake was enable to detect a default compiler, the `c_compiler`, `cpp_compiler`, `archiver` and `linker` members can be None.  
In this situation, it's your responsibility to give them a value before the call to the `powermake.compile_files` function.


If you haven't, we recommend you to try compiling your code without setting any `powermake_config.json`. In most cases, the automatic detection of your environnement does a good job finding your compiler/system/etc...

We provide a tool to interactively set your configuration file, you use it either by running `python -m powermake` or `python makefile.py config`, but this tool cannot configure everything, so we provide here an example of a `powermake_config.json`.  
Here, everything is set, but **you should set the bare minimum**, especially, you shouldn't set the "host_architecture", it's way better to let the script find it.  
Please note that this example is incoherent, but it shows as many options as possible.

```json
{
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
    "archiver": {
        "type": "ar",
        "path": "/usr/bin/ar"
    },
    "linker": {
        "type": "gnu",
        "path": "/usr/bin/cc"
    },

    "obj_build_directory": "./build/objects/",
    "lib_build_directory": "./build/lib/",
    "exe_build_directory": "./build/bin/",

    "defines": ["WIN32", "DEBUG"],
    "additional_includedirs": ["/usr/local/include", "../my_lib/"],
    "c_flags": ["-fanalyzer", "-O3"],
    "cpp_flags": ["-g", "-O0"],
    "c_cpp_flags": ["-Wall", "-Wextra"],
    "ar_flags": [],
    "ld_flags": ["-static"],

    "exported_headers": ["my_lib.h", "my_lib_linux.h", "my_lib_windows.h"]
}
```

All fields have the same name in the `powermake_config.json` and in the `powermake.Config` object, so we have grouped them below.

#### host_operating_system

A string representing the name of your operating system. For the moment it doesn't serve any purpose, but you can access it if needed.

- **It's not recommended to set this in the json file, the autodetection should do a better job.**


#### target_operating_system

A string representing the name of the operating system for which the executable is for.  
It's used to determine the subfolder of the build folder and for the functions `target_is_linux`, `target_is_windows`, etc...

- You can write this in the json configuration, but only if you are doing cross-compilation, on the other hand, you should let powermake retrieve this value.
- **Note that if you change this value in the script after the config is loaded, [obj_build_directory](#obj_build_directory), [lib_build_directory](#lib_build_directory) and [exe_build_directory](#exe_build_directory) will not be updated**


#### host_architecture

A string representing the architecture of your system, it can be "amd64", "x64", "x86", "i386", etc...  
If you need an easier string to work with, use `config.host_simplified_architecture` which can only be "x86", "x64", "arm32" or "arm64".  
For the moment it doesn't serve any purpose, but you can access it if needed.

- **It's not recommended to set this in the json file, the autodetection should do a better job.**


#### target_architecture

A string representing the architecture of the executable, it can be "amd64", "x64", "x86", "i386", etc...  
If you need an easier string to work with, use `config.target_simplified_architecture` which can only be "x86", "x64", "arm32" or "arm64".  
It's used to determine the subfolder of the build folder and to set the compiler architecture. However, for the moment, gcc and clang only switch from 64 bits to 32 bits. If you are on x64 and you set the target_architecture to "arm32", you will in reality compile for x86. You have to give the path of a cross-compiler in order to achieve what you want.

- You can write this in the json configuration, but only if you are doing cross-compilation, on the other hand, you should let powermake retrieve this value.
- **Note that if you change this value in the script after the config is loaded, the MSVC environnement will not be reloaded and the compiler will keep the previous architecture**


#### c_compiler

This one is different in the json config and in the loaded config.

In the json config, it's define as an object with 2 fields, like that:
```json
"c_compiler": {
    "type": "gcc",
    "path": "/usr/bin/gcc"
},
```
If the `"path"` field is omitted, the compiler corresponding to the type is searched in the path. For example if `"type"` is `"msvc"`, the compiler "cl.exe" is searched in the path.

If the `"type"` field is omitted, his default value is `"gnu"`.


- The `"type"` field can have the value `"gnu"`, `"gcc"`, `"clang"`, `"msvc"` or `"clang-cl"`.  
  It determines the syntax that should be used. For example, if you are using mingw, the syntax of the compiler is the same as the `gcc` syntax and your compiler should be set like that:
  ```json
  "c_compiler" {
      "type": "gcc",
      "path": "C:\\msys64\\ucrt64\\bin\\gcc.exe"
  }
  ```
  *Note: for mingw on Windows, you should simply set  `C:\msys64\ucrt64\bin` in your PATH and powermake will be able to find it automatically*

- The `"path"` field indicate where is the executable of the compiler. Note that PATH searching is always applied, so `"gcc"` work as well as `"/usr/bin/gcc"`
  For mingw on Linux, your compiler can be set like this:
  ```json
  "c_compiler" {
      "type": "gcc",
      "path": "x86_64-w64-mingw32-gcc"
  }
  ```

When the `powermake.Config` object is loaded, the `c_compiler` member is no longer a `dict`, it's a virtual class which inherit from `powermake.compilers.Compiler` and which is able to generate compile commands. see [documentation in coming]

#### cpp_compiler

The cpp_compiler behave exactly like the [c_compiler](#c_compiler) but the possible types are:
- `g++`
- `clang++`
- `msvc`

You can also use one of the [c_compiler](#c_compiler) types, but in this case you **must** add a path or the compilers will not be C++ compilers.

### archiver

The archiver is the program used to create a static library.

The configuration in the json behave exactly like the [c_compiler](#c_compiler) but the possible types are:
- `gnu`
- `ar`
- `llvm-ar`
- `msvc`

Once loaded, the `config.archiver` is a virtual class that inherit from `powermake.archivers.Archiver`.


### linker

The configuration in the json behave exactly like the [c_compiler](#c_compiler) but the possible types are:
- `gnu`
- `gcc`
- `g++`
- `clang`
- `clang++`
- `msvc`

Once loaded, the `config.linker` is a virtual class that inherit from `powermake.archivers.Linker`.


documentation in progress...
