# List of the things to do before next release

- [X] Improve architecture selection. In prior versions of PowerMake, it was really hard to set up the compiler for a specific architecture; sometimes we have to change the environment, sometimes it's just a flag and sometime we have to change the whole compiler. Now PowerMake is mature enough to implement cross compiler selection through architecture.
- [X] Add a MinGW toolchain (should be easy, PowerMake already support MinGW for Windows or when the path is supplied)
- [X] add `config.host_is_windows`, `config.host_is_linux`, etc... I don't know why these methods were not implemented in the first place.