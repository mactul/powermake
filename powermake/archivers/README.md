# Adding a Archiver

First of all, you have to create a new archiver virtual class (you can use ArchiverMSVC as a model).  
If your archiver inherit directly from `powermake.archivers.Archiver`, you should put your archiver in a new separate file.  
If your archiver inherit from `powermake.archivers.ArchiverGNU`, you may want to put your archiver in `gnu.py`, idem if your archiver inherit from `powermake.archivers.ArchiverMSVC`.

Then, in the `__init__.py` file of this folder, you must include your archiver class and you must put your archiver in the `_archiver_types` dict.