import powermake

def on_build(config: powermake.Config):
    config.add_flags("-Wsecurity")

    if config.target_is_windows():
        if config.target_is_mingw():
            files = {"my_lib.c", "subtract_windows.asm", "multiply_windows.s"}
        else:
            files = {"my_lib.c", "subtract_windows.asm"}
            config.add_defines("DISABLE_GNU_AS")
    elif config.target_is_macos():
        if config.target_simplified_architecture == "arm64":
            files = {"my_lib.c", "multiply_macos_arm.s", "subtract_macos_arm.s"}
        else:
            files = {"my_lib.c", "multiply_macos.s", "subtract_macos.asm"}
    else:
        files = {"my_lib.c", "multiply_linux.s", "subtract_linux.asm"}

    objects = powermake.compile_files(config, files)

    powermake.archive_files(config, objects)

    print("print utf-8 french \"e accent grave\" to test decoding: è")

    print("print non-utf8 byte to test decoding")
    powermake.utils.print_bytes(b"\xf8")

powermake.run("my_lib", build_callback=on_build)