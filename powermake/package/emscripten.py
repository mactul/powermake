import os
import typing as T

# libname -> (embuilder target, generated lib name, has -mt variant, has sjlj variants)
_PORTS: T.Dict[str, T.Tuple[str, str, bool, bool]] = {
    "z":         ("zlib",       "z",         False, False),
    "bz2":       ("bzip2",      "bz2",       False, False),
    "jpeg":      ("libjpeg",    "jpeg",      False, False),
    "ogg":       ("ogg",        "ogg",       False, False),
    "vorbis":    ("vorbis",     "vorbis",    False, False),
    "mpg123":    ("mpg123",     "mpg123",    False, False),
    "gif":       ("giflib",     "gif",       False, False),
    "freetype":  ("freetype",   "freetype",  False, True),
    "png":       ("libpng",     "png",       True,  True),
    "harfbuzz":  ("harfbuzz",   "harfbuzz",  True,  False),
    "sqlite3":   ("sqlite3",    "sqlite3",   True,  False),
    "SDL2":      ("sdl2",       "SDL2",      True,  False),
    "SDL2_ttf":  ("sdl2_ttf",   "SDL2_ttf",  True,  False),
    "SDL2_net":  ("sdl2_net",   "SDL2_net",  False, False),
    "SDL2_gfx":  ("sdl2_gfx",   "SDL2_gfx",  False, False),
    "SDL3":      ("sdl3",       "SDL3",      True,  False),
    "SDL3_ttf":  ("sdl3_ttf",   "SDL3_ttf",  True,  False),
}

_SJLJ_SUFFIX = {"emscripten": "legacysjlj", "wasm": "wasmsjlj"}


def _lib_to_emcc_port(libname: str, pthread: bool = False, sjlj: T.Union[T.Literal["emscripten", "wasm"], None] = None) -> T.Union[T.Tuple[str, str], None]:
    """
    Given the name of the lib (without the lib prefix and the extension), returns as a first argument
    the exact string to give to `embuilder build` and as a second argument the exact name of the lib this
    will generate (without the lib prefix and the extension).

    pthread: the lib is built with atomics/shared memory (link with -pthread or -sUSE_PTHREADS=1)
    sjlj:    setjmp/longjmp implementation (None = default, "emscripten" = JS-based, "wasm" = native wasm EH)
    """
    entry = _PORTS.get(libname)
    if entry is None:
        return None

    target, lib, has_mt, has_sjlj = entry

    if pthread and has_mt:
        target += "-mt"
        lib += "-mt"
    if sjlj is not None and has_sjlj:
        target += "-" + _SJLJ_SUFFIX[sjlj]
        lib += "-" + _SJLJ_SUFFIX[sjlj]

    return target, lib




def has_pthread(flags: list[str]) -> bool:
    enabled = False
    for i, f in enumerate(flags):
        if f == "-s" and i + 1 < len(flags):
            f = "-s" + flags[i + 1]
        if f in ("-pthread", "-sUSE_PTHREADS", "-sUSE_PTHREADS=1"):
            enabled = True
        elif f == "-sUSE_PTHREADS=0":
            enabled = False
    return enabled

def sjlj_mode(flags: list[str]) -> T.Union[T.Literal["emscripten", "wasm"], None]:
    """Returns "emscripten" (JS-based), "wasm" (Wasm EH-based) or None (no setjmp/longjmp support)."""
    setting = ""
    for i, f in enumerate(flags):
        if f == "-s" and i + 1 < len(flags):
            f = "-s" + flags[i + 1]
        if f == "-fwasm-exceptions":
            setting = "wasm"
        elif f == "-sSUPPORT_LONGJMP":
            setting = "emscripten"
        elif f.startswith("-sSUPPORT_LONGJMP="):
            setting = f.split("=", 1)[1]
    if setting == "wasm":
        return "wasm"
    if setting == "emscripten":
        return "emscripten"
    return None

def lib_to_emcc_port(libname: str, ld_flags: T.List[str]) -> T.Union[T.Tuple[str, str], None]:
    """"
    Given the name of the lib (without the lib prefix and the extension), returns as a first argument
    the exact string to give to `embuilder build` and as a second argument the exact name of the lib this
    will generate (without the lib prefix and the extension).
    """
    flags = ld_flags + os.environ.get("EMCC_CFLAGS", "").split()
    return _lib_to_emcc_port(libname, has_pthread(flags), sjlj_mode(flags))



def fix_sdl3_port(emscripten_sysroot: str) -> None:
    cmake_version_file = os.path.join(emscripten_sysroot, "lib/cmake/SDL3/sdl3-config-version.cmake")
    if os.path.exists(cmake_version_file):
        # already patched
        return

    version = ""
    try:
        with open(os.path.join(emscripten_sysroot, "lib/pkgconfig/sdl3.pc"), "r") as file:
            line = ""
            while not line.startswith("Version: "):
                line = file.readline()
                if not line:
                    break
            if line:
                version = line[len("Version: "):].strip()
    except OSError:
        pass
    if version:
        with open(cmake_version_file, "w") as file:
            file.write(f"""
set(PACKAGE_VERSION "{version}")
if(PACKAGE_VERSION VERSION_LESS PACKAGE_FIND_VERSION)
  set(PACKAGE_VERSION_COMPATIBLE FALSE)
else()
  set(PACKAGE_VERSION_COMPATIBLE TRUE)
  if(PACKAGE_FIND_VERSION STREQUAL PACKAGE_VERSION)
    set(PACKAGE_VERSION_EXACT TRUE)
  endif()
endif()
""")


def post_port_build_fixes(emscripten_sysroot: str, libname: str) -> None:
    if libname == "SDL3":
        fix_sdl3_port(emscripten_sysroot)