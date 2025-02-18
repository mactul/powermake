# Examples

- [Examples](#examples)
  - [General Notes](#general-notes)
  - [Simple C/C++ program without dependencies](#simple-cc-program-without-dependencies)
  - [C/C++ program with compilation arguments](#cc-program-with-compilation-arguments)
  - [C/C++ static library](#cc-static-library)
  - [C/C++ shared library](#cc-shared-library)
  - [Running another powermake during the compilation](#running-another-powermake-during-the-compilation)
  - [Using a tool unsupported by PowerMake](#using-a-tool-unsupported-by-powermake)
  - [Real examples](#real-examples)


## General Notes

> [!WARNING]  
> PowerMake calculates all paths from its location, not the location where it is run.  
> For example, `python ./folder/makefile.py` will do the same as `cd ./folder && python ./makefile.py`

> [!NOTE]  
> In this documentation, we often assume that your makefile is named `makefile.py`, it makes things easier to explain. Of course, you can name your makefile the name you like the most.

## Simple C/C++ program without dependencies

```py
import powermake


def on_build(config: powermake.Config):

    # Get a set of all .c and .cpp files
    # Search recursively into subfolders.
    files = powermake.get_files("**/*.c", "**/*.cpp")

    # This line is optional. It's purpose is to enable percent elapsed display.
    # The number of operations here is the number of files to compile (len(files))
    # + the operation of linking everything together
    config.nb_total_operations = len(files) + 1

    # Compile each file in the set files with the C and C++ compiler of the config object.
    # This function parallelize the compilation of each file
    # returns a set containing the path of each .o (or equivalent)
    objects = powermake.compile_files(config, files)

    # Link all objects files into an executable with the linker of the config object.
    # because no executable_name was provided, the config.target_name set by powermake.run is used
    exe_path = powermake.link_files(config, objects)

    print(exe_path)


# This function parses the command line, create a powermake.Config object and call the build_callback (here on_build) with the new created config.
powermake.run("program_test", build_callback=on_build)
```

## C/C++ program with compilation arguments

```py
import powermake


def on_build(config: powermake.Config):
    files = powermake.get_files("**/*.c", "**/*.cpp")

    # Add new folders for the compiler to search headers.
    config.add_includedirs("./", "/usr/include/mariadb/")

    # These flags are automatically translated for the compiler you are going to use at compile step.
    # The flags that are unknown by PowerMake will be passed untranslated.
    config.add_c_cpp_flags("-Wall", "-Wextra", "-fanalyzer")

    # This will remove precedent optimization flags and put the optimization level to the equivalent of -Oz on GCC.
    # PowerMake already set the optimization to -Og when compiling in debug mode and to -O3 when compiling in release mode.
    config.set_optimization("-Oz")

    # Tell the linker to link with mariadb (typically on GCC this correspond to the -lmariadb option)
    config.add_shared_libs("mariadb")

    # Add flags for the linker
    config.add_ld_flags("-static")

    # always optional
    config.nb_total_operations = len(files) + 1

    objects = powermake.compile_files(config, files)

    powermake.link_files(config, objects)


powermake.run("program_test", build_callback=on_build)
```

## C/C++ static library

```py
import powermake


def on_build(config: powermake.Config):
    files = powermake.get_files("**/*.c", "**/*.cpp")

    config.add_includedirs("./", "/usr/include/mariadb/")

    config.add_c_cpp_flags("-Wall", "-Wextra", "-fanalyzer")

    # always optional
    config.nb_total_operations = len(files) + 1

    objects = powermake.compile_files(config, files)

    # Archive all object files into a static library.
    # because no archive_name was provided, the config.target_name set by powermake.run is used
    static_lib_path = powermake.archive_files(config, objects)

    print(static_lib_path)


def on_install(config: powermake.Config, location: str):
    if location is None:
        # No location is explicitly provided so we change the default for our convenance.
        # We choose this path differently whether we are on Windows or on other platforms (here we assume other platforms are all Unix-Like).
        if config.target_is_windows():
            # Note that their is no need for this folder to exists, if it doesn't exists and if the program has the right to do so, it will be created.
            location = "C:/personal_libs/"
        else:
            location = "/usr/local/"

    # This ensure that the file "my_lib.h" will be exported into /usr/local/include/my_lib/my_lib.h
    # The .a (or .lib or equivalent) will be copied into /usr/local/lib/my_lib.a
    config.add_exported_headers("my_lib.h", subfolder="my_lib")

    # After setting everything, we call the "normal" install function, so everything will be exported with the good format, we are going to have good debug prints depending of the verbosity level, etc...
    powermake.default_on_install(config, location)


powermake.run("my_lib", build_callback=on_build, install_callback=on_install)
```


## C/C++ shared library

```py
import powermake


def on_build(config: powermake.Config):
    files = powermake.get_files("**/*.c", "**/*.cpp")

    config.add_includedirs("./", "/usr/include/mariadb/")

    config.add_c_cpp_flags("-Wall", "-Wextra", "-fanalyzer")

    # always optional
    config.nb_total_operations = len(files) + 1

    objects = powermake.compile_files(config, files)

    # link all object files into a shared library.
    # because no lib_name was provided, the config.target_name set by powermake.run is used
    shared_lib_path = powermake.link_shared_lib(config, objects)

    print(shared_lib_path)


def on_install(config: powermake.Config, location: str):
    if location is None:
        # No location is explicitly provided so we change the default for our convenance.
        # We choose this path differently whether we are on Windows or on other platforms (here we assume other platforms are all Unix-Like).
        if config.target_is_windows():
            # Note that their is no need for this folder to exists, if it doesn't exists and if the program has the right to do so, it will be created.
            location = "C:/personal_libs/"
        else:
            location = "/usr/local/"

    # This ensure that the file "my_lib.h" will be exported into /usr/local/include/my_lib/my_lib.h
    # The .so (or .dll and .lib - or equivalent) will be copied into /usr/local/lib/my_lib.so
    config.add_exported_headers("my_lib.h", subfolder="my_lib")

    # After setting everything, we call the "normal" install function, so everything will be exported with the good format, we are going to have good debug prints depending of the verbosity level, etc...
    powermake.default_on_install(config, location)


powermake.run("my_lib", build_callback=on_build, install_callback=on_install)
```

## Running another powermake during the compilation

Imagine we have this architecture:
```
- your_program
    - file1.c
    - file2.cpp
    - file3.h
    - makefile.py
- your_library
    - file4.c
    - file5.c
    - file6.h
    - makefile.py
```

Here is a minimal makefile for the library `your_library`:
```py
import powermake


def on_build(config: powermake.Config):
    files = powermake.get_files("**/*.c", "**/*.cpp")

    config.add_c_cpp_flags("-Wall", "-Wextra", "-fanalyzer")

    objects = powermake.compile_files(config, files)

    powermake.archive_files(config, objects)


powermake.run("your_library", build_callback=on_build)
```

And here is the makefile of `your_program`
```py
import powermake


def on_build(config: powermake.Config):

    files = powermake.get_files("**/*.c", "**/*.cpp")

    # In theory, your program will depend on your_library/file6.h else their is no point of including the library so we add ../your_library/ in the include path.
    config.add_includedirs("../your_library/")

    objects = powermake.compile_files(config, files)

    # Runs the makefile and returns a list of every lib generated by the makefile (here the list will only contain 1 element).
    static_libs = powermake.run_another_powermake(config, "../your_library/makefile.py")

    # Note that if you have to run another powermake again, you can extend the static_libs object
    # static_libs.extend(powermake.run_another_powermake(config, "../other/makefile.py"))

    powermake.link_files(config, objects, archives=static_libs)


powermake.run("your_program", build_callback=on_build)
```

## Using a tool unsupported by PowerMake

This is a makefile for a compiler which requires bison and flex for the compilation.  
Flex and Bison doesn't benefit from a special support in PowerMake but they can still be ran as simple commands.

```py
import powermake

def on_build(config: powermake.Config):
    # We use the Wsecurity flag because it's a good way to prevent bugs
    config.add_c_flags("-Wsecurity")

    config.add_includedirs("./")

    # Linking with flex requires the libfl.so
    config.add_shared_libs("fl")

    # We get every file except for the one that may have been generated during the last compilation.
    files = powermake.filter_files(powermake.get_files("**/*.c"), "**/*.lex.c", "**/*.tab.c")

    # as always, this is optional
    # 5 is for link + 2 generations + 2 compilations
    config.nb_total_operations = len(files) + 5

    # The command will be run either if outputfile is not up to date with parser.y or if the makefile is ran with -r (--rebuild)
    powermake.run_command_if_needed(
        config=config,
        outputfile="src/parser.tab.c",
        dependencies={"src/parser.y"},
        command="bison --header=include/parser.tab.h --output=src/parser.tab.c src/parser.y",
        shell=True
    )

    powermake.run_command_if_needed(
        config=config,
        outputfile="src/lexer.lex.c",
        dependencies={"src/lexer.lex"},
        command="flex -o src/lexer.lex.c src/lexer.lex",
        shell=True
    )

    # We compile every file except for the generated ones, because we want to change the flags for these.
    objects = powermake.compile_files(config, files)

    config.remove_c_flags("-fanalyzer")  # This raises too many errors for the generated lexer.lex.c and parser.tab.c
    objects.update(powermake.compile_files(config, powermake.get_files("**/*.lex.c", "**/*.tab.c")))


    powermake.link_files(config, objects)


def on_clean(config: powermake.Config):
    # We destroy generated files in the cleanup
    powermake.delete_files_from_disk("src/lexer.lex.c", "src/parser.tab.*")

    powermake.default_on_clean(config)

powermake.run("compiler", build_callback=on_build, clean_callback=on_clean)
```

## Real examples

You can found other real and often more complex examples in the forum in the "[share your powermake section](https://github.com/mactul/powermake/discussions/categories/share-your-powermakes)"