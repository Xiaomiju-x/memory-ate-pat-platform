#!/usr/bin/env python3
"""Generate the headless AT24C02 sample package in EStar-style formats.

The nine primary test families expand to 14 exported sections because the
functional family is split into six independently inspectable PAT files.
"""

import datetime
import hashlib
import os
import sys

# Make the project modules importable when this script is launched directly.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from at24c02_pat_generator import (
    TEST_PINS,
    VERSION,
    PATFormatter,
    TestPatternGenerator,
)


def generate_all_files(output_dir):
    """Generate all 14 export sections across nine primary test families."""
    os.makedirs(output_dir, exist_ok=True)

    # Default address pins are low; WP=0 enables writes.
    gen = TestPatternGenerator(addr_pins=(0, 0, 0), wp=0)
    fmt = PATFormatter()

    sections = []

    # 1. Open/short continuity.
    v, c, l = gen.generate_os_test()
    sections.append(("OS_TEST", "Open/Short Continuity Test", v, c, l))

    # 2. DC parametric tests.
    v, c, l = gen.generate_dc_test()
    sections.append(("DC_TEST", "DC Parameter Test", v, c, l))

    # 3. Functional tests, split into six standalone PAT sections.
    v, c, l = gen.generate_func_byte_write(custom_addr=0x30, custom_data=0xA5)
    sections.append(("FUNC_BW", "Byte Write + Read", v, c, l))

    v, c, l = gen.generate_func_page_write()
    sections.append(("FUNC_PW", "Page Write + Read", v, c, l))

    v, c, l = gen.generate_func_boundary()
    sections.append(("FUNC_BOUND", "Address Boundary", v, c, l))

    v, c, l = gen.generate_func_wp_test()
    sections.append(("FUNC_WP", "WP Protect Test", v, c, l))

    v, c, l = gen.generate_func_page_wrap()
    sections.append(("FUNC_WRAP", "Page Wrap Test", v, c, l))

    v, c, l = gen.generate_func_current_read()
    sections.append(("FUNC_CAR", "Current Address Read", v, c, l))

    # 4. March C- memory test over 0x00..0x07 (8 bytes).
    v, c, l = gen.generate_march_c_test(start_addr=0x00, count=8)
    sections.append(("MARCH_TEST", "March C- Memory Test", v, c, l))

    # 5. March B memory test over 0x00..0x07 (8 bytes).
    v, c, l = gen.generate_march_b_test(start_addr=0x00, count=8)
    sections.append(("MARCHB_TEST", "March B Memory Test", v, c, l))

    # 6. Address-space scan.
    v, c, l = gen.generate_addr_scan_test(start_addr=0x00, end_addr=0x07)
    sections.append(("SCAN_TEST", "Address Space Scan Test", v, c, l))

    # 7. Data-retention test.
    v, c, l = gen.generate_data_retention_test(start_addr=0x00, count=8)
    sections.append(("RET_TEST", "Data Retention Test", v, c, l))

    # 8. I2C error and boundary tests.
    v, c, l = gen.generate_i2c_error_test()
    sections.append(("ERR_TEST", "I2C Error/Boundary Test", v, c, l))

    # 9. Write-endurance test.
    v, c, l = gen.generate_endurance_test(test_addr=0x70, cycles=10)
    sections.append(("ENDUR_TEST", "Write Endurance Test", v, c, l))

    period_ns = 2500
    total_vectors = sum(len(s[2]) for s in sections)

    # Combined PAT: one EStar @@PATTERN_DEFINE block.
    combined_pat = fmt.generate_pat_header(
        "AT24C02_FULL_TEST",
        "AT24C02 Complete Test (All 9 Test Types)",
        TEST_PINS
    )
    combined_pat += "\n"
    combined_pat += "@@PATTERN_DEFINE  \n"
    combined_pat += f"// {','.join(TEST_PINS)}\n\n"

    for i, (name, desc, vectors, comments, labels) in enumerate(sections):
        combined_pat += f"// {'='*60}\n"
        combined_pat += f"// {desc}\n"
        combined_pat += f"// {'='*60}\n"
        combined_pat += fmt.format_vector_body(
            vectors, comments, labels, TEST_PINS, name,
            is_first_section=(i == 0)
        )

    combined_pat += "@@END_PATTERN_DEFINE\n"

    # Append reproducibility metadata and an integrity checksum.
    md5 = hashlib.md5(combined_pat.encode("utf-8")).hexdigest().upper()
    combined_pat += f"\n// {'='*60}\n"
    combined_pat += "// INTEGRITY CHECK\n"
    combined_pat += f"// {'='*60}\n"
    combined_pat += f"// VECTOR_COUNT   = {total_vectors}\n"
    combined_pat += f"// SECTION_COUNT  = {len(sections)}\n"
    combined_pat += f"// MD5_CHECKSUM   = {md5}\n"
    combined_pat += f"// GENERATED_BY   = AT24C02 PAT Generator {VERSION}\n"
    combined_pat += f"// {'='*60}\n"

    pat_path = os.path.join(output_dir, "AT24C02_FULL_TEST.pat")
    with open(pat_path, "w", encoding="utf-8") as f:
        f.write(combined_pat)
    print(f"  [PAT] {pat_path}")

    # Combined human-readable TXT preview.
    combined_txt = ""
    for name, desc, vectors, comments, labels in sections:
        combined_txt += fmt.format_txt_preview(vectors, comments, TEST_PINS, desc)
        combined_txt += "\n\n"

    txt_path = os.path.join(output_dir, "AT24C02_FULL_TEST_preview.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(combined_txt)
    print(f"  [TXT] {txt_path}")

    # EStar project files: PRG, timing and levels.
    prg_content = fmt.generate_prg_file(sections, period_ns=period_ns)
    prg_path = os.path.join(output_dir, "AT24C02_FULL_TEST.prg")
    with open(prg_path, "w", encoding="utf-8") as f:
        f.write(prg_content)
    print(f"  [PRG] {prg_path}")

    tim_content = fmt.generate_tim_file(period_ns, "5.0V")
    tim_path = os.path.join(output_dir, "AT24C02_timing.tim")
    with open(tim_path, "w", encoding="utf-8") as f:
        f.write(tim_content)
    print(f"  [TIM] {tim_path}")

    lvl_content = fmt.generate_lvl_file()
    lvl_path = os.path.join(output_dir, "AT24C02_level.lvl")
    with open(lvl_path, "w", encoding="utf-8") as f:
        f.write(lvl_content)
    print(f"  [LVL] {lvl_path}")

    # CSV vector and estimated-time summary.
    csv_lines = ["Test Segment,Description,Vectors,Percentage,Vector Time (ms),Write Ops,tWR Wait (ms),Total Time (ms)"]
    for name, desc, vectors, comments, _ in sections:
        cnt = len(vectors)
        pct = cnt / total_vectors * 100 if total_vectors else 0
        vec_ms = cnt * period_ns / 1_000_000
        writes = sum(1 for cm in comments
                     if cm and ("ACK Polling" in cm or "Poll #1" in cm))
        twr_ms = writes * 5.0
        csv_lines.append(f"{name},{desc},{cnt},{pct:.1f}%,{vec_ms:.2f},{writes},{twr_ms:.0f},{vec_ms + twr_ms:.2f}")
    total_vec_ms = total_vectors * period_ns / 1_000_000
    all_writes = sum(
        sum(1 for cm in s[3] if cm and ("ACK Polling" in cm or "Poll #1" in cm))
        for s in sections
    )
    csv_lines.append(f"TOTAL,All Segments,{total_vectors},100%,{total_vec_ms:.2f},{all_writes},{all_writes*5.0:.0f},{total_vec_ms+all_writes*5.0:.2f}")
    csv_lines.append(f"\nPeriod (ns),{period_ns}")
    csv_lines.append(f"Generated,{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    csv_lines.append(f"Tool,AT24C02 PAT Generator {VERSION}")

    csv_path = os.path.join(output_dir, "AT24C02_FULL_TEST_stats.csv")
    with open(csv_path, "w", encoding="utf-8-sig") as f:
        f.write("\n".join(csv_lines))
    print(f"  [CSV] {csv_path}")

    # Export each test section as an independent EStar pattern.
    for name, desc, vectors, comments, labels in sections:
        # Split ACK polling into its own pattern.
        (main_v, main_c, main_l), (poll_v, poll_c, poll_l) = \
            PATFormatter.split_ack_polling(vectors, comments, labels)

        # In the main file, replace the polling block with idle placeholders.
        seg_pat = fmt.generate_pat_header(name, desc, TEST_PINS)
        seg_pat += "\n"
        seg_pat += fmt.format_vectors(main_v, main_c, main_l, TEST_PINS, name)

        seg_path = os.path.join(output_dir, f"AT24C02_{name}.pat")
        with open(seg_path, "w", encoding="utf-8") as f:
            f.write(seg_pat)
        print(f"  [PAT] {seg_path}")

        # Write a standalone ACK-polling file when the section contains one.
        if poll_v:
            poll_name = f"{name}_ACK_POLL"
            poll_pat = fmt.generate_pat_header(
                poll_name, f"{desc} - ACK Polling", TEST_PINS)
            poll_pat += "\n"
            poll_pat += fmt.format_vectors(
                poll_v, poll_c, poll_l, TEST_PINS, poll_name)
            poll_path = os.path.join(output_dir, f"AT24C02_{poll_name}.pat")
            with open(poll_path, "w", encoding="utf-8") as f:
                f.write(poll_pat)
            print(f"  [PAT] {poll_path} (ACK Polling)")

        # Keep the complete, unsplit vectors in the TXT preview.
        seg_txt = fmt.format_txt_preview(vectors, comments, TEST_PINS, desc)
        seg_txt_path = os.path.join(output_dir, f"AT24C02_{name}_preview.txt")
        with open(seg_txt_path, "w", encoding="utf-8") as f:
            f.write(seg_txt)
        print(f"  [TXT] {seg_txt_path}")

    # Console summary.
    print(f"\n{'='*50}")
    print("Generation complete!")
    print(f"  Export sections: {len(sections)}")
    print(f"  Total vectors: {total_vectors}")
    print(f"  Output directory: {output_dir}")
    print(f"{'='*50}")


if __name__ == "__main__":
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    print("AT24C02 PAT sample generator (9 families / 14 export sections)")
    print("=" * 50)
    generate_all_files(output_dir)
