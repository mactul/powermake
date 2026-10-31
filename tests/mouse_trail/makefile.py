import os
import powermake
import powermake.cache

def on_build(config: powermake.Config):
    config.add_flags("-Wall", "-Wextra")

    # We want the tests install to be destroyed after cache deletion
    install_dir = os.path.join(powermake.cache.get_cache_dir(), "tests_install")

    sdl3_lib = powermake.package.find_lib(config, "SDL3", install_dir=install_dir)
    config.add_lib(sdl3_lib)

    files = powermake.get_files("**/*.c")

    objects = powermake.compile_files(config, files)

    if config.target_is_android():
        if not os.path.exists("./debug.keystore"):
            powermake.create_android_keystore(config, "./debug.keystore", password="android")

        java_files = powermake.get_files(os.path.join(sdl3_lib.includedir, "../src/**/*.java"))
        powermake.link_android_apk(config, objects, java_files, "./debug.keystore", keystore_password="android")
    else:
        powermake.link_files(config, objects)

powermake.run("mouse_trail", build_callback=on_build)
