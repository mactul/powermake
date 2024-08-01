# Examples

- [Examples](#examples)
  - [General Notes](#general-notes)
  - [Simple C/C++ program without dependencies](#simple-cc-program-without-dependencies)
  - [C/C++ program with compilation arguments](#cc-program-with-compilation-arguments)
  - [C/C++ static library](#cc-static-library)
  - [C/C++ shared library](#cc-shared-library)


## General Notes

**Warning !** PowerMake calculate all paths from his own location, not the location where it is run.  
For example, `python ./folder/makefile.py` will do the same as `cd ./folder && python ./makefile.py`

**Note:** In this documentation, we often assume that your makefile is named `makefile.py`, it makes thing easier to explain. Of course, you can name your makefile the name you like the most.

## Simple C/C++ program without dependencies

```py
import powermake


def on_build(config: powermake.Config):

    # Get a set of all .c and .cpp files
    # Search recursively into subfolders.
    files = powermake.get_files("**/*.c", "**/*.cpp")

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
    config.add_c_cpp_flags("-Wall", "-Wextra", "-fanalyzer", "-O3")

    config.add_shared_libs("mariadb")

    # These flags are not translated for the moment but this will arrive soon
    config.add_ld_flags("-static")

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

    config.add_c_cpp_flags("-Wall", "-Wextra", "-fanalyzer", "-O3")

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

    config.add_c_cpp_flags("-Wall", "-Wextra", "-fanalyzer", "-O3")

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