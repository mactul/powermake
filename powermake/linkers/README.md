# Adding a Linker

First of all, you have to create a new linker virtual class (you can use LinkerMSVC as a model).  
If your linker inherit directly from `powermake.linkers.Linker`, you should put your linker in a new separate file.  
If your linker inherit from `powermake.linkers.LinkerGNU`, you may want to put your linker in `gnu.py`, idem if your linker inherit from `powermake.linkers.LinkerMSVC`.

Then, in the `__init__.py` file of this folder, you must include your linker class and you must put your linker in the `_linker_types` dict.