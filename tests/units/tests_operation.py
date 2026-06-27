import os
import sys
import time
import powermake
import powermake.operation

def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)

def run_tests():
    config = powermake.generate_config('test', args_parsed=powermake.ArgumentParser().parse_args([]))
    powermake.run_another_powermake(config, '../lib_depend/makefile.py', rebuild=True)
    r, output = powermake.run_command_get_output(config, [sys.executable, '../lib_depend/makefile.py', '--get-probable-bin-path'])
    assert(r == 0)
    path = output.decode().strip()
    assert(not powermake.operation.needs_update(path, {'../library/my_lib.c', '../lib_depend/main.c'}, ['../library/']))
    time.sleep(0.1)
    touch("../library/my_lib.h", (time.time(), time.time()))
    time.sleep(0.1)
    assert(powermake.operation.needs_update(path, {'../library/my_lib.c', '../lib_depend/main.c'}, ['../library/']))
    powermake.run_another_powermake(config, '../lib_depend/makefile.py', skip_already_done=False)
    assert(not powermake.operation.needs_update(path, {'../library/my_lib.c', '../lib_depend/main.c'}, ['../library/']))
