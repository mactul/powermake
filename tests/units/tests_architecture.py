import powermake
import powermake.architecture
from unittest import mock


def run_tests():
    # Test split_toolchain_prefix
    assert(powermake.architecture.split_toolchain_prefix(None) == (None, ""))
    assert(powermake.architecture.split_toolchain_prefix("gfgrge_garbage_reghjrhgu") == (None, "gfgrge_garbage_reghjrhgu"))
    for tool in ("gcc", "g++", "clang", "clang++", "ar", "ld", "nasm", "masm", "windres", "cc", "c++", "cpp", "clang-cl"):
        assert(powermake.architecture.split_toolchain_prefix(f"i686-linux-gnu-{tool}") == ("i686-linux-gnu-", tool))

    # Test simplify_architecture
    for arch in ("i386", "i686", "x86", "i486"):
        assert(powermake.architecture.simplify_architecture(arch) == "x86")
    for arch in ("amd64", "x86_64", "x86-64", "intel64", "x64"):
        assert(powermake.architecture.simplify_architecture(arch) == "x64")
    for arch in ("arm32", "armv5", "arm", "armv7r", "armv6zk"):
        assert(powermake.architecture.simplify_architecture(arch) == "arm32")
    for arch in ("aarch64", "arm64", "armv8", "armv8-r", "iwmmxt"):
        assert(powermake.architecture.simplify_architecture(arch) == "arm64")
    assert(powermake.architecture.simplify_architecture("gfgrge_garbage_reghjrhgu") == "")

    # Test split_toolchain_architecture
    assert(powermake.architecture.split_toolchain_architecture("i686-w64-mingw32-gcc") == ("x86", "w64-mingw32-gcc"))
    assert(powermake.architecture.split_toolchain_architecture("x86_64-w64-mingw32-gcc") == ("x64", "w64-mingw32-gcc"))
    assert(powermake.architecture.split_toolchain_architecture("amd64-w64-mingw32-gcc") == ("x64", "w64-mingw32-gcc"))
    assert(powermake.architecture.split_toolchain_architecture("i386-elf-gcc") == ("x86", "elf-gcc"))
    assert(powermake.architecture.split_toolchain_architecture("aarch64-linux-gnu-gcc") == ("arm64", "linux-gnu-gcc"))
    assert(powermake.architecture.split_toolchain_architecture("arm-linux-gnu-gcc") == ("arm32", "linux-gnu-gcc"))
    assert(powermake.architecture.split_toolchain_architecture("garbage-linux-gnu-gcc") == (None, "garbage-linux-gnu-gcc"))

    # Test search_toolchain
    assert(powermake.architecture.search_new_toolchain("ml", "x64", "x64") == "ml64")
    assert(powermake.architecture.search_new_toolchain("ml64", "x64", "x86") == "ml")
    assert(powermake.architecture.search_new_toolchain("gcc", "x64", "arm64") == "aarch64-linux-gnu-gcc")
    assert(powermake.architecture.search_new_toolchain("gcc", "x64", "x64") == "gcc")
    assert(powermake.architecture.search_new_toolchain("gcc", "x64", "x86") == "gcc")
    assert(powermake.architecture.search_new_toolchain("gcc", "arm64", "arm64") == "gcc")
    assert(powermake.architecture.search_new_toolchain("aarch64-linux-gnu-gcc", "x64", "arm64") == "aarch64-linux-gnu-gcc")
    assert(powermake.architecture.search_new_toolchain("linux-gnu-gcc", "x64", "arm64") == "aarch64-linux-gnu-gcc")
    assert(powermake.architecture.search_new_toolchain("gcc", "arm64", "x64") == "x86_64-linux-gnu-gcc")
    assert(powermake.architecture.search_new_toolchain("linux-gnu-gcc", "arm64", "x64") == "x86_64-linux-gnu-gcc")
    with mock.patch("powermake.architecture.shutil.which", new=lambda name:"" if name.startswith("amd64-") else None):
        assert(powermake.architecture.search_new_toolchain("linux-gnu-gcc", "arm64", "x64") == "amd64-linux-gnu-gcc")
    assert(powermake.architecture.search_new_toolchain("gfgrge_garbage_reghjrhgu", "arm64", "x64") is None)
    assert(powermake.architecture.search_new_toolchain("windres", "arm64", "x64") is None)
    with mock.patch("powermake.architecture.shutil.which", new=lambda name:"" if name == "i686-linux-gnu-gcc" else None):
        assert(powermake.architecture.search_new_toolchain("gcc", "arm64", "x86") == "i686-linux-gnu-gcc")
        assert(powermake.architecture.search_new_toolchain("linux-gnu-gcc", "arm64", "x86") == "i686-linux-gnu-gcc")
    with mock.patch("powermake.architecture.shutil.which", new=lambda name:"" if name == "i386-linux-gnu-gcc" else None):
        assert(powermake.architecture.search_new_toolchain("linux-gnu-gcc", "arm64", "x86") == "i386-linux-gnu-gcc")
    assert(powermake.architecture.search_new_toolchain("gfgrge_garbage_reghjrhgu", "arm64", "x86") is None)
    assert(powermake.architecture.search_new_toolchain("windres", "arm64", "x86") is None)
    assert(powermake.architecture.search_new_toolchain("gfgrge_garbage_reghjrhgu", "x64", "arm64") is None)
    with mock.patch("powermake.architecture.shutil.which", new=lambda name:"" if name == "arm-linux-gnueabi-gcc" else None):
        assert(powermake.architecture.search_new_toolchain("linux-gnu-gcc", "x64", "arm32") == "arm-linux-gnueabi-gcc")
        assert(powermake.architecture.search_new_toolchain("x86_64-linux-gnueabi-gcc", "x64", "arm32") == "arm-linux-gnueabi-gcc")
    assert(powermake.architecture.search_new_toolchain("gfgrge_garbage_reghjrhgu", "x64", "arm32") is None)
    assert(powermake.architecture.search_new_toolchain("x86_64-linux-gnueabi-windres", "x64", "arm32") is None)
    assert(powermake.architecture.search_new_toolchain("x86_64-linux-gnueabi-windres", "x64", "garbage") is None)


