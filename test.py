import powermake


def on_build(config: powermake.Config):

    files = powermake.get_files("*.c", "*.cpp")

    objects = powermake.compile_files(files, config, force=config.rebuild)

    print(powermake.link_files("program_test", objects, config, force=config.rebuild))


powermake.run(build_callback=on_build)
