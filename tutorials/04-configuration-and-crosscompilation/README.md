# Configuration and Crosscompilation

### [<- Previous tutorial (Multiple Targets)](../03-multiple-targets/README.md)

> [!IMPORTANT]  
> This tutorial assumes that you have followed at least the first one: [First Powermake](../01-first-powermake/README.md)


In this tutorial, we will learn how to use different compilers with PowerMake and how to configure cross-compilation toolchains.  
As you will see, this point is one of the strengths of PowerMake, rendering this operation extremely easy.


> [!NOTE]  
> For this tutorial, you can take the file hierarchy of the first tutorial or any other project with a working PowerMake, just make sure your C code will compile with all the different compilers you are planning to use.

## Environment variables

The quickest way to change the PowerMake compiler for a single compilation is to use the environment variables.

For example, assuming you have `clang` installed and in your path, just writing:
```sh
CC=clang python makefile.py -rv
```
Will ensure that all the compilation is done with the clang toolchain.

> [!TIP]  
> If you are using Windows (shame on you ?), you cannot set a environment variable on the same line of a command.
> To do the same thing you have to enter:
> ```bat
> SET CC=clang
> python makefile.py -rv
> SET CC=
> ```

Even if your project is in C++, if you specify `CC=clang`, with no other information, PowerMake will assume that you want clang++ to compile the C++.

Here are all the environment variables you can set.
- `CC`: The path of the C compiler
- `CXX`: The of the C++ compiler
- `AS`: The path of the assembler for .s and .S files
- `ASM` The path of the assembler for .asm files
- `RC` The path of the Windows ressources compiler
- `AR` The path of the static lib archiver
- `LD`: The path of the linker
- `SHLD`: The path of the linker used for making shared library

Most of the time, setting just a single environment variable is enough for PowerMake to understand what you want to do.  
But you can do very strange things like compiling with GCC and linking with clang
```sh
CC=gcc LD=clang++ python makefile.py -rv
```

If you specify a cross-compiler, PowerMake handle everything for you.
For example:
```sh
CC=i686-w64-mingw32-gcc python makefile.py -rv
```
PowerMake will recognize that `i686-w64-mingw32-gcc` is a compiler for compiling in 32 bits for Windows.  
Automatically, the build path will become `build/Windows/x86/release/`, the method `config.target_is_windows()` will report `True`, `config.target_simplified_architecture` will report `x86`, etc...

These environment variables are extremely handy when you want to change the compiler one time to see different warnings or to generate something for a tool.  
For example if you want to use CodeChecker, you need to generate a compile_commands.json with clang:
```sh
CC=clang python makefile.py -rvd -o .

CodeChecker analyze ./compile_commands.json --enable sensitive --ctu -o ./reports

CodeChecker parse ./reports -e html -o ./reports_html
firefox ./reports_html/index.html
```

However, sometimes you want to change the default compiler of a project, for the whole life of the project. Here comes the configuration files

## Configuration files

PowerMake have 4 stages of configuration.  
You have the global config file, the local config file, the environment variables and the overwritten config in the makefile itself.

The idea is that each configuration stage overwrite the fields of the last one.

For example, specifying that you want to compile in 32 bits with clang in the global configuration and then specifying that you want to compile in 64 bits in the local config will result in a final configuration that specify clang/64 bits.

> [!IMPORTANT]  
> As seen above, PowerMake is able to infers all unspecified fields to find a value coherent with what you specifically specified.  
> However, it will ***never*** infers a field that you have specified somewhere. For example if you specify in the global config that your C++ compiler is clang++ and then you try to compile with:
> ```sh
> CC=i686-w64-mingw32-gcc python makefile.py -rv
> ```
> You will have everything configured for the i686-w64-mingw32-* toolchain, except for the C++ compiler which will be kept as clang++

### Global configuration file

The global config file can be found at `~/.powermake/powermake_config.json` (On Windows this is `C:/Users/YOUR_USERNAME/.powermake/powermake_config.json`)

> [!WARNING]  
> You will eventually forget that you have put something in the global config and you might be wondering why PowerMake is no longer auto-configuring some values.  
> To avoid having problems, keep the global configuration as small as possible and prefer using local configurations when possible.


We could edit the global configuration by hand, but for basic configurations like we are going to do, PowerMake comes with an interactive command line utility that will help us avoid configuration mistakes.

To launch the tool just type:
```sh
powermake -f
```
You can also use the makefile instead of the powermake script
```sh
python makefile.py -f
```

Choose the one you prefer, they will do the same.

Once you are in the tool, press 3 for Toolchain configuration.  
Then press 1 to edit the C Compiler configuration.


You will have two choices, the compiler type and the compiler type.

The compiler type is here to tell PowerMake what does the compiler command line syntax looks like. For example, `i386-elf-gcc` has the same command line syntax as `gcc`.

> [!TIP]  
> On some systems like MacOS, gcc is in fact clang and PowerMake is not able to detect that automatically. That's no big deal because GCC and Clang have very similar syntax, but this might create small inconveniences with advanced flags translation.  
> On these systems, it might be a good idea to set the C compiler type to clang in the global config.  
> Don't set the compiler path though, just setting the compiler type will give you way less annoyances when you will try to change the compiler.


Try to change the C Compiler.  
Once this is done, go all the way back to the main menu by pressing 3 and then 8.

Finally you can save your new configuration.

### Local configuration file

The local configuration must be a `powermake_config.json` just next to your makefile.py.  
Just like the global config file, you can edit it by hand, but it's easier to just do this with `powermake -f` as described in [Global configuration file](#global-configuration-file).


## Setting a compiler directly in the makefile.py

In some rare case, something can only be compiled by a very specific compiler.  
For example, compiling a LLVM libfuzzer script can only be done using clang (In fact, it can also be done with MSVC on Windows, but for the example, let's say the program is not compatible with MSVC and we have no point using any other compiler than clang.).

In this situation, you directly invoke a specific compiler during your compilation.  
Here is an example with a fuzzer.

```py
import powermake
import powermake.compilers
import powermake.linkers


def on_build(config: powermake.Config):
    files = powermake.get_files("fuzzer/*.c")

    config.c_compiler = powermake.compilers.CompilerClang()
    config.linker = powermake.linkers.LinkerClang()

    config.add_flags("-ffuzzer")

    objects = powermake.compile_files(config, files)

    powermake.link_files(config, objects)


powermake.run("fuzzer", build_callback=on_build)
```