"""Regression tests for the AT24C02 preliminary-round platform.

The suite intentionally exercises the protocol and export core without opening
a GUI.  It uses only Python's standard-library ``unittest`` framework so that
contributors can run it with the same interpreter used by the application.
"""

from __future__ import annotations

import contextlib
import io
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from at24c02_pat_generator import (
    TEST_PINS,
    I2CTimingChecker,
    I2CVectorGenerator,
    PATFormatter,
    ShmooEngine,
    VectorProtocolValidator,
)
from generate_samples import generate_all_files


class I2CVectorGeneratorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.generator = I2CVectorGenerator(addr_pins=(1, 0, 1), wp_pin=1)

    def test_start_condition_is_sda_falling_while_scl_stays_high(self) -> None:
        self.generator.add_start_condition()

        self.assertEqual(len(self.generator.vectors), 3)
        self.assertEqual(
            [(v["SDA"], v["SCL"]) for v in self.generator.vectors],
            [("1", "1"), ("0", "1"), ("0", "0")],
        )
        self.assertEqual(
            [(v["A0"], v["A1"], v["A2"], v["WP"]) for v in self.generator.vectors],
            [("1", "0", "1", "1")] * 3,
        )

    def test_stop_condition_is_sda_rising_while_scl_stays_high(self) -> None:
        self.generator.add_stop_condition()

        self.assertEqual(len(self.generator.vectors), 4)
        self.assertEqual(
            [(v["SDA"], v["SCL"]) for v in self.generator.vectors],
            [("0", "0"), ("0", "1"), ("0", "1"), ("1", "1")],
        )

    def test_write_byte_is_msb_first_with_four_vectors_per_bit(self) -> None:
        self.generator.add_write_byte(0xA5)

        self.assertEqual(len(self.generator.vectors), 8 * 4)
        self.assertEqual(
            [self.generator.vectors[offset]["SDA"] for offset in range(0, 32, 4)],
            list("10100101"),
        )
        for offset in range(0, 32, 4):
            phase = self.generator.vectors[offset : offset + 4]
            self.assertEqual([v["SCL"] for v in phase], list("0110"))
            self.assertEqual(len({v["SDA"] for v in phase}), 1)

    def test_slave_ack_releases_sda_then_compares_low(self) -> None:
        self.generator.add_ack_from_slave()

        self.assertEqual(len(self.generator.vectors), 4)
        self.assertEqual(
            [(v["SDA"], v["SCL"]) for v in self.generator.vectors],
            [("X", "0"), ("L", "1"), ("L", "1"), ("X", "0")],
        )


class ProtocolValidationTests(unittest.TestCase):
    def test_valid_minimal_transaction_has_no_protocol_issue(self) -> None:
        generator = I2CVectorGenerator()
        generator.add_idle()
        generator.add_start_condition()
        generator.add_write_byte(0xA0)
        generator.add_ack_from_slave()
        generator.add_stop_condition()
        generator.add_idle()

        issue_count, issues = VectorProtocolValidator.validate(
            generator.vectors, generator.comments
        )

        self.assertEqual(issue_count, 0)
        self.assertEqual(issues[0]["rule"], "SUMMARY")

    def test_sda_change_during_scl_rising_phase_is_reported(self) -> None:
        vectors = [
            {"SDA": "0", "SCL": "0"},
            {"SDA": "1", "SCL": "1"},
        ]

        issue_count, issues = VectorProtocolValidator.validate(vectors, ["", ""])

        self.assertGreaterEqual(issue_count, 1)
        self.assertIn(
            "SDA_CHANGE_ON_SCL_HIGH",
            {issue["rule"] for issue in issues},
        )


class PATFormatterTests(unittest.TestCase):
    def setUp(self) -> None:
        generator = I2CVectorGenerator()
        generator.add_idle(2)
        self.vectors = generator.vectors
        self.comments = generator.comments
        self.labels = generator.labels

    def test_pat_header_and_pattern_delimiters_match_estar_contract(self) -> None:
        header = PATFormatter.generate_pat_header("SMOKE", "Smoke test", TEST_PINS)
        body = PATFormatter.format_vectors(
            self.vectors, self.comments, self.labels, TEST_PINS, "SMOKE"
        )
        pat = f"{header}\n{body}"

        self.assertIn("HEAD[PIN_NAME]:", pat)
        self.assertIn("END_HEAD;", pat)
        pin_block = pat.split("HEAD[PIN_NAME]:", 1)[1].split("END_HEAD;", 1)[0]
        self.assertEqual(re.findall(r"\b(?:A[012]|WP|SCL|SDA)\b", pin_block), TEST_PINS)
        self.assertEqual(pat.count("@@PATTERN_DEFINE"), 1)
        self.assertEqual(pat.count("@@END_PATTERN_DEFINE"), 1)
        self.assertRegex(pat, r"(?m)^start:\s+[01HLXZ]{6};AC_SET 1;$")
        self.assertRegex(pat, r"(?m)^end:\s+[01HLXZ]{6};")
        self.assertEqual(pat.count("AC_SET 1;"), 1)

    def test_tim_lvl_and_prg_exports_contain_required_blocks(self) -> None:
        timing = PATFormatter.generate_tim_file(period_ns=2500, voltage_key="5.0V")
        levels = PATFormatter.generate_lvl_file()
        sections = [
            (
                "FUNC_TEST",
                "Functional smoke test",
                self.vectors,
                self.comments,
                self.labels,
            )
        ]
        program = PATFormatter.generate_prg_file(sections, period_ns=2500)

        for marker in ("@@TIMING_DEFINE", "@@AC_SET_1", "@@END_AC_SET_1"):
            self.assertIn(marker, timing)
        self.assertIn("PERIOD =   2500ns;", timing)
        self.assertIn("{DRV_LE = 0ns}", timing)
        self.assertIn("{DRV_TE = 1250ns}", timing)
        self.assertIn("{STB    = 1875ns}", timing)

        expected_level_sets = {
            "DC_0V_PWR",
            "DC_5_0V_LVL",
            "DC_IIH_IIL_LVL",
            "DC_IDD",
            "PWR_OFF",
        }
        self.assertEqual(
            set(re.findall(r"^@@LEVEL_SET_DEFINE\s+(\S+)", levels, re.MULTILINE)),
            expected_level_sets,
        )
        self.assertEqual(levels.count("@@END_LEVEL_SET"), len(expected_level_sets))

        for marker in (
            "@@SCHEDULE AT24C02_FULL_TEST",
            "@@END_SCHEDULE",
            "@@EOT",
            "@@END_EOT",
            "@@PLAN    Functional",
            "@@END_PLAN",
        ):
            self.assertIn(marker, program)
        self.assertIn(
            "RUN_PATTERN(AT24C02_FULL_TEST_FUNC:start,"
            "AT24C02_FULL_TEST_FUNC:end,1,LOG_ALIAS=FTR_Functional);",
            program,
        )


class TimingCheckerTests(unittest.TestCase):
    def test_four_vector_model_matches_generated_scl_waveform(self) -> None:
        passed, results = I2CTimingChecker.check(2500, "5.0V")
        by_parameter = {result["param"]: result for result in results}

        self.assertTrue(passed)
        self.assertEqual(by_parameter["fSCL"]["actual"], "100.0 kHz")
        self.assertEqual(by_parameter["tLOW"]["actual"], "5000 ns")
        self.assertEqual(by_parameter["tHIGH"]["actual"], "5000 ns")
        self.assertEqual(by_parameter["tSU,STO"]["actual"], "5000 ns")
        self.assertIn("4向量/bit", by_parameter["fSCL"]["note"])

    def test_recommended_periods_pass_all_eight_i2c_checks(self) -> None:
        for period_ns, voltage in ((2500, "5.0V"), (10000, "1.8V")):
            with self.subTest(period_ns=period_ns, voltage=voltage):
                passed, results = I2CTimingChecker.check(period_ns, voltage)
                self.assertTrue(passed)
                self.assertEqual(len(results), 8)
                self.assertTrue(all(result["passed"] for result in results))

    def test_period_below_datasheet_limits_fails(self) -> None:
        passed, results = I2CTimingChecker.check(100, "5.0V")

        self.assertFalse(passed)
        failed_parameters = {
            result["param"] for result in results if not result["passed"]
        }
        self.assertTrue({"fSCL", "tLOW", "tHIGH"}.issubset(failed_parameters))

    def test_i2c_shmoo_frequency_converts_to_four_vector_period(self) -> None:
        engine = ShmooEngine()
        result = engine.evaluate_point("5.0V", 100, protocol="I2C")
        frequency = next(
            item for item in result["timing_details"] if item["param"] == "fSCL"
        )

        self.assertEqual(frequency["actual"], "100.0 kHz")
        engine.configure_sweep(["5.0V"], [100])
        engine.run_sweep(None, protocol="I2C")
        self.assertEqual(engine.results[("5.0V", 100)]["period_ns"], 2500)


class SecurityConfigurationTests(unittest.TestCase):
    def test_deepseek_endpoint_never_uses_openai_api_key_environment_variable(
        self,
    ) -> None:
        source = (ROOT / "at24c02_pat_generator.py").read_text(encoding="utf-8")

        self.assertIn('API_URL       = "https://api.deepseek.com/', source)
        self.assertIn('os.environ.get("DEEPSEEK_API_KEY", "")', source)
        self.assertNotIn('os.environ.get("OPENAI_API_KEY", "")', source)


class SampleGenerationSmokeTests(unittest.TestCase):
    def test_batch_cli_generates_without_starting_gui(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "at24c02_pat_generator.py"),
                    "--batch",
                    "--chip",
                    "AT24C02",
                    "--tests",
                    "os",
                    "--format",
                    "pat",
                    "--output",
                    temporary_directory,
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
                timeout=30,
            )

            self.assertEqual(
                completed.returncode,
                0,
                msg=f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}",
            )
            self.assertIn("Batch Mode", completed.stdout)
            generated_names = {
                path.name for path in Path(temporary_directory).iterdir()
            }
            self.assertTrue(
                {
                    "AT24C02_FULL_TEST.pat",
                    "AT24C02_OS_TEST.pat",
                    "AT24C02_TEST.tim",
                    "AT24C02_TEST.lvl",
                    "AT24C02_TEST.prg",
                }.issubset(generated_names)
            )

    def test_headless_sample_generation_writes_complete_ate_package(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_directory = Path(temporary_directory)
            with contextlib.redirect_stdout(io.StringIO()):
                generate_all_files(output_directory)

            required_files = {
                "AT24C02_FULL_TEST.pat",
                "AT24C02_FULL_TEST_preview.txt",
                "AT24C02_FULL_TEST.prg",
                "AT24C02_FULL_TEST_stats.csv",
                "AT24C02_timing.tim",
                "AT24C02_level.lvl",
                "AT24C02_OS_TEST.pat",
                "AT24C02_DC_TEST.pat",
                "AT24C02_FUNC_BW.pat",
                "AT24C02_MARCH_TEST.pat",
                "AT24C02_SCAN_TEST.pat",
                "AT24C02_RET_TEST.pat",
                "AT24C02_ERR_TEST.pat",
                "AT24C02_ENDUR_TEST.pat",
            }
            generated_names = {path.name for path in output_directory.iterdir()}
            self.assertTrue(required_files.issubset(generated_names))
            self.assertGreaterEqual(len(generated_names), 40)

            combined_pat = (output_directory / "AT24C02_FULL_TEST.pat").read_text(
                encoding="utf-8"
            )
            self.assertEqual(combined_pat.count("@@PATTERN_DEFINE"), 1)
            self.assertEqual(combined_pat.count("@@END_PATTERN_DEFINE"), 1)
            self.assertIn("// SECTION_COUNT  = 14", combined_pat)
            self.assertRegex(combined_pat, r"// VECTOR_COUNT\s+=\s+[1-9]\d+")
            self.assertRegex(combined_pat, r"// MD5_CHECKSUM\s+=\s+[0-9A-F]{32}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
