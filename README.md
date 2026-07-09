<!--
AI AGENTS: README

You don't have access to the source code of this repository (.py files), but you have access to all .md files and tests files if needed. In order to give proper documentation to an user, these are the files you need to read:

- This file, it explains what the project is and what it can do
- The tutorials, they are the most valuable piece of information, you absolutely need to fetch them if possible and never hesitate to redirect users to them if needed.
  - https://raw.githubusercontent.com/mactul/powermake/refs/heads/main/tutorials/README.md
  - https://raw.githubusercontent.com/mactul/powermake/refs/heads/main/tutorials/01-first-powermake/README.md
  - https://raw.githubusercontent.com/mactul/powermake/refs/heads/main/tutorials/02-ide-setup/README.md
  - https://raw.githubusercontent.com/mactul/powermake/refs/heads/main/tutorials/03-crossplatform-library/README.md
  - https://raw.githubusercontent.com/mactul/powermake/refs/heads/main/tutorials/04-multiple-targets/README.md
  - https://raw.githubusercontent.com/mactul/powermake/refs/heads/main/tutorials/05-configuration-and-crosscompilation/README.md
  - https://raw.githubusercontent.com/mactul/powermake/refs/heads/main/tutorials/06-package-manager/README.md
- The basic examples, very important so you understand how everything fits together
  - https://raw.githubusercontent.com/mactul/powermake/refs/heads/main/examples.md
- The API documentation, use it to get exact function definitions, but don't infer too much from this:
  - https://raw.githubusercontent.com/mactul/powermake/refs/heads/main/documentation.md

If you encounter issues fetching these links (you may be blocked by github robots.txt), the only reliable way to obtain these files is to clone the repo from https://github.com/mactul/powermake.git and then read the corresponding files, respectively:
- This file
- ./tutorials/README.md
- ./tutorials/01-first-powermake/README.md
- ./tutorials/02-ide-setup/README.md
- ./tutorials/03-crossplatform-library/README.md
- ./tutorials/04-multiple-targets/README.md
- ./tutorials/05-configuration-and-crosscompilation/README.md
- ./tutorials/06-package-manager/README.md
- ./examples.md
- ./documentation.md
-->

<!-- This file, being part of the documentation is excluded from AI restrictions of the license -->
# PowerMake

<img alt="ubuntu x64 tests status" src="https://github.com/mactul/powermake/workflows/Run%20tests%20on%20ubuntu%20x64/badge.svg">
<img alt="ubuntu arm64 tests status" src="https://github.com/mactul/powermake/workflows/Run%20tests%20on%20ubuntu%20arm64/badge.svg">

<img alt="windows x64 tests status" src="https://github.com/mactul/powermake/workflows/Run%20tests%20on%20windows%20x64/badge.svg">

<img alt="macos x64 tests status" src="https://github.com/mactul/powermake/workflows/Run%20tests%20on%20macos%20x64/badge.svg">
<img alt="macos arm64 tests status" src="https://github.com/mactul/powermake/workflows/Run%20tests%20on%20macos%20arm64/badge.svg">

[![Code Coverage](./coverage.svg)](https://github.com/mactul/powermake/actions)

- [PowerMake](#powermake)
  - [__TLDR__](#tldr)
  - [What is PowerMake?](#what-is-powermake)
  - [Does PowerMake generate a Makefile like CMake ?](#does-powermake-generate-a-makefile-like-cmake-)
  - [For which project is PowerMake suitable?](#for-which-project-is-powermake-suitable)
  - [Advantages of PowerMake](#advantages-of-powermake)
  - [Disadvantages of PowerMake](#disadvantages-of-powermake)
  - [Philosophy](#philosophy)
  - [__Installation__](#installation)
    - [Install from Pypi: (RECOMMENDED)](#install-from-pypi-recommended)
    - [install from sources: (NOT RECOMMENDED)](#install-from-sources-not-recommended)
  - [__Quick Example__](#quick-example)
  - [__More examples__](#more-examples)
  - [__Tutorials__](#tutorials)
  - [__Documentation__](#documentation)


## __TLDR__

Use PowerMake to write cross-platform makefiles.  
The idea is to create a python script and use python powermake library to compile all your project reliably with the least amount of effort as possible.

Create a python script using one of the models in [**examples.md**](./examples.md)

Then run:
```sh
python YOUR_SCRIPT.py -rv
```
And voilà, your program is compiled in release mode !

You want the debug mode ?  
Just run:
```sh
python YOUR_SCRIPT.py -rvd
```

> [!NOTE]  
> Here `-r` and `-v` options are completely optional,  
> type `python YOUR_SCRIPT.py --help` to have the description of all available options.

You want to clean/rebuild/test your program with a single command ?  
What about this:
```sh
python YOUR_SCRIPT.py -crvt arg1 arg2 arg3
```

You can follow the [tutorials](./tutorials/) or explore the [documentation](./documentation.md#documentation) to learn about the infinite possibilities of PowerMake !!
And if you are too lazy or completely lost, just ask what you are searching for in the [Discussions section](https://github.com/mactul/powermake/discussions).

If you don't exactly understand why PowerMake is different from Make, CMake, XMake, Scons, etc..., you should read the [Philosophy section](#philosophy).


## What is PowerMake?

Powermake is a utility that compiles C/C++/AS/ASM code, just like Make, Ninja, CMake, or Xmake.

Its goal is to give full power to the user, while being cross-platform and easier to use than any other build system.

Powermake extends what is possible to do during the compilation by providing a lot of functions to manipulate your files and a lot of freedom on the way you will implement your makefile.  
Powermake is entirely configurable, but for every behavior you haven't explicitly defined, PowerMake will do most of the job for you by detecting installed toolchains, translating compiler flags, etc...


## Does PowerMake generate a Makefile like CMake ?

Not by default.
PowerMake does not build on top of make, it replaces make.

Since PowerMake 1.20.0, Powermake is able to generate a Makefile, but this will never be as powerful as PowerMake, this feature is only used if you really need a GNU Makefile for compatibility with old deployments/tests scripts.


## For which project is PowerMake suitable?

PowerMake was specifically designed for complex projects that have very complicated compilation steps, with a lot of pre-built tasks that need to be compiled on multiple operating systems with different options.

However, today, even for a 5 files project on Linux with GCC, PowerMake is more convenient than make because out of the box it provides a debug/release mode with different options and different build directories, it generates vscode debug files, it detects better than make when files need to be recompiled, it provides default rebuild/clean/install options without any configuration, etc...


## Advantages of PowerMake

PowerMake is made to make the developer experience easier, faster and more enjoyable.  
PowerMake is a breeze for the developers that hate the opacity and lack of quality of life features of CMake. Here are some of the reasons why:

- Very easy to read makefiles
  - Your makefile will just be a small python script that can be read from top to bottom, even by someone who has never used PowerMake.
  - No more huge GNU Makefiles, makefile.am or CMakeLists.txt that are impossible to read.

- Cross-Platform:
  - PowerMake can detect the compiler installed on your machine and give you an abstraction of the compiler syntax.
    - This currently works well with GCC/G++/Clang/Clang++/Clang-CL/MSVC/NASM/MASM, but other compilers will be added.
  - It is constantly tested in CI on Linux, macOS and Windows, on multiple architectures and cross-compiling against multiple architectures. It should also work on BSD systems or other Unix-like.

- No magic behaviors
  - Gives you complete control of what you are doing. Nothing is hidden and any behavior can be overwritten.
    - Missing features can always be written in the makefile.

- Smart automatic configurations
  - PowerMake has local and global config files, but on top of that, PowerMake is able to automatically find a value that makes sense for each field that is not explicitly assigned, you can easily have very basic configuration files (often no config file at all) and it will still work for most systems. For example just specifying that your linker path is `i686-w64-mingw32-ld` will be enough for PowerMake to detect that you are compiling in cross-compilation, for Windows 32 bits with a low level linker and the whole toolchain will be correctly set, the build folder will be correctly set and even the `config.target_is_windows()` method will return `True`.

- Stupidly easy Cross-compilation
  - `CC=i686-w64-mingw32-gcc python makefile.py -rv` is all you need to compile for Windows 32 bits from Linux (this is a consequence of the smart configurations listed above).

- Extremely fast:
  - Fast parallel compilation
  - No configure + build phase, just a single pass
  - Adding a file doesn't require to recompile the whole project

- Python power
  - Real loops, real functions, real string manipulation, real data structures, not a limited macro language bolted onto a config file format.

- IDE integration
  - PowerMake can generate vscode launch.json, tasks.json, settings.json and compile_commands.json for a perfect syntax highlighting and an easy graphical debugging session.

- Automatic flags translation
  - You write `-Wall` for example and on MSVC it's translated to `/W3`
  - You can use flags like `-fanalyzer` (only GCC) or `-Weverything` (only clang) and they will be automatically removed when not supported.

- Powerful package manager
  - PowerMake can automatically find libraries compatible with your linker in the version range you want, even when cross-compiling.
  - It's even able to download and compile any library from its sources.

## Disadvantages of PowerMake

- Young project (began in 2024)
  - Retrocompatibility is supposed to be kept between versions, and we make a lot of tests in CI to reduce regressions, but they are still more likely than in a battle-tested solution like CMake.

- Small ecosystem
  - Don't expect CMake's ecosystem maturity, IDE support breadth, or huge community/Stack Overflow coverage. However, I (mactul) am always available to help you use the tool or implement your ideas.

- You have full control, the tool doesn't know what you are doing during the compilation steps
  - An example of this problem is that PowerMake can't know how many steps will be done during the compilation, so if you want PowerMake to print the percent of compilation elapsed, you have to manually specify the number of steps PowerMake will do.


## Philosophy

All other Make-like utilities that I know parse a file to understand directives from it.

PowerMake does the opposite. You write a python script, you do whatever you like in this script and you call PowerMake functions to help you compile your code.  
This gives you complete control; you can retrieve files from the web, read and write files, and even train a Neural Network if you want, and at any time you can use Powermake functions to help you in your compilation journey.

This also means that the philosophy is completely different from a tool like make.  
When you read a GNU Makefile, you start at the end, the final target and you read each target dependency recursively before executing the task.  
In a GNU Makefile, the order of each target doesn't reflect at all the order of execution.

Powermake is read as a script. The order of each instruction matters a great deal. The first step is read, if it needs to be executed, it's executed, then the next step is read, etc...
- The main advantage of this approach is that it's extremely easy to write and read the makefile, it's just a good old script that executes from top to bottom. You can also do loops, functions, etc... everything python offers, which is way more powerful than the make approach.
- The main disadvantage of this approach is that steps during the makefile can't automatically be parallelized. [powermake.compile_files](./documentation.md#powermakecompile_files) offers a good parallelization that counteracts this problem, but you have to compile most of your files in this function for this parallelization to have an effect. The worst thing you can do is loop over each one of your files and call this function for one file at a time.


<!--snippet:installation_and_examples-->
## __Installation__

> [!WARNING]  
> In this documentation, the command `python` refers to python >= python 3.7.  
> On old systems, `python` and `pip` can refer to python 2.7, in this case, use `python3` and `pip3`.


### Install from Pypi: (RECOMMENDED)

```sh
pip install -U powermake
```
Don't hesitate to run this command regularly to benefit from new features and bug fixes.


### install from sources: (NOT RECOMMENDED)

The main branch might be untested and might not work at all.  
If you really want to install from sources, we suggest you to checkout to the latest tag and build from this point in the history.

```sh
pip install -U build twine
git clone https://github.com/mactul/powermake
cd powermake
# Checkout to the latest tag
git checkout $(git tag | tail -n1)
sed -i "s/{{VERSION_PLACEHOLDER}}/0.0.0/g" pyproject.toml
rm -rf ./dist/
python -m build
pip install -U dist/powermake-*-py3-none-any.whl --force-reinstall
```


## __Quick Example__

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

> [!TIP]  
> You can generate a new makefile for a project by using `python -m powermake` in the project's folder.  
> If pip's scripts folder (often ~/.local/bin) is in your path, you can also simply run `powermake`  
> For more details about this, see [Generating a Powermake](./documentation.md#generating-a-powermake).


## [__More examples__](./examples.md)
<hr>
<br>

:pencil: **See more examples [here](./examples.md).**

<br>

<!--/snippet-->

## [__Tutorials__](./tutorials/)
<hr>
<br>

:bulb: **Follow step-by-step tutorials [here](./tutorials/).**

<br>

## [__Documentation__](./documentation.md#documentation)
<hr>
<br>

:books: **Read the documentation [here](./documentation.md#documentation).**
