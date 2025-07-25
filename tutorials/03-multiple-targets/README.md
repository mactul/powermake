# Multiple Targets

### [<- Previous tutorial (Cross-platform Library)](../02-crossplatform-library/README.md)

> [!IMPORTANT]  
> This tutorial assumes that you have followed at least the first one: [First PowerMake](../01-first-powermake/README.md)


If you have ever made a GNU Makefile, you may be used to create makefiles with numerous targets.  
For example a target to compile a lib in static mode, one to compile in shared mode, a target to generate the docs, etc...

With PowerMake, you need to handle your targets differently.

You must differentiate two types of targets.
- The ones that don't have anything related to the others
- The ones that share or depends on the main makefile

For the former, the answer is easy, don't fear to make multiple makefiles. Because you don't need to name your makefile `makefile.py` you can easily have `generate_docs.py`, `generate_tests.py`, etc...

For the latter, you should use custom command line arguments.

Unfortunately, custom command line arguments are a little advanced and they require a little practice.

## Custom Command Line Arguments

To create a custom command line argument, you will need to use the class `powermake.ArgumentParser`.  
This class is a superset of [argparse.ArgumentParser](https://docs.python.org/3/library/argparse.html).
Basically, it's just an `argparse.ArgumentParser` but with all the powermake commands already set.

> [!CAUTION]  
> Never use `argparse.ArgumentParser` directly, you will lose all the powermake normal command line arguments and PowerMake rely on that to function properly.

> [!TIP]  
> If you need specific details, you can look at the [argparse documentation](https://docs.python.org/3/library/argparse.html), here we will show some examples.


Let's see an example that we are going to analyze:
```py
import powermake

argument_hello_enabled: bool = False


def on_build(config: powermake.Config):
    if argument_hello_enabled:
        print("--hello was found on command line")
    else:
        print("--hello was not found on command line")


parser = powermake.ArgumentParser()
parser.add_argument("--hello", help="some random argument", action="store_true")

args_parsed = parser.parse_args()

if args_parsed.hello:
    argument_hello_enabled = True

powermake.run("my_project", build_callback=on_build, args_parsed=args_parsed)
```

A lot is happening here.

```py
parser = powermake.ArgumentParser()
```
Here we are creating the parser object, that contains all PowerMake commands already registered.

```py
parser.add_argument("--hello", description="some random argument", action="store_true")
```
We add a new argument named `--hello`, because we put `action="store_true"`, this argument will be a boolean, `True` if the flag is on the command line, else `False`.

```py
args_parsed = parser.parse_args()
```

Here we parse the command line, put every parsed arg in a Namespace and `exit(1)` if there is an error.

At this time it might be a good idea to `print(args_parsed)` to see what does this object look like.

> [!IMPORTANT]  
> if your arg contains dashes (-), like `--foo-bar` for example, the Namespace will contain a member called `foo_bar`.

```py
if args_parsed.hello:
    argument_hello_enabled = True
```
Here we just store the result in a global variable.

```py
powermake.run("my_project", build_callback=on_build, args_parsed=args_parsed)
```

And finally, we can call `powermake.run` with the Namespace of parsed arguments.


Most of the time you will need to use boolean arguments (with `action="store_true"`).  
Obviously you can also have different type of arguments.  
You can't really have positional arguments because those are already all used by PowerMake for the test callback, but you can do almost anything you want with named arguments.

> [!TIP]  
> Avoid using single letter arguments for future-proof makefiles because you have a high risk to have a conflict with a future version of PowerMake.  
> To be perfectly future-proof, a good practice might be to prefix each of your argument with a name of your own. For example if the program you're compiling is called zorglub, a custom argument might be `--zb-enable-something`.


If you want to know everything you can do with the command line, please refer to the [argparse documentation](https://docs.python.org/3/library/argparse.html); however this documentation might not be very easy to read so here are some common examples:


```py
import powermake

parser = powermake.ArgumentParser()

# A boolean argument
parser.add_argument("--zb-version", help="display Zorglub version", action="store_true")

# An optional argument with constraints
# Will be "disabled" if --zb-enable-gui is not on the command line, None if there is just `--zb-enable-gui` without any argument, "SDL2" if the command line is `--zb-enable-gui=SDL2` or "QT" if the command line is `--zb-enable-gui QT`
parser.add_argument("--zb-enable-gui", nargs='?', help="enable the GUI, optionally specify which GUI frontend to use" choices=["SDL2", "SDL3", "QT", "GTK"], default="disabled")

# The same as above but this time it can either not be on the command line or have a value but it cannot be on the command line and empty.
parser.add_argument("--zb-set-gui", help="set the GUI to use if you want one", choices=["SDL2", "SDL3", "QT", "GTK"], default=None)

# An argument with a non-constrained value but which must be on the command line.
parser.add_argument("--zb-exec-name", metavar="NAME", help="set the name of the executable", required=True)

# An integer, that will be automatically converted.
parser.add_argument("--zb-buff-size", help="set the default buffer size zorglub will use.", default=0, type=int)

# A list of undefined size
parser.add_argument("--zb-enable-search-paths", nargs='*', help="Enable search paths, specify every search paths zorglub should use")

# A list that can have one or more items
parser.add_argument("--zb-search-paths", nargs='+', help="Specify every search paths zorglub should use")

# A list with exactly 3 integers
parser.add_argument("--zb-color-rgb", nargs=3, help="specify the zorglub main color as 3 int values between 0 and 255", type=int)


args_parsed = parser.parse_args()

print(args_parsed)
```

## Specifying executables/libraries names

Using custom command line arguments you can easily conditionally compile different pieces of code.
However, this doesn't serve a ton of purpose if you can only link files with the name specified in `powermake.run`.

Hopefully, `powermake.link_files`, `powermake.archive_files` and `powermake.link_shared_lib` all have an optional argument to specify the output file name.

For example, let's compile a lib under different names if it's hardened:
```py
import powermake

my_lib_hardened: bool = False


def on_build(config: powermake.Config):
    files = powermake.get_files("**/*.c")

    if my_lib_hardened:
        config.add_flags("-fsecurity")

    objects = powermake.compile_files(config, files)

    if my_lib_hardened:
        lib_name = f"lib{config.target_name}-hardened"
    else:
        lib_name = f"lib{config.target_name}"

    powermake.archive_files(config, powermake.filter_files(objects, "**/test.*"), archive_name=lib_name)
    powermake.link_shared_lib(config, powermake.filter_files(objects, "**/test.*"), lib_name=lib_name)

    powermake.link_files(config, objects, executable_name="test_lib")


parser = powermake.ArgumentParser()
parser.add_argument("--ml-hardened", help="Harden the lib my_lib", action="store_true")
args_parsed = parser.parse_args()

if args_parsed.ml_hardened:
    my_lib_hardened = True

powermake.run("my_lib", build_callback=on_build, args_parsed=args_parsed)
```

### [-> Next tutorial (Configuration and Cross-compilation)](../04-configuration-and-crosscompilation/README.md)