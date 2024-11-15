import powermake

def on_build(config: powermake.Config):
    config.add_c_cpp_as_asm_flags("-Wsecurity")
    config.add_includedirs("../library/")

    if config.target_is_windows() and not config.target_is_mingw():
        config.add_defines("DISABLE_GNU_AS")

    objects = powermake.compile_files(config, {"main.c"})

    archives = powermake.run_another_powermake(config, "../library/makefile.py")

    exe = powermake.link_files(config, objects, archives=archives)

    if powermake.run_command(config, [exe]) != 0:
        exit(1)

powermake.run("test", build_callback=on_build)