<!-- This file, being part of the documentation is excluded from AI restrictions of the license -->
# Package Manager

### [<- Previous tutorial (Configuration and Cross-compilation)](../05-configuration-and-crosscompilation/README.md)

> [!IMPORTANT]  
> The powermake package manager is one of the most complex powermake subsystems.  
> Make sure that you've followed all previous tutorials and that you have a correct understanding of simple powermake makefiles.

## Quick introduction

Managing dependencies for a C/C++ program has never been easy, there are a lot of library formats, and a lot of ways they can be compiled and installed.

You can assume the libraries you need are installed on your system with your favorite package manager, but if you are cross-compiling, they might not be available.  
It's even worse if you ever need to handle multiple versions of the same library that coexist on your system.

The powermake package manager is meant to tackle these issues.
- It can find libraries installed on your system and check their package version (only available for Linux distributions providing pacman yet).
- It verifies compatibility with your linker.
- It can clone git repos, compile them and install them in different subfolders for each version.
- It automatically parses package versions and can manage compatible version ranges.

## Syntax - `powermake.package.find_lib`

The most important piece of the powermake package manager is the `powermake.package.find_lib` function.

### Simplest call

The simplest call to this function looks like that
```py
lib = powermake.package.find_lib(config, "ssl")
config.add_lib(lib)
```

<details>
<summary>Full file sample</summary>

```py
import powermake

def on_build(config: powermake.Config):
    files = powermake.get_files("**/*.c")

    lib = powermake.package.find_lib(config, "ssl")
    config.add_lib(lib)

    objects = powermake.compile_files(config, files)

    powermake.link_files(config, objects)

powermake.run("my_project", build_callback=on_build)
```

</details>

Here, no version is specified, so PowerMake will just try to find a lib called ssl (libssl.so, libssl.a, ssl.dll, whatever...), that is compatible with the linker specified in the config.  
To do that, PowerMake uses 4 strategies:
- Search in the same folders as the linker does (usually /usr/lib, /usr/lib32, etc...)
- Search in powermake installed libs (by default: `~/.powermake/installed_libs/`)
- Interrogate the system package manager and ask you to install a package if available (only available for Linux distributions providing pacman yet).
- Clone https://github.com/openssl/openssl.git, compile and install it in a subfolder of `~/.powermake/installed_libs/`.

The `lib` returned is an object `powermake.package.Lib` that contains include dirs, lib version, lib path, etc... `config.add_lib` will set everything required to compile and link with this lib.

### Specifying a version range

To use a specific version of a lib, you must specify `min_version` and `max_version`.

```py
lib = powermake.package.find_lib(config, "ssl", min_version="v1.1.0", max_version="v1.*")
config.add_lib(lib)
```

<details>
<summary>Full file sample</summary>

```py
import powermake

def on_build(config: powermake.Config):
    files = powermake.get_files("**/*.c")

    lib = powermake.package.find_lib(config, "ssl", min_version="v1.1.0", max_version="v1.*")
    config.add_lib(lib)

    objects = powermake.compile_files(config, files)

    powermake.link_files(config, objects)

powermake.run("my_project", build_callback=on_build)
```
</details>


As you see, the min_version and max_version accept versions containing `'*'` in them. `v1.*` means any version that has 1 as the major version number.

Here, PowerMake will make sure to find the ssl lib in a version that is >= v1.1.0 and < v2.0.

Now, PowerMake can no longer blindly search the system lib folders, so for every candidate file, it has to ask the system package manager what is the version of the package that owns this file. Currently, this only works with pacman on Linux.

If the package is not in the correct version or powermake didn't manage to interrogate the system package manager (currently, any system that is not Linux Arch based), it will fall back to downloading and compiling via git as before.

> [!NOTE]  
> When choosing the version to download from git, PowerMake will always use the latest version available on git that matches the range.  
> Therefore, unless you want full reproducibility, you should use `'*'` when specifying your max version, at least on the version patch (example: `v1.3.*`), so you will always get security updates and bug fixes.

### Using another git repo

Earlier, we told you that ssl was downloaded from https://github.com/openssl/openssl.git.  
This is possible because by default, when you do:
```py
powermake.package.find_lib(config, "ssl")
```
You are in reality doing:
```py
powermake.package.find_lib(config, "ssl", git_repo=powermake.package.DefaultGitRepos())
```

`DefaultGitRepos` is an object that contains instructions on how to download and compile a lot of common libs.

If your lib is not in DefaultGitRepos, either because we didn't think of adding it or because it's your own code, you can replace `DefaultGitRepos` by a `powermake.package.GitRepo` object.

```py
# We specify where the repo can be found and where is the makefile.py in this repo
repo = powermake.package.GitRepo("https://github.com/someone/my_awesome_repo.git", "build/makefile.py")

# In reality, the repo doesn't have a file build/makefile.py, but PowerMake can get it from somewhere else and copy it after the clone.
# "somewhere else" can be a path from your computer (if you don't specify the second argument), or even another git repository like here:
repo.set_external_powermake_makefile("generic/cmake/cmake_makefile.py", "https://github.com/mactul/powermake-repos.git")

lib = powermake.package.find_lib(config, "my_awesome_lib", git_repo=repo)
config.add_lib(lib)
```

<details>
<summary>Full file sample</summary>

```py
import powermake

def on_build(config: powermake.Config):
    files = powermake.get_files("**/*.c")

    # We specify where the repo can be found and where is the makefile.py in this repo
    repo = powermake.package.GitRepo("https://github.com/someone/my_awesome_repo.git", "build/makefile.py")

    # In reality, the repo doesn't have a file build/makefile.py, but PowerMake can get it from somewhere else and copy it after the clone.
    # "somewhere else" can be a path from your computer (if you don't specify the second argument), or even another git repository like here:
    repo.set_external_powermake_makefile("generic/cmake/cmake_makefile.py", "https://github.com/mactul/powermake-repos.git")

    lib = powermake.package.find_lib(config, "my_awesome_lib", git_repo=repo)
    config.add_lib(lib)

    objects = powermake.compile_files(config, files)

    powermake.link_files(config, objects)

powermake.run("my_project", build_callback=on_build)
```
</details>

If the repo containing your lib is yours and uses PowerMake, don't bother with `repo.set_external_powermake_makefile`, but this feature is extremely handy when compiling an OpenSource project that isn't yours and that uses another build system than PowerMake.

In the example, we use a makefile.py that runs generic cmake commands. It can be a great fit if the lib you are trying to compile uses CMake, but of course, the idea is that you can use any makefile.py, as long as the build and install callbacks of this makefile.py are correctly implemented. You can even apply patches to the source code in this makefile.py.

> [!TIP]  
> Of course, you can combine this with `min_version` and `max_version`.

> [!CAUTION]  
> When you don't specify a version with `min_version` and `max_version`, it's not the latest commit on the main branch that is taken, it's the latest tag looking like a version.  
> If it's your own repository that you are using, make sure you tag your versions.

### Choosing static or dynamic libraries

By default, `powermake.package.find_lib` tries to use static libraries when they are available.  
This is the preference order used by default:
```py
from powermake.package import ExtType

DEFAULT_EXT_PREF_ORDER = [ExtType.LIB_A, ExtType.LIB_SO, ExtType.LIB_DLL_A, ExtType.LIB_LIB, ExtType.LIB_DLL, ExtType.LIB_DYLIB]
```

You can change this order and even remove entries if you want.  
This example only accepts .so and .dll (it prefers .so, but since a linker that accepts .so doesn't accept .dll and vice-versa, the order doesn't matter much).
```py
lib = powermake.package.find_lib(config, "ssl", ext_pref_order=[powermake.package.ExtType.LIB_SO, powermake.package.ExtType.LIB_DLL])
config.add_lib(lib)
```

<details>
<summary>Full file sample</summary>

```py
import powermake
from powermake.package import ExtType

def on_build(config: powermake.Config):
    files = powermake.get_files("**/*.c")

    lib = powermake.package.find_lib(config, "ssl", ext_pref_order=[.ExtType.LIB_SO, ExtType.LIB_DLL])
    config.add_lib(lib)

    objects = powermake.compile_files(config, files)

    powermake.link_files(config, objects)

powermake.run("my_project", build_callback=on_build)
```
</details>


## Libs pre-configured in PowerMake

Below is a matrix generated every Monday morning by a CI that shows all pre-configured libraries tested on multiple platforms and cross-compilation scenarios.

If you see red, that suggest this specific host OS/architecture - target OS/architecture combo might not work, but it can also be a CI quirk (missing build dependencies for example)

![Compatibility matrix](https://mactul.github.io/powermake/compatibility-matrix.svg)