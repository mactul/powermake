import os
import powermake

prog_test = True
assert_cc = None

def on_build(config: powermake.Config):
    config.add_flags("-Weverything")

    if config.target_is_mingw():
        config.add_ld_flags("-static")
        files = powermake.get_files("*.c", "*.cpp", "*.rc")
    else:
        files = powermake.get_files("*.c", "*.cpp")

    if config.target_is_windows():
        config.add_defines("POWERMAKE_WIN32")


    objects = powermake.compile_files(config, files)

    exe = powermake.link_files(config, objects)

    if assert_cc is not None:
        assert os.path.basename(assert_cc) == os.path.basename(config.c_compiler.path)

    if prog_test:
        print("testing generated program")
        returncode, output = powermake.run_command_get_output(config, [exe], stderr=powermake.subprocess.DEVNULL)
        if returncode != 0 or output.decode("ascii") not in ("Hello\nWorld\n", "Hello\r\nWorld\r\n"):
            print("Execution does not generate a good value")
            exit(1)

parser = powermake.ArgumentParser()
parser.add_argument("--no-prog-test", action="store_true")
parser.add_argument("--assert-cc", metavar="CC")

args_parsed = parser.parse_args()

if args_parsed.no_prog_test:
    prog_test = False

assert_cc = args_parsed.assert_cc

powermake.run("test", build_callback=on_build, args_parsed=args_parsed)