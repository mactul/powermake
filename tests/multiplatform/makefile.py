import powermake
import subprocess


def on_build(config: powermake.Config):
    config.add_c_cpp_as_asm_flags("-Weverything")
    config.add_ld_flags("-static")

    if config.target_is_windows():
        config.add_defines("POWERMAKE_WIN32")

    files = powermake.get_files("*.c", "*.cpp")

    objects = powermake.compile_files(config, files)

    exe = powermake.link_files(config, objects)

    output = subprocess.check_output([exe], encoding="ascii")
    if output != "Hello\nWorld\n":
        print("Execution does not generate a good value")
        exit(1)

powermake.run("test", build_callback=on_build)