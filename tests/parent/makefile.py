import powermake
import powermake.compilers


def on_build(config: powermake.Config):
    powermake.run_another_powermake(config, "../multiplatform/makefile.py", use_parent_toolchain=False, command_line_args=["--assert-cc", "gcc", "--assert-arch", "x64"], skip_already_done=False)

    powermake.run_another_powermake(config, "../multiplatform/makefile.py", command_line_args=["--assert-cc", "clang", "--assert-arch", "x86"], skip_already_done=False)


powermake.run("test", build_callback=on_build)