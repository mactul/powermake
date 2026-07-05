import os
import powermake
import powermake.version_parser as vp

def on_build(config: powermake.Config):
    config.add_flags("-Wall", "-Wextra")

    if config.target_is_windows():
        config.add_ld_flags("-static")

    # We want the tests install to be destroyed after cache deletion
    install_dir = os.path.join(powermake.cache.get_cache_dir(), "tests_install")

    lib = powermake.package.find_lib(config, "zs" if config.target_is_windows() else "z", install_dir=install_dir, min_version='1.3.2', max_version='1.*')

    config.add_includedirs(lib.includedir)

    objects = powermake.compile_files(config, {"main.c"})

    exe = powermake.link_files(config, objects, archives=[lib.lib_file])

    r, out = powermake.run_command_get_output(config, command=[exe], custom_info_msg="Testing the installed version")
    assert(r == 0)
    version = vp.parse_version(out.decode().strip().rsplit("\n", maxsplit=1)[-1].strip())
    assert(version >= vp.parse_version("v1.3.2"))
    lib.version.post_number = None
    assert(version == lib.version)

powermake.run("use_zlib", build_callback=on_build)
