# Copyright 2025 Macéo Tuloup

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from .config import Config
from .display import print_info
from .args_parser import run
from .generation import powermake as powermake_gen
from .utils import _get_run_path, _store_makefile_path


def on_build(config: Config) -> None:
    print_info("Generating default makefile.py", config.verbosity)
    powermake_gen.generate_default_powermake(config, "makefile.py")


def main() -> None:
    os.chdir(_get_run_path())  # For this specific file, we need to revert the chdir done in __init__
    _store_makefile_path("makefile.py")
    run("YOUR_PROGRAM", build_callback=on_build)


if __name__ == "__main__":
    main()
