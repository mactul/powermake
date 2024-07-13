# This script is not used for the moment but it should become a tool to help creating the json configuration.

def dp(string: str):
    if string is None:
        return "Let the program decide"
    return string


def multiple_choices(question: str, choices: list[str], values: list[str] = None):
    if values is None:
        values = choices
    assert len(choices) == len(values)

    answer = None
    while answer not in range(1, len(choices)+1):
        print("\033[H\033[2J", end="")
        print(question)
        for i in range(1, len(choices)+1):
            print(f"[{i}]: {dp(choices[i-1])}")
        answer = input(f"{' '.join([str(i) for i in range(1, len(choices)+1)])}: ")
        if answer.isnumeric():
            answer = int(answer)

    return values[answer-1]


class InteractiveConfig:
    target_architecture = None
    c_compiler = None

    def __init__(self):
        answer = 0
        while answer < 4:
            choices = [
                f"Architecture ({dp(self.target_architecture)})",
                "Compilers",
                "Build directories\n",
                "Save configuration",
                "Exit without saving"
            ]
            answer = multiple_choices("What do you want to configure ?", choices, range(1, len(choices)+1))

            if answer == 1:
                self.target_architecture = multiple_choices("Select the target architecture", [None, "x86", "x64", "arm32", "arm64"])


if __name__ == "__main__":
    InteractiveConfig()
