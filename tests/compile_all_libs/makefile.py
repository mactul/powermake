import os
import json
import powermake
import powermake.version_parser as vp

def on_build(config: powermake.Config):
    # If a compiler is missing, the CI should fail instead of generating a matrix all red.
    assert(config.c_compiler is not None)
    assert(config.cpp_compiler is not None)
    assert(config.asm_compiler is not None or config.as_compiler is not None)
    assert(config.linker is not None)
    assert(config.shared_linker is not None)

    libs = []
    repo = powermake.package.DefaultGitRepos()
    for libname in repo._default_packages:
        libs.append((libname, repo._default_packages[libname][0]))

    libs.append(("ssl", "boringssl"))
    libs.append(("crypto", "boringssl"))
    libs.append(("ssl", "libressl"))
    libs.append(("crypto", "libressl"))
    libs.append(("json-c", "json-c"))
    libs.append(("freetype", "freetype"))
    libs.append(("harfbuzz", "harfbuzz"))

    if config.target_is_windows():
        libs.remove(("z", "zlib"))
    else:
        libs.remove(("zs", "zlib"))

    if config.target_is_windows() and not config.target_is_mingw():
        libs.remove(("SDL2_image", "SDL_image"))
        libs.remove(("SDL3_image", "SDL_image"))
    else:
        libs.remove(("SDL2_image-static", "SDL_image"))
        libs.remove(("SDL3_image-static", "SDL_image"))

    libs.sort()  # We don't really care about the order, but we want something predictible

    # We want the tests install to be destroyed after cache deletion
    install_dir = os.path.join(powermake.cache.get_cache_dir(), "tests_install")

    success = {}

    for libname, package_name in libs:
        try:
            powermake.package.find_lib(config, libname, package_name=package_name, install_dir=install_dir, disable_system_packages=True)
            success[(libname, package_name)] = True
        except powermake.PowerMakeRuntimeError as e:
            print(e)
            success[(libname, package_name)] = False

    output = {
        "host_os": config.host_operating_system,
        "host_arch": config.host_simplified_architecture,
        "target_os": config.target_operating_system,
        "target_arch": config.target_simplified_architecture,
        "results": [
            {"lib": lib, "provider": provider, "success": ok}
            for (lib, provider), ok in success.items()
        ],
    }

    with open(f"results-{output['host_os']}_{output['host_arch']}-{output['target_os']}_{output['target_arch']}.json", "w") as f:
        json.dump(output, f, indent=4)

powermake.run("compile_all_libs", build_callback=on_build)
