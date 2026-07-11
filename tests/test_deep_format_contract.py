from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class DeepFormatContractTests(unittest.TestCase):
    def test_parser_exposes_long_flag_query(self):
        header = (ROOT / "src/lib/bp_args/bp_cmd.h").read_text()
        source = (ROOT / "src/lib/bp_args/bp_cmd.c").read_text()
        self.assertIn("bp_cmd_find_long_flag", header)
        self.assertIn("bool bp_cmd_find_long_flag", source)
        self.assertIn("tok_eq(name_start, name_len, long_name)", source)

    def test_flow_is_compiled(self):
        cmake = (ROOT / "src/CMakeLists.txt").read_text()
        self.assertIn("commands/global/disk_format_flow.c", cmake)

    def test_nand_layer_exposes_deep_reset(self):
        header = (ROOT / "src/nand/nand_ftl_diskio.h").read_text()
        source = (ROOT / "src/nand/nand_ftl_diskio.c").read_text()
        self.assertIn("diskio_deep_reset_result_t", header)
        self.assertIn("diskio_deep_reset(BYTE drv", header)
        self.assertIn("spi_nand_clear()", source)
        self.assertIn("dhara_map_init(&map", source)
        deep_reset = source[
            source.index("bool diskio_deep_reset"):
            source.index("DSTATUS diskio_status")
        ]
        self.assertNotIn("dhara_map_resume(&map", deep_reset)

    def test_deep_option_is_long_only(self):
        source = (ROOT / "src/commands/global/disk.c").read_text()
        self.assertRegex(
            source,
            re.compile(r'\{\s*"deep"\s*,\s*0\s*,\s*BP_ARG_NONE', re.MULTILINE),
        )
        self.assertNotRegex(source, r'\{\s*"deep"\s*,\s*\'d\'')

    def test_cli_calls_deep_flow_and_preserves_normal_flow(self):
        source = (ROOT / "src/commands/global/disk.c").read_text()
        self.assertIn('bp_cmd_find_long_flag(&disk_format_def, "deep")', source)
        self.assertIn("disk_format_deep_run", source)
        self.assertIn("uint8_t disk_format(void)", source)
        self.assertIn("Deep format is only supported", source)
        self.assertIn("ALL STORAGE DATA AND MAPPING STATE WILL BE ERASED", source)
        self.assertIn("format_status = disk_format()", source)

    def test_deep_failure_does_not_reinsert_usb(self):
        source = (ROOT / "src/commands/global/disk_format_flow.c").read_text()
        insert_at = source.index("ops->insert_usb();")
        mount_failure = source.index("DISK_FORMAT_DEEP_MOUNT_FAILED")
        self.assertGreater(insert_at, mount_failure)

    def test_documentation_exists(self):
        doc = (ROOT / "docs/commands/format-deep.md").read_text()
        self.assertIn("format --deep -y", doc)
        self.assertIn("bad-block markers", doc)


if __name__ == "__main__":
    unittest.main()
