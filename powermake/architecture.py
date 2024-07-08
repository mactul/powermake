# - applexros: arm64 armv7 armv7s i386 x86_64
# - windows: x86 x64 arm64
# - appletvos: arm64 armv7 armv7s i386 x86_64
# - cross: i386 x86_64 arm arm64 mips mips64 riscv riscv64 loong64 s390x ppc ppc64 sh4
# - mingw: i386 x86_64 arm arm64
# - msys: i386 x86_64
# - linux: i386 x86_64 armv7 armv7s arm64-v8a mips mips64 mipsel mips64el loong64
# - harmony: armeabi-v7a arm64-v8a x86 x86_64
# - watchos: armv7k i386
# - wasm: wasm32 wasm64
# - iphoneos: arm64 x86_64
# - haiku: i386 x86_64
# - bsd: i386 x86_64
# - android: armeabi armeabi-v7a arm64-v8a x86 x86_64 mips mip64
# - macosx: x86_64 arm64
# - cygwin: i386 x86_64


def simplify_architecture(architecture: str) -> str:
    arch = architecture.lower()
    if arch in ["x86", "x32", "80x86", "8086", "80386", "i286", "i386", "i486", "i586", "i686", "i786", "amd386", "am386", "amd486", "am486", "amd-k5", "amd-k6", "amd-k7"]:
        return "x86"

    if arch in ["x86_64", "x86-64", "x64", "amd64", "intel64"]:
        return "x64"

    if arch in ["arm32", "arm", "armv6", "armv6-m", "armv7a", "armv7s", "armv7m", "armv7r", "armv7-a", "armv7-m", "armv7-r", "armeabi", "armeabi-v7a"]:
        return "arm32"

    if arch in ["arm64", "armv8-a", "armv8.2-a", "armv8.3-a", "armv8-m", "armv8-r"]:
        return "arm64"

    return None
