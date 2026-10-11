import unittest

from tests.helpers import FakeRunner  # noqa: F401  (ajusta sys.path)
from salesforce_docs.errors import GlobalFailure
from salesforce_docs.validation.cli_validator import (is_version_at_least, parse_cli_version,
                                                      validate_cli)


class CliValidatorTest(unittest.TestCase):
    def test_parse_version(self):
        self.assertEqual(parse_cli_version("@salesforce/cli/2.61.8 linux-x64 node-v20.17.0"), "2.61.8")
        self.assertIsNone(parse_cli_version("sfdx-cli/7.209.6 linux-x64"))

    def test_compare(self):
        self.assertTrue(is_version_at_least("2.0.0", "2.0.0"))
        self.assertTrue(is_version_at_least("2.10.1", "2.9.9"))
        self.assertFalse(is_version_at_least("1.99.0", "2.0.0"))

    def test_cli_below_minimum_fails(self):
        runner = FakeRunner({"--version": (0, "@salesforce/cli/1.99.0 linux-x64 node-v18.0.0\n")})
        with self.assertRaises(GlobalFailure) as ctx:
            validate_cli(runner, "2.0.0")
        self.assertEqual(ctx.exception.code, "CLI_VERSION_TOO_LOW")

    def test_cli_ok(self):
        runner = FakeRunner({"--version": (0, "@salesforce/cli/2.60.0 linux-x64 node-v20.11.0\n")})
        self.assertEqual(validate_cli(runner, "2.0.0"), "2.60.0")


if __name__ == "__main__":
    unittest.main()
