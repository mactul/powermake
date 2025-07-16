# Internal Documentation

## Adding a Compiler

First of all, you have to create a new compiler derived class (you can use CompilerMSVC as a model).  
If your compiler inherit directly from `powermake.compilers.Compiler`, you should put your compiler in a new separate file.  
If your compiler inherit from `powermake.compilers.CompilerGNU`, you may want to put your compiler in `gnu.py`, idem if your compiler inherit from `powermake.compilers.CompilerMSVC`.

Then, in the `__init__.py` file of this folder, you must include your compiler class and you must put your compiler in either the `_c_compiler_types` dict or the `_cpp_compiler_types` dict.

> [!NOTE]  
> Each derived class should implement `check_if_arg_exists`, especially if the derived class uses the inherited `translate_flag` method.
> This method can be very tricky to implement, you have to play with the tool to find the command that will succeeds if the flag is supported and fails otherwise.  
> If you are not able to find such a command, you can parse the output like what was done with masm.


## Adding auto-toolchain support for the new compiler

Once the compiler is added in `__init__.py`, it is usable if the type is specified in a json config.

However, to be integrated well with the powermake environment and especially with the auto-toolchain mechanism, you need to modify [architecture.py](../architecture.py) and [config.py](../config.py).

The former is quite easy, you just have to modify the `split_toolchain_prefix` function.
> [!NOTE]  
> You can skip this if your tool never supports toolchains prefix like msvc.

The latter requires a little more work.

First, you need to modify the `get_type_pref` function. this is to make sure that the tool type is guessed correctly when only the path is specified.

Then you need to edit the top of `auto_toolchain`. If the tool you are adding doesn't give a ton of information on the rest of the toolchain, like `nasm` of `masm`, only edit the `to_<YOUR TOOL CATEGORY>` variable. At least make sure that the tool type is translated into the same tool type in its own category. When editing this function, you should rather put not enough corresponding entries than too many. An entry here should be a very plausible guess.

Finally, you can edit the bottom of the `Config.__init__` method to add your tool to be auto-selected. (Preferably, add your tool in the end of each list so it will be selected only if their is nothing else available. If you don't do that, you will change the default behavior of PowerMake which will break a ton of scripts.)
