import os

from .. import Config
from ..utils import makedirs, handle_filename_conflict

__default_powermake = """import powermake

def on_build(config: powermake.Config):
    config.add_flags("-Wall", "-Wextra")

    config.add_includedirs("./")

    files = powermake.get_files("**/*.c",
        "**/*.cpp", "**/*.cc", "**/*.C",
        "**/*.asm", "**/*.s", "**/*.rc")

    objects = powermake.compile_files(config, files)

    powermake.link_files(config, objects)

powermake.run("my_project", build_callback=on_build)
"""


def generate_default_powermake(config: Config, makefile_path: str) -> None:

    makefile_path = handle_filename_conflict(makefile_path, config._args_parsed.always_overwrite)
    if makefile_path == "":
        return

    makedirs(os.path.dirname(makefile_path))

    template_path = os.path.join(config.global_config_dir, "default_powermake.py")

    if not os.path.exists(template_path):
        makedirs(config.global_config_dir)
        with open(template_path, "w") as file:
            file.write(__default_powermake)
        content = __default_powermake
    else:
        with open(template_path, "r") as file:
            content = file.read()

    with open(makefile_path, "w") as file:
        file.write(content)