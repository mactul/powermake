# PowerMake

<img alt="ubuntu x64 tests status" src="https://github.com/mactul/powermake/workflows/Run%20tests%20on%20ubuntu%20x64/badge.svg">
<img alt="windows x64 tests status" src="https://github.com/mactul/powermake/workflows/Run%20tests%20on%20windows%20x64/badge.svg">

<img alt="macos x64 tests status" src="https://github.com/mactul/powermake/workflows/Run%20tests%20on%20macos%20x64/badge.svg">
<img alt="macos arm64 tests status" src="https://github.com/mactul/powermake/workflows/Run%20tests%20on%20macos%20arm64/badge.svg">

- [PowerMake](#powermake)
  - [What is PowerMake?](#what-is-powermake)
  - [Does PowerMake generates a Makefile like CMake ?](#does-powermake-generates-a-makefile-like-cmake-)
  - [For which project is PowerMake suitable?](#for-which-project-is-powermake-suitable)
  - [Advantages of PowerMake](#advantages-of-powermake)
  - [Disadvantages of PowerMake](#disadvantages-of-powermake)
  - [Philosophy](#philosophy)
  - [Installation](#installation)
  - [Install from Pypi: (RECOMMENDED)](#install-from-pypi-recommended)
  - [install from sources: (NOT RECOMMENDED AT ALL)](#install-from-sources-not-recommended-at-all)
  - [Quick Example](#quick-example)
  - [More examples](#more-examples)
  - [Documentation](#documentation)
  - [Compatibility with other tools](#compatibility-with-other-tools)
    - [Scan-Build](#scan-build)
    - [LLVM libfuzzer](#llvm-libfuzzer)
    - [GNU Make](#gnu-make)
    - [Visual Studio Code](#visual-studio-code)


## What is PowerMake?

Powermake is a utility that compiles C/C++/AS/ASM code, just like Make, Ninja, cmake, or xmake.

His goal is to give full power to the user, while being cross-platform and easier to use than Make.

Powermake extends what is possible to do during the compilation by providing a lot of functions to manipulate your files and a lot of freedom on the way you will implement your makefile.  
Powermake is entirely configurable, but for every behavior you haven't explicitly defined, PowerMake will do most of the job for you by detecting installed toolchains, translating compiler flags, etc...


## Does PowerMake generates a Makefile like CMake ?

Not by default.
PowerMake does not build on top of make, it replaces make.

Since PowerMake 1.20.0, Powermake is able to generate a Makefile, but this will never be as powerful as PowerMake, this feature is only used if you really need a GNU Makefile for compatibility with old deployments/tests scripts.


## For which project is PowerMake suitable?

PowerMake was specifically designed for complex projects that have very complicated compilation steps, with a lot of pre-built tasks that need to be compiled on multiple operating systems with different options.

However, today, even for a 5 files project on Linux with GCC, PowerMake is more convenient than make because out of the box it provides a debug/release mode with different options and different build directories, it can generates a compile_commands.json file for a better integration with vscode, it detects better than make when files need to be recompiled, it provides default rebuild/clean/install options without any configuration, etc...


## Advantages of PowerMake

- Cross-Platform:
  - PowerMake can detect the compiler installed on your machine and give you an abstraction of the compiler syntax.
    - This currently works well with GCC/G++/Clang/Clang++/Clang-CL/MSVC/NASM, but other compilers will be added.
  - Because it's written in python it works on almost all machines and you can always write the compilation instructions for your machine and your compiler.

- Gives you complete control of what you are doing. Nothing is hidden and any behavior can be overwritten.
  - Missing features can always be written in the makefile.

- Provides good automatic configurations
  - PowerMake have local and global config files, but on top of that, PowerMake is able to automatically find a value that make sense for each field that is not explicitly assigned, you can easily have very basic configurations files (often no config file at all) and it will still work for most systems.

- Extremely fast:
  - PowerMake is faster than make/xmake and most of the time faster than Ninja when building a project for the first time.
  - There are still some improvements to do to detect that there is nothing to do for a huge codebase because PowerMake doesn't store hidden dependencies (header files). But with less than 2000 files, this step is almost instant.


## Disadvantages of PowerMake

- PowerMake is very young so it changes a lot with each version and you may have to write some features by yourself (the whole point of PowerMake is that you can write missing features). In theory retrocompatibilty is kept between versions, but this might not be true if you are using very specific features, especially undocumented ones.

- Because PowerMake gives you full control, the tool can't know what you are doing during the compilation step. For example, if we want to import dependencies from another PowerMake, the only thing we can do for you is run the PowerMake where it stands and scan its output directory. This works well but has some limitations... Another example of this problem is that PowerMake can't know how many steps will be done during the compilation, so if you want PowerMake to print the percent of compilation elapsed, you have to manually specify the number of steps PowerMake will do.


## Philosophy

All other Make-like utilities that I know parse a file to understand directives from it.

PowerMake does the opposite. You write a python script, you do whatever you like in this script and you call PowerMake functions to help you compile your code.  
This gives you complete control; you can retrieve files from the web, read and write files, and even train a Neural Network if you want, and at any time you can use Powermake functions to help you in your compilation journey.

This also mean that the philosophy is completely different than in tool like make.  
When you read a GNU Makefile, you start at the end, the final target and you read each target dependency recursively before executing the task.  
In a GNU Makefile, the order of each target doesn't reflect at all the order of execution.

Powermake is read as a script. the order of each instruction has a capital importance. The first step is read, if it needs to be executed, it's executed, then the next step is read, etc...
- The main advantage of this approach is that it's extremely easy to write and read the makefile, it's just a good old script that executes from top to bottom. You can also do loops, functions, etc... everything python offers, which is way more powerful than the make approach.
- The main disadvantage of this approach is that steps during the makefile can't automatically be parallelized. [powermake.compile_files](./documentation.md#powermakecompile_files) offers a good parallelization that counteracts this problem, but you have to compile most of your files in this function for this parallelization to have an effect. The worse thing you can do is loop over each one of your file and call this function for one file at a time.


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

See more examples [here](./examples.md).

## [Documentation](./documentation.md#documentation)

Read the documentation [here](./documentation.md#documentation).

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

You can add the `-ffuzzer` argument to your compiler and your linker with [config.add_c_cpp_flags](./documentation.md#add_c_cpp_flags) and [config.add_ld_flags](./documentation.md#add_ld_flags).

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
> PowerMake tries its best to generate a valid Makefile, however, because of the [PowerMake philosophy](#philosophy), PowerMake can't know exactly what you are doing in your Makefile, every function that is not provided by PowerMake can't be translated in the Makefile.  
> To get a good Makefile, you should never use the `subprocess` module but instead use [powermake.run_command](./documentation.md#powermakerun_command) or [powermake.run_command_if_needed](./documentation.md#powermakerun_command_if_needed).
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