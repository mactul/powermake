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
    """
    Remove everything that will not be understand by the version parser.  
    For example Linux-6.12.3-hardened-1 will be transformed in 6.12.3-1.

    Please pay attention that not_a_release_3 will be transformed in "3",
    which will be interpreted as the version 3.
    """
    separators = ('.', '-', '+', ':', '!', '_')
    output = ""
    i = 0
    marker = 0
    while i < len(string):
        if string[i] in separators:
            if len(output) == 0 and string[marker+1 if marker > 0 else 0: i] in ("pre", "prerelease", "candidate", "preview") or re.fullmatch(f"{'v?(pre|prerelease|candidate|preview)?' if len(output) == 0 else ''}([0-9]+|\\*)|(([0-9]+|\\*)?(alpha|beta|a|b|rc|post|p|develop|dev|d)([0-9]+|\\*)?)", string[marker+1 if string[marker] in separators else 0: i], re.IGNORECASE):
                if len(output) == 0 and string[marker] in separators:
                    output += string[marker+1:i]
                else:
                    output += string[marker:i]
            marker = i
        i += 1
    if i == 0:
        return ""
    if len(output) == 0 and string[marker+1 if marker > 0 else 0: i] in ("pre", "prerelease", "candidate", "preview") or re.fullmatch(f"{'v?(pre|prerelease|candidate|preview)?' if len(output) == 0 else ''}([0-9]+|\\*)|(([0-9]+|\\*)?(alpha|beta|a|b|rc|post|p|develop|dev|d)([0-9]+|\\*)?)", string[marker+1 if string[marker] in separators else 0: i], re.IGNORECASE):
        if len(output) == 0 and string[marker] in separators:
            output += string[marker+1:i]
        else:
            output += string[marker:i]
    return output


def parse_version(string: str) -> T.Union[Version, None]:
    """
    Transform a version string in the corresponding Version object.  
    The version should not have any frills or the function will return None,
    for example `foo-1.1.1` will be rejected and will return None.  
    You can call `remove_version_frills` prior to this function to remove
    everything that is not related to the function number.  
    However, keep in mind that a random string containing isolated numbers
    can become a valid version because of remove_version_frills.

    The version can start with the letter v, like `v1.2.3`.

    Parameters
    ----------
    string : str
        A large variety of formats are accepted, however the base format
        that this function is meant to parse is PEP-440.

    Returns
    -------
    T.Union[Version, None]
        A version object or None if the version format was not valid.
    """
    if "." not in string:
        # Some versionning schemes uses _ or - instead of .
        # Example: OpenSSL_1_1_1
        underscore_pos = string.find("_")
        dash_pos = string.find("-")
        if dash_pos != -1 and (underscore_pos == -1 or dash_pos < underscore_pos):
            string = string.replace('-', '.')
        elif underscore_pos != -1 and (dash_pos == -1 or underscore_pos < dash_pos):
            string = string.replace('_', '.')

    extended_number_regex = "[0-9]+|\\*"
    separator_regex = "(?:\\.|-|\\+|:|_)"
    pre_regex_prefix = f"(?:(pre|prerelease|candidate|preview){separator_regex}?)"
    epoch_regex = f"(?:({extended_number_regex})(?:!|:|-|_))"
    release_regex = f"((?:{extended_number_regex})(?:\\.(?:{extended_number_regex}))*)"
    pre_regex_suffix = f"(?:{separator_regex}?(alpha|beta|a|b|r|rc){separator_regex}?({extended_number_regex}))"
    post_regex = f"(?:{separator_regex}?(?:post|p|{separator_regex}){separator_regex}?({extended_number_regex}))"
    dev_regex = f"(?:{separator_regex}?(?:develop|dev|d){separator_regex}?({extended_number_regex}))"
    search = re.fullmatch(f'(?:v|v{separator_regex})?{pre_regex_prefix}?{epoch_regex}?{release_regex}{pre_regex_suffix}?{post_regex}?{dev_regex}?', string, re.IGNORECASE)
    if not search:
        return None

    epoch = '1'
    release: T.Tuple[str, ...] = ('0', )
    pre_type = PreType.NOT_PRE
    pre_number: T.Union[str, None] = None
    post_number: T.Union[str, None] = None
    dev_number: T.Union[str, None] = None

    match_prerelease = search.group(1)
    match_epoch = search.group(2)
    match_release = search.group(3)
    match_pre_type = search.group(4)
    match_pre_number = search.group(5)
    match_post_number = search.group(6)
    match_dev_number = search.group(7)

    if match_prerelease is not None:
        # We choose to give pre- and preview- the alpha prerelease type
        # While prerelease- is given the beta prerelease type.
        # This is based on the SDL formatting scheme where
        # preview < prerelease < candidate < release
        # On other versionning schemes, pre- refers to just a prerelease
        # in general so that's why we choose to give alpha for pre-.
        # The mix is not a big deal as long as we can compare 2 versions
        # of the same versionning scheme.
        if match_prerelease == "candidate":
            pre_type = PreType.RELEASE_CANDIDATE
            pre_number = '1'
        elif match_prerelease == "prerelease":
            pre_type = PreType.BETA
            pre_number = '1'
        else:
            pre_type = PreType.ALPHA
            pre_number = '1'

    if match_epoch is not None:
        epoch = str(match_epoch)

    if match_release is not None:
        release = tuple(str(match_release).split('.'))

    if not match_prerelease or match_pre_type is not None:
        if match_pre_type is None:
            pre_type = PreType.NOT_PRE
        elif match_pre_type.startswith(('a', 'A')):
            pre_type = PreType.ALPHA
        elif match_pre_type.startswith(('b', 'B')):
            pre_type = PreType.BETA
        elif match_pre_type.startswith(('r', 'R')):
            pre_type = PreType.RELEASE_CANDIDATE
        else:
            return None  # can not happen

        if match_pre_number is not None:
            pre_number = str(match_pre_number)

    if match_post_number is not None:
        post_number = str(match_post_number)

    if match_dev_number is not None:
        dev_number = str(match_dev_number)

    return Version(epoch, release, pre_type, pre_number, post_number, dev_number)
