import typing as T
import powermake.package
from powermake.package import ExtType
from unittest import mock


def fake_listdir(answer: T.List[str]):
    def _listdir(dir: str) -> T.List[str]:
        return answer
    return _listdir

def run_tests():
    with mock.patch("powermake.package.os.listdir", new=fake_listdir(["libssl.so", "libssl.so.1", "libssl.a", "libssl.gz.a", "libssl.dll", "ssl.a", "ssl.dll.a", "lib.a", "fdgfr", "lib.dll.a", "crypto.so", "crypto.so.0", "crypto.a"])):
        assert(powermake.package.search_lib("abcd", "ssl") == (['libssl.a', 'libssl.so', 'libssl.so.1', 'libssl.dll', 'ssl.a', 'ssl.dll.a'], {"crypto": {"crypto.so", "crypto.a", "crypto.so.0"}, "ssl.gz": {"libssl.gz.a"}}))
        assert(powermake.package.search_lib("abcd", "ssl", ext_pref_order=[ExtType.LIB_DLL, ExtType.LIB_LIB, ExtType.LIB_SO_NUM, ExtType.LIB_A, ExtType.LIB_SO, ExtType.LIB_DLL_A]) == (['libssl.dll', 'libssl.so.1', 'libssl.a', 'libssl.so', 'ssl.a', 'ssl.dll.a'], {"crypto": {"crypto.so", "crypto.a", "crypto.so.0"}, "ssl.gz": {"libssl.gz.a"}}))
        assert(powermake.package.search_lib("abcd", "ssl", ext_pref_order=[ExtType.LIB_SO, ExtType.LIB_A]) == (['libssl.so', 'libssl.a', 'ssl.a'], {'ssl.gz': {'libssl.gz.a'}, 'crypto': {'crypto.a', 'crypto.so', 'crypto.so.0'}}))

