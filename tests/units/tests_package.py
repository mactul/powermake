import os
import time
import subprocess
import typing as T
import powermake.package
from unittest import mock
from powermake.package import ExtType
import powermake.version_parser as vp


def fake_listdir(answer: T.List[str]):
    def _listdir(dir: str) -> T.List[str]:
        return answer
    return _listdir

def fake_pacman_update_db():
    return True

_fake_get_installed_count = 0
def fake_pacman_get_package_installed_version(*version: str):
    global _fake_get_installed_count
    _fake_get_installed_count = 0
    def _fake_pacman_get_package_installed_version(package_name: str):
        return vp.parse_version(version[_fake_get_installed_count])
    return _fake_pacman_get_package_installed_version

old_pacman_get_available_versions = powermake.package.pacman_get_available_versions
def wrapper_pacman_get_available_versions(*args, **kwargs):
    global _fake_get_installed_count
    result = old_pacman_get_available_versions(*args, **kwargs)
    available = []
    for i in result:
        if os.path.exists(i[0]):
            available.append(i)
    _fake_get_installed_count += 1
    return available

def fake_pacman_get_server_versions(package: str, version: str):
    def _fake_pacman_get_server_versions(libpath: str):
        return [(package, vp.parse_version(version))]
    return _fake_pacman_get_server_versions


_fake_input_count = 0
def fake_input(*answers: str):
    global _fake_input_count
    _fake_input_count = 0
    def _input(prompt: str) -> str:
        global _fake_input_count
        _fake_input_count += 1
        print(prompt, answers[_fake_input_count-1], sep="")
        return answers[_fake_input_count-1]

    return _input

old_subprocess_run = subprocess.run

def fake_subprocess_run(cmd: T.List[str], **kwargs):
    if "pacman" in cmd and "-S" in cmd:
        return mock.MagicMock(returncode=0, stdout=b"mocked")
    return old_subprocess_run(cmd, **kwargs)

def fake_which(name: str):
    return str

def run_tests():
    assert(powermake.package.remove_version_ext("foo.dll") == "foo.dll")
    assert(powermake.package.remove_version_ext("foo.bar.so.3.6") == "foo.bar.so")
    assert(powermake.package.remove_version_ext("0.3") == "")

    with mock.patch("powermake.package.os.listdir", new=fake_listdir(["libssl.so", "libssl.so.1", "libssl.a", "libssl.gz.a", "libssl.dll", "ssl.a", "ssl.dll.a", "lib.a", "fdgfr", "lib.dll.a", "crypto.so", "crypto.so.0", "crypto.a"])):
        assert(powermake.package.search_lib("abcd", "ssl") == (['libssl.a', 'libssl.so', 'libssl.so.1', 'libssl.dll', 'ssl.a', 'ssl.dll.a'], {"crypto": {"crypto.so", "crypto.a", "crypto.so.0"}, "ssl.gz": {"libssl.gz.a"}}))
        assert(powermake.package.search_lib("abcd", "ssl", ext_pref_order=[ExtType.LIB_DLL, ExtType.LIB_LIB, ExtType.LIB_SO_NUM, ExtType.LIB_A, ExtType.LIB_SO, ExtType.LIB_DLL_A]) == (['libssl.dll', 'libssl.so.1', 'libssl.a', 'libssl.so', 'ssl.a', 'ssl.dll.a'], {"crypto": {"crypto.so", "crypto.a", "crypto.so.0"}, "ssl.gz": {"libssl.gz.a"}}))
        assert(powermake.package.search_lib("abcd", "ssl", ext_pref_order=[ExtType.LIB_SO, ExtType.LIB_A]) == (['libssl.so', 'libssl.a', 'ssl.a'], {'ssl.gz': {'libssl.gz.a'}, 'crypto': {'crypto.a', 'crypto.so', 'crypto.so.0'}}))

    print("Testing privilege escalation, will run `whoami` as root")
    cmd = powermake.package.linux_escalate_command(["whoami"])
    assert(cmd is not None)
    assert(subprocess.check_output(cmd).decode().strip() == "root")

    config = powermake.generate_config("test", args_parsed=powermake.ArgumentParser().parse_args([]))
    install_dir = os.path.expanduser("~/.cache/powermake/tests_install")

    with mock.patch("powermake.package.shutil.which", new=fake_which):

        with mock.patch("powermake.package.pacman_update_db", new=fake_pacman_update_db):
            with mock.patch("powermake.package.pacman_get_package_installed_version", new=fake_pacman_get_package_installed_version("v1.1.0")):
                with mock.patch("powermake.package.pacman_get_server_versions", new=fake_pacman_get_server_versions("openssl", "v1.1.0")):
                    lib = powermake.package.find_lib(config, "ssl", install_dir, min_version="1.0", max_version="1.*")
                    assert(lib.version == vp.parse_version("v1.1.0"))
                    assert(os.path.exists(os.path.join(lib.includedir, "openssl/ssl.h")))
                    assert(os.path.exists(lib.lib_file))

                with mock.patch("powermake.package.pacman_get_server_versions", new=fake_pacman_get_server_versions("libpng", "v1.6.58")):
                    with mock.patch("powermake.package.input", new=fake_input("n", "y")):
                        lib = powermake.package.find_lib(config, "png", install_dir, min_version="1.6.0", max_version="1.6.*")
                        assert(lib.version >= vp.parse_version("v1.6.0") and lib.version < vp.parse_version("v1.7.0"))
                        assert(os.path.exists(os.path.join(lib.includedir, "png.h")))
                        assert(os.path.exists(lib.lib_file))

            with mock.patch("powermake.package.pacman_get_available_versions", new=wrapper_pacman_get_available_versions):
                with mock.patch("powermake.package.pacman_get_package_installed_version", new=fake_pacman_get_package_installed_version("none", "v3.6")):
                    with mock.patch("powermake.package.pacman_get_server_versions", new=fake_pacman_get_server_versions("openssl", "v3.6")):
                        with mock.patch("powermake.package.subprocess.run", side_effect=fake_subprocess_run):
                            with mock.patch("powermake.package.input", new=fake_input("y")):
                                lib = powermake.package.find_lib(config, "ssl", install_dir, min_version="3.0", max_version="3.*")
                                print(lib)
                                assert(lib.version == vp.parse_version("v3.6"))
                                assert(os.path.exists(os.path.join(lib.includedir, "openssl/ssl.h")))
                                assert(os.path.exists(lib.lib_file))

    start_time = time.time()
    lib = powermake.package.find_lib(config, "png", install_dir, min_version="1.6.0", max_version="1.6.*")
    assert(time.time() - start_time < 1.0)  # The lib is installed, it should definitely take less than a second
    assert(lib.version >= vp.parse_version("v1.6.0") and lib.version < vp.parse_version("v1.7.0"))
    assert(os.path.exists(os.path.join(lib.includedir, "png.h")))
    assert(os.path.exists(lib.lib_file))

    start_time = time.time()
    lib = powermake.package.find_lib(config, "ssl", install_dir, min_version="3.0", max_version="3.*")
    assert(time.time() - start_time < 1.0)  # The lib should be in the system cache
    assert(lib.version == vp.parse_version("v3.6"))
    assert(os.path.exists(os.path.join(lib.includedir, "openssl/ssl.h")))
    assert(os.path.exists(lib.lib_file))

    # We assume libc is always installed, since we don't provide a version it should immediatly be found
    start_time = time.time()
    lib = powermake.package.find_lib(config, "c", install_dir, min_version=None, max_version=None)
    assert(time.time() - start_time < 1.0)  # We are just asking GCC where the libraries are
    assert(lib.version is None)
    assert(os.path.exists(os.path.join(lib.includedir, "stdio.h")))
    assert(os.path.exists(lib.lib_file))
