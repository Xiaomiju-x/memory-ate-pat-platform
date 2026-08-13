from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import by25q40al_pat_generator as pat


class AddressAndPatternTests(unittest.TestCase):
    def test_address_parsing_and_page_alignment(self) -> None:
        self.assertEqual(pat.parse_address("000003h"), 3)
        self.assertEqual(pat.parse_address("0x07ffff"), pat.MAX_ADDRESS)
        self.assertEqual(pat.align_write_range("000003h", "0001F1h"), (0, 0x1FF))
        with self.assertRaises(ValueError):
            pat.parse_address("080000h")

    def test_core_data_algorithms(self) -> None:
        self.assertEqual(
            [pat.pattern_byte("mode_2", i) for i in range(4)], [0xAA, 0x55, 0xAA, 0x55]
        )
        self.assertEqual(
            [pat.pattern_byte("mode_3", i) for i in range(8)],
            [1, 2, 4, 8, 16, 32, 64, 128],
        )
        self.assertEqual(
            [pat.pattern_byte("mode_4", i) for i in range(8)],
            [0xFE, 0xFD, 0xFB, 0xF7, 0xEF, 0xDF, 0xBF, 0x7F],
        )
        self.assertEqual(pat.galpat_byte(0x100, 0x100), 0x80)
        self.assertEqual(pat.galpat_byte(0x101, 0x100), 0x00)

    def test_stable_output_names(self) -> None:
        self.assertEqual(
            pat.memory_output_names("QUAD"),
            ("QUAD_MEMORY_ERASE_CHECK.pat", "QUAD_MEMORY_PROGRAM_READ.pat"),
        )


class WriterAndValidatorTests(unittest.TestCase):
    def test_writer_enforces_start_and_end_contract(self) -> None:
        import io

        output = io.StringIO()
        writer = pat.EStarPATWriter(output, "public-test")
        writer.start(pat.SPIEmitter.NORMAL_IDLE)
        writer.close(pat.SPIEmitter.NORMAL_IDLE)
        report = pat.PATValidator.validate_text(output.getvalue())
        self.assertTrue(report.ok, report.errors)
        self.assertIn("start:", output.getvalue())
        self.assertIn("AC_SET 1;", output.getvalue())
        self.assertIn("end:", output.getvalue())

    def test_validator_rejects_bad_state(self) -> None:
        text = """HEAD[PIN_NAME]:
CS_N,
SO_IO1,
WP_IO2,
SI_IO0,
SCLK,
HOLD_IO3;
END_HEAD;
@@PATTERN_DEFINE
start:              1Z1001; AC_SET 1;
end:                1X1001;
@@END_PATTERN_DEFINE
"""
        self.assertFalse(pat.PATValidator.validate_text(text).ok)


class EndToEndTests(unittest.TestCase):
    def test_clean_room_generation_for_all_buses(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            for bus in pat.BUS_SPECS:
                with self.subTest(bus=bus):
                    result = pat.BY25Q40ALPatternGenerator().generate(
                        root / bus, "mode_1", bus, "000003h", "00000Fh"
                    )
                    self.assertTrue(result.erase_validation.ok)
                    self.assertTrue(result.program_validation.ok)
                    self.assertEqual(result.program_stats.page_count, 1)
                    self.assertEqual(result.program_stats.compared_bytes, 13)
                    for output in result.paths:
                        self.assertTrue(output.is_file())
                        self.assertTrue(pat.PATValidator.validate_file(output).ok)

    def test_checkerboard_has_one_wip_check_per_page(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            destination = Path(temp_dir) / "checkerboard.pat"
            stats, report, write_range = (
                pat.BY25Q40ALPatternGenerator().generate_program_pat(
                    destination, "mode_2", "SPI", "000003h", "0001F1h"
                )
            )
            self.assertTrue(report.ok, report.errors)
            self.assertEqual(write_range, (0, 0x1FF))
            self.assertEqual(stats.page_count, 2)
            text = destination.read_text(encoding="utf-8")
            self.assertEqual(text.count("Post-program WIP check for page"), 2)
            pat._verify_standard_checkerboard_wip_contract(text, 2)

    def test_source_has_no_private_asset_fingerprints(self) -> None:
        source = Path(pat.__file__).read_text(encoding="utf-8")
        forbidden = (
            "_MEMORY_HASHES",
            "_FUNC_HASHES",
            "golden_templates",
            "func_templates",
            "赛方示例",
            "逐字节复制",
        )
        for marker in forbidden:
            with self.subTest(marker=marker):
                self.assertNotIn(marker, source)


if __name__ == "__main__":
    unittest.main()
