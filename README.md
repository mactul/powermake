# PowerMake

## What is PowerMake ?

Powermake is an utility to compile C/C++ code, just like Make, Ninja, cmake or xmake.

His goal is to give full power to the user, while being cross-platform, easier to use than Make and faster than Ninja.

## For which project is PowerMake suitable ?

PowerMake was specifically designed for all the complex projects that have very complicated compilation steps, with a lot of pre-built tasks and which need to be compiled on multiple operating systems with different options.

## Advantages of PowerMake

- Extremely fast:
  - PowerMake is approximately 2x faster than Ninja, at least on relatively small projects
      - With a project that has 10 000 lines of C:
        - Ninja takes 1.484 seconds
        - PowerMake takes 0.649 seconds

- Cross-Platform:
  - PowerMake is able to detect the compiler installed on your machine and give you an abstraction of the compiler syntax.
    - This currently works well with GCC/G++/Clang/Clang++/MSVC, but other compilers will be add.
  - Because it's written in python it works in almost all machine and you can always write the compilation instructions for your machine and for your compiler.

- Gives you complete control of what you are doing. Nothing is hidden and any behavior can be overwritten.

## Disadvantages of PowerMake

- PowerMake is very young so it changes a lot at each version and you may have to write some features by yourself (the whole point of PowerMake is that you can write missing features).

- Because PowerMake gives you full control, the tool can't really now what's you are doing during the compilation step. For example, if we want to import dependencies from another PowerMake, the only thing we can do for you is running the PowerMake where it stands and scanning his output directory. This works well but has some limitations...

## Philosophy

All other Make-like utilities that I know parse a file to understand directives from it.

PowerMake does the opposite. You write a python script, you do whatever you like in this script and you call PowerMake functions to help you compiling your code.  
This gives you a complete control; you can retrieve files from the web, read an write files, even train a Neural Network if you want and at any time you can use Powermake functions to help you in your compilation journey.

## Installation

Documentation in coming...

## Quick Example

This example compile all `.c` and `.cpp` files that are recursively in the same folder as the python script and generate an executable named `program_test`

**Warning !** PowerMake calculate all paths from his own location, not the location where it is run.  
For example, `python ./folder/makefile.py` will do the same as `cd ./folder && python ./makefile.py`

```py
import powermake


def on_build(config: powermake.Config):

    files = powermake.get_files("**/*.c", "**/*.cpp")

    objects = powermake.compile_files(config, files)

    print(powermake.link_files(config, objects))


powermake.run("program_test", build_callback=on_build)
```

## Documentation

Documentation in coming...