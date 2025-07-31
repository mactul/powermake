import powermake
import powermake.compilers

def run_tests():
    for compiler in (powermake.compilers.CompilerGCC(), powermake.compilers.CompilerGPlusPlus(), powermake.compilers.CompilerClang(), powermake.compilers.CompilerClangPlusPlus(), powermake.compilers.CompilerMinGW(), powermake.compilers.CompilerMinGWPlusPlus()):
        assert(compiler.translate_flags(["-Wall", "-Wextra", ('-isystem', '/usr/include')]) == ["-Wall", "-Wextra", "-isystem", "/usr/include"])

        # verify cache
        assert(compiler.translate_flags(["-Wall", "-Wextra", ('-isystem', '/usr/include')]) == ["-Wall", "-Wextra", "-isystem", "/usr/include"])

        assert(compiler.translate_flags(["-Wall", "-Wextra", ('-ispstem', '/usr/include'), "-Wghfvr"]) == ["-Wall", "-Wextra"])

        assert(compiler.translate_flags(["-Wall", "-Wextra", powermake.EnforcedFlag("-fzceggfe")]) == ["-Wall", "-Wextra", powermake.EnforcedFlag("-fzceggfe")])

        if "clang" in compiler.type:
            assert(compiler.translate_flags(["-Weverything"]) == ["-Weverything"])
        else:
            assert(len(compiler.translate_flags(["-Weverything"])) > 5)
