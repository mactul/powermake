import os
import shutil
from ..display import hint_text

def update_zshenv() -> None:
    zshenv_lines = []
    try:
        with open(os.path.expanduser("~/.zshenv"), "r") as zshenv:
            zshenv_lines = zshenv.readlines()
    except OSError:
        pass
    for line in reversed(zshenv_lines):
        if line == 'fpath=( ' + os.path.dirname(__file__) + ' "${fpath[@]}" )\n':
            # Up to date !
            return
        if line.endswith('argcomplete/bash_completion.d "${fpath[@]}" )\n'):
            # argcomplete is below powermake or powermake is not installed at all
            break
    with open(os.path.expanduser("~/.zshenv"), "w") as zshenv:
        for line in zshenv_lines:
            if not line.endswith('powermake/zsh_completions "${fpath[@]}" )\n'):
                zshenv.write(line)
        zshenv.write('\n' + 'fpath=( ' + os.path.dirname(__file__) + ' "${fpath[@]}" )\n')

    print(hint_text("zsh completions have been updated, run `exec zsh` to benefit from PowerMake completions."))
    shutil.rmtree(os.path.expanduser("~/.zcompdump"), ignore_errors=True)


if shutil.which("zsh") is not None:
    update_zshenv()