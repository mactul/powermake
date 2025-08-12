import re
import typing as T
from enum import Enum

_Version = T.TypeVar("_Version", bound="Version")

_PreType = T.TypeVar("_PreType", bound="PreType")

class PreType(Enum):
    ALPHA = 0
    BETA = 1
    RELEASE_CANDIDATE = 2
    NOT_PRE = 3

    def __lt__(self, other: _PreType) -> bool:
        if self.__class__ is other.__class__:
            return bool(self.value < other.value)
        raise NotImplementedError()


class Version():
    def __init__(self, epoch: str = '1', release: T.Tuple[str, ...] = ('0', ), pre_type: PreType = PreType.NOT_PRE, pre_number: T.Union[str, None] = None, post_number: T.Union[str, None] = None, dev_number: T.Union[str, None] = None) -> None:
        self.epoch = epoch
        self.release = release
        self.pre_type = pre_type
        self.pre_number = pre_number
        self.post_number = post_number
        self.dev_number = dev_number

    def __test(self, other: _Version) -> T.Union[bool, None]:
        if self.epoch != '*' and other.epoch != '*' and int(self.epoch) != int(other.epoch):
            return int(self.epoch) > int(other.epoch)  # one epoch is bigger

        for i in range(min(len(self.release), len(other.release))):
            if self.release[i] != '*' and other.release[i] != '*' and int(self.release[i]) != int(other.release[i]):
                return int(self.release[i]) > int(other.release[i])  # one release i is bigger
        if len(self.release) > len(other.release) and (len(other.release) == 0 or other.release[-1] != '*'):
            for i in range(len(other.release), len(self.release)):
                if self.release[i] != '0':
                    return True
        if len(other.release) > len(self.release) and (len(self.release) == 0 or self.release[-1] != '*'):
            for i in range(len(self.release), len(other.release)):
                if other.release[i] != '0':
                    return False

        if self.pre_type != other.pre_type:
            return self.pre_type > other.pre_type

        if self.pre_number is not None and other.pre_number is None:
            return True
        if self.pre_number is None and other.pre_number is not None:
            return False
        if self.pre_number is not None and other.pre_number is not None:
            if self.pre_number != '*' and other.pre_number != '*' and int(self.pre_number) != int(other.pre_number):
                return int(self.pre_number) > int(other.pre_number)

        if self.post_number is not None and other.post_number is None:
            return True
        if self.post_number is None and other.post_number is not None:
            return False
        if self.post_number is not None and other.post_number is not None:
            if self.post_number != '*' and other.post_number != '*' and int(self.post_number) != int(other.post_number):
                return int(self.post_number) > int(other.post_number)

        if self.dev_number is not None and other.dev_number is None:
            return True
        if self.dev_number is None and other.dev_number is not None:
            return False
        if self.dev_number is not None and other.dev_number is not None:
            if self.dev_number != '*' and other.dev_number != '*' and int(self.dev_number) != int(other.dev_number):
                return int(self.dev_number) > int(other.dev_number)

        return None

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Version):
            return False
        return self.__test(other) is None

    def __ge__(self, other: _Version) -> bool:
        return self.__test(other) is not False

    def __gt__(self, other: _Version) -> bool:
        return self.__test(other) is True

    def __str__(self) -> str:
        string = f"{self.epoch}!{'.'.join(self.release)}"
        if self.pre_type == PreType.ALPHA:
            string += f"-alpha{self.pre_number}"
        elif self.pre_type == PreType.BETA:
            string += f"-beta{self.pre_number}"
        elif self.pre_type == PreType.RELEASE_CANDIDATE:
            string += f"-rc{self.pre_number}"
        if self.post_number is not None:
            string += f"-post{self.post_number}"
        if self.dev_number is not None:
            string += f"-dev{self.dev_number}"

        return string

    def __repr__(self) -> str:
        return f"<Version {str(self)}>"


def remove_version_frills(string: str) -> str:
    output = ""
    i = 0
    marker = 0
    while i < len(string) and (string[i].isdigit() or string[i] in ('*', ':', '!')):
        if string[i] in (':', '!'):
            marker = i
        i += 1
    while i < len(string) and (string[i].isdigit() or string[i] in ('*', '.')):
        if string[i] == '.':
            marker = i
        i += 1
    output = string[0:marker]
    while i < len(string):
        if string[i] in ('.', '-', '+'):
            if re.fullmatch("([0-9]+|\\*)|((alpha|beta|a|b|rc|post|p|develop|dev|d)([0-9]+|\\*)?)", string[marker+1:i]):
                output += string[marker:i]
            marker = i
        i += 1
    if re.fullmatch("([0-9]+|\\*)|((alpha|beta|a|b|rc|post|p|develop|dev|d)([0-9]+|\\*)?)", string[marker+1:i]):
        output += string[marker:i]
    return output


def parse_version(string: str) -> T.Union[Version, None]:
    extended_number_regex = "[0-9]+|\\*"
    separator = "(?:\\.|-|\\+)"
    pre_regex = f"(?:{separator}?(alpha|beta|a|b|r|rc){separator}?({extended_number_regex}))"
    post_regex = f"(?:{separator}?(?:post|p|-|\\.){separator}?({extended_number_regex}))"
    dev_regex = f"(?:{separator}?(?:develop|dev|d){separator}?({extended_number_regex}))"
    search = re.fullmatch(f'v?(?:({extended_number_regex})(?:!|:))?((?:{extended_number_regex})(?:\\.(?:{extended_number_regex}))*){pre_regex}?{post_regex}?{dev_regex}?', string, re.IGNORECASE)
    if not search:
        return None

    epoch = search.group(1)
    release = search.group(2)
    pre_type = search.group(3)
    pre_number = search.group(4)
    post_number = search.group(5)
    dev_number = search.group(6)

    if epoch is None:
        epoch = '1'
    else:
        epoch = str(epoch)
    if release is None:
        release = '0'  # impossible but let's be extra careful
    else:
        release = str(release)
    release = tuple(release.split('.'))

    if pre_type is None:
        pre_type = PreType.NOT_PRE
    elif pre_type.startswith('a'):
        pre_type = PreType.ALPHA
    elif pre_type.startswith('b'):
        pre_type = PreType.BETA
    elif pre_type.startswith('r'):
        pre_type = PreType.RELEASE_CANDIDATE
    else:
        return None  # can not happen

    if pre_number is not None:
        pre_number = str(pre_number)

    if post_number is not None:
        post_number = str(post_number)

    if dev_number is not None:
        dev_number = str(dev_number)

    return Version(epoch, release, pre_type, pre_number, post_number, dev_number)
