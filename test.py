import blazymake


config = blazymake.Config()

files = blazymake.get_files("*.c", "*.cpp")


objects = blazymake.compile_files(files, config)

print(blazymake.link_files("program_test", objects, config))
