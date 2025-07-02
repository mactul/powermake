################################################################
# This program is used to visualize all GCC warnings and which #
#   one is enabled by our custom `-Weverything` translation    #
################################################################

import shutil
import subprocess
import powermake.compilers

compiler = powermake.compilers.CompilerGCC()

ps = subprocess.Popen([compiler.path, *compiler.translate_flags(["-Weverything"]), "-Q", "--help=warning"], stdout=subprocess.PIPE)

subprocess.run(f"""{shutil.which("sed") or "sed"} -e s/'\\[disabled\\]'/`printf "[\\033[31mdisabled\\033[0m]"`/g -e s/'\\[enabled\\]'/`printf "[\\033[32menabled\\033[0m]"`/g""", shell=True, stdin=ps.stdout)