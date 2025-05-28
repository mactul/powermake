import powermake


def on_build(config: powermake.Config):
    powermake.run_another_powermake(config, "../library/makefile.py")
    powermake.run_another_powermake(config, "../library/makefile.py")


powermake.run("test", build_callback=on_build)