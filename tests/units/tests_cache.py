import os
import time
import powermake
import powermake.cache
from unittest import mock


def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)


def run_tests():
    # Test get_cache_dir
    with mock.patch("powermake.cache.platform.system", new=lambda :"Darwin"):
        assert(powermake.cache.get_cache_dir().endswith("/Library/Caches/powermake/"))
    with mock.patch("powermake.cache.platform.system", new=lambda :"Windows"):
        assert(powermake.cache.get_cache_dir().endswith("\\powermake\\cache"))
    with mock.patch("powermake.cache.platform.system", new=lambda :"Linux"):
        assert(powermake.cache.get_cache_dir().endswith("/.cache/powermake/"))

    # Test load_cache_from_file and store_cache_to_file
    cache_content = {
        "foo": "bar"
    }
    powermake.delete_files_from_disk("foo")
    cache_file = os.path.join(powermake.cache.get_cache_dir(), "foo/bar")
    powermake.cache.store_cache_to_file(cache_file, cache_content, "foo")
    assert(os.path.exists(cache_file))
    cache_loaded = powermake.cache.load_cache_from_file(cache_file)
    assert(cache_loaded == {}) # Control filepath doesn't exists

    touch("foo") # Create the control filepath
    powermake.cache.store_cache_to_file(cache_file, cache_content, "foo")
    assert(os.path.exists(cache_file))
    cache_loaded = powermake.cache.load_cache_from_file(cache_file)
    assert("foo" in cache_loaded and cache_loaded["foo"] == "bar")

    touch("foo", (time.time() * 10, time.time() * 10)) # modify the control filepath
    cache_loaded = powermake.cache.load_cache_from_file(cache_file)
    assert(cache_loaded == {} or print("cache_loaded:", cache_loaded))
    powermake.delete_files_from_disk("foo")

    # Simulate an old cache that is no longer compatible
    file = open(cache_file, "w")
    file.write('{"foo": "bar"}')
    file.close()
    cache_loaded = powermake.cache.load_cache_from_file(cache_file)
    assert(cache_loaded == {})