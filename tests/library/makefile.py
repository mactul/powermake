import os
import powermake

shared_lib = False

def on_build(config: powermake.Config):
    if "-fsanitize=address" in config.c_flags:
        print("ASAN propagated, MAGIC=zJgH_V5s2")

    config.add_flags("-Wsecurity")

    if config.target_is_windows():
        if config.asm_compiler is not None and config.asm_compiler.type == "masm":
            asm_file = f"subtract_windows_masm.asm"
        else:
            asm_file = f"subtract_windows.asm"
        if config.target_is_mingw():
            files = {"my_lib.c", asm_file, f"multiply_windows.s"}
        else:
            files = {"my_lib.c", asm_file}
            config.add_defines("DISABLE_GNU_AS")
    elif config.target_is_macos():
        if config.target_simplified_architecture == "arm64":
            files = {"my_lib.c", "multiply_macos_arm.s", "subtract_macos_arm.s"}
        else:
            files = {"my_lib.c", "multiply_macos.s", "subtract_macos.asm"}
    else:
        if config.target_simplified_architecture == "arm64":
            files = {"my_lib.c", "multiply_linux_arm.s", "subtract_linux_arm.s"}
        else:
            files = {"my_lib.c", "multiply_linux.s", "subtract_linux.asm"}

    objects = powermake.compile_files(config, files)

    if shared_lib:
        powermake.link_shared_lib(config, objects)
        if config.target_is_mingw():
            assert(os.path.exists(os.path.join(config.lib_build_directory, f"{config.target_name}.dll")))
            assert(os.path.exists(os.path.join(config.lib_build_directory, f"lib{config.target_name}.dll.a")))
        else:
            assert(os.path.exists(os.path.join(config.lib_build_directory, f"lib{config.target_name}.so")))
    else:
        powermake.archive_files(config, objects)

    print("print utf-8 french \"e accent grave\" to test decoding: è")

    print("print non-utf8 byte to test decoding")
    powermake.utils.print_bytes(b"\xf8")


def on_install(config: powermake.Config, location: str | None):
    config.add_exported_headers("my_lib.h", subfolder="my_lib")

    powermake.default_on_install(config, location)

parser = powermake.ArgumentParser()
parser.add_argument("--shared-lib", action="store_true")
args_parsed = parser.parse_args()

if args_parsed.shared_lib:
    shared_lib = True

powermake.run("my_lib", build_callback=on_build, install_callback=on_install, args_parsed=args_parsed)
