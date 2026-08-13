#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BY25Q40AL SPI NOR Flash PAT parameterized generator.

This public edition is implemented from the device protocol and the team's own
algorithms. It does not contain, fingerprint, copy, or require competition- or
vendor-provided PAT examples. Generated files must be validated against the
target ATE configuration before production use.
"""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
import threading
from typing import Callable, Iterable, Iterator, Mapping, Optional, Sequence


APP_TITLE = "BY25Q40AL PAT 向量生成工具（开源参数化版）"
CHIP_NAME = "BY25Q40AL"
CAPACITY_BYTES = 512 * 1024
MAX_ADDRESS = CAPACITY_BYTES - 1
PAGE_SIZE = 256
VECTOR_PERIOD_NS = 50
PINS = ("CS_N", "SO_IO1", "WP_IO2", "SI_IO0", "SCLK", "HOLD_IO3")
ALLOWED_STATES = frozenset("01HLX")
SLIDING_BASE = (0x7F, 0xBF, 0xDF, 0xEF, 0xF7, 0xFB, 0xFD, 0xFE)


@dataclasses.dataclass(frozen=True)
class ModeSpec:
    key: str
    label: str
    file_tag: str
    provisional: bool = False


@dataclasses.dataclass(frozen=True)
class BusSpec:
    key: str
    label: str
    program_opcode: int
    read_opcode: int
    program_width: int
    read_width: int
    dummy_clocks: int = 0
    needs_qe: bool = False


MODE_SPECS: Mapping[str, ModeSpec] = {
    "mode_1": ModeSpec("mode_1", "模式一：全 0", "ALL_ZERO"),
    "mode_2": ModeSpec("mode_2", "模式二：Checkerboard", "CHECKERBOARD"),
    "mode_3": ModeSpec("mode_3", "模式三：Walking One", "WALKING_ONE"),
    "mode_4": ModeSpec("mode_4", "模式四：Walking 0", "WALKING_ZERO"),
    "mode_5": ModeSpec("mode_5", "模式五：Sliding Diagonal", "SLIDING_DIAGONAL"),
    "mode_6": ModeSpec("mode_6", "模式六：GALPAT 乒乓", "GALPAT"),
}

BUS_SPECS: Mapping[str, BusSpec] = {
    "SPI": BusSpec("SPI", "Standard SPI", 0x02, 0x03, 1, 1),
    "DUAL": BusSpec("DUAL", "Dual SPI", 0xA2, 0x3B, 2, 2, 8),
    "QUAD": BusSpec("QUAD", "Quad SPI", 0x32, 0x6B, 4, 4, 8, True),
}

# Stable output names used by the public generator.
MEMORY_OUTPUT_NAMES: Mapping[str, tuple[str, str]] = {
    "SPI": ("STANDARD_MEMORY_ERASE_CHECK.pat", "STANDARD_MEMORY_PROGRAM_READ.pat"),
    "DUAL": ("DUAL_MEMORY_ERASE_CHECK.pat", "DUAL_MEMORY_PROGRAM_READ.pat"),
    "QUAD": ("QUAD_MEMORY_ERASE_CHECK.pat", "QUAD_MEMORY_PROGRAM_READ.pat"),
}

MODE_ALIASES = {
    "1": "mode_1", "mode1": "mode_1", "all_zero": "mode_1", "zero": "mode_1",
    "2": "mode_2", "mode2": "mode_2", "checkerboard": "mode_2",
    "3": "mode_3", "mode3": "mode_3", "walking_one": "mode_3", "walking1": "mode_3",
    "4": "mode_4", "mode4": "mode_4", "walking_zero": "mode_4", "walking0": "mode_4",
    "5": "mode_5", "mode5": "mode_5", "sliding": "mode_5", "sliding_diagonal": "mode_5",
    "6": "mode_6", "mode6": "mode_6", "galpat": "mode_6", "ping_pong": "mode_6",
}


def normalize_mode(value: str) -> str:
    key = str(value).strip().lower().replace("-", "_").replace(" ", "_")
    key = MODE_ALIASES.get(key, key)
    if key not in MODE_SPECS:
        raise ValueError(f"未知数据模式：{value!r}")
    return key


def normalize_bus(value: str) -> str:
    key = str(value).strip().upper().replace("标准", "").replace(" ", "")
    aliases = {"1-1-1": "SPI", "111": "SPI", "1-1-2": "DUAL", "112": "DUAL",
               "1-1-4": "QUAD", "114": "QUAD"}
    key = aliases.get(key, key)
    if key not in BUS_SPECS:
        raise ValueError(f"未知总线模式：{value!r}")
    return key


def memory_output_names(bus: str) -> tuple[str, str]:
    """Return stable erase and program/read output names."""
    return MEMORY_OUTPUT_NAMES[normalize_bus(bus)]


def parse_address(value: int | str) -> int:
    """解析 0x000100、000100h 或裸十六进制地址。"""
    if isinstance(value, bool):
        raise ValueError("布尔值不是有效地址")
    if isinstance(value, int):
        address = value
    else:
        text = str(value).strip().replace("_", "")
        if not text:
            raise ValueError("地址不能为空")
        if text.lower().startswith("0x"):
            text = text[2:]
        elif text.lower().endswith("h"):
            text = text[:-1]
        if not text or not re.fullmatch(r"[0-9a-fA-F]+", text):
            raise ValueError(f"无效十六进制地址：{value!r}")
        address = int(text, 16)
    if not 0 <= address <= MAX_ADDRESS:
        raise ValueError(f"地址 0x{address:X} 超出范围 0x000000~0x{MAX_ADDRESS:06X}")
    return address


def align_write_range(start: int | str, end: int | str) -> tuple[int, int]:
    first = parse_address(start)
    last = parse_address(end)
    if first > last:
        raise ValueError("起始地址不能大于终止地址")
    return first & ~(PAGE_SIZE - 1), min(MAX_ADDRESS, last | (PAGE_SIZE - 1))


def align_page_range(start: int | str, end: int | str) -> tuple[int, int]:
    return align_write_range(start, end)


def sliding_byte(address: int, state: int = 0) -> int:
    address = parse_address(address)
    if not 0 <= state <= 7:
        raise ValueError("Sliding state 必须为 0..7")
    return SLIDING_BASE[((address & 7) + state) & 7]


def galpat_byte(address: int, bc_address: Optional[int] = None) -> int:
    address = parse_address(address)
    if bc_address is None:
        bc_address = address & ~(PAGE_SIZE - 1)
    bc_address = parse_address(bc_address)
    return 0x80 if address == bc_address else 0x00


def pattern_byte(mode: str, address: int) -> int:
    """Return the team's algorithmic data for one address.

    模式五返回 state0；模式六默认把所在页页首作为 BC。完整状态型流程由
    BY25Q40ALPatternGenerator 负责组合。
    """
    key = normalize_mode(mode)
    address = parse_address(address)
    if key == "mode_1":
        return 0x00
    if key == "mode_2":
        return 0xAA if (address & 1) == 0 else 0x55
    if key == "mode_3":
        return 1 << (address & 7)
    if key == "mode_4":
        return 0xFF ^ (1 << (address & 7))
    if key == "mode_5":
        return sliding_byte(address, 0)
    return galpat_byte(address)


def iter_pattern_bytes(mode: str, start: int | str, end: int | str) -> Iterator[int]:
    first = parse_address(start)
    last = parse_address(end)
    if first > last:
        raise ValueError("起始地址不能大于终止地址")
    for address in range(first, last + 1):
        yield pattern_byte(mode, address)


def mode_data(mode: str, start: int | str, end: int | str) -> bytes:
    return bytes(iter_pattern_bytes(mode, start, end))


def mode_period(mode: str, start_address: int, state: int = 0) -> tuple[int, ...]:
    key = normalize_mode(mode)
    start_address = parse_address(start_address)
    if key == "mode_1":
        return (0x00,)
    if key == "mode_2":
        return tuple(pattern_byte(key, start_address + index) for index in range(2))
    if key in ("mode_3", "mode_4"):
        return tuple(pattern_byte(key, start_address + index) for index in range(8))
    if key == "mode_5":
        return tuple(sliding_byte(start_address + index, state) for index in range(8))
    raise ValueError("GALPAT 不是单次周期数据")


Vector = tuple[str, str, str, str, str, str]


@dataclasses.dataclass(frozen=True)
class Transaction:
    kind: str
    opcode: int
    address: Optional[int] = None
    length: int = 0
    width: int = 1


@dataclasses.dataclass
class GenerationStats:
    vector_count: int = 0
    directive_count: int = 0
    transaction_count: int = 0
    page_count: int = 0
    compared_bytes: int = 0
    written_bytes: int = 0


@dataclasses.dataclass(frozen=True)
class ValidationReport:
    ok: bool
    errors: tuple[str, ...]
    warnings: tuple[str, ...] = ()
    vector_count: int = 0

    def summary(self) -> str:
        if self.ok:
            return f"通过（{self.vector_count} 条物理向量）"
        return f"失败（{len(self.errors)} 个错误，{self.vector_count} 条物理向量）"


@dataclasses.dataclass(frozen=True)
class GenerationResult:
    erase_path: Path
    program_path: Path
    erase_validation: ValidationReport
    program_validation: ValidationReport
    erase_stats: GenerationStats
    program_stats: GenerationStats
    mode: str
    bus: str
    read_start: int
    read_end: int
    write_start: int
    write_end: int

    @property
    def paths(self) -> tuple[Path, Path]:
        return self.erase_path, self.program_path


class CancelledError(RuntimeError):
    pass


def _validate_vector(vector: Sequence[str]) -> Vector:
    if len(vector) != len(PINS):
        raise ValueError("向量必须包含 6 个引脚状态")
    normalized = tuple(str(value).upper() for value in vector)
    if any(len(value) != 1 or value not in ALLOWED_STATES for value in normalized):
        raise ValueError(f"非法向量状态：{normalized}")
    return normalized  # type: ignore[return-value]


class EStarPATWriter:
    """Write the public EStar-compatible PAT subset used by this project."""

    VECTOR_COLUMN = 20
    COMMENT_INDENT = " " * 30

    def __init__(self, file_obj, title: str, metadata: Iterable[str] = ()):
        self.file_obj = file_obj
        self.stats = GenerationStats()
        self._started = False
        self._closed = False
        self._labels: set[str] = set()
        self._write_preamble(title, metadata)

    @staticmethod
    def _safe_text(text: object) -> str:
        result = str(text).replace("\r", " ").replace("\n", " ")
        if "Z" in result:
            raise ValueError("生成 PAT 的文字中禁止出现大写字母 Z")
        return result

    def _write_preamble(self, title: str, metadata: Iterable[str]) -> None:
        border = "// Public generator output " + "-" * 52
        self.file_obj.write(border + "\n")
        self.file_obj.write("// " + self._safe_text(title) + "\n")
        for item in metadata:
            self.file_obj.write("// " + self._safe_text(item) + "\n")
        self.file_obj.write(border + "\n\n")
        self.file_obj.write("HEAD[PIN_NAME]:\n")
        for index, pin in enumerate(PINS):
            self.file_obj.write(pin + (";" if index == len(PINS) - 1 else ",") + "\n")
        self.file_obj.write("END_HEAD;\n\n")
        self.file_obj.write("@@PATTERN_DEFINE\n\n")
        self.file_obj.write("// Generated pin order: " + ",".join(PINS) + "\n\n")

    def blank(self) -> None:
        self.file_obj.write("\n")

    def comment(self, text: str = "", *, indent: bool = True) -> None:
        if not text:
            self.file_obj.write("//\n")
            return
        prefix = self.COMMENT_INDENT if indent else ""
        self.file_obj.write(prefix + "// " + self._safe_text(text) + "\n")

    def emit(self, vector: Sequence[str], *, label: Optional[str] = None,
             instructions: Iterable[str] = (), inline_comment: str = "") -> None:
        if self._closed:
            raise RuntimeError("PAT writer 已关闭")
        checked = _validate_vector(vector)
        commands = [str(item).strip().rstrip(";") for item in instructions if str(item).strip()]
        if not self._started:
            if label is None:
                label = "start"
            if label != "start":
                raise ValueError("首向量标签必须为 start")
            if not any(command.upper().startswith("AC_SET ") for command in commands):
                commands.insert(0, "AC_SET 1")
            self._started = True
        if label:
            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", label):
                raise ValueError(f"非法标签：{label!r}")
            if label in self._labels:
                raise ValueError(f"重复标签：{label}")
            self._labels.add(label)
            label_text = label + ":"
            prefix = label_text.ljust(self.VECTOR_COLUMN)
            if len(label_text) >= self.VECTOR_COLUMN:
                prefix += " "
        else:
            prefix = " " * self.VECTOR_COLUMN
        line = prefix + "".join(checked) + ";"
        if commands:
            line += " " + " ".join(command + ";" for command in commands)
            self.stats.directive_count += len(commands)
        if inline_comment:
            line += "    // " + self._safe_text(inline_comment)
        self.file_obj.write(line + "\n")
        self.stats.vector_count += 1

    def start(self, vector: Sequence[str]) -> None:
        self.emit(vector, label="start", instructions=("AC_SET 1", "RPT 3"))

    def labeled_idle(self, label: str, vector: Sequence[str], *, ac_set: bool) -> None:
        commands = ("AC_SET 1", "RPT 3") if ac_set else ("RPT 3",)
        self.emit(vector, label=label, instructions=commands)

    def close(self, end_vector: Sequence[str]) -> GenerationStats:
        if self._closed:
            return self.stats
        if not self._started:
            raise ValueError("PAT 文件没有向量")
        self.emit(end_vector, label="end", instructions=("RPT 3",))
        self.file_obj.write("\n@@END_PATTERN_DEFINE\n")
        self._closed = True
        return self.stats


class SPIEmitter:
    """Emit Standard/Dual/Quad transactions using four vectors per clock."""

    NORMAL_IDLE: Vector = ("1", "X", "1", "0", "0", "1")
    NORMAL_ACTIVE: Vector = ("0", "X", "1", "0", "0", "1")
    QUAD_IDLE: Vector = ("1", "X", "X", "X", "0", "X")
    QUAD_ACTIVE: Vector = ("0", "X", "X", "X", "0", "X")

    def __init__(self, writer: EStarPATWriter, transactions: list[Transaction],
                 *, release_quad: bool = False):
        self.writer = writer
        self.transactions = transactions
        self.release_quad = release_quad

    @property
    def idle_state(self) -> Vector:
        return self.QUAD_IDLE if self.release_quad else self.NORMAL_IDLE

    @property
    def active_state(self) -> Vector:
        return self.QUAD_ACTIVE if self.release_quad else self.NORMAL_ACTIVE

    @staticmethod
    def _drive(bit: int) -> str:
        return "1" if bit else "0"

    @staticmethod
    def _compare(bit: int) -> str:
        return "H" if bit else "L"

    def emit_idle(self, *, instructions: Iterable[str] = ()) -> None:
        self.writer.emit(self.idle_state, instructions=instructions)

    def begin_transaction(self, title: str) -> None:
        self.writer.comment(title)
        self.writer.emit(self.idle_state)
        self.writer.emit(self.active_state, instructions=("RPT 3",))

    def _released_state(self, cs: str, width: int = 1) -> Vector:
        # Modes 5/6 explicitly release all IO pins while QE is enabled.
        if self.release_quad:
            return (cs, "X", "X", "X", "0", "X")
        return (cs, "X", "1", "0", "0", "1")

    def end_transaction(self, *, release_data: bool = False, release_width: int = 1) -> None:
        active = self._released_state("0", release_width) if release_data else self.active_state
        idle = self._released_state("1", release_width) if release_data else self.idle_state
        self.writer.emit(active, instructions=("RPT 2",))
        self.writer.emit(idle, instructions=("RPT 2",))

    def _send_clock_states(self, group: int, width: int) -> tuple[Vector, Vector]:
        if width == 1:
            io2 = "X" if self.release_quad else "1"
            io3 = "X" if self.release_quad else "1"
            low = ("0", "X", io2, self._drive(group), "0", io3)
            high = ("0", "X", io2, self._drive(group), "1", io3)
        elif width == 2:
            low = ("0", self._drive((group >> 1) & 1), "1",
                   self._drive(group & 1), "0", "1")
            high = ("0", self._drive((group >> 1) & 1), "1",
                    self._drive(group & 1), "1", "1")
        elif width == 4:
            # group bit3..0 = IO3..IO0；HEAD 顺序为 IO1,IO2,IO0,SCLK,IO3。
            low = ("0", self._drive((group >> 1) & 1), self._drive((group >> 2) & 1),
                   self._drive(group & 1), "0", self._drive((group >> 3) & 1))
            high = ("0", self._drive((group >> 1) & 1), self._drive((group >> 2) & 1),
                    self._drive(group & 1), "1", self._drive((group >> 3) & 1))
        else:
            raise ValueError("总线宽度必须为 1、2 或 4")
        return low, high

    def send_value(self, value: int, bits: int, width: int = 1, *,
                   first_instruction: str = "", last_instruction: str = "") -> None:
        if width not in (1, 2, 4) or bits <= 0 or bits % width:
            raise ValueError("发送位数必须能被总线宽度整除")
        chunks = bits // width
        mask = (1 << width) - 1
        for index in range(chunks):
            shift = bits - width * (index + 1)
            group = (value >> shift) & mask
            low, high = self._send_clock_states(group, width)
            for phase, vector in enumerate((low, low, high, high)):
                commands: list[str] = []
                if index == 0 and phase == 0 and first_instruction:
                    commands.append(first_instruction)
                if index == chunks - 1 and phase == 3 and last_instruction:
                    commands.append(last_instruction)
                self.writer.emit(vector, instructions=commands)

    def _receive_clock_states(self, group: int, width: int) -> tuple[Vector, Vector, Vector]:
        if width == 1:
            io2 = "X" if self.release_quad else "1"
            io3 = "X" if self.release_quad else "1"
            low_x = ("0", "X", io2, "X", "0", io3)
            low_cmp = ("0", self._compare(group), io2, "X", "0", io3)
            high_x = ("0", "X", io2, "X", "1", io3)
        elif width == 2:
            low_x = ("0", "X", "1", "X", "0", "1")
            low_cmp = ("0", self._compare((group >> 1) & 1), "1",
                       self._compare(group & 1), "0", "1")
            high_x = ("0", "X", "1", "X", "1", "1")
        elif width == 4:
            low_x = ("0", "X", "X", "X", "0", "X")
            low_cmp = ("0", self._compare((group >> 1) & 1),
                       self._compare((group >> 2) & 1), self._compare(group & 1),
                       "0", self._compare((group >> 3) & 1))
            high_x = ("0", "X", "X", "X", "1", "X")
        else:
            raise ValueError("总线宽度必须为 1、2 或 4")
        return low_x, low_cmp, high_x

    def receive_value(self, expected: int, bits: int = 8, width: int = 1, *,
                      first_instruction: str = "", last_instruction: str = "") -> None:
        if width not in (1, 2, 4) or bits <= 0 or bits % width:
            raise ValueError("接收位数必须能被总线宽度整除")
        chunks = bits // width
        mask = (1 << width) - 1
        for index in range(chunks):
            shift = bits - width * (index + 1)
            group = (expected >> shift) & mask
            low_x, low_cmp, high_x = self._receive_clock_states(group, width)
            for phase, vector in enumerate((low_x, low_cmp, high_x, high_x)):
                commands: list[str] = []
                if index == 0 and phase == 0 and first_instruction:
                    commands.append(first_instruction)
                if index == chunks - 1 and phase == 3 and last_instruction:
                    commands.append(last_instruction)
                self.writer.emit(vector, instructions=commands)

    def receive_masked_byte(self, expected_bits: Mapping[int, int]) -> None:
        for bit_index in range(7, -1, -1):
            io2 = "X" if self.release_quad else "1"
            io3 = "X" if self.release_quad else "1"
            low_x = ("0", "X", io2, "X", "0", io3)
            expected = expected_bits.get(bit_index)
            low_cmp = low_x if expected is None else (
                "0", self._compare(expected), io2, "X", "0", io3)
            high_x = ("0", "X", io2, "X", "1", io3)
            for vector in (low_x, low_cmp, high_x, high_x):
                self.writer.emit(vector)

    def dummy_clocks(self, count: int, *, quad: bool) -> None:
        low = ("0", "X", "X", "X", "0", "X") if quad else (
            "0", "X", "1", "X", "0", "1")
        high = ("0", "X", "X", "X", "1", "X") if quad else (
            "0", "X", "1", "X", "1", "1")
        for _ in range(count):
            for vector in (low, low, high, high):
                self.writer.emit(vector)

    def command(self, opcode: int) -> None:
        self.send_value(opcode, 8, 1)

    def address24(self, address: int) -> None:
        self.send_value(parse_address(address), 24, 1)

    def simple_command(self, opcode: int, kind: str) -> None:
        self.begin_transaction(f"{kind}：0x{opcode:02X}")
        self.command(opcode)
        self.end_transaction()
        self.transactions.append(Transaction(kind, opcode))

    def write_enable(self) -> None:
        self.simple_command(0x06, "Write Enable")

    def fixed_wait(self, loop_count: int, cycles: int, title: str) -> None:
        if not 2 <= loop_count <= 65535:
            raise ValueError("LOOP 次数必须为 2..65535")
        if not 4 <= cycles <= 4096:
            raise ValueError("LOOP 块必须包含 4..4096 个向量")
        self.writer.comment(title)
        for index in range(cycles):
            commands: list[str] = []
            if index == 0:
                commands.append(f"LOOP {loop_count}")
            if index == cycles - 1:
                commands.append("LOOP END")
            self.writer.emit(self.idle_state, instructions=commands)

    def read_status(self, opcode: int, expected_bits: Mapping[int, int], kind: str) -> None:
        self.begin_transaction(f"{kind}：0x{opcode:02X}")
        self.command(opcode)
        self.receive_masked_byte(expected_bits)
        self.end_transaction(release_data=True)
        self.transactions.append(Transaction(kind, opcode, length=1))

    def standard_checkerboard_wip_once(self, page_start: int) -> None:
        """Emit one uncompressed WIP=0 check after a page program.

        该专用段只用于 Standard SPI Checkerboard。事务边界不使用 RPT
        压缩；05h 和 SR1 的每一位都显式保留四行向量，且仅在
        SR1[0] 的第二个低相位比较 L。
        """
        page_start = parse_address(page_start)
        if page_start & (PAGE_SIZE - 1):
            raise ValueError("Checkerboard WIP 检查地址必须页对齐")
        if self.release_quad:
            raise ValueError("Standard SPI Checkerboard WIP 检查不能在 QE 模式执行")

        page_number = page_start // PAGE_SIZE
        self.writer.blank()
        self.writer.comment(
            f"Post-program WIP check for page {page_number}: require SR1[0] low")
        self.writer.comment(
            "Issue RDSR1 opcode 05h; compare only SR1[0] as the busy flag")

        # Expand the CS_N transition explicitly for readability.
        self.writer.emit(self.idle_state)
        for _ in range(3):
            self.writer.emit(self.active_state)
        self.writer.blank()

        # 05h = 00000101，Standard SPI、MSB First、每 bit 四行。
        for bit_index in range(7, -1, -1):
            bit = (0x05 >> bit_index) & 1
            self.writer.comment(f"RDSR1 opcode bit[{bit_index}] => {bit}")
            self.send_value(bit, 1, 1)
            self.writer.blank()

        # SR1[7:1] 全部 X；只在 SR1[0] 的第二个低相位比较 L。
        for bit_index in range(7, -1, -1):
            if bit_index == 0:
                self.writer.comment("SR1 bit0: expect low (not busy)")
            else:
                self.writer.comment(f"SR1 bit{bit_index}：不比较")
            low_x, low_l, high_x = self._receive_clock_states(0, 1)
            sample = low_l if bit_index == 0 else low_x
            for vector in (low_x, sample, high_x, high_x):
                self.writer.emit(vector)
            self.writer.blank()

        # End the read transaction explicitly before deasserting CS_N.
        read_active: Vector = ("0", "X", "1", "X", "0", "1")
        self.writer.emit(read_active)
        self.writer.emit(read_active)
        self.writer.emit(self.idle_state)
        self.writer.blank()
        self.writer.blank()
        self.transactions.append(Transaction("WIP_CHECK", 0x05, length=1))

    def set_qe_volatile(self, enabled: bool) -> None:
        """Set or restore the volatile QE bit for Quad flows."""
        self.simple_command(0x50, "Volatile SR Write Enable")
        self.begin_transaction("Write Status Register：0x01")
        self.command(0x01)
        self.send_value(0x00, 8, 1)
        self.send_value(0x02 if enabled else 0x00, 8, 1)
        self.end_transaction()
        self.transactions.append(Transaction("QE_ON" if enabled else "QE_OFF", 0x01, length=2))
        self.release_quad = enabled
        self.read_status(0x35, {1: 1 if enabled else 0},
                         "Verify QE on" if enabled else "Verify QE off")

    def _emit_period(self, values: Sequence[int], repeat_count: int, width: int,
                     *, compare: bool) -> None:
        if not values or repeat_count <= 0:
            return
        remaining = repeat_count
        while remaining:
            count = min(remaining, 65535)
            if count == 1:
                for value in values:
                    if compare:
                        self.receive_value(value, 8, width)
                    else:
                        self.send_value(value, 8, width)
            else:
                for index, value in enumerate(values):
                    first = f"LOOP {count}" if index == 0 else ""
                    last = "LOOP END" if index == len(values) - 1 else ""
                    if compare:
                        self.receive_value(value, 8, width,
                                           first_instruction=first, last_instruction=last)
                    else:
                        self.send_value(value, 8, width,
                                        first_instruction=first, last_instruction=last)
            remaining -= count

    def emit_periodic_bytes(self, values: Sequence[int], length: int, width: int,
                            *, compare: bool) -> None:
        if length < 0 or not values:
            raise ValueError("周期数据长度非法")
        repeat_count, remainder = divmod(length, len(values))
        self._emit_period(values, repeat_count, width, compare=compare)
        for value in values[:remainder]:
            if compare:
                self.receive_value(value, 8, width)
            else:
                self.send_value(value, 8, width)

    def emit_arbitrary_bytes(self, values: Sequence[int], width: int, *, compare: bool) -> None:
        index = 0
        while index < len(values):
            run_end = index + 1
            while run_end < len(values) and values[run_end] == values[index]:
                run_end += 1
            run_length = run_end - index
            if run_length >= 2:
                self._emit_period((values[index],), run_length, width, compare=compare)
            else:
                if compare:
                    self.receive_value(values[index], 8, width)
                else:
                    self.send_value(values[index], 8, width)
            index = run_end

    def _program_prefix(self, bus: BusSpec, address: int) -> None:
        self.write_enable()
        self.begin_transaction(
            f"{bus.label} Page Program：0x{bus.program_opcode:02X} + {address:06X}h")
        self.command(bus.program_opcode)
        self.address24(address)

    def _program_suffix(self, bus: BusSpec, address: int, length: int,
                        *, check_wip: bool) -> None:
        self.end_transaction(release_data=bus.program_width > 1,
                             release_width=bus.program_width)
        self.transactions.append(Transaction("PAGE_PROGRAM", bus.program_opcode,
                                             address, length, bus.program_width))
        self.fixed_wait(15000, 4, "Page Program 固定等待 3ms")
        if check_wip:
            self.read_status(0x05, {0: 0}, "Read SR1，检查 WIP=0")

    def page_program_periodic(self, bus: BusSpec, address: int, period: Sequence[int],
                              *, check_wip: bool = True) -> None:
        if address & (PAGE_SIZE - 1):
            raise ValueError("Page Program 地址必须页对齐")
        if PAGE_SIZE % len(period):
            raise ValueError("页数据周期必须整除 256")
        self._program_prefix(bus, address)
        self.emit_periodic_bytes(period, PAGE_SIZE, bus.program_width, compare=False)
        self._program_suffix(bus, address, PAGE_SIZE, check_wip=check_wip)

    def page_program_bytes(self, bus: BusSpec, address: int, data: Sequence[int],
                           *, check_wip: bool = True) -> None:
        if address & (PAGE_SIZE - 1) or len(data) != PAGE_SIZE:
            raise ValueError("Page Program 必须从页首写满 256 Byte")
        self._program_prefix(bus, address)
        self.emit_arbitrary_bytes(data, bus.program_width, compare=False)
        self._program_suffix(bus, address, len(data), check_wip=check_wip)

    def page_erase(self, address: int) -> None:
        page_start = parse_address(address) & ~(PAGE_SIZE - 1)
        self.write_enable()
        self.begin_transaction(f"Page Erase：0x81 + {page_start:06X}h")
        self.command(0x81)
        self.address24(page_start)
        self.end_transaction()
        self.transactions.append(Transaction("PAGE_ERASE", 0x81, page_start))
        self.fixed_wait(60000, 4, "Page Erase 固定等待 12ms")
        self.read_status(0x05, {0: 0}, "Read SR1，检查 WIP=0")

    def _read_prefix(self, bus: BusSpec, address: int) -> None:
        self.begin_transaction(
            f"{bus.label} Read：0x{bus.read_opcode:02X} + {address:06X}h")
        self.command(bus.read_opcode)
        self.address24(address)
        if bus.dummy_clocks:
            self.dummy_clocks(bus.dummy_clocks, quad=bus.read_width == 4)

    def _read_suffix(self, bus: BusSpec, address: int, length: int) -> None:
        self.end_transaction(release_data=True, release_width=bus.read_width)
        self.transactions.append(Transaction("READ_COMPARE", bus.read_opcode,
                                             address, length, bus.read_width))

    def read_compare_periodic(self, bus: BusSpec, address: int, period: Sequence[int],
                              length: int) -> None:
        if length <= 0 or address + length - 1 > MAX_ADDRESS:
            raise ValueError("读比较范围非法")
        self._read_prefix(bus, address)
        self.emit_periodic_bytes(period, length, bus.read_width, compare=True)
        self._read_suffix(bus, address, length)

    def read_compare_bytes(self, bus: BusSpec, address: int, data: Sequence[int]) -> None:
        if not data or address + len(data) - 1 > MAX_ADDRESS:
            raise ValueError("读比较范围非法")
        self._read_prefix(bus, address)
        self.emit_arbitrary_bytes(data, bus.read_width, compare=True)
        self._read_suffix(bus, address, len(data))


class PatternData:
    @staticmethod
    def byte(mode: str, address: int) -> int:
        return pattern_byte(mode, address)

    @staticmethod
    def iter_bytes(mode: str, start: int | str, end: int | str) -> Iterator[int]:
        return iter_pattern_bytes(mode, start, end)

    @staticmethod
    def page(mode: str, page_start: int | str) -> bytes:
        first = parse_address(page_start)
        if first & (PAGE_SIZE - 1):
            raise ValueError("page_start 必须页对齐")
        return bytes(pattern_byte(mode, first + offset) for offset in range(PAGE_SIZE))


class PATValidator:
    """Validate the EStar-compatible PAT subset emitted by this project."""

    VECTOR_RE = re.compile(
        r"^\s*(?:(?P<label>[A-Za-z_][A-Za-z0-9_]*):\s*)?"
        r"(?P<vector>[01HLX]{6});(?P<tail>.*)$"
    )
    VECTOR_CANDIDATE_RE = re.compile(
        r"^\s*(?:[A-Za-z_][A-Za-z0-9_]*:\s*)?([A-Za-z0-9]{5,8});"
    )
    INSTRUCTION_RE = re.compile(
        r"\s*(?:(AC_SET)\s+(\d+)|(RPT)\s+(\d+)|(LOOP)\s+(END|\d+));",
        re.IGNORECASE,
    )

    @classmethod
    def validate_file(cls, path: os.PathLike[str] | str, *,
                      forbid_text_z: bool = True) -> ValidationReport:
        try:
            text = Path(path).read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            return ValidationReport(False, (f"无法按 UTF-8 读取：{exc}",))
        return cls.validate_text(text, forbid_text_z=forbid_text_z)

    @classmethod
    def validate_text(cls, text: str, *, forbid_text_z: bool = True) -> ValidationReport:
        lines = text.splitlines()
        errors: list[str] = []
        warnings: list[str] = []
        if forbid_text_z and "Z" in text:
            errors.append("PAT 全文禁止出现大写字母 Z")
        try:
            head_start = next(i for i, line in enumerate(lines) if line.strip() == "HEAD[PIN_NAME]:")
            head_end = next(i for i in range(head_start + 1, len(lines))
                            if lines[i].strip() == "END_HEAD;")
        except StopIteration:
            return ValidationReport(False, tuple(errors + ["缺少完整 HEAD[PIN_NAME] 块"]))
        pin_text = "".join(line.split("//", 1)[0].strip()
                           for line in lines[head_start + 1:head_end])
        parsed_pins = tuple(token.strip() for token in pin_text.rstrip(";").split(",")
                            if token.strip())
        if parsed_pins != PINS:
            errors.append("HEAD 引脚顺序必须为 " + ", ".join(PINS))
        pattern_indices = [i for i, line in enumerate(lines)
                           if line.strip() == "@@PATTERN_DEFINE"]
        end_indices = [i for i, line in enumerate(lines)
                       if line.strip() == "@@END_PATTERN_DEFINE"]
        if len(pattern_indices) != 1 or len(end_indices) != 1:
            errors.append("@@PATTERN_DEFINE 与 @@END_PATTERN_DEFINE 必须各出现一次")
            return ValidationReport(False, tuple(errors), tuple(warnings))
        pattern_start, pattern_end = pattern_indices[0], end_indices[0]
        if not head_end < pattern_start < pattern_end:
            errors.append("HEAD 与 PATTERN 块顺序错误")

        vectors: list[tuple[int, Optional[str], str, tuple[tuple[str, str], ...]]] = []
        labels: set[str] = set()
        active_loop: Optional[tuple[int, int]] = None
        for line_index in range(pattern_start + 1, pattern_end):
            raw = lines[line_index]
            stripped = raw.strip()
            if not stripped or stripped.startswith("//"):
                continue
            match = cls.VECTOR_RE.match(raw)
            if not match:
                candidate = cls.VECTOR_CANDIDATE_RE.match(raw)
                if candidate:
                    errors.append(f"第 {line_index + 1} 行向量宽度或状态非法：{candidate.group(1)}")
                else:
                    errors.append(f"第 {line_index + 1} 行不是支持的 PAT 向量语法")
                continue
            label = match.group("label")
            state = match.group("vector")
            if label:
                if label in labels:
                    errors.append(f"第 {line_index + 1} 行标签重复：{label}")
                labels.add(label)
            tail = match.group("tail").split("//", 1)[0]
            commands: list[tuple[str, str]] = []
            position = 0
            while position < len(tail):
                if not tail[position:].strip():
                    break
                command = cls.INSTRUCTION_RE.match(tail, position)
                if not command:
                    errors.append(f"第 {line_index + 1} 行微指令非法：{tail.strip()}")
                    break
                if command.group(1):
                    commands.append(("AC_SET", command.group(2)))
                elif command.group(3):
                    commands.append(("RPT", command.group(4)))
                else:
                    commands.append(("LOOP", command.group(6).upper()))
                position = command.end()
            vector_number = len(vectors)
            for name, argument in commands:
                if name == "AC_SET" and int(argument) <= 0:
                    errors.append(f"第 {line_index + 1} 行 AC_SET 必须大于 0")
                elif name == "RPT" and not 2 <= int(argument) <= 65535:
                    errors.append(f"第 {line_index + 1} 行 RPT 必须为 2..65535")
                elif name == "LOOP":
                    if argument == "END":
                        if active_loop is None:
                            errors.append(f"第 {line_index + 1} 行 LOOP END 没有起点")
                        else:
                            block_size = vector_number - active_loop[1] + 1
                            if not 4 <= block_size <= 4096:
                                errors.append(
                                    f"第 {line_index + 1} 行 LOOP 块为 {block_size} 向量，必须为 4..4096")
                            active_loop = None
                    else:
                        count = int(argument)
                        if not 2 <= count <= 65535:
                            errors.append(f"第 {line_index + 1} 行 LOOP 必须为 2..65535")
                        if active_loop is not None:
                            errors.append(f"第 {line_index + 1} 行不允许嵌套 LOOP")
                        else:
                            active_loop = (line_index, vector_number)
            vectors.append((line_index, label, state, tuple(commands)))
        if active_loop is not None:
            errors.append(f"第 {active_loop[0] + 1} 行 LOOP 未闭合")
        if not vectors:
            errors.append("PATTERN 块中没有向量")
        else:
            first = vectors[0]
            last = vectors[-1]
            if first[1] != "start":
                errors.append("首向量标签必须为 start")
            if ("AC_SET", "1") not in first[3]:
                errors.append("首向量必须包含 AC_SET 1")
            if last[1] != "end":
                errors.append("末向量标签必须为 end")
            for line_index, label, _state, commands in vectors:
                if label and label.endswith("_start") and ("AC_SET", "1") not in commands:
                    errors.append(f"第 {line_index + 1} 行子段 start 标签缺少 AC_SET 1")
        return ValidationReport(not errors, tuple(errors), tuple(warnings), len(vectors))


def validate_pat(source: os.PathLike[str] | str, *, is_text: bool = False) -> ValidationReport:
    return (PATValidator.validate_text(str(source)) if is_text
            else PATValidator.validate_file(source))


def validate_transactions(transactions: Sequence[Transaction], bus: str,
                          *_ranges: object) -> ValidationReport:
    """对动态生成器登记的事务做第二层一致性检查。"""
    spec = BUS_SPECS[normalize_bus(bus)]
    errors: list[str] = []
    for index, item in enumerate(transactions):
        if item.kind == "PAGE_PROGRAM":
            if item.opcode != spec.program_opcode or item.width != spec.program_width:
                errors.append(f"事务 {index} Page Program opcode/width 错误")
            if item.address is None or item.address & (PAGE_SIZE - 1) or item.length != PAGE_SIZE:
                errors.append(f"事务 {index} Page Program 未从页首写满 256 Byte")
            if index == 0 or transactions[index - 1].kind != "Write Enable":
                # 实际记录名为 Write Enable；状态检查不会插在 WREN 与 Program 之间。
                errors.append(f"事务 {index} Page Program 前缺少紧邻 WREN")
        elif item.kind == "PAGE_ERASE":
            if item.opcode != 0x81 or item.address is None or item.address & 0xFF:
                errors.append(f"事务 {index} Page Erase 错误")
            if index == 0 or transactions[index - 1].kind != "Write Enable":
                errors.append(f"事务 {index} Page Erase 前缺少紧邻 WREN")
        elif item.kind == "READ_COMPARE":
            if item.opcode != spec.read_opcode or item.width != spec.read_width:
                errors.append(f"事务 {index} Read opcode/width 错误")
    return ValidationReport(not errors, tuple(errors))


def _sha256(path: os.PathLike[str] | str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _atomic_write_bytes(destination: Path, data: bytes) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp_path = destination.with_name(destination.name + ".tmp")
    try:
        with open(temp_path, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_path, destination)
    finally:
        temp_path.unlink(missing_ok=True)


def _standard_checkerboard_wip_block(page_number: int, newline: str) -> str:
    """Generate an explicit single 05h/SR1 WIP check block."""
    comment = EStarPATWriter.COMMENT_INDENT
    vector = " " * EStarPATWriter.VECTOR_COLUMN
    lines = [
        "",
        f"{comment}// Post-program WIP check for page {page_number}: require SR1[0] low",
        f"{comment}// Issue RDSR1 opcode 05h; compare only SR1[0] as the busy flag",
        f"{vector}1X1001;",
        f"{vector}0X1001;",
        f"{vector}0X1001;",
        f"{vector}0X1001;",
        "",
    ]
    for bit_index in range(7, -1, -1):
        bit = (0x05 >> bit_index) & 1
        low = f"0X1{bit}01"
        high = f"0X1{bit}11"
        lines.extend((
            f"{comment}// RDSR1 opcode bit[{bit_index}] => {bit}",
            f"{vector}{low};",
            f"{vector}{low};",
            f"{vector}{high};",
            f"{vector}{high};",
            "",
        ))
    for bit_index in range(7, -1, -1):
        description = "expect low (not busy)" if bit_index == 0 else "not compared"
        sample = "0L1X01" if bit_index == 0 else "0X1X01"
        lines.extend((
            f"{comment}// SR1 bit{bit_index}: {description}",
            f"{vector}0X1X01;",
            f"{vector}{sample};",
            f"{vector}0X1X11;",
            f"{vector}0X1X11;",
            "",
        ))
    lines.extend((
        f"{vector}0X1X01;",
        f"{vector}0X1X01;",
        f"{vector}1X1001;",
        "",
        "",
    ))
    return newline.join(lines) + newline


def _insert_standard_checkerboard_wip_checks(data: bytes) -> bytes:
    """Insert one WIP check after each uncompressed 3 ms wait block."""
    text = data.decode("utf-8")
    if "Issue RDSR1 opcode 05h; compare only SR1[0] as the busy flag" in text:
        raise ValueError("Standard SPI Checkerboard PAT 已含 WIP 段，拒绝重复插入")
    newline = "\r\n" if "\r\n" in text else "\n"
    output: list[str] = []
    current_page: Optional[int] = None
    waiting_for_loop_end = False
    skip_blank_after_insert = False
    wait_count = text.count("LOOP 15000;")
    inserted = 0

    for line in text.splitlines(keepends=True):
        if skip_blank_after_insert and not line.strip():
            continue
        skip_blank_after_insert = False

        page_match = re.search(r"Page\s+(\d+)[：:]", line)
        if page_match and "从页首" in line:
            current_page = int(page_match.group(1))
        output.append(line)

        if "LOOP 15000;" in line:
            if current_page is None or waiting_for_loop_end:
                raise ValueError("Standard SPI Checkerboard 等待段结构异常")
            waiting_for_loop_end = True
        elif waiting_for_loop_end and "LOOP END;" in line:
            output.append(_standard_checkerboard_wip_block(current_page, newline))
            inserted += 1
            waiting_for_loop_end = False
            skip_blank_after_insert = True

    if waiting_for_loop_end or inserted != wait_count or inserted == 0:
        raise ValueError(
            f"Standard SPI Checkerboard WIP 插入数量异常：等待 {wait_count}，插入 {inserted}")
    result = "".join(output).encode("utf-8")
    if b"Z" in result:
        raise ValueError("Standard SPI Checkerboard WIP 修正后出现大写字母 Z")
    return result


def _verify_standard_checkerboard_wip_contract(text: str, expected_pages: int) -> None:
    """运行时强制页数=WIP 次数，并核对每段 05h/SR1 的关键物理格式。"""
    if expected_pages <= 0:
        raise ValueError("Standard SPI Checkerboard 页数必须大于 0")
    header = re.compile(
        r"(?m)^\s*// Post-program WIP check for page \d+: require SR1\[0\] low\r?$")
    matches = list(header.finditer(text))
    if len(matches) != expected_pages:
        raise ValueError(
            f"Standard SPI Checkerboard WIP 次数错误：页数 {expected_pages}，"
            f"WIP {len(matches)}")
    if text.count("LOOP 15000;") != expected_pages:
        raise ValueError("Standard SPI Checkerboard 每页必须恰有一次 3ms 固定等待")

    command_comments = [
        f"RDSR1 opcode bit[{bit}] => {(0x05 >> bit) & 1}"
        for bit in range(7, -1, -1)
    ]
    for index, match in enumerate(matches):
        try:
            bit0 = text.index("// SR1 bit0: expect low (not busy)", match.start())
            close = text.index("1X1001;", bit0) + len("1X1001;")
        except ValueError as exc:
            raise ValueError(f"第 {index + 1} 个 WIP 段不完整") from exc
        section = text[match.start():close]
        if "RPT" in section or "LOOP" in section:
            raise ValueError(f"第 {index + 1} 个 WIP 段禁止 RPT/LOOP 压缩或循环查询")
        if section.count(
                "Issue RDSR1 opcode 05h; compare only SR1[0] as the busy flag") != 1:
            raise ValueError(f"第 {index + 1} 个 WIP 段缺少唯一 05h 说明")
        if any(section.count(comment) != 1 for comment in command_comments):
            raise ValueError(f"第 {index + 1} 个 WIP 段的 05h 位序错误")
        if section.count("// SR1 bit") != 8 or section.count("0L1X01;") != 1:
            raise ValueError(f"第 {index + 1} 个 WIP 段必须只在 SR1[0] 比较一次 L")
        rows = [line.strip() for line in section.splitlines() if line.strip()]
        if rows[-3:] != ["0X1X01;", "0X1X01;", "1X1001;"]:
            raise ValueError(f"第 {index + 1} 个 WIP 段的 CS_N 结尾格式错误")


class BY25Q40ALPatternGenerator:
    """Clean-room, parameterized four-vector generator."""

    def __init__(self, progress: Optional[Callable[[str, int, int], None]] = None,
                 cancel_event: Optional[threading.Event] = None):
        self.progress = progress
        self.cancel_event = cancel_event

    def _check_cancelled(self) -> None:
        if self.cancel_event is not None and self.cancel_event.is_set():
            raise CancelledError("生成已取消")

    def _progress(self, stage: str, current: int, total: int) -> None:
        if self.progress is not None:
            self.progress(stage, current, total)

    @staticmethod
    def _path(path: os.PathLike[str] | str) -> Path:
        result = Path(path)
        result.parent.mkdir(parents=True, exist_ok=True)
        return result

    @staticmethod
    def _stats_from_report(report: ValidationReport) -> GenerationStats:
        return GenerationStats(vector_count=report.vector_count)

    def generate_erase_pat(self, path: os.PathLike[str] | str, bus: str = "SPI") \
            -> tuple[GenerationStats, ValidationReport]:
        bus_key = normalize_bus(bus)
        destination = self._path(path)
        bus_spec = BUS_SPECS[bus_key]
        transactions: list[Transaction] = []
        temp_path = destination.with_name(destination.name + ".tmp")
        try:
            with open(temp_path, "w", encoding="utf-8", newline="\r\n") as stream:
                writer = EStarPATWriter(
                    stream,
                    f"BY25Q40AL - {bus_spec.label} - Chip Erase and Blank Check",
                    (
                        f"总线：{bus_spec.label}",
                        "流程：WREN → Chip Erase C7h → 固定等待 → WIP=0 → 抽样空白检查",
                        "抽样地址：000000h、040000h、07FFF0h，各 16 Byte",
                        "向量位序：CS_N, SO_IO1, WP_IO2, SI_IO0, SCLK, HOLD_IO3",
                    ),
                )
                emitter = SPIEmitter(writer, transactions)
                writer.start(emitter.idle_state)
                if bus_spec.needs_qe:
                    emitter.set_qe_volatile(True)
                emitter.write_enable()
                emitter.simple_command(0xC7, "Chip Erase")
                emitter.fixed_wait(60000, 4, "Chip Erase 固定等待 12ms")
                emitter.read_status(0x05, {0: 0}, "Read SR1，检查 WIP=0")
                for sample_address in (0x000000, 0x040000, 0x07FFF0):
                    emitter.read_compare_periodic(
                        bus_spec, sample_address, (0xFF,), 16)
                    writer.stats.compared_bytes += 16
                if bus_spec.needs_qe:
                    emitter.set_qe_volatile(False)
                stats = writer.close(emitter.idle_state)
                stats.transaction_count = len(transactions)
            report = PATValidator.validate_file(temp_path)
            if not report.ok:
                raise ValueError("擦除 PAT 校验失败：" + "；".join(report.errors[:8]))
            tx_report = validate_transactions(transactions, bus_key)
            if not tx_report.ok:
                raise ValueError("擦除事务校验失败：" + "；".join(tx_report.errors[:8]))
            os.replace(temp_path, destination)
            return stats, report
        finally:
            temp_path.unlink(missing_ok=True)

    def _generate_dynamic(self, destination: Path, mode_key: str, bus_key: str,
                          read_start: int, read_end: int) \
            -> tuple[GenerationStats, ValidationReport, tuple[int, int]]:
        bus = BUS_SPECS[bus_key]
        write_start, write_end = align_write_range(read_start, read_end)
        page_starts = list(range(write_start, write_end + 1, PAGE_SIZE))
        transactions: list[Transaction] = []
        temp_path = destination.with_name(destination.name + ".tmp")
        try:
            with open(temp_path, "w", encoding="utf-8", newline="\r\n") as stream:
                metadata = (
                    f"总线：{bus.label}；模式：{MODE_SPECS[mode_key].label}",
                    f"页写范围：{write_start:06X}h~{write_end:06X}h",
                    f"读比较范围：{read_start:06X}h~{read_end:06X}h",
                    "向量位序：CS_N, SO_IO1, WP_IO2, SI_IO0, SCLK, HOLD_IO3",
                    "AC_SET 1，PERIOD=50ns；每个 SCLK 使用低2行+高2行",
                )
                writer = EStarPATWriter(
                    stream, f"BY25Q40AL - {bus.label} - {MODE_SPECS[mode_key].label}", metadata)
                emitter = SPIEmitter(writer, transactions)
                writer.start(emitter.idle_state)

                if mode_key in ("mode_1", "mode_2", "mode_3", "mode_4"):
                    total = len(page_starts)
                    for page_index, page_start in enumerate(page_starts, 1):
                        self._check_cancelled()
                        writer.comment(f"Page {page_start // PAGE_SIZE}：写满 256 Byte")
                        period = mode_period(mode_key, page_start)
                        is_standard_checkerboard = mode_key == "mode_2" and bus_key == "SPI"
                        emitter.page_program_periodic(
                            bus, page_start, period, check_wip=not is_standard_checkerboard)
                        if is_standard_checkerboard:
                            emitter.standard_checkerboard_wip_once(page_start)
                        writer.stats.page_count += 1
                        writer.stats.written_bytes += PAGE_SIZE
                        self._progress("页写", page_index, total)
                    read_length = read_end - read_start + 1
                    emitter.read_compare_periodic(
                        bus, read_start, mode_period(mode_key, read_start), read_length)
                    writer.stats.compared_bytes = read_length

                elif mode_key == "mode_5":
                    if bus.needs_qe:
                        emitter.set_qe_volatile(True)
                    total_states = len(page_starts) * 8
                    completed = 0
                    for page_start in page_starts:
                        page_number = page_start // PAGE_SIZE
                        segment_start = max(page_start, read_start)
                        segment_end = min(page_start + PAGE_SIZE - 1, read_end)
                        segment_length = segment_end - segment_start + 1
                        for state in range(8):
                            self._check_cancelled()
                            writer.labeled_idle(
                                f"page{page_number}_state{state}_start",
                                emitter.idle_state, ac_set=True)
                            writer.comment(
                                f"Page {page_number}，Sliding 状态 {state}/7，写后立即读比较")
                            emitter.page_program_periodic(
                                bus, page_start, mode_period(mode_key, page_start, state))
                            read_period = mode_period(mode_key, segment_start, state)
                            emitter.read_compare_periodic(
                                bus, segment_start, read_period, segment_length)
                            if state < 7:
                                emitter.page_erase(page_start)
                            writer.labeled_idle(
                                f"page{page_number}_state{state}_end",
                                emitter.idle_state, ac_set=False)
                            writer.stats.written_bytes += PAGE_SIZE
                            writer.stats.compared_bytes += segment_length
                            completed += 1
                            self._progress("Sliding 状态", completed, total_states)
                        writer.stats.page_count += 1
                    if bus.needs_qe:
                        emitter.set_qe_volatile(False)

                else:
                    if bus.needs_qe:
                        emitter.set_qe_volatile(True)
                    total_pages = len(page_starts)
                    for page_index, page_start in enumerate(page_starts, 1):
                        self._check_cancelled()
                        segment_start = max(page_start, read_start)
                        segment_end = min(page_start + PAGE_SIZE - 1, read_end)
                        bc_address = segment_start
                        page_data = [0x00] * PAGE_SIZE
                        page_data[bc_address - page_start] = 0x80
                        writer.comment(
                            f"GALPAT Page {page_start // PAGE_SIZE}：BC={bc_address:06X}h")
                        emitter.page_program_bytes(bus, page_start, page_data)
                        oc_addresses = [address for address in range(segment_start, segment_end + 1)
                                        if address != bc_address]
                        if not oc_addresses:
                            emitter.read_compare_bytes(bus, bc_address, (0x80,))
                            writer.stats.compared_bytes += 1
                        else:
                            for pair_index, oc_address in enumerate(oc_addresses, 1):
                                if pair_index == 1 or pair_index % 32 == 0:
                                    self._check_cancelled()
                                writer.comment(
                                    f"Pair {pair_index:03d}：OC {oc_address:06X}h → BC {bc_address:06X}h")
                                emitter.read_compare_bytes(bus, oc_address, (0x00,))
                                emitter.read_compare_bytes(bus, bc_address, (0x80,))
                                writer.stats.compared_bytes += 2
                        writer.stats.page_count += 1
                        writer.stats.written_bytes += PAGE_SIZE
                        self._progress("GALPAT 页", page_index, total_pages)
                    if bus.needs_qe:
                        emitter.set_qe_volatile(False)

                stats = writer.close(emitter.idle_state)
                stats.transaction_count = len(transactions)
            if mode_key == "mode_2" and bus_key == "SPI":
                _verify_standard_checkerboard_wip_contract(
                    temp_path.read_text(encoding="utf-8"), len(page_starts))
            report = PATValidator.validate_file(temp_path)
            if not report.ok:
                raise ValueError("动态 PAT 语法校验失败：" + "；".join(report.errors[:8]))
            tx_report = validate_transactions(transactions, bus_key)
            if not tx_report.ok:
                raise ValueError("动态 PAT 事务校验失败：" + "；".join(tx_report.errors[:8]))
            os.replace(temp_path, destination)
            return stats, report, (write_start, write_end)
        finally:
            temp_path.unlink(missing_ok=True)

    def generate_program_pat(self, path: os.PathLike[str] | str, mode: str, bus: str,
                             start: int | str, end: int | str) \
            -> tuple[GenerationStats, ValidationReport, tuple[int, int]]:
        mode_key = normalize_mode(mode)
        bus_key = normalize_bus(bus)
        read_start = parse_address(start)
        read_end = parse_address(end)
        if read_start > read_end:
            raise ValueError("起始地址不能大于终止地址")
        destination = self._path(path)
        return self._generate_dynamic(destination, mode_key, bus_key, read_start, read_end)

    def generate(self, output_dir: os.PathLike[str] | str, mode: str, bus: str,
                 start: int | str, end: int | str) -> GenerationResult:
        mode_key = normalize_mode(mode)
        bus_key = normalize_bus(bus)
        read_start = parse_address(start)
        read_end = parse_address(end)
        if read_start > read_end:
            raise ValueError("起始地址不能大于终止地址")
        write_start, write_end = align_write_range(read_start, read_end)
        directory = Path(output_dir)
        directory.mkdir(parents=True, exist_ok=True)
        erase_name, program_name = memory_output_names(bus_key)
        erase_path = directory / erase_name
        program_path = directory / program_name
        staging = Path(tempfile.mkdtemp(prefix=".by25q40al_stage_", dir=directory))
        staged_erase = staging / erase_path.name
        staged_program = staging / program_path.name
        try:
            erase_stats, erase_report = self.generate_erase_pat(staged_erase, bus_key)
            program_stats, program_report, _ = self.generate_program_pat(
                staged_program, mode_key, bus_key, read_start, read_end)
            self._check_cancelled()
            for source, target in ((staged_erase, erase_path), (staged_program, program_path)):
                os.replace(source, target)
        finally:
            shutil.rmtree(staging, ignore_errors=True)
        return GenerationResult(
            erase_path, program_path, erase_report, program_report,
            erase_stats, program_stats, mode_key, bus_key,
            read_start, read_end, write_start, write_end)


PatternGenerator = BY25Q40ALPatternGenerator


def preview_pat(path: os.PathLike[str] | str, head_lines: int = 500,
                tail_bytes: int = 32 * 1024) -> str:
    file_path = Path(path)
    size = file_path.stat().st_size
    with open(file_path, "r", encoding="utf-8") as stream:
        head = [stream.readline() for _ in range(head_lines)]
    head_text = "".join(line for line in head if line)
    if size <= len(head_text.encode("utf-8")) + tail_bytes:
        return file_path.read_text(encoding="utf-8")
    with open(file_path, "rb") as stream:
        stream.seek(max(0, size - tail_bytes))
        tail = stream.read().decode("utf-8", errors="replace")
    if "\n" in tail:
        tail = tail.split("\n", 1)[1]
    return (head_text +
            f"\n// ... 有限预览：已省略中间内容；文件大小 {size / 1024 / 1024:.2f} MiB ...\n\n" +
            tail)


class FinalsApp:
    """复赛现场极简 GUI。"""

    def __init__(self, root):
        import tkinter as tk
        from tkinter import ttk

        self.root = root
        self.tk = tk
        self.ttk = ttk
        self.root.title(APP_TITLE)
        self.root.geometry("1120x760")
        self.root.minsize(920, 640)
        self.workspace = Path(tempfile.mkdtemp(prefix="by25q40al_pat_"))
        self.current_files: list[Path] = []
        self.cancel_event = threading.Event()
        self.worker: Optional[threading.Thread] = None

        self.mode_var = tk.StringVar(value="mode_1")
        self.bus_var = tk.StringVar(value="SPI")
        self.start_var = tk.StringVar(value="000000h")
        self.end_var = tk.StringVar(value="0001FFh")
        self.range_var = tk.StringVar(value="")
        self.status_var = tk.StringVar(value="就绪")
        self.progress_var = tk.DoubleVar(value=0.0)

        self._build_ui()
        self.mode_var.trace_add("write", self._on_mode_changed)
        self.bus_var.trace_add("write", self._update_range)
        self.start_var.trace_add("write", self._update_range)
        self.end_var.trace_add("write", self._update_range)
        self._update_range()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self) -> None:
        tk, ttk = self.tk, self.ttk
        outer = ttk.Frame(self.root, padding=12)
        outer.pack(fill="both", expand=True)
        outer.columnconfigure(1, weight=1)
        outer.rowconfigure(0, weight=1)

        controls = ttk.LabelFrame(outer, text="BY25Q40AL PAT 配置", padding=12)
        controls.grid(row=0, column=0, sticky="nsw", padx=(0, 10))
        ttk.Label(controls, text="固定芯片：BY25Q40AL（512 KiB）").pack(anchor="w", pady=(0, 8))
        ttk.Label(controls, text="公开参数化生成器｜不含第三方竞赛资产",
                  foreground="#166534").pack(anchor="w", pady=(0, 8))
        ttk.Separator(controls).pack(fill="x", pady=(0, 8))

        ttk.Label(controls, text="数据模式").pack(anchor="w")
        # 两列排布，保持紧凑且便于现场操作。
        mode_frame = ttk.Frame(controls)
        mode_frame.pack(fill="x", pady=(1, 0))
        for index, spec in enumerate(MODE_SPECS.values()):
            ttk.Radiobutton(mode_frame, text=spec.label, variable=self.mode_var,
                            value=spec.key).grid(
                                row=index // 2, column=index % 2,
                                sticky="w", padx=(0, 12), pady=1)
        ttk.Label(controls, text="总线模式").pack(anchor="w", pady=(10, 2))
        bus_frame = ttk.Frame(controls)
        bus_frame.pack(fill="x")
        for index, spec in enumerate(BUS_SPECS.values()):
            ttk.Radiobutton(bus_frame, text=spec.label, variable=self.bus_var,
                            value=spec.key).grid(
                                row=0, column=index, sticky="w", padx=(0, 12), pady=1)

        address_frame = ttk.Frame(controls)
        address_frame.pack(fill="x", pady=(10, 0))
        ttk.Label(address_frame, text="起始地址").grid(row=0, column=0, sticky="w")
        ttk.Entry(address_frame, width=14, textvariable=self.start_var).grid(
            row=0, column=1, padx=(8, 0))
        ttk.Label(address_frame, text="终止地址").grid(row=1, column=0, sticky="w", pady=(5, 0))
        ttk.Entry(address_frame, width=14, textvariable=self.end_var).grid(
            row=1, column=1, padx=(8, 0), pady=(5, 0))
        ttk.Label(controls, textvariable=self.range_var, foreground="#245c9b",
                  wraplength=290, justify="left").pack(anchor="w", pady=(6, 8))

        buttons = ttk.Frame(controls)
        buttons.pack(fill="x", pady=(2, 8))
        self.generate_button = ttk.Button(buttons, text="生成 Memory PAT",
                                          command=self._generate_patterns)
        self.generate_button.pack(side="left", fill="x", expand=True)
        self.cancel_button = ttk.Button(buttons, text="取消", command=self._cancel,
                                        state="disabled", width=7)
        self.cancel_button.pack(side="left", padx=(6, 0))

        self.export_button = ttk.Button(controls, text="导出当前 PAT…", command=self._export,
                                        state="disabled")
        self.export_button.pack(fill="x", pady=(2, 4))

        right = ttk.Frame(outer)
        right.grid(row=0, column=1, sticky="nsew")
        right.rowconfigure(2, weight=1)
        right.columnconfigure(0, weight=1)
        status_frame = ttk.Frame(right)
        status_frame.grid(row=0, column=0, sticky="ew")
        status_frame.columnconfigure(0, weight=1)
        ttk.Label(status_frame, textvariable=self.status_var).grid(row=0, column=0, sticky="w")
        ttk.Progressbar(status_frame, variable=self.progress_var, maximum=100,
                        length=220).grid(row=0, column=1, sticky="e")
        file_frame = ttk.LabelFrame(right, text="生成文件（单击切换预览）", padding=5)
        file_frame.grid(row=1, column=0, sticky="ew", pady=(8, 8))
        file_frame.columnconfigure(0, weight=1)
        self.file_list = tk.Listbox(file_frame, height=3, exportselection=False)
        self.file_list.grid(row=0, column=0, sticky="ew")
        self.file_list.bind("<<ListboxSelect>>", self._on_select_file)
        preview_frame = ttk.LabelFrame(right, text="PAT 有限预览 / 校验结果", padding=5)
        preview_frame.grid(row=2, column=0, sticky="nsew")
        preview_frame.rowconfigure(0, weight=1)
        preview_frame.columnconfigure(0, weight=1)
        self.preview = tk.Text(preview_frame, wrap="none", font=("Consolas", 10), undo=False)
        y_scroll = ttk.Scrollbar(preview_frame, orient="vertical", command=self.preview.yview)
        x_scroll = ttk.Scrollbar(preview_frame, orient="horizontal", command=self.preview.xview)
        self.preview.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        self.preview.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        self._set_preview("配置总线、模式和地址后点击“生成 Memory PAT”。")

    def _on_mode_changed(self, *_args) -> None:
        """Adjust the default example range when the mode changes."""
        mode = normalize_mode(self.mode_var.get())
        start_text = self.start_var.get().strip().lower()
        end_text = self.end_var.get().strip().lower()
        if start_text in {"000000h", "0x000000", "000000"} and end_text in {
                "0000ffh", "0x0000ff", "0000ff",
                "0001ffh", "0x0001ff", "0001ff",
        }:
            default_end = "0000FFh" if mode == "mode_6" else "0001FFh"
            if self.end_var.get() != default_end:
                self.end_var.set(default_end)
        self._update_range()

    def _update_range(self, *_args) -> None:
        try:
            start = parse_address(self.start_var.get())
            end = parse_address(self.end_var.get())
            write_start, write_end = align_write_range(start, end)
            mode = normalize_mode(self.mode_var.get())
            bus = normalize_bus(self.bus_var.get())
            page_count = (write_end - write_start + 1) // PAGE_SIZE
            wip_line = (
                f"\nCheckerboard WIP：{page_count} 次（每页固定等待后单次检查）"
                if mode == "mode_2" and bus == "SPI" else ""
            )
            self.range_var.set(
                f"读比较：0x{start:06X}～0x{end:06X}\n"
                f"页写扩展：0x{write_start:06X}～0x{write_end:06X} "
                f"（{page_count} 页）"
                f"{wip_line}")
        except ValueError as exc:
            self.range_var.set("地址错误：" + str(exc))

    def _set_preview(self, text: str) -> None:
        self.preview.configure(state="normal")
        self.preview.delete("1.0", "end")
        self.preview.insert("1.0", text)
        self.preview.configure(state="disabled")

    def _set_busy(self, busy: bool) -> None:
        state = "disabled" if busy else "normal"
        self.generate_button.configure(state=state)
        self.cancel_button.configure(state="normal" if busy else "disabled")
        self.export_button.configure(state="disabled" if busy or not self.current_files else "normal")

    def _run_worker(self, target: Callable[[], object], done: Callable[[object], None]) -> None:
        if self.worker and self.worker.is_alive():
            return
        self.cancel_event.clear()
        self._set_busy(True)
        self.progress_var.set(0)

        def runner() -> None:
            try:
                result = target()
            except CancelledError as exc:
                self.root.after(0, lambda: self._worker_failed(str(exc), False))
            except Exception as exc:
                self.root.after(0, lambda exc=exc: self._worker_failed(str(exc), True))
            else:
                self.root.after(0, lambda: self._worker_done(result, done))

        self.worker = threading.Thread(target=runner, name="PATGenerator", daemon=True)
        self.worker.start()

    def _worker_failed(self, message: str, show_dialog: bool) -> None:
        from tkinter import messagebox
        self.status_var.set(message)
        self._set_busy(False)
        if show_dialog:
            messagebox.showerror("生成失败", message, parent=self.root)

    def _worker_done(self, result: object, done: Callable[[object], None]) -> None:
        done(result)
        self._set_busy(False)
        self.progress_var.set(100)

    def _progress(self, stage: str, current: int, total: int) -> None:
        percent = 100.0 * current / max(1, total)
        self.root.after(0, lambda: (self.status_var.set(f"{stage}：{current}/{total}"),
                                   self.progress_var.set(percent)))

    def _generate_patterns(self) -> None:
        from tkinter import messagebox
        try:
            start = parse_address(self.start_var.get())
            end = parse_address(self.end_var.get())
            write_start, write_end = align_write_range(start, end)
        except ValueError as exc:
            messagebox.showerror("地址错误", str(exc), parent=self.root)
            return
        mode, bus = self.mode_var.get(), self.bus_var.get()
        pages = (write_end - write_start + 1) // PAGE_SIZE
        if mode in ("mode_5", "mode_6") and pages > 2 and not messagebox.askyesno(
                "大算法范围确认",
                f"该算法将在 {pages} 页执行多轮事务，文件可能很大。继续吗？",
                parent=self.root):
            return
        self.current_files = []
        self.file_list.delete(0, "end")
        self._set_preview("正在参数化生成并进行语法与事务校验，请稍候…")
        self.status_var.set("准备生成…")

        def target() -> GenerationResult:
            return BY25Q40ALPatternGenerator(self._progress, self.cancel_event).generate(
                self.workspace, mode, bus, start, end)

        def done(raw_result: object) -> None:
            result = raw_result
            assert isinstance(result, GenerationResult)
            self.current_files = list(result.paths)
            wip_summary = (
                f"Checkerboard WIP：{result.program_stats.page_count} 次（页数=检查次数）。\n"
                if result.mode == "mode_2" and result.bus == "SPI" else ""
            )
            summary = (
                f"生成完成。页写 0x{result.write_start:06X}～0x{result.write_end:06X}；"
                f"读比较 0x{result.read_start:06X}～0x{result.read_end:06X}。\n"
                f"{wip_summary}"
                f"擦除：{result.erase_validation.summary()}\n"
                f"写读：{result.program_validation.summary()}\n"
                f"写入={result.program_stats.written_bytes} Byte，"
                f"比较={result.program_stats.compared_bytes} Byte。\n\n")
            self._show_files(summary)
            self.status_var.set("生成与校验完成，可导出")

        self._run_worker(target, done)

    def _show_files(self, prefix: str = "") -> None:
        self.file_list.delete(0, "end")
        for path in self.current_files:
            self.file_list.insert("end", f"{path.name}  ({path.stat().st_size / 1024:.1f} KiB)")
        if self.current_files:
            self.file_list.selection_set(0)
            self._set_preview(prefix + preview_pat(self.current_files[0]))

    def _on_select_file(self, _event=None) -> None:
        selection = self.file_list.curselection()
        if selection:
            self._set_preview(preview_pat(self.current_files[selection[0]]))

    def _export(self) -> None:
        from tkinter import filedialog, messagebox
        if not self.current_files:
            return
        directory = filedialog.askdirectory(title="选择 PAT 导出目录", parent=self.root)
        if not directory:
            return
        sources = tuple(self.current_files)

        def target() -> tuple[Path, ...]:
            destinations: list[Path] = []
            for source in sources:
                if self.cancel_event.is_set():
                    raise CancelledError("导出已取消")
                destination = Path(directory) / source.name
                data = source.read_bytes()
                _atomic_write_bytes(destination, data)
                if _sha256(source) != _sha256(destination):
                    destination.unlink(missing_ok=True)
                    raise OSError(f"{source.name} 导出后校验失败")
                destinations.append(destination)
            return tuple(destinations)

        def done(raw_result: object) -> None:
            destinations = raw_result
            assert isinstance(destinations, tuple)
            messagebox.showinfo("导出完成", "\n".join(str(path) for path in destinations),
                                parent=self.root)
            self.status_var.set(f"已导出到 {directory}")

        self.status_var.set("正在导出并校验…")
        self._run_worker(target, done)

    def _cancel(self) -> None:
        self.cancel_event.set()
        self.status_var.set("正在取消…")

    def _on_close(self) -> None:
        self.cancel_event.set()
        if not (self.worker and self.worker.is_alive()):
            shutil.rmtree(self.workspace, ignore_errors=True)
        self.root.destroy()


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=APP_TITLE)
    parser.add_argument("--batch", action="store_true", help="无 GUI 批量生成")
    parser.add_argument("--mode", default="mode_1", help="mode_1..mode_6")
    parser.add_argument("--bus", default="SPI", help="SPI / DUAL / QUAD")
    parser.add_argument("--start", default="000000h", help="读比较起始地址")
    parser.add_argument(
        "--end", default=None,
        help="读比较终止地址；省略时模式1~5为0001FFh，模式6为0000FFh")
    parser.add_argument("--output", default="output_finals", help="输出目录")
    parser.add_argument("--validate", metavar="PAT", help="仅校验现有 PAT")
    return parser


def run_batch(args: argparse.Namespace) -> int:
    try:
        if args.validate:
            report = PATValidator.validate_file(args.validate)
            print(report.summary())
            for error in report.errors:
                print("ERROR:", error)
            return 0 if report.ok else 2
        mode_key = normalize_mode(args.mode)
        default_end = "0000FFh" if mode_key == "mode_6" else "0001FFh"
        result = BY25Q40ALPatternGenerator().generate(
            args.output, mode_key, args.bus, args.start,
            args.end if args.end is not None else default_end)
        for path in result.paths:
            print(path)
        print(result.erase_validation.summary())
        print(result.program_validation.summary())
        return 0
    except (OSError, ValueError, CancelledError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


def launch_gui() -> int:
    import tkinter as tk
    from tkinter import messagebox
    root = tk.Tk()
    try:
        FinalsApp(root)
        root.mainloop()
    except Exception as exc:
        messagebox.showerror("启动失败", str(exc), parent=root)
        root.destroy()
        return 2
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    if args.batch or args.validate:
        return run_batch(args)
    return launch_gui()


if __name__ == "__main__":
    raise SystemExit(main())
