import powermake
import powermake.compilers

def on_build(config: powermake.Config):
    config.add_c_flags("-Wall", "-Wextra", ("-isystem", "/usr/include/c_flags"))
    assert("-Wall" in config.c_flags and "-Wextra" in config.c_flags and ("-isystem", "/usr/include/c_flags") in config.c_flags)

    config.add_cpp_flags("-Wall", "-Wextra", ("-isystem", "/usr/include/cpp_flags"))
    assert("-Wall" in config.cpp_flags and "-Wextra" in config.cpp_flags and ("-isystem", "/usr/include/cpp_flags") in config.cpp_flags)

    config.add_as_flags("-Wall", "-Wextra", ("-isystem", "/usr/include/as_flags"))
    assert("-Wall" in config.as_flags and "-Wextra" in config.as_flags and ("-isystem", "/usr/include/as_flags") in config.as_flags)

    config.add_asm_flags("-Wall", "-Wextra", ("-isystem", "/usr/include/asm_flags"))
    assert("-Wall" in config.asm_flags and "-Wextra" in config.asm_flags and ("-isystem", "/usr/include/asm_flags") in config.asm_flags)

    config.add_ld_flags("-Wall", "-Wextra", ("-isystem", "/usr/include/ld_flags"))
    assert("-Wall" in config.ld_flags and "-Wextra" in config.ld_flags and ("-isystem", "/usr/include/ld_flags") in config.ld_flags)

    config.add_shared_linker_flags("-Wall", "-Wextra", ("-isystem", "/usr/include/shared_linker_flags"))
    assert("-Wall" in config.shared_linker_flags and "-Wextra" in config.shared_linker_flags and ("-isystem", "/usr/include/shared_linker_flags") in config.shared_linker_flags)

    config.remove_flags("-Wall", "-Wextra", *[("-isystem", f"/usr/include/{f}") for f in {"c_flags", "cpp_flags", "as_flags", "asm_flags", "ld_flags", "shared_linker_flags"}])
    assert("-Wall" not in config.c_flags and "-Wextra" not in config.c_flags and ("-isystem", "/usr/include/c_flags") not in config.c_flags)
    assert("-Wall" not in config.cpp_flags and "-Wextra" not in config.cpp_flags and ("-isystem", "/usr/include/cpp_flags") not in config.cpp_flags)
    assert("-Wall" not in config.as_flags and "-Wextra" not in config.as_flags and ("-isystem", "/usr/include/as_flags") not in config.as_flags)
    assert("-Wall" not in config.asm_flags and "-Wextra" not in config.asm_flags and ("-isystem", "/usr/include/asm_flags") not in config.asm_flags)
    assert("-Wall" not in config.ld_flags and "-Wextra" not in config.ld_flags and ("-isystem", "/usr/include/ld_flags") not in config.ld_flags)
    assert("-Wall" not in config.shared_linker_flags and "-Wextra" not in config.shared_linker_flags and ("-isystem", "/usr/include/shared_linker_flags") not in config.shared_linker_flags)

    config.add_flags("-Wall", "-Wextra")
    assert("-Wall" in config.c_flags and "-Wextra" in config.c_flags)
    assert("-Wall" in config.cpp_flags and "-Wextra" in config.cpp_flags)
    assert("-Wall" in config.as_flags and "-Wextra" in config.as_flags)
    assert("-Wall" in config.asm_flags and "-Wextra" in config.asm_flags)
    assert("-Wall" in config.ld_flags and "-Wextra" in config.ld_flags)
    assert("-Wall" in config.shared_linker_flags and "-Wextra" in config.shared_linker_flags)

    config.add_rc_flags("-foo", "-bar")
    assert("-foo" in config.rc_flags and "-bar" in config.rc_flags)

    config.remove_rc_flags("-foo", "-bar")
    assert("-foo" not in config.rc_flags and "-bar" not in config.rc_flags)

    config.add_ar_flags("-foo", "-bar")
    assert("-foo" in config.ar_flags and "-bar" in config.ar_flags)

    config.remove_ar_flags("-foo", "-bar")
    assert("-foo" not in config.ar_flags and "-bar" not in config.ar_flags)

    config.add_exported_headers("foo.h", "bar.h")
    assert(("foo.h", None) in config.exported_headers and ("bar.h", None) in config.exported_headers)

    config.remove_exported_headers("foo.h", "bar.h")
    assert(("foo.h", None) not in config.exported_headers and ("bar.h", None) not in config.exported_headers)

    config.add_exported_headers("foo.h", "bar.h", subfolder="some")
    assert(("foo.h", "some") in config.exported_headers and ("bar.h", "some") in config.exported_headers)

    config.add_exported_headers("foo.h", "bar.h")
    assert(("foo.h", None) in config.exported_headers and ("bar.h", None) in config.exported_headers)

    config.remove_exported_headers("foo.h", "bar.h")
    assert(("foo.h", None) not in config.exported_headers and ("bar.h", None) not in config.exported_headers)

    assert(("foo.h", "some") in config.exported_headers and ("bar.h", "some") in config.exported_headers)

    config.add_includedirs("foo", "bar")
    assert("foo" in config.additional_includedirs and "bar" in config.additional_includedirs)

    config.remove_includedirs("foo", "bar")
    assert("foo" not in config.additional_includedirs and "bar" not in config.additional_includedirs)

    config.add_shared_libs("foo", "bar")
    assert("foo" in config.shared_libs and "bar" in config.shared_libs)

    config.remove_shared_libs("foo", "bar")
    assert("foo" not in config.shared_libs and "bar" not in config.shared_libs)


    config.target_operating_system = "Windows XP"
    assert(config.target_is_windows())

    config.target_operating_system = "Windows Server 2022"
    assert(config.target_is_windows())

    config.target_operating_system = "win32"
    assert(config.target_is_windows())

    config.target_operating_system = "Linux"
    assert(config.target_is_linux())

    config.target_operating_system = "Darwin"
    assert(config.target_is_macos())

    config.host_operating_system = "Windows"
    assert(config.host_is_windows())

    config.host_operating_system = "Darwin"
    assert(config.host_is_macos())

    config.host_operating_system = "Linux"
    assert(config.host_is_linux())

    if config.debug:
        assert(config.get_optimization_level() == "-Og")
    else:
        assert(config.get_optimization_level() == "-O3")

    config.set_optimization("-WTF")
    assert(config.get_optimization_level() is None)

    config.target_operating_system = "Darwin"
    config.set_target_architecture("x86")
    assert("-fmacho32" in config.asm_flags)

    config.c_compiler = powermake.compilers.CompilerClang()
    assert(config.c_compiler.type == "clang")
    assert(config.empty_copy().c_compiler.type == "gcc")
    assert(config.copy().c_compiler.type == "clang")


def run_tests():
    powermake.run("test", build_callback=on_build)