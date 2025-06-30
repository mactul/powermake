# Multiple Targets

### [<- Previous tutorial (Crossplatform Library)](../02-crossplatform-library/README.md)

> [!IMPORTANT]  
> This tutorial assumes that you have followed at least the first one: [First Powermake](../01-first-powermake/README.md)


If you have ever made a GNU Makefile, you may be used to create Makefiles with numerous different targets.  
For example a target to compile a lib in static mode, one to compile in shared mode, a target to generate the docs, etc...

With PowerMake, you need to handle your targets differently.

You must differentiate two types of targets.
- The ones that don't have anything related to the others
- The ones that share or depends on the main makefile

For the former, the answer is easy, don't fear to make multiple makefiles. beaucoup you don't need to name your makefile `makefile.py` you can easily have `generate_docs.py`, `generate_tests.py`, etc...

For the latter, you should use custom command line arguments.

Unfortunately, custom command line arguments are a little bit advanced and they require a little bit of practice.

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
parser.add_argument("--hello", description="some random argument", action="store_true")

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

Here we parse the command line, put every parsed arg in a Namespace and `exit(1)` if their is an error.

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

And finally, we can call `powermake.run` with the Namespace of parsed args.