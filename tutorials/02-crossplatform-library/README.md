# Crossplatform Library

### [<- Previous tutorial (First PowerMake)](../01-first-powermake/README.md)

> [!IMPORTANT]  
> This tutorial assumes that you have followed the first one: [First Powermake](../01-first-powermake/README.md)

In this tutorial, we are going to create 2 minuscule projects, a mini-library and a mini program depending on this library.

## Architecture

```
- tutorial2
  - library
    - include
      - my_time.h
    - src
      - time_linux.c
      - time_windows.c
    - makefile.py
  - program
    - src
      - main.c
    - makefile.py
```

Here is the content of each file:

my_time.h
```c
#ifndef MY_TIME_H
#define MY_TIME_H

void my_sleep(unsigned int ms);

#endif
```

time_linux.c
```c
#include <unistd.h>
#include "my_time.h"


void my_sleep(unsigned int ms)
{
    usleep(1000 * ms);
}
```

time_windows.h
```c
#include <windows.h>
#include "my_time.h"

void my_sleep(unsigned int ms)
{
    Sleep(ms);
}
```

main.c
```c
#include <stdio.h>
#include "my_time.h"

int main()
{
    puts("entering 2 seconds sleep");
    my_sleep(2000);
    puts("Waking up from 2 seconds sleep");

    return 0;
}
```

For the makefile.py files, you can start by generating them with the `powermake` command like in the previous tutorial.


## Library makefile

For this library we have 2 new challenges.
- It's a library, we will not be able to use the normal link operation.
- We will have to compile different files depending on the platform.

Let's first address the second issue.

Later, we would do `files = powermake.get_files("**/*.c")`, but here, we must have a condition.  
Something like this:
```py
if config.target_is_windows():
    files = powermake.get_files("src/*windows.c")
else:
    files = powermake.get_files("src/*linux.c")
```

This would work, because we don't have common files between windows and Linux.
But what if we had 100 common files and just some `*windows.c` and some `*linux.c` to separate ?

The best approach is to get all files, then remove the files that we don't want.
```py
files = powermake.get_files("**/*.c")
if config.target_is_windows():
    files = powermake.filter_files(files, "**/*linux.c")
else:
    files = powermake.filter_files(files, "**/*windows.c")
```

And voilà ! Our makefile will now automatically pick the good files to compile, as long as we keep the naming convention !

> [!NOTE]  
> You may be wondering if it's possible to test `config.target_is_linux()`, of course it's possible, but here we should not because usleep will also work under MacOS, FreeBSD, Android, etc... Maybe we should have called our file `time_unix.c`, but whatever...


It's now time to address the link issue !  
The link operation will change if we want a shared library or a static library.  
For the moment, let assume we want a static library.

We just have to replace:
```py
powermake.link_files(config, objects)
```
By:
```py
powermake.archive_files(config, objects)
```

So our final makefile for the library looks like this:
```py
import powermake

def on_build(config: powermake.Config):
    config.add_flags("-Wall", "-Wextra")

    config.add_includedirs("./include/")

    files = powermake.get_files("**/*.c")
    if config.target_is_windows():
        files = powermake.filter_files(files, "**/*linux.c")
    else:
        files = powermake.filter_files(files, "**/*windows.c")

    objects = powermake.compile_files(config, files)

    powermake.archive_files(config, objects)

powermake.run("my_time", build_callback=on_build)
```

You can see that we added `config.add_includedirs("./include/")`, that is required for `time_linux.c` and `time_windows.c` to found the `my_time.h` file.

In the last chapter we haven't talked about the first parameter of `powermake.run`, here it's `"my_time"`.  
This parameter is the name of the project and it is used for link operations to automatically give a name to the binary.  
For example here, we haven't specified the output name for `powermake.archive_files` (yes it's possible to do so, we will see later), so the name will be automatically attributed and will be `libmy_time.a`

Try to run:
```sh
python makefile.py -rv
```
In the `library` subfolder and see that a file named `libmy_time.a` is generated under `build/Linux/x64/release/lib/libmy_time.a`


## Program makefile

This program is close to the one made in the previous chapter, with two differences:
- We will need a way to automatically trigger the library makefile so we will not have to run it by hand each time
- We will need to link with a set of objects AND a static library

Triggering the other makefile is relatively easy thanks to `powermake.run_another_powermake`

```py
libraries = powermake.run_another_powermake(config, "../library/makefile.py")
```
libraries will be a list of the generated libs by `"../library/makefile.py"` (here just `libmy_time.a`)


And linking with objects AND static libraries is also easy using the `archives` parameter of `powermake.link_files`

In the end we have something like this:
```py
import powermake

def on_build(config: powermake.Config):
    config.add_flags("-Wall", "-Wextra")

    config.add_includedirs("../library/include/")

    files = powermake.get_files("**/*.c")

    objects = powermake.compile_files(config, files)

    archives = powermake.run_another_powermake(config, "../library/makefile.py")

    powermake.link_files(config, objects, archives=archives)

powermake.run("program", build_callback=on_build)
```

Run `python makefile.py -rvt` in the `program` subfolder.
You can see that `../library/makefile.py` is indeed called and the final program should work as expected.


## Making a shared lib

If you want to switch to a shared lib, you just need to change the library side, replacing `powermake.archive_files` by `powermake.link_shared_lib`, with the same parameters.
```py
powermake.link_shared_lib(config, objects)
```

### Installing your shared lib

If you do nothing, when you will try to run:
```sh
python makefile.py -rvd --install
```
in the library directory, an `install` folder will be created, with a subfolder `lib` containing your shared library.

However, you may want to add an `include/` folder in this install directory and probably change the default install location.

Here, exporting the `include/` folder would be easy because we already have separated the headers and the sources, but PowerMake can export public headers even if they are mixed with sources, we just have to specify which header need to be exported.

We do that by overwriting the install callback

```py
import powermake

def on_build(config: powermake.Config):
    config.add_flags("-Wall", "-Wextra")

    config.add_includedirs("./include/")

    files = powermake.get_files("**/*.c")
    if config.target_is_windows():
        files = powermake.filter_files(files, "**/*linux.c")
    else:
        files = powermake.filter_files(files, "**/*windows.c")

    objects = powermake.compile_files(config, files)

    powermake.archive_files(config, objects)


def on_install(config: powermake.Config, location: str):
    if location is None:
        # No location is explicitly provided so we change the default for our convenance.
        location = "/usr/local/"

    # This ensure that the file "my_time.h" will be exported into /usr/local/include/my_time/my_time.h
    # The .so will be copied into /usr/local/lib/my_time.so
    config.add_exported_headers("my_time.h", subfolder="my_time")

    # After setting everything, we call the "normal" install function, so everything will be exported with the good format, we are going to have good debug prints depending of the verbosity level, etc...
    powermake.default_on_install(config, location)

# Make sure you register the on_install callback in powermake.run
powermake.run("my_time", build_callback=on_build, install_callback=on_install)
```


Once your lib is installed under `/usr/local/lib` and `/usr/local/include/my_time/`, you can create a program using it like this:

Assuming that /usr/local/lib/ is not in the LD_LIBRARY_PATH:
```py
import powermake

def on_build(config: powermake.Config):
    config.add_flags("-Wall", "-Wextra", "-L/usr/local/lib/")

    config.add_includedirs("/usr/local/include/my_time/")

    config.add_shared_libs("my_time")

    files = powermake.get_files("**/*.c")

    objects = powermake.compile_files(config, files)

    powermake.link_files(config, objects)

powermake.run("program", build_callback=on_build)
```


And to run the program:

```sh
LD_LIBRARY_PATH=/usr/local/lib python makefile.py -t
```

### [-> Next tutorial (Multiple Targets)](../03-multiple-targets/README.md)