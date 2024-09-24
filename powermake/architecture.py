# Copyright 2024 Macéo Tuloup

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


def simplify_architecture(architecture: str) -> str:
    arch = architecture.lower()
    if arch in ["x86", "x32", "80x86", "8086", "80386", "i286", "i386", "i486", "i586", "i686", "i786", "amd386", "am386", "amd486", "am486", "amd-k5", "amd-k6", "amd-k7"]:
        return "x86"

    if arch in ["x86_64", "x86-64", "x64", "amd64", "intel64"]:
        return "x64"

    if arch in ["arm32", "arm", "armeabi", "armv4", "armv4t", "armv5", "armv5t", "armv5te", "armv6", "armv6-m", "armv6j", "armv6k", "armv6kz", "armv6t2", "armv6z", "armv6zk", "armv6s-m", "armv7", "armv7a", "armv7s", "armv7m", "armv7r", "armv7l", "armv7-a", "armv7-m", "armv7-r", "armeabi-v7a", "armv7ve", "armv7-r", "armv7-m", "armv7e-m"]:
        return "arm32"

    if arch in ["arm64", "aarch64", "armv8", "armv8-a", "armv8.2-a", "armv8.3-a", "armv8-m", "armv8-r", "armv8.1-a", "armv8.4-a", "armv8.5-a", "armv8.6-a", "armv8-m.base", "armv8-m.main", "armv8.1-m.main", "armv9", "armv9-a", "iwmmxt", "iwmmxt2"]:
        return "arm64"

    return ""
