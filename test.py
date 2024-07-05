import powermake


config = powermake.Config()

files = powermake.get_files("*.c", "*.cpp")


objects = powermake.compile_files(files, config)

print(powermake.link_files("program_test", objects, config))
