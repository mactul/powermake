import powermake
import powermake.interactive_config
from unittest import mock

_count = 0
def fake_input(*answers: str):
    global _count
    _count = 0
    def _input(prompt: str) -> str:
        global _count
        _count += 1
        print(prompt, answers[_count-1], sep="")
        return answers[_count-1]

    return _input


def run_tests():
    powermake.delete_files_from_disk("./powermake_config.json")
    with mock.patch("powermake.interactive_config.input", new=fake_input("1", "3", "2", "2", "3", "4", "2", "/usr/bin/echo", "1", "1", "3", "8", "4", "1")):
        powermake.interactive_config.InteractiveConfig()

    with mock.patch("powermake.interactive_config.input", new=fake_input("1", "3", "2", "2", "3", "1", "2", "/usr/bin/clang", "1", "1", "3", "8", "4", "1", "1")):
        powermake.interactive_config.InteractiveConfig()

    config = powermake.generate_config("test")

    assert(config.c_compiler.type == "clang")  # Profit to test whether the auto-toolchain works as expected
    assert(config.c_compiler.path == "/usr/bin/clang" and config.asm_compiler.path == "/usr/bin/echo")  # merge was successful

    with mock.patch("powermake.interactive_config.input", new=fake_input("1", "3", "2", "4", "3", "2", "2", "/usr/bin/i686-w64-mingw32-g++", "1", "1", "3", "8", "4", "1", "2", "y")):
        powermake.interactive_config.InteractiveConfig()

    config = powermake.generate_config("test")

    assert(config.c_compiler.type != "clang")  # Overwrite success
    assert(config.c_compiler.path == "/usr/bin/i686-w64-mingw32-gcc")
    assert(config.target_architecture == "arm32")

    powermake.delete_files_from_disk("./powermake_config.json")
