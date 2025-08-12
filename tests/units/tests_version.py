import powermake.version_parser

def run_tests():
    assert(powermake.version_parser.parse_version("v3!2.1.0-a12") > powermake.version_parser.parse_version("v0:2.1.0-a12"))
    assert(powermake.version_parser.parse_version("v2.1.0-a12") == powermake.version_parser.parse_version("v1:2.1.0-a12"))
    assert(powermake.version_parser.parse_version("v2.1.0") > powermake.version_parser.parse_version("v1:2.1.0-a12"))
    assert(powermake.version_parser.parse_version("v2.1.0-post1") > powermake.version_parser.parse_version("v1:2.1.0"))

    assert(powermake.version_parser.remove_version_frills("15.1.1+r500+gb1b8d8ce3eea-1") == "15.1.1-1")
    assert(powermake.version_parser.remove_version_frills("15.1.1+alpha1+gb1b8d8ce3eea-1") == "15.1.1+alpha1-1")
    assert(powermake.version_parser.remove_version_frills("6.15.9.zen1-1") == "6.15.9-1")
    assert(powermake.version_parser.remove_version_frills("6.15.9.hardened1-1") == "6.15.9-1")
