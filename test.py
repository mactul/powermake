import powermake


def on_build(rebuild: bool):
    config = powermake.Config()

    files = powermake.get_files("*.c", "*.cpp")

    objects = powermake.compile_files(files, config, force=rebuild)

    print(powermake.link_files("program_test", objects, config))


powermake.run(build_callback=on_build)
