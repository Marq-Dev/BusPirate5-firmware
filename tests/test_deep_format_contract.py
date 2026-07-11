from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class DeepFormatContractTests(unittest.TestCase):
    def test_parser_exposes_long_flag_query(self):
        header = (ROOT / "src/lib/bp_args/bp_cmd.h").read_text()
        source = (ROOT / "src/lib/bp_args/bp_cmd.c").read_text()
        self.assertIn("bp_cmd_find_long_flag", header)
        self.assertIn("bp_cmd_find_long_flag", source)


if __name__ == "__main__":
    unittest.main()
