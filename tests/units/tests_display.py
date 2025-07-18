import powermake.display
from unittest import mock

class FakePrint:
    def __init__(self):
        self.last_string_printed = ""

    def print(self, string: str):
        self.last_string_printed = string

def run_tests():
    printer = FakePrint()
    with mock.patch("powermake.display.print", new=printer.print):
        powermake.display.print_info("test foo bar", verbosity=0)
        assert("test foo bar" not in printer.last_string_printed)

        powermake.display.print_info("test foo bar", verbosity=1)
        assert("test foo bar" in printer.last_string_printed)

        powermake.display.print_info("test foo bar", verbosity=2)
        assert("test foo bar" in printer.last_string_printed)

        powermake.display.print_info("test foo bar", verbosity=1, step_counter=42)
        assert("[42/-] test foo bar" in printer.last_string_printed)

        powermake.display.print_info("test foo bar", verbosity=1, step_counter=42, step_total=67)
        assert("[42/67] 63% test foo bar" in printer.last_string_printed)

    assert("test foo bar" in powermake.display.warning_text("test foo bar"))
    assert("test foo bar" in powermake.display.error_text("test foo bar"))
    assert("test foo bar" in powermake.display.bold_text("test foo bar"))
    assert("test foo bar" in powermake.display.dim_text("test foo bar"))
