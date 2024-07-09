import powermake


def on_build(config: powermake.Config):

    files = powermake.get_files("*.c", "*.cpp")

    print(powermake.run_another_powermake("/home/mactul/Documents/c-cpp/stage/git_dev/LibSrc/SA/powermake/makefile.py"))

    objects = powermake.compile_files(files, config, force=config.rebuild)

    print(powermake.link_files("program_test", objects, config, force=config.rebuild))


powermake.run(build_callback=on_build)
