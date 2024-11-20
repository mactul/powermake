import os
import powermake

prog_test = True
assert_cc = None

def on_build(config: powermake.Config):
    config.add_c_cpp_as_asm_flags("-Wsecurity")
    config.add_includedirs("../library/")

    if config.target_is_mingw():
        config.add_ld_flags("-static")

    if config.target_is_windows() and not config.target_is_mingw():
        config.add_defines("DISABLE_GNU_AS")

    objects = powermake.compile_files(config, {"main.c"})

    archives = powermake.run_another_powermake(config, "../library/makefile.py")

    exe = powermake.link_files(config, objects, archives=archives)

    if assert_cc is not None:
        assert os.path.basename(assert_cc) == os.path.basename(config.c_compiler.path)

    if prog_test:
        print("testing generated program")
        if powermake.run_command(config, [exe]) != 0:
            print("generated program doesn't work")
            exit(1)

parser = powermake.ArgumentParser()
parser.add_argument("--no-prog-test", action="store_true")
parser.add_argument("--assert-cc", metavar="CC")

args_parsed = parser.parse_args()
if args_parsed.no_prog_test:
    prog_test = False
assert_cc = args_parsed.assert_cc

powermake.run("test", build_callback=on_build, args_parsed=args_parsed)