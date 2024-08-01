# Adding a SharedLinker

First of all, you have to create a new shared linker virtual class (you can use SharedLinkerMSVC as a model).  
If your shared linker inherit directly from `powermake.shared_linkers.SharedLinker`, you should put your shared linker in a new separate file.  
If your shared linker inherit from `powermake.shared_linkers.SharedLinkerGNU`, you may want to put your shared linker in `gnu.py`, idem if your shared linker inherit from `powermake.shared_linkers.SharedLinkerMSVC`.

Then, in the `__init__.py` file of this folder, you must include your shared linker class and you must put your shared linker in the `_shared_linker_types` dict.