import typing as T
import powermake.package
from unittest import mock


def fake_listdir(answer: T.List[str]):
    def _listdir(dir: str) -> T.List[str]:
        return answer
    return _listdir

def run_tests():
    with mock.patch("powermake.package.os.listdir", new=fake_listdir(["libssl.so", "libssl.so.1", "libssl.a", "libssl.gz.a", "libssl.dll", "ssl.a", "ssl.dll.a", "lib.a", "fdgfr", "lib.dll.a", "crypto.so", "crypto.a"])):
        assert(powermake.package.search_lib("abcd", "ssl") == (['libssl.a', 'libssl.so', 'libssl.so.1', 'libssl.dll', 'ssl.a', 'ssl.dll.a'], {"crypto": {"crypto.so", "crypto.a"}, "ssl.gz": {"libssl.gz.a"}}))

