import os
import sys
import json
import powermake
from unittest import mock
import powermake.generation.compile_commands as cc

not_files = {
        os.path.abspath("not_a_file_1.c"),
        os.path.abspath("not_a_file_2.cpp"),
        os.path.abspath("not_a_file_3.s"),
        os.path.abspath("not_a_file_4.asm")
    }

def build_will_fail(config: powermake.Config):

    powermake.compile_files(config, not_files)

def build_empty(config: powermake.Config):
    return

def fail(_):
    raise NotImplementedError("test")

def run_failing_compilation():
    parser = powermake.ArgumentParser()
    stdout = sys.stdout
    sys.stdout = open(os.devnull, 'w')
    with mock.patch("powermake.args_parser.exit", new=fail):
        try:
            powermake.run("test", build_callback=build_will_fail, args_parsed=parser.parse_args(["-o", "."]))
        except NotImplementedError:
            pass
    sys.stdout.close()
    sys.stdout = stdout

    compile_commands = []
    with open("compile_commands.json", "r") as file:
        compile_commands = json.load(file)

    assert(len(compile_commands) == 4)
    compile_commands_files = {entry["file"] for entry in compile_commands}
    for file in not_files:
        assert(file in compile_commands_files)


def run_succeeding_compilation():
    parser = powermake.ArgumentParser()
    powermake.run("test", build_callback=build_empty, args_parsed=parser.parse_args(["-o", "."]))

    compile_commands = []
    with open("compile_commands.json", "r") as file:
        compile_commands = json.load(file)

    assert(len(compile_commands) == 0)

def run_tests():
    powermake.delete_files_from_disk("compile_commands.json")
    run_failing_compilation()  # Test if compile_commands.json doesn't exists
    run_failing_compilation()  # Test merging compile_commands.json

    not_files.pop()

    run_failing_compilation()  # Test merging a missing file in compile_commands.json

    run_succeeding_compilation()  # Verify that a succeeding compilation was not merged with the old compile_commands.json

    powermake.delete_files_from_disk("compile_commands.json")
    cc.generate_compile_commands(powermake.generate_config("test"))
    assert(not os.path.exists("compile_commands.json"))