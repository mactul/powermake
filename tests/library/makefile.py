import powermake

def on_build(config: powermake.Config):
    config.add_c_cpp_as_asm_flags("-Wsecurity")

    if config.target_is_windows() and not config.target_is_mingw():
        config.add_defines("DISABLE_GNU_AS")
        files = {"my_lib.c", "subtract.asm"}
    else:
        files = {"my_lib.c", "multiply.s", "subtract.asm"}

    objects = powermake.compile_files(config, files)

    powermake.archive_files(config, objects)

powermake.run("my_lib", build_callback=on_build)