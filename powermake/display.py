import colorama


def init_colors():
    colorama.init()


def print_info(string: str, verbosity: int):
    if verbosity >= 1:
        print(colorama.Fore.LIGHTMAGENTA_EX + str(string) + colorama.Style.RESET_ALL)


def print_debug_info(string: str, verbosity: int):
    if verbosity >= 2:
        print(colorama.Fore.LIGHTBLACK_EX + str(string) + colorama.Style.RESET_ALL)
