import powermake

def on_build(config: powermake.Config):
    config.add_c_cpp_as_asm_flags("-Wsecurity")

    objects = powermake.compile_files(config, {"my_lib.c", "multiply.s", "subtract.asm"})

    powermake.archive_files(config, objects)

powermake.run("my_lib", build_callback=on_build)