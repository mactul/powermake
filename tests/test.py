import powermake


def on_build(config: powermake.Config):

    config.add_c_cpp_flags("-Weverything")

    config.add_shared_libs("pthread")

    files = powermake.get_files("*.c", "*.cpp")

    objects = powermake.compile_files(config, files)

    print(powermake.link_files(config, objects))


powermake.run("program_test", build_callback=on_build)
