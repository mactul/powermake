import tests_utils
import tests_cache
import tests_config
import tests_display
import tests_exceptions
import tests_architecture
import tests_compile_commands
import tests_flags_translation
import tests_interactive_config


if __name__ == "__main__":
    tests_utils.run_tests()
    tests_cache.run_tests()
    tests_config.run_tests()
    tests_display.run_tests()
    tests_exceptions.run_tests()
    tests_architecture.run_tests()
    tests_compile_commands.run_tests()
    tests_flags_translation.run_tests()
    tests_interactive_config.run_tests()