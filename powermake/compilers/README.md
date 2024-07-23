# Adding a Compiler

First of all, you have to create a new compiler virtual class (you can use CompilerMSVC as a model).  
If your compiler inherit directly from `powermake.compilers.Compiler`, you should put your compiler in a new separate file.  
If your compiler inherit from `powermake.compilers.CompilerGNU`, you may want to put your compiler in `gnu.py`, idem if your compiler inherit from `powermake.compilers.CompilerMSVC`.

Then, in the `__init__.py` file of this folder, you must include your compiler class and you must put your compiler in either the `_c_compiler_types` dict or the `_cpp_compiler_types` dict.