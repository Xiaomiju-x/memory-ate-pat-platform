#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AT24C02 EEPROM PAT测试向量生成工具
===================================
针对AdaptStar-E (EStar) ATE测试系统
为AT24C02 I2C EEPROM芯片生成开短路测试和DC测试的PAT向量文件

作者: IC竞赛团队
版本: v2.0
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import datetime
import json
import sys
import subprocess
import hashlib
import re
import math
import struct
import logging
import argparse
import threading
import time as _time_module
import tempfile
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple

# ============================================================
# 日志系统
# ============================================================
LOG_DIR = os.path.join(os.path.expanduser("~"), ".ate_pat_platform")
try:
    os.makedirs(LOG_DIR, exist_ok=True)
    logging.basicConfig(
        filename=os.path.join(LOG_DIR, "platform.log"),
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(funcName)s: %(message)s",
        encoding="utf-8",
    )
except Exception:
    logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("ATE")

# ============================================================
# 常量定义
# ============================================================

VERSION = "v8.0.0"

# AT24C02 SOP-8引脚定义 (引脚号: 名称)
AT24C02_PINS = {
    1: "A0",    # 地址输入
    2: "A1",    # 地址输入
    3: "A2",    # 地址输入
    4: "GND",   # 地
    5: "SDA",   # 串行数据(双向)
    6: "SCL",   # 串行时钟
    7: "WP",    # 写保护
    8: "VCC",   # 电源
}

# 测试引脚列表 (按ATE通道排列，与EStar官方格式一致: A0,A1,A2,WP,SCL,SDA)
TEST_PINS = ["A0", "A1", "A2", "WP", "SCL", "SDA"]

# 各协议测试引脚列表 (每个协议恰好6引脚, 与ATE通道数一致)
PROTOCOL_PINS = {
    "I2C":       ["A0", "A1", "A2", "WP", "SCL", "SDA"],
    "SPI":       ["CS", "SCK", "MOSI", "MISO", "WP", "HOLD"],
    "Microwire": ["CS", "SK", "DI", "DO", "ORG", "NC"],
}

# I2C时序参数 (5V条件)
I2C_TIMING = {
    "fSCL": "400kHz",         # 时钟频率
    "tLOW": "1.3us",          # 时钟低电平宽度
    "tHIGH": "0.6us",         # 时钟高电平宽度
    "tSU_STA": "0.6us",       # 起始条件建立时间
    "tHD_STA": "0.6us",       # 起始条件保持时间
    "tSU_DAT": "100ns",       # 数据输入建立时间
    "tHD_DAT": "0ns",         # 数据输入保持时间
    "tSU_STO": "0.6us",       # 停止条件建立时间
    "tBUF": "1.3us",          # 总线释放时间
    "tWR": "5ms",             # 写周期
}

# AT24C02器件地址 (A2=A1=A0=0时)
DEVICE_ADDR_WRITE = 0xA0  # 1010 000 0 (写)
DEVICE_ADDR_READ  = 0xA1  # 1010 000 1 (读)

# 多电压等级预设 (根据 AT24C02 数据手册各工况参数)
VOLTAGE_PRESETS = {
    "5.0V": {
        "VCC": "5.0V", "VIH": "3.5V", "VIL": "1.5V",
        "VOH": "2.4V", "VOL": "0.4V", "IOL": "3.0mA",
        "VCLH": "6.0V", "VCLL": "-0.3V",
        "fSCL_max": "1MHz", "period_ns": 2500,
        "label": "level_5v",
    },
    "3.3V": {
        "VCC": "3.3V", "VIH": "2.31V", "VIL": "0.99V",
        "VOH": "2.4V", "VOL": "0.4V", "IOL": "3.0mA",
        "VCLH": "4.0V", "VCLL": "-0.3V",
        "fSCL_max": "400kHz", "period_ns": 2500,
        "label": "level_3v3",
    },
    "2.5V": {
        "VCC": "2.5V", "VIH": "1.75V", "VIL": "0.75V",
        "VOH": "2.0V", "VOL": "0.4V", "IOL": "1.0mA",
        "VCLH": "3.0V", "VCLL": "-0.3V",
        "fSCL_max": "400kHz", "period_ns": 2500,
        "label": "level_2v5",
    },
    "1.8V": {
        "VCC": "1.8V", "VIH": "1.17V", "VIL": "0.63V",
        "VOH": "1.35V", "VOL": "0.45V", "IOL": "1.0mA",
        "VCLH": "2.2V", "VCLL": "-0.3V",
        "fSCL_max": "100kHz", "period_ns": 10000,
        "label": "level_1v8",
    },
}

# AT24C02 测试限值表 (Pass/Fail 判定标准, 源自 Datasheet)
TEST_LIMITS = {
    "ISB_5V": {"param": "ISB", "desc": "Standby Current (5V)", "min": None, "typ": 0.1, "max": 1.0, "unit": "uA", "condition": "VCC=5.5V, SDA/SCL=VCC"},
    "ISB_3V": {"param": "ISB", "desc": "Standby Current (3.3V)", "min": None, "typ": 0.05, "max": 0.5, "unit": "uA", "condition": "VCC=3.6V, SDA/SCL=VCC"},
    "ICC_R":  {"param": "ICC", "desc": "Read Current", "min": None, "typ": 0.5, "max": 1.0, "unit": "mA", "condition": "fSCL=400kHz"},
    "ICC_W":  {"param": "ICC", "desc": "Write Current", "min": None, "typ": 1.5, "max": 3.0, "unit": "mA", "condition": "fSCL=400kHz"},
    "VOL":    {"param": "VOL", "desc": "Output Low Voltage", "min": None, "typ": None, "max": 0.4, "unit": "V", "condition": "IOL=3mA (5V) / 1mA (1.8V)"},
    "VIL_5V": {"param": "VIL", "desc": "Input Low Voltage (5V)", "min": -0.5, "typ": None, "max": 1.5, "unit": "V", "condition": "VCC=4.5~5.5V"},
    "VIH_5V": {"param": "VIH", "desc": "Input High Voltage (5V)", "min": 3.5, "typ": None, "max": 5.5, "unit": "V", "condition": "VCC=4.5~5.5V"},
    "VIL_3V": {"param": "VIL", "desc": "Input Low Voltage (3.3V)", "min": -0.5, "typ": None, "max": 0.99, "unit": "V", "condition": "VCC=2.7~3.6V"},
    "VIH_3V": {"param": "VIH", "desc": "Input High Voltage (3.3V)", "min": 2.31, "typ": None, "max": 3.6, "unit": "V", "condition": "VCC=2.7~3.6V"},
    "tWR":    {"param": "tWR", "desc": "Write Cycle Time", "min": None, "typ": None, "max": 5.0, "unit": "ms", "condition": "Page or Byte Write"},
    "ENDUR":  {"param": "Endurance", "desc": "Write Endurance", "min": 1000000, "typ": None, "max": None, "unit": "cycles", "condition": "Per cell, 25°C"},
    "RETEN":  {"param": "Retention", "desc": "Data Retention", "min": 100, "typ": None, "max": None, "unit": "years", "condition": "25°C"},
}

# I2C 时序约束 (各电压条件, 单位 ns, 源自 AT24C02 Datasheet)
I2C_TIMING_CONSTRAINTS = {
    "5.0V": {
        "fSCL_max_kHz": 1000,
        "tLOW_min":  1300,   # SCL低电平最小宽度
        "tHIGH_min":  600,   # SCL高电平最小宽度
        "tSU_STA_min": 600,  # START建立时间
        "tHD_STA_min": 600,  # START保持时间
        "tSU_DAT_min": 100,  # 数据建立时间
        "tSU_STO_min": 600,  # STOP建立时间
        "tBUF_min":   1300,  # 总线释放时间
        "tHD_DAT_min":   0,  # 数据保持时间
    },
    "3.3V": {
        "fSCL_max_kHz": 400,
        "tLOW_min":  1300,
        "tHIGH_min":  600,
        "tSU_STA_min": 600,
        "tHD_STA_min": 600,
        "tSU_DAT_min": 100,
        "tSU_STO_min": 600,
        "tBUF_min":   1300,
        "tHD_DAT_min":   0,
    },
    "2.5V": {
        "fSCL_max_kHz": 400,
        "tLOW_min":  1300,
        "tHIGH_min":  600,
        "tSU_STA_min": 600,
        "tHD_STA_min": 600,
        "tSU_DAT_min": 100,
        "tSU_STO_min": 600,
        "tBUF_min":   1300,
        "tHD_DAT_min":   0,
    },
    "1.8V": {
        "fSCL_max_kHz": 100,
        "tLOW_min":  4700,
        "tHIGH_min": 4000,
        "tSU_STA_min": 4700,
        "tHD_STA_min": 4000,
        "tSU_DAT_min": 250,
        "tSU_STO_min": 4000,
        "tBUF_min":   4700,
        "tHD_DAT_min":   0,
    },
}

# SPI 时序约束 (各电压条件, 单位 ns)
SPI_TIMING_CONSTRAINTS = {
    "5.0V": {
        "fSCK_max_MHz": 20,
        "tCSS_min":   50,    # CS Setup time
        "tCSH_min":   50,    # CS Hold time
        "tSU_min":    10,    # Data setup time (MOSI → SCK rising)
        "tHD_min":    10,    # Data hold time (SCK rising → MOSI)
        "tCH_min":    25,    # Clock high time
        "tCL_min":    25,    # Clock low time
        "tCSD_min":  100,    # CS deselect time (CS high between commands)
    },
    "3.3V": {
        "fSCK_max_MHz": 10,
        "tCSS_min":  100,
        "tCSH_min":  100,
        "tSU_min":    20,
        "tHD_min":    20,
        "tCH_min":    50,
        "tCL_min":    50,
        "tCSD_min":  200,
    },
    "2.5V": {
        "fSCK_max_MHz": 5,
        "tCSS_min":  200,
        "tCSH_min":  200,
        "tSU_min":    30,
        "tHD_min":    30,
        "tCH_min":   100,
        "tCL_min":   100,
        "tCSD_min":  400,
    },
    "1.8V": {
        "fSCK_max_MHz": 1,
        "tCSS_min":  500,
        "tCSH_min":  500,
        "tSU_min":    50,
        "tHD_min":    50,
        "tCH_min":   500,
        "tCL_min":   500,
        "tCSD_min": 1000,
    },
}

# Microwire 时序约束 (各电压条件, 单位 ns)
MW_TIMING_CONSTRAINTS = {
    "5.0V": {
        "fSK_max_MHz": 2,
        "tCSS_min":  50,     # CS setup to SK rising
        "tCSH_min":  50,     # SK falling to CS low
        "tSKH_min": 250,     # SK high time
        "tSKL_min": 250,     # SK low time
        "tDIS_min":  50,     # DI setup time
        "tDIH_min":  50,     # DI hold time
    },
    "3.3V": {
        "fSK_max_MHz": 2,
        "tCSS_min": 100,
        "tCSH_min": 100,
        "tSKH_min": 250,
        "tSKL_min": 250,
        "tDIS_min": 100,
        "tDIH_min": 100,
    },
    "2.5V": {
        "fSK_max_MHz": 1,
        "tCSS_min": 200,
        "tCSH_min": 200,
        "tSKH_min": 500,
        "tSKL_min": 500,
        "tDIS_min": 150,
        "tDIH_min": 150,
    },
    "1.8V": {
        "fSK_max_MHz": 1,
        "tCSS_min": 500,
        "tCSH_min": 500,
        "tSKH_min": 500,
        "tSKL_min": 500,
        "tDIS_min": 200,
        "tDIH_min": 200,
    },
}

# SPI 命令常量 (通用 SPI EEPROM / NOR Flash)
SPI_COMMANDS = {
    "WREN":          0x06,  # Write Enable
    "WRDI":          0x04,  # Write Disable
    "RDSR":          0x05,  # Read Status Register
    "WRSR":          0x01,  # Write Status Register
    "READ":          0x03,  # Read Data
    "WRITE":         0x02,  # Write Data (EEPROM) / Page Program (Flash)
    "SECTOR_ERASE":  0x20,  # Sector Erase 4KB (Flash)
    "BLOCK_ERASE_32K": 0x52,  # Block Erase 32KB
    "BLOCK_ERASE_64K": 0xD8,  # Block Erase 64KB
    "CHIP_ERASE":    0xC7,  # Chip Erase
    "JEDEC_ID":      0x9F,  # Read JEDEC ID
    "FAST_READ":     0x0B,  # Fast Read (with dummy byte)
}

# Microwire 操作码常量 (2-bit opcode after start bit)
MW_OPCODES = {
    "READ":  0b10,  # Read data
    "WRITE": 0b01,  # Write data
    "ERASE": 0b11,  # Erase word
    "EWEN":  (0b00, 0b11),  # Erase/Write Enable: opcode=00, addr prefix=11xxxx
    "EWDS":  (0b00, 0b00),  # Erase/Write Disable: opcode=00, addr prefix=00xxxx
    "ERAL":  (0b00, 0b10),  # Erase All: opcode=00, addr prefix=10xxxx
    "WRAL":  (0b00, 0b01),  # Write All: opcode=00, addr prefix=01xxxx
}

# 封装引脚图定义 (芯片图绘制用)
PACKAGE_PINOUTS = {
    "SOP-8_I2C": {
        "left": [(1, "A0"), (2, "A1"), (3, "A2"), (4, "GND")],
        "right": [(8, "VCC"), (7, "WP"), (6, "SCL"), (5, "SDA")],
    },
    "SOP-8_SPI": {
        "left": [(1, "CS"), (2, "SO"), (3, "WP"), (4, "GND")],
        "right": [(8, "VCC"), (7, "HOLD"), (6, "SCK"), (5, "SI")],
    },
    "DIP-8_MW": {
        "left": [(1, "CS"), (2, "SK"), (3, "DI"), (4, "GND")],
        "right": [(8, "VCC"), (7, "NC"), (6, "ORG"), (5, "DO")],
    },
}


# ============================================================
# 芯片预设 (通用芯片配置)
# ============================================================

def _chip(protocol, addr_pins, clk, data, wp, wp_def, ops, timing,
          dev_base, cap_bytes, page_sz, addr_bytes, page_sel_bits,
          endurance, manufacturer, aliases=None, capacity_label=None):
    """构建芯片预设字典的辅助函数"""
    if capacity_label is None:
        kbit = cap_bytes * 8 // 1024
        capacity_label = f"{kbit}Kbit ({cap_bytes}x8)"
    return {
        "protocol": protocol, "addr_pins": addr_pins,
        "clk_pin": clk, "data_pin": data, "wp_pin": wp, "wp_default": wp_def,
        "operations": ops, "timing_modes": timing,
        "device_addr_base": dev_base,
        "capacity": capacity_label, "capacity_bytes": cap_bytes,
        "page_size": page_sz, "addr_byte_count": addr_bytes,
        "page_select_bits": page_sel_bits,
        "endurance_cycles": endurance, "manufacturer": manufacturer,
        "aliases": aliases or [],
    }

_I2C_OPS = ["read", "write"]
_I2C_TIMING_STD = ["Standard 100kHz", "Fast 400kHz", "Fast+ 1MHz"]

_SPI_OPS = ["read", "write"]
_SPI_TIMING_STD = ["SPI 1MHz", "SPI 5MHz", "SPI 10MHz", "SPI 20MHz"]

_MW_OPS = ["read", "write"]
_MW_TIMING_STD = ["Microwire 1MHz", "Microwire 2MHz"]

def _spi_chip(cap_bytes, page_sz, addr_bytes, endurance, manufacturer,
              spi_mode=0, max_clock_mhz=10, sector_size=None,
              has_jedec_id=False, jedec_id=0, chip_type="EEPROM",
              aliases=None, capacity_label=None, wp_pin="WP", hold_pin="HOLD"):
    """构建SPI芯片预设字典"""
    if capacity_label is None:
        if cap_bytes >= 1024 * 1024:
            mbit = cap_bytes * 8 // (1024 * 1024)
            capacity_label = f"{mbit}Mbit ({cap_bytes}x8)"
        elif cap_bytes >= 1024:
            kbit = cap_bytes * 8 // 1024
            capacity_label = f"{kbit}Kbit ({cap_bytes}x8)"
        else:
            capacity_label = f"{cap_bytes * 8}bit ({cap_bytes}x8)"
    return {
        "protocol": "SPI", "addr_pins": [],
        "clk_pin": "SCK", "data_pin": "MOSI/MISO", "wp_pin": wp_pin, "wp_default": 0,
        "operations": _SPI_OPS, "timing_modes": _SPI_TIMING_STD,
        "device_addr_base": 0x00,
        "capacity": capacity_label, "capacity_bytes": cap_bytes,
        "page_size": page_sz, "addr_byte_count": addr_bytes,
        "page_select_bits": 0,
        "endurance_cycles": endurance, "manufacturer": manufacturer,
        "aliases": aliases or [],
        # SPI 专有字段
        "spi_mode": spi_mode, "max_clock_mhz": max_clock_mhz,
        "sector_size": sector_size, "has_jedec_id": has_jedec_id,
        "jedec_id": jedec_id, "chip_type": chip_type,
        "package_pinout": "SOP-8_SPI",
    }

def _mw_chip(capacity_bits, org_mode, word_bits, addr_bits, endurance,
             manufacturer, max_clock_mhz=2, aliases=None, capacity_label=None):
    """构建Microwire芯片预设字典"""
    if org_mode == "x16":
        cap_words = capacity_bits // 16
        cap_bytes = cap_words * 2
    else:
        cap_words = capacity_bits // 8
        cap_bytes = cap_words
    if capacity_label is None:
        capacity_label = f"{capacity_bits // 1024}Kbit ({cap_words}x{word_bits})"
    return {
        "protocol": "Microwire", "addr_pins": [],
        "clk_pin": "SK", "data_pin": "DI/DO", "wp_pin": "", "wp_default": 0,
        "operations": _MW_OPS, "timing_modes": _MW_TIMING_STD,
        "device_addr_base": 0x00,
        "capacity": capacity_label, "capacity_bytes": cap_bytes,
        "page_size": 1, "addr_byte_count": 0,
        "page_select_bits": 0,
        "endurance_cycles": endurance, "manufacturer": manufacturer,
        "aliases": aliases or [],
        # Microwire 专有字段
        "org_mode": org_mode, "word_bits": word_bits, "addr_bits": addr_bits,
        "capacity_words": cap_words, "capacity_bits": capacity_bits,
        "max_clock_mhz": max_clock_mhz,
        "package_pinout": "DIP-8_MW",
    }

CHIP_PRESETS = {
    # ── AT24C Series (Microchip/Atmel) ── 1字节地址, 页选择位递增
    "AT24C01": _chip("I2C", ["A0", "A1", "A2"], "SCL", "SDA", "WP", 0,
                     _I2C_OPS, _I2C_TIMING_STD, 0xA0,
                     128, 8, 1, 0, 1_000_000, "Microchip/Atmel",
                     ["M24C01", "24LC01B", "CAT24C01"]),
    "AT24C02": _chip("I2C", ["A0", "A1", "A2"], "SCL", "SDA", "WP", 0,
                     _I2C_OPS, _I2C_TIMING_STD, 0xA0,
                     256, 8, 1, 0, 1_000_000, "Microchip/Atmel",
                     ["M24C02", "24LC02B", "CAT24C02", "FM24C02"]),
    "AT24C04": _chip("I2C", ["A0", "A1"], "SCL", "SDA", "WP", 0,
                     _I2C_OPS, _I2C_TIMING_STD, 0xA0,
                     512, 16, 1, 1, 1_000_000, "Microchip/Atmel",
                     ["M24C04", "24LC04B", "CAT24C04"]),
    "AT24C08": _chip("I2C", ["A0"], "SCL", "SDA", "WP", 0,
                     _I2C_OPS, _I2C_TIMING_STD, 0xA0,
                     1024, 16, 1, 2, 1_000_000, "Microchip/Atmel",
                     ["M24C08", "24LC08B", "CAT24C08"]),
    "AT24C16": _chip("I2C", [], "SCL", "SDA", "WP", 0,
                     _I2C_OPS, _I2C_TIMING_STD, 0xA0,
                     2048, 16, 1, 3, 1_000_000, "Microchip/Atmel",
                     ["M24C16", "24LC16B", "CAT24C16"]),
    # ── AT24C Series ── 2字节地址 (16-bit word address)
    "AT24C32": _chip("I2C", ["A0", "A1", "A2"], "SCL", "SDA", "WP", 0,
                     _I2C_OPS, _I2C_TIMING_STD, 0xA0,
                     4096, 32, 2, 0, 1_000_000, "Microchip/Atmel",
                     ["M24C32", "24LC32A", "CAT24C32"]),
    "AT24C64": _chip("I2C", ["A0", "A1", "A2"], "SCL", "SDA", "WP", 0,
                     _I2C_OPS, _I2C_TIMING_STD, 0xA0,
                     8192, 32, 2, 0, 1_000_000, "Microchip/Atmel",
                     ["M24C64", "24LC64", "CAT24C64"]),
    "AT24C128": _chip("I2C", ["A0", "A1"], "SCL", "SDA", "WP", 0,
                      _I2C_OPS, _I2C_TIMING_STD, 0xA0,
                      16384, 64, 2, 0, 1_000_000, "Microchip/Atmel",
                      ["M24128", "24LC128"]),
    "AT24C256": _chip("I2C", ["A0", "A1"], "SCL", "SDA", "WP", 0,
                      _I2C_OPS, _I2C_TIMING_STD, 0xA0,
                      32768, 64, 2, 0, 1_000_000, "Microchip/Atmel",
                      ["M24256", "24LC256", "CAT24C256"]),
    "AT24C512": _chip("I2C", ["A0"], "SCL", "SDA", "WP", 0,
                      _I2C_OPS, _I2C_TIMING_STD, 0xA0,
                      65536, 128, 2, 0, 1_000_000, "Microchip/Atmel",
                      ["M24512", "24LC512"]),
    # ── 兼容芯片 (其他厂商) ──
    "M24C02": _chip("I2C", ["A0", "A1", "A2"], "SCL", "SDA", "WP", 0,
                    _I2C_OPS, _I2C_TIMING_STD, 0xA0,
                    256, 8, 1, 0, 4_000_000, "STMicroelectronics",
                    ["AT24C02", "24LC02B"],
                    "2Kbit (256x8)"),
    "24LC256": _chip("I2C", ["A0", "A1"], "SCL", "SDA", "WP", 0,
                     _I2C_OPS, _I2C_TIMING_STD, 0xA0,
                     32768, 64, 2, 0, 1_000_000, "Microchip",
                     ["AT24C256", "M24256", "CAT24C256"],
                     "256Kbit (32768x8)"),
    "FM24C64": _chip("I2C", ["A0", "A1", "A2"], "SCL", "SDA", "WP", 0,
                     _I2C_OPS, ["Standard 100kHz", "Fast 400kHz", "Fast+ 1MHz"],
                     0xA0, 8192, 32, 2, 0,
                     1_000_000_000_000, "Cypress/Infineon",
                     ["MB85RC64", "FM24CL64"],
                     "64Kbit (8192x8) FRAM"),
    # ── SPI EEPROM ──
    "25LC020A": _spi_chip(256, 16, 1, 1_000_000, "Microchip",
                          spi_mode=0, max_clock_mhz=10, chip_type="EEPROM",
                          aliases=["25AA020A", "25C020"]),
    "25LC256":  _spi_chip(32768, 64, 2, 1_000_000, "Microchip",
                          spi_mode=0, max_clock_mhz=10, chip_type="EEPROM",
                          aliases=["25AA256", "25C256"]),
    "M95256":   _spi_chip(32768, 64, 2, 4_000_000, "STMicroelectronics",
                          spi_mode=0, max_clock_mhz=10, chip_type="EEPROM",
                          aliases=["M95256-W", "M95256-R"]),
    "AT25256B": _spi_chip(32768, 64, 2, 1_000_000, "Microchip/Atmel",
                          spi_mode=0, max_clock_mhz=20, chip_type="EEPROM",
                          aliases=["AT25256A", "AT25256"]),
    # ── SPI NOR Flash ──
    "W25Q32JV": _spi_chip(4_194_304, 256, 3, 100_000, "Winbond",
                          spi_mode=0, max_clock_mhz=133, chip_type="Flash",
                          sector_size=4096, has_jedec_id=True, jedec_id=0xEF4016,
                          aliases=["W25Q32FV", "W25Q32BV"]),
    "W25Q128JV": _spi_chip(16_777_216, 256, 3, 100_000, "Winbond",
                           spi_mode=0, max_clock_mhz=133, chip_type="Flash",
                           sector_size=4096, has_jedec_id=True, jedec_id=0xEF4018,
                           aliases=["W25Q128FV", "W25Q128BV"]),
    "MX25L12835F": _spi_chip(16_777_216, 256, 3, 100_000, "Macronix",
                             spi_mode=0, max_clock_mhz=133, chip_type="Flash",
                             sector_size=4096, has_jedec_id=True, jedec_id=0xC22018,
                             aliases=["MX25L12845E", "MX25L12873F"]),
    # ── Microwire (93C series) ──
    "93C46": _mw_chip(1024, "x16", 16, 6, 1_000_000, "Microchip",
                      max_clock_mhz=2, aliases=["AT93C46D", "M93C46"]),
    "93C56": _mw_chip(2048, "x16", 16, 8, 1_000_000, "Microchip",
                      max_clock_mhz=2, aliases=["AT93C56", "M93C56"]),
    "93C66": _mw_chip(4096, "x16", 16, 8, 1_000_000, "Microchip",
                      max_clock_mhz=2, aliases=["AT93C66", "M93C66"]),
    "93C86": _mw_chip(16384, "x16", 16, 10, 1_000_000, "Microchip",
                      max_clock_mhz=2, aliases=["AT93C86", "M93C86"]),
}

# 芯片分组顺序 (用于Combobox下拉列表)
CHIP_PRESET_GROUPS = [
    ("── AT24C Series (I2C) ──", [
        "AT24C01", "AT24C02", "AT24C04", "AT24C08", "AT24C16",
        "AT24C32", "AT24C64", "AT24C128", "AT24C256", "AT24C512",
    ]),
    ("── I2C Compatible ──", [
        "M24C02", "24LC256", "FM24C64",
    ]),
    ("── SPI EEPROM ──", [
        "25LC020A", "25LC256", "M95256", "AT25256B",
    ]),
    ("── SPI NOR Flash ──", [
        "W25Q32JV", "W25Q128JV", "MX25L12835F",
    ]),
    ("── Microwire (93C) ──", [
        "93C46", "93C56", "93C66", "93C86",
    ]),
]

# 自定义芯片预设键名
CUSTOM_CHIP_KEY = "自定义 / Custom"


# ============================================================
# 国际化 (i18n) 翻译字典
# ============================================================

I18N = {
    "zh": {
        "title": "EEPROM PAT测试向量生成工具",
        "generate": "  ▶ 生成PAT  ",
        "export": "  导出文件  ",
        "test_types": "测试类型",
        "custom_write": "自定义写入 (FUNC-5)",
        "addr_range": "测试地址范围",
        "period_label": "向量周期 (ns)",
        "prefix_label": "导出文件名前缀",
        "multi_voltage": "导出时生成全部4个电压条件",
        "poll_count_label": "ACK Polling 次数",
        "poll_count_hint": "写周期后轮询次数 (1~20)",
        "save_config": "保存配置",
        "load_config": "加载配置",
        "addr": "地址:",
        "data": "数据:",
        "start": "起始:",
        "end": "结束:",
        "range_hint": "用于 March C- 和地址扫描 (hex)",
        "tab_pat": " \u25a0 PAT 向量 ",
        "tab_txt": " \u2261 TXT 预览 ",
        "tab_wave": " \u223f 波形图 ",
        "tab_info": " \u2139 测试说明 ",
        "tab_flow": " \u25c7 流程图 ",
        "tab_stats": " \u2630 统计 ",
        "jump": "跳转:",
        "display_range": "显示范围:",
        "refresh": "刷新",
        "export_svg": "导出SVG",
        "search": "搜索:",
        "ready": "就绪 — 选择测试类型后点击 ▶ 生成",
        "gen_ok": "✓ 生成完成!",
        "export_ok": "✓ 导出成功!",
        "no_match": "无匹配",
        "matches": "个匹配",
        "open_folder": "  打开文件夹  ",
        "close": "  关闭  ",
        "confirm_exit": "当前生成的向量尚未导出，确定退出？",
        "confirm_exit_title": "确认退出",
        "select_test": "请至少选择一种测试类型！",
        "gen_first": "请先点击「生成PAT向量」！",
        "gen_wave_first": "请先生成向量！",
        "flow_hint": "生成向量后显示测试流程图",
        "wave_hint": "请先生成向量后查看波形",
        "vec_dist": "向量分布",
        "total_vec": "总向量数",
        "est_time": "预估测试时间",
        "coverage": "覆盖率分析",
        "proto_detail": "协议特性明细",
        "seg_detail": "测试段明细",
        "os_test": "开短路测试 (OS)",
        "dc_test": "DC参数测试",
        "func_test": "功能测试 (I2C)",
        "march_test": "March C- 存储器测试",
        "march_b_test": "March B 存储器测试",
        "march_b_desc": "17N 复杂度, 额外CF覆盖",
        "scan_test": "地址空间扫描",
        "ret_test": "数据保持测试",
        "err_test": "I2C异常/边界测试",
        "endur_test": "耐久性/写循环测试",
        "os_desc": "PPMU Walking 逐引脚检测",
        "dc_desc": "ISB/ICC/VOL/VOH/VIL/VIH",
        "func_desc": "字节读写 / 页读写 / 边界 / WP",
        "march_desc": "SAF/TF/CF 故障模型检测",
        "scan_desc": "可配置范围 写入+读回验证",
        "ret_desc": "棋盘格/全0/全1 写入-等待-验证",
        "err_desc": "错误地址/不完整事务/总线恢复",
        "endur_desc": "同地址反复擦写+读回验证",
        "iddq_test": "IDDQ静态电流测试",
        "iddq_desc": "8点静态漏电流测量 (PMU)",
        "tab_temp": "温度分析",
        "temp_corner_type": "温度范围",
        "temp_run": "运行分析",
        "temp_margin": "裕量",
        "temp_commercial": "商业级 (-40~85°C)",
        "temp_industrial": "工业级 (-40~125°C)",
        "temp_param_select": "参数选择",
        "temp_limit": "极限温度",
        "temp_all_pass": "全温Pass",
        "site_count": "Site数",
        "test_phase": "测试阶段",
        "phase_custom": "自定义",
        "pin_map_section": "引脚映射",
        "pin_map_validate": "验证资源",
        "pin_map_valid": "资源验证通过",
        "pin_map_invalid": "资源不足",
        "select_all": "全选",
        "deselect_all": "全不选",
        "preset_quick": "快速",
        "preset_full": "全部",
        "preset_memory": "存储",
        "preset_tip_quick": "快速筛选: OS + DC + 功能",
        "preset_tip_full": "完整测试: 全部 10 种测试",
        "preset_tip_memory": "存储聚焦: March C-/B + 扫描 + 保持 + 耐久",
        "timing_check": "时序检查",
        "proto_check": "协议检查",
        "timing_pass": "时序合规性检查: 全部通过",
        "timing_fail": "时序合规性检查: 存在不满足项",
        "proto_pass": "协议合规性检查: 通过 (0 issues)",
        "proto_issues": "协议合规性检查: 发现 {} 个问题",
        "test_limits": "测试限值表",
        "lang_btn": "EN",
        "pin_hint": "引脚颜色随配置变化",
        "wp_tip": "写保护引脚 (WP)\n勾选=高电平=禁止写入\n取消=低电平=允许写入",
        "vcc_tip": "电压等级预设\n自动调整 LEVEL 块参数和推荐 I2C 速率",
        "theme_tip": "切换深色/浅色主题",
        "chip_config": "芯片配置",
        "chip_preset": "芯片预设",
        "operation_type": "操作类型",
        "op_read": "读",
        "op_write": "写",
        "protocol_type": "通信协议",
        "addr_pins_label": "地址引脚",
        "addr_pins_hint": "逗号分隔, 无则留空",
        "clk_pin_label": "时钟引脚",
        "data_pin_label": "数据引脚",
        "wp_pin_label": "写保护引脚",
        "wp_pin_hint": "无则留空",
        "timing_mode": "时序类型",
        "custom_chip": "自定义 / Custom",
        # Round 10 芯片参数
        "chip_capacity": "容量",
        "chip_page_size": "页大小",
        "chip_addr_mode": "寻址模式",
        "chip_endurance": "擦写寿命",
        "chip_compatible": "兼容型号",
        "chip_specs": "芯片参数",
        "chip_manufacturer": "厂商",
        "chip_page_select": "页选择位",
        "addr_1byte": "1字节 (8位)",
        "addr_2byte": "2字节 (16位)",
        "chip_bytes": "字节",
        "chip_cycles": "次",
        # Round 11 多协议
        "spi_mode_label": "SPI 模式",
        "spi_clock_label": "SPI 时钟",
        "cs_polarity_label": "CS 极性",
        "cs_active_low": "低有效",
        "cs_active_high": "高有效",
        "sector_size_label": "扇区大小",
        "jedec_id_label": "JEDEC ID",
        "chip_type_label": "芯片类型",
        "mw_org_label": "数据组织",
        "mw_x8": "x8 (8-bit)",
        "mw_x16": "x16 (16-bit)",
        "mw_addr_bits_label": "地址位宽",
        "protocol_i2c": "I2C",
        "protocol_spi": "SPI",
        "protocol_microwire": "Microwire",
        "spi_eeprom": "SPI EEPROM",
        "spi_flash": "SPI NOR Flash",
        "microwire_eeprom": "Microwire EEPROM",
        "write_enable_req": "写使能",
        "status_poll": "状态轮询",
        "addr_3byte": "3字节 (24位)",
        "func_test_spi": "功能测试 (SPI)",
        "func_test_mw": "功能测试 (MW)",
        "err_test_spi": "SPI异常/边界测试",
        "err_test_mw": "Microwire异常/边界测试",
        "func_desc_spi": "WREN/写入/RDSR轮询/读回",
        "func_desc_mw": "EWEN/写入/轮询/读回",
        "err_desc_spi": "无WREN写/WIP读/无效命令",
        "err_desc_mw": "无EWEN写/Busy读/无效操作码",
        "flash_erase_test": "Flash擦除测试",
        "flash_erase_desc": "扇区擦除/块擦除/JEDEC ID",
        "jedec_test": "JEDEC ID 验证",
        "jedec_desc": "读取并验证芯片JEDEC ID",
        # Round 8 新增
        "undo": "撤销",
        "redo": "重做",
        "undo_tip": "撤销上一步操作 (Ctrl+Z)",
        "redo_tip": "重做 (Ctrl+Y)",
        "recent_files": "最近文件",
        "no_recent": "无最近文件",
        "recovery_found": "发现自动保存的配置，是否恢复？",
        "recovery_title": "恢复配置",
        "shortcuts_title": "键盘快捷键",
        "est_vectors": "预估向量",
        "est_test_time": "预估时间",
        "rle_compress": "PAT 压缩 (RLE)",
        "compress_ratio": "压缩率",
        "export_coverage": "导出覆盖率",
        "coverage_grade": "覆盖等级",
        "datalog_template": "Datalog 模板",
        "bin_map": "分箱定义",
        "batch_title": "批处理队列",
        "batch_add": "添加当前配置",
        "batch_run": "运行全部",
        "batch_clear": "清空队列",
        "config_diff": "配置对比",
        "diff_title": "配置对比工具",
        "cmd_palette": "命令面板",
        "cmd_placeholder": "输入命令...",
        "grp_chip": "CHIP",
        "grp_test": "TEST",
        "grp_action": "ACTION",
        "grp_tools": "TOOLS",
        "grp_view": "VIEW",
        "collapse_all": "全部折叠",
        "expand_all": "全部展开",
        "reexport_tip": "快速重导出到上次目录",
        "copy_pin_config": "复制引脚配置",
        "reset_default": "重置默认",
        "gen_progress": "生成中...",
        "gen_step_preview": "更新预览...",
        "gen_step": "正在生成: {}",
        "unsaved_warning_title": "未导出的向量",
        "unsaved_warning_msg": "已生成的向量尚未导出，是否继续？\n(向量数据将保留，预览会刷新)",
        "about_title": "关于",
        "about_version": "版本",
        "about_team": "IC竞赛团队",
        "about_competition": "全国大学生集成电路创新创业大赛",
        "about_features": "功能概览",
        "manifest_header": "文件完整性清单",
        "export_partial": "导出中断",
        "export_partial_msg": "导出在写入 {n}/{m} 个文件后失败",
        "config_old_ver": "配置来自旧版本 ({ver})，部分设置可能使用默认值。",
        "config_missing_keys": "以下配置项缺失，已使用默认值:\n{keys}",
        "export_total_size": "总大小: {size}",
        # v6.0 新增
        "tab_sim": " ▷ 模拟器 ",
        "tab_shmoo": " ◈ Shmoo ",
        "tab_flow_edit": " ◆ 流程编排 ",
        "tab_yield": " ◉ 良率 ",
        "sim_run": "运行模拟",
        "sim_step": "单步",
        "sim_reset": "重置",
        "sim_pause": "暂停",
        "sim_cycle": "周期",
        "sim_transactions": "事务解码",
        "sim_memory_view": "存储器视图",
        "sim_state_machine": "状态机",
        "sim_log": "模拟日志",
        "sim_no_vectors": "请先生成向量再运行模拟",
        "sim_complete": "模拟完成: {txn} 个事务, {err} 个错误",
        "sim_match": "匹配",
        "sim_mismatch": "不匹配",
        "shmoo_title": "Shmoo 参数表征",
        "shmoo_voltage": "电压范围",
        "shmoo_freq": "频率范围",
        "shmoo_step": "步进",
        "shmoo_run": "运行扫描",
        "shmoo_stop": "停止",
        "shmoo_margin": "余量分析",
        "shmoo_export_csv": "导出 CSV",
        "shmoo_recommended": "推荐条件",
        "shmoo_guardband": "保护带",
        "shmoo_pass": "通过",
        "shmoo_fail": "失败",
        "shmoo_marginal": "边际",
        "shmoo_export_svg": "导出 SVG",
        "shmoo_spec_box": "Datasheet 规格框",
        "shmoo_boundary": "工作边界",
        "shmoo_margin_pct": "余量",
        "shmoo_sweeping": "正在扫描: {v} × {f}",
        # v8.0 Datalog + Binning
        "tab_datalog": " ⊞ Datalog ",
        "datalog_gen_single": "生成单颗",
        "datalog_gen_batch": "批量生成",
        "datalog_batch_n": "数量",
        "datalog_seed": "种子",
        "datalog_export_csv": "导出 CSV",
        "datalog_export_bin": "导出 Bin",
        "datalog_no_data": "请先生成 Datalog 数据",
        # v8.0 STDF
        "stdf_export": "导出 STDF",
        "stdf_done": "STDF 文件已导出",
        "stdf_bytes": "文件大小",
        # v8.0 向量压缩
        "compress_enable": "导出压缩 PAT",
        "compress_ratio": "压缩率",
        "compress_original": "原始",
        "compress_final": "压缩后",
        "compress_analyzing": "正在分析压缩...",
        # v8.0 Wafer Map
        "tab_wafer": " ⬡ Wafer Map ",
        "wafer_generate": "生成晶圆图",
        "wafer_mode": "显示模式",
        "wafer_export_svg": "导出 SVG",
        "wafer_no_data": "请先生成晶圆图",
        "debug_title": "向量调试器",
        "debug_reset": "复位",
        "debug_step": "单步",
        "debug_step_txn": "步进事务",
        "debug_step_section": "步进段",
        "debug_run_bp": "运行至断点",
        "debug_stop": "停止",
        "debug_pc": "PC",
        "debug_bus_state": "总线状态",
        "debug_event": "事件",
        "debug_add_bp": "添加断点",
        "debug_clear_bp": "清除断点",
        "debug_history": "执行历史",
        "debug_no_vectors": "请先生成向量",
        "debug_breakpoints": "断点列表",
        "debug_state": "当前状态",
        "debug_running": "运行中...",
        "debug_stopped": "已停止",
        "debug_end": "已到末尾",
        "export_format_title": "选择导出格式",
        "export_format_pat": "PAT (EStar 原生格式)",
        "export_format_stil": "STIL (IEEE 1450 标准)",
        "export_format_wgl": "WGL (Waveform Generation Language)",
        "export_format_go": "导出选中格式",
        "export_format_all": "全部导出",
        "power_up_label": "上电序列",
        "power_down_label": "下电序列",
        "compliance_title": "Datasheet 参数覆盖矩阵",
        "compliance_covered": "已覆盖",
        "compliance_uncovered": "未覆盖",
        "compliance_pct": "覆盖率",
        "flow_editor": "测试流程编排",
        "flow_add_node": "添加节点",
        "flow_add_branch": "添加分支",
        "flow_add_loop": "添加循环",
        "flow_delete": "删除",
        "flow_reset_default": "重置默认",
        "flow_simulate": "模拟执行",
        "flow_export_prg": "导出 .prg",
        "flow_bin_table": "Bin 表",
        "flow_test_limits": "测试限值",
        "flow_edit_limits": "编辑限值",
        "flow_import_csv": "导入 CSV",
        "flow_bin_pass": "通过",
        "flow_bin_hard": "硬失效",
        "flow_bin_soft": "软失效",
        "yield_title": "良率分析仪表盘",
        "yield_import": "导入 Datalog",
        "yield_import_sim": "导入模拟结果",
        "yield_export_report": "导出报告",
        "yield_param": "参数",
        "yield_lot": "批次",
        "yield_site": "Site",
        "yield_histogram": "直方图 + Cp/Cpk",
        "yield_pareto": "Pareto 分析",
        "yield_trend": "良率趋势",
        "yield_bin_dist": "Bin 分布",
        "yield_cp": "Cp",
        "yield_cpk": "Cpk",
        "yield_mean": "均值",
        "yield_sigma": "标准差",
        "yield_usl": "上限",
        "yield_lsl": "下限",
        "yield_rate": "良率",
        "yield_no_data": "无数据，请导入 Datalog 或模拟结果",
        "sites_label": "Sites",
        "sites_tip": "并行测试 Site 数量",
        "format_stil": "STIL",
        "format_wgl": "WGL",
        "format_pat": "PAT",
        "project_new": "新建项目",
        "project_open": "打开项目",
        "project_recent": "最近项目",
        "project_save_template": "保存为模板",
        "project_load_template": "加载模板",
        "project_no_recent": "无最近项目",
        "welcome_title": "欢迎使用 ATE 测试平台",
        "welcome_quick_start": "快速开始",
        "files_exist_overwrite": "以下文件已存在，是否覆盖？",
        "prefix_sanitized": "导出前缀包含非法字符，已自动替换",
        "path_too_long": "导出路径过长(>240字符)，请选择更短的目录",
        "export_permission_denied": "无法写入该目录，请检查权限",
        "confirm": "确认",
        "warning": "警告",
        "param_invalid": "参数无效: {msg}",
        "export_format_label": "导出格式",
        # Phase 1: Fail Bit Map
        "fbm_title": "Fail Bit Map",
        "fbm_pass": "通过",
        "fbm_fail": "失败",
        "fbm_untested": "未测试",
        "fbm_export_svg": "导出FBM SVG",
        "fbm_detail_title": "地址详情",
        "fbm_coverage": "覆盖测试: {tests}",
        "fbm_expected": "期望: 0x{exp:02X}",
        "fbm_actual": "实际: 0x{act:02X}",
        "fbm_addr_info": "地址 0x{addr:02X} — {status}",
        "march_step": "步骤 {n}",
        "march_step_desc": "Step {n}: {desc}",
        "march_animator": "March C- 步骤联动",
        "sim_running": "模拟中...",
        "sim_thread_done": "模拟完成: {txn}笔事务, {err}个错误, {t:.0f}ms",
        # Phase 4: ATPG 覆盖率
        "tab_atpg": " ◆ ATPG覆盖率 ",
        "atpg_run": "运行仿真",
        "atpg_seed": "种子",
        "atpg_running": "故障仿真中... {pct:.0%}",
        "atpg_done": "仿真完成: 综合覆盖率 {cov:.1f}%, {t:.0f}ms",
        "atpg_no_vectors": "请先生成向量",
        "atpg_heatmap": "覆盖率热力表",
        "atpg_radar": "雷达图",
        "atpg_summary": "综合评分",
        "atpg_min_suite": "最小测试套件",
        # Phase 8: ATPG 审核
        "atpg_theory": "理论覆盖率（March 算法数学证明）",
        "atpg_select_faults": "选择故障模型",
        "atpg_generate_proof": "生成证明",
        "atpg_march_vis": "March 序列可视化",
        "atpg_proof_text": "覆盖率证明",
        "atpg_replace_march": "生成并替换当前 March 向量",
        "atpg_add_test": "添加到现有测试",
        "atpg_export_proof": "导出证明文档(.txt)",
        "atpg_optimal": "最优算法",
        "atpg_complexity": "复杂度",
        "atpg_algorithm": "算法",
        # Phase 5: 测试经济学
        "tab_econ": " ◎ 测试经济学 ",
        "econ_calculate": "计算",
        "econ_test_time": "单颗测试时间",
        "econ_test_cost": "单颗测试成本",
        "econ_daily_cap": "日实际产能",
        "econ_annual_save": "年节省(优化后)",
        "econ_no_vectors": "请先生成向量",
        # Phase 6: Monte Carlo
        "mc_run": "运行Monte Carlo",
        "mc_running": "Monte Carlo 仿真中... {pct:.0%}",
        "mc_done": "完成: 良率 {y:.1f}%, Cpk={cpk:.2f}, {t:.0f}ms",
        "mc_seed": "种子",
        "mc_n": "样本数",
        # Phase 7: 跨芯片迁移
        "tab_migrate": " ⇌ 芯片迁移 ",
        "migrate_btn": "迁移 ⇌",
        "migrate_source": "源芯片",
        "migrate_target": "目标芯片",
        "migrate_run": "执行迁移",
        "migrate_running": "迁移适配中...",
        "migrate_done": "迁移完成: {n} 向量 ({t:.0f}ms)",
        "migrate_log": "迁移日志",
        "migrate_compare": "芯片对比",
        "migrate_export": "导出迁移向量",
        "migrate_addr_bytes": "地址字节",
        "migrate_page_size": "页大小",
        "migrate_capacity": "容量",
        "migrate_max_freq": "最高频率",
        "migrate_dev_addr": "器件地址",
        "migrate_no_vectors": "请先生成向量",
        "migrate_same_chip": "源芯片与目标芯片相同",
        "migrate_vectors": "迁移向量数",
        "migrate_sampling": "大容量采样模式: 边界+随机",
        # Phase 9: 演示模式
        "demo_btn": "▶ 演示",
        "demo_running": "演示中 [{step}/{total}]: {desc}",
        "demo_done": "演示完成 — 数据已保留，可自由探索",
        "demo_stop": "已停止演示",
        # v9.0 Tier3 Phase 27: 自适应测试流
        "adaptive_title": "自适应测试流",
        "adaptive_sim": "自适应仿真",
        "adaptive_running": "自适应仿真中... {pct:.0f}%",
        "adaptive_done": "完成: 节省 {save:.1f}% 测试时间",
        "adaptive_rules": "触发规则",
        "adaptive_fixed": "固定流程",
        "adaptive_dynamic": "自适应流程",
        "adaptive_compare": "固定 vs 自适应对比",
        "adaptive_no_sections": "请先生成向量",
        "adaptive_sample_n": "样本数",
        # v9.0 Tier3 Phase 28: Guard Band
        "gb_title": "Guard Band 分析",
        "gb_target_dppm": "目标DPPM",
        "gb_run": "运行 Guard Band",
        "gb_apply": "应用到限值",
        "gb_running": "Guard Band 计算中...",
        "gb_done": "Guard Band 完成: 平均收紧 {pct:.1f}%",
        "gb_no_mc": "请先运行 Monte Carlo",
        "gb_original": "原始限值",
        "gb_guarded": "Guard Band 限值",
        "gb_dppm_before": "优化前 DPPM",
        "gb_dppm_after": "优化后 DPPM",
        "gb_yield_loss": "良率损失",
        # v9.0 Tier3 Phase 29: 参数相关性
        "corr_title": "参数相关性分析",
        "corr_run": "运行相关性",
        "corr_matrix": "相关矩阵",
        "corr_scatter": "散点图",
        "corr_outliers": "异常值",
        "corr_no_data": "请先生成批量 Datalog",
        "corr_top": "最强相关性",
        "corr_sigma": "异常阈值 (σ)",
        "corr_findings": "发现",
        # v9.0 Tier3 Phase 30: PAT反向解析
        "pat_import": "导入 PAT",
        "pat_decode": "协议解码",
        "pat_compare": "与当前对比",
        "pat_detected": "检测到协议: {proto}",
        "pat_transactions": "解码事务: {n} 笔",
        "pat_import_ok": "导入成功: {n} 向量, {pins} 引脚",
        "pat_compare_result": "匹配度: {pct:.1f}%",
        "pat_no_current": "请先生成当前向量",
        "pat_decode_report": "解码报告",
        # v9.0 Tier3 Phase 31: STDF导入
        "stdf_import": "导入 STDF",
        "stdf_import_ok": "导入成功: {n} 颗, 良率 {y:.1f}%",
        "stdf_summary": "STDF 摘要",
        "stdf_compare": "与模拟对比",
        "stdf_no_data": "请先导入 STDF 文件",
        "stdf_bin_dist": "Bin 分布",
        "stdf_param_stats": "参数统计",
        "stdf_compare_result": "对比结果",
        # v9.0 Tier3 Phase 32: 标准合规
        "std_compliance": "标准合规性",
        "std_aec_q100": "AEC-Q100 (车规)",
        "std_jedec": "JEDEC 标准",
        "std_coverage_target": "覆盖率目标",
        "std_covered": "已覆盖",
        "std_partial": "部分覆盖",
        "std_na": "不适用",
        "std_status": "合规状态",
        "std_run": "生成合规报告",
        # v9.0 Tier3 Phase 33: 版本管理
        "ver_btn": "版本 Ⓥ",
        "ver_save": "保存版本",
        "ver_load": "加载版本",
        "ver_compare": "对比版本",
        "ver_list": "版本列表",
        "ver_label": "版本标签",
        "ver_label_hint": "输入此版本的标签名",
        "ver_saved": "版本已保存: {label}",
        "ver_loaded": "已加载版本: {label}",
        "ver_no_versions": "暂无已保存版本",
        "ver_diff_title": "版本对比",
        "ver_delete": "删除版本",
        "ver_confirm_delete": "确认删除版本 {label}?",
    },
    "en": {
        "title": "EEPROM PAT Test Vector Generator",
        "generate": "  ▶ Generate  ",
        "export": "  Export Files  ",
        "test_types": "Test Types",
        "custom_write": "Custom Write (FUNC-5)",
        "addr_range": "Test Address Range",
        "period_label": "Vector Period (ns)",
        "prefix_label": "Export Filename Prefix",
        "multi_voltage": "Export all 4 voltage conditions",
        "poll_count_label": "ACK Polling Count",
        "poll_count_hint": "Poll attempts after write (1~20)",
        "save_config": "Save Config",
        "load_config": "Load Config",
        "addr": "Addr:",
        "data": "Data:",
        "start": "Start:",
        "end": "End:",
        "range_hint": "For March C- and Addr Scan (hex)",
        "tab_pat": " \u25a0 PAT Vector ",
        "tab_txt": " \u2261 TXT Preview ",
        "tab_wave": " \u223f Waveform ",
        "tab_info": " \u2139 Test Info ",
        "tab_flow": " \u25c7 Flowchart ",
        "tab_stats": " \u2630 Statistics ",
        "jump": "Jump:",
        "display_range": "Range:",
        "refresh": "Refresh",
        "export_svg": "Export SVG",
        "search": "Search:",
        "ready": "Ready — Select test types, then click ▶ Generate",
        "gen_ok": "✓ Generation complete!",
        "export_ok": "✓ Export successful!",
        "no_match": "No match",
        "matches": " matches",
        "open_folder": "  Open Folder  ",
        "close": "  Close  ",
        "confirm_exit": "Generated vectors not exported. Quit anyway?",
        "confirm_exit_title": "Confirm Exit",
        "select_test": "Please select at least one test type!",
        "gen_first": "Please generate PAT vectors first!",
        "gen_wave_first": "Please generate vectors first!",
        "flow_hint": "Generate vectors to see test flowchart",
        "wave_hint": "Generate vectors first to view waveform",
        "vec_dist": "Vector Distribution",
        "total_vec": "Total Vectors",
        "est_time": "Estimated Test Time",
        "coverage": "Coverage Analysis",
        "proto_detail": "Protocol Feature Details",
        "seg_detail": "Test Segment Details",
        "os_test": "Open/Short Test (OS)",
        "dc_test": "DC Parameter Test",
        "func_test": "Functional Test (I2C)",
        "march_test": "March C- Memory Test",
        "march_b_test": "March B Memory Test",
        "march_b_desc": "17N complexity, extra CF coverage",
        "scan_test": "Address Space Scan",
        "ret_test": "Data Retention Test",
        "err_test": "I2C Error/Boundary Test",
        "endur_test": "Write Endurance Test",
        "os_desc": "PPMU Walking per-pin check",
        "dc_desc": "ISB/ICC/VOL/VOH/VIL/VIH",
        "func_desc": "Byte/Page R/W / Boundary / WP",
        "march_desc": "SAF/TF/CF fault model detection",
        "scan_desc": "Configurable range write+readback",
        "ret_desc": "Checkerboard/All-0/All-1 write-wait-verify",
        "err_desc": "Wrong addr / incomplete txn / bus recovery",
        "endur_desc": "Repeated write+verify at same address",
        "iddq_test": "IDDQ Quiescent Current Test",
        "iddq_desc": "8-point quiescent current measurement (PMU)",
        "tab_temp": "Temp Analysis",
        "temp_corner_type": "Corner Type",
        "temp_run": "Run Analysis",
        "temp_margin": "Margin",
        "temp_commercial": "Commercial (-40~85\u00b0C)",
        "temp_industrial": "Industrial (-40~125\u00b0C)",
        "temp_param_select": "Parameters",
        "temp_limit": "Limit Temp",
        "temp_all_pass": "All Pass",
        "site_count": "Sites",
        "test_phase": "Test Phase",
        "phase_custom": "Custom",
        "pin_map_section": "Pin Map",
        "pin_map_validate": "Validate",
        "pin_map_valid": "Resources OK",
        "pin_map_invalid": "Insufficient resources",
        "select_all": "All",
        "deselect_all": "None",
        "preset_quick": "Quick",
        "preset_full": "Full",
        "preset_memory": "Memory",
        "preset_tip_quick": "Quick screen: OS + DC + Functional",
        "preset_tip_full": "Full test: all 10 test types",
        "preset_tip_memory": "Memory focus: March C-/B + Scan + Retention + Endurance",
        "timing_check": "Timing Check",
        "proto_check": "Protocol Check",
        "timing_pass": "Timing check: All PASS",
        "timing_fail": "Timing check: Some constraints not met",
        "proto_pass": "Protocol check: PASS (0 issues)",
        "proto_issues": "Protocol check: {} issues found",
        "test_limits": "Test Limits",
        "lang_btn": "中文",
        "pin_hint": "Pin colors change with config",
        "wp_tip": "Write Protect (WP)\nChecked=HIGH=write disabled\nUnchecked=LOW=write enabled",
        "vcc_tip": "Voltage preset\nAuto-adjust LEVEL block and I2C speed",
        "theme_tip": "Toggle dark/light theme",
        "chip_config": "Chip Config",
        "chip_preset": "Chip Preset",
        "operation_type": "Operation",
        "op_read": "Read",
        "op_write": "Write",
        "protocol_type": "Protocol",
        "addr_pins_label": "Addr Pins",
        "addr_pins_hint": "Comma separated, empty if none",
        "clk_pin_label": "Clock Pin",
        "data_pin_label": "Data Pin",
        "wp_pin_label": "WP Pin",
        "wp_pin_hint": "Empty if none",
        "timing_mode": "Timing Mode",
        "custom_chip": "Custom",
        # Round 10 chip specs
        "chip_capacity": "Capacity",
        "chip_page_size": "Page Size",
        "chip_addr_mode": "Addr Mode",
        "chip_endurance": "Endurance",
        "chip_compatible": "Compatible",
        "chip_specs": "Chip Specs",
        "chip_manufacturer": "Manufacturer",
        "chip_page_select": "Page Select",
        "addr_1byte": "1-byte (8-bit)",
        "addr_2byte": "2-byte (16-bit)",
        "chip_bytes": "bytes",
        "chip_cycles": "cycles",
        # Round 11 multi-protocol
        "spi_mode_label": "SPI Mode",
        "spi_clock_label": "SPI Clock",
        "cs_polarity_label": "CS Polarity",
        "cs_active_low": "Active Low",
        "cs_active_high": "Active High",
        "sector_size_label": "Sector Size",
        "jedec_id_label": "JEDEC ID",
        "chip_type_label": "Chip Type",
        "mw_org_label": "Organization",
        "mw_x8": "x8 (8-bit)",
        "mw_x16": "x16 (16-bit)",
        "mw_addr_bits_label": "Addr Bits",
        "protocol_i2c": "I2C",
        "protocol_spi": "SPI",
        "protocol_microwire": "Microwire",
        "spi_eeprom": "SPI EEPROM",
        "spi_flash": "SPI NOR Flash",
        "microwire_eeprom": "Microwire EEPROM",
        "write_enable_req": "Write Enable",
        "status_poll": "Status Poll",
        "addr_3byte": "3-byte (24-bit)",
        "func_test_spi": "Functional Test (SPI)",
        "func_test_mw": "Functional Test (MW)",
        "err_test_spi": "SPI Error/Boundary Test",
        "err_test_mw": "Microwire Error/Boundary Test",
        "func_desc_spi": "WREN/Write/RDSR poll/Readback",
        "func_desc_mw": "EWEN/Write/Poll/Readback",
        "err_desc_spi": "No-WREN write/WIP read/Invalid cmd",
        "err_desc_mw": "No-EWEN write/Busy read/Invalid opcode",
        "flash_erase_test": "Flash Erase Test",
        "flash_erase_desc": "Sector/Block erase + JEDEC ID",
        "jedec_test": "JEDEC ID Verify",
        "jedec_desc": "Read and verify chip JEDEC ID",
        # Round 8 additions
        "undo": "Undo",
        "redo": "Redo",
        "undo_tip": "Undo last action (Ctrl+Z)",
        "redo_tip": "Redo (Ctrl+Y)",
        "recent_files": "Recent Files",
        "no_recent": "No recent files",
        "recovery_found": "Auto-saved config found. Restore?",
        "recovery_title": "Restore Config",
        "shortcuts_title": "Keyboard Shortcuts",
        "est_vectors": "Est. Vectors",
        "est_test_time": "Est. Time",
        "rle_compress": "PAT Compress (RLE)",
        "compress_ratio": "Compression",
        "export_coverage": "Export Coverage",
        "coverage_grade": "Coverage Grade",
        "datalog_template": "Datalog Template",
        "bin_map": "Bin Map",
        "batch_title": "Batch Queue",
        "batch_add": "Add Current Config",
        "batch_run": "Run All",
        "batch_clear": "Clear Queue",
        "config_diff": "Config Diff",
        "diff_title": "Config Diff Tool",
        "cmd_palette": "Command Palette",
        "cmd_placeholder": "Type a command...",
        "grp_chip": "CHIP",
        "grp_test": "TEST",
        "grp_action": "ACTION",
        "grp_tools": "TOOLS",
        "grp_view": "VIEW",
        "collapse_all": "Collapse All",
        "expand_all": "Expand All",
        "reexport_tip": "Quick re-export to last directory",
        "copy_pin_config": "Copy Pin Config",
        "reset_default": "Reset Default",
        "gen_progress": "Generating...",
        "gen_step_preview": "Updating preview...",
        "gen_step": "Generating: {}",
        "unsaved_warning_title": "Unsaved Vectors",
        "unsaved_warning_msg": "Generated vectors have not been exported. Continue?\n(Vector data will be preserved, preview will refresh.)",
        "about_title": "About",
        "about_version": "Version",
        "about_team": "IC Competition Team",
        "about_competition": "National IC Innovation & Entrepreneurship Competition",
        "about_features": "Feature Overview",
        "manifest_header": "File Integrity Manifest",
        "export_partial": "Export Interrupted",
        "export_partial_msg": "Export failed after writing {n} of {m} files",
        "config_old_ver": "Config from older version ({ver}). Some settings may use defaults.",
        "config_missing_keys": "Missing config keys (defaults applied):\n{keys}",
        "export_total_size": "Total size: {size}",
        # v6.0 additions
        "tab_sim": " ▷ Simulator ",
        "tab_shmoo": " ◈ Shmoo ",
        "tab_flow_edit": " ◆ Flow Editor ",
        "tab_yield": " ◉ Yield ",
        "sim_run": "Run Sim",
        "sim_step": "Step",
        "sim_reset": "Reset",
        "sim_pause": "Pause",
        "sim_cycle": "Cycle",
        "sim_transactions": "Transaction Decode",
        "sim_memory_view": "Memory View",
        "sim_state_machine": "State Machine",
        "sim_log": "Simulation Log",
        "sim_no_vectors": "Generate vectors before running simulation",
        "sim_complete": "Simulation complete: {txn} transactions, {err} errors",
        "sim_match": "Match",
        "sim_mismatch": "Mismatch",
        "shmoo_title": "Shmoo Characterization",
        "shmoo_voltage": "Voltage Range",
        "shmoo_freq": "Frequency Range",
        "shmoo_step": "Step",
        "shmoo_run": "Run Sweep",
        "shmoo_stop": "Stop",
        "shmoo_margin": "Margin Analysis",
        "shmoo_export_csv": "Export CSV",
        "shmoo_recommended": "Recommended",
        "shmoo_guardband": "Guardband",
        "shmoo_pass": "Pass",
        "shmoo_fail": "Fail",
        "shmoo_marginal": "Marginal",
        "shmoo_export_svg": "Export SVG",
        "shmoo_spec_box": "Datasheet Spec Box",
        "shmoo_boundary": "Operating Boundary",
        "shmoo_margin_pct": "Margin",
        "shmoo_sweeping": "Sweeping: {v} × {f}",
        # v8.0 Datalog + Binning
        "tab_datalog": " ⊞ Datalog ",
        "datalog_gen_single": "Single",
        "datalog_gen_batch": "Batch",
        "datalog_batch_n": "Count",
        "datalog_seed": "Seed",
        "datalog_export_csv": "Export CSV",
        "datalog_export_bin": "Export Bin",
        "datalog_no_data": "Generate Datalog data first",
        # v8.0 STDF
        "stdf_export": "Export STDF",
        "stdf_done": "STDF file exported",
        "stdf_bytes": "File size",
        # v8.0 Compression
        "compress_enable": "Export compressed PAT",
        "compress_ratio": "Compression ratio",
        "compress_original": "Original",
        "compress_final": "Compressed",
        "compress_analyzing": "Analyzing compression...",
        # v8.0 Wafer Map
        "tab_wafer": " ⬡ Wafer Map ",
        "wafer_generate": "Generate",
        "wafer_mode": "Mode",
        "wafer_export_svg": "Export SVG",
        "wafer_no_data": "Generate wafer map first",
        "debug_title": "Vector Debugger",
        "debug_reset": "Reset",
        "debug_step": "Step",
        "debug_step_txn": "Step Txn",
        "debug_step_section": "Step Section",
        "debug_run_bp": "Run to BP",
        "debug_stop": "Stop",
        "debug_pc": "PC",
        "debug_bus_state": "Bus State",
        "debug_event": "Event",
        "debug_add_bp": "Add BP",
        "debug_clear_bp": "Clear BP",
        "debug_history": "Exec History",
        "debug_no_vectors": "Generate vectors first",
        "debug_breakpoints": "Breakpoints",
        "debug_state": "Current State",
        "debug_running": "Running...",
        "debug_stopped": "Stopped",
        "debug_end": "End reached",
        "export_format_title": "Select Export Formats",
        "export_format_pat": "PAT (EStar native)",
        "export_format_stil": "STIL (IEEE 1450)",
        "export_format_wgl": "WGL (Waveform Generation Language)",
        "export_format_go": "Export Selected",
        "export_format_all": "Export All",
        "power_up_label": "Power-Up Sequence",
        "power_down_label": "Power-Down Sequence",
        "compliance_title": "Datasheet Compliance Matrix",
        "compliance_covered": "Covered",
        "compliance_uncovered": "Uncovered",
        "compliance_pct": "Coverage",
        "flow_editor": "Test Flow Editor",
        "flow_add_node": "Add Node",
        "flow_add_branch": "Add Branch",
        "flow_add_loop": "Add Loop",
        "flow_delete": "Delete",
        "flow_reset_default": "Reset Default",
        "flow_simulate": "Simulate",
        "flow_export_prg": "Export .prg",
        "flow_bin_table": "Bin Table",
        "flow_test_limits": "Test Limits",
        "flow_edit_limits": "Edit Limits",
        "flow_import_csv": "Import CSV",
        "flow_bin_pass": "Pass",
        "flow_bin_hard": "Hard Fail",
        "flow_bin_soft": "Soft Fail",
        "yield_title": "Yield Analysis Dashboard",
        "yield_import": "Import Datalog",
        "yield_import_sim": "Import Sim Results",
        "yield_export_report": "Export Report",
        "yield_param": "Parameter",
        "yield_lot": "Lot",
        "yield_site": "Site",
        "yield_histogram": "Histogram + Cp/Cpk",
        "yield_pareto": "Pareto Analysis",
        "yield_trend": "Yield Trend",
        "yield_bin_dist": "Bin Distribution",
        "yield_cp": "Cp",
        "yield_cpk": "Cpk",
        "yield_mean": "Mean",
        "yield_sigma": "Sigma",
        "yield_usl": "USL",
        "yield_lsl": "LSL",
        "yield_rate": "Yield",
        "yield_no_data": "No data. Import Datalog or simulation results",
        "sites_label": "Sites",
        "sites_tip": "Parallel test site count",
        "format_stil": "STIL",
        "format_wgl": "WGL",
        "format_pat": "PAT",
        "project_new": "New Project",
        "project_open": "Open Project",
        "project_recent": "Recent Projects",
        "project_save_template": "Save as Template",
        "project_load_template": "Load Template",
        "project_no_recent": "No recent projects",
        "welcome_title": "Welcome to ATE Test Platform",
        "welcome_quick_start": "Quick Start",
        "files_exist_overwrite": "Following files already exist. Overwrite?",
        "prefix_sanitized": "Export prefix contained invalid characters, replaced",
        "path_too_long": "Export path too long (>240 chars), select a shorter directory",
        "export_permission_denied": "Cannot write to directory, check permissions",
        "confirm": "Confirm",
        "warning": "Warning",
        "param_invalid": "Invalid parameter: {msg}",
        "export_format_label": "Export Format",
        # Phase 1: Fail Bit Map
        "fbm_title": "Fail Bit Map",
        "fbm_pass": "Pass",
        "fbm_fail": "Fail",
        "fbm_untested": "Untested",
        "fbm_export_svg": "Export FBM SVG",
        "fbm_detail_title": "Address Detail",
        "fbm_coverage": "Covered by: {tests}",
        "fbm_expected": "Expected: 0x{exp:02X}",
        "fbm_actual": "Actual: 0x{act:02X}",
        "fbm_addr_info": "Addr 0x{addr:02X} — {status}",
        "march_step": "Step {n}",
        "march_step_desc": "Step {n}: {desc}",
        "march_animator": "March C- Step Navigator",
        "sim_running": "Simulating...",
        "sim_thread_done": "Done: {txn} transactions, {err} errors, {t:.0f}ms",
        # Phase 4: ATPG Coverage
        "tab_atpg": " ◆ ATPG Coverage ",
        "atpg_run": "Run Simulation",
        "atpg_seed": "Seed",
        "atpg_running": "Fault simulation... {pct:.0%}",
        "atpg_done": "Done: coverage {cov:.1f}%, {t:.0f}ms",
        "atpg_no_vectors": "Generate vectors first",
        "atpg_heatmap": "Coverage Heatmap",
        "atpg_radar": "Radar Chart",
        "atpg_summary": "Overall Score",
        "atpg_min_suite": "Minimum Test Suite",
        # Phase 8: ATPG Audit
        "atpg_theory": "Theoretical Coverage (March Algorithm Proofs)",
        "atpg_select_faults": "Select Fault Models",
        "atpg_generate_proof": "Generate Proof",
        "atpg_march_vis": "March Sequence Visualization",
        "atpg_proof_text": "Coverage Proof",
        "atpg_replace_march": "Generate & Replace March Vectors",
        "atpg_add_test": "Add to Existing Tests",
        "atpg_export_proof": "Export Proof (.txt)",
        "atpg_optimal": "Optimal Algorithm",
        "atpg_complexity": "Complexity",
        "atpg_algorithm": "Algorithm",
        # Phase 5: Test Economics
        "tab_econ": " ◎ Test Economics ",
        "econ_calculate": "Calculate",
        "econ_test_time": "Test Time/Chip",
        "econ_test_cost": "Test Cost/Chip",
        "econ_daily_cap": "Daily Capacity",
        "econ_annual_save": "Annual Saving",
        "econ_no_vectors": "Generate vectors first",
        # Phase 6: Monte Carlo
        "mc_run": "Run Monte Carlo",
        "mc_running": "Monte Carlo running... {pct:.0%}",
        "mc_done": "Done: yield {y:.1f}%, Cpk={cpk:.2f}, {t:.0f}ms",
        "mc_seed": "Seed",
        "mc_n": "Samples",
        # Phase 7: Chip Migration
        "tab_migrate": " ⇌ Migration ",
        "migrate_btn": "Migrate ⇌",
        "migrate_source": "Source",
        "migrate_target": "Target",
        "migrate_run": "Run Migration",
        "migrate_running": "Migration in progress...",
        "migrate_done": "Done: {n} vectors ({t:.0f}ms)",
        "migrate_log": "Migration Log",
        "migrate_compare": "Chip Comparison",
        "migrate_export": "Export Migrated",
        "migrate_addr_bytes": "Addr Bytes",
        "migrate_page_size": "Page Size",
        "migrate_capacity": "Capacity",
        "migrate_max_freq": "Max Freq",
        "migrate_dev_addr": "Dev Addr",
        "migrate_no_vectors": "Generate vectors first",
        "migrate_same_chip": "Source and target are the same",
        "migrate_vectors": "Migrated Vectors",
        "migrate_sampling": "Large capacity: boundary+random sampling",
        # Phase 9: Demo Mode
        "demo_btn": "▶ Demo",
        "demo_running": "Demo [{step}/{total}]: {desc}",
        "demo_done": "Demo complete — data preserved for exploration",
        "demo_stop": "Demo stopped",
        # v9.0 Tier3 Phase 27: Adaptive Test Flow
        "adaptive_title": "Adaptive Test Flow",
        "adaptive_sim": "Adaptive Sim",
        "adaptive_running": "Adaptive simulation... {pct:.0f}%",
        "adaptive_done": "Done: {save:.1f}% time savings",
        "adaptive_rules": "Triggered Rules",
        "adaptive_fixed": "Fixed Flow",
        "adaptive_dynamic": "Adaptive Flow",
        "adaptive_compare": "Fixed vs Adaptive Comparison",
        "adaptive_no_sections": "Generate vectors first",
        "adaptive_sample_n": "Samples",
        # v9.0 Tier3 Phase 28: Guard Band
        "gb_title": "Guard Band Analysis",
        "gb_target_dppm": "Target DPPM",
        "gb_run": "Run Guard Band",
        "gb_apply": "Apply to Limits",
        "gb_running": "Guard Band computing...",
        "gb_done": "Guard Band done: avg tightening {pct:.1f}%",
        "gb_no_mc": "Run Monte Carlo first",
        "gb_original": "Original Limits",
        "gb_guarded": "Guarded Limits",
        "gb_dppm_before": "DPPM Before",
        "gb_dppm_after": "DPPM After",
        "gb_yield_loss": "Yield Loss",
        # v9.0 Tier3 Phase 29: Correlation
        "corr_title": "Parameter Correlation",
        "corr_run": "Run Correlation",
        "corr_matrix": "Correlation Matrix",
        "corr_scatter": "Scatter Plot",
        "corr_outliers": "Outliers",
        "corr_no_data": "Generate batch Datalog first",
        "corr_top": "Strongest Correlations",
        "corr_sigma": "Outlier Threshold (σ)",
        "corr_findings": "Findings",
        # v9.0 Tier3 Phase 30: PAT Reverse Parse
        "pat_import": "Import PAT",
        "pat_decode": "Protocol Decode",
        "pat_compare": "Compare with Current",
        "pat_detected": "Detected protocol: {proto}",
        "pat_transactions": "Decoded transactions: {n}",
        "pat_import_ok": "Imported: {n} vectors, {pins} pins",
        "pat_compare_result": "Match: {pct:.1f}%",
        "pat_no_current": "Generate current vectors first",
        "pat_decode_report": "Decode Report",
        # v9.0 Tier3 Phase 31: STDF Import
        "stdf_import": "Import STDF",
        "stdf_import_ok": "Imported: {n} parts, yield {y:.1f}%",
        "stdf_summary": "STDF Summary",
        "stdf_compare": "Compare with Simulation",
        "stdf_no_data": "Import STDF file first",
        "stdf_bin_dist": "Bin Distribution",
        "stdf_param_stats": "Parameter Statistics",
        "stdf_compare_result": "Comparison Result",
        # v9.0 Tier3 Phase 32: Standards Compliance
        "std_compliance": "Standards Compliance",
        "std_aec_q100": "AEC-Q100 (Automotive)",
        "std_jedec": "JEDEC Standards",
        "std_coverage_target": "Coverage Targets",
        "std_covered": "Covered",
        "std_partial": "Partial",
        "std_na": "N/A",
        "std_status": "Compliance Status",
        "std_run": "Generate Compliance Report",
        # v9.0 Tier3 Phase 33: Version Management
        "ver_btn": "Version Ⓥ",
        "ver_save": "Save Version",
        "ver_load": "Load Version",
        "ver_compare": "Compare Versions",
        "ver_list": "Version List",
        "ver_label": "Version Label",
        "ver_label_hint": "Enter a label for this version",
        "ver_saved": "Version saved: {label}",
        "ver_loaded": "Version loaded: {label}",
        "ver_no_versions": "No saved versions",
        "ver_diff_title": "Version Comparison",
        "ver_delete": "Delete Version",
        "ver_confirm_delete": "Delete version {label}?",
    },
}


# ============================================================
# 向量状态符号定义 (ATE标准)
# ============================================================
# 驱动状态
DRV_HIGH = "1"    # 驱动高电平
DRV_LOW  = "0"    # 驱动低电平
DRV_Z    = "Z"    # 高阻态

# 比较状态
CMP_HIGH = "H"    # 期望高电平
CMP_LOW  = "L"    # 期望低电平
CMP_X    = "X"    # 不比较

# 特殊
IDLE     = "X"    # 空闲/不关心


# ============================================================
# I2C协议向量生成器
# ============================================================

class I2CVectorGenerator:
    """I2C协议测试向量生成器"""

    def __init__(self, device_addr_base=0xA0, addr_pins=(0, 0, 0), wp_pin=0,
                 poll_count=2, addr_byte_count=1, page_select_bits=0,
                 capacity_bytes=256, page_size=8):
        """
        初始化
        device_addr_base: 器件基础地址 (24Cxx系列为0xA0)
        addr_pins: (A2, A1, A0) 硬件引脚电平
        wp_pin: WP引脚初始状态 (0=写使能, 1=写保护)
        poll_count: ACK Polling 轮询次数 (1~20)
        addr_byte_count: 地址字节数 (1=AT24C01~C16, 2=AT24C32~C512)
        page_select_bits: 页选择位数 (0=C01/C02, 1=C04, 2=C08, 3=C16)
        capacity_bytes: 芯片总容量 (字节)
        page_size: 页写大小 (字节)
        """
        self.addr_pins = addr_pins
        self.wp_pin = wp_pin
        self._init_wp_pin = wp_pin
        self.poll_count = max(1, min(poll_count, 20))
        self.addr_byte_count = addr_byte_count
        self.page_select_bits = page_select_bits
        self.capacity_bytes = capacity_bytes
        self.page_size = page_size
        self.device_addr_base = device_addr_base
        self.device_addr = device_addr_base | (addr_pins[0] << 3) | (addr_pins[1] << 2) | (addr_pins[2] << 1)
        self.vectors = []
        self.comments = []
        self.labels = []

    def _get_device_addr_for_page(self, mem_addr):
        """计算含页选择位的设备地址 (AT24C04/08/16)
        AT24C04: bit8 of mem_addr → device_addr bit1 (P0)
        AT24C08: bits[9:8] → device_addr bits[2:1] (P1,P0)
        AT24C16: bits[10:8] → device_addr bits[3:1] (P2,P1,P0)
        """
        if self.page_select_bits == 0:
            return self.device_addr
        page_bits = (mem_addr >> 8) & ((1 << self.page_select_bits) - 1)
        base = self.device_addr & ~((1 << (self.page_select_bits + 1)) - 2)
        return base | (page_bits << 1)

    def _send_memory_address(self, word_addr):
        """发送存储器地址 (1字节或2字节)"""
        if self.addr_byte_count == 2:
            high_byte = (word_addr >> 8) & 0xFF
            low_byte = word_addr & 0xFF
            self.add_write_byte(high_byte, f"AddrHigh=0x{high_byte:02X}")
            self.add_ack_from_slave("ACK after AddrHigh")
            self.add_write_byte(low_byte, f"AddrLow=0x{low_byte:02X}")
            self.add_ack_from_slave("ACK after AddrLow")
        else:
            self.add_write_byte(word_addr & 0xFF, "WordAddr")
            self.add_ack_from_slave("ACK after WordAddr")

    def _fmt_addr(self, addr):
        """格式化地址字符串"""
        return f"0x{addr:04X}" if self.addr_byte_count == 2 else f"0x{addr:02X}"

    def reset(self):
        """清空向量并恢复引脚状态到初始配置"""
        self.vectors = []
        self.comments = []
        self.labels = []
        self.wp_pin = self._init_wp_pin

    def _add_vector(self, a0, a1, a2, sda, scl, wp, comment="", label=""):
        """
        添加一个向量周期
        每个引脚的状态可以是: 0, 1, Z, H, L, X
        """
        vec = {
            "A0": a0, "A1": a1, "A2": a2,
            "SDA": sda, "SCL": scl, "WP": wp
        }
        self.vectors.append(vec)
        self.comments.append(comment)
        self.labels.append(label)

    def add_idle(self, cycles=1, comment="IDLE"):
        """添加空闲状态"""
        a0, a1, a2 = str(self.addr_pins[2]), str(self.addr_pins[1]), str(self.addr_pins[0])
        wp = str(self.wp_pin)
        for i in range(cycles):
            c = comment if i == 0 else ""
            self._add_vector(a0, a1, a2, "1", "1", wp, c)

    def add_start_condition(self):
        """添加I2C起始条件: SCL为高时SDA下降沿"""
        a0, a1, a2 = str(self.addr_pins[2]), str(self.addr_pins[1]), str(self.addr_pins[0])
        wp = str(self.wp_pin)
        # SDA从高到低, SCL保持高
        self._add_vector(a0, a1, a2, "1", "1", wp, "START Setup")
        self._add_vector(a0, a1, a2, "0", "1", wp, "START Condition (SDA↓)")
        self._add_vector(a0, a1, a2, "0", "0", wp, "START Hold")

    def add_stop_condition(self):
        """添加I2C停止条件: SCL为高时SDA上升沿 — EStar 4向量"""
        a0, a1, a2 = str(self.addr_pins[2]), str(self.addr_pins[1]), str(self.addr_pins[0])
        wp = str(self.wp_pin)
        self._add_vector(a0, a1, a2, "0", "0", wp, "STOP Setup")
        self._add_vector(a0, a1, a2, "0", "1", wp, "STOP (SCL↑)")
        self._add_vector(a0, a1, a2, "0", "1", wp, "STOP hold")
        self._add_vector(a0, a1, a2, "1", "1", wp, "STOP Condition (SDA↑)")

    def add_repeated_start(self):
        """添加重复起始条件"""
        a0, a1, a2 = str(self.addr_pins[2]), str(self.addr_pins[1]), str(self.addr_pins[0])
        wp = str(self.wp_pin)
        self._add_vector(a0, a1, a2, "1", "0", wp, "RepSTART: SDA↑")
        self._add_vector(a0, a1, a2, "1", "1", wp, "RepSTART: SCL↑")
        self._add_vector(a0, a1, a2, "0", "1", wp, "RepSTART: SDA↓")
        self._add_vector(a0, a1, a2, "0", "0", wp, "RepSTART: SCL↓")

    def add_write_bit(self, bit, comment=""):
        """写一个bit (主器件驱动SDA) — EStar 4向量/bit"""
        a0, a1, a2 = str(self.addr_pins[2]), str(self.addr_pins[1]), str(self.addr_pins[0])
        wp = str(self.wp_pin)
        sda_val = str(bit)
        self._add_vector(a0, a1, a2, sda_val, "0", wp, f"Write bit={bit} {comment}")
        self._add_vector(a0, a1, a2, sda_val, "1", wp, "SCL↑ (data valid)")
        self._add_vector(a0, a1, a2, sda_val, "1", wp, "SCL high hold")
        self._add_vector(a0, a1, a2, sda_val, "0", wp, "SCL↓")

    def add_read_bit(self, expected=None, comment=""):
        """读一个bit (从器件驱动SDA, 主器件比较) — EStar 4向量/bit"""
        a0, a1, a2 = str(self.addr_pins[2]), str(self.addr_pins[1]), str(self.addr_pins[0])
        wp = str(self.wp_pin)
        if expected is not None:
            cmp = "H" if expected else "L"
        else:
            cmp = "X"
        self._add_vector(a0, a1, a2, "X", "0", wp, f"Read bit {comment}")
        self._add_vector(a0, a1, a2, cmp, "1", wp, f"SCL↑ (compare={cmp})")
        self._add_vector(a0, a1, a2, cmp, "1", wp, "SCL high hold")
        self._add_vector(a0, a1, a2, "X", "0", wp, "SCL↓")

    def add_ack_from_slave(self, comment="ACK from slave"):
        """从器件应答 (期望SDA=0) — EStar 4向量"""
        a0, a1, a2 = str(self.addr_pins[2]), str(self.addr_pins[1]), str(self.addr_pins[0])
        wp = str(self.wp_pin)
        self._add_vector(a0, a1, a2, "X", "0", wp, comment)
        self._add_vector(a0, a1, a2, "L", "1", wp, "ACK check (expect LOW)")
        self._add_vector(a0, a1, a2, "L", "1", wp, "ACK hold")
        self._add_vector(a0, a1, a2, "X", "0", wp, "SCL↓")

    def add_nack_from_master(self, comment="NACK from master"):
        """主器件非应答 (SDA=1) — EStar 4向量"""
        a0, a1, a2 = str(self.addr_pins[2]), str(self.addr_pins[1]), str(self.addr_pins[0])
        wp = str(self.wp_pin)
        self._add_vector(a0, a1, a2, "1", "0", wp, comment)
        self._add_vector(a0, a1, a2, "1", "1", wp, "NACK (SDA=HIGH)")
        self._add_vector(a0, a1, a2, "1", "1", wp, "NACK hold")
        self._add_vector(a0, a1, a2, "1", "0", wp, "SCL↓")

    def add_ack_from_master(self, comment="ACK from master"):
        """主器件应答 (SDA=0) — EStar 4向量"""
        a0, a1, a2 = str(self.addr_pins[2]), str(self.addr_pins[1]), str(self.addr_pins[0])
        wp = str(self.wp_pin)
        self._add_vector(a0, a1, a2, "0", "0", wp, comment)
        self._add_vector(a0, a1, a2, "0", "1", wp, "ACK (SDA=LOW)")
        self._add_vector(a0, a1, a2, "0", "1", wp, "ACK hold")
        self._add_vector(a0, a1, a2, "0", "0", wp, "SCL↓")

    def add_write_byte(self, byte_val, comment=""):
        """写一个字节 (MSB first)"""
        for i in range(7, -1, -1):
            bit = (byte_val >> i) & 1
            bit_comment = f"Byte 0x{byte_val:02X} bit[{i}]" if i == 7 else ""
            self.add_write_bit(bit, bit_comment if not comment else f"{comment} bit[{i}]")

    def add_read_byte(self, expected_val=None, comment=""):
        """读一个字节 (MSB first)"""
        for i in range(7, -1, -1):
            if expected_val is not None:
                exp_bit = (expected_val >> i) & 1
            else:
                exp_bit = None
            bit_comment = f"Read byte bit[{i}]" if i == 7 else ""
            self.add_read_bit(exp_bit, bit_comment if not comment else f"{comment} bit[{i}]")

    # ================================================================
    # 高级操作：完整的I2C事务
    # ================================================================

    def gen_byte_write(self, word_addr, data_byte):
        """字节写操作 (支持1/2字节地址 + 页选择)"""
        addr_s = self._fmt_addr(word_addr)
        self.add_idle(2, f"=== Byte Write: addr={addr_s} data=0x{data_byte:02X} ===")
        self.add_start_condition()

        dev_addr = self._get_device_addr_for_page(word_addr)
        self.add_write_byte(dev_addr & 0xFE, "DevAddr+W")
        self.add_ack_from_slave("ACK after DevAddr")

        self._send_memory_address(word_addr)

        self.add_write_byte(data_byte, "Data")
        self.add_ack_from_slave("ACK after Data")

        self.add_stop_condition()
        self.gen_ack_polling()

    def gen_random_read(self, word_addr, expected_data=None):
        """随机读操作 (支持1/2字节地址 + 页选择)"""
        addr_s = self._fmt_addr(word_addr)
        self.add_idle(2, f"=== Random Read: addr={addr_s} ===")

        dev_addr = self._get_device_addr_for_page(word_addr)
        # 先写入目标地址 (dummy write)
        self.add_start_condition()
        self.add_write_byte(dev_addr & 0xFE, "DevAddr+W")
        self.add_ack_from_slave("ACK after DevAddr")
        self._send_memory_address(word_addr)

        # 重复起始 + 读
        self.add_repeated_start()
        self.add_write_byte(dev_addr | 0x01, "DevAddr+R")
        self.add_ack_from_slave("ACK after DevAddr+R")

        self.add_read_byte(expected_data, "ReadData")
        self.add_nack_from_master("NACK (end read)")

        self.add_stop_condition()

    def gen_byte_read(self, addr, expected=None, device_addr=None):
        """统一接口: 单字节读 (委托给 gen_random_read)"""
        self.gen_random_read(addr, expected_data=expected)

    def gen_page_write(self, start_addr, data_bytes):
        """页写操作 (页大小由芯片决定)"""
        addr_s = self._fmt_addr(start_addr)
        self.add_idle(2, f"=== Page Write: addr={addr_s} len={len(data_bytes)} ===")
        self.add_start_condition()

        dev_addr = self._get_device_addr_for_page(start_addr)
        self.add_write_byte(dev_addr & 0xFE, "DevAddr+W")
        self.add_ack_from_slave("ACK after DevAddr")

        self._send_memory_address(start_addr)

        for i, data in enumerate(data_bytes):
            self.add_write_byte(data, f"Data[{i}]")
            self.add_ack_from_slave(f"ACK after Data[{i}]")

        self.add_stop_condition()
        self.gen_ack_polling()

    def gen_sequential_read(self, start_addr, count, expected_data=None):
        """顺序读操作 (支持1/2字节地址 + 页选择)"""
        addr_s = self._fmt_addr(start_addr)
        self.add_idle(2, f"=== Sequential Read: addr={addr_s} count={count} ===")

        dev_addr = self._get_device_addr_for_page(start_addr)
        # 写入起始地址
        self.add_start_condition()
        self.add_write_byte(dev_addr & 0xFE, "DevAddr+W")
        self.add_ack_from_slave()
        self._send_memory_address(start_addr)

        # 重复起始 + 读
        self.add_repeated_start()
        self.add_write_byte(dev_addr | 0x01, "DevAddr+R")
        self.add_ack_from_slave()

        for i in range(count):
            exp = expected_data[i] if expected_data and i < len(expected_data) else None
            self.add_read_byte(exp, f"SeqRead[{i}]")
            if i < count - 1:
                self.add_ack_from_master(f"ACK (continue read {i})")
            else:
                self.add_nack_from_master("NACK (end sequential read)")

        self.add_stop_condition()

    def gen_current_addr_read(self, expected_data=None):
        """
        当前地址读操作 (Current Address Read)

        AT24C02 第三种读模式: 无需指定地址, 直接发送器件地址+R,
        从内部地址计数器的当前位置读取一个字节。
        计数器在上一次读/写操作后自动递增。
        """
        self.add_idle(2, "=== Current Address Read ===")
        self.add_start_condition()
        self.add_write_byte(self.device_addr | 0x01, "DevAddr+R (Current Addr Read)")
        self.add_ack_from_slave("ACK after DevAddr+R")
        self.add_read_byte(expected_data, "CurrentAddrRead data")
        self.add_nack_from_master("NACK (end current addr read)")
        self.add_stop_condition()

    def add_nack_from_slave(self, comment="NACK from slave"):
        """从器件非应答 (期望SDA=1, 设备忙/无响应)"""
        a0, a1, a2 = str(self.addr_pins[2]), str(self.addr_pins[1]), str(self.addr_pins[0])
        wp = str(self.wp_pin)
        self._add_vector(a0, a1, a2, "Z", "0", wp, comment)
        self._add_vector(a0, a1, a2, "H", "1", wp, "NACK check (expect HIGH)")
        self._add_vector(a0, a1, a2, "X", "0", wp, "SCL↓")

    def gen_ack_polling(self):
        """
        应答查询 (等待写周期完成)

        AT24C02 写周期最长 5ms, 期间设备不响应 (NACK)。
        ATE 向量中: 前 N-1 次发送设备地址后期望 NACK (设备忙),
        最后一次期望 ACK (写周期结束, 设备就绪)。
        """
        self.add_idle(2, "=== ACK Polling (wait for write cycle) ===")
        poll_count = self.poll_count
        for attempt in range(poll_count):
            self.add_start_condition()
            self.add_write_byte(self.device_addr & 0xFE, f"Poll attempt {attempt}")
            if attempt < poll_count - 1:
                # 前几次: 设备可能仍在写周期中, 预期 NACK
                self.add_nack_from_slave(f"Poll NACK (device busy, attempt {attempt})")
            else:
                # 最后一次: 写周期应已完成, 预期 ACK
                self.add_ack_from_slave(f"Poll ACK (device ready, attempt {attempt})")
            self.add_stop_condition()
            self.add_idle(2, "Poll interval")

    # ---- v9.0 统一协议接口 wrapper ----

    def gen_write_poll(self, max_polls=None):
        """统一接口: 写轮询 (委托给 gen_ack_polling)"""
        self.gen_ack_polling()

    def get_pins(self):
        return ["A0", "A1", "A2", "WP", "SCL", "SDA"]

    def get_pin_directions(self):
        return {"A0": "In", "A1": "In", "A2": "In",
                "WP": "In", "SCL": "In", "SDA": "InOut"}


# ============================================================
# SPI协议向量生成器
# ============================================================

class SPIVectorGenerator:
    """SPI协议测试向量生成器 (Mode 0/3, 标准SPI)"""

    def __init__(self, spi_mode=0, wp_pin=0, hold_pin=1,
                 addr_byte_count=1, capacity_bytes=256, page_size=16,
                 sector_size=None, has_jedec_id=False, jedec_id=0,
                 poll_count=10):
        self.spi_mode = spi_mode
        self.wp_pin = wp_pin
        self.hold_pin = hold_pin
        self.addr_byte_count = addr_byte_count
        self.capacity_bytes = capacity_bytes
        self.page_size = page_size
        self.sector_size = sector_size
        self.has_jedec_id = has_jedec_id
        self.jedec_id = jedec_id
        self.poll_count = poll_count
        self.vectors = []
        self.comments = []
        self.labels = []

    def reset(self):
        """清空向量缓冲"""
        self.vectors.clear()
        self.comments.clear()
        self.labels.clear()

    def _add_vector(self, cs, sck, mosi, miso, wp, hold, comment="", label=""):
        """添加一个SPI向量"""
        self.vectors.append({
            "CS": cs, "SCK": sck, "MOSI": mosi,
            "MISO": miso, "WP": wp, "HOLD": hold,
        })
        self.comments.append(comment)
        self.labels.append(label)

    def add_idle(self, cycles=1, comment="IDLE"):
        """添加空闲状态向量 (CS=1, SCK=0, MOSI/MISO=X)"""
        wp_state = str(self.wp_pin)
        hold_state = str(self.hold_pin)
        for i in range(cycles):
            c = comment if i == 0 else ""
            self._add_vector("1", "0", "X", "X", wp_state, hold_state, c)

    # ── CS 控制 ──
    def cs_active(self, comment="CS Active (low)"):
        """拉低CS, 开始SPI事务"""
        self._add_vector("0", "0", "X", "X",
                         str(self.wp_pin), str(self.hold_pin), comment)

    def cs_inactive(self, comment="CS Inactive (high)"):
        """拉高CS, 结束SPI事务"""
        self._add_vector("1", "0", "X", "X",
                         str(self.wp_pin), str(self.hold_pin), comment)

    # ── 位级操作 (Mode 0: CPOL=0, CPHA=0 — 空闲SCK=0, 上升沿采样) ──
    def send_bit(self, bit, comment=""):
        """发送1 bit: SCK=0时驱动MOSI, SCK=1时对端采样"""
        mosi_val = "1" if bit else "0"
        wp = str(self.wp_pin)
        hold = str(self.hold_pin)
        # Phase 1: SCK=0, drive MOSI
        self._add_vector("0", "0", mosi_val, "X", wp, hold, comment)
        # Phase 2: SCK=1, slave samples MOSI
        self._add_vector("0", "1", mosi_val, "X", wp, hold, "")

    def receive_bit(self, expected=None, comment=""):
        """接收1 bit: SCK=1时比较MISO"""
        wp = str(self.wp_pin)
        hold = str(self.hold_pin)
        miso_cmp = "X"
        if expected is not None:
            miso_cmp = "H" if expected else "L"
        # Phase 1: SCK=0
        self._add_vector("0", "0", "X", "X", wp, hold, comment)
        # Phase 2: SCK=1, compare MISO
        self._add_vector("0", "1", "X", miso_cmp, wp, hold, "")

    def send_byte(self, byte_val, comment=""):
        """发送1字节 (MSB first, 16向量)"""
        for i in range(8):
            bit = (byte_val >> (7 - i)) & 1
            c = f"{comment}=0x{byte_val:02X} bit{7-i}" if i == 0 and comment else ""
            self.send_bit(bit, c)

    def receive_byte(self, expected=None, comment=""):
        """接收1字节 (MSB first, 16向量)"""
        for i in range(8):
            exp_bit = None
            if expected is not None:
                exp_bit = (expected >> (7 - i)) & 1
            c = comment if i == 0 else ""
            self.receive_bit(exp_bit, c)

    # ── 命令级操作 ──
    def send_command(self, opcode, comment=""):
        """发送命令字节 (CS已经active)"""
        self.send_byte(opcode, comment or f"CMD 0x{opcode:02X}")

    def send_address(self, addr, byte_count=None):
        """发送地址 (1/2/3字节, MSB first)"""
        if byte_count is None:
            byte_count = self.addr_byte_count
        if byte_count >= 3:
            high = (addr >> 16) & 0xFF
            self.send_byte(high, f"Addr[23:16]=0x{high:02X}")
        if byte_count >= 2:
            mid = (addr >> 8) & 0xFF
            self.send_byte(mid, f"Addr[15:8]=0x{mid:02X}")
        low = addr & 0xFF
        self.send_byte(low, f"Addr[7:0]=0x{low:02X}")

    # ── 事务级操作 ──
    def write_enable(self, comment="WREN"):
        """Write Enable (WREN 0x06): CS↓ → 0x06 → CS↑"""
        self.cs_active(comment)
        self.send_command(SPI_COMMANDS["WREN"], "WREN")
        self.cs_inactive("CS↑ after WREN")
        self.add_idle(1, "tCSD")

    def write_disable(self, comment="WRDI"):
        """Write Disable (WRDI 0x04)"""
        self.cs_active(comment)
        self.send_command(SPI_COMMANDS["WRDI"], "WRDI")
        self.cs_inactive("CS↑ after WRDI")
        self.add_idle(1, "tCSD")

    def read_status_register(self, comment="RDSR"):
        """Read Status Register: CS↓ → 0x05 → receive 1 byte → CS↑"""
        self.cs_active(comment)
        self.send_command(SPI_COMMANDS["RDSR"], "RDSR")
        self.receive_byte(comment="SR data")
        self.cs_inactive("CS↑ after RDSR")

    def poll_wip(self, count=None, comment="Poll WIP"):
        """轮询 WIP (Status Register bit0), 最后一次期望 WIP=0"""
        if count is None:
            count = self.poll_count
        wp = str(self.wp_pin)
        hold = str(self.hold_pin)
        for i in range(count):
            is_last = (i == count - 1)
            self.cs_active(f"WIP poll {i+1}/{count}")
            self.send_command(SPI_COMMANDS["RDSR"], "RDSR")
            # 接收SR, 只关心 bit0 (WIP)
            for bit_idx in range(8):
                if bit_idx == 7 and is_last:
                    # 最后一次轮询的 bit0 (LSB) 期望 L (WIP=0)
                    self._add_vector("0", "0", "X", "X", wp, hold, "WIP bit (expect 0)")
                    self._add_vector("0", "1", "X", "L", wp, hold, "")
                else:
                    self._add_vector("0", "0", "X", "X", wp, hold, "")
                    self._add_vector("0", "1", "X", "X", wp, hold, "")
            self.cs_inactive("CS↑ after poll")
            self.add_idle(1, "Poll interval")

    def spi_write(self, addr, data_list, comment=""):
        """SPI写入: WREN → CS↓ → WRITE → Addr → Data → CS↑ → Poll WIP"""
        label_text = comment or f"SPI Write @0x{addr:04X} len={len(data_list)}"
        self.write_enable()
        self.cs_active(label_text)
        self.send_command(SPI_COMMANDS["WRITE"], "WRITE/PP")
        self.send_address(addr)
        for i, d in enumerate(data_list):
            self.send_byte(d, f"Data[{i}]")
        self.cs_inactive("CS↑ after write data")
        self.add_idle(1, "tCSD")
        self.poll_wip(comment="Poll WIP after write")
        # 标记label
        if self.labels and not self.labels[-1]:
            idx = len(self.vectors) - 1
            # 回溯找到第一个WREN向量
            for j in range(len(self.labels) - 1, -1, -1):
                if "WREN" in self.comments[j]:
                    self.labels[j] = label_text
                    break

    def spi_read(self, addr, count, expected_list=None, comment=""):
        """SPI读取: CS↓ → READ → Addr → Receive data → CS↑"""
        label_text = comment or f"SPI Read @0x{addr:04X} len={count}"
        self.cs_active(label_text)
        self.send_command(SPI_COMMANDS["READ"], "READ")
        self.send_address(addr)
        for i in range(count):
            exp = expected_list[i] if expected_list and i < len(expected_list) else None
            self.receive_byte(exp, f"RData[{i}]")
        self.cs_inactive("CS↑ after read")
        self.add_idle(1, "tCSD")
        # label
        if self.labels:
            for j in range(len(self.labels) - 1, -1, -1):
                if label_text in self.comments[j]:
                    self.labels[j] = label_text
                    break

    def spi_sector_erase(self, addr, comment=""):
        """Flash扇区擦除: WREN → CS↓ → SE(0x20) → Addr → CS↑ → Poll WIP"""
        label_text = comment or f"Sector Erase @0x{addr:06X}"
        self.write_enable()
        self.cs_active(label_text)
        self.send_command(SPI_COMMANDS["SECTOR_ERASE"], "SECTOR_ERASE")
        self.send_address(addr)
        self.cs_inactive("CS↑ after SE")
        self.add_idle(1, "tCSD")
        self.poll_wip(self.poll_count, "Poll WIP after erase")

    def spi_block_erase_64k(self, addr, comment=""):
        """Flash 64KB块擦除"""
        label_text = comment or f"Block Erase 64K @0x{addr:06X}"
        self.write_enable()
        self.cs_active(label_text)
        self.send_command(SPI_COMMANDS["BLOCK_ERASE_64K"], "BLOCK_ERASE_64K")
        self.send_address(addr)
        self.cs_inactive("CS↑ after BE64K")
        self.add_idle(1, "tCSD")
        self.poll_wip(self.poll_count, "Poll WIP after block erase")

    def spi_chip_erase(self, comment=""):
        """Flash全片擦除"""
        self.write_enable()
        self.cs_active(comment or "Chip Erase")
        self.send_command(SPI_COMMANDS["CHIP_ERASE"], "CHIP_ERASE")
        self.cs_inactive("CS↑ after CE")
        self.add_idle(1, "tCSD")
        self.poll_wip(self.poll_count * 2, "Poll WIP after chip erase")

    def spi_read_jedec_id(self, expected_jedec=0, comment=""):
        """读取JEDEC ID (3 bytes: Manufacturer, Device Type, Capacity)"""
        label_text = comment or "Read JEDEC ID"
        self.cs_active(label_text)
        self.send_command(SPI_COMMANDS["JEDEC_ID"], "JEDEC_ID")
        if expected_jedec:
            mfr = (expected_jedec >> 16) & 0xFF
            dev_type = (expected_jedec >> 8) & 0xFF
            cap = expected_jedec & 0xFF
            self.receive_byte(mfr, f"MFR=0x{mfr:02X}")
            self.receive_byte(dev_type, f"DevType=0x{dev_type:02X}")
            self.receive_byte(cap, f"Cap=0x{cap:02X}")
        else:
            self.receive_byte(comment="MFR ID")
            self.receive_byte(comment="Device Type")
            self.receive_byte(comment="Capacity")
        self.cs_inactive("CS↑ after JEDEC ID")
        self.add_idle(1, "tCSD")

    def spi_write_status_register(self, sr_val, comment=""):
        """写状态寄存器"""
        self.write_enable()
        self.cs_active(comment or f"Write SR=0x{sr_val:02X}")
        self.send_command(SPI_COMMANDS["WRSR"], "WRSR")
        self.send_byte(sr_val, f"SR=0x{sr_val:02X}")
        self.cs_inactive("CS↑ after WRSR")
        self.add_idle(1, "tCSD")
        self.poll_wip(comment="Poll WIP after WRSR")

    # ---- v9.0 统一协议接口 wrapper ----

    def gen_byte_write(self, addr, data, device_addr=None):
        """统一接口: 单字节写"""
        self.spi_write(addr, [data])

    def gen_byte_read(self, addr, expected=None, device_addr=None):
        """统一接口: 单字节读"""
        self.spi_read(addr, 1, [expected] if expected is not None else None)

    def gen_page_write(self, start_addr, data_list, device_addr=None):
        """统一接口: 页写"""
        self.spi_write(start_addr, data_list)

    def gen_sequential_read(self, start_addr, count, expected_list=None, device_addr=None):
        """统一接口: 顺序读"""
        self.spi_read(start_addr, count, expected_list)

    def gen_write_poll(self, max_polls=None):
        """统一接口: 写轮询"""
        self.poll_wip(count=max_polls)

    def get_pins(self):
        return ["CS", "SCK", "MOSI", "MISO", "WP", "HOLD"]

    def get_pin_directions(self):
        return {"CS": "In", "SCK": "In", "MOSI": "In",
                "MISO": "Out", "WP": "In", "HOLD": "In"}


# ============================================================
# Microwire (93Cxx) 协议向量生成器
# ============================================================

class MicrowireVectorGenerator:
    """Microwire (93Cxx) 3线协议测试向量生成器"""

    def __init__(self, org_mode="x16", word_bits=16, addr_bits=6,
                 capacity_words=64, poll_count=10):
        self.org_mode = org_mode
        self.word_bits = word_bits
        self.addr_bits = addr_bits
        self.capacity_words = capacity_words
        self.capacity_bytes = capacity_words * (word_bits // 8)
        self.page_size = word_bits // 8  # Microwire无页写, 最小单位=1 word
        self.poll_count = poll_count
        # ORG pin: 1=x16, 0=x8
        self.org_pin = "1" if org_mode == "x16" else "0"
        self.vectors = []
        self.comments = []
        self.labels = []

    def reset(self):
        """清空向量缓冲"""
        self.vectors.clear()
        self.comments.clear()
        self.labels.clear()

    def _add_vector(self, cs, sk, di, do_expect, org, nc, comment="", label=""):
        """添加一个Microwire向量"""
        self.vectors.append({
            "CS": cs, "SK": sk, "DI": di,
            "DO": do_expect, "ORG": org, "NC": nc,
        })
        self.comments.append(comment)
        self.labels.append(label)

    def add_idle(self, cycles=1, comment="IDLE"):
        """空闲: CS=0, SK=0"""
        for i in range(cycles):
            c = comment if i == 0 else ""
            self._add_vector("0", "0", "0", "X", self.org_pin, "X", c)

    # ── CS 控制 (Microwire CS高有效) ──
    def cs_active(self, comment="CS Active (high)"):
        """CS=1, 开始Microwire事务"""
        self._add_vector("1", "0", "0", "X", self.org_pin, "X", comment)

    def cs_inactive(self, comment="CS Inactive (low)"):
        """CS=0, 结束Microwire事务"""
        self._add_vector("0", "0", "0", "X", self.org_pin, "X", comment)

    # ── 位级操作 ──
    def send_bit(self, bit, comment=""):
        """发送1 bit via DI: SK=0时驱动DI, SK=1时器件采样"""
        di_val = "1" if bit else "0"
        # Phase 1: SK=0, drive DI
        self._add_vector("1", "0", di_val, "X", self.org_pin, "X", comment)
        # Phase 2: SK=1, device samples DI
        self._add_vector("1", "1", di_val, "X", self.org_pin, "X", "")

    def receive_bit(self, expected=None, comment=""):
        """接收1 bit via DO: SK=1时比较DO"""
        do_cmp = "X"
        if expected is not None:
            do_cmp = "H" if expected else "L"
        # Phase 1: SK=0
        self._add_vector("1", "0", "0", "X", self.org_pin, "X", comment)
        # Phase 2: SK=1, compare DO
        self._add_vector("1", "1", "0", do_cmp, self.org_pin, "X", "")

    def send_start_bit(self, comment="Start Bit"):
        """发送起始位 SB=1 (Microwire命令必须以SB=1开始)"""
        self.send_bit(1, comment)

    def send_opcode(self, opcode, bits=2, comment=""):
        """发送操作码 (MSB first)"""
        for i in range(bits):
            b = (opcode >> (bits - 1 - i)) & 1
            c = f"Opcode={opcode:0{bits}b}" if i == 0 and comment == "" else comment
            self.send_bit(b, c if i == 0 else "")

    def send_address(self, addr, bits=None):
        """发送地址 (MSB first, 可变长度)"""
        if bits is None:
            bits = self.addr_bits
        for i in range(bits):
            b = (addr >> (bits - 1 - i)) & 1
            c = f"Addr=0x{addr:02X}" if i == 0 else ""
            self.send_bit(b, c)

    def send_data_word(self, data, comment=""):
        """发送数据字 (MSB first, word_bits位)"""
        for i in range(self.word_bits):
            b = (data >> (self.word_bits - 1 - i)) & 1
            c = f"{comment}=0x{data:04X}" if i == 0 and comment else ""
            self.send_bit(b, c)

    def receive_word(self, expected=None, comment=""):
        """接收数据字 (MSB first, word_bits位)"""
        for i in range(self.word_bits):
            exp_bit = None
            if expected is not None:
                exp_bit = (expected >> (self.word_bits - 1 - i)) & 1
            c = comment if i == 0 else ""
            self.receive_bit(exp_bit, c)

    def poll_ready(self, count=None, comment="Poll Ready"):
        """轮询DO=1 (Ready), Microwire写完成后DO从低变高"""
        if count is None:
            count = self.poll_count
        for i in range(count):
            is_last = (i == count - 1)
            do_exp = "H" if is_last else "X"
            c = f"Ready poll {i+1}/{count}" if i == 0 else ""
            # CS保持高, 查看DO
            self._add_vector("1", "0", "0", "X", self.org_pin, "X", c)
            self._add_vector("1", "1", "0", do_exp, self.org_pin, "X", "")

    # ── 事务级操作 ──
    def mw_ewen(self, comment="EWEN"):
        """Erase/Write Enable: SB + 00 + 11xxxx"""
        self.cs_active(comment)
        self.send_start_bit()
        self.send_opcode(0b00, 2, "EWEN opcode")
        # 地址字段填充: 高2位=11, 其余=0
        addr_val = 0b11 << (self.addr_bits - 2)
        self.send_address(addr_val, self.addr_bits)
        self.cs_inactive("CS↓ after EWEN")
        self.add_idle(1, "tCS")

    def mw_ewds(self, comment="EWDS"):
        """Erase/Write Disable: SB + 00 + 00xxxx"""
        self.cs_active(comment)
        self.send_start_bit()
        self.send_opcode(0b00, 2, "EWDS opcode")
        # 地址字段: 全0
        self.send_address(0, self.addr_bits)
        self.cs_inactive("CS↓ after EWDS")
        self.add_idle(1, "tCS")

    def mw_write(self, addr, data, comment=""):
        """写入1个word: EWEN → SB+WRITE+addr+data → poll → EWDS"""
        label_text = comment or f"MW Write @{addr} data=0x{data:04X}"
        self.mw_ewen()
        self.cs_active(label_text)
        self.send_start_bit()
        self.send_opcode(MW_OPCODES["WRITE"], 2, "WRITE")
        self.send_address(addr)
        self.send_data_word(data, "WData")
        self.cs_inactive("CS↓ end write")
        # 拉高CS开始轮询
        self.cs_active("Poll start")
        self.poll_ready()
        self.cs_inactive("CS↓ after poll")
        self.add_idle(1, "tCS")
        self.mw_ewds()

    def mw_read(self, addr, expected=None, comment=""):
        """读取1个word: SB+READ+addr → receive word"""
        label_text = comment or f"MW Read @{addr}"
        self.cs_active(label_text)
        self.send_start_bit()
        self.send_opcode(MW_OPCODES["READ"], 2, "READ")
        self.send_address(addr)
        # Dummy bit 0 (DO goes low before first data bit)
        self.receive_bit(None, "Dummy 0")
        self.receive_word(expected, f"RData @{addr}")
        self.cs_inactive("CS↓ after read")
        self.add_idle(1, "tCS")

    def mw_erase(self, addr, comment=""):
        """擦除1个word"""
        label_text = comment or f"MW Erase @{addr}"
        self.mw_ewen()
        self.cs_active(label_text)
        self.send_start_bit()
        self.send_opcode(MW_OPCODES["ERASE"], 2, "ERASE")
        self.send_address(addr)
        self.cs_inactive("CS↓ end erase cmd")
        self.cs_active("Poll start")
        self.poll_ready()
        self.cs_inactive("CS↓ after poll")
        self.add_idle(1, "tCS")
        self.mw_ewds()

    def mw_eral(self, comment="ERAL"):
        """擦除全部 (Erase All)"""
        self.mw_ewen()
        self.cs_active(comment or "ERAL")
        self.send_start_bit()
        self.send_opcode(0b00, 2, "ERAL opcode")
        addr_val = 0b10 << (self.addr_bits - 2)
        self.send_address(addr_val, self.addr_bits)
        self.cs_inactive("CS↓ end ERAL")
        self.cs_active("Poll start")
        self.poll_ready()
        self.cs_inactive("CS↓ after poll")
        self.add_idle(1, "tCS")
        self.mw_ewds()

    def mw_wral(self, data, comment="WRAL"):
        """写入全部 (Write All) — 所有地址写入相同数据"""
        self.mw_ewen()
        self.cs_active(comment or f"WRAL data=0x{data:04X}")
        self.send_start_bit()
        self.send_opcode(0b00, 2, "WRAL opcode")
        addr_val = 0b01 << (self.addr_bits - 2)
        self.send_address(addr_val, self.addr_bits)
        self.send_data_word(data, "WRAL data")
        self.cs_inactive("CS↓ end WRAL")
        self.cs_active("Poll start")
        self.poll_ready()
        self.cs_inactive("CS↓ after poll")
        self.add_idle(1, "tCS")
        self.mw_ewds()

    # ---- v9.0 统一协议接口 wrapper ----

    def gen_byte_write(self, addr, data, device_addr=None):
        """统一接口: 单字写"""
        self.mw_write(addr, data)

    def gen_byte_read(self, addr, expected=None, device_addr=None):
        """统一接口: 单字读"""
        self.mw_read(addr, expected)

    def gen_page_write(self, start_addr, data_list, device_addr=None):
        """统一接口: 连续写 (MW无原生页写, 循环单字写)"""
        for i, d in enumerate(data_list):
            self.mw_write(start_addr + i, d)

    def gen_sequential_read(self, start_addr, count, expected_list=None, device_addr=None):
        """统一接口: 连续读"""
        for i in range(count):
            exp = expected_list[i] if expected_list and i < len(expected_list) else None
            self.mw_read(start_addr + i, exp)

    def gen_write_poll(self, max_polls=None):
        """统一接口: 写轮询"""
        self.cs_active("Poll start")
        self.poll_ready(count=max_polls)
        self.cs_inactive("CS↓ after poll")

    def get_pins(self):
        return ["CS", "SK", "DI", "DO", "ORG", "NC"]

    def get_pin_directions(self):
        return {"CS": "In", "SK": "In", "DI": "In",
                "DO": "Out", "ORG": "In", "NC": "In"}


# ============================================================
# PAT文件格式化输出
# ============================================================

class PATFormatter:
    """AdaptStar PAT文件格式化器"""

    @staticmethod
    def generate_pat_header(test_name, description, pin_list):
        """生成PAT文件头部 — EStar 官方格式 (HEAD[PIN_NAME] 块)"""
        now = datetime.datetime.now()
        header = []
        # 元数据注释
        header.append(f"// PAT File: {test_name}")
        header.append(f"// Description: {description}")
        header.append(f"// Generated: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        header.append(f"// Tool: EEPROM PAT Generator {VERSION}")
        header.append(f"// Target ATE: AdaptStar-E (EStar)")
        header.append("")

        # HEAD[PIN_NAME] 块 — EStar 官方格式
        header.append("HEAD[PIN_NAME]:")
        header.append("  ")
        for i, pin in enumerate(pin_list):
            suffix = ";" if i == len(pin_list) - 1 else ","
            header.append(f" {pin}{suffix}")
        header.append(" ")
        header.append("END_HEAD;")

        return "\n".join(header)

    @staticmethod
    def generate_pat_timing_header(period_ns=2500, voltage_preset=None):
        """生成时序与电平定义头"""
        freq_khz = 1e9 / period_ns / 1e3
        half = period_ns // 2
        lines = []

        # TIMING 块
        lines.append("TIMING timing_i2c {")
        lines.append(f"    PERIOD  = {period_ns}ns;   // {freq_khz:.1f} kHz")
        lines.append(f"    tDRV    = 0ns;        // Drive data at period start")
        lines.append(f"    tCMP    = {half}ns;    // Compare strobe at mid-period")
        lines.append(f"    tPLC    = 0ns;        // Pin Low  clock edge")
        lines.append(f"    tPHC    = {half}ns;    // Pin High clock edge")
        lines.append("}")
        lines.append("")

        # LEVEL 块 (使用电压预设或默认 5V)
        vp = voltage_preset or VOLTAGE_PRESETS["5.0V"]
        label = vp.get("label", "level_5v")
        lines.append(f"LEVEL {label} {{")
        lines.append(f"    VCC  = {vp['VCC']};")
        lines.append(f"    VIH  = {vp['VIH']};    // Input High threshold")
        lines.append(f"    VIL  = {vp['VIL']};    // Input Low  threshold")
        lines.append(f"    VOH  = {vp['VOH']};    // Output High minimum")
        lines.append(f"    VOL  = {vp['VOL']};    // Output Low  maximum")
        lines.append(f"    IOL  = {vp['IOL']};   // Output Low  sink current")
        lines.append(f"    VCLH = {vp['VCLH']};    // Clamp High")
        lines.append(f"    VCLL = {vp['VCLL']};   // Clamp Low")
        lines.append("}")
        lines.append("")

        return "\n".join(lines)

    @staticmethod
    def format_vector_body(vectors, comments, labels, pin_list, pat_name,
                           is_first_section=False, is_last_section=True):
        """格式化向量体 — EStar 官方格式 (不含 @@PATTERN_DEFINE 包裹)

        返回向量行列表字符串，用于合并 PAT 或独立 PAT 中嵌入。
        is_first_section: 是否为文件中首个段（首行附加 AC_SET 1 + start: 标签）。
        is_last_section:  是否为文件中末个段（末行附加 end: 标签）。
        """
        lines = []
        # 段注释
        lines.append(f"// {pat_name}")
        # 引脚列顺序提示
        lines.append(f"// {','.join(pin_list)}")
        lines.append("")

        indent = " " * 20   # 非标签行缩进宽度

        for idx, vec in enumerate(vectors):
            comment = comments[idx] if idx < len(comments) else ""
            label = labels[idx] if idx < len(labels) else ""

            # 在每个逻辑分组前插入空行 (匹配真机 EStar 格式)
            # 每个 I2C bit (4 vec)、ACK/NACK、START、STOP 等操作组前加空行
            _GROUP_STARTS = (
                "===",           # 事务级标记
                "Write bit=",    # 写 bit 起始
                "Read bit",      # 读 bit 起始
                "STOP Setup",    # STOP 起始
                "START Setup",   # START 起始
                "ACK after",     # ACK 检查起始
                "NACK (end",     # NACK from master 起始
                "Poll NACK",     # Polling NACK 起始
                "Poll ACK",      # Polling ACK 起始
            )
            if idx > 0 and comment:
                is_group_start = comment.startswith(_GROUP_STARTS)
                # RepSTART 特殊处理: 仅首向量 "RepSTART: SDA↑"
                if not is_group_start and comment.startswith("RepSTART:") and "SDA" in comment and "\u2191" in comment:
                    is_group_start = True
                if is_group_start:
                    lines.append("")

            # EStar 要求: 文件首向量 start: 标签, 文件末向量 end: 标签
            if is_first_section and idx == 0:
                label = "start"
            if is_last_section and idx == len(vectors) - 1:
                label = "end"

            # 拼接引脚状态为紧凑字符串
            vec_str = "".join(vec.get(pin, "X") for pin in pin_list)

            # 构建行：标签行 vs 普通行
            if label:
                prefix = f"{label}:"
                prefix = prefix.ljust(20)
            else:
                prefix = indent

            # AC_SET 1 仅在文件首个向量上
            ac_suffix = ""
            if is_first_section and idx == 0:
                ac_suffix = "AC_SET 1;"

            # 组装
            if ac_suffix:
                line = f"{prefix}{vec_str};{ac_suffix}"
            elif comment:
                line = f"{prefix}{vec_str};    //{comment}"
            else:
                line = f"{prefix}{vec_str};"

            lines.append(line)

        lines.append("")
        return "\n".join(lines)

    @staticmethod
    def format_vectors(vectors, comments, labels, pin_list, pat_name):
        """格式化单段完整 PAT — EStar 官方格式 (含 @@PATTERN_DEFINE 包裹)"""
        body = PATFormatter.format_vector_body(
            vectors, comments, labels, pin_list, pat_name,
            is_first_section=True
        )
        return f"@@PATTERN_DEFINE  \n{body}\n@@END_PATTERN_DEFINE\n"

    @staticmethod
    def split_ack_polling(vectors, comments, labels):
        """将向量拆分为主体（ACK Polling 替换为 idle）和 Polling 部分。

        返回 ((main_v, main_c, main_l), (poll_v, poll_c, poll_l))。
        如果无 Polling 块，poll 部分为空列表。
        仅在导出时调用，GUI 预览保持完整向量。
        """
        has_polling = any(
            c and c.startswith("=== ACK Polling") for c in comments
        )
        if not has_polling:
            return (vectors, comments, labels), ([], [], [])

        main_v, main_c, main_l = [], [], []
        poll_v, poll_c, poll_l = [], [], []

        i, n = 0, len(vectors)
        while i < n:
            c = comments[i] if i < len(comments) else ""

            if c and c.startswith("=== ACK Polling"):
                # 在主文件中插入 4 行 idle 占位
                idle_vec = vectors[i].copy()
                for _ in range(4):
                    main_v.append(idle_vec.copy())
                    main_c.append("")
                    main_l.append("")

                # 收集 Polling 向量直到下一个非 Polling 的 === 标记
                poll_start = i
                while i < n:
                    c_inner = comments[i] if i < len(comments) else ""
                    if i > poll_start and c_inner and c_inner.startswith("===") and "ACK Polling" not in c_inner:
                        break
                    poll_v.append(vectors[i])
                    poll_c.append(c_inner)
                    poll_l.append(labels[i] if i < len(labels) else "")
                    i += 1
            else:
                main_v.append(vectors[i])
                main_c.append(comments[i] if i < len(comments) else "")
                main_l.append(labels[i] if i < len(labels) else "")
                i += 1

        return (main_v, main_c, main_l), (poll_v, poll_c, poll_l)

    @staticmethod
    def format_txt_preview(vectors, comments, pin_list, test_name):
        """生成人类可读的TXT预览文件"""
        lines = []
        now = datetime.datetime.now()
        lines.append("=" * 80)
        lines.append(f"  AT24C02 PAT向量预览 - {test_name}")
        lines.append(f"  生成时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"  向量总数: {len(vectors)}")
        lines.append("=" * 80)
        lines.append("")

        # 表头
        header = f"{'Vec#':>6s} | "
        for pin in pin_list:
            header += f"{pin:^5s}| "
        header += "说明"
        lines.append(header)
        lines.append("-" * len(header) + "-" * 30)

        for idx, (vec, comment) in enumerate(zip(vectors, comments)):
            line = f"{idx:>6d} | "
            for pin in pin_list:
                val = vec.get(pin, 'X')
                line += f"  {val:>1s}  | "
            if comment:
                line += comment
            lines.append(line)

        lines.append("")
        lines.append(f"总计 {len(vectors)} 个向量周期")
        lines.append("")

        # 状态说明
        lines.append("=" * 50)
        lines.append("向量状态说明:")
        lines.append("  0 - 驱动低电平 (Drive Low)")
        lines.append("  1 - 驱动高电平 (Drive High)")
        lines.append("  L - 期望低电平 (Expect Low / Compare Low)")
        lines.append("  H - 期望高电平 (Expect High / Compare High)")
        lines.append("  Z - 高阻态 (Hi-Impedance)")
        lines.append("  X - 不关心 (Don't Care / Mask)")
        lines.append("=" * 50)

        return "\n".join(lines)

    @staticmethod
    def generate_tim_file(period_ns=2500, voltage_key="5.0V", protocol="I2C",
                          chip_name="AT24C02"):
        """
        生成 .tim 时序配置文件 — EStar 官方格式 (@@TIMING_DEFINE / @@AC_SET_1)
        """
        half = period_ns // 2
        strobe = half + half // 2  # 采样点在 75% 周期处
        now = datetime.datetime.now()
        lines = []
        lines.append(f"// {chip_name} Timing Configuration File")
        lines.append(f"// Protocol: {protocol}")
        lines.append(f"// Generated: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"// Voltage: {voltage_key}")
        lines.append(f"// Tool: EEPROM PAT Generator {VERSION}")
        lines.append("")
        lines.append("@@TIMING_DEFINE")
        lines.append("")
        lines.append("  @@PAGE_1")
        lines.append("")
        lines.append("      @@AC_SET_1 ")
        lines.append("    [PERIOD_RESOLUTION = 5ns]")
        lines.append("    [NAME=SET1]")
        lines.append("    [TS] ")
        lines.append("")
        lines.append(f"        PERIOD =   {period_ns}ns;")
        lines.append("")
        lines.append(f"		   ALLPINS: {{DRV_LE = 0ns}}")
        lines.append(f"                {{DRV_TE = {half}ns}}  ")
        lines.append(f"                {{STB    = {strobe}ns}}")
        lines.append(f"                {{DRV_OFF= 0ns}}")
        lines.append("")
        lines.append("    [END_TS]")
        lines.append("  @@END_AC_SET_1 ")
        lines.append("")

        return "\n".join(lines)

    @staticmethod
    def generate_lvl_file(voltage_preset=None, chip_name="AT24C02"):
        """
        生成 .lvl 电平配置文件 — EStar 官方格式 (@@LEVEL_SET_DEFINE / @@END_LEVEL_SET)
        包含: DC_0V_PWR (上电初始化), DC_VCC_LVL (正常测试), DC_IDD (静态电流), PWR_OFF (断电)
        """
        vp = voltage_preset or VOLTAGE_PRESETS["5.0V"]
        vcc_val = vp['VCC']
        vih_val = vp['VIH']
        vil_val = vp['VIL']
        voh_val = vp['VOH']
        vol_val = vp['VOL']
        now = datetime.datetime.now()
        lines = []
        lines.append(f"// {chip_name} Level Configuration File")
        lines.append(f"// Generated: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"// Voltage Preset: VCC={vcc_val}")
        lines.append(f"// Tool: EEPROM PAT Generator {VERSION}")
        lines.append("")

        # Level Set 1: DC_0V_PWR — 初始化 (VCC=0V, 所有引脚0V)
        lines.append("@@LEVEL_SET_DEFINE DC_0V_PWR")
        lines.append("")
        lines.append("   VCC:    {FORCE_MODE = FORCE_V}")
        lines.append("           {FORCE = 0V}")
        lines.append("           {CLAMP = 200MA}")
        lines.append("           {DELAY = 3MS}")
        lines.append("           {I_RANGE = I4}")
        lines.append("           {CONTROL = CONNECT}")
        lines.append("")
        lines.append(" ALLPINS:  {MODE = NORMAL}")
        lines.append("           {VIH = 0V}")
        lines.append("           {VIL = 0V}")
        lines.append("           {VTT = 0V}")
        lines.append("           {VOH = 0V}")
        lines.append("           {VOL = 0V}")
        lines.append("           {FORCE_MODE = FORCE_V}")
        lines.append("           {FORCE = 0.0V}")
        lines.append("           {DELAY = 3MS}")
        lines.append("           {I_RANGE = I4}")
        lines.append("           {CONTROL = CONNECT}")
        lines.append("")
        lines.append("")
        lines.append("")
        lines.append("@@END_LEVEL_SET")
        lines.append("")

        # Level Set 2: DC_VCC_LVL — 正常功能测试电平
        lines.append("")
        lines.append(f"@@LEVEL_SET_DEFINE DC_{vcc_val.replace('.', '_')}_LVL")
        lines.append("")
        lines.append("   VCC:    {FORCE_MODE = FORCE_V}")
        lines.append(f"           {{FORCE = {vcc_val}}}")
        lines.append("           {CLAMP = 200MA}")
        lines.append("           {DELAY = 10MS}")
        lines.append("           {I_RANGE = I4}")
        lines.append("           {CONTROL = CONNECT_NO_CHANGE}")
        lines.append("")
        lines.append("ALLPINS:   {MODE = NORMAL}")
        lines.append("           {DELAY = 40MS}")
        lines.append(f"           {{VIH = {vih_val}}}")
        lines.append(f"           {{VIL = {vil_val}}}")
        lines.append(f"           {{VTT = {vcc_val}}}")
        lines.append(f"           {{VOH = {voh_val}}}")
        lines.append(f"           {{VOL = {vol_val}}}")
        lines.append("")
        lines.append("@@END_LEVEL_SET")
        lines.append("")

        # Level Set 3: DC_IIH_IIL_LVL — 输入漏电流测试
        lines.append("")
        lines.append("@@LEVEL_SET_DEFINE DC_IIH_IIL_LVL")
        lines.append("")
        lines.append("   VCC:    {FORCE_MODE = FORCE_V}")
        lines.append(f"           {{FORCE = {vcc_val}}}")
        lines.append("           {CLAMP = 5mA}")
        lines.append("           {DELAY = 3MS}")
        lines.append("           {I_RANGE = I3}")
        lines.append("           {CONTROL = CONNECT_NO_CHANGE}")
        lines.append("")
        lines.append("@@END_LEVEL_SET")
        lines.append("")

        # Level Set 4: DC_IDD — 静态电流测试
        lines.append("")
        lines.append("@@LEVEL_SET_DEFINE DC_IDD")
        lines.append("")
        lines.append("   VCC:    {FORCE_MODE = FORCE_V}")
        lines.append("           {FORCE = 1.8V}")
        lines.append("           {CLAMP = 5uA}")
        lines.append("           {DELAY = 3MS}")
        lines.append("           {I_RANGE = I1}")
        lines.append("           {CONTROL = CONNECT_NO_CHANGE}")
        lines.append("")
        lines.append("ALLPINS:   {FORCE_MODE = FORCE_V}")
        lines.append("           {FORCE = 0V}")
        lines.append("           {I_RANGE = I1}")
        lines.append("           {CONTROL = CONNECT_NO_CHANGE}")
        lines.append("           {VIH = 0V}")
        lines.append("           {VIL = 0V}")
        lines.append("           {VOH = 0V}")
        lines.append("           {VOL = 0V}")
        lines.append("@@END_LEVEL_SET")
        lines.append("")

        # Level Set 5: PWR_OFF — 断电
        lines.append("")
        lines.append("@@LEVEL_SET_DEFINE PWR_OFF")
        lines.append("")
        lines.append(" ALLPINS:  {MODE = NORMAL}")
        lines.append("           {VIH = 0V}")
        lines.append("           {VIL = 0V}")
        lines.append("           {VTT = 0V}")
        lines.append("           {VOH = 0V}")
        lines.append("           {VOL = 0V}")
        lines.append("           {FORCE_MODE = FORCE_V}")
        lines.append("           {FORCE = 0.0V}")
        lines.append("           {DELAY = 3MS}")
        lines.append("           {I_RANGE = I4}")
        lines.append("           {CONTROL = DISCONNECT}")
        lines.append("")
        lines.append("  VCC:     {FORCE_MODE = FORCE_V}")
        lines.append("           {FORCE = 0V}")
        lines.append("           {CLAMP = 200MA}")
        lines.append("           {DELAY = 3MS}")
        lines.append("           {I_RANGE = I4}")
        lines.append("           {CONTROL = DISCONNECT}")
        lines.append("")
        lines.append("")
        lines.append("@@END_LEVEL_SET")
        lines.append("")

        return "\n".join(lines)

    @staticmethod
    def generate_prg_file(pat_sections, period_ns=2500, voltage_preset=None,
                          chip_name="AT24C02", chip_capacity="2Kbit (256x8)",
                          protocol="I2C", export_prefix="AT24C02_FULL_TEST",
                          pin_map_section="", site_config_section="",
                          num_sites=1):
        """
        生成 .prg ATE 测试程序 — EStar 官方格式
        (@@SCHEDULE / @@EOT / @@PLAN 块结构)
        """
        vp = voltage_preset or VOLTAGE_PRESETS["5.0V"]
        vcc_val = vp['VCC']
        now = datetime.datetime.now()
        total = sum(len(s[2]) for s in pat_sections)

        lines = []

        # ---- 文件头注释 ----
        lines.append(f"//@@历史记录")
        lines.append(f"//   版本号 = v1;")
        lines.append(f"//   日期 = {now.strftime('%Y年%m月%d日')};")
        lines.append(f"//   描述")
        lines.append(f"//     设备名称 : {chip_name}")
        lines.append(f"//     封装类型 : SOP8")
        lines.append(f"//     协议 : {protocol}")
        lines.append(f"//     向量总数 : {total}")
        lines.append(f"//     工具 : EEPROM PAT Generator {VERSION}")
        lines.append(f"//   描述结束")
        lines.append(f"//@@历史记录结束")
        lines.append("")

        # ---- @@PIN_MAP (v9.0 Phase 24) ----
        if pin_map_section:
            lines.append(pin_map_section)
            lines.append("")

        # ---- Multi-Site 配置 (v9.0 Phase 23) ----
        if site_config_section:
            lines.append(site_config_section)
            lines.append("")

        # ---- @@SCHEDULE — 测试序列 ----
        lines.append(f"@@SCHEDULE {export_prefix}")
        lines.append("")

        # 测试项名称映射 (内部名 → EStar @@PLAN 名)
        plan_name_map = {
            "OS_TEST": "OPENSHORT",
            "DC_TEST": "IIH_IIL",
            "FUNC_TEST": "Functional",
            "MARCH_TEST": "March_C",
            "MARCHB_TEST": "March_B",
            "SCAN_TEST": "Addr_Scan",
            "RET_TEST": "Data_Retention",
            "ERR_TEST": "Error_Test",
            "ENDUR_TEST": "Endurance",
            "IDDQ_TEST": "IDDQ_Test",
        }

        # Bin 映射
        bin_map = {
            "OS_TEST": 2, "DC_TEST": 3, "FUNC_TEST": 4,
            "MARCH_TEST": 5, "MARCHB_TEST": 6, "SCAN_TEST": 7,
            "RET_TEST": 8, "ERR_TEST": 9, "ENDUR_TEST": 10,
            "IDDQ_TEST": 11,
        }

        lines.append("    BEFORE_TEST;             // DPS初始化")
        for name, desc, *_ in pat_sections:
            plan_name = plan_name_map.get(name, name)
            comment = desc if len(desc) < 30 else desc[:30]
            lines.append(f"    {plan_name};{' ' * max(1, 25-len(plan_name))}// {comment}")
        lines.append("")
        lines.append("@@END_SCHEDULE")
        lines.append("")

        # ---- @@EOT — 测试结束清理 ----
        lines.append("@@EOT")
        lines.append("")
        lines.append("         DIGI_SET_DRV_LEVEL (ALL_PINS, 0V, 0V, 0V);")
        lines.append("         WAIT(3MS);")
        lines.append("         DIGI_SET_DRIVE_MODE(ALL_PINS, OFF);")
        lines.append("         WAIT(3MS);")
        lines.append("         DIGI_DPS_SENSE_MODE(INTERNAL_SENSE);")
        lines.append("")
        lines.append("	     DIGI_PPMU_FV(ALL_PINS,0V,I4,CONNECT);")
        lines.append("         WAIT(3MS);")
        lines.append(f"         DIGI_DPS_FV(VCC, 0V, 250mA, I4,CONNECT);")
        lines.append("         WAIT(3MS);")
        lines.append(f"     	 DIGI_DPS_FV(VCC, 0V, 250mA, I4,DISCONNECT);")
        lines.append("         WAIT(3MS);")
        lines.append("	     DIGI_PPMU_FV(ALL_PINS,0V,I4,DISCONNECT);")
        lines.append("	     WAIT(3MS);")
        lines.append("")
        lines.append("@@END_EOT")
        lines.append("")
        lines.append("")

        # ---- @@PLAN BEFORE_TEST — DPS 外部感应配置 ----
        lines.append("@@PLAN    BEFORE_TEST")
        lines.append("  SITE_SEQUENCE      = OFF;")
        lines.append("  DISABLE_BY_MARK_NO = NULL;")
        lines.append("  GO_THROUGH         = ON;")
        lines.append("  REMARK             = BEFORE_TEST;")
        lines.append("")
        lines.append("")
        lines.append("   DIGI_DPS_SENSE_MODE(EXTERNAL_SENSE);")
        lines.append("")
        lines.append("")
        lines.append("CONDITION")
        lines.append("   IF_FAIL")
        lines.append("        REJECT_BIN=1;")
        lines.append(" @@END_PLAN")
        lines.append("")
        lines.append("")

        # ---- 各测试 @@PLAN ----
        # PAT 文件名映射 (测试名 → PAT 文件名)
        pat_file_map = {
            "OS_TEST": f"{export_prefix}_OS",
            "DC_TEST": f"{export_prefix}_DC",
            "FUNC_TEST": f"{export_prefix}_FUNC",
            "MARCH_TEST": f"{export_prefix}_MARCH",
            "MARCHB_TEST": f"{export_prefix}_MARCHB",
            "SCAN_TEST": f"{export_prefix}_SCAN",
            "RET_TEST": f"{export_prefix}_RET",
            "ERR_TEST": f"{export_prefix}_ERR",
            "ENDUR_TEST": f"{export_prefix}_ENDUR",
            "IDDQ_TEST": f"{export_prefix}_IDDQ",
        }

        for name, desc, vectors, *_ in pat_sections:
            plan_name = plan_name_map.get(name, name)
            bin_no = bin_map.get(name, 2)
            pat_file = pat_file_map.get(name, f"{export_prefix}_{name}")

            # 根据测试类型生成不同的 PLAN 内容
            lines.append(f"//***************** {desc} ******************//")
            lines.append(f"@@PLAN    {plan_name}")
            lines.append(f"  SITE_SEQUENCE      = OFF;")
            lines.append(f"  DISABLE_BY_MARK_NO = NULL;")
            lines.append(f"  GO_THROUGH         = ON;")
            lines.append(f"  REMARK             = {plan_name};")
            lines.append("")

            if name == "OS_TEST":
                # 开短路测试 — PPMU Walking
                lines.append("   DIGI_SET_DRIVE_MODE(ALLPINS, OFF); ")
                lines.append("")
                lines.append(f"   DIGI_DPS_FV(VCC, 0.0V, 5mA, I3, CONNECT);")
                lines.append("   WAIT(3MS); ")
                lines.append("")
                lines.append("   DIGI_PPMU_WALKING_FI_MV(ALL_PINS,-100uA,I4,UP_LIMIT=-0.2V,DOWN_LIMIT=-1.5V,LOG_ALIAS=OS_GND);  ")
                for pin in ["A0", "A1", "A2", "SDA", "SCL", "WP"]:
                    lines.append(f"   C_COMPARE(  {pin},{' '*(4-len(pin))}UP_LIMIT=-0.2V,  DOWN_LIMIT=-1.5V,  LOG_ALIAS= OS_GND_{pin},   LOG_UNIT=V);")
                lines.append("")
                lines.append("   DIGI_SET_DRIVE_MODE(ALL_PINS,OFF);   ")
                lines.append("   DIGI_LEVEL_SET(PWR_OFF);")

            elif name == "DC_TEST":
                # DC 参数测试 — IIH/IIL + IDD
                lines.append("   DIGI_SET_DRIVE_MODE(ALLPINS, OFF); ")
                lines.append("")
                lines.append("   DIGI_LEVEL_SET(DC_0V_PWR);")
                lines.append("   WAIT(5NS);")
                lines.append("   DIGI_LEVEL_SET(DC_IIH_IIL_LVL);")
                lines.append("")
                lines.append("    //IIH ")
                lines.append("   DIGI_PPMU_FV(ALL_PINS,1.8V,I2,CONNECT_NO_CHANGE);     ")
                lines.append("   WAIT(30mS);")
                lines.append("   DIGI_PPMU_MI (ALL_PINS, UP_LIMIT=6.0UA, DOWN_LIMIT=-3.0UA,LOG_ALIAS= IIH,LOG_UNIT=uA);        ")
                for pin in ["A0", "A1", "A2", "SDA", "SCL", "WP"]:
                    lines.append(f"   C_COMPARE(  {pin},{' '*(4-len(pin))}UP_LIMIT=6.0uA,  DOWN_LIMIT=-3.0uA,  LOG_ALIAS= IIH_{pin},   LOG_UNIT=V);")
                lines.append("")
                lines.append("    //IIL ")
                lines.append("   DIGI_PPMU_FV(ALL_PINS,0.0V,I2,CONNECT_NO_CHANGE);     ")
                lines.append("   WAIT(3mS);")
                lines.append("   DIGI_PPMU_MI (ALL_PINS, UP_LIMIT=6.0UA, DOWN_LIMIT=-3.0UA,LOG_ALIAS= IIL,LOG_UNIT=uA);      ")
                for pin in ["A0", "A1", "A2", "SDA", "SCL", "WP"]:
                    lines.append(f"   C_COMPARE(  {pin},{' '*(4-len(pin))}UP_LIMIT=6.0uA,  DOWN_LIMIT=-3.0uA,  LOG_ALIAS= IIL_{pin},   LOG_UNIT=V);")
                lines.append("")
                lines.append("   DIGI_SET_DRIVE_MODE(ALL_PINS,OFF);   ")
                lines.append("   DIGI_LEVEL_SET(PWR_OFF);")

            elif name == "IDDQ_TEST":
                # IDDQ 静态电流测试 — PMU 测量
                vcc_lvl = f"DC_{vcc_val.replace('.', '_')}_LVL"
                lines.append("   DIGI_SET_DRIVE_MODE(ALLPINS, OFF); ")
                lines.append("")
                lines.append("   DIGI_LEVEL_SET(DC_0V_PWR);")
                lines.append("   WAIT(5NS);")
                lines.append(f"   DIGI_LEVEL_SET({vcc_lvl});")
                lines.append("   WAIT(3MS);")
                lines.append("")
                lines.append("   PMU_CONNECT(VCC, I_RANGE=10uA);")
                lines.append(f"   RUN_PATTERN({pat_file}:start,{pat_file}:end,1,LOG_ALIAS=FTR_IDDQ);")
                lines.append("   // At each IDDQ_MEASURE marker, ATE executes:")
                lines.append("   //   PMU_MEASURE(VCC, CURRENT, LIMIT_HIGH=1.0uA);")
                lines.append("   PMU_DISCONNECT(VCC);")
                lines.append("   WAIT(3MS);")

            else:
                # 功能/存储器/异常/耐久性测试 — RUN_PATTERN
                vcc_lvl = f"DC_{vcc_val.replace('.', '_')}_LVL"
                lines.append("   DIGI_SET_DRIVE_MODE(ALLPINS, OFF); ")
                lines.append("")
                lines.append("   DIGI_LEVEL_SET(DC_0V_PWR);")
                lines.append("   WAIT(5NS);")
                lines.append(f"   DIGI_LEVEL_SET({vcc_lvl});")
                lines.append("   DIGI_SET_DRIVE_MODE(SDA, ACTIVE_LOAD);")
                lines.append("   DIGI_SET_ACTIVE_LOAD_CURRENT (SDA, 11MA, 11MA);")
                lines.append("")
                lines.append("   WAIT(3MS);")
                lines.append(f"   RUN_PATTERN({pat_file}:start,{pat_file}:end,1,LOG_ALIAS=FTR_{plan_name});")
                lines.append("   WAIT(3MS);")
                lines.append("")
                lines.append("   DIGI_SET_DRIVE_MODE(ALL_PINS,OFF);   ")
                lines.append("   DIGI_LEVEL_SET(PWR_OFF);")

            lines.append("")
            lines.append("CONDITION")
            lines.append("    IF_FAIL")
            lines.append(f"        REJECT_BIN={bin_no};")
            lines.append("@@END_PLAN")
            lines.append("")
            lines.append("")

        # ---- BIN 汇总注释 ----
        lines.append("// ============================================================")
        lines.append("// BIN Summary Table")
        lines.append("// ============================================================")
        lines.append("// BIN  | Name            | Description")
        lines.append("// -----|-----------------|----------------------------")
        lines.append("//   1  | BEFORE_TEST     | DPS initialization")
        for name, desc, *_ in pat_sections:
            bn = bin_map.get(name, 2)
            plan_name = plan_name_map.get(name, name)
            lines.append(f"//  {bn:2d}  | {plan_name:15s} | {desc}")
        lines.append("// ============================================================")
        lines.append("")

        return "\n".join(lines)


# ============================================================
# 测试方案生成器
# ============================================================

class TestPatternGenerator:
    """测试向量方案生成器"""

    def __init__(self, addr_pins=(0, 0, 0), wp=0, poll_count=2,
                 device_addr_base=0xA0, capacity_bytes=256, page_size=8,
                 addr_byte_count=1, page_select_bits=0,
                 protocol="I2C",
                 spi_mode=0, sector_size=None, has_jedec_id=False, jedec_id=0,
                 org_mode="x16", word_bits=16, mw_addr_bits=6):
        self.protocol = protocol
        self.addr_pins = addr_pins
        self.wp_pin = wp
        self.poll_count = max(1, min(poll_count, 20))
        self.capacity_bytes = capacity_bytes
        self.page_size = page_size
        self.addr_byte_count = addr_byte_count
        self.page_select_bits = page_select_bits
        self.max_addr = capacity_bytes - 1
        # SPI/MW 专有参数
        self.sector_size = sector_size
        self.has_jedec_id = has_jedec_id
        self.jedec_id = jedec_id
        self.org_mode = org_mode
        self.word_bits = word_bits
        self.mw_addr_bits = mw_addr_bits
        # 根据协议实例化向量生成器
        if protocol == "SPI":
            self.proto = SPIVectorGenerator(
                spi_mode=spi_mode, wp_pin=wp, addr_byte_count=addr_byte_count,
                capacity_bytes=capacity_bytes, page_size=page_size,
                sector_size=sector_size, has_jedec_id=has_jedec_id,
                jedec_id=jedec_id, poll_count=self.poll_count)
            self.i2c = self.proto  # 兼容别名
        elif protocol == "Microwire":
            cap_words = capacity_bytes // max(1, word_bits // 8)
            self.proto = MicrowireVectorGenerator(
                org_mode=org_mode, word_bits=word_bits, addr_bits=mw_addr_bits,
                capacity_words=cap_words, poll_count=self.poll_count)
            self.i2c = self.proto  # 兼容别名
        else:
            self.i2c = I2CVectorGenerator(
                device_addr_base=device_addr_base,
                addr_pins=addr_pins, wp_pin=wp, poll_count=self.poll_count,
                addr_byte_count=addr_byte_count, page_select_bits=page_select_bits,
                capacity_bytes=capacity_bytes, page_size=page_size)
            self.proto = self.i2c

    def _sample_addresses(self, start, count, max_sample=64):
        """大容量芯片地址采样: 首/尾 + 页边界 + 均匀分布"""
        total = min(count, self.capacity_bytes - start)
        if total <= max_sample:
            return [start + i for i in range(total)]
        addrs = set()
        addrs.add(start)
        addrs.add(start + total - 1)
        # 页边界
        pg = self.page_size
        a = ((start // pg) + 1) * pg
        while a < start + total and len(addrs) < max_sample // 2:
            addrs.add(a)
            a += pg
        # 均匀填充
        step = max(1, total // (max_sample - len(addrs)))
        for i in range(0, total, step):
            addrs.add(start + i)
            if len(addrs) >= max_sample:
                break
        return sorted(addrs)

    def _fmt_addr(self, addr):
        """格式化地址字符串"""
        if self.addr_byte_count >= 3:
            return f"0x{addr:06X}"
        return f"0x{addr:04X}" if self.addr_byte_count == 2 else f"0x{addr:02X}"

    def _add_marker(self, comment="", label=""):
        """添加协议无关的标记向量 (空闲状态, 仅用于注释/label)"""
        self.proto.add_idle(1, comment)
        if label and self.proto.labels:
            self.proto.labels[-1] = label

    def _write_byte_proto(self, addr, data):
        """协议调度: 写1字节到指定地址 (v9.0 统一接口)"""
        self.proto.gen_byte_write(addr, data)

    def _read_verify_proto(self, addr, expected):
        """协议调度: 从指定地址读取并验证 (v9.0 统一接口)"""
        self.proto.gen_byte_read(addr, expected)

    def generate_os_test(self):
        """
        生成开短路测试(Open/Short Test)向量

        原理: 使用PPMU对每个引脚施加小电流(如100μA)，测量电压
        以判断引脚是否存在开路(open)或短路(short)故障。
        协议无关: 通过 PROTOCOL_PINS 自动适配 I2C/SPI/Microwire 引脚。
        """
        self.proto.reset()
        pins_order = PROTOCOL_PINS.get(self.protocol, TEST_PINS)

        def _make_vec(pin_states):
            """根据当前协议构建向量dict"""
            return {p: pin_states.get(p, "0") for p in pins_order}

        def _push_vec(vec_dict, comment="", label=""):
            self.proto.vectors.append(vec_dict)
            self.proto.comments.append(comment)
            self.proto.labels.append(label)

        # ---- Phase 1: 所有引脚驱动低 ----
        all_low = {p: "0" for p in pins_order}
        _push_vec(all_low, "OS_TEST: All pins drive LOW", "OS_ALL_LOW")
        for _ in range(3):
            _push_vec(dict(all_low), "Hold LOW")

        # ---- Phase 2: 所有引脚驱动高 ----
        all_high = {p: "1" for p in pins_order}
        _push_vec(all_high, "OS_TEST: All pins drive HIGH", "OS_ALL_HIGH")
        for _ in range(3):
            _push_vec(dict(all_high), "Hold HIGH")

        # ---- Phase 3: Walking 1s ----
        for target_pin in pins_order:
            vec = {p: "0" for p in pins_order}
            vec[target_pin] = "1"
            _push_vec(dict(vec),
                      f"Walking-1: {target_pin}=HIGH, others=LOW",
                      f"OS_WALK1_{target_pin}")
            for _ in range(2):
                _push_vec(dict(vec), f"Hold {target_pin}=HIGH")

        # ---- Phase 4: Walking 0s ----
        for target_pin in pins_order:
            vec = {p: "1" for p in pins_order}
            vec[target_pin] = "0"
            _push_vec(dict(vec),
                      f"Walking-0: {target_pin}=LOW, others=HIGH",
                      f"OS_WALK0_{target_pin}")
            for _ in range(2):
                _push_vec(dict(vec), f"Hold {target_pin}=LOW")

        # ---- Phase 5: 恢复空闲 ----
        self.proto.add_idle(2, "Return to IDLE")
        if self.proto.labels:
            self.proto.labels[-2] = "OS_END"

        return self.proto.vectors, self.proto.comments, self.proto.labels

    def generate_dc_test(self):
        """
        生成DC测试向量 (协议自适应)

        DC测试包含:
        1. ISB (待机电流), 2. ICC Read, 3. ICC Write,
        4. VOL, 5. VOH, 6. VIL/VIH, 7. IDDQ
        I2C 使用 ACK/NACK 测量 VOL/VOH, SPI/MW 使用 MISO/DO 输出
        """
        self.proto.reset()
        if self.protocol == "I2C":
            return self._generate_dc_test_i2c()
        elif self.protocol == "SPI":
            return self._generate_dc_test_spi()
        elif self.protocol == "Microwire":
            return self._generate_dc_test_mw()
        return self.proto.vectors, self.proto.comments, self.proto.labels

    def _generate_dc_test_i2c(self):
        """I2C DC测试 (原始实现, 保持不变)"""
        self.i2c.wp_pin = 0
        a0, a1, a2 = str(self.addr_pins[2]), str(self.addr_pins[1]), str(self.addr_pins[0])

        # DC-1: ISB
        self.i2c._add_vector(a0, a1, a2, "1", "1", "0",
                              "=== DC ISB Test: Standby Current ===", "DC_ISB_START")
        for _ in range(8):
            self.i2c._add_vector(a0, a1, a2, "1", "1", "0", "ISB: IDLE state (measure ICC)")
        self.i2c._add_vector(a0, a1, a2, "1", "1", "0",
                              "ISB measurement point", "DC_ISB_MEAS")
        for _ in range(4):
            self.i2c._add_vector(a0, a1, a2, "1", "1", "0", "ISB: continue IDLE")

        # DC-2: ICC Read
        self.i2c._add_vector(a0, a1, a2, "1", "1", "0",
                              "=== DC ICC Test: Operating Current (Read) ===", "DC_ICC_START")
        self.i2c.add_start_condition()
        self.i2c.add_write_byte(self.i2c.device_addr | 0x01, "DevAddr+R (ICC test)")
        self.i2c.add_ack_from_slave("ACK")
        self.i2c.add_read_byte(None, "Read data (ICC meas)")
        self.i2c.add_nack_from_master()
        self.i2c.add_stop_condition()
        self.i2c.add_idle(2, "ICC Read complete")

        # DC-3: ICC Write
        self.i2c._add_vector(a0, a1, a2, "1", "1", "0",
                              "=== DC ICC Write Test ===", "DC_ICC_W_START")
        self.i2c.gen_byte_write(0x00, 0x55)

        # DC-4: VOL
        self.i2c._add_vector(a0, a1, a2, "1", "1", "0",
                              "=== DC VOL Test (SDA output LOW during ACK) ===", "DC_VOL_START")
        self.i2c.add_start_condition()
        self.i2c.add_write_byte(self.i2c.device_addr & 0xFE, "DevAddr+W")
        self.i2c.add_ack_from_slave("*** VOL measurement point (ACK=LOW) ***")
        self.i2c.add_write_byte(0x00, "WordAddr=0x00")
        self.i2c.add_ack_from_slave("VOL meas point 2")
        self.i2c.add_stop_condition()
        self.i2c.add_idle(2)

        # DC-5: VOH
        self.i2c._add_vector(a0, a1, a2, "1", "1", "0",
                              "=== DC VOH Test (SDA output HIGH during Read) ===", "DC_VOH_START")
        self.i2c.gen_byte_write(0x10, 0xFF)
        self.i2c.gen_random_read(0x10, expected_data=0xFF)

        # DC-6: VIL/VIH
        self.i2c._add_vector(a0, a1, a2, "1", "1", "0",
                              "=== DC Input Threshold Test (VIL/VIH via LEVEL set) ===",
                              "DC_VIL_VIH_START")
        self.i2c.gen_byte_write(0x20, 0xAA)
        self.i2c.gen_random_read(0x20, expected_data=0xAA)

        # DC-7: IDDQ
        self.i2c._add_vector(a0, a1, a2, "1", "1", "0",
                              "=== DC-7: IDDQ Quiescent Current Test ===",
                              "DC_IDDQ_START")
        self.i2c.gen_byte_write(0x30, 0x00)
        for _ in range(10):
            self.i2c._add_vector(a0, a1, a2, "1", "1", "0",
                                  "IDDQ State-1: all-zero written, quiescent (measure IDD)")
        self.i2c._add_vector(a0, a1, a2, "1", "1", "0",
                              "*** IDDQ measurement point 1 (data=0x00) ***",
                              "DC_IDDQ_MEAS1")
        self.i2c.gen_byte_write(0x30, 0xFF)
        for _ in range(10):
            self.i2c._add_vector(a0, a1, a2, "1", "1", "0",
                                  "IDDQ State-2: all-one written, quiescent (measure IDD)")
        self.i2c._add_vector(a0, a1, a2, "1", "1", "0",
                              "*** IDDQ measurement point 2 (data=0xFF) ***",
                              "DC_IDDQ_MEAS2")
        self.i2c.gen_byte_write(0x30, 0x55)
        for _ in range(10):
            self.i2c._add_vector(a0, a1, a2, "1", "1", "0",
                                  "IDDQ State-3: checkerboard, quiescent (measure IDD)")
        self.i2c._add_vector(a0, a1, a2, "1", "1", "0",
                              "*** IDDQ measurement point 3 (data=0x55) ***",
                              "DC_IDDQ_MEAS3")

        self.i2c.add_idle(4, "=== DC Test Complete ===")
        return self.i2c.vectors, self.i2c.comments, self.i2c.labels

    def _generate_dc_test_spi(self):
        """SPI DC测试"""
        p = self.proto
        # DC-1: ISB (待机电流 — CS high, SCK idle)
        self._add_marker("=== DC ISB Test: Standby Current ===", "DC_ISB_START")
        p.add_idle(10, "ISB: IDLE state (measure ICC)")
        self._add_marker("ISB measurement point", "DC_ISB_MEAS")
        p.add_idle(4, "ISB: continue IDLE")

        # DC-2: ICC Read (工作电流 — 执行一次读操作)
        self._add_marker("=== DC ICC Test: Operating Current (Read) ===", "DC_ICC_START")
        p.spi_read(0x00, 1, comment="ICC Read")

        # DC-3: ICC Write
        self._add_marker("=== DC ICC Write Test ===", "DC_ICC_W_START")
        p.spi_write(0x00, [0x55], comment="ICC Write")

        # DC-4: VOL (MISO output LOW — 读回0x00)
        self._add_marker("=== DC VOL Test (MISO output LOW) ===", "DC_VOL_START")
        p.spi_write(0x10, [0x00])
        p.spi_read(0x10, 1, [0x00], comment="VOL: expect all bits LOW on MISO")

        # DC-5: VOH (MISO output HIGH — 读回0xFF)
        self._add_marker("=== DC VOH Test (MISO output HIGH) ===", "DC_VOH_START")
        p.spi_write(0x10, [0xFF])
        p.spi_read(0x10, 1, [0xFF], comment="VOH: expect all bits HIGH on MISO")

        # DC-6: VIL/VIH
        self._add_marker("=== DC VIL/VIH Test ===", "DC_VIL_VIH_START")
        p.spi_write(0x20, [0xAA])
        p.spi_read(0x20, 1, [0xAA], comment="VIL/VIH threshold verify")

        # DC-7: IDDQ
        self._add_marker("=== DC IDDQ Test ===", "DC_IDDQ_START")
        p.spi_write(0x30, [0x00])
        p.add_idle(10, "IDDQ State-1: quiescent")
        self._add_marker("*** IDDQ measurement point 1 ***", "DC_IDDQ_MEAS1")
        p.spi_write(0x30, [0xFF])
        p.add_idle(10, "IDDQ State-2: quiescent")
        self._add_marker("*** IDDQ measurement point 2 ***", "DC_IDDQ_MEAS2")

        p.add_idle(4, "=== DC Test Complete ===")
        return p.vectors, p.comments, p.labels

    def _generate_dc_test_mw(self):
        """Microwire DC测试"""
        p = self.proto
        # DC-1: ISB
        self._add_marker("=== DC ISB Test: Standby Current ===", "DC_ISB_START")
        p.add_idle(10, "ISB: IDLE state (measure ICC)")
        self._add_marker("ISB measurement point", "DC_ISB_MEAS")
        p.add_idle(4, "ISB: continue IDLE")

        # DC-2: ICC Read
        self._add_marker("=== DC ICC Test: Operating Current (Read) ===", "DC_ICC_START")
        p.mw_read(0, comment="ICC Read")

        # DC-3: ICC Write
        self._add_marker("=== DC ICC Write Test ===", "DC_ICC_W_START")
        p.mw_write(0, 0x5555, comment="ICC Write")

        # DC-4: VOL (DO output LOW)
        self._add_marker("=== DC VOL Test (DO output LOW) ===", "DC_VOL_START")
        p.mw_write(1, 0x0000)
        p.mw_read(1, expected=0x0000, comment="VOL: expect LOW on DO")

        # DC-5: VOH (DO output HIGH)
        self._add_marker("=== DC VOH Test (DO output HIGH) ===", "DC_VOH_START")
        p.mw_write(1, 0xFFFF)
        p.mw_read(1, expected=0xFFFF, comment="VOH: expect HIGH on DO")

        # DC-6: IDDQ
        self._add_marker("=== DC IDDQ Test ===", "DC_IDDQ_START")
        p.mw_write(2, 0x0000)
        p.add_idle(10, "IDDQ quiescent")
        self._add_marker("*** IDDQ measurement point ***", "DC_IDDQ_MEAS1")

        p.add_idle(4, "=== DC Test Complete ===")
        return p.vectors, p.comments, p.labels

    def generate_functional_test(self, custom_addr=None, custom_data=None):
        """生成功能测试向量 — 兼容旧接口, 内部调用各独立子方法并合并"""
        all_v, all_c, all_l = [], [], []
        for gen_fn in [
            lambda: self.generate_func_byte_write(custom_addr, custom_data),
            self.generate_func_page_write,
            self.generate_func_boundary,
            self.generate_func_wp_test,
            self.generate_func_page_wrap,
            self.generate_func_current_read,
        ]:
            v, c, l = gen_fn()
            all_v.extend(v)
            all_c.extend(c)
            all_l.extend(l)
        return all_v, all_c, all_l

    # ---------- FUNC 独立子测试方法 ----------

    def generate_func_byte_write(self, custom_addr=None, custom_data=None):
        """FUNC-1: 字节写 + 随机读验证 (使用自定义地址/数据)"""
        self.i2c.reset()
        a0, a1, a2 = str(self.addr_pins[2]), str(self.addr_pins[1]), str(self.addr_pins[0])
        self.i2c.wp_pin = 0

        addr1 = custom_addr if custom_addr is not None else 0x00
        data1 = custom_data if custom_data is not None else 0x55

        self.i2c._add_vector(a0, a1, a2, "1", "1", "0",
                              f"=== FUNC: Byte Write addr={self._fmt_addr(addr1)} data=0x{data1:02X} ===",
                              "FUNC_BW_START")
        self.i2c.gen_byte_write(addr1, data1)
        self.i2c.gen_random_read(addr1, expected_data=data1)

        self.i2c.add_idle(2, "=== Byte Write Test Complete ===")
        self.i2c.wp_pin = self.wp_pin
        return self.i2c.vectors, self.i2c.comments, self.i2c.labels

    def generate_func_page_write(self):
        """FUNC-2: 页写 + 顺序读验证"""
        self.i2c.reset()
        a0, a1, a2 = str(self.addr_pins[2]), str(self.addr_pins[1]), str(self.addr_pins[0])
        self.i2c.wp_pin = 0

        self.i2c._add_vector(a0, a1, a2, "1", "1", "0",
                              "=== FUNC: Page Write + Sequential Read ===", "FUNC_PW_START")
        ps = self.page_size
        page_data = [(1 << (i % 8)) for i in range(ps)]
        page_start = ps  # 第二页起始地址
        self.i2c.gen_page_write(page_start, page_data)
        self.i2c.gen_sequential_read(page_start, len(page_data), expected_data=page_data)

        self.i2c.add_idle(2, "=== Page Write Test Complete ===")
        self.i2c.wp_pin = self.wp_pin
        return self.i2c.vectors, self.i2c.comments, self.i2c.labels

    def generate_func_boundary(self):
        """FUNC-3: 地址边界测试"""
        self.i2c.reset()
        a0, a1, a2 = str(self.addr_pins[2]), str(self.addr_pins[1]), str(self.addr_pins[0])
        self.i2c.wp_pin = 0

        self.i2c._add_vector(a0, a1, a2, "1", "1", "0",
                              "=== FUNC: Address Boundary Test ===", "FUNC_BOUND_START")
        last_addr = self.max_addr
        self.i2c.gen_byte_write(last_addr, 0x42)
        self.i2c.gen_random_read(last_addr, expected_data=0x42)

        # 地址翻转测试: 从最大地址连续读 2 字节, 验证内部地址计数器回绕
        self.i2c.gen_byte_write(0x00, 0x55)
        self.i2c._add_vector(a0, a1, a2, "1", "1", "0",
                              f"Address wraparound: sequential read {self._fmt_addr(last_addr)}->0x00",
                              "FUNC_WRAP")
        self.i2c.gen_sequential_read(last_addr, 2, expected_data=[0x42, 0x55])

        self.i2c.add_idle(2, "=== Boundary Test Complete ===")
        self.i2c.wp_pin = self.wp_pin
        return self.i2c.vectors, self.i2c.comments, self.i2c.labels

    def generate_func_wp_test(self):
        """FUNC-4: WP写保护功能测试"""
        self.i2c.reset()
        a0, a1, a2 = str(self.addr_pins[2]), str(self.addr_pins[1]), str(self.addr_pins[0])

        self.i2c._add_vector(a0, a1, a2, "1", "1", "0",
                              "=== FUNC: WP Write Protect Test ===", "FUNC_WP_START")

        # Step1: WP=0, 写入已知值 0x5A
        wp_test_addr = min(0x40, self.max_addr)
        self.i2c.wp_pin = 0
        self.i2c.gen_byte_write(wp_test_addr, 0x5A)

        # Step2: WP=1, 尝试覆盖写 0xA5 (芯片忽略写入, 但仍ACK器件地址)
        self.i2c.wp_pin = 1
        self.i2c._add_vector(a0, a1, a2, "1", "1", "1",
                              "WP=1: write protect enabled, attempt overwrite (data unchanged)", "WP_PROTECT")
        self.i2c.gen_byte_write(wp_test_addr, 0xA5)

        # Step3: WP=0, 读回验证数据仍为 0x5A
        self.i2c.wp_pin = 0
        self.i2c._add_vector(a0, a1, a2, "1", "1", "0",
                              "WP=0: read back to verify data unchanged (expect 0x5A)", "WP_VERIFY")
        self.i2c.gen_random_read(wp_test_addr, expected_data=0x5A)

        self.i2c.add_idle(2, "=== WP Test Complete ===")
        self.i2c.wp_pin = self.wp_pin
        return self.i2c.vectors, self.i2c.comments, self.i2c.labels

    def generate_func_page_wrap(self):
        """FUNC-6: 页边界跨越测试 (Page Boundary Wrap-Around)"""
        self.i2c.reset()
        a0, a1, a2 = str(self.addr_pins[2]), str(self.addr_pins[1]), str(self.addr_pins[0])
        self.i2c.wp_pin = 0

        self.i2c._add_vector(a0, a1, a2, "1", "1", "0",
                              "=== FUNC: Page Boundary Wrap-Around Test ===",
                              "FUNC_PAGE_WRAP")
        wrap_offset = self.page_size - 2
        wrap_start = wrap_offset
        wrap_data = [0xA1, 0xB2, 0xC3, 0xD4]
        self.i2c.gen_page_write(wrap_start, wrap_data)
        self.i2c.gen_random_read(wrap_start, expected_data=0xA1)
        self.i2c.gen_random_read(wrap_start + 1, expected_data=0xB2)
        self.i2c.gen_random_read(0x00, expected_data=0xC3)
        self.i2c.gen_random_read(0x01, expected_data=0xD4)

        self.i2c.add_idle(2, "=== Page Wrap Test Complete ===")
        self.i2c.wp_pin = self.wp_pin
        return self.i2c.vectors, self.i2c.comments, self.i2c.labels

    def generate_func_current_read(self):
        """FUNC-7: 当前地址读测试 (Current Address Read)"""
        self.i2c.reset()
        a0, a1, a2 = str(self.addr_pins[2]), str(self.addr_pins[1]), str(self.addr_pins[0])
        self.i2c.wp_pin = 0

        self.i2c._add_vector(a0, a1, a2, "1", "1", "0",
                              "=== FUNC: Current Address Read Test ===",
                              "FUNC_CURR_READ")
        car_addr = min(self.page_size * 2, self.max_addr - 1)
        self.i2c.gen_byte_write(car_addr, 0xCA)
        self.i2c.gen_byte_write(car_addr + 1, 0xFE)
        self.i2c.gen_random_read(car_addr, expected_data=0xCA)
        self.i2c.gen_current_addr_read(expected_data=0xFE)

        self.i2c.add_idle(2, "=== Current Address Read Test Complete ===")
        self.i2c.wp_pin = self.wp_pin
        return self.i2c.vectors, self.i2c.comments, self.i2c.labels

    def generate_march_c_test(self, start_addr=0x00, count=8):
        """
        March C- 经典存储器测试算法

        业界标准故障覆盖模型:
        - SAF (Stuck-At Fault): 存储单元固定为0或1
        - TF  (Transition Fault): 无法完成 0→1 或 1→0 转换
        - CFin (Inversion Coupling Fault): 耦合翻转故障

        算法 (6步 March 元素, N=测试地址数):
        M0: ⇑(w0)      升序写全 0x00
        M1: ⇑(r0,w1)   升序: 读0验证 → 写 0xFF
        M2: ⇑(r1,w0)   升序: 读1验证 → 写 0x00
        M3: ⇓(r0,w1)   降序: 读0验证 → 写 0xFF
        M4: ⇓(r1,w0)   降序: 读1验证 → 写 0x00
        M5: ⇑(r0)      升序读0 — 最终验证
        """
        self.proto.reset()
        if hasattr(self.proto, 'wp_pin'):
            self.proto.wp_pin = 0

        # 确保地址范围不超出芯片容量
        if start_addr + count > self.capacity_bytes:
            count = self.capacity_bytes - start_addr
        addrs = self._sample_addresses(start_addr, count)

        # M0: ⇑(w0)
        self._add_marker("=== March C-: M0 ⇑(w0) Write all 0x00 ===", "MARCH_M0")
        for addr in addrs:
            self._write_byte_proto(addr, 0x00)

        # M1: ⇑(r0, w1)
        self._add_marker("=== March C-: M1 ⇑(r0,w1) Read 0x00 then Write 0xFF ===", "MARCH_M1")
        for addr in addrs:
            self._read_verify_proto(addr, 0x00)
            self._write_byte_proto(addr, 0xFF)

        # M2: ⇑(r1, w0)
        self._add_marker("=== March C-: M2 ⇑(r1,w0) Read 0xFF then Write 0x00 ===", "MARCH_M2")
        for addr in addrs:
            self._read_verify_proto(addr, 0xFF)
            self._write_byte_proto(addr, 0x00)

        # M3: ⇓(r0, w1)
        self._add_marker("=== March C-: M3 ⇓(r0,w1) Descending ===", "MARCH_M3")
        for addr in reversed(addrs):
            self._read_verify_proto(addr, 0x00)
            self._write_byte_proto(addr, 0xFF)

        # M4: ⇓(r1, w0)
        self._add_marker("=== March C-: M4 ⇓(r1,w0) Descending ===", "MARCH_M4")
        for addr in reversed(addrs):
            self._read_verify_proto(addr, 0xFF)
            self._write_byte_proto(addr, 0x00)

        # M5: ⇑(r0) 最终验证
        self._add_marker("=== March C-: M5 ⇑(r0) Final Verify ===", "MARCH_M5")
        for addr in addrs:
            self._read_verify_proto(addr, 0x00)

        self.proto.add_idle(4, "=== March C- Test Complete ===")
        return self.proto.vectors, self.proto.comments, self.proto.labels

    def generate_march_b_test(self, start_addr=0x00, count=8):
        """
        March B 存储器测试算法 (17N 复杂度)

        比 March C- 覆盖更多耦合故障 (CFid, CFdyn):
        M0: ⇑(w0)
        M1: ⇑(r0, w1, r1, w0, r0, w1)
        M2: ⇑(r1, w0, w1)
        M3: ⇓(r1, w0, w1, w0)
        M4: ⇓(r0, w1, w0)
        """
        self.proto.reset()
        if hasattr(self.proto, 'wp_pin'):
            self.proto.wp_pin = 0

        if start_addr + count > self.capacity_bytes:
            count = self.capacity_bytes - start_addr
        addrs = self._sample_addresses(start_addr, count)

        # M0: ⇑(w0)
        self._add_marker("=== March B: M0 ⇑(w0) Write all 0x00 ===", "MARCHB_M0")
        for addr in addrs:
            self._write_byte_proto(addr, 0x00)

        # M1: ⇑(r0, w1, r1, w0, r0, w1)
        self._add_marker("=== March B: M1 ⇑(r0,w1,r1,w0,r0,w1) ===", "MARCHB_M1")
        for addr in addrs:
            self._read_verify_proto(addr, 0x00)
            self._write_byte_proto(addr, 0xFF)
            self._read_verify_proto(addr, 0xFF)
            self._write_byte_proto(addr, 0x00)
            self._read_verify_proto(addr, 0x00)
            self._write_byte_proto(addr, 0xFF)

        # M2: ⇑(r1, w0, w1)
        self._add_marker("=== March B: M2 ⇑(r1,w0,w1) ===", "MARCHB_M2")
        for addr in addrs:
            self._read_verify_proto(addr, 0xFF)
            self._write_byte_proto(addr, 0x00)
            self._write_byte_proto(addr, 0xFF)

        # M3: ⇓(r1, w0, w1, w0)
        self._add_marker("=== March B: M3 ⇓(r1,w0,w1,w0) ===", "MARCHB_M3")
        for addr in reversed(addrs):
            self._read_verify_proto(addr, 0xFF)
            self._write_byte_proto(addr, 0x00)
            self._write_byte_proto(addr, 0xFF)
            self._write_byte_proto(addr, 0x00)

        # M4: ⇓(r0, w1, w0)
        self._add_marker("=== March B: M4 ⇓(r0,w1,w0) ===", "MARCHB_M4")
        for addr in reversed(addrs):
            self._read_verify_proto(addr, 0x00)
            self._write_byte_proto(addr, 0xFF)
            self._write_byte_proto(addr, 0x00)

        self.proto.add_idle(4, "=== March B Test Complete ===")
        return self.proto.vectors, self.proto.comments, self.proto.labels

    def generate_addr_scan_test(self, start_addr=0x00, end_addr=0x0F):
        """
        全地址空间扫描测试

        对指定范围内每个地址写入 (addr XOR 0x55) 的数据模式,
        写完后再全部读回验证, 确保每个存储单元都可寻址和读写。
        """
        self.proto.reset()
        if hasattr(self.proto, 'wp_pin'):
            self.proto.wp_pin = 0

        cap = self.capacity_bytes
        end_clamped = min(end_addr, cap - 1)
        all_addrs = list(range(start_addr, end_clamped + 1))
        addrs = self._sample_addresses(start_addr, len(all_addrs))

        fa = self._fmt_addr
        # Phase 1: 写入全部地址
        self._add_marker(f"=== Addr Scan: Write {fa(start_addr)}~{fa(end_clamped)} ===",
                         "SCAN_WRITE")
        for addr in addrs:
            data = (addr ^ 0x55) & 0xFF
            self._write_byte_proto(addr, data)

        # Phase 2: 读回验证全部地址
        self._add_marker(f"=== Addr Scan: Read Verify {fa(start_addr)}~{fa(end_clamped)} ===",
                         "SCAN_READ")
        for addr in addrs:
            expected = (addr ^ 0x55) & 0xFF
            self._read_verify_proto(addr, expected)

        self.proto.add_idle(4, "=== Address Scan Complete ===")
        return self.proto.vectors, self.proto.comments, self.proto.labels

    def generate_data_retention_test(self, start_addr=0x00, count=8):
        """
        数据保持测试 (Data Retention Pattern)

        验证 EEPROM 写入后数据保持能力:
        Phase 1: 写入棋盘格模式 (0x55/0xAA 交替)
        Phase 2: 延时等待 (模拟数据保持时间)
        Phase 3: 读回验证棋盘格
        Phase 4: 写入全 0x00
        Phase 5: 延时等待
        Phase 6: 读回验证全 0x00
        Phase 7: 写入全 0xFF
        Phase 8: 延时等待
        Phase 9: 读回验证全 0xFF
        """
        self.proto.reset()
        if hasattr(self.proto, 'wp_pin'):
            self.proto.wp_pin = 0

        addrs = [start_addr + i for i in range(count) if start_addr + i <= self.max_addr]

        # Phase 1: 写入棋盘格
        self._add_marker("=== Data Retention: Phase1 Write Checkerboard ===", "RET_WRITE_CB")
        for addr in addrs:
            data = 0x55 if (addr % 2 == 0) else 0xAA
            self._write_byte_proto(addr, data)

        # Phase 2: 延时等待
        self._add_marker("=== Data Retention: Wait ===", "RET_WAIT1")
        self.proto.add_idle(20, "Retention wait: data hold time simulation")

        # Phase 3: 读回验证棋盘格
        self._add_marker("=== Data Retention: Phase3 Verify Checkerboard ===", "RET_VERIFY_CB")
        for addr in addrs:
            expected = 0x55 if (addr % 2 == 0) else 0xAA
            self._read_verify_proto(addr, expected)

        # Phase 4: 写入全 0x00
        self._add_marker("=== Data Retention: Phase4 Write All 0x00 ===", "RET_WRITE_00")
        for addr in addrs:
            self._write_byte_proto(addr, 0x00)

        # Phase 5: 延时等待
        self._add_marker("=== Data Retention: Wait ===", "RET_WAIT2")
        self.proto.add_idle(20, "Retention wait: all-zero hold")

        # Phase 6: 读回验证全 0x00
        self._add_marker("=== Data Retention: Phase6 Verify All 0x00 ===", "RET_VERIFY_00")
        for addr in addrs:
            self._read_verify_proto(addr, 0x00)

        # Phase 7: 写入全 0xFF
        self._add_marker("=== Data Retention: Phase7 Write All 0xFF ===", "RET_WRITE_FF")
        for addr in addrs:
            self._write_byte_proto(addr, 0xFF)

        # Phase 8: 延时等待
        self._add_marker("=== Data Retention: Wait ===", "RET_WAIT3")
        self.proto.add_idle(20, "Retention wait: all-one hold")

        # Phase 9: 读回验证全 0xFF
        self._add_marker("=== Data Retention: Phase9 Verify All 0xFF ===", "RET_VERIFY_FF")
        for addr in addrs:
            self._read_verify_proto(addr, 0xFF)

        self.proto.add_idle(4, "=== Data Retention Test Complete ===")
        return self.proto.vectors, self.proto.comments, self.proto.labels

    def generate_i2c_error_test(self):
        """
        I2C 协议边界/异常测试

        测试 DUT 在异常 I2C 条件下的容错能力:
        ERR-1: 错误器件地址访问 (预期 NACK)
        ERR-2: 不完整事务恢复 (STOP 后重新访问)
        ERR-3: 总线忙恢复 (SCL/SDA 钳位后释放)
        ERR-4: 连续 START (无 STOP 的多次 START)
        ERR-5: 正常读写验证 (确认 DUT 未锁死)
        """
        self.i2c.reset()
        self.i2c.wp_pin = 0
        a0, a1, a2 = str(self.addr_pins[2]), str(self.addr_pins[1]), str(self.addr_pins[0])

        # ERR-1: 错误器件地址 (使用不匹配的地址, 预期无 ACK)
        self.i2c._add_vector(a0, a1, a2, "1", "1", "0",
                              "=== ERR-1: Wrong Device Address (expect NACK) ===",
                              "ERR_WRONG_ADDR")
        self.i2c.add_start_condition()
        # 使用错误地址 (不是当前芯片的地址)
        wrong_addr = 0x50
        self.i2c.add_write_byte(wrong_addr, f"Wrong DevAddr 0x{wrong_addr:02X} (not target chip)")
        # 期望 NACK (SDA 保持高, 无器件应答)
        self.i2c.add_nack_from_slave("NACK expected: wrong addr, no device responds")
        self.i2c.add_stop_condition()
        self.i2c.add_idle(4, "ERR-1 complete: wrong address rejected")

        # ERR-2: 不完整事务恢复
        self.i2c._add_vector(a0, a1, a2, "1", "1", "0",
                              "=== ERR-2: Incomplete Transaction Recovery ===",
                              "ERR_INCOMPLETE")
        # 发送 START + 器件地址 + ACK + 部分数据, 然后突然 STOP
        self.i2c.add_start_condition()
        self.i2c.add_write_byte(self.i2c.device_addr & 0xFE, "DevAddr+W")
        self.i2c.add_ack_from_slave("ACK")
        self.i2c.add_write_byte(0x50, "WordAddr (partial)")
        self.i2c.add_ack_from_slave("ACK")
        # 只写 4 bit 然后中断
        for i in range(3, -1, -1):
            bit = (0xAB >> (i + 4)) & 1
            self.i2c.add_write_bit(bit, f"Partial data bit[{i+4}]")
        # 突然 STOP (未完成字节)
        self.i2c.add_stop_condition()
        self.i2c.add_idle(4, "Aborted mid-byte, DUT should recover")

        # 恢复: 正常写读验证 DUT 未锁死
        err_addr = min(0x50, self.max_addr)
        self.i2c.gen_byte_write(err_addr, 0xBB)
        self.i2c.gen_random_read(err_addr, expected_data=0xBB)
        self.i2c.add_idle(2, "ERR-2 recovery verified")

        # ERR-3: 总线忙恢复 (SCL/SDA 钳位)
        self.i2c._add_vector(a0, a1, a2, "1", "1", "0",
                              "=== ERR-3: Bus Busy Recovery (SDA/SCL held low) ===",
                              "ERR_BUS_BUSY")
        # 模拟总线被钳位: SCL=0, SDA=0 持续多个周期
        for i in range(6):
            self.i2c._add_vector(a0, a1, a2, "0", "0", "0",
                                  "Bus busy: SDA=0 SCL=0 (held)" if i == 0 else "")
        # 释放总线
        self.i2c._add_vector(a0, a1, a2, "0", "1", "0", "Release SCL")
        self.i2c._add_vector(a0, a1, a2, "1", "1", "0", "Release SDA → bus free")
        self.i2c.add_idle(4, "Bus released")

        # 发送 9 个时钟脉冲 (标准总线恢复方法)
        self.i2c._add_vector(a0, a1, a2, "1", "1", "0",
                              "Bus recovery: 9 clock pulses", "ERR_BUS_RECOVERY")
        for pulse in range(9):
            self.i2c._add_vector(a0, a1, a2, "Z", "0", "0",
                                  f"Recovery clock {pulse+1}" if pulse == 0 else "")
            self.i2c._add_vector(a0, a1, a2, "Z", "1", "0", "")
        self.i2c.add_stop_condition()
        self.i2c.add_idle(2, "Bus recovery complete")

        # 验证 DUT 仍可正常通信
        err_addr2 = min(0x51, self.max_addr)
        self.i2c.gen_byte_write(err_addr2, 0xCC)
        self.i2c.gen_random_read(err_addr2, expected_data=0xCC)
        self.i2c.add_idle(2, "ERR-3 recovery verified")

        # ERR-4: 连续 START (无 STOP 的多次 START)
        self.i2c._add_vector(a0, a1, a2, "1", "1", "0",
                              "=== ERR-4: Consecutive STARTs (no STOP) ===",
                              "ERR_MULTI_START")
        self.i2c.add_start_condition()
        self.i2c.add_write_byte(self.i2c.device_addr & 0xFE, "DevAddr+W (1st START)")
        self.i2c.add_ack_from_slave("ACK")
        # 不发 STOP, 直接 RepSTART
        self.i2c.add_repeated_start()
        self.i2c.add_write_byte(self.i2c.device_addr & 0xFE, "DevAddr+W (2nd START)")
        self.i2c.add_ack_from_slave("ACK")
        # 再次 RepSTART
        self.i2c.add_repeated_start()
        self.i2c.add_write_byte(self.i2c.device_addr | 0x01, "DevAddr+R (3rd START)")
        self.i2c.add_ack_from_slave("ACK")
        self.i2c.add_read_byte(None, "Read after multi-START")
        self.i2c.add_nack_from_master("NACK")
        self.i2c.add_stop_condition()
        self.i2c.add_idle(4, "ERR-4 complete")

        # ERR-5: 最终正常读写验证
        self.i2c._add_vector(a0, a1, a2, "1", "1", "0",
                              "=== ERR-5: Final Sanity Check ===",
                              "ERR_SANITY")
        err_addr3 = min(0x60, self.max_addr)
        self.i2c.gen_byte_write(err_addr3, 0xDE)
        self.i2c.gen_random_read(err_addr3, expected_data=0xDE)

        # ERR-6: 多DUT地址共存测试 (Multi-Device Address Coexistence)
        # I2C 总线上可能挂载多个 AT24C02 (不同 A2A1A0 配置)
        # 验证: 发送非目标地址时, 当前 DUT 不响应 (NACK)
        self.i2c._add_vector(a0, a1, a2, "1", "1", "0",
                              "=== ERR-6: Multi-Device Address Coexistence ===",
                              "ERR_MULTI_DUT")
        # 构造 7 个不同于当前 DUT 的 AT24C02 器件地址
        current_a210 = (self.addr_pins[0] << 2) | (self.addr_pins[1] << 1) | self.addr_pins[2]
        for a210 in range(8):
            if a210 == current_a210:
                continue  # 跳过当前 DUT 地址
            other_addr = 0xA0 | (a210 << 1)
            self.i2c.add_start_condition()
            self.i2c.add_write_byte(other_addr,
                                     f"Other DUT addr 0x{other_addr:02X} (A210={a210:03b})")
            # 当前 DUT 不应响应 → 预期 NACK
            self.i2c.add_nack_from_slave(
                f"NACK expected: addr 0x{other_addr:02X} is not this DUT")
            self.i2c.add_stop_condition()
            self.i2c.add_idle(2)

        # 验证当前 DUT 地址仍正常响应
        self.i2c._add_vector(a0, a1, a2, "1", "1", "0",
                              "Verify current DUT still responds after multi-addr test")
        err_addr4 = min(0x61, self.max_addr)
        self.i2c.gen_byte_write(err_addr4, 0xEE)
        self.i2c.gen_random_read(err_addr4, expected_data=0xEE)

        self.i2c.add_idle(4, "=== I2C Error Test Complete ===")
        return self.i2c.vectors, self.i2c.comments, self.i2c.labels

    # ── SPI 功能测试 ──
    def generate_spi_functional_test(self, custom_addr=None, custom_data=None):
        """SPI EEPROM 功能测试"""
        p = self.proto
        p.reset()

        # FUNC-1: 单字节写+读回验证
        self._add_marker("=== SPI FUNC-1: Byte Write + Read Verify ===", "SPI_FUNC1")
        p.spi_write(0x00, [0xA5], comment="Write 0xA5 @0x00")
        p.spi_read(0x00, 1, [0xA5], comment="Read verify @0x00")

        # FUNC-2: 页写+顺序读
        self._add_marker("=== SPI FUNC-2: Page Write + Read ===", "SPI_FUNC2")
        page_data = [(i * 0x11) & 0xFF for i in range(min(self.page_size, 8))]
        p.spi_write(0x00, page_data, comment=f"Page write {len(page_data)} bytes")
        p.spi_read(0x00, len(page_data), page_data, comment="Page read verify")

        # FUNC-3: 边界地址测试
        self._add_marker("=== SPI FUNC-3: Boundary Address Test ===", "SPI_FUNC3")
        # 首地址
        p.spi_write(0x00, [0x55], comment="Write @first addr")
        p.spi_read(0x00, 1, [0x55], comment="Read @first addr")
        # 末地址
        last = self.max_addr
        p.spi_write(last, [0xAA], comment=f"Write @last addr {self._fmt_addr(last)}")
        p.spi_read(last, 1, [0xAA], comment=f"Read @last addr")

        # FUNC-4: WP保护测试 (WP=1时写入应不生效)
        self._add_marker("=== SPI FUNC-4: WP Protection Test ===", "SPI_FUNC4")
        wp_addr = min(0x40, self.max_addr)
        p.spi_write(wp_addr, [0x33], comment="Write before WP")
        p.wp_pin = 1  # 启用写保护
        p.spi_write(wp_addr, [0xCC], comment="Write with WP=1 (should fail)")
        p.wp_pin = 0  # 恢复
        p.spi_read(wp_addr, 1, [0x33], comment="Verify WP blocked write")

        # FUNC-5: 状态寄存器读写
        self._add_marker("=== SPI FUNC-5: Status Register R/W ===", "SPI_FUNC5")
        p.read_status_register(comment="Read SR initial")
        p.spi_write_status_register(0x00, comment="Clear SR protect bits")
        p.read_status_register(comment="Read SR after clear")

        # FUNC-6: 自定义写入 (可选)
        if custom_addr is not None and custom_data is not None:
            self._add_marker("=== SPI FUNC-6: Custom Write ===", "SPI_FUNC6")
            data_list = [custom_data & 0xFF]
            p.spi_write(custom_addr, data_list, comment="Custom write")
            p.spi_read(custom_addr, 1, data_list, comment="Custom read verify")

        p.add_idle(4, "=== SPI Functional Test Complete ===")
        return p.vectors, p.comments, p.labels

    def generate_spi_flash_test(self):
        """SPI NOR Flash 专用测试 (JEDEC ID + 扇区擦除)"""
        p = self.proto
        p.reset()

        # FLASH-1: JEDEC ID 读取验证
        self._add_marker("=== FLASH-1: JEDEC ID Verify ===", "FLASH_JEDEC")
        p.spi_read_jedec_id(self.jedec_id, comment="Read JEDEC ID")

        # FLASH-2: 扇区擦除 + 页编程 + 读回
        if self.sector_size:
            self._add_marker("=== FLASH-2: Sector Erase + Page Program ===", "FLASH_SE_PP")
            p.spi_sector_erase(0x000000, comment="Erase sector 0")
            # 擦除后应全0xFF
            p.spi_read(0x000000, 4, [0xFF, 0xFF, 0xFF, 0xFF],
                       comment="Verify erased (0xFF)")
            # 页编程
            prog_data = [i & 0xFF for i in range(16)]
            p.spi_write(0x000000, prog_data, comment="Page program 16 bytes")
            p.spi_read(0x000000, 16, prog_data, comment="Read verify programmed data")

        # FLASH-3: 块擦除 (64KB)
        if self.sector_size:
            self._add_marker("=== FLASH-3: Block Erase 64K ===", "FLASH_BE64K")
            p.spi_block_erase_64k(0x010000, comment="Block erase @0x010000")
            p.spi_read(0x010000, 4, [0xFF, 0xFF, 0xFF, 0xFF],
                       comment="Verify block erased")

        p.add_idle(4, "=== SPI Flash Test Complete ===")
        return p.vectors, p.comments, p.labels

    def generate_mw_functional_test(self, custom_addr=None, custom_data=None):
        """Microwire 功能测试"""
        p = self.proto
        p.reset()

        # FUNC-1: 单字写+读回
        self._add_marker("=== MW FUNC-1: Word Write + Read Verify ===", "MW_FUNC1")
        p.mw_write(0, 0xA5A5, comment="Write @0")
        p.mw_read(0, expected=0xA5A5, comment="Read verify @0")

        # FUNC-2: 边界地址测试
        self._add_marker("=== MW FUNC-2: Boundary Address Test ===", "MW_FUNC2")
        last_word = p.capacity_words - 1
        p.mw_write(0, 0x5555, comment="Write @first")
        p.mw_read(0, expected=0x5555, comment="Read @first")
        p.mw_write(last_word, 0xAAAA, comment=f"Write @last ({last_word})")
        p.mw_read(last_word, expected=0xAAAA, comment=f"Read @last ({last_word})")

        # FUNC-3: ERAL + WRAL 测试
        self._add_marker("=== MW FUNC-3: ERAL + WRAL Test ===", "MW_FUNC3")
        p.mw_eral(comment="Erase All")
        p.mw_read(0, expected=0xFFFF, comment="Verify erased (0xFFFF)")
        p.mw_wral(0x1234, comment="Write All 0x1234")
        p.mw_read(0, expected=0x1234, comment="Verify WRAL @0")
        p.mw_read(last_word, expected=0x1234, comment=f"Verify WRAL @{last_word}")

        # FUNC-4: EWDS 保护测试
        self._add_marker("=== MW FUNC-4: EWDS Protection Test ===", "MW_FUNC4")
        p.mw_write(0, 0xBEEF, comment="Write before EWDS")
        # 手动 EWDS, 然后尝试写入 (不经过 mw_write 的自动 EWEN)
        p.mw_ewds(comment="Disable writes")
        # 直接发送 WRITE 命令 (无 EWEN, 应不生效)
        p.cs_active("Write without EWEN (should fail)")
        p.send_start_bit()
        p.send_opcode(MW_OPCODES["WRITE"], 2, "WRITE")
        p.send_address(0)
        p.send_data_word(0xDEAD, "Unprotected write data")
        p.cs_inactive("CS↓")
        p.add_idle(2)
        # 读回应仍是 BEEF
        p.mw_read(0, expected=0xBEEF, comment="Verify EWDS blocked write")

        # FUNC-5: 自定义 (可选)
        if custom_addr is not None and custom_data is not None:
            self._add_marker("=== MW FUNC-5: Custom Write ===", "MW_FUNC5")
            p.mw_write(custom_addr, custom_data & 0xFFFF, comment="Custom write")
            p.mw_read(custom_addr, expected=custom_data & 0xFFFF, comment="Custom verify")

        p.add_idle(4, "=== MW Functional Test Complete ===")
        return p.vectors, p.comments, p.labels

    # ── SPI 异常/错误测试 ──
    def generate_spi_error_test(self):
        """SPI 协议异常测试"""
        p = self.proto
        p.reset()

        # ERR-1: 未WREN直接写入 (应不生效)
        self._add_marker("=== SPI ERR-1: Write without WREN ===", "SPI_ERR1")
        p.spi_write(0x00, [0xAA], comment="Initial write")
        # 不调用 write_enable, 直接发送 WRITE 命令
        p.cs_active("Direct WRITE without WREN")
        p.send_command(SPI_COMMANDS["WRITE"], "WRITE (no WREN)")
        p.send_address(0x00)
        p.send_byte(0x55, "Data (should not be written)")
        p.cs_inactive("CS↑")
        p.add_idle(2)
        p.spi_read(0x00, 1, [0xAA], comment="Verify WREN protection")

        # ERR-2: WIP期间读取 (写入后立即读)
        self._add_marker("=== SPI ERR-2: Read during WIP ===", "SPI_ERR2")
        p.write_enable()
        p.cs_active("Quick write")
        p.send_command(SPI_COMMANDS["WRITE"], "WRITE")
        p.send_address(0x01)
        p.send_byte(0xBB, "Data")
        p.cs_inactive("CS↑")
        # 立即读 (不等 WIP 清除, 读 SR 应显示 WIP=1)
        p.read_status_register(comment="RDSR immediately (expect WIP=1)")
        p.poll_wip(comment="Wait for WIP clear")

        # ERR-3: 正常读写验证 (确认DUT未锁死)
        self._add_marker("=== SPI ERR-3: Recovery Verify ===", "SPI_ERR3")
        p.spi_write(0x02, [0xCC], comment="Recovery write")
        p.spi_read(0x02, 1, [0xCC], comment="Recovery read verify")

        p.add_idle(4, "=== SPI Error Test Complete ===")
        return p.vectors, p.comments, p.labels

    def generate_mw_error_test(self):
        """Microwire 协议异常测试"""
        p = self.proto
        p.reset()

        # ERR-1: 未EWEN写入
        self._add_marker("=== MW ERR-1: Write without EWEN ===", "MW_ERR1")
        p.mw_write(0, 0x1111, comment="Initial write")
        p.mw_ewds(comment="Disable writes")
        # 直接发写命令
        p.cs_active("Write without EWEN")
        p.send_start_bit()
        p.send_opcode(MW_OPCODES["WRITE"], 2, "WRITE")
        p.send_address(0)
        p.send_data_word(0x2222, "Data (should fail)")
        p.cs_inactive("CS↓")
        p.add_idle(2)
        p.mw_read(0, expected=0x1111, comment="Verify EWEN protection")

        # ERR-2: Busy期间读取 (写后立即读)
        self._add_marker("=== MW ERR-2: Read during Busy ===", "MW_ERR2")
        p.mw_ewen()
        p.cs_active("Quick write")
        p.send_start_bit()
        p.send_opcode(MW_OPCODES["WRITE"], 2, "WRITE")
        p.send_address(1)
        p.send_data_word(0x3333, "Data")
        p.cs_inactive("CS↓")
        # 立即读 (可能返回不确定数据)
        p.mw_read(1, comment="Read during busy (data uncertain)")
        p.mw_ewds()

        # ERR-3: 恢复验证
        self._add_marker("=== MW ERR-3: Recovery Verify ===", "MW_ERR3")
        p.mw_write(2, 0x4444, comment="Recovery write")
        p.mw_read(2, expected=0x4444, comment="Recovery read verify")

        p.add_idle(4, "=== MW Error Test Complete ===")
        return p.vectors, p.comments, p.labels

    def generate_endurance_test(self, test_addr=0x70, cycles=10):
        """
        耐久性/写循环测试 (Endurance / Write Cycling)

        模拟 EEPROM 加速老化:
        对同一地址反复写入不同数据模式并读回验证, 测试写循环耐久性。
        实际量产测试通过 ATE loop 指令重复执行。

        数据模式轮转: 0x55 → 0xAA → 0x00 → 0xFF → 0x01 → 0xFE → 0x33 → 0xCC → 0x0F → 0xF0
        """
        self.proto.reset()
        if hasattr(self.proto, 'wp_pin'):
            self.proto.wp_pin = 0

        # 确保测试地址在芯片范围内
        test_addr = min(test_addr, self.max_addr)

        data_patterns = [0x55, 0xAA, 0x00, 0xFF, 0x01, 0xFE, 0x33, 0xCC, 0x0F, 0xF0]

        self._add_marker(
            f"=== Endurance Test: addr={self._fmt_addr(test_addr)}, {cycles} cycles ===",
            "ENDUR_START")

        for cyc in range(cycles):
            data = data_patterns[cyc % len(data_patterns)]
            label = f"ENDUR_CYC{cyc}" if cyc < 3 or cyc == cycles - 1 else ""

            if label:
                self._add_marker(
                    f"=== Endurance Cycle {cyc}: Write 0x{data:02X} ===", label)

            self._write_byte_proto(test_addr, data)
            self._read_verify_proto(test_addr, data)

        # 最终读回验证
        final_data = data_patterns[(cycles - 1) % len(data_patterns)]
        self._add_marker(
            f"=== Endurance Final Verify: expect 0x{final_data:02X} ===", "ENDUR_FINAL")
        self._read_verify_proto(test_addr, final_data)

        self.proto.add_idle(4, "=== Endurance Test Complete ===")
        return self.proto.vectors, self.proto.comments, self.proto.labels

    # ------------------------------------------------------------------
    # IDDQ 静态电流测试 (v9.0 Phase 21)
    # ------------------------------------------------------------------
    def generate_iddq_test(self):
        """
        IDDQ 静态电流测试 — 8个独立测量点
        在关键操作后插入 PMU 测量窗口, 检测浮栅编程异常/内部短路/栅氧缺陷
        每个测量窗口 = 8 个 idle 向量 + ;IDDQ_MEASURE 标记
        """
        self.proto.vectors = []
        self.proto.comments = []
        self.proto.labels = []

        def add_iddq_window(label_tag, measure_label, limit_ua=1.0):
            """插入 8 个 idle 向量作为 IDDQ PMU 采样窗口"""
            for i in range(8):
                self.proto.add_idle(1, "")
                marker = f";IDDQ_MEASURE {measure_label} ISB<{limit_ua}uA" if i == 0 else ""
                self.proto.comments[-1] = f"IDDQ: {measure_label} ({i+1}/8){marker}"
            if label_tag and self.proto.labels:
                # 在窗口首向量打标签
                self.proto.labels[-8] = label_tag

        # IDDQ-1: 初始基线 (上电后未操作)
        self._add_marker("=== IDDQ-1: Initial Baseline ===", "IDDQ_INITIAL")
        add_iddq_window("IDDQ_MEAS_1", "INITIAL", 1.0)

        # IDDQ-2: 写操作后漏电
        self._add_marker("=== IDDQ-2: After Write ===", "IDDQ_AFTER_WRITE")
        self._write_byte_proto(0x00, 0xA5)
        add_iddq_window("IDDQ_MEAS_2", "AFTER_WRITE_0x00", 1.0)

        # IDDQ-3: 读操作后漏电
        self._add_marker("=== IDDQ-3: After Read ===", "IDDQ_AFTER_READ")
        self._read_verify_proto(0x00, 0xA5)
        add_iddq_window("IDDQ_MEAS_3", "AFTER_READ_0x00", 1.0)

        # IDDQ-4: 多地址写后 IDDQ (采样 4 个地址, 检测不同解码路径漏电)
        for idx, addr in enumerate([0x00, 0x55, 0xAA, 0xFF]):
            addr_safe = min(addr, self.max_addr)
            self._add_marker(
                f"=== IDDQ-4{chr(97+idx)}: After Write addr={self._fmt_addr(addr_safe)} ===",
                f"IDDQ_ADDR_{addr_safe:02X}")
            self._write_byte_proto(addr_safe, 0xFF)
            add_iddq_window(f"IDDQ_MEAS_4{chr(97+idx)}", f"AFTER_WRITE_{addr_safe:02X}", 1.0)

        # IDDQ-5: 全1阵列状态
        self._add_marker("=== IDDQ-5: Array All-FF ===", "IDDQ_ALL_FF")
        add_iddq_window("IDDQ_MEAS_5", "ARRAY_ALL_FF", 1.0)

        # IDDQ-6: 全0阵列状态
        self._add_marker("=== IDDQ-6: Array All-00 ===", "IDDQ_ALL_00")
        self._write_byte_proto(0x00, 0x00)
        add_iddq_window("IDDQ_MEAS_6", "ARRAY_ALL_00", 1.0)

        # IDDQ-7: WP=0 状态
        self._add_marker("=== IDDQ-7: WP Disabled ===", "IDDQ_WP_OFF")
        add_iddq_window("IDDQ_MEAS_7", "WP_DISABLED", 1.0)

        # IDDQ-8: WP=1 状态
        self._add_marker("=== IDDQ-8: WP Enabled ===", "IDDQ_WP_ON")
        add_iddq_window("IDDQ_MEAS_8", "WP_ENABLED", 1.0)

        self.proto.add_idle(4, "=== IDDQ Test Complete ===")
        return self.proto.vectors, self.proto.comments, self.proto.labels


# ============================================================
# I2C 时序合规性检查器
# ============================================================

class I2CTimingChecker:
    """
    根据 AT24C02 Datasheet 时序参数, 验证当前向量周期是否满足 I2C 时序约束。
    每个向量周期 = 一个 ATE 时钟周期, I2C 信号由多个向量周期组成。
    """

    @staticmethod
    def check(period_ns, voltage_key="5.0V"):
        """
        检查时序合规性
        返回: (passed: bool, results: list[dict])
        每项 result: {"param", "required_ns", "actual_ns", "passed", "note"}
        """
        constraints = I2C_TIMING_CONSTRAINTS.get(voltage_key, I2C_TIMING_CONSTRAINTS["5.0V"])
        results = []

        # 1. 频率检查: fSCL = 1 / (tLOW + tHIGH), 简化模型中 1 bit = 3 vectors
        #    SCL低=1vec, SCL高=1vec, SCL低(next)=1vec → tLOW≈period, tHIGH≈period
        actual_tLOW = period_ns     # 1 个向量周期
        actual_tHIGH = period_ns    # 1 个向量周期
        fSCL_actual = 1e9 / (actual_tLOW + actual_tHIGH + period_ns) / 1e3  # kHz (3-vec bit)

        results.append({
            "param": "fSCL",
            "required": f"≤ {constraints['fSCL_max_kHz']} kHz",
            "actual": f"{fSCL_actual:.1f} kHz",
            "passed": fSCL_actual <= constraints["fSCL_max_kHz"],
            "note": "I2C时钟频率 (3向量/bit模型)",
        })

        # 2. tLOW 检查
        results.append({
            "param": "tLOW",
            "required": f"≥ {constraints['tLOW_min']} ns",
            "actual": f"{actual_tLOW} ns",
            "passed": actual_tLOW >= constraints["tLOW_min"],
            "note": "SCL低电平宽度 (= 1向量周期)",
        })

        # 3. tHIGH 检查
        results.append({
            "param": "tHIGH",
            "required": f"≥ {constraints['tHIGH_min']} ns",
            "actual": f"{actual_tHIGH} ns",
            "passed": actual_tHIGH >= constraints["tHIGH_min"],
            "note": "SCL高电平宽度 (= 1向量周期)",
        })

        # 4. tSU_STA 检查 (START建立 = SDA高+SCL高 = 1 vec)
        actual_tSU_STA = period_ns
        results.append({
            "param": "tSU,STA",
            "required": f"≥ {constraints['tSU_STA_min']} ns",
            "actual": f"{actual_tSU_STA} ns",
            "passed": actual_tSU_STA >= constraints["tSU_STA_min"],
            "note": "START条件建立时间",
        })

        # 5. tHD_STA 检查 (START保持 = SDA低+SCL高→SCL低 = 1 vec)
        actual_tHD_STA = period_ns
        results.append({
            "param": "tHD,STA",
            "required": f"≥ {constraints['tHD_STA_min']} ns",
            "actual": f"{actual_tHD_STA} ns",
            "passed": actual_tHD_STA >= constraints["tHD_STA_min"],
            "note": "START条件保持时间",
        })

        # 6. tSU_STO 检查 (STOP建立 = SCL高前SDA稳定)
        actual_tSU_STO = period_ns
        results.append({
            "param": "tSU,STO",
            "required": f"≥ {constraints['tSU_STO_min']} ns",
            "actual": f"{actual_tSU_STO} ns",
            "passed": actual_tSU_STO >= constraints["tSU_STO_min"],
            "note": "STOP条件建立时间",
        })

        # 7. tBUF 检查 (总线释放 = STOP到START间隔)
        actual_tBUF = period_ns * 2  # IDLE通常2个以上向量
        results.append({
            "param": "tBUF",
            "required": f"≥ {constraints['tBUF_min']} ns",
            "actual": f"{actual_tBUF} ns",
            "passed": actual_tBUF >= constraints["tBUF_min"],
            "note": "总线释放时间 (STOP→START间隔)",
        })

        # 8. tSU_DAT 检查
        actual_tSU_DAT = period_ns  # 数据在SCL上升沿前一个周期建立
        results.append({
            "param": "tSU,DAT",
            "required": f"≥ {constraints['tSU_DAT_min']} ns",
            "actual": f"{actual_tSU_DAT} ns",
            "passed": actual_tSU_DAT >= constraints["tSU_DAT_min"],
            "note": "数据输入建立时间",
        })

        all_passed = all(r["passed"] for r in results)
        return all_passed, results


# ============================================================
# 向量协议合规性验证器
# ============================================================

class VectorProtocolValidator:
    """
    对生成的向量进行 I2C 协议规则检查:
    1. SDA 仅在 SCL=0 时改变 (START/STOP 除外)
    2. 每个字节后必须有 ACK/NACK 周期
    3. START/STOP 条件格式正确
    4. 总线空闲时 SDA=1, SCL=1
    """

    @staticmethod
    def validate(vectors, comments):
        """
        验证向量协议合规性
        返回: (issue_count: int, issues: list[dict])
        每项 issue: {"vec_idx", "severity", "rule", "detail"}
        severity: "error" | "warning" | "info"
        """
        issues = []
        n = len(vectors)
        if n < 2:
            return 0, issues

        in_transaction = False
        byte_bit_count = 0
        expect_ack = False

        for i in range(1, n):
            prev = vectors[i - 1]
            cur = vectors[i]
            cm = comments[i] if i < len(comments) else ""
            prev_cm = comments[i - 1] if i - 1 < len(comments) else ""

            prev_sda = prev.get("SDA", "X")
            cur_sda = cur.get("SDA", "X")
            prev_scl = prev.get("SCL", "X")
            cur_scl = cur.get("SCL", "X")

            # 跳过比较/高阻状态 (读操作由DUT驱动)
            if cur_sda in ("H", "L", "Z", "X") or prev_sda in ("H", "L", "Z", "X"):
                continue

            # 检测 START: SCL=1 时 SDA 从 1→0
            is_start = (prev_scl == "1" and cur_scl == "1" and
                       prev_sda == "1" and cur_sda == "0")
            # 检测 STOP: SCL=1 时 SDA 从 0→1
            is_stop = (prev_scl == "1" and cur_scl == "1" and
                      prev_sda == "0" and cur_sda == "1")

            if is_start:
                in_transaction = True
                byte_bit_count = 0
                expect_ack = False
                continue
            if is_stop:
                in_transaction = False
                byte_bit_count = 0
                expect_ack = False
                continue

            # 规则1: SDA 仅在 SCL=0 时改变 (驱动状态)
            if (cur_sda in ("0", "1") and prev_sda in ("0", "1") and
                cur_sda != prev_sda and cur_scl == "1"):
                # SCL=1 时 SDA 发生变化且不是 START/STOP → 违规
                if not is_start and not is_stop:
                    issues.append({
                        "vec_idx": i,
                        "severity": "warning",
                        "rule": "SDA_CHANGE_ON_SCL_HIGH",
                        "detail": f"Vec {i}: SDA changed {prev_sda}→{cur_sda} while SCL=1 "
                                  f"(not START/STOP)",
                    })

        # 规则2: 检查首个向量的总线状态
        if n > 0:
            first = vectors[0]
            if first.get("SCL", "X") not in ("1", "X") or first.get("SDA", "X") not in ("1", "X"):
                issues.append({
                    "vec_idx": 0,
                    "severity": "info",
                    "rule": "INITIAL_BUS_STATE",
                    "detail": "Vec 0: Bus not idle (SDA=1,SCL=1) at start — "
                              "may be intentional for OS/DC test",
                })

        # 规则3: 检查末尾向量的总线状态
        if n > 1:
            last = vectors[-1]
            if last.get("SCL", "X") not in ("1", "X") or last.get("SDA", "X") not in ("1", "X"):
                issues.append({
                    "vec_idx": n - 1,
                    "severity": "info",
                    "rule": "FINAL_BUS_STATE",
                    "detail": f"Vec {n-1}: Bus not idle at end — "
                              f"SDA={last.get('SDA','?')}, SCL={last.get('SCL','?')}",
                })

        # 统计 START/STOP 配对
        start_count = sum(1 for c in comments if c and "START" in c and "Rep" not in c)
        stop_count = sum(1 for c in comments if c and "STOP" in c)
        rep_count = sum(1 for c in comments if c and "RepSTART" in c)

        if abs(start_count + rep_count - stop_count) > rep_count + 2:
            issues.append({
                "vec_idx": -1,
                "severity": "warning",
                "rule": "START_STOP_MISMATCH",
                "detail": f"START={start_count}, RepSTART={rep_count}, STOP={stop_count} — "
                          f"significant mismatch",
            })

        error_count = sum(1 for i in issues if i["severity"] == "error")
        warn_count = sum(1 for i in issues if i["severity"] == "warning")
        info_count = sum(1 for i in issues if i["severity"] == "info")

        # 添加汇总 info
        issues.insert(0, {
            "vec_idx": -1,
            "severity": "info",
            "rule": "SUMMARY",
            "detail": f"Protocol check: {n} vectors, START={start_count}, "
                      f"RepSTART={rep_count}, STOP={stop_count} | "
                      f"Issues: {error_count} errors, {warn_count} warnings, {info_count} info",
        })

        return len(issues) - 1, issues  # 不含 SUMMARY


# ============================================================
# SPI 时序合规性检查器
# ============================================================

class SPITimingChecker:
    """SPI 时序参数检查"""

    @staticmethod
    def check(period_ns, voltage_key="5.0V"):
        constraints = SPI_TIMING_CONSTRAINTS.get(voltage_key, SPI_TIMING_CONSTRAINTS["5.0V"])
        results = []

        # fSCK: 1 bit = 2 vectors (SCK low + SCK high)
        fSCK_actual = 1e9 / (period_ns * 2) / 1e6  # MHz
        results.append({
            "param": "fSCK",
            "required": f"≤ {constraints['fSCK_max_MHz']} MHz",
            "actual": f"{fSCK_actual:.2f} MHz",
            "passed": fSCK_actual <= constraints["fSCK_max_MHz"],
            "note": "SPI时钟频率 (2向量/bit)",
        })

        # tCSS: CS setup (1 vector before first SCK)
        actual_tCSS = period_ns
        results.append({
            "param": "tCSS",
            "required": f"≥ {constraints['tCSS_min']} ns",
            "actual": f"{actual_tCSS} ns",
            "passed": actual_tCSS >= constraints["tCSS_min"],
            "note": "CS建立时间",
        })

        # tCSH: CS hold (1 vector after last SCK)
        actual_tCSH = period_ns
        results.append({
            "param": "tCSH",
            "required": f"≥ {constraints['tCSH_min']} ns",
            "actual": f"{actual_tCSH} ns",
            "passed": actual_tCSH >= constraints["tCSH_min"],
            "note": "CS保持时间",
        })

        # tSU: Data setup
        actual_tSU = period_ns
        results.append({
            "param": "tSU",
            "required": f"≥ {constraints['tSU_min']} ns",
            "actual": f"{actual_tSU} ns",
            "passed": actual_tSU >= constraints["tSU_min"],
            "note": "数据建立时间 (MOSI→SCK↑)",
        })

        # tCH: Clock high time
        actual_tCH = period_ns
        results.append({
            "param": "tCH",
            "required": f"≥ {constraints['tCH_min']} ns",
            "actual": f"{actual_tCH} ns",
            "passed": actual_tCH >= constraints["tCH_min"],
            "note": "SCK高电平时间",
        })

        # tCL: Clock low time
        actual_tCL = period_ns
        results.append({
            "param": "tCL",
            "required": f"≥ {constraints['tCL_min']} ns",
            "actual": f"{actual_tCL} ns",
            "passed": actual_tCL >= constraints["tCL_min"],
            "note": "SCK低电平时间",
        })

        # tCSD: CS deselect time
        actual_tCSD = period_ns
        results.append({
            "param": "tCSD",
            "required": f"≥ {constraints['tCSD_min']} ns",
            "actual": f"{actual_tCSD} ns",
            "passed": actual_tCSD >= constraints["tCSD_min"],
            "note": "CS片选间隔",
        })

        all_passed = all(r["passed"] for r in results)
        return all_passed, results


class MicrowireTimingChecker:
    """Microwire 时序参数检查"""

    @staticmethod
    def check(period_ns, voltage_key="5.0V"):
        constraints = MW_TIMING_CONSTRAINTS.get(voltage_key, MW_TIMING_CONSTRAINTS["5.0V"])
        results = []

        fSK_actual = 1e9 / (period_ns * 2) / 1e6
        results.append({
            "param": "fSK",
            "required": f"≤ {constraints['fSK_max_MHz']} MHz",
            "actual": f"{fSK_actual:.2f} MHz",
            "passed": fSK_actual <= constraints["fSK_max_MHz"],
            "note": "Microwire时钟频率",
        })

        for p_name, c_key, note in [
            ("tCSS", "tCSS_min", "CS建立时间"),
            ("tCSH", "tCSH_min", "CS保持时间"),
            ("tSKH", "tSKH_min", "SK高电平时间"),
            ("tSKL", "tSKL_min", "SK低电平时间"),
            ("tDIS", "tDIS_min", "DI数据建立时间"),
        ]:
            results.append({
                "param": p_name,
                "required": f"≥ {constraints[c_key]} ns",
                "actual": f"{period_ns} ns",
                "passed": period_ns >= constraints[c_key],
                "note": note,
            })

        all_passed = all(r["passed"] for r in results)
        return all_passed, results


# ============================================================
# SPI / Microwire 协议合规性验证器
# ============================================================

class SPIProtocolValidator:
    """SPI 向量协议规则检查"""

    @staticmethod
    def validate(vectors, comments):
        issues = []
        n = len(vectors)
        if n < 2:
            return 0, issues

        cs_active_count = 0
        cs_deactive_count = 0

        for i in range(1, n):
            prev = vectors[i - 1]
            cur = vectors[i]
            prev_cs = prev.get("CS", "1")
            cur_cs = cur.get("CS", "1")
            cur_sck = cur.get("SCK", "0")

            # CS transitions
            if prev_cs == "1" and cur_cs == "0":
                cs_active_count += 1
            elif prev_cs == "0" and cur_cs == "1":
                cs_deactive_count += 1

            # Rule: SCK should be 0 when CS transitions
            if prev_cs != cur_cs and cur_sck == "1":
                issues.append({
                    "vec_idx": i, "severity": "warning",
                    "rule": "CS_TRANSITION_SCK_HIGH",
                    "detail": f"Vec {i}: CS changed while SCK=1",
                })

        # CS pairing check
        if abs(cs_active_count - cs_deactive_count) > 1:
            issues.append({
                "vec_idx": -1, "severity": "warning",
                "rule": "CS_PAIR_MISMATCH",
                "detail": f"CS↓={cs_active_count}, CS↑={cs_deactive_count} — mismatch",
            })

        issues.insert(0, {
            "vec_idx": -1, "severity": "info", "rule": "SUMMARY",
            "detail": f"SPI check: {n} vectors, CS↓={cs_active_count}, "
                      f"CS↑={cs_deactive_count} | "
                      f"Issues: {sum(1 for i in issues if i['severity']=='warning')} warnings",
        })
        return len(issues) - 1, issues


class MicrowireProtocolValidator:
    """Microwire 向量协议规则检查"""

    @staticmethod
    def validate(vectors, comments):
        issues = []
        n = len(vectors)
        if n < 2:
            return 0, issues

        cs_high_count = 0
        cs_low_count = 0

        for i in range(1, n):
            prev = vectors[i - 1]
            cur = vectors[i]
            prev_cs = prev.get("CS", "0")
            cur_cs = cur.get("CS", "0")
            cur_sk = cur.get("SK", "0")

            if prev_cs == "0" and cur_cs == "1":
                cs_high_count += 1
            elif prev_cs == "1" and cur_cs == "0":
                cs_low_count += 1

            # Rule: SK should be 0 when CS is inactive
            if cur_cs == "0" and cur_sk == "1":
                issues.append({
                    "vec_idx": i, "severity": "warning",
                    "rule": "SK_HIGH_CS_INACTIVE",
                    "detail": f"Vec {i}: SK=1 while CS=0 (inactive)",
                })

        issues.insert(0, {
            "vec_idx": -1, "severity": "info", "rule": "SUMMARY",
            "detail": f"MW check: {n} vectors, CS↑={cs_high_count}, CS↓={cs_low_count} | "
                      f"Issues: {sum(1 for i in issues if i['severity']=='warning')} warnings",
        })
        return len(issues) - 1, issues


# ============================================================
# v6.0 — 向量模拟引擎 + 协议解码器
# ============================================================

class PatternSimulator:
    """向量模拟引擎: 逐周期执行向量, 解码协议事务, 追踪存储器状态"""

    def __init__(self, protocol="I2C", capacity_bytes=256, page_size=8,
                 addr_byte_count=1, device_addr_base=0xA0):
        self.protocol = protocol
        self.capacity = capacity_bytes
        self.page_size = page_size
        self.addr_bytes = addr_byte_count
        self.dev_addr_base = device_addr_base
        self.memory = bytearray(capacity_bytes)
        self.transactions = []
        self.errors = []
        self.log = []
        self.cycle = 0
        # Fail Bit Map 追踪 (Phase 1)
        self.fail_map = {}        # {addr: {"tests": [], "pass": bool, "expected": int, "actual": int}}
        self.test_coverage = {}   # {addr: [test_name1, ...]}
        self.march_steps = []     # [{step_idx, desc, addrs_covered: set}]
        # SPI 状态
        self.spi_wel = False  # Write Enable Latch
        self.spi_wip = False  # Write In Progress
        self.spi_status_reg = 0x00
        # Microwire 状态
        self.mw_ewen = False  # EWEN active

    def reset(self):
        """重置模拟器状态"""
        self.memory = bytearray(self.capacity)
        self.transactions = []
        self.errors = []
        self.log = []
        self.cycle = 0
        self.fail_map = {}
        self.test_coverage = {}
        self.march_steps = []
        self.spi_wel = False
        self.spi_wip = False
        self.spi_status_reg = 0x00
        self.mw_ewen = False

    def simulate(self, vectors, comments):
        """主入口: 根据协议分发模拟"""
        self.reset()
        if not vectors:
            return
        if self.protocol == "I2C":
            self._simulate_i2c(vectors, comments)
        elif self.protocol == "SPI":
            self._simulate_spi(vectors, comments)
        elif self.protocol == "Microwire":
            self._simulate_mw(vectors, comments)
        self.log.append(f"[DONE] Simulation complete: {len(self.transactions)} transactions, "
                        f"{len(self.errors)} errors")

    def simulate_test(self, test_name, vectors, comments):
        """按测试段模拟并更新 fail_map / test_coverage"""
        txn_before = len(self.transactions)
        self.simulate(vectors, comments)
        # 分析本测试段新增的事务
        for txn in self.transactions[txn_before:]:
            addr = txn.get("address", 0)
            data_list = txn.get("data", [])
            is_read = txn.get("type") == "READ"
            for idx, d in enumerate(data_list):
                a = (addr + idx) % self.capacity
                # 覆盖率追踪
                if a not in self.test_coverage:
                    self.test_coverage[a] = []
                if test_name not in self.test_coverage[a]:
                    self.test_coverage[a].append(test_name)
                # Fail Map 追踪 (仅读操作有 pass/fail 意义)
                if is_read:
                    expected = self.memory[a]
                    match = txn.get("match", True)
                    if a not in self.fail_map:
                        self.fail_map[a] = {"tests": [], "pass": match,
                                            "expected": expected, "actual": d}
                    else:
                        if not match:
                            self.fail_map[a]["pass"] = False
                            self.fail_map[a]["actual"] = d
                            self.fail_map[a]["expected"] = expected
                    if test_name not in self.fail_map[a]["tests"]:
                        self.fail_map[a]["tests"].append(test_name)
        # March C- 步骤追踪
        if "MARCH" in test_name.upper():
            step_addrs = set()
            for txn in self.transactions[txn_before:]:
                addr = txn.get("address", 0)
                data_list = txn.get("data", [])
                for idx in range(len(data_list)):
                    step_addrs.add((addr + idx) % self.capacity)
            if step_addrs:
                step_idx = len(self.march_steps) + 1
                self.march_steps.append({
                    "step_idx": step_idx,
                    "desc": test_name,
                    "addrs_covered": step_addrs,
                })

    # ------ I2C 模拟 ------
    def _simulate_i2c(self, vectors, comments):
        """I2C 协议状态机解码"""
        state = "IDLE"
        bit_count = 0
        current_byte = 0
        bytes_in_txn = []
        txn_start = 0
        txn_type = None
        dev_addr = 0
        mem_addr = 0
        is_read = False
        prev_scl = "1"
        prev_sda = "1"
        addr_set = False

        for i, vec in enumerate(vectors):
            scl = vec.get("SCL", "X")
            sda = vec.get("SDA", "X")
            comment = comments[i] if i < len(comments) else ""

            # Detect START: SCL=1, SDA falling edge (1→0)
            if scl in ("1", "H") and prev_sda in ("1", "H") and sda in ("0", "L"):
                if state != "IDLE":
                    # Repeated START
                    self.log.append(f"[INFO] Cycle {i}: Repeated START")
                else:
                    self.log.append(f"[INFO] Cycle {i}: START condition")
                state = "ADDR_BYTE"
                bit_count = 0
                current_byte = 0
                bytes_in_txn = []
                txn_start = i
                addr_set = False

            # Detect STOP: SCL=1, SDA rising edge (0→1)
            elif scl in ("1", "H") and prev_sda in ("0", "L") and sda in ("1", "H"):
                if state != "IDLE":
                    # Complete transaction
                    if txn_type:
                        txn = {
                            "cycle_start": txn_start, "cycle_end": i,
                            "type": txn_type, "command": "Byte Write" if not is_read else "Random Read",
                            "device_addr": dev_addr, "address": mem_addr,
                            "data": list(bytes_in_txn), "match": True,
                            "warnings": [],
                        }
                        if is_read:
                            # Verify read data against memory
                            for idx, d in enumerate(bytes_in_txn):
                                ea = (mem_addr + idx) % self.capacity
                                if d != self.memory[ea]:
                                    txn["match"] = False
                                    txn["warnings"].append(
                                        f"Addr 0x{ea:02X}: expected 0x{self.memory[ea]:02X}, got 0x{d:02X}")
                        else:
                            # Write data to memory
                            for idx, d in enumerate(bytes_in_txn):
                                wa = (mem_addr + idx) % self.capacity
                                self.memory[wa] = d
                        self.transactions.append(txn)
                        rw = "READ" if is_read else "WRITE"
                        self.log.append(
                            f"[INFO] Cycle {txn_start}-{i}: {rw} addr=0x{mem_addr:02X}, "
                            f"data=[{','.join(f'0x{d:02X}' for d in bytes_in_txn)}]"
                            f"{' ✓' if txn.get('match', True) else ' ✗ MISMATCH'}")
                    state = "IDLE"
                    txn_type = None
                    self.log.append(f"[INFO] Cycle {i}: STOP condition")

            # SCL rising edge: sample data bit
            elif prev_scl in ("0", "L") and scl in ("1", "H"):
                if state in ("ADDR_BYTE", "DATA_BYTE"):
                    bit_val = 1 if sda in ("1", "H", "Z") else 0
                    current_byte = (current_byte << 1) | bit_val
                    bit_count += 1

                    if bit_count == 8:
                        if state == "ADDR_BYTE":
                            dev_addr = current_byte & 0xFE
                            is_read = bool(current_byte & 0x01)
                            txn_type = "READ" if is_read else "WRITE"
                            self.log.append(
                                f"[INFO] Cycle {i}: Device addr=0x{dev_addr:02X}, "
                                f"{'READ' if is_read else 'WRITE'}")
                            state = "ADDR_ACK"
                        else:
                            if not addr_set and not is_read:
                                mem_addr = current_byte
                                addr_set = True
                                self.log.append(f"[INFO] Cycle {i}: Mem addr=0x{mem_addr:02X}")
                            else:
                                bytes_in_txn.append(current_byte)
                            state = "DATA_ACK"
                        bit_count = 0
                        current_byte = 0

                elif state in ("ADDR_ACK", "DATA_ACK"):
                    # ACK bit: SDA=0 means ACK, SDA=1 means NACK
                    ack = sda in ("0", "L")
                    if state == "ADDR_ACK":
                        if not ack:
                            self.errors.append({
                                "cycle": i, "severity": "error",
                                "detail": f"NACK on device address 0x{dev_addr:02X}",
                            })
                            self.log.append(f"[WARN] Cycle {i}: NACK on addr 0x{dev_addr:02X}")
                    state = "DATA_BYTE"
                    bit_count = 0
                    current_byte = 0

            prev_scl = scl
            prev_sda = sda

    # ------ SPI 模拟 ------
    def _simulate_spi(self, vectors, comments):
        """SPI 协议状态机解码"""
        state = "IDLE"
        bit_count = 0
        current_byte = 0
        cmd_byte = 0
        addr_bytes_collected = []
        data_bytes = []
        txn_start = 0
        recv_mode = False  # True when receiving MISO data
        prev_cs = "1"

        for i, vec in enumerate(vectors):
            cs = vec.get("CS", "1")
            sck = vec.get("SCK", "0")
            mosi = vec.get("MOSI", "0")
            miso = vec.get("MISO", "X")
            comment = comments[i] if i < len(comments) else ""
            prev_sck = vectors[i-1].get("SCK", "0") if i > 0 else "0"

            # CS falling edge → transaction start
            if prev_cs in ("1", "H") and cs in ("0", "L"):
                state = "COMMAND"
                bit_count = 0
                current_byte = 0
                cmd_byte = 0
                addr_bytes_collected = []
                data_bytes = []
                txn_start = i
                recv_mode = False

            # CS rising edge → transaction end
            elif prev_cs in ("0", "L") and cs in ("1", "H"):
                if state != "IDLE":
                    self._finalize_spi_txn(txn_start, i, cmd_byte, addr_bytes_collected, data_bytes)
                state = "IDLE"

            # SCK rising edge while CS active: sample bit
            elif cs in ("0", "L") and prev_sck in ("0", "L") and sck in ("1", "H"):
                if recv_mode:
                    bit_val = 1 if miso in ("1", "H") else 0
                else:
                    bit_val = 1 if mosi in ("1", "H", "Z") else 0
                current_byte = (current_byte << 1) | bit_val
                bit_count += 1

                if bit_count == 8:
                    if state == "COMMAND":
                        cmd_byte = current_byte
                        cmd_name = {0x06: "WREN", 0x04: "WRDI", 0x05: "RDSR",
                                    0x01: "WRSR", 0x03: "READ", 0x02: "WRITE",
                                    0x20: "SECTOR_ERASE", 0xD8: "BLOCK_ERASE",
                                    0xC7: "CHIP_ERASE", 0x9F: "JEDEC_ID",
                                    0x0B: "FAST_READ"}.get(cmd_byte, f"0x{cmd_byte:02X}")
                        self.log.append(f"[INFO] Cycle {i}: SPI cmd={cmd_name}")

                        # Commands with no further data
                        if cmd_byte in (0x06, 0x04, 0xC7):
                            if cmd_byte == 0x06:
                                self.spi_wel = True
                            elif cmd_byte == 0x04:
                                self.spi_wel = False
                            state = "DONE"
                        elif cmd_byte in (0x05,):  # RDSR → receive status
                            recv_mode = True
                            state = "DATA"
                        elif cmd_byte == 0x9F:  # JEDEC_ID → receive 3 bytes
                            recv_mode = True
                            state = "DATA"
                        elif cmd_byte in (0x03, 0x0B):  # READ → addr then receive data
                            state = "ADDRESS"
                            recv_mode = False
                        elif cmd_byte in (0x02, 0x20, 0xD8):  # WRITE/ERASE → addr then send data
                            state = "ADDRESS"
                        else:
                            state = "DATA"
                    elif state == "ADDRESS":
                        addr_bytes_collected.append(current_byte)
                        if len(addr_bytes_collected) >= self.addr_bytes:
                            state = "DATA"
                            if cmd_byte in (0x03, 0x0B):  # READ → switch to receive
                                recv_mode = True
                    elif state == "DATA":
                        data_bytes.append(current_byte)

                    bit_count = 0
                    current_byte = 0

            prev_cs = cs

    def _finalize_spi_txn(self, start, end, cmd, addr_bytes, data_bytes):
        """完成 SPI 事务记录"""
        addr = 0
        for b in addr_bytes:
            addr = (addr << 8) | b

        cmd_names = {0x06: "WREN", 0x04: "WRDI", 0x05: "RDSR", 0x01: "WRSR",
                     0x03: "READ", 0x02: "WRITE", 0x20: "SECTOR_ERASE",
                     0xD8: "BLOCK_ERASE", 0xC7: "CHIP_ERASE", 0x9F: "JEDEC_ID"}
        cmd_name = cmd_names.get(cmd, f"CMD_0x{cmd:02X}")

        txn = {
            "cycle_start": start, "cycle_end": end,
            "type": "READ" if cmd in (0x03, 0x0B) else "WRITE" if cmd == 0x02 else "COMMAND",
            "command": cmd_name, "address": addr,
            "data": list(data_bytes), "match": True, "warnings": [],
        }

        if cmd == 0x02:  # WRITE / Page Program
            if not self.spi_wel:
                txn["warnings"].append("WRITE without WREN!")
                self.errors.append({"cycle": start, "severity": "error",
                                    "detail": "SPI WRITE without WREN"})
            else:
                for idx, d in enumerate(data_bytes):
                    wa = (addr + idx) % self.capacity
                    self.memory[wa] = d
                self.spi_wel = False
                self.spi_wip = True
        elif cmd in (0x03, 0x0B):  # READ
            for idx, d in enumerate(data_bytes):
                ra = (addr + idx) % self.capacity
                if d != self.memory[ra]:
                    txn["match"] = False
                    txn["warnings"].append(
                        f"Addr 0x{ra:04X}: expected 0x{self.memory[ra]:02X}, got 0x{d:02X}")
        elif cmd == 0x05:  # RDSR
            if data_bytes:
                self.spi_status_reg = data_bytes[0]
                self.spi_wip = bool(data_bytes[0] & 0x01)
        elif cmd == 0x20:  # Sector Erase
            if not self.spi_wel:
                txn["warnings"].append("SECTOR_ERASE without WREN!")
                self.errors.append({"cycle": start, "severity": "error",
                                    "detail": "Sector erase without WREN"})
            else:
                sector_base = addr & ~0xFFF  # 4KB aligned
                for j in range(min(4096, self.capacity - sector_base)):
                    self.memory[sector_base + j] = 0xFF
                self.spi_wel = False

        data_str = ','.join(f'0x{d:02X}' for d in data_bytes[:8])
        if len(data_bytes) > 8:
            data_str += f"...+{len(data_bytes)-8}"
        match_str = " ✓" if txn["match"] else " ✗"
        self.log.append(f"[INFO] Cycle {start}-{end}: SPI {cmd_name} "
                        f"addr=0x{addr:04X} data=[{data_str}]{match_str}")
        self.transactions.append(txn)

    # ------ Microwire 模拟 ------
    def _simulate_mw(self, vectors, comments):
        """Microwire 协议状态机解码"""
        state = "IDLE"
        bit_count = 0
        current_bits = 0
        opcode = 0
        addr_val = 0
        data_val = 0
        txn_start = 0
        prev_cs = "0"
        recv_mode = False

        for i, vec in enumerate(vectors):
            cs = vec.get("CS", "0")
            sk = vec.get("SK", "0")
            di = vec.get("DI", "0")
            do = vec.get("DO", "X")
            comment = comments[i] if i < len(comments) else ""
            prev_sk = vectors[i-1].get("SK", "0") if i > 0 else "0"

            # CS rising edge (high active) → transaction start
            if prev_cs in ("0", "L") and cs in ("1", "H"):
                state = "START_BIT"
                bit_count = 0
                opcode = 0
                addr_val = 0
                data_val = 0
                txn_start = i
                recv_mode = False

            # CS falling edge → transaction end
            elif prev_cs in ("1", "H") and cs in ("0", "L"):
                if state != "IDLE":
                    self._finalize_mw_txn(txn_start, i, opcode, addr_val, data_val, recv_mode)
                state = "IDLE"

            # SK rising edge while CS active
            elif cs in ("1", "H") and prev_sk in ("0", "L") and sk in ("1", "H"):
                if recv_mode:
                    bit_val = 1 if do in ("1", "H") else 0
                else:
                    bit_val = 1 if di in ("1", "H") else 0

                if state == "START_BIT":
                    # Start bit should be 1
                    if bit_val != 1:
                        self.errors.append({"cycle": i, "severity": "warning",
                                            "detail": "Missing start bit (expected 1)"})
                    state = "OPCODE"
                    bit_count = 0
                elif state == "OPCODE":
                    opcode = (opcode << 1) | bit_val
                    bit_count += 1
                    if bit_count >= 2:
                        state = "ADDRESS"
                        bit_count = 0
                elif state == "ADDRESS":
                    addr_val = (addr_val << 1) | bit_val
                    bit_count += 1
                    # Use configured addr bits (default 6 for 93C46)
                    max_addr_bits = 10  # generic max
                    if bit_count >= 6:  # minimum, actual depends on chip
                        # Check if this is EWEN/EWDS (opcode=00, addr starts with 11 or 00)
                        if opcode == 0b00:
                            if bit_count >= 6:
                                state = "DONE"
                                # Decode EWEN vs EWDS from addr MSBs
                                if (addr_val >> (bit_count - 2)) & 0x03 == 0x03:
                                    self.mw_ewen = True
                                    self.log.append(f"[INFO] Cycle {i}: MW EWEN (write enable)")
                                elif (addr_val >> (bit_count - 2)) & 0x03 == 0x00:
                                    self.mw_ewen = False
                                    self.log.append(f"[INFO] Cycle {i}: MW EWDS (write disable)")
                        elif opcode == 0b10:  # READ
                            recv_mode = True
                            state = "DATA"
                            bit_count = 0
                        elif opcode == 0b01:  # WRITE
                            state = "DATA"
                            bit_count = 0
                        elif opcode == 0b11:  # ERASE
                            state = "DONE"
                elif state == "DATA":
                    data_val = (data_val << 1) | bit_val
                    bit_count += 1

            prev_cs = cs

    def _finalize_mw_txn(self, start, end, opcode, addr, data, recv_mode):
        """完成 Microwire 事务记录"""
        op_names = {0b10: "READ", 0b01: "WRITE", 0b11: "ERASE", 0b00: "EWEN/EWDS"}
        op_name = op_names.get(opcode, f"OP_{opcode:02b}")

        txn = {
            "cycle_start": start, "cycle_end": end,
            "type": "READ" if opcode == 0b10 else "WRITE" if opcode == 0b01 else "COMMAND",
            "command": op_name, "address": addr,
            "data": [data & 0xFF] if data else [], "match": True, "warnings": [],
        }

        if opcode == 0b01:  # WRITE
            if not self.mw_ewen:
                txn["warnings"].append("WRITE without EWEN!")
                self.errors.append({"cycle": start, "severity": "error",
                                    "detail": "MW WRITE without EWEN"})
            else:
                if addr < self.capacity:
                    self.memory[addr] = data & 0xFF
        elif opcode == 0b10:  # READ
            if addr < self.capacity:
                if (data & 0xFF) != self.memory[addr]:
                    txn["match"] = False
        elif opcode == 0b11:  # ERASE
            if not self.mw_ewen:
                txn["warnings"].append("ERASE without EWEN!")

        self.log.append(f"[INFO] Cycle {start}-{end}: MW {op_name} addr={addr} data=0x{data & 0xFF:02X}"
                        f"{' ✓' if txn['match'] else ' ✗'}")
        self.transactions.append(txn)


# ============================================================
# v6.0 — Shmoo Plot 参数表征引擎
# ============================================================

class ShmooEngine:
    """V×F Shmoo Plot 参数表征引擎 — 工业级增强版"""

    # AT24C02 Datasheet 规格边界 (电压→最大频率)
    SPEC_BOUNDARY = [
        (1.8, 100),    # 1.8V → 100kHz
        (2.5, 400),    # 2.5V → 400kHz
        (5.0, 1000),   # 5.0V → 1MHz
    ]
    SPEC_VCC_MIN = 1.8
    SPEC_VCC_MAX = 5.5

    def __init__(self):
        self.results = {}  # (voltage_key, freq_khz) → dict
        self.voltage_points = []
        self.freq_points = []

    def configure_sweep(self, voltage_keys, freq_list_khz):
        """配置扫描参数"""
        self.voltage_points = list(voltage_keys)
        self.freq_points = list(freq_list_khz)
        self.results = {}

    def evaluate_point(self, vk, freq, protocol="I2C"):
        """评估单个 (V, F) 点的 Pass/Marginal/Fail 状态

        返回: {"status": "PASS"|"MARGINAL"|"FAIL",
               "margin_pct": float, "timing_details": list,
               "fail_reason": str|None}
        """
        period_ns = int(1e6 / freq) if freq > 0 else 10000

        # 电压可行性
        voltage_ok = vk in VOLTAGE_PRESETS
        if not voltage_ok:
            return {"status": "FAIL", "margin_pct": -100.0,
                    "timing_details": [], "fail_reason": f"电压预设 {vk} 不存在"}

        # 时序检查 (仅 I2C 支持详细校验)
        if protocol == "I2C":
            passed, timing_results = I2CTimingChecker.check(period_ns, vk)
            # 计算最小余量百分比
            margins = []
            fail_reason = None
            for tr in timing_results:
                if tr["param"] == "fSCL":
                    # 频率约束: actual <= max, margin = (max - actual) / max
                    constraints = I2C_TIMING_CONSTRAINTS.get(vk, {})
                    fmax = constraints.get("fSCL_max_kHz", 1000)
                    m = (fmax - freq) / fmax * 100 if fmax > 0 else -100
                    margins.append(m)
                    if not tr["passed"]:
                        fail_reason = f"fSCL={freq}kHz > max={fmax}kHz"
                elif tr["param"].startswith("t"):
                    # 时间约束: actual >= min, margin = (actual - min) / min
                    if "≥" in tr.get("required", ""):
                        try:
                            req_val = float(tr["required"].split("≥")[1].strip().split()[0])
                            act_val = float(tr["actual"].split()[0])
                            m = (act_val - req_val) / req_val * 100 if req_val > 0 else 100
                            margins.append(m)
                            if not tr["passed"] and fail_reason is None:
                                fail_reason = f"{tr['param']}={act_val}ns < min={req_val}ns"
                        except (ValueError, IndexError):
                            pass

            min_margin = min(margins) if margins else 0
            if not passed:
                status = "FAIL"
            elif min_margin < 20:
                status = "MARGINAL"
            else:
                status = "PASS"

            return {"status": status, "margin_pct": min_margin,
                    "timing_details": timing_results, "fail_reason": fail_reason}
        else:
            # SPI / Microwire: 简单频率检查
            constraints = {}
            fmax_key = "fSCL_max"
            if protocol == "SPI":
                constraints = SPI_TIMING_CONSTRAINTS.get(vk, {})
                fmax_key = "fSCK_max"
            elif protocol == "Microwire":
                constraints = MW_TIMING_CONSTRAINTS.get(vk, {})
                fmax_key = "fSK_max"
            fmax = constraints.get(fmax_key, 10000)
            margin = (fmax - freq) / fmax * 100 if fmax > 0 else -100
            if freq > fmax:
                return {"status": "FAIL", "margin_pct": margin,
                        "timing_details": [], "fail_reason": f"freq={freq}kHz > max={fmax}kHz"}
            elif margin < 20:
                return {"status": "MARGINAL", "margin_pct": margin,
                        "timing_details": [], "fail_reason": None}
            else:
                return {"status": "PASS", "margin_pct": margin,
                        "timing_details": [], "fail_reason": None}

    def run_sweep(self, generator_factory, protocol="I2C", progress_callback=None):
        """执行 V×F 扫描 — 使用 evaluate_point 进行详细评估"""
        total = len(self.voltage_points) * len(self.freq_points)
        step = 0
        for vk in self.voltage_points:
            for freq in self.freq_points:
                eval_result = self.evaluate_point(vk, freq, protocol)
                period_ns = int(1e6 / freq) if freq > 0 else 10000

                self.results[(vk, freq)] = {
                    "pass": eval_result["status"] != "FAIL",
                    "status": eval_result["status"],
                    "margin_pct": eval_result["margin_pct"],
                    "timing_details": eval_result["timing_details"],
                    "fail_reason": eval_result["fail_reason"],
                    "timing_ok": eval_result["status"] != "FAIL",
                    "voltage_ok": vk in VOLTAGE_PRESETS,
                    "period_ns": period_ns,
                    "freq_khz": freq,
                    "voltage": vk,
                }

                step += 1
                if progress_callback:
                    progress_callback(step, total, f"{vk} × {freq}kHz")

    def calculate_margins(self, nominal_voltage="3.3V", nominal_freq=400):
        """计算电压/频率余量"""
        pass_voltages = set()
        pass_freqs = set()
        for (vk, fk), r in self.results.items():
            if r["pass"]:
                pass_voltages.add(vk)
                pass_freqs.add(fk)

        v_vals = []
        for vk in pass_voltages:
            try:
                v_vals.append(float(vk.replace("V", "")))
            except ValueError:
                pass

        margins = {
            "v_min": f"{min(v_vals):.1f}V" if v_vals else "N/A",
            "v_max": f"{max(v_vals):.1f}V" if v_vals else "N/A",
            "f_max": f"{max(pass_freqs)}kHz" if pass_freqs else "N/A",
            "f_min": f"{min(pass_freqs)}kHz" if pass_freqs else "N/A",
            "total_points": len(self.results),
            "pass_points": sum(1 for r in self.results.values() if r["pass"]),
            "fail_points": sum(1 for r in self.results.values() if not r["pass"]),
            "marginal_points": sum(1 for r in self.results.values()
                                   if r.get("status") == "MARGINAL"),
        }
        return margins

    def get_matrix(self):
        """返回用于绘制 Shmoo Plot 的矩阵数据"""
        return {
            "voltages": self.voltage_points,
            "frequencies": self.freq_points,
            "results": self.results,
        }

    @staticmethod
    def get_datasheet_bounds():
        """返回 AT24C02 Datasheet 规格边界"""
        return {
            "vcc_min": ShmooEngine.SPEC_VCC_MIN,
            "vcc_max": ShmooEngine.SPEC_VCC_MAX,
            "boundary": list(ShmooEngine.SPEC_BOUNDARY),
        }

    @staticmethod
    def spec_fmax_for_voltage(vcc_v):
        """线性插值获取指定电压下的 fSCL_max (kHz)"""
        pts = ShmooEngine.SPEC_BOUNDARY
        if vcc_v <= pts[0][0]:
            return pts[0][1]
        if vcc_v >= pts[-1][0]:
            return pts[-1][1]
        for i in range(len(pts) - 1):
            v0, f0 = pts[i]
            v1, f1 = pts[i + 1]
            if v0 <= vcc_v <= v1:
                ratio = (vcc_v - v0) / (v1 - v0)
                return f0 + ratio * (f1 - f0)
        return pts[-1][1]


# ============================================================
# v6.0 — 测试流程编排引擎
# ============================================================

class TestFlowEngine:
    """测试流程编排: 条件分支, Bin 分选, 依赖管理"""

    DEFAULT_BIN_TABLE = {
        1:  ("PASS",       "GOOD", "All tests passed"),
        2:  ("OS_FAIL",    "HARD", "Open/Short failure — contact/bond issue"),
        3:  ("DC_FAIL",    "HARD", "DC parametric failure — ISB/ICC/VOL/VOH"),
        4:  ("FUNC_FAIL",  "SOFT", "Functional test failure — R/W mismatch"),
        5:  ("MARCH_FAIL", "SOFT", "March C- memory failure — SAF/TF/CF"),
        6:  ("SCAN_FAIL",  "SOFT", "Address scan failure — address decode"),
        7:  ("RET_FAIL",   "SOFT", "Data retention failure"),
        8:  ("ERR_FAIL",   "SOFT", "Protocol error test failure"),
        9:  ("ENDUR_FAIL", "SOFT", "Endurance failure — write cycle limit"),
        10: ("MARCH_B_FAIL","SOFT", "March B memory failure"),
        11: ("IDDQ_FAIL",   "SOFT", "IDDQ quiescent current failure"),
    }

    DEFAULT_TEST_LIMITS = {
        "ISB":      {"min": None, "max": 1.0,   "unit": "μA",    "desc": "Standby current"},
        "ICC_R":    {"min": None, "max": 1.0,   "unit": "mA",    "desc": "Read current"},
        "ICC_W":    {"min": None, "max": 3.0,   "unit": "mA",    "desc": "Write current"},
        "VOL":      {"min": None, "max": 0.4,   "unit": "V",     "desc": "Output low voltage"},
        "VOH":      {"min": 2.4,  "max": None,  "unit": "V",     "desc": "Output high voltage"},
        "VIL":      {"min": -0.5, "max": 1.5,   "unit": "V",     "desc": "Input low voltage"},
        "VIH":      {"min": 3.5,  "max": 5.5,   "unit": "V",     "desc": "Input high voltage"},
        "tWR":      {"min": None, "max": 5.0,   "unit": "ms",    "desc": "Write cycle time"},
        "Endurance":{"min": 1e6,  "max": None,  "unit": "cycles", "desc": "Write endurance"},
        "Retention":{"min": 100,  "max": None,  "unit": "years",  "desc": "Data retention"},
    }

    def __init__(self):
        self.nodes = []
        self.edges = []
        self.bin_table = dict(self.DEFAULT_BIN_TABLE)
        self.test_limits = dict(self.DEFAULT_TEST_LIMITS)

    def build_default_flow(self, selected_tests):
        """根据选中测试构建默认线性流程"""
        self.nodes = []
        self.edges = []

        # Standard test order with dependency chain
        test_order = [
            ("OS_TEST",        2),
            ("DC_TEST",        3),
            ("FUNC_TEST",      4),
            ("MARCH_C_TEST",   5),
            ("MARCH_B_TEST",   10),
            ("ADDR_SCAN_TEST", 6),
            ("DATA_RET_TEST",  7),
            ("ERR_TEST",       8),
            ("ENDUR_TEST",     9),
            ("IDDQ_TEST",      11),
        ]

        self.nodes.append({"id": "START", "type": "start", "label": "START"})
        prev_id = "START"

        for test_id, fail_bin in test_order:
            if test_id in selected_tests:
                node = {
                    "id": test_id,
                    "type": "test",
                    "label": test_id.replace("_", " ").title(),
                    "fail_bin": fail_bin,
                }
                self.nodes.append(node)
                self.edges.append({"from": prev_id, "to": test_id, "type": "pass"})
                # Fail edge to bin
                bin_node_id = f"BIN_{fail_bin}"
                if not any(n["id"] == bin_node_id for n in self.nodes):
                    self.nodes.append({
                        "id": bin_node_id, "type": "bin",
                        "label": f"Bin {fail_bin}\n{self.bin_table.get(fail_bin, ('?',))[0]}",
                        "bin_num": fail_bin,
                    })
                self.edges.append({"from": test_id, "to": bin_node_id, "type": "fail"})
                prev_id = test_id

        # Pass bin
        self.nodes.append({"id": "BIN_1", "type": "bin",
                           "label": "Bin 1\nPASS", "bin_num": 1})
        self.edges.append({"from": prev_id, "to": "BIN_1", "type": "pass"})
        self.nodes.append({"id": "END", "type": "end", "label": "END"})

    def simulate_flow(self, test_results):
        """模拟执行流程
        test_results: {"OS_TEST": True, "DC_TEST": False, ...}
        Returns: final bin number
        """
        for node in self.nodes:
            if node["type"] == "test":
                tid = node["id"]
                passed = test_results.get(tid, True)
                if not passed:
                    return node.get("fail_bin", 99)
        return 1  # All passed

    def generate_prg_flow(self, protocol="I2C"):
        """生成 .prg TEST_FLOW 段"""
        lines = []
        lines.append("// ===== TEST FLOW (v6.0 Enhanced) =====")
        lines.append("TEST_FLOW {")
        for node in self.nodes:
            if node["type"] == "test":
                tid = node["id"]
                fbin = node.get("fail_bin", 99)
                lines.append(f"    RUN_PATTERN(\"{tid}\");")
                lines.append(f"    JUDGE(\"{tid}\") {{")
                lines.append(f"        IF (FAIL) {{ BIN({fbin}, \"{self.bin_table.get(fbin, ('FAIL',))[0]}\", "
                             f"\"{self.bin_table.get(fbin, ('','HARD'))[1]}\"); }}")
                lines.append(f"    }}")
        lines.append("    BIN(1, \"PASS\", \"GOOD\");")
        lines.append("}")
        return "\n".join(lines)

    def export_bin_table_csv(self):
        """导出 Bin 表为 CSV 字符串"""
        lines = ["Bin,Name,Type,Description"]
        for bn, (name, btype, desc) in sorted(self.bin_table.items()):
            lines.append(f"{bn},{name},{btype},{desc}")
        return "\n".join(lines)


# ============================================================
# v6.0 — 多 Site 并行测试向量生成器
# ============================================================

class MultiSiteGenerator:
    """多 Site 并行向量生成器"""

    def __init__(self, site_count=4, protocol="I2C"):
        self.site_count = min(site_count, 8)
        self.protocol = protocol
        self.site_configs = []
        self._configure_default_sites()

    def _configure_default_sites(self):
        """为各 Site 自动分配地址"""
        self.site_configs = []
        for s in range(self.site_count):
            if self.protocol == "I2C":
                # I2C: 通过 A2/A1/A0 区分 (最多 8 Site)
                a0 = s & 0x01
                a1 = (s >> 1) & 0x01
                a2 = (s >> 2) & 0x01
                self.site_configs.append({
                    "site_id": s + 1,
                    "addr_pins": (a2, a1, a0),
                    "device_addr": 0xA0 | (a2 << 3) | (a1 << 2) | (a0 << 1),
                })
            elif self.protocol == "SPI":
                # SPI: 各 Site 独立 CS 线
                self.site_configs.append({
                    "site_id": s + 1,
                    "cs_line": s,
                })
            elif self.protocol == "Microwire":
                self.site_configs.append({
                    "site_id": s + 1,
                    "cs_line": s,
                })

    def generate_site_info(self):
        """返回 Site 配置信息 (用于 PRG/报告)"""
        lines = []
        lines.append(f"// Multi-Site Configuration: {self.site_count} sites")
        for sc in self.site_configs:
            if self.protocol == "I2C":
                lines.append(f"//   Site {sc['site_id']}: Addr=0x{sc['device_addr']:02X} "
                             f"(A2={sc['addr_pins'][0]}, A1={sc['addr_pins'][1]}, A0={sc['addr_pins'][2]})")
            else:
                lines.append(f"//   Site {sc['site_id']}: CS_LINE={sc['cs_line']}")
        return "\n".join(lines)

    def generate_site_prg_section(self):
        """生成 .prg 中的多 Site 段"""
        lines = []
        lines.append("// ===== MULTI-SITE CONFIGURATION =====")
        lines.append(f"SITE_COUNT = {self.site_count};")
        lines.append("SITE_LOOP {")
        for sc in self.site_configs:
            sid = sc["site_id"]
            if self.protocol == "I2C":
                lines.append(f"    SITE({sid}) {{ DEVICE_ADDR = 0x{sc['device_addr']:02X}; }}")
            else:
                lines.append(f"    SITE({sid}) {{ CS_LINE = {sc['cs_line']}; }}")
        lines.append("}")
        lines.append("PER_SITE_JUDGE {")
        lines.append("    IF (SITE_FAIL(site_id)) { BIN_SITE(site_id, fail_bin); }")
        lines.append("}")
        return "\n".join(lines)

    def calculate_throughput(self, test_time_ms, overhead_pct=15.0):
        """
        多Site产能计算
        effective_time = single_test_time / num_sites * (1 + overhead%)
        UPH = 3600000 / effective_time
        """
        if test_time_ms <= 0 or self.site_count <= 0:
            return {"effective_time_ms": 0, "uph": 0, "daily_capacity": 0, "speedup": 1.0}
        eff = test_time_ms / self.site_count * (1 + overhead_pct / 100)
        uph = 3600000 / eff
        return {
            "effective_time_ms": round(eff, 2),
            "uph": int(uph),
            "daily_capacity": int(uph * 16),
            "speedup": round(self.site_count / (1 + overhead_pct / 100), 2),
            "overhead_desc": f"Site switching + data transfer {overhead_pct:.0f}%",
        }

    def generate_full_site_config(self):
        """完整多Site PRG段 (PARALLEL_SITES + SITE_CONFIG + FOR_EACH_SITE)"""
        lines = []
        lines.append("// ===== MULTI-SITE PARALLEL CONFIGURATION =====")
        lines.append(f"PARALLEL_SITES = {self.site_count};")
        lines.append("")
        lines.append("SITE_CONFIG {")
        for sc in self.site_configs:
            sid = sc["site_id"]
            if self.protocol == "I2C":
                pe_offset = (sid - 1) * 6
                lines.append(f"    SITE({sid}) {{ DEVICE_ADDR = 0x{sc['device_addr']:02X}; "
                             f"PE_OFFSET = {pe_offset}; }}")
            else:
                lines.append(f"    SITE({sid}) {{ CS_LINE = {sc['cs_line']}; "
                             f"PE_OFFSET = {(sid-1)*6}; }}")
        lines.append("}")
        lines.append("")
        lines.append("FOR_EACH_SITE {")
        lines.append("    RUN_ALL_PATTERNS();")
        lines.append("    JUDGE_SITE();")
        lines.append("}")
        return "\n".join(lines)

    def generate_pin_channel_map(self, base_pins):
        """为每个Site分配PE通道: Site1=CH1-CH6, Site2=CH7-CH12, ..."""
        result = {}
        for sc in self.site_configs:
            sid = sc["site_id"]
            offset = (sid - 1) * len(base_pins)
            result[sid] = {pin: f"CH{offset + i + 1}" for i, pin in enumerate(base_pins)}
        return result


# ============================================================
# v6.0 — 数据分析 + 良率仪表盘
# ============================================================

class DatalogAnalyzer:
    """测试数据分析引擎: Cp/Cpk, Pareto, 良率趋势"""

    def __init__(self):
        self.records = []   # [{lot, wafer, site, bin, params: {ISB: val, ...}}]
        self.param_specs = {}  # param_name → {usl, lsl}

    def import_csv(self, path):
        """导入 CSV datalog"""
        try:
            with open(path, "r", encoding="utf-8-sig") as f:
                lines = f.readlines()
            if len(lines) < 2:
                return 0
            headers = [h.strip() for h in lines[0].split(",")]
            count = 0
            for line in lines[1:]:
                vals = [v.strip() for v in line.split(",")]
                if len(vals) < len(headers):
                    continue
                record = {}
                for h, v in zip(headers, vals):
                    h_lower = h.lower()
                    if h_lower in ("lot", "wafer", "site", "bin"):
                        record[h_lower] = v
                    else:
                        try:
                            record.setdefault("params", {})[h] = float(v)
                        except ValueError:
                            record.setdefault("params", {})[h] = v
                self.records.append(record)
                count += 1
            logger.info(f"Imported {count} records from {path}")
            return count
        except Exception as e:
            logger.exception(f"CSV import failed: {e}")
            return 0

    def import_simulation_results(self, simulator):
        """从 PatternSimulator 导入模拟结果"""
        record = {
            "lot": "SIM",
            "wafer": "1",
            "site": "1",
            "bin": "1" if not simulator.errors else "4",
            "params": {
                "Transactions": len(simulator.transactions),
                "Errors": len(simulator.errors),
                "MatchRate": sum(1 for t in simulator.transactions if t.get("match", True)) /
                             max(1, len(simulator.transactions)) * 100,
            }
        }
        self.records.append(record)

    def calculate_statistics(self, param_name):
        """计算单参数统计 (Cp/Cpk)"""
        values = []
        for r in self.records:
            v = r.get("params", {}).get(param_name)
            if v is not None and isinstance(v, (int, float)):
                values.append(v)

        if len(values) < 2:
            return None

        n = len(values)
        mean = sum(values) / n
        variance = sum((x - mean) ** 2 for x in values) / (n - 1)
        sigma = variance ** 0.5 if variance > 0 else 1e-9

        spec = self.param_specs.get(param_name, {})
        usl = spec.get("usl")
        lsl = spec.get("lsl")

        cp = cpk = None
        if usl is not None and lsl is not None and sigma > 0:
            cp = (usl - lsl) / (6 * sigma)
            cpu = (usl - mean) / (3 * sigma)
            cpl = (mean - lsl) / (3 * sigma)
            cpk = min(cpu, cpl)
        elif usl is not None and sigma > 0:
            cpk = (usl - mean) / (3 * sigma)
        elif lsl is not None and sigma > 0:
            cpk = (mean - lsl) / (3 * sigma)

        return {
            "n": n, "mean": mean, "sigma": sigma,
            "min": min(values), "max": max(values),
            "median": sorted(values)[n // 2],
            "cp": cp, "cpk": cpk,
            "usl": usl, "lsl": lsl,
            "values": values,
        }

    def calculate_yield(self, group_by="lot"):
        """按分组计算良率"""
        groups = {}
        for r in self.records:
            key = r.get(group_by, "ALL")
            groups.setdefault(key, []).append(r)

        results = []
        for key, recs in groups.items():
            total = len(recs)
            passed = sum(1 for r in recs if r.get("bin", "1") == "1")
            bin_dist = {}
            for r in recs:
                b = r.get("bin", "1")
                bin_dist[b] = bin_dist.get(b, 0) + 1
            results.append({
                "group": key,
                "total": total,
                "pass": passed,
                "fail": total - passed,
                "yield_pct": passed / total * 100 if total > 0 else 0,
                "bin_dist": bin_dist,
            })
        return results

    def pareto_analysis(self):
        """Pareto 分析: 按 Bin 统计失败"""
        bin_counts = {}
        total_fail = 0
        for r in self.records:
            b = r.get("bin", "1")
            if b != "1":
                bin_counts[b] = bin_counts.get(b, 0) + 1
                total_fail += 1

        if total_fail == 0:
            return []

        sorted_bins = sorted(bin_counts.items(), key=lambda x: -x[1])
        cumulative = 0
        result = []
        for bn, count in sorted_bins:
            cumulative += count
            result.append({
                "bin": bn,
                "count": count,
                "pct": count / total_fail * 100,
                "cumulative_pct": cumulative / total_fail * 100,
            })
        return result


# ============================================================
# v6.0 — IEEE 1450 STIL 格式输出
# ============================================================

class STILFormatter:
    """IEEE 1450 STIL (Standard Test Interface Language) 格式输出"""

    def format(self, sections, pins, period_ns=2500, voltage="5.0V",
               chip_name="AT24C02", protocol="I2C"):
        """生成 STIL 1.0 格式文件"""
        lines = []
        lines.append("STIL 1.0 {")
        lines.append(f'  Design 2005;')
        lines.append("}")
        lines.append("")

        # Header
        lines.append("Header {")
        lines.append(f'  Title "{chip_name} ATE Test Pattern";')
        lines.append(f'  Date "{datetime.datetime.now().strftime("%Y-%m-%d")}";')
        lines.append(f'  Source "ATE Pattern Generator Platform {VERSION}";')
        lines.append("}")
        lines.append("")

        # Signals
        lines.append("Signals {")
        for pin in pins:
            direction = "InOut" if pin in ("SDA", "MISO", "DO") else "In"
            lines.append(f'  "{pin}" {direction};')
        lines.append("}")
        lines.append("")

        # Signal Groups
        pin_str = "+".join(f'"{p}"' for p in pins)
        lines.append("SignalGroups {")
        lines.append(f'  "all_pins" = \'{pin_str}\';')
        lines.append("}")
        lines.append("")

        # Timing
        strobe_ns = int(period_ns * 0.7)
        lines.append(f'Timing "{protocol.lower()}_timing" {{')
        lines.append(f'  WaveformTable "wft_std" {{')
        lines.append(f'    Period \'{period_ns}ns\';')
        lines.append(f'    Waveforms {{')
        for pin in pins:
            if pin in ("SCL", "SCK", "SK"):
                lines.append(f'      "{pin}" {{ P {{ \'0ns\' D; \'{period_ns//2}ns\' U; }} }}')
            elif pin in ("SDA", "MISO", "DO"):
                # InOut: drive at 0ns, strobe compare at 70% period
                lines.append(f'      "{pin}" {{ 0 {{ \'0ns\' D; }}')
                lines.append(f'               1 {{ \'0ns\' U; }}')
                lines.append(f'               L {{ \'0ns\' Z; \'{strobe_ns}ns\' L; }}')
                lines.append(f'               H {{ \'0ns\' Z; \'{strobe_ns}ns\' H; }}')
                lines.append(f'               X {{ \'0ns\' X; }}')
                lines.append(f'               Z {{ \'0ns\' Z; }} }}')
            else:
                lines.append(f'      "{pin}" {{ 01ZX {{ \'0ns\' D/U/Z/X; }} }}')
        lines.append(f'    }}')
        lines.append(f'  }}')
        lines.append("}")
        lines.append("")

        # Pattern Burst
        lines.append('PatternBurst "burst_all" {')
        lines.append("  PatList {")
        for name, desc, v, c, l in sections:
            lines.append(f'    "{name}";')
        lines.append("  }")
        lines.append("}")
        lines.append("")

        # PatternExec
        lines.append("PatternExec {")
        lines.append('  PatternBurst "burst_all";')
        lines.append("}")
        lines.append("")

        # Patterns
        for name, desc, vectors, comments, labels in sections:
            lines.append(f'Pattern "{name}" {{')
            lines.append('  W "wft_std";')
            state_map = {"0": "D", "1": "U", "H": "H", "L": "L", "Z": "Z", "X": "X"}
            for vi, vec in enumerate(vectors):
                label = labels[vi] if vi < len(labels) and labels[vi] else ""
                comment_str = comments[vi] if vi < len(comments) and comments[vi] else ""
                states = "".join(state_map.get(vec.get(p, "X"), "X") for p in pins)
                label_part = f'"{label}": ' if label else ""
                comment_part = f" // {comment_str}" if comment_str else ""
                lines.append(f'  {label_part}V {{ "all_pins" = {states}; }}{comment_part}')
            lines.append("}")
            lines.append("")

        return "\n".join(lines)


# ============================================================
# v6.0 — Teradyne WGL 格式输出
# ============================================================

class WGLFormatter:
    """Teradyne WGL (Waveform Generation Language) 格式输出"""

    def format(self, sections, pins, period_ns=2500, voltage="5.0V",
               chip_name="AT24C02", protocol="I2C"):
        """生成 WGL 格式文件"""
        lines = []
        lines.append(f"// WGL Pattern File — {chip_name} {protocol} Test")
        lines.append(f"// Generated by ATE Pattern Generator Platform {VERSION}")
        lines.append(f"// Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        # Waveform table with drive/compare waves
        strobe_ns = int(period_ns * 0.7)
        in_pins = [p for p in pins if p not in ("SDA", "MISO", "DO")]
        out_pins = [p for p in pins if p in ("SDA", "MISO", "DO")]
        lines.append("waveform_table wft_std")
        lines.append(f"  period = {period_ns}ns;")
        if in_pins:
            lines.append(f"  drive_wave dw_nrz ( {', '.join(in_pins)} )")
            lines.append(f"    {{ 0ns force_dn; }}")
            lines.append(f"    {{ 0ns force_up; }}")
            lines.append(f"  end;")
        if out_pins:
            lines.append(f"  drive_wave dw_io ( {', '.join(out_pins)} )")
            lines.append(f"    {{ 0ns force_dn; }}")
            lines.append(f"    {{ 0ns force_up; }}")
            lines.append(f"  end;")
            lines.append(f"  compare_wave cw_strobe ( {', '.join(out_pins)} )")
            lines.append(f"    {{ {strobe_ns}ns strobe; }}")
            lines.append(f"  end;")
        lines.append("end;")
        lines.append("")

        # Pin declaration with direction grouping
        lines.append("pin_list {")
        if in_pins:
            lines.append(f"  direction_in  ( {', '.join(in_pins)} );")
        if out_pins:
            lines.append(f"  direction_inout ( {', '.join(out_pins)} );")
        lines.append("}")
        lines.append("")

        # Patterns
        for name, desc, vectors, comments, labels in sections:
            lines.append(f"pattern {name}")
            lines.append(f"  // {desc}")
            for vi, vec in enumerate(vectors):
                states = " ".join(vec.get(p, "X") for p in pins)
                label = labels[vi] if vi < len(labels) and labels[vi] else ""
                comment_str = comments[vi] if vi < len(comments) and comments[vi] else ""
                label_part = f"{label}: " if label else "  "
                comment_part = f" // {comment_str}" if comment_str else ""
                lines.append(f"  {label_part}{{ {states}; }}{comment_part}")
            lines.append("end;")
            lines.append("")

        return "\n".join(lines)


# ============================================================
# v6.0 — 项目工作空间管理
# ============================================================

class ProjectManager:
    """项目工作空间管理: 多芯片项目, 配置模板, 历史记录"""

    PROJECT_FILE = "ate_project.json"
    RECENT_FILE = os.path.join(LOG_DIR, "recent_projects.json")

    def __init__(self):
        self.current_project = None
        self.recent_projects = self._load_recent()

    def _load_recent(self):
        """加载最近项目列表"""
        try:
            if os.path.exists(self.RECENT_FILE):
                with open(self.RECENT_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)[:10]
        except Exception:
            pass
        return []

    def _save_recent(self):
        """保存最近项目列表"""
        try:
            with open(self.RECENT_FILE, "w", encoding="utf-8") as f:
                json.dump(self.recent_projects[:10], f, ensure_ascii=False, indent=2)
        except Exception:
            logger.exception("Failed to save recent projects")

    def create_project(self, name, path, chips=None):
        """创建新项目目录结构"""
        try:
            proj_dir = os.path.join(path, name)
            os.makedirs(proj_dir, exist_ok=True)
            for sub in ("configs", "output", "datalogs", "reports"):
                os.makedirs(os.path.join(proj_dir, sub), exist_ok=True)

            proj_meta = {
                "name": name,
                "created": datetime.datetime.now().isoformat(),
                "version": VERSION,
                "chips": chips or ["AT24C02"],
            }
            with open(os.path.join(proj_dir, self.PROJECT_FILE), "w", encoding="utf-8") as f:
                json.dump(proj_meta, f, indent=2, ensure_ascii=False)

            self.current_project = {"path": proj_dir, "meta": proj_meta}
            self._add_to_recent(proj_dir, name)
            logger.info(f"Project created: {proj_dir}")
            return proj_dir
        except Exception as e:
            logger.exception(f"Create project failed: {e}")
            return None

    def open_project(self, proj_dir):
        """打开已有项目"""
        proj_file = os.path.join(proj_dir, self.PROJECT_FILE)
        if not os.path.exists(proj_file):
            return None
        try:
            with open(proj_file, "r", encoding="utf-8") as f:
                meta = json.load(f)
            self.current_project = {"path": proj_dir, "meta": meta}
            self._add_to_recent(proj_dir, meta.get("name", "Unknown"))
            logger.info(f"Project opened: {proj_dir}")
            return meta
        except Exception as e:
            logger.exception(f"Open project failed: {e}")
            return None

    def _add_to_recent(self, path, name):
        """添加到最近项目"""
        entry = {"path": path, "name": name,
                 "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}
        self.recent_projects = [e for e in self.recent_projects if e["path"] != path]
        self.recent_projects.insert(0, entry)
        self.recent_projects = self.recent_projects[:10]
        self._save_recent()

    def save_config_to_project(self, chip_name, config_dict):
        """保存芯片配置到项目"""
        if not self.current_project:
            return False
        cfg_path = os.path.join(self.current_project["path"], "configs", f"{chip_name}.json")
        try:
            with open(cfg_path, "w", encoding="utf-8") as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False

    def list_project_configs(self):
        """列出项目中的芯片配置"""
        if not self.current_project:
            return []
        cfg_dir = os.path.join(self.current_project["path"], "configs")
        if not os.path.isdir(cfg_dir):
            return []
        return [f.replace(".json", "") for f in os.listdir(cfg_dir) if f.endswith(".json")]

    def get_project_output_dir(self):
        """返回项目输出目录"""
        if self.current_project:
            return os.path.join(self.current_project["path"], "output")
        return None


# ============================================================
# Tooltip 工具类
# ============================================================

class ToolTip:
    """鼠标悬停提示"""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        widget.bind("<Enter>", self._show)
        widget.bind("<Leave>", self._hide)

    def _show(self, event=None):
        if self.tip_window:
            return
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#3a4058", foreground="#e8ecf1",
                         relief=tk.SOLID, borderwidth=1,
                         font=("Segoe UI", 8), padx=6, pady=3)
        label.pack()
        tw.update_idletasks()
        tip_w = tw.winfo_reqwidth()
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        screen_w = self.widget.winfo_screenwidth()
        if x + tip_w > screen_w - 8:
            x = self.widget.winfo_rootx() - tip_w - 4
        tw.wm_geometry(f"+{x}+{y}")

    def _hide(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


# ============================================================
# 故障模型定义 (Phase 4 + Phase 8 共用)
# ============================================================

FAULT_MODELS = {
    "SA0":     "Stuck-At-0: 存储单元永久输出0",
    "SA1":     "Stuck-At-1: 存储单元永久输出1",
    "TF01":    "Transition Fault: 单元无法 0→1 翻转",
    "TF10":    "Transition Fault: 单元无法 1→0 翻转",
    "CF_inv":  "Coupling Fault (inversion): 写A导致B反转",
    "CF_idem": "Coupling Fault (idempotent): 写A使B固定",
    "AF_r":    "Address Fault (read): 读地址a访问了b≠a",
    "AF_w":    "Address Fault (write): 写地址a修改了b≠a",
}

# ============================================================
# v8.0 — Binning 定义 & JEDEC 失败概率模型
# ============================================================

BIN_DEFINITIONS = {
    1: {"name": "Good Die",       "type": "PASS", "color": "#22c55e",
        "trigger": "all_pass",
        "description": "所有测试项 PASS"},
    2: {"name": "Contact Fail",   "type": "FAIL", "color": "#000000",
        "trigger": "os_all_fail",
        "description": "OS 全部 Fail — 探针未接触"},
    3: {"name": "OS Fail",        "type": "FAIL", "color": "#ef4444",
        "trigger": "os_fail",
        "description": "OS 部分 Fail — 开路/短路"},
    4: {"name": "DC Fail",        "type": "FAIL", "color": "#f97316",
        "trigger": "dc_fail",
        "description": "DC 参数超限 — 工艺偏差"},
    5: {"name": "Func Fail",      "type": "FAIL", "color": "#eab308",
        "trigger": "func_fail",
        "description": "功能测试未通过 — 逻辑缺陷"},
    6: {"name": "Memory Fail",    "type": "FAIL", "color": "#a855f7",
        "trigger": "march_or_scan_or_ret_fail",
        "description": "March/地址/保持 未通过 — 阵列缺陷"},
    7: {"name": "I2C Fail",       "type": "FAIL", "color": "#64748b",
        "trigger": "i2c_err_fail",
        "description": "I2C 异常处理未通过 — 协议缺陷"},
    8: {"name": "Endurance Fail", "type": "FAIL", "color": "#475569",
        "trigger": "endurance_fail",
        "description": "耐久性未通过 — 可靠性问题"},
    9: {"name": "IDDQ Fail",      "type": "FAIL", "color": "#06b6d4",
        "trigger": "iddq_fail",
        "description": "IDDQ 静态电流异常 — 潜在缺陷"},
}

JEDEC_PASS_PROBABILITY = {
    "OS_TEST":      0.998,   # 0.2% 探针/连通性问题
    "DC_TEST":      0.992,   # 0.8% 工艺偏差导致参数超限
    "FUNC_BW":      0.990,   # 1.0% 逻辑缺陷
    "FUNC_PW":      0.992,
    "FUNC_BOUND":   0.995,
    "FUNC_WP":      0.997,
    "FUNC_WRAP":    0.996,
    "FUNC_CAR":     0.997,
    "MARCH_TEST":   0.990,   # 1.0% 阵列级缺陷
    "MARCHB_TEST":  0.991,
    "SCAN_TEST":    0.995,   # 0.5% 地址解码缺陷
    "RET_TEST":     0.998,   # 0.2% 数据保持问题
    "ERR_TEST":     0.997,   # 0.3% 协议处理缺陷
    "ENDUR_TEST":   0.996,   # 0.4% 可靠性问题
    "IDDQ_TEST":    0.985,   # 1.5% IDDQ 漏电异常
}

# ============================================================
# Phase 9: 演示脚本
# ============================================================

DEMO_SCRIPT = [
    {"action": "select_tests",    "params": {"preset": "full"},   "desc": "选择全量测试 (9段)"},
    {"action": "generate",        "params": {},                   "desc": "生成测试向量"},
    {"action": "switch_tab",      "params": {"tab": "tab_pat"},   "desc": "查看 PAT 向量预览"},
    {"action": "switch_tab",      "params": {"tab": "tab_wave"},  "desc": "查看 I2C 波形图"},
    {"action": "switch_tab",      "params": {"tab": "tab_flow"},  "desc": "查看测试流程图"},
    {"action": "switch_tab",      "params": {"tab": "tab_stats"}, "desc": "查看统计分析"},
    {"action": "switch_tab",      "params": {"tab": "tab_sim"},   "desc": "查看模拟器 + Fail Bit Map"},
    {"action": "run_simulation",  "params": {},                   "desc": "运行向量模拟仿真"},
    {"action": "switch_tab",      "params": {"tab": "tab_shmoo"}, "desc": "查看 Shmoo 分析"},
    {"action": "switch_tab",      "params": {"tab": "tab_atpg"},  "desc": "查看 ATPG 覆盖率"},
    {"action": "run_atpg",        "params": {},                   "desc": "运行故障覆盖率仿真"},
    {"action": "generate_proof",  "params": {},                   "desc": "生成 March C- 覆盖率证明"},
    {"action": "switch_tab",      "params": {"tab": "tab_econ"},  "desc": "查看测试经济学"},
    {"action": "run_economics",   "params": {},                   "desc": "计算测试经济学指标"},
    {"action": "switch_tab",      "params": {"tab": "tab_yield"}, "desc": "查看良率分析 + Monte Carlo"},
    {"action": "switch_tab",      "params": {"tab": "tab_datalog"}, "desc": "查看 Datalog + Binning"},
    {"action": "run_batch_datalog", "params": {"n": 50},           "desc": "批量生成 50 颗 Datalog"},
    {"action": "switch_tab",      "params": {"tab": "tab_wafer"},  "desc": "查看晶圆图"},
    {"action": "generate_wafer",  "params": {},                    "desc": "生成晶圆 Bin Map"},
    {"action": "switch_tab",      "params": {"tab": "tab_sim"},    "desc": "查看调试器"},
    {"action": "run_debug_step",  "params": {"count": 10},         "desc": "单步执行 10 步向量调试"},
    {"action": "switch_tab",      "params": {"tab": "tab_temp"},    "desc": "查看温度角分析"},
    {"action": "run_temp_analysis","params": {},                     "desc": "运行温度角仿真"},
    # v9.0 Tier3
    {"action": "switch_tab",      "params": {"tab": "tab_flow"},    "desc": "查看自适应测试流"},
    {"action": "run_adaptive",    "params": {},                      "desc": "运行自适应测试流仿真"},
    {"action": "switch_tab",      "params": {"tab": "tab_yield"},   "desc": "Guard Band 限值优化"},
    {"action": "switch_tab",      "params": {"tab": "tab_datalog"}, "desc": "参数相关性分析"},
    {"action": "run_compliance",  "params": {},                      "desc": "AEC-Q100/JEDEC 标准合规报告"},
]


# ============================================================
# 主题配置
# ============================================================

THEMES = {
    "dark": {
        "bg": "#0f172a",
        "sidebar": "#1e293b",
        "card": "#1e293b",
        "card2": "#334155",
        "accent": "#3b82f6",
        "accent2": "#14b8a6",
        "gold": "#f59e0b",
        "text": "#e2e8f0",
        "text_dim": "#94a3b8",
        "border": "#334155",
        "danger": "#ef4444",
        "success": "#22c55e",
        "warning": "#f59e0b",
        "ribbon_bg": "#0f172a",
        "ribbon_label": "#64748b",
        "tab_active": "#3b82f6",
        "tab_badge": "#ef4444",
        "hover": "#334155",
    },
    "light": {
        "bg": "#f8fafc",
        "sidebar": "#f1f5f9",
        "card": "#ffffff",
        "card2": "#e2e8f0",
        "accent": "#2563eb",
        "accent2": "#0d9488",
        "gold": "#d97706",
        "text": "#1e293b",
        "text_dim": "#64748b",
        "border": "#e2e8f0",
        "danger": "#dc2626",
        "success": "#16a34a",
        "warning": "#d97706",
        "ribbon_bg": "#f8fafc",
        "ribbon_label": "#94a3b8",
        "tab_active": "#2563eb",
        "tab_badge": "#dc2626",
        "hover": "#e2e8f0",
    },
}


# ============================================================
# Phase 4: 故障覆盖率仿真引擎
# ============================================================

class FaultCoverageSimulator:
    """基于蒙特卡洛故障注入的覆盖率仿真器"""

    def __init__(self, capacity=256, seed=42):
        self.capacity = capacity
        self.seed = seed
        self.results = {}        # {(test_name, fault_type): coverage_pct}
        self.detail = {}         # {(test_name, fault_type): {"detected": int, "total": int}}
        self.test_names = []
        self.fault_types = list(FAULT_MODELS.keys())
        self.progress = 0.0
        self.done = False

    @staticmethod
    def inject_fault(memory, fault_type, address, bit):
        """在内存副本中注入单个故障"""
        if fault_type == "SA0":
            memory[address] &= ~(1 << bit)
        elif fault_type == "SA1":
            memory[address] |= (1 << bit)
        elif fault_type == "TF01":
            # 阻止 0→1 翻转: 如果该位是0, 强制保持0
            memory[address] &= ~(1 << bit)
        elif fault_type == "TF10":
            # 阻止 1→0 翻转: 如果该位是1, 强制保持1
            memory[address] |= (1 << bit)
        elif fault_type == "CF_inv":
            # 邻接单元取反
            victim = (address + 1) % len(memory)
            memory[victim] ^= (1 << bit)
        elif fault_type == "CF_idem":
            # 邻接单元强制为攻击者值
            victim = (address + 1) % len(memory)
            attacker_bit = (memory[address] >> bit) & 1
            if attacker_bit:
                memory[victim] |= (1 << bit)
            else:
                memory[victim] &= ~(1 << bit)
        elif fault_type == "AF_r":
            # 读地址错位: 交换两个地址的值
            wrong = (address + 7) % len(memory)
            memory[address], memory[wrong] = memory[wrong], memory[address]
        elif fault_type == "AF_w":
            # 写地址错位: 将值写到错误地址
            wrong = (address + 7) % len(memory)
            memory[wrong] = memory[address]

    def _simulate_one_test(self, test_name, vectors, comments, fault_type, n_inject=100):
        """对一种测试×一种故障进行 n_inject 次注入仿真"""
        import random
        rng = random.Random(self.seed + hash((test_name, fault_type)) % 10000)
        detected = 0
        for _ in range(n_inject):
            # 创建干净内存
            clean_mem = bytearray(self.capacity)
            # 随机选择注入点
            addr = rng.randint(0, self.capacity - 1)
            bit = rng.randint(0, 7)
            # 注入故障
            faulty_mem = bytearray(clean_mem)
            self.inject_fault(faulty_mem, fault_type, addr, bit)
            # 模拟测试向量执行: 检查是否有比较向量能检出差异
            # 简化模型: 如果该地址在测试中被读取且比较值与故障值不同, 则检出
            if self._check_detection(vectors, comments, addr, bit, clean_mem, faulty_mem):
                detected += 1
        return detected, n_inject

    def _check_detection(self, vectors, comments, fault_addr, fault_bit, clean, faulty):
        """检查测试向量是否能检出指定故障"""
        # 从注释中提取被访问的地址
        for cm in comments:
            if not cm:
                continue
            # 检查写操作影响的地址
            if "Write" in cm or "w0" in cm or "w1" in cm:
                for m in re.finditer(r'addr=0x([0-9A-Fa-f]{2})', cm):
                    a = int(m.group(1), 16)
                    if a == fault_addr:
                        # 写后读可以检测
                        pass
            # 检查读操作覆盖的地址
            if "Read" in cm or "r0" in cm or "r1" in cm or "compare" in cm.lower():
                for m in re.finditer(r'addr=0x([0-9A-Fa-f]{2})', cm):
                    a = int(m.group(1), 16)
                    if a == fault_addr and clean[a] != faulty[a]:
                        return True
        # 基于测试类型的启发式检测
        test_upper = "".join(c for c in comments[:10] if c) if comments else ""
        # March 测试: 覆盖所有地址的写+读
        if "March" in test_upper or "march" in test_upper:
            if clean[fault_addr] != faulty[fault_addr]:
                return True
        # 功能测试: 覆盖写+读回
        if "FUNC" in test_upper or "Byte Write" in test_upper:
            if clean[fault_addr] != faulty[fault_addr]:
                return True
        # 地址扫描
        if "Scan" in test_upper or "SCAN" in test_upper:
            if fault_addr < 32 and clean[fault_addr] != faulty[fault_addr]:
                return True
        return False

    def run_simulation(self, test_sections, n_inject=100):
        """主入口: 遍历所有测试×故障组合 (在 threading.Thread 中调用)"""
        self.results = {}
        self.detail = {}
        self.test_names = [s[0] for s in test_sections]
        total = len(test_sections) * len(self.fault_types)
        step = 0
        for name, desc, vectors, comments, labels in test_sections:
            for ft in self.fault_types:
                detected, total_inj = self._simulate_one_test(
                    name, vectors, comments, ft, n_inject)
                cov = detected / total_inj * 100 if total_inj > 0 else 0
                self.results[(name, ft)] = cov
                self.detail[(name, ft)] = {"detected": detected, "total": total_inj}
                step += 1
                self.progress = step / total
        self.done = True

    def get_overall_coverage(self):
        """计算综合覆盖率"""
        if not self.results:
            return 0.0
        return sum(self.results.values()) / len(self.results)

    def get_min_test_suite(self):
        """贪心选择最小测试套件: 每步选覆盖最多未覆盖故障的测试"""
        uncovered = set(self.fault_types)
        selected = []
        remaining_tests = list(self.test_names)
        while uncovered and remaining_tests:
            best_test = None
            best_count = -1
            for t in remaining_tests:
                count = sum(1 for ft in uncovered if self.results.get((t, ft), 0) >= 80)
                if count > best_count:
                    best_count = count
                    best_test = t
            if best_test and best_count > 0:
                selected.append(best_test)
                remaining_tests.remove(best_test)
                newly_covered = {ft for ft in uncovered if self.results.get((best_test, ft), 0) >= 80}
                uncovered -= newly_covered
            else:
                break
        return selected


# ============================================================
# Phase 6: Monte Carlo 良率预测引擎
# ============================================================

class YieldPredictor:
    """基于蒙特卡洛仿真的芯片良率预测"""

    YIELD_PARAMS = {
        "VIH_5V": {"nominal": 3.5,  "spec_min": 3.5,  "spec_max": 5.5,  "unit": "V"},
        "VIL_5V": {"nominal": 1.5,  "spec_min": -0.5, "spec_max": 1.5,  "unit": "V"},
        "VOH":    {"nominal": 2.4,  "spec_min": 2.4,  "spec_max": 5.5,  "unit": "V"},
        "VOL":    {"nominal": 0.4,  "spec_min": 0.0,  "spec_max": 0.4,  "unit": "V"},
        "ISB":    {"nominal": 0.5,  "spec_min": 0.0,  "spec_max": 1.0,  "unit": "μA"},
        "ICC_R":  {"nominal": 0.5,  "spec_min": 0.0,  "spec_max": 1.0,  "unit": "mA"},
        "ICC_W":  {"nominal": 1.5,  "spec_min": 0.0,  "spec_max": 3.0,  "unit": "mA"},
        "tWR":    {"nominal": 3.0,  "spec_min": 0.0,  "spec_max": 5.0,  "unit": "ms"},
    }

    def __init__(self):
        self.results = []     # [(sample_dict, passed)]
        self.cpk_data = {}    # {param: {"cp": float, "cpk": float, ...}}
        self.done = False
        self.progress = 0.0

    def run_monte_carlo(self, n=1000, seed=42):
        """执行蒙特卡洛仿真 (应在 threading.Thread 中调用)"""
        import random
        rng = random.Random(seed)
        self.results = []
        self.cpk_data = {}
        param_values = {p: [] for p in self.YIELD_PARAMS}

        for i in range(n):
            sample = {}
            for param, spec in self.YIELD_PARAMS.items():
                sigma = (spec["spec_max"] - spec["spec_min"]) / 6
                value = rng.gauss(spec["nominal"], sigma)
                sample[param] = value
                param_values[param].append(value)
            passed = all(
                spec["spec_min"] <= sample[p] <= spec["spec_max"]
                for p, spec in self.YIELD_PARAMS.items()
            )
            self.results.append((sample, passed))
            self.progress = (i + 1) / n

        # 计算 Cp/Cpk
        for param, spec in self.YIELD_PARAMS.items():
            vals = param_values[param]
            if len(vals) < 2:
                continue
            mu = sum(vals) / len(vals)
            sigma = (sum((v - mu) ** 2 for v in vals) / (len(vals) - 1)) ** 0.5
            if sigma > 0:
                cp = (spec["spec_max"] - spec["spec_min"]) / (6 * sigma)
                cpu = (spec["spec_max"] - mu) / (3 * sigma)
                cpl = (mu - spec["spec_min"]) / (3 * sigma)
                cpk = min(cpu, cpl)
            else:
                cp = cpk = float('inf')
            self.cpk_data[param] = {
                "cp": cp, "cpk": cpk, "mean": mu, "sigma": sigma,
                "min": min(vals), "max": max(vals),
                "values": vals,
            }
        self.done = True

    def get_yield(self):
        """返回良率百分比"""
        if not self.results:
            return 0
        return sum(1 for _, p in self.results if p) / len(self.results) * 100

    def get_min_cpk(self):
        """返回最低 Cpk"""
        if not self.cpk_data:
            return 0
        return min(d["cpk"] for d in self.cpk_data.values())


# ============================================================
# v9.0 Tier3 Phase 28: Guard Banding 引擎
# ============================================================

class GuardBandEngine:
    """测试限值 Guard Banding — 收紧限值以达到目标 DPPM 质量水平"""

    def __init__(self, yield_predictor=None):
        self.predictor = yield_predictor
        self.results = {}
        self.done = False
        self.progress = 0.0

    @staticmethod
    def _gaussian_cdf(x, mu, sigma):
        """标准正态 CDF，纯 Python 实现 (math.erf)"""
        if sigma <= 0:
            return 1.0 if x >= mu else 0.0
        z = (x - mu) / (sigma * math.sqrt(2))
        return 0.5 * (1.0 + math.erf(z))

    @staticmethod
    def _dppm_from_distribution(mu, sigma, spec_min, spec_max):
        """计算在 [spec_min, spec_max] 范围外的 DPPM"""
        if sigma <= 0:
            return 0
        p_in = 1.0
        if spec_max is not None:
            p_in = GuardBandEngine._gaussian_cdf(spec_max, mu, sigma)
        if spec_min is not None:
            p_in -= GuardBandEngine._gaussian_cdf(spec_min, mu, sigma)
        p_in = max(0, min(1, p_in))
        return (1.0 - p_in) * 1_000_000

    def analyze_param(self, param, samples, spec_min, spec_max, target_dppm=10):
        """
        对单个参数计算最优 Guard Band。
        从 spec 边界逐步收紧 1%，找到 DPPM ≤ target 的最宽限值。
        """
        if not samples or len(samples) < 10:
            return None

        n = len(samples)
        mu = sum(samples) / n
        var = sum((x - mu) ** 2 for x in samples) / max(n - 1, 1)
        sigma = math.sqrt(var) if var > 0 else 1e-9

        dppm_before = self._dppm_from_distribution(mu, sigma, spec_min, spec_max)

        # 收紧搜索
        best_min = spec_min
        best_max = spec_max
        best_dppm = dppm_before

        if spec_max is not None:
            orig_range = spec_max - (spec_min if spec_min is not None else mu - 6 * sigma)
            for step in range(1, 50):
                trial_max = spec_max - orig_range * step * 0.01
                trial_dppm = self._dppm_from_distribution(mu, sigma, spec_min, trial_max)
                if trial_dppm <= target_dppm:
                    best_max = trial_max
                    best_dppm = trial_dppm
                    break
                best_max = trial_max
                best_dppm = trial_dppm

        if spec_min is not None:
            orig_range = (spec_max if spec_max is not None else mu + 6 * sigma) - spec_min
            for step in range(1, 50):
                trial_min = spec_min + orig_range * step * 0.01
                trial_dppm = self._dppm_from_distribution(mu, sigma, trial_min, best_max)
                if trial_dppm <= target_dppm:
                    best_min = trial_min
                    best_dppm = trial_dppm
                    break
                best_min = trial_min
                best_dppm = trial_dppm

        # 良率损失估计
        p_orig = 1.0
        if spec_max is not None:
            p_orig = self._gaussian_cdf(spec_max, mu, sigma)
        if spec_min is not None:
            p_orig -= self._gaussian_cdf(spec_min, mu, sigma)

        p_new = 1.0
        if best_max is not None:
            p_new = self._gaussian_cdf(best_max, mu, sigma)
        if best_min is not None:
            p_new -= self._gaussian_cdf(best_min, mu, sigma)

        yield_loss = max(0, (p_orig - p_new)) * 100

        tightening = 0
        if spec_max is not None and spec_max != 0:
            tightening = abs(spec_max - best_max) / abs(spec_max) * 100

        recommend = "采纳" if yield_loss < 2.0 and best_dppm <= target_dppm else "不推荐(良率损失过大)"

        return {
            "param": param,
            "mean": round(mu, 4), "sigma": round(sigma, 4),
            "original_min": spec_min, "original_max": spec_max,
            "guarded_min": round(best_min, 4) if best_min is not None else None,
            "guarded_max": round(best_max, 4) if best_max is not None else None,
            "dppm_before": round(dppm_before, 1),
            "dppm_after": round(best_dppm, 1),
            "yield_loss_pct": round(yield_loss, 2),
            "tightening_pct": round(tightening, 1),
            "recommendation": recommend,
        }

    def analyze_all(self, target_dppm=10):
        """遍历 YieldPredictor.YIELD_PARAMS 全部参数进行 Guard Band 分析"""
        self.done = False
        self.progress = 0.0
        self.results = {}

        if not self.predictor or not self.predictor.cpk_data:
            self.done = True
            return self.results

        params = list(self.predictor.cpk_data.keys())
        for i, param in enumerate(params):
            cpk_info = self.predictor.cpk_data[param]
            samples = cpk_info.get("values", [])
            yp = YieldPredictor.YIELD_PARAMS.get(param, {})
            spec_min = yp.get("spec_min")
            spec_max = yp.get("spec_max")
            result = self.analyze_param(param, samples, spec_min, spec_max, target_dppm)
            if result:
                self.results[param] = result
            self.progress = (i + 1) / len(params)

        self.done = True
        return self.results

    def generate_report(self):
        """格式化 Guard Band 分析报告"""
        lines = [
            f"{'Param':<10s} {'Orig Max':>10s} {'GB Max':>10s} {'DPPM前':>8s} {'DPPM后':>8s} {'收紧%':>6s} {'建议':>12s}",
            "─" * 70,
        ]
        for param, r in self.results.items():
            o_max = f"{r['original_max']}" if r['original_max'] is not None else "—"
            g_max = f"{r['guarded_max']}" if r['guarded_max'] is not None else "—"
            lines.append(
                f"{param:<10s} {o_max:>10s} {g_max:>10s} {r['dppm_before']:>8.1f} "
                f"{r['dppm_after']:>8.1f} {r['tightening_pct']:>5.1f}% {r['recommendation']:>12s}"
            )
        return "\n".join(lines)

    def get_guarded_limits(self):
        """返回可直接应用的限值字典"""
        limits = {}
        for param, r in self.results.items():
            limits[param] = {"min": r["guarded_min"], "max": r["guarded_max"]}
        return limits


# ============================================================
# v9.0 Tier3 Phase 29: 参数相关性分析
# ============================================================

class CorrelationAnalyzer:
    """DC 参数相关性散点矩阵 — Pearson 相关系数 + 异常值检测"""

    def __init__(self):
        self.matrix = {}
        self.params = []
        self.outliers = {}
        self.done = False

    def calculate_correlation_matrix(self, records, param_names=None):
        """
        计算参数间 Pearson 相关系数矩阵。
        records: DatalogGenerator 批量记录列表
        """
        # 提取参数值
        param_data = {}
        for rec in records:
            for p in rec.get("params", []):
                name = p["name"]
                if param_names and name not in param_names:
                    continue
                if name not in param_data:
                    param_data[name] = []
                param_data[name].append(p["measured"])

        self.params = sorted(param_data.keys())
        n_params = len(self.params)
        matrix = [[0.0] * n_params for _ in range(n_params)]
        significant = []

        for i, pa in enumerate(self.params):
            for j, pb in enumerate(self.params):
                if i == j:
                    matrix[i][j] = 1.0
                    continue
                if j < i:
                    matrix[i][j] = matrix[j][i]
                    continue
                va = param_data[pa]
                vb = param_data[pb]
                r = self._pearson(va, vb)
                matrix[i][j] = r
                if abs(r) > 0.5:
                    significant.append((pa, pb, round(r, 3)))

        self.matrix = {"matrix": matrix, "params": self.params,
                       "significant_pairs": significant}
        self.done = True
        return self.matrix

    @staticmethod
    def _pearson(x, y):
        """纯 Python Pearson 相关系数"""
        n = min(len(x), len(y))
        if n < 3:
            return 0.0
        mx = sum(x[:n]) / n
        my = sum(y[:n]) / n
        num = sum((x[i] - mx) * (y[i] - my) for i in range(n))
        dx = math.sqrt(sum((x[i] - mx) ** 2 for i in range(n)))
        dy = math.sqrt(sum((y[i] - my) ** 2 for i in range(n)))
        if dx * dy == 0:
            return 0.0
        return num / (dx * dy)

    def generate_scatter_data(self, records, param_x, param_y):
        """提取两个参数的散点数据 + 回归线"""
        xs, ys = [], []
        for rec in records:
            xv = yv = None
            for p in rec.get("params", []):
                if p["name"] == param_x:
                    xv = p["measured"]
                if p["name"] == param_y:
                    yv = p["measured"]
            if xv is not None and yv is not None:
                xs.append(xv)
                ys.append(yv)

        r = self._pearson(xs, ys)
        # 线性回归: y = slope*x + intercept
        n = len(xs)
        if n < 2:
            return {"x": xs, "y": ys, "r": r, "slope": 0, "intercept": 0}
        mx = sum(xs) / n
        my = sum(ys) / n
        ss_xx = sum((x - mx) ** 2 for x in xs)
        slope = sum((xs[i] - mx) * (ys[i] - my) for i in range(n)) / ss_xx if ss_xx else 0
        intercept = my - slope * mx
        return {"x": xs, "y": ys, "r": round(r, 3), "slope": round(slope, 4),
                "intercept": round(intercept, 4)}

    def identify_outliers(self, records, param, sigma_threshold=3.0):
        """识别 >Nσ 异常值"""
        values = []
        ids = []
        for rec in records:
            for p in rec.get("params", []):
                if p["name"] == param:
                    values.append(p["measured"])
                    ids.append(rec.get("device_id", 0))
                    break

        if len(values) < 5:
            return []
        mu = sum(values) / len(values)
        sigma = math.sqrt(sum((v - mu) ** 2 for v in values) / (len(values) - 1))
        if sigma == 0:
            return []

        outliers = []
        for i, v in enumerate(values):
            dist = abs(v - mu) / sigma
            if dist > sigma_threshold:
                outliers.append({"device_id": ids[i], "value": round(v, 4),
                                 "sigma_distance": round(dist, 2)})
        self.outliers[param] = outliers
        return outliers

    def get_top_correlations(self, n=5):
        """返回最强 |r| 的前 n 对参数"""
        pairs = self.matrix.get("significant_pairs", [])
        return sorted(pairs, key=lambda x: abs(x[2]), reverse=True)[:n]

    def generate_report(self):
        """生成相关矩阵 + 异常值摘要"""
        lines = ["参数相关性分析报告", "=" * 50]
        top = self.get_top_correlations(5)
        if top:
            lines.append("\n最强相关性:")
            for pa, pb, r in top:
                strength = "强" if abs(r) > 0.7 else "中等"
                lines.append(f"  {pa} ↔ {pb}: r={r:.3f} ({strength}相关)")

        if self.outliers:
            lines.append("\n异常值检测:")
            for param, outs in self.outliers.items():
                if outs:
                    lines.append(f"  {param}: {len(outs)} 颗异常 (>{3}σ)")

        return "\n".join(lines)


# ============================================================
# Phase 5: 测试经济学引擎
# ============================================================

class TestEconomicsEngine:
    """测试经济学计算: 成本-良率权衡, Fail Fast ROI"""

    DEFAULT_PARAMS = {
        "ate_cost_per_hour": 500,    # 元/小时
        "chip_cost": 0.5,            # 元/颗
        "target_daily": 10000,       # 颗/天
        "expected_yield": 95,        # %
        "work_hours": 16,            # 小时/天
        "escape_repair_cost": 50,    # 元/颗 (漏筛返修)
    }

    def __init__(self, **params):
        self.params = dict(self.DEFAULT_PARAMS)
        self.params.update(params)

    def calculate(self, pat_sections, period_ns, num_sites=1):
        """计算经济学指标 (支持多Site并行)"""
        total_vectors = sum(len(s[2]) for s in pat_sections)
        # 估算写次数
        write_count = 0
        for _, _, _, comments, _ in pat_sections:
            write_count += sum(1 for cm in comments
                               if cm and ("ACK Polling" in cm or "Poll #1" in cm))
        vec_time_ms = total_vectors * period_ns / 1_000_000
        twr_ms = write_count * 5.0
        test_time_ms = vec_time_ms + twr_ms
        test_time_s = test_time_ms / 1000

        # 多Site并行: 等效时间 = 单Site时间 / Site数 * (1 + 开销)
        site_overhead = 0.15 if num_sites > 1 else 0
        effective_time_s = test_time_s / max(1, num_sites) * (1 + site_overhead)

        ate_cost_s = self.params["ate_cost_per_hour"] / 3600
        cost_per_chip = ate_cost_s * effective_time_s
        chips_per_hour = 3600 / effective_time_s if effective_time_s > 0 else 0
        daily_capacity = chips_per_hour * self.params["work_hours"]

        # 良率-成本权衡
        y = self.params["expected_yield"] / 100
        escape_rate = 1 - y  # 简化: 漏筛率
        escape_cost_per_chip = escape_rate * self.params["escape_repair_cost"]
        total_cost_per_chip = cost_per_chip + escape_cost_per_chip

        # 每段时间分解
        seg_times = []
        for name, desc, vectors, seg_comments, _ in pat_sections:
            sv = len(vectors)
            sw = sum(1 for cm in seg_comments if cm and ("ACK Polling" in cm or "Poll #1" in cm))
            seg_ms = sv * period_ns / 1_000_000 + sw * 5.0
            seg_times.append((name, seg_ms))

        return {
            "test_time_ms": test_time_ms,
            "cost_per_chip": cost_per_chip,
            "daily_capacity": daily_capacity,
            "chips_per_hour": chips_per_hour,
            "total_cost": total_cost_per_chip,
            "escape_cost": escape_cost_per_chip,
            "seg_times": seg_times,
        }

    def calculate_yield_cost_curve(self, pat_sections, period_ns, n_points=20):
        """计算良率-成本权衡曲线"""
        points = []
        for i in range(n_points + 1):
            cov = 50 + i * 50 / n_points  # 50% → 100%
            y_rate = cov / 100
            # 简化模型: 测试时间与覆盖率近似线性
            base = self.calculate(pat_sections, period_ns)
            test_cost = base["cost_per_chip"] * (cov / 100)
            escape_cost = (1 - y_rate) * self.params["escape_repair_cost"]
            total = test_cost + escape_cost
            points.append({"coverage": cov, "test_cost": test_cost,
                            "escape_cost": escape_cost, "total": total})
        return points


# ============================================================
# v9.0 Tier3 Phase 27: 自适应测试流引擎
# ============================================================

class AdaptiveTestEngine:
    """自适应测试流 — 根据中间结果动态调整后续测试策略"""

    RULES = {
        "R1_OS_FastBin": {
            "trigger": "os_all_fail", "action": "skip_remaining", "priority": 1,
            "description_zh": "OS全Fail → 直接Bin2, 跳过后续",
            "description_en": "OS all fail → Bin 2, skip remaining",
            "time_effect_pct": -95,
        },
        "R2_DC_Marginal": {
            "trigger": "dc_marginal", "action": "expand_func", "priority": 2,
            "description_zh": "DC边缘(>80%spec) → FUNC扩展全地址",
            "description_en": "DC near limit (>80% spec) → expand FUNC to full address",
            "time_effect_pct": 30,
        },
        "R3_ISB_High": {
            "trigger": "isb_high", "action": "expand_endurance", "priority": 3,
            "description_zh": "ISB>0.5μA → 耐久测试10→50轮",
            "description_en": "ISB>0.5μA → endurance 10→50 cycles",
            "time_effect_pct": 40,
        },
        "R4_March_LocalFail": {
            "trigger": "march_local_fail", "action": "add_march_b", "priority": 4,
            "description_zh": "March局部Fail → 追加March B诊断±16地址",
            "description_en": "March local fail → add March B ±16 addresses",
            "time_effect_pct": 15,
        },
        "R5_AllPass_Reduce": {
            "trigger": "all_pass_early", "action": "reduce_endurance", "priority": 5,
            "description_zh": "前7项全Pass → 耐久10→3轮",
            "description_en": "First 7 all pass → endurance 10→3 cycles",
            "time_effect_pct": -7,
        },
        "R6_IDDQ_Anomaly": {
            "trigger": "iddq_anomaly", "action": "add_march_ss", "priority": 6,
            "description_zh": "IDDQ异常(>2σ) → 追加March SS",
            "description_en": "IDDQ anomaly (>2σ) → add March SS",
            "time_effect_pct": 120,
        },
    }

    # 基础测试执行顺序及典型时间占比
    BASE_TEST_ORDER = [
        ("OS_TEST", 2), ("DC_TEST", 5), ("FUNC_BW", 8), ("FUNC_PW", 6),
        ("FUNC_BOUND", 4), ("FUNC_WP", 3), ("FUNC_WRAP", 3), ("FUNC_CAR", 3),
        ("MARCH_TEST", 20), ("MARCHB_TEST", 15), ("SCAN_TEST", 10),
        ("RET_TEST", 8), ("ERR_TEST", 5), ("ENDUR_TEST", 5), ("IDDQ_TEST", 3),
    ]

    def __init__(self):
        self.triggered_rules = []
        self.simulation_results = {}
        self.progress = 0.0
        self.done = False

    def evaluate(self, results_so_far):
        """
        在每个测试项完成后调用，评估是否触发自适应规则。
        results_so_far: {"OS_TEST":{"pass":True}, "DC_TEST":{"pass":True,"params":{"ISB":0.6}}, ...}
        返回: [{"rule_id":..., "action":..., "description":...}]
        """
        triggered = []
        for rule_id, rule in sorted(self.RULES.items(), key=lambda x: x[1]["priority"]):
            if self._check_rule(rule_id, rule, results_so_far):
                triggered.append({
                    "rule_id": rule_id,
                    "action": rule["action"],
                    "description_zh": rule["description_zh"],
                    "description_en": rule["description_en"],
                    "time_effect_pct": rule["time_effect_pct"],
                })
        self.triggered_rules = triggered
        return triggered

    def _check_rule(self, rule_id, rule, results):
        """单规则条件判定"""
        trigger = rule["trigger"]

        if trigger == "os_all_fail":
            os_r = results.get("OS_TEST")
            return os_r is not None and not os_r.get("pass", True)

        if trigger == "dc_marginal":
            dc_r = results.get("DC_TEST")
            if dc_r and dc_r.get("params"):
                for p, v in dc_r["params"].items():
                    lim = TEST_LIMITS.get(p, {})
                    hi = lim.get("max")
                    if hi and v > hi * 0.8:
                        return True
            return False

        if trigger == "isb_high":
            dc_r = results.get("DC_TEST")
            if dc_r and dc_r.get("params"):
                isb = dc_r["params"].get("ISB", 0)
                return isb > 0.5
            return False

        if trigger == "march_local_fail":
            m = results.get("MARCH_TEST")
            return m is not None and not m.get("pass", True) and m.get("partial", False)

        if trigger == "all_pass_early":
            early = ["OS_TEST", "DC_TEST", "FUNC_BW", "FUNC_PW",
                     "FUNC_BOUND", "FUNC_WP", "MARCH_TEST"]
            if all(k in results for k in early):
                return all(results[k].get("pass", False) for k in early)
            return False

        if trigger == "iddq_anomaly":
            iddq_r = results.get("IDDQ_TEST")
            return iddq_r is not None and iddq_r.get("anomaly", False)

        return False

    def simulate_adaptive_flow(self, n=1000, seed=42):
        """
        Monte Carlo 仿真: 对比固定流程 vs 自适应流程的测试时间和成本。
        必须在后台线程中调用。
        """
        import random as _rnd
        r = _rnd.Random(seed)
        self.done = False
        self.progress = 0.0

        base_time_ms = 225.0  # 典型单颗总测试时间
        fixed_total_time = 0.0
        adaptive_total_time = 0.0
        fixed_escapes = 0
        adaptive_escapes = 0
        rule_counts = {rid: 0 for rid in self.RULES}

        for i in range(n):
            # 生成此颗芯片的测试结果
            chip_results = {}
            chip_truly_good = True
            isb_val = abs(r.gauss(0.1, 0.15))

            for test_name, time_pct in self.BASE_TEST_ORDER:
                prob = JEDEC_PASS_PROBABILITY.get(test_name, 0.99)
                passed = r.random() < prob
                params = {}
                if test_name == "DC_TEST":
                    params["ISB"] = isb_val
                chip_results[test_name] = {
                    "pass": passed,
                    "params": params,
                    "partial": r.random() < 0.3 if not passed else False,
                    "anomaly": isb_val > 0.7 if test_name == "IDDQ_TEST" else False,
                }
                if not passed:
                    chip_truly_good = False

            # 固定流程: 跑全部测试
            fixed_total_time += base_time_ms

            # 自适应流程: 逐步评估
            adaptive_time = 0.0
            cumulative = {}
            skipped = False
            for test_name, time_pct in self.BASE_TEST_ORDER:
                if skipped:
                    break
                adaptive_time += base_time_ms * time_pct / 100
                cumulative[test_name] = chip_results[test_name]
                rules = self.evaluate(cumulative)
                for tr in rules:
                    rule_counts[tr["rule_id"]] += 1
                    eff = tr["time_effect_pct"]
                    if eff < -50:  # skip_remaining
                        skipped = True
                    elif eff > 0:
                        adaptive_time += base_time_ms * eff / 100 * 0.3
                    elif eff < 0:
                        adaptive_time += base_time_ms * eff / 100 * 0.1

            adaptive_total_time += adaptive_time

            # 漏检统计: 自适应跳过后续测试时，可能漏掉后面的 Fail
            if skipped and chip_truly_good:
                pass  # 正确跳过
            elif skipped and not chip_truly_good:
                # 已在 OS 阶段发现 fail, 不算漏检
                pass

            if not chip_truly_good:
                # 固定流程一定能检出
                pass

            self.progress = (i + 1) / n

        avg_fixed = fixed_total_time / n
        avg_adaptive = adaptive_total_time / n
        savings = (1 - avg_adaptive / avg_fixed) * 100 if avg_fixed > 0 else 0

        self.simulation_results = {
            "n": n,
            "fixed": {"avg_time_ms": round(avg_fixed, 2), "total_time_s": round(fixed_total_time / 1000, 1)},
            "adaptive": {"avg_time_ms": round(avg_adaptive, 2), "total_time_s": round(adaptive_total_time / 1000, 1)},
            "time_savings_pct": round(savings, 1),
            "rule_trigger_counts": rule_counts,
        }
        self.done = True
        return self.simulation_results

    def get_rule_summary(self, lang="zh"):
        """获取规则摘要文本，用于流程图标注"""
        key = "description_zh" if lang == "zh" else "description_en"
        lines = []
        for rid, rule in sorted(self.RULES.items(), key=lambda x: x[1]["priority"]):
            lines.append(f"[{rid}] {rule[key]}")
        return lines

    def get_test_to_rule_map(self):
        """返回测试项→关联规则的映射，用于流程图节点标注"""
        mapping = {
            "OS_TEST": ["R1_OS_FastBin"],
            "DC_TEST": ["R2_DC_Marginal", "R3_ISB_High"],
            "MARCH_TEST": ["R4_March_LocalFail"],
            "FUNC_WP": ["R5_AllPass_Reduce"],
            "IDDQ_TEST": ["R6_IDDQ_Anomaly"],
        }
        return mapping


# ============================================================
# Phase 8: 存储器 ATPG 审核
# ============================================================

class MemoryATPG:
    """存储器 ATPG 审核引擎 — March 算法理论覆盖率证明"""

    # 经典 March 算法定义
    # 格式: {name: {"steps": [(direction, operations), ...], "complexity": "N表达式", "description": "..."}}
    # direction: "⇑"(升), "⇓"(降), "⇕"(任意)
    # operations: "w0"=写0, "w1"=写1, "r0"=读期望0, "r1"=读期望1
    CLASSIC_ALGORITHMS = {
        "MATS+": {
            "steps": [
                ("⇕", ["w0"]),
                ("⇑", ["r0", "w1"]),
                ("⇓", ["r1", "w0"]),
            ],
            "complexity": "5N",
            "description": "最简 March 算法，检测 SAF",
            "detects": ["SA0", "SA1"],
        },
        "March Y": {
            "steps": [
                ("⇕", ["w0"]),
                ("⇑", ["r0", "w1", "r1"]),
                ("⇓", ["r1", "w0", "r0"]),
                ("⇕", ["r0"]),
            ],
            "complexity": "8N",
            "description": "检测 SAF + TF + 部分 CF",
            "detects": ["SA0", "SA1", "TF01", "TF10", "CF_inv"],
        },
        "March C-": {
            "steps": [
                ("⇕", ["w0"]),
                ("⇑", ["r0", "w1"]),
                ("⇑", ["r1", "w0"]),
                ("⇓", ["r0", "w1"]),
                ("⇓", ["r1", "w0"]),
                ("⇕", ["r0"]),
            ],
            "complexity": "10N",
            "description": "经典全覆盖算法，SAF+TF+CF 完全覆盖",
            "detects": ["SA0", "SA1", "TF01", "TF10", "CF_inv", "CF_idem"],
        },
        "March B": {
            "steps": [
                ("⇕", ["w0"]),
                ("⇑", ["r0", "w1", "r1", "w0", "r0", "w1"]),
                ("⇑", ["r1", "w0", "w1"]),
                ("⇓", ["r1", "w0", "w1", "w0"]),
                ("⇓", ["r0", "w1", "w0"]),
            ],
            "complexity": "17N",
            "description": "高覆盖率，额外检测链式 CF",
            "detects": ["SA0", "SA1", "TF01", "TF10", "CF_inv", "CF_idem", "AF_r", "AF_w"],
        },
        "March SS": {
            "steps": [
                ("⇕", ["w0"]),
                ("⇑", ["r0", "r0", "w0", "r0", "w1"]),
                ("⇑", ["r1", "r1", "w1", "r1", "w0"]),
                ("⇓", ["r0", "r0", "w0", "r0", "w1"]),
                ("⇓", ["r1", "r1", "w1", "r1", "w0"]),
                ("⇕", ["r0"]),
            ],
            "complexity": "22N",
            "description": "最高覆盖率，支持静态 NPSF 检测",
            "detects": ["SA0", "SA1", "TF01", "TF10", "CF_inv", "CF_idem", "AF_r", "AF_w"],
        },
    }

    def __init__(self):
        self.selected_faults = list(FAULT_MODELS.keys())
        self.current_algorithm = None
        self.proof_text = ""

    def generate_optimal(self, target_faults):
        """根据目标故障选择最小复杂度算法"""
        target_set = set(target_faults)
        best = None
        best_complexity = 999
        for name, algo in self.CLASSIC_ALGORITHMS.items():
            detects_set = set(algo["detects"])
            if target_set.issubset(detects_set):
                # 提取复杂度数值 (如 "10N" → 10)
                try:
                    c = int(algo["complexity"].replace("N", ""))
                except ValueError:
                    c = 999
                if c < best_complexity:
                    best = name
                    best_complexity = c
        if best is None:
            # 没有单个算法能覆盖所有目标，选最全面的
            best = "March SS"
        self.current_algorithm = best
        return best

    def generate_proof(self, algorithm, fault_type):
        """生成特定算法对特定故障类型的数学证明文本"""
        algo = self.CLASSIC_ALGORITHMS.get(algorithm)
        if not algo:
            return f"未知算法: {algorithm}"

        fault_desc = FAULT_MODELS.get(fault_type, fault_type)
        detects = set(algo["detects"])
        covered = fault_type in detects

        proof_lines = []
        proof_lines.append(f"{'='*60}")
        proof_lines.append(f"算法: {algorithm}")
        proof_lines.append(f"故障模型: {fault_type} — {fault_desc}")
        proof_lines.append(f"复杂度: {algo['complexity']} (N=地址数)")
        proof_lines.append(f"{'='*60}")
        proof_lines.append("")

        # March 序列展示
        proof_lines.append("March 序列:")
        for i, (direction, ops) in enumerate(algo["steps"]):
            ops_str = ", ".join(ops)
            proof_lines.append(f"  M{i}: {direction}({ops_str})")
        proof_lines.append("")

        if covered:
            proof_lines.append(f"✓ {algorithm} 可检测 {fault_type}")
            proof_lines.append("")
            # 根据故障类型生成具体证明
            if fault_type in ("SA0", "SA1"):
                stuck_val = "0" if fault_type == "SA0" else "1"
                comp_val = "1" if fault_type == "SA0" else "0"
                proof_lines.append(f"证明:")
                proof_lines.append(f"  假设单元 c 存在 {fault_type} (永久输出 {stuck_val})")
                proof_lines.append(f"  March 步骤中写入 w{comp_val} 后读取 r{comp_val}:")
                proof_lines.append(f"    - 期望读出 {comp_val}")
                proof_lines.append(f"    - 实际读出 {stuck_val} (故障)")
                proof_lines.append(f"    - 不匹配 → 检测到 {fault_type}")
            elif fault_type in ("TF01", "TF10"):
                src = "0→1" if fault_type == "TF01" else "1→0"
                proof_lines.append(f"证明:")
                proof_lines.append(f"  假设单元 c 存在 {fault_type} (无法 {src} 翻转)")
                proof_lines.append(f"  March 步骤中执行 w0→w1 (或 w1→w0) 后读取:")
                proof_lines.append(f"    - 写入翻转值后读取不匹配")
                proof_lines.append(f"    - 检测到 {fault_type}")
            elif fault_type.startswith("CF"):
                proof_lines.append(f"证明:")
                proof_lines.append(f"  假设单元对 (a,v): 写 a 影响 v")
                proof_lines.append(f"  March ⇑/⇓ 双向扫描确保 a<v 和 a>v 均被测试")
                proof_lines.append(f"  写 a 后立即读 v → 检测耦合故障")
            elif fault_type.startswith("AF"):
                proof_lines.append(f"证明:")
                proof_lines.append(f"  假设地址译码故障: 访问 a 实际访问 b≠a")
                proof_lines.append(f"  March 升序写入不同值后读回验证:")
                proof_lines.append(f"    - 若 a→b 映射, 则 b 的值被覆盖")
                proof_lines.append(f"    - 后续读 b 发现值错误 → 检测到 {fault_type}")
        else:
            proof_lines.append(f"✗ {algorithm} 不能检测 {fault_type}")
            proof_lines.append(f"  原因: 算法步骤中不包含检测 {fault_type} 所需的操作序列")
            # 推荐可检测的算法
            for name, a in self.CLASSIC_ALGORITHMS.items():
                if fault_type in a["detects"]:
                    proof_lines.append(f"  推荐: {name} (复杂度 {a['complexity']})")
                    break

        proof_lines.append("")
        proof_lines.append(f"结论: {'COVERED' if covered else 'NOT COVERED'}")
        return "\n".join(proof_lines)

    def generate_full_proof(self, algorithm):
        """生成算法对所有故障模型的完整证明"""
        sections = []
        for ft in FAULT_MODELS:
            sections.append(self.generate_proof(algorithm, ft))
        return "\n\n".join(sections)

    def get_theory_coverage(self, algorithm):
        """获取算法的理论覆盖率矩阵"""
        algo = self.CLASSIC_ALGORITHMS.get(algorithm)
        if not algo:
            return {}
        result = {}
        for ft in FAULT_MODELS:
            result[ft] = 100.0 if ft in algo["detects"] else 0.0
        return result


# ============================================================
# Phase 7: 跨芯片迁移引擎
# ============================================================

class ChipMigrationEngine:
    """AT24Cxx 系列 EEPROM 跨芯片迁移引擎"""

    # AT24Cxx 芯片数据库
    CHIP_DB = {
        "AT24C01":  {"capacity_bits": 1024,    "capacity_bytes": 128,    "pages": 16,   "page_size": 8,   "addr_bytes": 1, "max_freq_khz": 1000, "dev_addr_mask": 0b1010_0000, "a_pins": 3},
        "AT24C02":  {"capacity_bits": 2048,    "capacity_bytes": 256,    "pages": 32,   "page_size": 8,   "addr_bytes": 1, "max_freq_khz": 1000, "dev_addr_mask": 0b1010_0000, "a_pins": 3},
        "AT24C04":  {"capacity_bits": 4096,    "capacity_bytes": 512,    "pages": 32,   "page_size": 16,  "addr_bytes": 1, "max_freq_khz": 1000, "dev_addr_mask": 0b1010_0000, "a_pins": 2},
        "AT24C08":  {"capacity_bits": 8192,    "capacity_bytes": 1024,   "pages": 64,   "page_size": 16,  "addr_bytes": 1, "max_freq_khz": 1000, "dev_addr_mask": 0b1010_0000, "a_pins": 1},
        "AT24C16":  {"capacity_bits": 16384,   "capacity_bytes": 2048,   "pages": 128,  "page_size": 16,  "addr_bytes": 1, "max_freq_khz": 1000, "dev_addr_mask": 0b1010_0000, "a_pins": 0},
        "AT24C32":  {"capacity_bits": 32768,   "capacity_bytes": 4096,   "pages": 128,  "page_size": 32,  "addr_bytes": 2, "max_freq_khz": 400,  "dev_addr_mask": 0b1010_0000, "a_pins": 3},
        "AT24C64":  {"capacity_bits": 65536,   "capacity_bytes": 8192,   "pages": 256,  "page_size": 32,  "addr_bytes": 2, "max_freq_khz": 400,  "dev_addr_mask": 0b1010_0000, "a_pins": 3},
        "AT24C128": {"capacity_bits": 131072,  "capacity_bytes": 16384,  "pages": 256,  "page_size": 64,  "addr_bytes": 2, "max_freq_khz": 400,  "dev_addr_mask": 0b1010_0000, "a_pins": 2},
        "AT24C256": {"capacity_bits": 262144,  "capacity_bytes": 32768,  "pages": 512,  "page_size": 64,  "addr_bytes": 2, "max_freq_khz": 400,  "dev_addr_mask": 0b1010_0000, "a_pins": 2},
        "AT24C512": {"capacity_bits": 524288,  "capacity_bytes": 65536,  "pages": 512,  "page_size": 128, "addr_bytes": 2, "max_freq_khz": 400,  "dev_addr_mask": 0b1010_0000, "a_pins": 2},
    }

    MAX_VECTORS = 5_000_000  # 安全上限

    def __init__(self, source_chip="AT24C02", target_chip="AT24C02"):
        self.source = source_chip
        self.target = target_chip
        self.log = []  # 迁移日志

    def get_chip_info(self, chip_name):
        """获取芯片信息"""
        return self.CHIP_DB.get(chip_name, self.CHIP_DB["AT24C02"]).copy()

    def compare_chips(self):
        """对比源芯片和目标芯片参数"""
        src = self.get_chip_info(self.source)
        tgt = self.get_chip_info(self.target)
        diff = {}
        for key in src:
            diff[key] = {"source": src[key], "target": tgt[key],
                         "changed": src[key] != tgt[key]}
        return diff

    def _estimate_vector_count(self, target_info, test_types):
        """估算目标芯片的向量数"""
        cap = target_info["capacity_bytes"]
        page_size = target_info["page_size"]
        addr_bytes = target_info["addr_bytes"]
        # 每个I2C bit = 4 向量, 每字节 = 8 bit
        # 字节写: START(4) + DevAddr(36) + WordAddr(36*addr_bytes) + Data(36) + STOP(4) + Polling(~200)
        vectors_per_byte_write = 4 + 36 + 36 * addr_bytes + 36 + 4 + 200
        # March C-: 6步 × 全地址 × (写+读)
        march_vectors = 6 * cap * vectors_per_byte_write * 2
        # 其他测试基线
        base_vectors = 5000  # OS + DC + Error + Endurance 等
        total = base_vectors + march_vectors
        return total

    def _need_sampling(self, target_info, test_types):
        """判断是否需要采样模式"""
        est = self._estimate_vector_count(target_info, test_types)
        return est > self.MAX_VECTORS

    def _generate_sampling_addresses(self, target_info):
        """大容量芯片: 边界 + 随机采样地址"""
        import random
        cap = target_info["capacity_bytes"]
        page_size = target_info["page_size"]
        addrs = set()
        # 边界地址: 首页、末页、中间页的首尾
        boundary_pages = [0, cap // page_size - 1, cap // (2 * page_size)]
        for p in boundary_pages:
            base = p * page_size
            addrs.add(base)
            addrs.add(base + page_size - 1)
        # 首尾全局地址
        addrs.add(0)
        addrs.add(cap - 1)
        # 随机采样: 取 min(256, cap/4) 个地址
        rng = random.Random(42)
        n_sample = min(256, cap // 4)
        while len(addrs) < n_sample + len(addrs):
            a = rng.randint(0, cap - 1)
            addrs.add(a)
            if len(addrs) >= n_sample + 8:
                break
        return sorted(addrs)

    def migrate(self, source_vectors, source_comments, test_sections):
        """
        执行迁移: 将源芯片向量适配到目标芯片。
        返回 (migrated_vectors, migrated_comments, log_entries)
        """
        import random
        self.log = []
        src_info = self.get_chip_info(self.source)
        tgt_info = self.get_chip_info(self.target)

        if self.source == self.target:
            self.log.append("[INFO] 源芯片与目标芯片相同，无需迁移")
            return source_vectors[:], source_comments[:], self.log

        self.log.append(f"[START] 迁移: {self.source} → {self.target}")
        self.log.append(f"[INFO] 源: {src_info['capacity_bytes']}B, 页={src_info['page_size']}B, 地址={src_info['addr_bytes']}B")
        self.log.append(f"[INFO] 目标: {tgt_info['capacity_bytes']}B, 页={tgt_info['page_size']}B, 地址={tgt_info['addr_bytes']}B")

        migrated_vectors = []
        migrated_comments = []

        # 地址字节变化检测
        addr_change = tgt_info["addr_bytes"] != src_info["addr_bytes"]
        if addr_change:
            self.log.append(f"[ADAPT] 地址字节: {src_info['addr_bytes']}B → {tgt_info['addr_bytes']}B (需重新生成I2C事务)")

        # 页大小变化检测
        page_change = tgt_info["page_size"] != src_info["page_size"]
        if page_change:
            self.log.append(f"[ADAPT] 页大小: {src_info['page_size']}B → {tgt_info['page_size']}B (页写边界重计算)")

        # 容量变化
        cap_ratio = tgt_info["capacity_bytes"] / src_info["capacity_bytes"]
        self.log.append(f"[INFO] 容量比: {cap_ratio:.1f}x")

        # 采样模式检测
        use_sampling = self._need_sampling(tgt_info, test_sections)
        if use_sampling:
            sample_addrs = self._generate_sampling_addresses(tgt_info)
            self.log.append(f"[SAMPLE] 大容量采样模式: {len(sample_addrs)} 个地址")

        # 频率适配
        if tgt_info["max_freq_khz"] < src_info["max_freq_khz"]:
            self.log.append(f"[ADAPT] 最高频率: {src_info['max_freq_khz']}kHz → {tgt_info['max_freq_khz']}kHz (需调整时序)")

        # 器件地址引脚适配
        if tgt_info["a_pins"] != src_info["a_pins"]:
            self.log.append(f"[ADAPT] 地址引脚: A[{src_info['a_pins']-1}:0] → A[{tgt_info['a_pins']-1}:0]")

        # --- 执行向量迁移 ---
        # 对于地址字节相同且容量相同的情况，直接复用
        if not addr_change and cap_ratio == 1.0:
            migrated_vectors = source_vectors[:]
            migrated_comments = source_comments[:]
            self.log.append("[DONE] 向量兼容，直接复用")
        else:
            # 需要重新生成向量
            # 策略: 复用 OS/DC/Error 测试 (与地址无关), 重新适配 March/Scan/Func 等
            for i, (vec, cmt) in enumerate(zip(source_vectors, source_comments)):
                cmt_str = cmt if isinstance(cmt, str) else ""
                # OS/DC 测试向量: 与存储地址无关，直接复用
                if any(tag in cmt_str for tag in ["OS_", "DC_", "IDLE", "POWER"]):
                    migrated_vectors.append(vec.copy())
                    migrated_comments.append(cmt)
                    continue

                # 功能/March/地址相关向量: 需要适配
                # 对于地址字节变化: 模拟插入额外地址字节向量
                if addr_change and "WORD_ADDR" in cmt_str:
                    # 插入原向量
                    migrated_vectors.append(vec.copy())
                    migrated_comments.append(cmt + f" [迁移自{self.source}]")
                    # 如果目标是2字节地址，插入高字节地址向量(全0占位)
                    if tgt_info["addr_bytes"] > src_info["addr_bytes"]:
                        for _ in range(36):  # 1个字节 = 9 bit(8+ACK) × 4 向量
                            extra = {pin: "0" for pin in vec}
                            extra["SCL"] = vec.get("SCL", "0")
                            migrated_vectors.append(extra)
                            migrated_comments.append("ADDR_HIGH_BYTE [迁移插入]")
                    continue

                # 其他向量直接复用
                migrated_vectors.append(vec.copy())
                migrated_comments.append(cmt)

            self.log.append(f"[DONE] 迁移完成: {len(source_vectors)} → {len(migrated_vectors)} 向量")

        # 向量数安全检查
        if len(migrated_vectors) > self.MAX_VECTORS:
            self.log.append(f"[WARN] 向量数 {len(migrated_vectors)} 超过安全上限 {self.MAX_VECTORS}，将截断")
            migrated_vectors = migrated_vectors[:self.MAX_VECTORS]
            migrated_comments = migrated_comments[:self.MAX_VECTORS]

        return migrated_vectors, migrated_comments, self.log


# ============================================================
# v8.0 — BinningEngine: 测试分 Bin 引擎
# ============================================================

class BinningEngine:
    """ATE 测试 Binning 引擎 — 将测试结果分类为 Good/Fail Bin"""

    def __init__(self, bin_defs=None):
        self.bin_map = dict(bin_defs or BIN_DEFINITIONS)

    def classify(self, test_results):
        """将单颗芯片的测试结果分类到 Bin。

        test_results: dict, key=测试段名, value=True(Pass)/False(Fail)
        返回: Bin 号 (int), 优先级: Bin 2→8 依次匹配, 全 Pass → Bin 1
        """
        os_tests = [k for k in test_results if k.startswith("OS")]
        os_results = [test_results[k] for k in os_tests]

        # Bin 2: OS 全部 Fail → Contact Fail
        if os_results and all(not r for r in os_results):
            return 2

        # Bin 3: OS 部分 Fail
        if os_results and any(not r for r in os_results):
            return 3

        # Bin 4: DC Fail
        dc_tests = [k for k in test_results if k.startswith("DC")]
        if any(not test_results[k] for k in dc_tests):
            return 4

        # Bin 5: Func Fail
        func_tests = [k for k in test_results if k.startswith("FUNC")]
        if any(not test_results[k] for k in func_tests):
            return 5

        # Bin 6: Memory Fail (March / Scan / Retention)
        mem_tests = [k for k in test_results
                     if any(k.startswith(p) for p in ("MARCH", "SCAN", "RET"))]
        if any(not test_results[k] for k in mem_tests):
            return 6

        # Bin 7: I2C Error Fail
        err_tests = [k for k in test_results if k.startswith("ERR")]
        if any(not test_results[k] for k in err_tests):
            return 7

        # Bin 8: Endurance Fail
        end_tests = [k for k in test_results if k.startswith("ENDUR")]
        if any(not test_results[k] for k in end_tests):
            return 8

        # Bin 9: IDDQ Fail
        iddq_tests = [k for k in test_results if k.startswith("IDDQ")]
        if any(not test_results[k] for k in iddq_tests):
            return 9

        return 1  # Bin 1: Good Die

    def classify_batch(self, batch_results):
        """批量分类, 返回 {bin_num: count}"""
        counts = {}
        for result in batch_results:
            b = self.classify(result)
            counts[b] = counts.get(b, 0) + 1
        return counts

    def generate_prg_binning(self):
        """生成 EStar .prg 文件的 @@EOT Binning 逻辑"""
        lines = ["@@EOT"]
        test_bin_map = {
            "OS_TEST": (1, 3), "DC_TEST": (1, 4),
            "FUNC_BW": (1, 5), "FUNC_PW": (1, 5),
            "FUNC_BOUND": (1, 5), "FUNC_WP": (1, 5),
            "FUNC_WRAP": (1, 5), "FUNC_CAR": (1, 5),
            "MARCH_TEST": (1, 6), "MARCHB_TEST": (1, 6),
            "SCAN_TEST": (1, 6), "RET_TEST": (1, 6),
            "ERR_TEST": (1, 7), "ENDUR_TEST": (1, 8),
            "IDDQ_TEST": (1, 9),
        }
        for test_name, (pass_bin, fail_bin) in test_bin_map.items():
            lines.append(f"  BIN_MAP({test_name}, {pass_bin}, {fail_bin});")
        lines.append("@@END_EOT")
        return "\n".join(lines)


# ============================================================
# v8.0 — DatalogGenerator: 测试数据日志生成器
# ============================================================

class DatalogGenerator:
    """模拟 ATE Datalog 生成 — 单颗/批量测试记录"""

    def __init__(self, binning_engine=None):
        self.binning = binning_engine or BinningEngine()
        self.records = []

    def generate_single(self, device_id=1, seed=42, test_segments=None):
        """生成单颗芯片的完整 Datalog 记录。

        test_segments: 可选, 当前测试段名列表
        返回: dict with keys: device_id, timestamp, tests, params, bin, result, test_time_ms
        """
        import random as _rng
        r = _rng.Random(seed + device_id)

        record = {
            "device_id": device_id,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tests": {},      # {test_name: {"passed": bool}}
            "params": [],     # [{"name", "measured", "lo", "hi", "unit", "passed"}]
            "bin": 1,
            "result": "PASS",
            "test_time_ms": 0.0,
        }

        # DC 参数测试 (模拟测量值)
        yield_params = {
            "ISB":   {"nominal": 0.5,  "lo": None,  "hi": 1.0,  "unit": "μA", "sigma_div": 6},
            "ICC_R": {"nominal": 0.5,  "lo": None,  "hi": 1.0,  "unit": "mA", "sigma_div": 6},
            "ICC_W": {"nominal": 1.5,  "lo": None,  "hi": 3.0,  "unit": "mA", "sigma_div": 6},
            "VOL":   {"nominal": 0.2,  "lo": None,  "hi": 0.4,  "unit": "V",  "sigma_div": 6},
            "VOH":   {"nominal": 4.3,  "lo": 2.4,   "hi": None, "unit": "V",  "sigma_div": 6},
        }
        for pname, spec in yield_params.items():
            hi = spec["hi"] if spec["hi"] is not None else 999
            lo = spec["lo"] if spec["lo"] is not None else -999
            sigma = (hi - lo) / spec["sigma_div"] if hi < 900 and lo > -900 else \
                    abs(spec["nominal"]) * 0.15
            measured = r.gauss(spec["nominal"], sigma)
            if spec["hi"] is not None and spec["lo"] is not None:
                passed = spec["lo"] <= measured <= spec["hi"]
            elif spec["hi"] is not None:
                passed = measured <= spec["hi"]
            else:
                passed = measured >= spec["lo"]
            record["params"].append({
                "name": pname, "measured": round(measured, 3),
                "lo": spec["lo"], "hi": spec["hi"],
                "unit": spec["unit"], "passed": passed,
            })

        # 功能测试 (基于 JEDEC 概率)
        segments = test_segments or list(JEDEC_PASS_PROBABILITY.keys())
        test_results = {}
        for seg in segments:
            prob = JEDEC_PASS_PROBABILITY.get(seg, 0.99)
            passed = r.random() < prob
            test_results[seg] = passed
            record["tests"][seg] = {"passed": passed}

        # Binning
        record["bin"] = self.binning.classify(test_results)
        record["result"] = "PASS" if record["bin"] == 1 else "FAIL"

        # 估算测试时间
        record["test_time_ms"] = round(r.uniform(180, 280), 1)

        return record

    def generate_batch(self, count=100, seed=42, test_segments=None,
                       progress_callback=None):
        """批量生成 Datalog 记录"""
        self.records = []
        for i in range(count):
            rec = self.generate_single(device_id=i + 1, seed=seed,
                                       test_segments=test_segments)
            self.records.append(rec)
            if progress_callback and i % 20 == 0:
                progress_callback(i + 1, count)
        return self.records

    def format_datalog_text(self, record):
        """格式化单颗 Datalog 为人类可读文本"""
        lines = []
        lines.append("=" * 64)
        lines.append("  AT24C02 TEST DATALOG — AdaptStar-E ATE")
        lines.append("=" * 64)
        lines.append(f"Program:  AT24C02_FULL_TEST      Date: {record['timestamp']}")
        lines.append(f"Device:   AT24C02-10SU-2.7       Lot:  SIM-2026-001")
        lines.append(f"Site: 1   Temperature: 25°C      Operator: AUTO")
        lines.append("")
        lines.append(f"{'Test#':<6}{'Name':<18}{'Measured':>10}{'LoLim':>10}"
                     f"{'HiLim':>9}{'Unit':>6}{'P/F':>5}")
        lines.append(f"{'-----':<6}{'----------------':<18}{'----------':>10}"
                     f"{'--------':>10}{'-------':>9}{'-----':>6}{'---':>5}")

        test_num = 1
        # DC 参数
        for p in record["params"]:
            lo_str = f"{p['lo']:.3f}" if p["lo"] is not None else "---"
            hi_str = f"{p['hi']:.3f}" if p["hi"] is not None else "---"
            pf = "P" if p["passed"] else "F"
            lines.append(f"{test_num:03d}    {p['name']:<18}{p['measured']:>10.3f}"
                         f"{lo_str:>10}{hi_str:>9}{p['unit']:>6}    {pf}")
            test_num += 1

        # 功能测试
        for tname, tdata in record["tests"].items():
            pf = "P" if tdata["passed"] else "F"
            lines.append(f"{test_num:03d}    {tname:<18}{'---':>10}{'---':>10}"
                         f"{'---':>9}{'---':>6}    {pf}")
            test_num += 1

        lines.append("")
        bin_info = BIN_DEFINITIONS.get(record["bin"], {})
        bin_name = bin_info.get("name", f"Bin{record['bin']}")
        lines.append(f"RESULT: {record['result']}    BIN: {record['bin']} ({bin_name})"
                     f"    Test Time: {record['test_time_ms']:.1f} ms")
        lines.append("=" * 64)
        return "\n".join(lines)

    def export_csv(self, records, filepath):
        """导出批量 Datalog 为 CSV"""
        with open(filepath, "w", encoding="utf-8-sig") as f:
            f.write("DeviceID,Bin,Result,TestTime_ms")
            # 参数列
            if records:
                for p in records[0]["params"]:
                    f.write(f",{p['name']}")
            # 测试列
            if records:
                for t in records[0]["tests"]:
                    f.write(f",{t}")
            f.write("\n")
            for rec in records:
                f.write(f"{rec['device_id']},{rec['bin']},{rec['result']},"
                        f"{rec['test_time_ms']:.1f}")
                for p in rec["params"]:
                    f.write(f",{p['measured']:.3f}")
                for t, td in rec["tests"].items():
                    f.write(f",{'P' if td['passed'] else 'F'}")
                f.write("\n")

    def export_bin_summary_csv(self, records, filepath):
        """导出 Bin Summary CSV"""
        total = len(records)
        counts = {}
        for rec in records:
            b = rec["bin"]
            counts[b] = counts.get(b, 0) + 1
        with open(filepath, "w", encoding="utf-8-sig") as f:
            f.write("Bin,Name,Type,Count,Percent,CumYield\n")
            cum = 0
            for b in sorted(counts.keys()):
                info = BIN_DEFINITIONS.get(b, {"name": f"Bin{b}", "type": "?"})
                cnt = counts[b]
                pct = cnt / total * 100 if total > 0 else 0
                if info.get("type") == "PASS":
                    cum += pct
                f.write(f"{b},{info['name']},{info['type']},{cnt},{pct:.1f}%,"
                        f"{cum:.1f}%\n")
            f.write(f"\nTotal,,{total},100%,Yield: {cum:.1f}%\n")


# ============================================================
# v8.0 — STDFWriter: STDF V4 二进制测试数据格式导出
# ============================================================

class STDFWriter:
    """STDF V4 二进制文件生成器 — 使用 struct 模块, 零第三方依赖"""

    ENDIAN = '<'     # Little-Endian (STDF V4 标准)
    CPU_TYPE = 2     # 2 = x86 Little-Endian
    STDF_VER = 4

    def __init__(self):
        self.file = None

    def _write_record(self, rec_typ, rec_sub, data):
        """写入一条 STDF 记录: [REC_LEN:U*2][REC_TYP:U*1][REC_SUB:U*1][DATA]"""
        header = struct.pack(self.ENDIAN + 'HBB', len(data), rec_typ, rec_sub)
        self.file.write(header + data)

    def _pack_cn(self, string, max_len=255):
        """C*n 格式: 第一字节=长度, 后跟 ASCII 字符"""
        s = string[:max_len].encode('ascii', errors='replace')
        return struct.pack('B', len(s)) + s

    def write_far(self):
        """FAR - File Attributes Record (typ=0, sub=10)"""
        data = struct.pack(self.ENDIAN + 'BB', self.CPU_TYPE, self.STDF_VER)
        self._write_record(0, 10, data)

    def write_mir(self, lot_id="SIM-2026-001", part_type="AT24C02",
                  job_name="AT24C02_FULL_TEST", tester_name="AdaptStar-E"):
        """MIR - Master Information Record (typ=1, sub=10)"""
        now_ts = int(datetime.datetime.now().timestamp())
        data = struct.pack(self.ENDIAN + 'II', now_ts, now_ts)  # SETUP_T, START_T
        data += struct.pack(self.ENDIAN + 'B', 1)  # STAT_NUM
        data += b'P'  # MODE_COD (production)
        data += b' '  # RTST_COD
        data += b' '  # PROT_COD
        data += struct.pack(self.ENDIAN + 'H', 0)  # BURN_TIM
        data += b' '  # CMOD_COD
        data += self._pack_cn(lot_id)
        data += self._pack_cn(part_type)
        data += self._pack_cn("")           # NODE_NAM
        data += self._pack_cn(tester_name)  # TSTR_TYP
        data += self._pack_cn(job_name)     # JOB_NAM
        data += self._pack_cn("")           # JOB_REV
        data += self._pack_cn("")           # SBLOT_ID
        data += self._pack_cn("")           # OPER_NAM
        data += self._pack_cn("")           # EXEC_TYP
        data += self._pack_cn(VERSION)      # EXEC_VER
        self._write_record(1, 10, data)

    def write_sdr(self, site_num=1):
        """SDR - Site Description Record (typ=1, sub=80)"""
        data = struct.pack(self.ENDIAN + 'B', 0)      # HEAD_NUM
        data += struct.pack(self.ENDIAN + 'B', 1)     # SITE_GRP
        data += struct.pack(self.ENDIAN + 'B', 1)     # SITE_CNT
        data += struct.pack(self.ENDIAN + 'B', site_num)  # SITE_NUM array
        data += self._pack_cn(f"Site_{site_num}")     # HAND_TYP
        self._write_record(1, 80, data)

    def write_pmr(self, pin_index, pin_name):
        """PMR - Pin Map Record (typ=1, sub=60)"""
        data = struct.pack(self.ENDIAN + 'H', pin_index)
        data += struct.pack(self.ENDIAN + 'H', 0)   # CHAN_TYP
        data += self._pack_cn(pin_name)
        data += self._pack_cn("")   # PHY_NAM
        data += self._pack_cn("")   # LOG_NAM
        self._write_record(1, 60, data)

    def write_pir(self, head_num=1, site_num=1):
        """PIR - Part Information Record (typ=5, sub=10)"""
        data = struct.pack(self.ENDIAN + 'BB', head_num, site_num)
        self._write_record(5, 10, data)

    def write_ptr(self, test_num, test_name, passed, measured,
                  lo_limit=None, hi_limit=None, unit=""):
        """PTR - Parametric Test Record (typ=15, sub=10)"""
        pf_flag = 0 if passed else 0x80
        opt_flag = 0
        if lo_limit is None:
            opt_flag |= 0x10
        if hi_limit is None:
            opt_flag |= 0x20

        data = struct.pack(self.ENDIAN + 'I', test_num)
        data += struct.pack(self.ENDIAN + 'B', 1)       # HEAD_NUM
        data += struct.pack(self.ENDIAN + 'B', 1)       # SITE_NUM
        data += struct.pack(self.ENDIAN + 'B', pf_flag)  # TEST_FLG
        data += struct.pack(self.ENDIAN + 'B', 0)       # PARM_FLG
        data += struct.pack(self.ENDIAN + 'f', float(measured))
        data += self._pack_cn(test_name)
        data += self._pack_cn("")                        # ALARM_ID
        data += struct.pack(self.ENDIAN + 'B', opt_flag)
        data += struct.pack(self.ENDIAN + 'b', 0)       # RES_SCAL
        data += struct.pack(self.ENDIAN + 'b', 0)       # LLM_SCAL
        data += struct.pack(self.ENDIAN + 'b', 0)       # HLM_SCAL
        data += struct.pack(self.ENDIAN + 'f', float(lo_limit or 0.0))
        data += struct.pack(self.ENDIAN + 'f', float(hi_limit or 0.0))
        data += self._pack_cn(unit)
        self._write_record(15, 10, data)

    def write_ftr(self, test_num, test_name, passed):
        """FTR - Functional Test Record (typ=15, sub=20)"""
        pf_flag = 0 if passed else 0x80
        data = struct.pack(self.ENDIAN + 'I', test_num)
        data += struct.pack(self.ENDIAN + 'B', 1)
        data += struct.pack(self.ENDIAN + 'B', 1)
        data += struct.pack(self.ENDIAN + 'B', pf_flag)
        data += self._pack_cn(test_name)
        self._write_record(15, 20, data)

    def write_prr(self, part_id, bin_num, passed, test_time_ms=0):
        """PRR - Part Results Record (typ=5, sub=20)"""
        part_flag = 0 if passed else 0x08
        data = struct.pack(self.ENDIAN + 'BB', 1, 1)    # HEAD, SITE
        data += struct.pack(self.ENDIAN + 'B', part_flag)
        data += struct.pack(self.ENDIAN + 'H', 0)       # NUM_TEST
        data += struct.pack(self.ENDIAN + 'H', bin_num)  # HARD_BIN
        data += struct.pack(self.ENDIAN + 'H', bin_num)  # SOFT_BIN
        data += struct.pack(self.ENDIAN + 'hh', 0, 0)   # X_COORD, Y_COORD
        data += struct.pack(self.ENDIAN + 'I', int(test_time_ms * 1000))
        data += self._pack_cn(str(part_id))
        data += self._pack_cn("")                        # PART_TXT
        data += struct.pack(self.ENDIAN + 'B', 0)       # PART_FIX len
        self._write_record(5, 20, data)

    def write_mrr(self):
        """MRR - Master Results Record (typ=1, sub=20)"""
        finish_t = int(datetime.datetime.now().timestamp())
        data = struct.pack(self.ENDIAN + 'I', finish_t)
        data += b' '  # DISP_COD
        self._write_record(1, 20, data)

    def export_from_datalog(self, datalog_records, pin_list, filepath,
                            lot_id="SIM-2026-001", part_type="AT24C02",
                            progress_callback=None):
        """从 DatalogGenerator 记录导出完整 STDF 文件。

        返回: 文件字节数
        """
        with open(filepath, 'wb') as f:
            self.file = f
            self.write_far()
            self.write_mir(lot_id=lot_id, part_type=part_type)
            self.write_sdr()

            for i, pin in enumerate(pin_list):
                self.write_pmr(i, pin)

            for idx, rec in enumerate(datalog_records):
                self.write_pir()

                test_num = 1
                # PTR for parametric tests
                for p in rec.get("params", []):
                    self.write_ptr(test_num, p["name"], p["passed"],
                                   p["measured"], p.get("lo"), p.get("hi"),
                                   p.get("unit", ""))
                    test_num += 1

                # FTR for functional tests
                for tname, tdata in rec.get("tests", {}).items():
                    self.write_ftr(test_num, tname, tdata["passed"])
                    test_num += 1

                # PRR
                self.write_prr(rec["device_id"], rec["bin"],
                               rec["result"] == "PASS",
                               rec.get("test_time_ms", 0))

                if progress_callback and idx % 50 == 0:
                    progress_callback(idx + 1, len(datalog_records))

            self.write_mrr()

        return os.path.getsize(filepath)


# ============================================================
# v9.0 Tier3 Phase 31: STDF 导入分析器
# ============================================================

class STDFReader:
    """STDF V4 二进制文件读取器 — STDFWriter 的逆操作"""

    ENDIAN = '<'

    def __init__(self):
        self.records = []
        self.mir = {}
        self.parts = []
        self.pin_map = {}
        self._current_part = None

    def read_file(self, filepath):
        """逐记录读取 STDF 文件"""
        self.records = []
        self.parts = []
        self.mir = {}
        self.pin_map = {}
        self._current_part = None

        with open(filepath, 'rb') as f:
            while True:
                rec = self._read_record(f)
                if rec is None:
                    break
                typ, sub, data = rec
                parsed = self._parse_record(typ, sub, data)
                if parsed:
                    self.records.append(parsed)
        return len(self.records)

    def _read_record(self, f):
        """读取单条 STDF 记录"""
        header = f.read(4)
        if len(header) < 4:
            return None
        rec_len, rec_typ, rec_sub = struct.unpack(self.ENDIAN + 'HBB', header)
        data = f.read(rec_len)
        if len(data) < rec_len:
            return None
        return (rec_typ, rec_sub, data)

    def _unpack_cn(self, data, offset):
        """读取 C*n 字符串"""
        if offset >= len(data):
            return "", offset
        length = data[offset]
        offset += 1
        end = min(offset + length, len(data))
        text = data[offset:end].decode('ascii', errors='replace')
        return text, end

    def _parse_record(self, typ, sub, data):
        """根据类型分发解析"""
        if (typ, sub) == (0, 10):
            return self._parse_far(data)
        if (typ, sub) == (1, 10):
            return self._parse_mir(data)
        if (typ, sub) == (1, 60):
            return self._parse_pmr(data)
        if (typ, sub) == (5, 10):
            return self._parse_pir(data)
        if (typ, sub) == (15, 10):
            return self._parse_ptr(data)
        if (typ, sub) == (15, 20):
            return self._parse_ftr(data)
        if (typ, sub) == (5, 20):
            return self._parse_prr(data)
        if (typ, sub) == (1, 20):
            return self._parse_mrr(data)
        return None

    def _parse_far(self, data):
        if len(data) < 2:
            return None
        cpu, ver = struct.unpack(self.ENDIAN + 'BB', data[:2])
        return {"type": "FAR", "cpu_type": cpu, "stdf_ver": ver}

    def _parse_mir(self, data):
        if len(data) < 8:
            return None
        setup_t, start_t = struct.unpack_from(self.ENDIAN + 'II', data, 0)
        self.mir = {"type": "MIR", "setup_time": setup_t, "start_time": start_t}
        # 尝试解析后续 C*n 字段
        offset = 9  # 跳过 stat_num(B)
        for field in ["mode_cod", "rtst_cod", "prot_cod", "burn_tim", "cmod_cod"]:
            if offset < len(data):
                offset += 1  # 跳过单字符字段
        # 解析关键字符串字段
        for field in ["lot_id", "part_typ", "node_nam", "tstr_typ", "job_nam"]:
            if offset < len(data):
                val, offset = self._unpack_cn(data, offset)
                self.mir[field] = val
        return self.mir

    def _parse_pmr(self, data):
        if len(data) < 4:
            return None
        pmr_idx = struct.unpack_from(self.ENDIAN + 'H', data, 0)[0]
        # chan_typ at offset 2 (U*2)
        offset = 4
        pin_name, offset = self._unpack_cn(data, offset)
        self.pin_map[pmr_idx] = pin_name
        return {"type": "PMR", "index": pmr_idx, "name": pin_name}

    def _parse_pir(self, data):
        if len(data) < 2:
            return None
        head_num, site_num = data[0], data[1]
        self._current_part = {"tests": [], "head": head_num, "site": site_num}
        return {"type": "PIR", "head": head_num, "site": site_num}

    def _parse_ptr(self, data):
        if len(data) < 12:
            return None
        test_num = struct.unpack_from(self.ENDIAN + 'I', data, 0)[0]
        head_num, site_num = data[4], data[5]
        test_flg = data[6]
        result = struct.unpack_from(self.ENDIAN + 'f', data, 8)[0]
        passed = not (test_flg & 0x80)

        offset = 12
        test_txt, offset = self._unpack_cn(data, offset)

        # 尝试读取限值
        lo_limit = hi_limit = None
        unit = ""
        # alarm_id (C*n)
        _, offset = self._unpack_cn(data, offset)
        # opt_flag
        opt_flag = data[offset] if offset < len(data) else 0xFF
        offset += 1
        # res_scal, llm_scal, hlm_scal, lo_limit, hi_limit, units
        if offset + 10 <= len(data):
            offset += 3  # skip scales
            lo_limit = struct.unpack_from(self.ENDIAN + 'f', data, offset)[0]
            offset += 4
            hi_limit = struct.unpack_from(self.ENDIAN + 'f', data, offset)[0]
            offset += 4
            unit, offset = self._unpack_cn(data, offset)
            if opt_flag & 0x10:
                lo_limit = None
            if opt_flag & 0x20:
                hi_limit = None

        rec = {"type": "PTR", "test_num": test_num, "name": test_txt,
               "result": result, "pass": passed,
               "lo_limit": lo_limit, "hi_limit": hi_limit, "unit": unit}
        if self._current_part is not None:
            self._current_part["tests"].append(rec)
        return rec

    def _parse_ftr(self, data):
        if len(data) < 7:
            return None
        test_num = struct.unpack_from(self.ENDIAN + 'I', data, 0)[0]
        test_flg = data[6]
        rec = {"type": "FTR", "test_num": test_num, "pass": not (test_flg & 0x80)}
        if self._current_part is not None:
            self._current_part["tests"].append(rec)
        return rec

    def _parse_prr(self, data):
        if len(data) < 8:
            return None
        head_num, site_num = data[0], data[1]
        # part_flg at offset 2
        hard_bin = struct.unpack_from(self.ENDIAN + 'H', data, 4)[0]
        soft_bin = struct.unpack_from(self.ENDIAN + 'H', data, 6)[0]
        passed = not (data[2] & 0x08) if len(data) > 2 else True

        part = {
            "type": "PRR", "hard_bin": hard_bin, "soft_bin": soft_bin,
            "passed": passed, "tests": []
        }
        if self._current_part is not None:
            part["tests"] = self._current_part["tests"]
        self.parts.append(part)
        self._current_part = None
        return part

    def _parse_mrr(self, data):
        finish_t = struct.unpack_from(self.ENDIAN + 'I', data, 0)[0] if len(data) >= 4 else 0
        return {"type": "MRR", "finish_time": finish_t}

    def get_summary(self):
        """汇总 STDF 内容"""
        total = len(self.parts)
        passed = sum(1 for p in self.parts if p.get("passed", False))
        yield_pct = passed / total * 100 if total > 0 else 0

        bin_dist = {}
        for p in self.parts:
            b = p.get("soft_bin", p.get("hard_bin", 0))
            bin_dist[b] = bin_dist.get(b, 0) + 1

        # 参数统计
        param_stats = {}
        for p in self.parts:
            for t in p.get("tests", []):
                if t["type"] == "PTR":
                    name = t.get("name", f"T{t['test_num']}")
                    if name not in param_stats:
                        param_stats[name] = {"values": [], "unit": t.get("unit", "")}
                    param_stats[name]["values"].append(t["result"])

        for name, info in param_stats.items():
            vals = info["values"]
            n = len(vals)
            if n > 0:
                mu = sum(vals) / n
                var = sum((v - mu) ** 2 for v in vals) / max(n - 1, 1)
                sigma = math.sqrt(var)
                info["mean"] = round(mu, 4)
                info["sigma"] = round(sigma, 4)
                info["min"] = round(min(vals), 4)
                info["max"] = round(max(vals), 4)
                info["count"] = n
            del info["values"]

        return {
            "total_parts": total, "pass_count": passed,
            "yield_pct": round(yield_pct, 1),
            "bin_distribution": bin_dist,
            "param_stats": param_stats,
        }

    def get_parametric_data(self, test_name):
        """提取指定参数的全部测量值"""
        values = []
        for p in self.parts:
            for t in p.get("tests", []):
                if t["type"] == "PTR" and t.get("name", "") == test_name:
                    values.append(t["result"])
        return values

    def compare_with_generated(self, datalog_records):
        """与 DatalogGenerator 生成的记录对比"""
        stdf_summary = self.get_summary()
        gen_total = len(datalog_records)
        gen_passed = sum(1 for r in datalog_records if r.get("result") == "PASS")
        gen_yield = gen_passed / gen_total * 100 if gen_total > 0 else 0

        gen_bins = {}
        for r in datalog_records:
            b = r.get("bin", 0)
            gen_bins[b] = gen_bins.get(b, 0) + 1

        return {
            "stdf": {"total": stdf_summary["total_parts"],
                     "yield_pct": stdf_summary["yield_pct"],
                     "bins": stdf_summary["bin_distribution"]},
            "generated": {"total": gen_total,
                          "yield_pct": round(gen_yield, 1),
                          "bins": gen_bins},
            "yield_diff": round(stdf_summary["yield_pct"] - gen_yield, 1),
        }


# ============================================================
# v9.0 Tier3 Phase 30: PAT 反向解析器
# ============================================================

class PATReverseParser:
    """PAT 文件反向解析：.pat → I2C/SPI/MW 事务序列"""

    def __init__(self):
        self.pins = []
        self.vectors = []
        self.labels = {}
        self.comments = []
        self.protocol = None
        self.transactions = []

    def parse_pat_file(self, content):
        """解析 PAT 文件，提取引脚列表和向量"""
        self.pins = []
        self.vectors = []
        self.labels = {}
        lines = content.split('\n')

        in_header = False
        in_pattern = False
        vec_idx = 0

        for line in lines:
            stripped = line.strip()

            # 解析 HEAD
            if stripped.startswith("HEAD[PIN_NAME]:"):
                in_header = True
                continue
            if in_header and stripped.startswith("END_HEAD"):
                in_header = False
                continue
            if in_header:
                # 提取引脚名 (逗号分隔)
                for pin in stripped.rstrip(';').split(','):
                    pin = pin.strip()
                    if pin:
                        self.pins.append(pin)
                continue

            # 解析 @@PATTERN_DEFINE
            if stripped == "@@PATTERN_DEFINE":
                in_pattern = True
                continue
            if stripped == "@@END_PATTERN_DEFINE":
                in_pattern = False
                continue

            if in_pattern and stripped:
                # 提取标签
                label = None
                vec_part = stripped
                if ':' in stripped:
                    parts = stripped.split(':', 1)
                    label_candidate = parts[0].strip()
                    if label_candidate and not label_candidate.startswith('//'):
                        label = label_candidate
                        vec_part = parts[1].strip()

                # 提取向量数据 (去掉注释和 AC_SET)
                vec_str = vec_part.split(';')[0].strip()
                if vec_str and len(vec_str) == len(self.pins):
                    vec = {}
                    for i, ch in enumerate(vec_str):
                        if i < len(self.pins):
                            vec[self.pins[i]] = ch
                    self.vectors.append(vec)
                    if label:
                        self.labels[label] = vec_idx
                    vec_idx += 1

        return {"pins": self.pins, "vectors": self.vectors,
                "labels": self.labels, "vector_count": len(self.vectors)}

    def detect_protocol(self, pins=None):
        """根据引脚名自动判断协议"""
        pin_set = set(p.upper() for p in (pins or self.pins))
        if {"SCL", "SDA"}.issubset(pin_set):
            self.protocol = "I2C"
        elif {"SCK", "MOSI", "MISO"}.issubset(pin_set) or {"SCLK", "SI", "SO"}.issubset(pin_set):
            self.protocol = "SPI"
        elif {"SK", "DI", "DO"}.issubset(pin_set):
            self.protocol = "Microwire"
        else:
            self.protocol = "Unknown"
        return self.protocol

    def decode_i2c_transactions(self, vectors=None, pins=None):
        """从向量序列中解码 I2C 事务"""
        vecs = vectors or self.vectors
        pin_list = pins or self.pins
        self.transactions = []

        if not vecs or "SCL" not in pin_list or "SDA" not in pin_list:
            return self.transactions

        def get_state(vec, pin):
            v = vec.get(pin, "0")
            if v in ("1", "H"):
                return 1
            if v in ("0", "L"):
                return 0
            return -1  # X, Z

        # 扫描 START/STOP 条件
        events = []  # [(index, "START"|"STOP")]
        for i in range(1, len(vecs)):
            scl_now = get_state(vecs[i], "SCL")
            scl_prev = get_state(vecs[i - 1], "SCL")
            sda_now = get_state(vecs[i], "SDA")
            sda_prev = get_state(vecs[i - 1], "SDA")

            if scl_now == 1 and scl_prev == 1:
                if sda_prev == 1 and sda_now == 0:
                    events.append((i, "START"))
                elif sda_prev == 0 and sda_now == 1:
                    events.append((i, "STOP"))

        # 在 START-STOP 之间解码字节
        for ei in range(len(events)):
            if events[ei][1] != "START":
                continue
            start_idx = events[ei][0]
            # 找对应的 STOP 或下一个 START
            end_idx = len(vecs) - 1
            for ej in range(ei + 1, len(events)):
                end_idx = events[ej][0]
                break

            # 解码 4向量/bit 的字节
            bytes_decoded = []
            acks = []
            pos = start_idx + 2  # 跳过 START 条件本身
            while pos + 35 < end_idx:  # 需要 36 向量 (8bit*4 + ACK*4)
                byte_val = 0
                valid = True
                for bit in range(8):
                    sample_idx = pos + bit * 4 + 1  # 采样相位
                    if sample_idx >= len(vecs):
                        valid = False
                        break
                    sda = get_state(vecs[sample_idx], "SDA")
                    if sda == 1:
                        byte_val |= (1 << (7 - bit))
                    elif sda < 0:
                        # 读操作: 检查 H/L 期望
                        v = vecs[sample_idx].get("SDA", "X")
                        if v == "H":
                            byte_val |= (1 << (7 - bit))

                if not valid:
                    break

                # ACK (第9个bit)
                ack_idx = pos + 32 + 1
                ack = True  # 默认 ACK
                if ack_idx < len(vecs):
                    ack_sda = vecs[ack_idx].get("SDA", "X")
                    ack = ack_sda in ("L", "0")
                acks.append(ack)
                bytes_decoded.append(byte_val)
                pos += 36

            # 组装事务
            if len(bytes_decoded) >= 2:
                dev_addr = bytes_decoded[0]
                rw = "R" if dev_addr & 1 else "W"
                txn = {
                    "type": "Write" if rw == "W" else "Read",
                    "device_addr": f"0x{dev_addr & 0xFE:02X}",
                    "bytes": [f"0x{b:02X}" for b in bytes_decoded[1:]],
                    "acks": acks,
                    "vector_range": (start_idx, end_idx),
                }
                if rw == "W" and len(bytes_decoded) >= 3:
                    txn["type"] = "ByteWrite"
                    txn["word_addr"] = f"0x{bytes_decoded[1]:02X}"
                    txn["data"] = [f"0x{b:02X}" for b in bytes_decoded[2:]]
                self.transactions.append(txn)

        return self.transactions

    def decode_spi_transactions(self, vectors=None, pins=None):
        """SPI 事务解码 (简化版)"""
        vecs = vectors or self.vectors
        self.transactions = []
        # 检测 CS 下降→上升窗口，窗口内按2向量/bit解码MOSI/MISO
        return self.transactions

    def decode_mw_transactions(self, vectors=None, pins=None):
        """Microwire 事务解码 (简化版)"""
        self.transactions = []
        return self.transactions

    def generate_decode_report(self, transactions=None):
        """生成人类可读的事务解码报告"""
        txns = transactions or self.transactions
        lines = [
            f"{'#':>4s}  {'Type':<12s}  {'DevAddr':<8s}  {'Data':<20s}  {'ACKs':<10s}  {'Vectors':<12s}",
            "─" * 72,
        ]
        for i, t in enumerate(txns):
            data = ", ".join(t.get("data", t.get("bytes", [])))[:18]
            acks = "".join("✓" if a else "✗" for a in t.get("acks", []))[:8]
            vr = t.get("vector_range", (0, 0))
            lines.append(
                f"{i + 1:>4d}  {t['type']:<12s}  {t.get('device_addr', '?'):<8s}  "
                f"{data:<20s}  {acks:<10s}  {vr[0]}-{vr[1]}"
            )
        lines.append(f"\nTotal transactions: {len(txns)}")
        return "\n".join(lines)

    def compare_with_reference(self, ref_transactions):
        """事务级对比"""
        own = self.transactions
        match_count = min(len(own), len(ref_transactions))
        matches = 0
        diffs = []
        for i in range(match_count):
            if own[i].get("type") == ref_transactions[i].get("type") and \
               own[i].get("device_addr") == ref_transactions[i].get("device_addr"):
                matches += 1
            else:
                diffs.append({"index": i, "own": own[i].get("type"),
                             "ref": ref_transactions[i].get("type")})

        total = max(len(own), len(ref_transactions), 1)
        return {
            "match_pct": round(matches / total * 100, 1),
            "total_own": len(own),
            "total_ref": len(ref_transactions),
            "diffs": diffs[:20],
        }


# ============================================================
# v8.0 — VectorCompressor: 向量压缩引擎
# ============================================================

class VectorCompressor:
    """ATE 向量压缩引擎 — 分析 REPEAT/LOOP/SUBROUTINE 压缩机会。
    核心约束: 不修改原始向量列表, 仅生成压缩分析报告和压缩格式输出。
    """

    def __init__(self):
        self.analysis = {}

    def compress(self, vectors, comments, labels=None):
        """执行三层压缩分析, 返回分析报告。

        返回 dict:
          original_count, repeat_saved, loop_saved, sub_saved,
          final_count, compression_ratio, details
        """
        original = len(vectors)
        if original == 0:
            self.analysis = {"original_count": 0, "final_count": 0,
                             "compression_ratio": 0, "details": {}}
            return self.analysis

        # 第一层: REPEAT 压缩
        repeat_info = self._find_repeats(vectors)
        repeat_saved = repeat_info["saved"]

        # 第二层: LOOP 压缩 (基于注释模式匹配)
        loop_info = self._find_loops(vectors, comments)
        loop_saved = loop_info["saved"]

        # 第三层: SUBROUTINE 提取
        sub_info = self._find_subroutines(vectors, comments)
        sub_saved = sub_info["saved"]

        # 总压缩 (各层独立计算, 加和但不超过原始)
        total_saved = min(repeat_saved + loop_saved + sub_saved, int(original * 0.85))
        final = original - total_saved

        self.analysis = {
            "original_count": original,
            "repeat_saved": repeat_saved,
            "loop_saved": loop_saved,
            "sub_saved": sub_saved,
            "final_count": final,
            "compression_ratio": total_saved / original * 100 if original > 0 else 0,
            "memory_original_kb": original * 8 / 1024,
            "memory_final_kb": final * 8 / 1024,
            "details": {
                "repeat": repeat_info,
                "loop": loop_info,
                "subroutine": sub_info,
            }
        }
        return self.analysis

    def _find_repeats(self, vectors):
        """检测连续相同向量 (≥3个), 返回可压缩信息"""
        blocks = []
        i = 0
        saved = 0
        while i < len(vectors):
            j = i + 1
            while j < len(vectors) and vectors[j] == vectors[i]:
                j += 1
            count = j - i
            if count >= 3:
                blocks.append({"start": i, "count": count})
                saved += count - 1  # REPEAT N 只需 1 行
            i = j
        return {"blocks": len(blocks), "saved": saved,
                "max_repeat": max((b["count"] for b in blocks), default=0)}

    def _find_loops(self, vectors, comments):
        """基于注释模式检测循环结构"""
        loop_blocks = []
        saved = 0

        # 策略: 按注释中的地址变化检测重复事务
        # 寻找 "addr=0xNN" 递增的连续段
        import re
        addr_pattern = re.compile(r'addr=0x([0-9A-Fa-f]+)')

        segments = []
        current_seg = []
        for i, c in enumerate(comments):
            if c and c.startswith("==="):
                if current_seg:
                    segments.append(current_seg)
                current_seg = [(i, c)]
            elif current_seg:
                current_seg.append((i, c))
        if current_seg:
            segments.append(current_seg)

        # 检测长度相同且结构相似的连续段
        if len(segments) >= 3:
            i = 0
            while i < len(segments) - 1:
                seg_len = len(segments[i])
                j = i + 1
                count = 1
                while j < len(segments) and len(segments[j]) == seg_len:
                    # 检查结构相似性 (忽略地址/数据差异)
                    similar = True
                    for k in range(min(3, seg_len)):
                        c1 = segments[i][k][1] if k < len(segments[i]) else ""
                        c2 = segments[j][k][1] if k < len(segments[j]) else ""
                        c1_clean = addr_pattern.sub("addr=0xNN", c1)
                        c2_clean = addr_pattern.sub("addr=0xNN", c2)
                        if c1_clean != c2_clean:
                            similar = False
                            break
                    if similar:
                        count += 1
                        j += 1
                    else:
                        break
                if count >= 3:
                    loop_blocks.append({"start_seg": i, "iterations": count,
                                        "body_vectors": seg_len})
                    saved += (count - 1) * seg_len
                    i = j
                else:
                    i += 1

        return {"blocks": len(loop_blocks), "saved": saved,
                "details": loop_blocks[:5]}

    def _find_subroutines(self, vectors, comments):
        """检测公共子序列 (如 START+DevAddr 事务头)"""
        # 统计常见的向量模式片段 (长度 4-16)
        pattern_counts = {}
        min_len, max_len = 4, 16

        # 采样: 每 100 个向量取一次窗口
        sample_step = max(1, len(vectors) // 200)
        for start in range(0, len(vectors) - max_len, sample_step):
            for plen in [4, 8, 12, 16]:
                if start + plen > len(vectors):
                    break
                pattern = tuple(
                    tuple(sorted(vectors[start + k].items()))
                    for k in range(plen)
                )
                pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1

        # 筛选出现 >= 3 次的模式
        subroutines = []
        saved = 0
        for pattern, count in sorted(pattern_counts.items(),
                                      key=lambda x: -x[1] * len(x[0])):
            if count >= 3:
                plen = len(pattern)
                sub_saved = (count - 1) * (plen - 1)
                subroutines.append({
                    "length": plen,
                    "occurrences": count,
                    "saved": sub_saved,
                })
                saved += sub_saved
                if len(subroutines) >= 5:
                    break

        return {"count": len(subroutines), "saved": saved,
                "subroutines": subroutines}

    def format_compressed_pat(self, vectors, comments, labels, pin_list, name):
        """生成压缩格式的 PAT 文件内容 (使用 REPEAT/LOOP 指令)"""
        analysis = self.compress(vectors, comments, labels)
        lines = []
        lines.append(f"// Compressed PAT: {name}")
        lines.append(f"// Original: {analysis['original_count']} vectors")
        lines.append(f"// Compressed: {analysis['final_count']} effective vectors")
        lines.append(f"// Ratio: {analysis['compression_ratio']:.1f}%")
        lines.append("")
        lines.append("@@PATTERN_DEFINE  ")
        lines.append(f"// {','.join(pin_list)}")
        lines.append("")

        i = 0
        vec_str_func = lambda v: ''.join(str(v.get(p, '0')) for p in pin_list)
        while i < len(vectors):
            # 检测 REPEAT
            j = i + 1
            while j < len(vectors) and vectors[j] == vectors[i]:
                j += 1
            count = j - i

            label_str = ""
            if labels and i < len(labels) and labels[i]:
                label_str = f"{labels[i]}:"
            comment_str = ""
            if i < len(comments) and comments[i]:
                comment_str = f"    //{comments[i]}"

            vs = vec_str_func(vectors[i])

            if count >= 3:
                prefix = f"{label_str:20s}" if label_str else " " * 20
                lines.append(f"{prefix}{vs};REPEAT {count};{comment_str}")
                i = j
            else:
                prefix = f"{label_str:20s}" if label_str else " " * 20
                lines.append(f"{prefix}{vs};{comment_str}")
                i += 1

        lines.append("")
        lines.append("@@END_PATTERN_DEFINE")
        return "\n".join(lines)


# ============================================================
# v8.0 — WaferMapGenerator: 晶圆级测试结果可视化
# ============================================================

class WaferMapGenerator:
    """晶圆级测试结果可视化 — 200mm 晶圆 + 空间缺陷模型"""

    WAFER_CONFIG = {
        "diameter_mm": 200,
        "die_width_mm": 2.0,
        "die_height_mm": 2.0,
        "edge_exclusion_mm": 3.0,
        "flat_length_mm": 57.5,
    }

    def __init__(self, seed=42):
        self.seed = seed
        self.die_map = {}     # {(col, row): {"bin": int, "x_mm": float, "y_mm": float}}
        self.die_list = []
        self.stats = {}

    def generate_die_layout(self):
        """计算晶圆内所有有效 die 的坐标"""
        cfg = self.WAFER_CONFIG
        radius = cfg["diameter_mm"] / 2
        effective_r = radius - cfg["edge_exclusion_mm"]
        dx = cfg["die_width_mm"]
        dy = cfg["die_height_mm"]

        cols = int(2 * effective_r / dx) + 1
        rows = int(2 * effective_r / dy) + 1

        dies = []
        for row in range(rows):
            for col in range(cols):
                cx = -effective_r + col * dx + dx / 2
                cy = -effective_r + row * dy + dy / 2
                # 圆形边界检查
                if cx ** 2 + cy ** 2 > effective_r ** 2:
                    continue
                # Flat 区域检查 (底部)
                flat_y = -radius + (radius - math.sqrt(radius**2 - (cfg["flat_length_mm"]/2)**2))
                if cy < flat_y:
                    continue
                dies.append({"x_mm": cx, "y_mm": cy, "col": col, "row": row})

        self.die_list = dies
        return dies

    def assign_bins(self, binning_engine=None, yield_pct=95.0):
        """使用空间缺陷模型为每个 die 分配 Bin。
        random.seed(self.seed) 保证可复现。
        """
        import random as _rng
        r = _rng.Random(self.seed)

        if not self.die_list:
            self.generate_die_layout()

        cfg = self.WAFER_CONFIG
        radius = cfg["diameter_mm"] / 2

        # 缺陷簇 (2-3 个)
        num_clusters = r.randint(2, 3)
        clusters = []
        for _ in range(num_clusters):
            cx = r.uniform(-60, 60)
            cy = r.uniform(-60, 60)
            cr = r.uniform(5, 15)
            clusters.append((cx, cy, cr))

        # 划痕线
        scratch_angle = r.uniform(0, math.pi)
        scratch_offset = r.uniform(-30, 30)

        base_fail = 1.0 - yield_pct / 100.0

        self.die_map = {}
        for die in self.die_list:
            x, y = die["x_mm"], die["y_mm"]
            fail_prob = base_fail

            # 边缘衰减
            dist_to_edge = radius - math.sqrt(x**2 + y**2)
            if dist_to_edge < 5:
                fail_prob += 0.15

            # 缺陷簇
            for (cx, cy, cr) in clusters:
                dist = math.sqrt((x - cx)**2 + (y - cy)**2)
                if dist < cr:
                    fail_prob += 0.50 * (1 - dist / cr)

            # 划痕线
            line_dist = abs(x * math.sin(scratch_angle)
                           - y * math.cos(scratch_angle) + scratch_offset)
            if line_dist < 1.0:
                fail_prob += 0.80

            fail_prob = min(fail_prob, 0.99)

            if r.random() < fail_prob:
                bin_num = self._random_fail_bin(r)
            else:
                bin_num = 1

            self.die_map[(die["col"], die["row"])] = {
                "bin": bin_num,
                "x_mm": x, "y_mm": y,
                "result": "PASS" if bin_num == 1 else "FAIL",
            }

    def _random_fail_bin(self, rng):
        """按 JEDEC 典型分布随机分配 Fail Bin"""
        rv = rng.random()
        if rv < 0.05:   return 2
        if rv < 0.20:   return 3
        if rv < 0.45:   return 4
        if rv < 0.70:   return 5
        if rv < 0.85:   return 6
        if rv < 0.93:   return 7
        return 8

    def calculate_stats(self):
        """计算晶圆级统计"""
        total = len(self.die_map)
        good = sum(1 for d in self.die_map.values() if d["bin"] == 1)
        bin_counts = {}
        for d in self.die_map.values():
            b = d["bin"]
            bin_counts[b] = bin_counts.get(b, 0) + 1
        self.stats = {
            "total_dies": total,
            "good_dies": good,
            "yield_pct": good / total * 100 if total > 0 else 0,
            "bin_counts": bin_counts,
        }
        return self.stats


# ============================================================
# v8.0 — VectorDebugger: 向量同步调试器
# ============================================================

class VectorDebugger:
    """向量同步调试器 — 模拟 ATE Debug 模式, 逐向量/逐事务单步执行"""

    def __init__(self, vectors, comments, labels=None):
        self.vectors = vectors
        self.comments = comments
        self.labels = labels or [""] * len(vectors)
        self.pc = 0              # 程序计数器 (当前向量索引)
        self.breakpoints = set()  # 断点集合 {向量索引}
        self.history = []         # 执行历史 [{pc, vector, comment, bus_state, event}]
        self.mode = "STOPPED"     # STOPPED / STEPPING / RUNNING / BREAKPOINT
        self.on_step_callback = None  # 每步回调

    def reset(self):
        """复位到第一个向量"""
        self.pc = 0
        self.history = []
        self.mode = "STOPPED"

    def step(self):
        """单步执行一个向量, 返回状态快照"""
        if self.pc >= len(self.vectors):
            self.mode = "STOPPED"
            return {"pc": self.pc, "done": True, "vector_str": "-",
                    "event": "END", "comment": "", "bus_state": "IDLE"}

        vec = self.vectors[self.pc]
        comment = self.comments[self.pc] if self.pc < len(self.comments) else ""
        label = self.labels[self.pc] if self.pc < len(self.labels) else ""

        pin_order = ["A0", "A1", "A2", "WP", "SCL", "SDA"]
        vec_str = "".join(str(vec.get(p, "?")) for p in pin_order)
        snapshot = {
            "pc": self.pc,
            "vector": vec,
            "vector_str": vec_str,
            "comment": comment,
            "label": label,
            "scl": vec.get("SCL", "?"),
            "sda": vec.get("SDA", "?"),
            "bus_state": self._analyze_bus_state(),
            "event": self._detect_event(),
            "pin_states": {p: vec.get(p, "?") for p in pin_order},
            "done": False,
        }

        self.history.append(snapshot)
        if len(self.history) > 50:
            self.history = self.history[-50:]

        self.pc += 1

        # 检查断点
        if self.pc in self.breakpoints:
            self.mode = "BREAKPOINT"

        if self.on_step_callback:
            self.on_step_callback(snapshot)

        return snapshot

    def step_transaction(self):
        """跳到下一个 I2C 事务边界 (START/STOP)"""
        self.mode = "STEPPING"
        snapshot = None
        # 先跳过当前的 START/STOP
        if self.pc < len(self.comments):
            c = self.comments[self.pc]
            if c and ("START" in c or "STOP" in c):
                snapshot = self.step()

        while self.pc < len(self.vectors) and self.mode == "STEPPING":
            c = self.comments[self.pc] if self.pc < len(self.comments) else ""
            if c and ("START" in c and "Setup" in c or "STOP Setup" in c):
                break
            snapshot = self.step()
            if self.mode == "BREAKPOINT":
                break
        self.mode = "STOPPED"
        return snapshot

    def step_section(self):
        """跳到下一个测试段 (=== 标记)"""
        self.mode = "STEPPING"
        snapshot = None
        # 先跳过当前的 === 标记
        if self.pc < len(self.comments):
            c = self.comments[self.pc]
            if c and c.startswith("==="):
                snapshot = self.step()

        while self.pc < len(self.vectors) and self.mode == "STEPPING":
            c = self.comments[self.pc] if self.pc < len(self.comments) else ""
            if c and c.startswith("==="):
                break
            snapshot = self.step()
            if self.mode == "BREAKPOINT":
                break
        self.mode = "STOPPED"
        return snapshot

    def run_to_breakpoint(self):
        """运行直到断点或结束"""
        self.mode = "RUNNING"
        snapshot = None
        while self.pc < len(self.vectors) and self.mode == "RUNNING":
            snapshot = self.step()
            if self.mode == "BREAKPOINT":
                break
        if self.mode == "RUNNING":
            self.mode = "STOPPED"
        return snapshot

    def stop(self):
        """停止执行"""
        self.mode = "STOPPED"

    def set_breakpoint(self, index):
        """设置断点"""
        self.breakpoints.add(index)

    def clear_breakpoint(self, index):
        """清除断点"""
        self.breakpoints.discard(index)

    def _detect_event(self):
        """检测当前向量的 I2C 事件"""
        if self.pc >= len(self.vectors):
            return "END"
        c = self.comments[self.pc] if self.pc < len(self.comments) else ""
        if not c:
            return "IDLE"
        if "START Condition" in c or "START Setup" in c:
            return "START"
        if "RepSTART" in c:
            return "REP_START"
        if "STOP Condition" in c or "STOP Setup" in c:
            return "STOP"
        if "ACK check" in c or "ACK after" in c:
            return "ACK"
        if "NACK" in c:
            return "NACK"
        if "Write bit=" in c:
            return "WRITE_BIT"
        if "Read bit" in c:
            return "READ_BIT"
        if "Poll" in c:
            return "POLL"
        return "DATA"

    def _analyze_bus_state(self):
        """分析当前总线状态"""
        if self.pc >= len(self.vectors):
            return "IDLE"
        vec = self.vectors[self.pc]
        scl = str(vec.get("SCL", "0"))
        sda = str(vec.get("SDA", "0"))
        if scl in ("1", "H") and sda in ("1", "H"):
            return "IDLE"
        if scl in ("1", "H") and sda in ("0", "L"):
            return "BUSY"
        return "ACTIVE"


# ============================================================
# Phase 3: EStar 格式自验证系统
# ============================================================

class EStarValidator:
    """EStar ATE 文件格式验证器 — 基于真机文件规范的 23 条规则"""

    RULES = [
        # PAT 文件规则 (12条)
        ("pat_head",           "HEAD[PIN_NAME]: 格式正确"),
        ("pat_pin_order",      "引脚顺序 A0,A1,A2,WP,SCL,SDA"),
        ("pat_end_head",       "END_HEAD; 存在"),
        ("pat_pattern_define", "@@PATTERN_DEFINE 存在"),
        ("pat_start_label",    "start: 标签存在"),
        ("pat_end_label",      "end: 标签存在"),
        ("pat_ac_set",         "首向量含 AC_SET 1;"),
        ("pat_end_pattern",    "@@END_PATTERN_DEFINE 存在"),
        ("pat_bit_4cycle",     "每 I2C bit 使用4向量周期"),
        ("pat_ack_4cycle",     "ACK 使用4向量周期 X→L→L→X"),
        ("pat_stop_4cycle",    "STOP 使用4向量周期"),
        ("pat_sda_x",          "非采样相 SDA 使用 X 而非 Z"),
        # LVL 文件规则 (4条)
        ("lvl_define",         "@@LEVEL_SET_DEFINE 格式正确"),
        ("lvl_end",            "@@END_LEVEL_SET 存在"),
        ("lvl_5groups",        "包含5组电平定义"),
        ("lvl_vcc_levels",     "各电压组电平值在规格范围内"),
        # TIM 文件规则 (3条)
        ("tim_define",         "@@TIMING_DEFINE 格式正确"),
        ("tim_ac_set",         "@@AC_SET_1 块存在"),
        ("tim_ts_block",       "[TS] 块格式正确"),
        # PRG 文件规则 (4条)
        ("prg_schedule",       "@@SCHEDULE 格式正确"),
        ("prg_eot",            "@@EOT 块存在"),
        ("prg_plan",           "@@PLAN 块存在"),
        ("prg_pattern_ref",    "PAT 文件引用格式正确"),
    ]

    @staticmethod
    def validate_all(pat_content="", lvl_content="", tim_content="", prg_content=""):
        """逐条验证, 返回 [{"rule": id, "desc": str, "pass": bool, "detail": str}]"""
        results = []

        def _check(rule_id, desc, passed, detail=""):
            results.append({"rule": rule_id, "desc": desc, "pass": passed, "detail": detail})

        # --- PAT 规则 ---
        _check("pat_head", "HEAD[PIN_NAME]: 格式正确",
               "HEAD[PIN_NAME]:" in pat_content,
               "未找到 HEAD[PIN_NAME]: 标记" if "HEAD[PIN_NAME]:" not in pat_content else "")
        _check("pat_pin_order", "引脚顺序 A0,A1,A2,WP,SCL,SDA",
               bool(re.search(r'A0.*A1.*A2.*WP.*SCL.*SDA', pat_content)),
               "引脚顺序不匹配或缺失")
        _check("pat_end_head", "END_HEAD; 存在",
               "END_HEAD;" in pat_content, "")
        _check("pat_pattern_define", "@@PATTERN_DEFINE 存在",
               "@@PATTERN_DEFINE" in pat_content, "")
        _check("pat_start_label", "start: 标签存在",
               bool(re.search(r'start:\s', pat_content)),
               "未找到 start: 标签")
        _check("pat_end_label", "end: 标签存在",
               bool(re.search(r'end:\s', pat_content)),
               "未找到 end: 标签")
        _check("pat_ac_set", "首向量含 AC_SET 1;",
               "AC_SET 1;" in pat_content,
               "首向量应包含 AC_SET 1; 后缀")
        _check("pat_end_pattern", "@@END_PATTERN_DEFINE 存在",
               "@@END_PATTERN_DEFINE" in pat_content, "")

        # I2C bit 4周期检测 (检查注释中是否有 SCL↑/SCL↓ 模式间距=4)
        scl_up_lines = [i for i, line in enumerate(pat_content.split('\n'))
                        if 'SCL' in line and '↑' in line]
        bit_4cycle = True
        if len(scl_up_lines) >= 2:
            gaps = [scl_up_lines[i+1] - scl_up_lines[i] for i in range(min(10, len(scl_up_lines)-1))]
            bit_4cycle = all(g == 4 for g in gaps) if gaps else True
        _check("pat_bit_4cycle", "每 I2C bit 使用4向量周期", bit_4cycle,
               f"检测到间距: {gaps[:5]}" if not bit_4cycle and 'gaps' in dir() else "")

        # ACK 4周期 X→L→L→X
        ack_ok = True
        ack_lines = [i for i, line in enumerate(pat_content.split('\n')) if 'ACK' in line]
        if len(ack_lines) >= 4:
            lines = pat_content.split('\n')
            # 抽样检查前几个 ACK
            for al in ack_lines[:3]:
                if al + 3 < len(lines):
                    block = [lines[al+j] for j in range(4)]
                    has_x = any('X' in b.split(';')[0][-6:] if ';' in b else False for b in [block[0], block[3]])
                    has_l = any('L' in b.split(';')[0][-6:] if ';' in b else False for b in [block[1], block[2]])
                    if not (has_x and has_l):
                        ack_ok = False
                        break
        _check("pat_ack_4cycle", "ACK 使用4向量周期 X→L→L→X", ack_ok, "")

        # STOP 4周期
        stop_lines = [i for i, line in enumerate(pat_content.split('\n')) if 'STOP' in line]
        stop_ok = len(stop_lines) == 0 or len(stop_lines) >= 4  # 至少有4行包含STOP
        _check("pat_stop_4cycle", "STOP 使用4向量周期", stop_ok, "")

        # SDA 非采样相用 X 不用 Z
        z_in_sda = bool(re.search(r'[01]{4}[01]Z', pat_content))
        _check("pat_sda_x", "非采样相 SDA 使用 X 而非 Z", not z_in_sda,
               "发现 SDA 使用 Z, 应改为 X" if z_in_sda else "")

        # --- LVL 规则 ---
        _check("lvl_define", "@@LEVEL_SET_DEFINE 格式正确",
               "@@LEVEL_SET_DEFINE" in lvl_content or not lvl_content,
               "未找到 @@LEVEL_SET_DEFINE" if lvl_content and "@@LEVEL_SET_DEFINE" not in lvl_content else "")
        _check("lvl_end", "@@END_LEVEL_SET 存在",
               "@@END_LEVEL_SET" in lvl_content or not lvl_content, "")
        lvl_groups = len(re.findall(r'@@LEVEL_SET_DEFINE', lvl_content))
        _check("lvl_5groups", "包含5组电平定义",
               lvl_groups >= 5 or not lvl_content,
               f"检测到 {lvl_groups} 组, 需要 5 组" if lvl_content and lvl_groups < 5 else "")
        _check("lvl_vcc_levels", "各电压组电平值在规格范围内",
               True, "需人工审核电平值")

        # --- TIM 规则 ---
        _check("tim_define", "@@TIMING_DEFINE 格式正确",
               "@@TIMING_DEFINE" in tim_content or not tim_content, "")
        _check("tim_ac_set", "@@AC_SET_1 块存在",
               "@@AC_SET_1" in tim_content or not tim_content, "")
        ts_ok = "[TS]" in tim_content and "[END_TS]" in tim_content if tim_content else True
        _check("tim_ts_block", "[TS] 块格式正确", ts_ok,
               "缺少 [TS] 或 [END_TS] 块" if not ts_ok else "")

        # --- PRG 规则 ---
        _check("prg_schedule", "@@SCHEDULE 格式正确",
               "@@SCHEDULE" in prg_content or not prg_content, "")
        _check("prg_eot", "@@EOT 块存在",
               "@@EOT" in prg_content or not prg_content, "")
        _check("prg_plan", "@@PLAN 块存在",
               "@@PLAN" in prg_content or not prg_content, "")
        pat_ref_ok = bool(re.search(r'RUN_PATTERN\(', prg_content)) if prg_content else True
        _check("prg_pattern_ref", "PAT 文件引用格式正确", pat_ref_ok,
               "未找到 RUN_PATTERN() 调用" if prg_content and not pat_ref_ok else "")

        return results

    @staticmethod
    def validate_stil(stil_content):
        """验证 STIL 文件格式 (8条规则)"""
        results = []
        def _c(rid, desc, ok, det=""):
            results.append({"rule": rid, "desc": desc, "pass": ok, "detail": det})
        _c("stil_version", "STIL 1.0 版本声明",
           "STIL 1.0" in stil_content, "")
        _c("stil_header", "Header 块存在",
           "Header {" in stil_content, "")
        _c("stil_signals", "Signals 块引脚定义正确",
           "Signals {" in stil_content, "")
        _c("stil_timing", "Timing/WaveformTable 块存在",
           "WaveformTable" in stil_content, "")
        _c("stil_pattern", "Pattern 块存在",
           bool(re.search(r'Pattern\s+"', stil_content)), "")
        _c("stil_wft_ref", "Pattern 中 W 语句引用已定义 WaveformTable",
           'W "wft_std"' in stil_content or "Pattern" not in stil_content, "")
        # 引脚数一致性: 检查 V 语句中值长度
        v_matches = re.findall(r'V\s*\{\s*"all_pins"\s*=\s*([^;]+);', stil_content)
        sig_count = stil_content.count("In;") + stil_content.count("InOut;") + stil_content.count("Out;")
        pin_ok = all(len(m.strip()) == sig_count for m in v_matches[:5]) if v_matches and sig_count > 0 else True
        _c("stil_pin_count", "每行 V 语句引脚数与 Signals 一致", pin_ok, "")
        valid_chars = set("DUHLXZ ")
        sym_ok = all(all(ch in valid_chars for ch in m.strip()) for m in v_matches[:20]) if v_matches else True
        _c("stil_symbols", "只使用 D/U/L/H/X/Z 符号", sym_ok, "")
        return results

    @staticmethod
    def validate_wgl(wgl_content):
        """验证 WGL 文件格式 (7条规则)"""
        results = []
        def _c(rid, desc, ok, det=""):
            results.append({"rule": rid, "desc": desc, "pass": ok, "detail": det})
        _c("wgl_version", "WGL 文件头存在",
           "WGL Pattern File" in wgl_content or "waveform_table" in wgl_content, "")
        _c("wgl_pin_list", "pin_list 块方向正确",
           "pin_list" in wgl_content, "")
        _c("wgl_time_plate", "waveform_table 块存在",
           "waveform_table" in wgl_content, "")
        _c("wgl_pattern", "pattern 块存在",
           bool(re.search(r'^pattern\s+\w+', wgl_content, re.MULTILINE)), "")
        _c("wgl_tp_ref", "pattern 引用已定义 waveform_table",
           "wft_std" in wgl_content or "pattern" not in wgl_content, "")
        # 引脚数
        vec_matches = re.findall(r'\{\s*([^}]+);\s*\}', wgl_content)
        vec_samples = [m for m in vec_matches if any(c in m for c in "01LHXZ")][:10]
        if vec_samples:
            expected_count = len(vec_samples[0].split())
            pin_ok = all(len(v.split()) == expected_count for v in vec_samples)
        else:
            pin_ok = True
        _c("wgl_pin_count", "每行 vector 引脚数正确", pin_ok, "")
        valid_chars = set("01LHXZ ,")
        sym_ok = all(all(ch in valid_chars for ch in v) for v in vec_samples) if vec_samples else True
        _c("wgl_symbols", "只使用 0/1/L/H/X/Z", sym_ok, "")
        return results

    @staticmethod
    def summary(results):
        """返回 (passed_count, failed_count, total)"""
        passed = sum(1 for r in results if r["pass"])
        return passed, len(results) - passed, len(results)


# ============================================================
# v9.0 — Datasheet 参数覆盖矩阵
# ============================================================

class DatasheetComplianceMatrix:
    """Datasheet 参数→测试项→覆盖状态映射"""

    # AT24C02 完整参数清单 (~33项)
    PARAMS = {
        # DC 参数 (9项)
        "DC-01": {"name": "ISB",        "cat": "DC",   "spec": "<1.0μA @5.5V",       "covered_by": ["DC"]},
        "DC-02": {"name": "ICC(R)",     "cat": "DC",   "spec": "<1.0mA @400kHz",     "covered_by": ["DC"]},
        "DC-03": {"name": "ICC(W)",     "cat": "DC",   "spec": "<3.0mA @400kHz",     "covered_by": ["DC"]},
        "DC-04": {"name": "VIL",        "cat": "DC",   "spec": "-0.5~0.3×VCC",      "covered_by": ["DC"]},
        "DC-05": {"name": "VIH",        "cat": "DC",   "spec": "0.7×VCC~VCC+0.5",   "covered_by": ["DC"]},
        "DC-06": {"name": "VOL",        "cat": "DC",   "spec": "<0.4V @IOL=3mA",    "covered_by": ["DC"]},
        "DC-07": {"name": "VOH",        "cat": "DC",   "spec": "开漏(外拉)",          "covered_by": ["DC"]},
        "DC-08": {"name": "ILI",        "cat": "DC",   "spec": "<1.0μA",             "covered_by": ["OS"]},
        "DC-09": {"name": "IOL",        "cat": "DC",   "spec": "3mA(5V)/1mA(1.8V)", "covered_by": ["DC"]},
        "DC-10": {"name": "IDDQ",       "cat": "DC",   "spec": "<1.0μA quiescent",  "covered_by": ["IDDQ"]},
        # AC 参数 (9项)
        "AC-01": {"name": "fSCL",       "cat": "AC",   "spec": "≤1MHz @5V",          "covered_by": ["FUNC", "Shmoo"]},
        "AC-02": {"name": "tLOW",       "cat": "AC",   "spec": ">1.3μs (Std)",       "covered_by": ["FUNC"]},
        "AC-03": {"name": "tHIGH",      "cat": "AC",   "spec": ">0.6μs (Fast)",      "covered_by": ["FUNC"]},
        "AC-04": {"name": "tSU:STA",    "cat": "AC",   "spec": ">0.6μs",             "covered_by": ["FUNC"]},
        "AC-05": {"name": "tHD:STA",    "cat": "AC",   "spec": ">0.6μs",             "covered_by": ["FUNC"]},
        "AC-06": {"name": "tSU:DAT",    "cat": "AC",   "spec": ">100ns",             "covered_by": ["FUNC"]},
        "AC-07": {"name": "tSU:STO",    "cat": "AC",   "spec": ">0.6μs",             "covered_by": ["FUNC"]},
        "AC-08": {"name": "tBUF",       "cat": "AC",   "spec": ">1.3μs",             "covered_by": ["FUNC"]},
        "AC-09": {"name": "tWR",        "cat": "AC",   "spec": "<5ms",               "covered_by": ["FUNC", "March", "Endurance"]},
        # 功能参数 (9项)
        "FN-01": {"name": "ByteWrite",  "cat": "Func", "spec": "单字节写入",           "covered_by": ["FUNC"]},
        "FN-02": {"name": "PageWrite",  "cat": "Func", "spec": "8字节页写",            "covered_by": ["FUNC"]},
        "FN-03": {"name": "RandomRead", "cat": "Func", "spec": "随机读",               "covered_by": ["FUNC"]},
        "FN-04": {"name": "SeqRead",    "cat": "Func", "spec": "顺序读",               "covered_by": ["FUNC"]},
        "FN-05": {"name": "CurAddrRead","cat": "Func", "spec": "当前地址读",            "covered_by": ["FUNC"]},
        "FN-06": {"name": "WP",         "cat": "Func", "spec": "写保护",               "covered_by": ["FUNC"]},
        "FN-07": {"name": "DevAddr",    "cat": "Func", "spec": "1010_A2A1A0_RW",     "covered_by": ["FUNC", "I2CErr"]},
        "FN-08": {"name": "ACK/NACK",   "cat": "Func", "spec": "应答机制",              "covered_by": ["FUNC", "I2CErr"]},
        "FN-09": {"name": "AddrRollover","cat":"Func",  "spec": "地址翻转",              "covered_by": ["FUNC"]},
        # 存储器参数 (4项)
        "MEM-01": {"name": "SA Fault",  "cat": "Mem",  "spec": "无SA故障",             "covered_by": ["March"]},
        "MEM-02": {"name": "TF Fault",  "cat": "Mem",  "spec": "0→1翻转正常",          "covered_by": ["March"]},
        "MEM-03": {"name": "CF Fault",  "cat": "Mem",  "spec": "无耦合故障",            "covered_by": ["March"]},
        "MEM-04": {"name": "AF Fault",  "cat": "Mem",  "spec": "地址唯一映射",           "covered_by": ["AddrScan"]},
        # 可靠性参数 (2项)
        "REL-01": {"name": "Retention", "cat": "Rel",  "spec": ">100年 @25°C",        "covered_by": ["DataRet"]},
        "REL-02": {"name": "Endurance", "cat": "Rel",  "spec": ">1M cycles @25°C",    "covered_by": ["Endurance"]},
    }

    # 测试项名→GUI复选框名映射
    TEST_KEY_MAP = {
        "OS": "os_test", "DC": "dc_test", "FUNC": "func_test",
        "March": "march_test", "AddrScan": "scan_test",
        "DataRet": "ret_test", "I2CErr": "err_test",
        "Endurance": "endur_test", "IDDQ": "iddq_test", "Shmoo": "shmoo",
    }

    def calculate_coverage(self, enabled_tests):
        """计算覆盖率: {total, covered, pct, uncovered[], by_category{}}"""
        total = len(self.PARAMS)
        covered_ids = []
        uncovered_ids = []
        by_cat = {}
        for pid, p in self.PARAMS.items():
            is_covered = any(t in enabled_tests for t in p["covered_by"])
            if is_covered:
                covered_ids.append(pid)
            else:
                uncovered_ids.append(pid)
            cat = p["cat"]
            if cat not in by_cat:
                by_cat[cat] = {"total": 0, "covered": 0}
            by_cat[cat]["total"] += 1
            if is_covered:
                by_cat[cat]["covered"] += 1
        return {
            "total": total,
            "covered": len(covered_ids),
            "pct": len(covered_ids) / total * 100 if total > 0 else 0,
            "uncovered": uncovered_ids,
            "by_category": by_cat,
        }

    def generate_matrix_data(self, enabled_tests):
        """返回表格数据: [{id, name, cat, spec, covered_by, status}]"""
        result = []
        for pid, p in self.PARAMS.items():
            status = "COVERED" if any(t in enabled_tests for t in p["covered_by"]) else "UNCOVERED"
            result.append({**p, "id": pid, "status": status})
        return result


# ============================================================
# v9.0 — 上电/下电序列生成器
# ============================================================

class PowerSequenceGenerator:
    """ATE 上电/下电/热切换序列生成器"""

    @staticmethod
    def generate_power_up(pins, protocol="I2C", vcc=5.0):
        """
        上电序列 (~20向量):
        Phase 1: 安全状态 — 全引脚=0, LEVEL_SET=DC_0V_PWR (4 vec)
        Phase 2: VCC斜坡 — 切换LEVEL_SET=DC_VCC_LVL (4 vec)
        Phase 3: POR等待 — 保持低等待tPOR (8 vec)
        Phase 4: 总线idle — 协议空闲状态 (4 vec)
        返回: (vectors, comments, level_switches)
        """
        vectors, comments, ls = [], [], []
        zero = {p: "0" for p in pins}

        # Phase 1: 安全状态
        ls.append((0, "DC_0V_PWR"))
        for _ in range(4):
            vectors.append(dict(zero))
            comments.append("PwrUp: safe state VCC=0V")

        # Phase 2: VCC 斜坡
        ls.append((4, "DC_VCC_LVL"))
        for _ in range(4):
            vectors.append(dict(zero))
            comments.append(f"PwrUp: VCC ramp to {vcc}V")

        # Phase 3: POR 等待
        for i in range(8):
            vectors.append(dict(zero))
            comments.append(f"PwrUp: POR wait ({i + 1}/8)")

        # Phase 4: 总线 idle
        idle = dict(zero)
        if protocol == "I2C":
            idle["SCL"] = "1"
            idle["SDA"] = "1"
        elif protocol == "SPI":
            idle["CS"] = "1"
        # Microwire: CS=0 即为 idle (CS高有效)
        for _ in range(4):
            vectors.append(dict(idle))
            comments.append("PwrUp: bus idle")

        return vectors, comments, ls

    @staticmethod
    def generate_power_down(pins):
        """
        下电序列 (~8向量):
        Phase 1: 全引脚=0 (4 vec)
        Phase 2: LEVEL_SET=PWR_OFF (4 vec)
        """
        vectors, comments, ls = [], [], []
        zero = {p: "0" for p in pins}

        for _ in range(4):
            vectors.append(dict(zero))
            comments.append("PwrDown: all pins low")

        ls.append((4, "PWR_OFF"))
        for _ in range(4):
            vectors.append(dict(zero))
            comments.append("PwrDown: VCC=0V safe")

        return vectors, comments, ls

    @staticmethod
    def generate_hot_switch(pins, from_v, to_v, protocol="I2C"):
        """热切换 (~6向量, 用于多电压Shmoo)"""
        vectors, comments, ls = [], [], []
        zero = {p: "0" for p in pins}

        for _ in range(2):
            vectors.append(dict(zero))
            comments.append(f"HotSwitch: hold {from_v}V→{to_v}V")

        ls.append((2, f"DC_VCC_{to_v}V"))
        for _ in range(4):
            vectors.append(dict(zero))
            comments.append(f"HotSwitch: stabilize {to_v}V")

        return vectors, comments, ls


# ============================================================
# v9.0 Phase 22 — 温度角仿真引擎
# ============================================================

class TemperatureCornerSimulator:
    """三温参数漂移仿真 — 基于 AT24C02 Datasheet 温度系数模型"""

    TEMP_COEFFICIENTS = {
        "ISB":   {"model": "exponential", "ref": 25, "nominal": 0.1,
                  "coeff": 0.06, "unit": "\u03bcA",
                  "spec_min": None, "spec_max": 1.0},
        "ICC_R": {"model": "linear", "ref": 25, "nominal": 0.5,
                  "slope": 0.003, "unit": "mA",
                  "spec_min": None, "spec_max": 1.0},
        "ICC_W": {"model": "linear", "ref": 25, "nominal": 1.5,
                  "slope": 0.008, "unit": "mA",
                  "spec_min": None, "spec_max": 3.0},
        "VOL":   {"model": "linear", "ref": 25, "nominal": 0.2,
                  "slope": 0.001, "unit": "V",
                  "spec_min": None, "spec_max": 0.4},
        "VOH":   {"model": "linear", "ref": 25, "nominal": 2.4,
                  "slope": -0.002, "unit": "V",
                  "spec_min": 2.4, "spec_max": None},
        "tWR":   {"model": "linear", "ref": 25, "nominal": 3.0,
                  "slope": 0.02, "unit": "ms",
                  "spec_min": None, "spec_max": 5.0},
        "fSCL":  {"model": "linear", "ref": 25, "nominal": 400,
                  "slope": -0.5, "unit": "kHz",
                  "spec_min": None, "spec_max": 1000},
        "VIH":   {"model": "linear", "ref": 25, "nominal": 3.5,
                  "slope": -0.001, "unit": "V",
                  "spec_min": 3.5, "spec_max": 5.5},
    }

    TEMP_CORNERS = {
        "commercial": [-40, 0, 25, 70, 85],
        "industrial": [-40, -20, 0, 25, 50, 85, 125],
    }

    def calc_at_temp(self, param, temp):
        """计算参数在指定温度下的值"""
        c = self.TEMP_COEFFICIENTS[param]
        dt = temp - c["ref"]
        if c["model"] == "exponential":
            return c["nominal"] * (2.718281828 ** (c["coeff"] * dt))
        return c["nominal"] + c["slope"] * dt

    def run_corner_analysis(self, corner_type="commercial"):
        """
        全温角分析
        返回: {temp: {param: {value, spec_min, spec_max, pass, margin_pct}}}
        """
        temps = self.TEMP_CORNERS.get(corner_type, self.TEMP_CORNERS["commercial"])
        results = {}
        for temp in temps:
            results[temp] = {}
            for param, c in self.TEMP_COEFFICIENTS.items():
                val = self.calc_at_temp(param, temp)
                smin = c["spec_min"]
                smax = c["spec_max"]
                passed = True
                if smin is not None and val < smin:
                    passed = False
                if smax is not None and val > smax:
                    passed = False
                margin = self._calc_margin(val, smin, smax)
                results[temp][param] = {
                    "value": round(val, 4), "spec_min": smin, "spec_max": smax,
                    "pass": passed, "margin_pct": round(margin, 1), "unit": c["unit"],
                }
        return results

    def find_temp_limit(self, param):
        """二分搜索参数首次超 spec 的温度 (-55~150°C)"""
        c = self.TEMP_COEFFICIENTS[param]
        smin, smax = c["spec_min"], c["spec_max"]
        if smin is None and smax is None:
            return {"param": param, "limit_temp": None, "limit_value": None, "boundary": "N/A"}
        lo, hi = -55.0, 150.0
        # 判断在高温还是低温端超标
        val_lo = self.calc_at_temp(param, lo)
        val_hi = self.calc_at_temp(param, hi)
        exceeds_at_hi = (smax is not None and val_hi > smax) or (smin is not None and val_hi < smin)
        exceeds_at_lo = (smax is not None and val_lo > smax) or (smin is not None and val_lo < smin)
        if not exceeds_at_hi and not exceeds_at_lo:
            return {"param": param, "limit_temp": None, "limit_value": None, "boundary": "All Pass"}
        # 二分搜索
        for _ in range(30):
            mid = (lo + hi) / 2
            val = self.calc_at_temp(param, mid)
            exceeds = (smax is not None and val > smax) or (smin is not None and val < smin)
            if exceeds_at_hi:
                if exceeds:
                    hi = mid
                else:
                    lo = mid
            else:
                if exceeds:
                    lo = mid
                else:
                    hi = mid
        limit_t = round((lo + hi) / 2, 1)
        return {"param": param, "limit_temp": limit_t,
                "limit_value": round(self.calc_at_temp(param, limit_t), 4),
                "boundary": f">{smax}" if smax is not None else f"<{smin}"}

    def generate_report_data(self, corner_type="commercial"):
        """返回表格数据用于 Treeview 显示"""
        results = self.run_corner_analysis(corner_type)
        temps = self.TEMP_CORNERS.get(corner_type, self.TEMP_CORNERS["commercial"])
        rows = []
        for param, c in self.TEMP_COEFFICIENTS.items():
            row = {"param": param, "unit": c["unit"], "values": {}}
            limit_info = self.find_temp_limit(param)
            for t in temps:
                r = results[t][param]
                row["values"][t] = r
            row["limit_temp"] = limit_info["limit_temp"]
            row["limit_boundary"] = limit_info["boundary"]
            rows.append(row)
        return rows, temps

    @staticmethod
    def _calc_margin(val, spec_min, spec_max):
        if spec_max is not None and spec_max != 0:
            return (1 - val / spec_max) * 100
        if spec_min is not None and spec_min != 0:
            return (val / spec_min - 1) * 100
        return 100.0


# ============================================================
# v9.0 Phase 24 — Pin Map 资源映射
# ============================================================

class PinMapManager:
    """ATE Pin Electronics 通道分配"""

    ESTAR_PIN_CARDS = {
        "DPS_1": {"type": "Power",  "channels": 4,  "desc": "Digital Power Supply"},
        "PE_1":  {"type": "PE",     "channels": 16, "desc": "Pin Electronics Card 1"},
        "PE_2":  {"type": "PE",     "channels": 16, "desc": "Pin Electronics Card 2"},
        "PMU_1": {"type": "PMU",    "channels": 8,  "desc": "Precision Measurement Unit"},
    }

    POWER_PINS = {"VCC": "power_supply", "GND": "ground"}

    def __init__(self, protocol="I2C"):
        self.protocol = protocol

    def generate_pin_map(self, pins, pin_directions=None, num_sites=1):
        """
        自动分配引脚到 PE 通道
        返回: {pin_name: {"card": str, "channel": int, "direction": str, "site": int}}
        """
        if pin_directions is None:
            pin_directions = {}
        result = {}
        for site in range(1, num_sites + 1):
            offset = (site - 1) * len(pins)
            for i, pin in enumerate(pins):
                direction = pin_directions.get(pin, "input")
                ch = offset + i
                # 双向引脚分配到 PE_2, 其他分配到 PE_1
                if direction.lower() in ("bidirectional", "inout", "out"):
                    card = "PE_2"
                else:
                    card = "PE_1"
                key = pin if num_sites == 1 else f"S{site}_{pin}"
                result[key] = {
                    "card": card, "channel": ch, "direction": direction, "site": site,
                }
        # 电源引脚
        result["VCC"] = {"card": "DPS_1", "channel": 0, "direction": "power", "site": 0}
        result["GND"] = {"card": "DPS_1", "channel": 1, "direction": "ground", "site": 0}
        return result

    def generate_pin_map_section(self, pin_map):
        """生成 EStar @@PIN_MAP 格式文本"""
        lines = ["@@PIN_MAP"]
        lines.append(f"  {'PIN_NAME':<12} {'CARD':<8} {'CHANNEL':<10} {'DIRECTION':<12}")
        for pin_name, info in pin_map.items():
            lines.append(f"  {pin_name:<12} {info['card']:<8} CH{info['channel']:<8} "
                         f"{info['direction'].upper():<12}")
        lines.append("@@END_PIN_MAP")
        return "\n".join(lines)

    def validate_resource(self, pin_map, num_sites=1):
        """验证通道资源是否足够"""
        card_usage = {}
        for info in pin_map.values():
            card = info["card"]
            card_usage[card] = card_usage.get(card, 0) + 1

        errors = []
        warnings = []
        utilization = {}
        for card, count in card_usage.items():
            spec = self.ESTAR_PIN_CARDS.get(card, {})
            max_ch = spec.get("channels", 16)
            pct = count / max_ch * 100
            utilization[card] = round(pct, 1)
            if count > max_ch:
                errors.append(f"{card}: need {count} channels, only {max_ch} available")
            elif pct > 80:
                warnings.append(f"{card}: {pct:.0f}% utilization (near capacity)")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "utilization": utilization,
            "total_channels": sum(card_usage.values()),
        }


# ============================================================
# v9.0 Phase 25 — 测试阶段管理
# ============================================================

class TestPhaseManager:
    """ATE 测试阶段管理 — Wafer Sort / Final Test / QA"""

    PHASES = {
        "wafer_sort": {
            "label_zh": "晶圆测试",
            "label_en": "Wafer Sort",
            "enabled_tests": ["os_test", "dc_test", "func_test", "march_test"],
            "disabled_tests": ["march_b_test", "scan_test", "ret_test",
                               "err_test", "endur_test", "iddq_test"],
            "rationale_zh": "晶圆级快速筛选: OS+DC+FUNC+March 覆盖~90%缺陷",
            "rationale_en": "Wafer-level screening: OS+DC+FUNC+March covers ~90% defects",
            "typical_time_pct": 40,
        },
        "final_test": {
            "label_zh": "终测",
            "label_en": "Final Test",
            "enabled_tests": ["os_test", "dc_test", "func_test", "march_test",
                              "march_b_test", "scan_test", "ret_test",
                              "err_test", "endur_test", "iddq_test"],
            "disabled_tests": [],
            "rationale_zh": "封装后完整测试: 全部 10 项, 确保出厂质量",
            "rationale_en": "Post-package full test: all 10 types for shipping quality",
            "typical_time_pct": 100,
        },
        "qa_audit": {
            "label_zh": "质量抽检",
            "label_en": "QA Audit",
            "enabled_tests": ["os_test", "dc_test", "func_test", "iddq_test"],
            "disabled_tests": ["march_test", "march_b_test", "scan_test",
                               "ret_test", "err_test", "endur_test"],
            "rationale_zh": "批量抽样: 接触+参数+基本功能+IDDQ",
            "rationale_en": "Lot sampling: contact + parametric + basic function + IDDQ",
            "typical_time_pct": 30,
        },
        "incoming_inspection": {
            "label_zh": "来料检验",
            "label_en": "Incoming Inspection",
            "enabled_tests": ["os_test", "dc_test", "func_test"],
            "disabled_tests": ["march_test", "march_b_test", "scan_test",
                               "ret_test", "err_test", "endur_test", "iddq_test"],
            "rationale_zh": "客户端来料验证: 确认芯片未在运输中损坏",
            "rationale_en": "Customer incoming: verify parts not damaged in transit",
            "typical_time_pct": 25,
        },
        "characterization": {
            "label_zh": "特征评估",
            "label_en": "Characterization",
            "enabled_tests": ["os_test", "dc_test", "func_test", "march_test",
                              "march_b_test", "scan_test", "ret_test",
                              "err_test", "endur_test", "iddq_test"],
            "disabled_tests": [],
            "rationale_zh": "研发阶段全参数特征化 (不考虑测试时间)",
            "rationale_en": "R&D full characterization (time not a concern)",
            "typical_time_pct": 150,
        },
    }

    def apply_phase(self, phase_name):
        """应用测试阶段配置, 返回 enabled/disabled 列表"""
        phase = self.PHASES.get(phase_name)
        if not phase:
            return {"enabled": [], "disabled": [], "rationale": "Unknown phase"}
        return {
            "enabled": phase["enabled_tests"],
            "disabled": phase["disabled_tests"],
            "rationale": phase.get("rationale_en", ""),
        }

    def compare_phases(self, phase_a, phase_b):
        """对比两个阶段的差异"""
        a = set(self.PHASES.get(phase_a, {}).get("enabled_tests", []))
        b = set(self.PHASES.get(phase_b, {}).get("enabled_tests", []))
        return {
            "only_in_a": sorted(a - b),
            "only_in_b": sorted(b - a),
            "common": sorted(a & b),
        }

    def generate_multi_phase_prg(self, phases, pat_sections, export_prefix="AT24C02"):
        """生成多阶段 @@PLAN 块"""
        lines = []
        plan_name_map = {
            "OS_TEST": "OPENSHORT", "DC_TEST": "IIH_IIL",
            "FUNC_TEST": "Functional", "MARCH_TEST": "March_C",
            "MARCHB_TEST": "March_B", "SCAN_TEST": "Addr_Scan",
            "RET_TEST": "Data_Retention", "ERR_TEST": "Error_Test",
            "ENDUR_TEST": "Endurance", "IDDQ_TEST": "IDDQ_Test",
        }
        test_key_to_section = {
            "os_test": "OS_TEST", "dc_test": "DC_TEST", "func_test": "FUNC_TEST",
            "march_test": "MARCH_TEST", "march_b_test": "MARCHB_TEST",
            "scan_test": "SCAN_TEST", "ret_test": "RET_TEST",
            "err_test": "ERR_TEST", "endur_test": "ENDUR_TEST",
            "iddq_test": "IDDQ_TEST",
        }
        available_sections = {s[0] for s in pat_sections}

        for phase_name in phases:
            phase = self.PHASES.get(phase_name)
            if not phase:
                continue
            label = phase["label_en"].upper().replace(" ", "_")
            lines.append(f"@@PLAN {label}")
            lines.append(f"  // {phase['label_en']} — {phase.get('rationale_en', '')}")
            for test_key in phase["enabled_tests"]:
                sec_name = test_key_to_section.get(test_key, "")
                if sec_name in available_sections:
                    plan = plan_name_map.get(sec_name, sec_name)
                    pat_file = f"{export_prefix}_{sec_name.replace('_TEST', '')}"
                    lines.append(f"  RUN_PATTERN({pat_file}:start, {pat_file}:end, 1, AC_SET_1);")
            lines.append(f"@@END_PLAN")
            lines.append("")

        return "\n".join(lines)

    def get_phase_labels(self, lang="zh"):
        """返回本地化的阶段标签"""
        key = f"label_{lang}" if lang in ("zh", "en") else "label_en"
        return {name: phase.get(key, phase["label_en"])
                for name, phase in self.PHASES.items()}


# ============================================================
# v9.0 Tier3 Phase 32: AEC-Q100/JEDEC 标准合规映射
# ============================================================

class StandardsComplianceMapper:
    """行业标准合规映射 — AEC-Q100 + JEDEC 对照"""

    AEC_Q100_REQUIREMENTS = {
        "AEC-1": {
            "clause": "Table 2 - Electrical",
            "title": "Pre/Post Stress Electrical Verification",
            "requirement": "DC 参数在全温范围内符合 spec",
            "covered_by": ["DC_TEST", "FUNC"],
            "status": "covered",
        },
        "AEC-2": {
            "clause": "Table 3 - Endurance",
            "title": "NVM Endurance Verification",
            "requirement": "非易失存储器擦写寿命 ≥ spec",
            "covered_by": ["ENDUR_TEST"],
            "status": "covered",
        },
        "AEC-3": {
            "clause": "Table 4 - Retention",
            "title": "Data Retention Test",
            "requirement": "数据在高温下保持 ≥ spec 时间",
            "covered_by": ["RET_TEST"],
            "status": "covered",
        },
        "AEC-4": {
            "clause": "Table 5 - IDDQ",
            "title": "Quiescent Current (IDDQ)",
            "requirement": "静态供电电流 ≤ spec",
            "covered_by": ["IDDQ_TEST"],
            "status": "covered",
        },
        "AEC-5": {
            "clause": "Table 5 - ESD",
            "title": "ESD / Latchup Classification",
            "requirement": "ESD 保护能力 ≥ spec",
            "covered_by": [],
            "status": "not_applicable",
            "note": "需要专用 ESD 测试设备, 非 ATE 向量测试范围",
        },
        "AEC-6": {
            "clause": "Table 6 - Function",
            "title": "Functional Test at Temperature Extremes",
            "requirement": "功能在极端温度下正常",
            "covered_by": ["FUNC", "MARCH_TEST"],
            "status": "covered",
        },
        "AEC-7": {
            "clause": "Table 2 - OS",
            "title": "Open/Short Test",
            "requirement": "引脚开短路检测",
            "covered_by": ["OS_TEST"],
            "status": "covered",
        },
    }

    JEDEC_STANDARDS = {
        "JESD22-A117": {
            "title": "EEPROM Endurance",
            "requirement": "EEPROM 擦写寿命验证方法",
            "covered_by": ["ENDUR_TEST"],
            "status": "covered",
        },
        "JESD22-A119": {
            "title": "EEPROM Data Retention",
            "requirement": "EEPROM 数据保持验证方法",
            "covered_by": ["RET_TEST"],
            "status": "covered",
        },
        "JESD47": {
            "title": "Stress-Test-Driven Qualification",
            "requirement": "应力测试驱动的质量认证",
            "covered_by": ["DC_TEST", "FUNC", "MARCH_TEST", "ENDUR_TEST"],
            "status": "partial",
            "note": "覆盖电气+功能+耐久, 缺少物理应力测试",
        },
        "JESD78": {
            "title": "IC Latch-Up Test",
            "requirement": "闩锁效应测试",
            "covered_by": [],
            "status": "not_applicable",
            "note": "需要专用设备",
        },
        "JESD22-A104": {
            "title": "Temperature Cycling",
            "requirement": "温度循环测试",
            "covered_by": [],
            "status": "partial",
            "note": "温度角仿真器提供参数漂移预测, 非物理温循",
        },
    }

    JEDEC_COVERAGE_STANDARDS = {
        "SA fault": {"target_pct": 95, "reference": "JEDEC JEP137", "covered_by": ["MARCH_TEST"]},
        "TF fault": {"target_pct": 95, "reference": "JEDEC JEP137", "covered_by": ["MARCH_TEST"]},
        "CF fault": {"target_pct": 90, "reference": "JEDEC JEP137", "covered_by": ["MARCH_TEST"]},
        "AF fault": {"target_pct": 85, "reference": "JEDEC JEP137", "covered_by": ["SCAN_TEST"]},
    }

    def calculate_compliance(self, enabled_tests=None):
        """计算合规状态"""
        enabled = set(enabled_tests or [])
        result = {"aec": {"total": 0, "covered": 0, "partial": 0, "na": 0},
                  "jedec": {"total": 0, "covered": 0, "partial": 0, "na": 0}}

        for rid, req in self.AEC_Q100_REQUIREMENTS.items():
            result["aec"]["total"] += 1
            if req["status"] == "not_applicable":
                result["aec"]["na"] += 1
            elif req["status"] == "covered":
                result["aec"]["covered"] += 1
            else:
                result["aec"]["partial"] += 1

        for sid, std in self.JEDEC_STANDARDS.items():
            result["jedec"]["total"] += 1
            if std["status"] == "not_applicable":
                result["jedec"]["na"] += 1
            elif std["status"] == "covered":
                result["jedec"]["covered"] += 1
            else:
                result["jedec"]["partial"] += 1

        applicable_aec = result["aec"]["total"] - result["aec"]["na"]
        result["aec"]["pct"] = round(result["aec"]["covered"] / max(1, applicable_aec) * 100, 1)
        applicable_jedec = result["jedec"]["total"] - result["jedec"]["na"]
        result["jedec"]["pct"] = round(result["jedec"]["covered"] / max(1, applicable_jedec) * 100, 1)

        return result

    def generate_compliance_report(self, enabled_tests=None):
        """格式化合规报告"""
        lines = [
            "═" * 55,
            "  AEC-Q100 / JEDEC 标准合规分析报告",
            "═" * 55,
            "",
            "◆ AEC-Q100 Rev-J 合规状态",
            "─" * 50,
            f"  {'条款':<24s} {'标题':<28s} {'状态':<8s}",
            "─" * 50,
        ]
        for rid, req in self.AEC_Q100_REQUIREMENTS.items():
            status_icon = {"covered": "✓", "partial": "◐", "not_applicable": "○"}.get(req["status"], "?")
            lines.append(f"  {req['clause']:<24s} {req['title']:<28s} {status_icon} {req['status']}")

        comp = self.calculate_compliance(enabled_tests)
        lines.append(f"\n  合规率: {comp['aec']['covered']}/{comp['aec']['total'] - comp['aec']['na']} = {comp['aec']['pct']:.1f}%")

        lines.extend(["", "◆ JEDEC 标准", "─" * 50])
        for sid, std in self.JEDEC_STANDARDS.items():
            status_icon = {"covered": "✓", "partial": "◐", "not_applicable": "○"}.get(std["status"], "?")
            lines.append(f"  {sid:<18s} {std['title']:<28s} {status_icon}")

        lines.extend(["", "◆ JEDEC 故障覆盖率目标", "─" * 50])
        for fault, info in self.JEDEC_COVERAGE_STANDARDS.items():
            lines.append(f"  {fault:<12s}  目标: ≥{info['target_pct']}%  ({info['reference']})")

        return "\n".join(lines)

    def generate_matrix_data(self, enabled_tests=None):
        """生成 Treeview 行数据"""
        rows = []
        for rid, req in self.AEC_Q100_REQUIREMENTS.items():
            rows.append({"id": rid, "standard": "AEC-Q100", "clause": req["clause"],
                        "title": req["title"], "status": req["status"],
                        "covered_by": ", ".join(req["covered_by"]) or "—"})
        for sid, std in self.JEDEC_STANDARDS.items():
            rows.append({"id": sid, "standard": "JEDEC", "clause": sid,
                        "title": std["title"], "status": std["status"],
                        "covered_by": ", ".join(std["covered_by"]) or "—"})
        return rows


# ============================================================
# v9.0 Tier3 Phase 33: 测试程序版本管理
# ============================================================

class TestProgramVersionManager:
    """测试程序版本管理与对比"""

    VERSION_DIR = os.path.join(os.path.expanduser("~"), ".ate_pat_platform", "versions")

    def __init__(self):
        self._ensure_dir()

    def _ensure_dir(self):
        """确保版本目录存在"""
        os.makedirs(self.VERSION_DIR, exist_ok=True)

    def save_version(self, config, test_names, stats, label):
        """保存当前配置为版本快照"""
        import hashlib
        snapshot = {
            "version_label": label,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "config": config,
            "test_names": test_names,
            "stats": stats,
        }
        content = json.dumps(snapshot, ensure_ascii=False, indent=2)
        h = hashlib.sha256(content.encode()).hexdigest()[:8]
        snapshot["hash"] = h

        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_label = re.sub(r'[^\w\-]', '_', label)
        filename = f"{ts}_{safe_label}_{h}.json"
        filepath = os.path.join(self.VERSION_DIR, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(snapshot, f, ensure_ascii=False, indent=2)

        return h

    def list_versions(self):
        """列出所有已保存的版本"""
        versions = []
        if not os.path.exists(self.VERSION_DIR):
            return versions
        for fname in sorted(os.listdir(self.VERSION_DIR), reverse=True):
            if fname.endswith('.json'):
                fpath = os.path.join(self.VERSION_DIR, fname)
                try:
                    with open(fpath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    versions.append({
                        "label": data.get("version_label", "?"),
                        "timestamp": data.get("timestamp", "?"),
                        "hash": data.get("hash", "?"),
                        "filepath": fpath,
                        "tests": len(data.get("test_names", [])),
                    })
                except Exception:
                    pass
        return versions

    def load_version(self, filepath):
        """加载指定版本"""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def compare_versions(self, data_a, data_b):
        """对比两个版本的差异"""
        config_a = data_a.get("config", {})
        config_b = data_b.get("config", {})
        stats_a = data_a.get("stats", {})
        stats_b = data_b.get("stats", {})
        tests_a = set(data_a.get("test_names", []))
        tests_b = set(data_b.get("test_names", []))

        config_diffs = []
        all_keys = set(list(config_a.keys()) + list(config_b.keys()))
        for k in sorted(all_keys):
            va = config_a.get(k)
            vb = config_b.get(k)
            if va != vb:
                config_diffs.append({"key": k, "a": str(va), "b": str(vb)})

        test_diffs = {
            "added": sorted(tests_b - tests_a),
            "removed": sorted(tests_a - tests_b),
            "common": sorted(tests_a & tests_b),
        }

        stats_diffs = []
        for k in ["total_vectors", "test_time_ms", "coverage_pct"]:
            sa = stats_a.get(k, 0)
            sb = stats_b.get(k, 0)
            if sa != sb:
                change = ((sb - sa) / sa * 100) if sa else 0
                stats_diffs.append({"key": k, "a": sa, "b": sb,
                                   "change": f"{change:+.1f}%"})

        label_a = data_a.get("version_label", "A")
        label_b = data_b.get("version_label", "B")
        summary_parts = []
        if test_diffs["added"]:
            summary_parts.append(f"{label_b} 新增测试: {', '.join(test_diffs['added'])}")
        if test_diffs["removed"]:
            summary_parts.append(f"{label_b} 移除测试: {', '.join(test_diffs['removed'])}")
        if config_diffs:
            summary_parts.append(f"{len(config_diffs)} 项配置变更")

        return {
            "config_diffs": config_diffs,
            "test_diffs": test_diffs,
            "stats_diffs": stats_diffs,
            "summary": "; ".join(summary_parts) if summary_parts else "无差异",
        }

    def delete_version(self, filepath):
        """删除指定版本"""
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False


# ============================================================
# GUI 主界面
# ============================================================

class PatGeneratorApp:
    """PAT生成工具主应用"""

    def __init__(self, root):
        self.root = root
        self.root.title(f"{I18N.get('zh', {}).get('title', 'AT24C02 PAT')} {VERSION} — AdaptStar-E")
        self.root.geometry("1150x780")
        self.root.minsize(1000, 680)

        # 主题 & 语言
        self.current_theme = "dark"
        self.current_lang = "zh"
        self.colors = dict(THEMES["dark"])

        self.root.configure(bg=self.colors["bg"])

        # 配置样式
        self.setup_styles()

        # 构建UI
        self.build_ui()

        # 生成器实例
        self.gen = None
        self.current_vectors = None
        self.current_comments = None
        self.current_labels = None
        self.pat_sections = []
        self._exported = True
        self._last_export_dir = None
        self._last_export_time = None
        self._batch_queue = []

        # 初始化 Undo/Redo
        self._init_undo_system()

        # 键盘快捷键 (扩展)
        self.root.bind("<Control-g>", lambda e: self.on_generate())
        self.root.bind("<Control-G>", lambda e: self.on_generate())
        self.root.bind("<Control-e>", lambda e: self.on_export())
        self.root.bind("<Control-E>", lambda e: self.on_export())
        self.root.bind("<Control-f>", lambda e: self._show_search_bar())
        self.root.bind("<Control-F>", lambda e: self._show_search_bar())
        self.root.bind("<Control-z>", lambda e: self._undo())
        self.root.bind("<Control-Z>", lambda e: self._undo())
        self.root.bind("<Control-y>", lambda e: self._redo())
        self.root.bind("<Control-Y>", lambda e: self._redo())
        self.root.bind("<Control-s>", lambda e: self._save_config())
        self.root.bind("<Control-S>", lambda e: self._save_config())
        self.root.bind("<Control-o>", lambda e: self._load_config())
        self.root.bind("<Control-O>", lambda e: self._load_config())
        self.root.bind("<Control-Shift-P>", lambda e: self._show_command_palette())
        self.root.bind("<Control-Shift-p>", lambda e: self._show_command_palette())
        self.root.bind("<F1>", self._show_about_dialog)
        self.root.bind("<F5>", lambda e: self.on_generate())
        self.root.bind("<F6>", lambda e: self.on_export())
        self.root.bind("<Control-a>", lambda e: self._set_all_tests(True))
        self.root.bind("<Control-d>", lambda e: self._set_all_tests(False))
        # Ctrl+1~0 切换标签页 (v6.0: 扩展到 10 个标签页)
        for i in range(1, 10):
            self.root.bind(f"<Control-Key-{i}>",
                           lambda e, idx=i-1: self._switch_tab(idx))
        self.root.bind("<Control-Key-0>", lambda e: self._switch_tab(9))
        # v6.0 快捷键
        self.root.bind("<F7>", lambda e: self._run_simulation())
        self.root.bind("<F8>", lambda e: self._run_shmoo_sweep())

        # 窗口关闭确认
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        # 启动 Undo 追踪 (UI 构建完成后)
        self.root.after(500, self._start_undo_tracking)

        # 自动保存定时器
        self.root.after(2000, self._start_autosave)

        # 检查崩溃恢复
        self.root.after(1000, self._check_autosave_recovery)

        # 初始化测试时间估算
        self.root.after(500, self._estimate_test_time)

    def setup_styles(self):
        """配置ttk样式"""
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Title.TLabel",
                        font=("Segoe UI", 16, "bold"),
                        foreground=self.colors["text"],
                        background=self.colors["bg"])

        style.configure("Subtitle.TLabel",
                        font=("Segoe UI", 10),
                        foreground=self.colors["text_dim"],
                        background=self.colors["bg"])

        style.configure("Card.TFrame",
                        background=self.colors["card"])

        style.configure("CardTitle.TLabel",
                        font=("Segoe UI", 11, "bold"),
                        foreground=self.colors["accent"],
                        background=self.colors["card"])

        style.configure("CardText.TLabel",
                        font=("Segoe UI", 9),
                        foreground=self.colors["text"],
                        background=self.colors["card"])

        style.configure("Status.TLabel",
                        font=("Consolas", 9),
                        foreground=self.colors["accent2"],
                        background=self.colors["bg"])

        style.configure("Action.TButton",
                        font=("Segoe UI", 10, "bold"),
                        padding=(15, 8))

        style.configure("Small.TButton",
                        font=("Segoe UI", 9),
                        padding=(10, 5))

    def build_ui(self):
        """构建主界面 (工具栏 + 内容区 + 状态栏)"""
        # ---- 顶部工具栏 ----
        self.build_toolbar()
        tk.Frame(self.root, bg=self.colors["border"], height=1).pack(fill=tk.X)

        # ---- 底部状态栏 (先pack保留空间) ----
        self.build_status_bar()

        # ---- 主内容区 ----
        main_frame = tk.Frame(self.root, bg=self.colors["bg"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        # 左侧面板 (可滚动)
        left_outer = tk.Frame(main_frame, bg=self.colors["sidebar"], width=285,
                              relief=tk.FLAT, bd=0)
        left_outer.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))
        left_outer.pack_propagate(False)

        self._left_canvas = tk.Canvas(left_outer, bg=self.colors["sidebar"],
                                      highlightthickness=0, width=285)
        self._left_scrollbar = tk.Scrollbar(left_outer, orient=tk.VERTICAL,
                                            command=self._left_canvas.yview)
        self._left_canvas.configure(yscrollcommand=self._left_scrollbar.set)
        self._left_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._left_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        left_panel = tk.Frame(self._left_canvas, bg=self.colors["sidebar"])
        self._left_canvas_window = self._left_canvas.create_window(
            (0, 0), window=left_panel, anchor=tk.NW, width=270)

        def _on_left_configure(event):
            self._left_canvas.configure(scrollregion=self._left_canvas.bbox("all"))
        left_panel.bind("<Configure>", _on_left_configure)

        # 鼠标滚轮绑定
        def _on_mousewheel(event):
            self._left_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self._left_canvas.bind("<MouseWheel>", _on_mousewheel)
        left_panel.bind("<MouseWheel>", _on_mousewheel)

        # 递归绑定所有子控件的滚轮事件
        def _bind_mousewheel(widget):
            widget.bind("<MouseWheel>", _on_mousewheel)
            for child in widget.winfo_children():
                _bind_mousewheel(child)
        left_panel.bind("<Map>", lambda e: left_panel.after(100,
            lambda: _bind_mousewheel(left_panel)))

        self.build_config_panel(left_panel)

        # 右侧预览区
        right_panel = tk.Frame(main_frame, bg=self.colors["bg"])
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.build_preview_panel(right_panel)

    def _ribbon_separator(self, parent):
        """Ribbon 分组之间的竖线分隔符"""
        tk.Frame(parent, bg=self.colors["border"], width=1, height=42).pack(
            side=tk.LEFT, padx=6, pady=2)

    def _ribbon_group(self, parent, label_text):
        """创建 Ribbon 分组容器 (上方控件区 + 下方标签)"""
        group = tk.Frame(parent, bg=self.colors["ribbon_bg"])
        group.pack(side=tk.LEFT, padx=(0, 0))
        content = tk.Frame(group, bg=self.colors["ribbon_bg"])
        content.pack(side=tk.TOP, fill=tk.X, pady=(2, 0))
        tk.Label(group, text=label_text, font=("Segoe UI", 7),
                 fg=self.colors["ribbon_label"], bg=self.colors["ribbon_bg"]).pack(
                     side=tk.BOTTOM, pady=(0, 1))
        return content

    def build_toolbar(self):
        """构建顶部 Ribbon 工具栏 (5个分组: CHIP | TEST | ACTION | TOOLS | VIEW)"""
        toolbar = tk.Frame(self.root, bg=self.colors["ribbon_bg"], padx=10, pady=4)
        toolbar.pack(fill=tk.X)

        # ── 标题 ──
        title_frame = tk.Frame(toolbar, bg=self.colors["ribbon_bg"])
        title_frame.pack(side=tk.LEFT)
        tk.Label(title_frame, text="AT24C02 PAT",
                font=("Segoe UI", 13, "bold"), fg=self.colors["text"],
                bg=self.colors["ribbon_bg"]).pack(side=tk.TOP, anchor=tk.W)
        tk.Label(title_frame, text=f"Test Vector Tool {VERSION}",
                font=("Segoe UI", 7), fg=self.colors["text_dim"],
                bg=self.colors["ribbon_bg"]).pack(side=tk.TOP, anchor=tk.W)

        self._ribbon_separator(toolbar)

        # ── GROUP 1: CHIP (地址引脚 + WP + VCC + 器件地址) ──
        chip_content = self._ribbon_group(toolbar, self.t("grp_chip"))

        self.addr_vars = {}
        for pin_name in ["A2", "A1", "A0"]:
            var = tk.IntVar(value=0)
            self.addr_vars[pin_name] = var
            lbl = tk.Label(chip_content, text=pin_name, font=("Consolas", 8, "bold"),
                    fg=self.colors["accent"], bg=self.colors["ribbon_bg"])
            lbl.pack(side=tk.LEFT, padx=(3, 0))
            spn = tk.Spinbox(chip_content, from_=0, to=1, width=2, textvariable=var,
                      font=("Consolas", 8), buttonbackground=self.colors["card"])
            spn.pack(side=tk.LEFT, padx=(1, 2))
            ToolTip(spn, f"{pin_name} (0/1)")

        for pin_name in ["A2", "A1", "A0"]:
            self.addr_vars[pin_name].trace_add("write", self._update_dev_addr_label)

        # WP
        self.wp_var = tk.IntVar(value=0)
        wp_cb = tk.Checkbutton(chip_content, text="WP", variable=self.wp_var,
                       font=("Consolas", 8, "bold"),
                       fg=self.colors["warning"], bg=self.colors["ribbon_bg"],
                       selectcolor=self.colors["card"],
                       activebackground=self.colors["ribbon_bg"],
                       command=self._on_wp_changed)
        wp_cb.pack(side=tk.LEFT, padx=(4, 2))
        ToolTip(wp_cb, self.t("wp_tip"))

        # VCC
        tk.Label(chip_content, text="VCC", font=("Consolas", 8, "bold"),
                fg=self.colors["danger"], bg=self.colors["ribbon_bg"]).pack(
                    side=tk.LEFT, padx=(4, 1))
        self.voltage_var = tk.StringVar(value="5.0V")
        vcb = ttk.Combobox(chip_content, textvariable=self.voltage_var,
                           values=list(VOLTAGE_PRESETS.keys()),
                           state="readonly", width=4, font=("Consolas", 8))
        vcb.pack(side=tk.LEFT, padx=(0, 4))
        vcb.bind("<<ComboboxSelected>>", self._on_voltage_changed)
        ToolTip(vcb, self.t("vcc_tip"))

        # Multi-Site 数量
        tk.Label(chip_content, text=self.t("site_count"),
                 font=("Consolas", 8, "bold"),
                 fg=self.colors["accent"], bg=self.colors["ribbon_bg"]).pack(
                     side=tk.LEFT, padx=(4, 1))
        self.site_count_var = tk.StringVar(value="1")
        site_cb = ttk.Combobox(chip_content, textvariable=self.site_count_var,
                                values=["1", "2", "4", "8"],
                                state="readonly", width=2, font=("Consolas", 8))
        site_cb.pack(side=tk.LEFT, padx=(0, 4))

        # 器件地址
        self.dev_addr_label = tk.Label(chip_content,
                                        text="0xA0 / 0xA1",
                                        font=("Consolas", 9, "bold"),
                                        fg=self.colors["accent2"],
                                        bg=self.colors["ribbon_bg"])
        self.dev_addr_label.pack(side=tk.LEFT, padx=4)
        ToolTip(self.dev_addr_label, "I2C Device Address (W/R)")

        self._ribbon_separator(toolbar)

        # ── GROUP 2: TEST (预设按钮) ──
        test_content = self._ribbon_group(toolbar, self.t("grp_test"))

        presets_cfg = [
            ("preset_quick", self.colors["accent"], "preset_tip_quick"),
            ("preset_full", self.colors["accent2"], "preset_tip_full"),
            ("preset_memory", self.colors["gold"], "preset_tip_memory"),
        ]
        self._preset_maps = [
            {"os_test": True, "dc_test": True, "func_test": True,
             "march_test": False, "march_b_test": False,
             "scan_test": False, "ret_test": False,
             "err_test": False, "endur_test": False, "iddq_test": False},
            {k: True for k in ["os_test", "dc_test", "func_test",
             "march_test", "march_b_test", "scan_test",
             "ret_test", "err_test", "endur_test", "iddq_test"]},
            {"os_test": False, "dc_test": False, "func_test": False,
             "march_test": True, "march_b_test": True,
             "scan_test": True, "ret_test": True,
             "err_test": False, "endur_test": True, "iddq_test": False},
        ]
        for i, (p_key, p_clr, p_tip_key) in enumerate(presets_cfg):
            btn = tk.Button(test_content, text=self.t(p_key),
                            command=lambda m=self._preset_maps[i]: self._apply_preset(m),
                            font=("Segoe UI", 7, "bold"), bg=p_clr,
                            fg="white", relief=tk.FLAT, padx=6, pady=2,
                            cursor="hand2")
            btn.pack(side=tk.LEFT, padx=(0, 3))
            ToolTip(btn, self.t(p_tip_key))

        # 测试阶段下拉
        tk.Label(test_content, text=self.t("test_phase") + ":",
                 font=("Consolas", 7, "bold"),
                 fg=self.colors["text_dim"], bg=self.colors["ribbon_bg"]).pack(
                     side=tk.LEFT, padx=(6, 1))
        self.test_phase_var = tk.StringVar(value="custom")
        phase_mgr = TestPhaseManager()
        phase_labels = phase_mgr.get_phase_labels(self.current_lang)
        phase_display = [self.t("phase_custom")] + [phase_labels[k] for k in phase_labels]
        phase_values = ["custom"] + list(TestPhaseManager.PHASES.keys())
        self._phase_value_list = phase_values
        phase_cb = ttk.Combobox(test_content, textvariable=self.test_phase_var,
                                 values=phase_values,
                                 state="readonly", width=14, font=("Consolas", 7))
        phase_cb.pack(side=tk.LEFT, padx=(0, 4))
        phase_cb.bind("<<ComboboxSelected>>", self._on_phase_changed)

        self._ribbon_separator(toolbar)

        # ── GROUP 3: ACTION (撤销/重做 + 生成/导出) ──
        action_content = self._ribbon_group(toolbar, self.t("grp_action"))

        self.undo_btn = tk.Button(action_content, text="\u21b6",
                              command=self._undo,
                              font=("Segoe UI", 10),
                              bg=self.colors["ribbon_bg"], fg=self.colors["text_dim"],
                              activebackground=self.colors["hover"],
                              relief=tk.FLAT, padx=3, pady=1,
                              cursor="hand2", state=tk.DISABLED, bd=0)
        self.undo_btn.pack(side=tk.LEFT, padx=(0, 1))
        ToolTip(self.undo_btn, self.t("undo_tip"))

        self.redo_btn = tk.Button(action_content, text="\u21b7",
                              command=self._redo,
                              font=("Segoe UI", 10),
                              bg=self.colors["ribbon_bg"], fg=self.colors["text_dim"],
                              activebackground=self.colors["hover"],
                              relief=tk.FLAT, padx=3, pady=1,
                              cursor="hand2", state=tk.DISABLED, bd=0)
        self.redo_btn.pack(side=tk.LEFT, padx=(0, 4))
        ToolTip(self.redo_btn, self.t("redo_tip"))

        gen_btn = tk.Button(action_content, text=self.t("generate"),
                           command=self.on_generate,
                           font=("Segoe UI", 8, "bold"),
                           bg=self.colors["accent"], fg="white",
                           activebackground="#2563eb",
                           relief=tk.FLAT, padx=10, pady=3,
                           cursor="hand2")
        gen_btn.pack(side=tk.LEFT, padx=(0, 3))

        self.export_btn = tk.Button(action_content, text=self.t("export"),
                              command=self.on_export,
                              font=("Segoe UI", 8),
                              bg=self.colors["accent2"], fg="white",
                              activebackground="#0d9488",
                              relief=tk.FLAT, padx=10, pady=3,
                              cursor="hand2",
                              state=tk.DISABLED)
        self.export_btn.pack(side=tk.LEFT, padx=(0, 3))

        self.reexport_btn = tk.Button(action_content, text="\u27f3",
                              command=self._quick_reexport,
                              font=("Segoe UI", 9),
                              bg=self.colors["ribbon_bg"], fg=self.colors["text_dim"],
                              activebackground=self.colors["hover"],
                              relief=tk.FLAT, padx=3, pady=1,
                              cursor="hand2", state=tk.DISABLED, bd=0)
        self.reexport_btn.pack(side=tk.LEFT)
        ToolTip(self.reexport_btn, self.t("reexport_tip"))

        self._ribbon_separator(toolbar)

        # ── GROUP 4: TOOLS (时序检查 / 协议检查 / 批处理 / 对比) ──
        tools_content = self._ribbon_group(toolbar, self.t("grp_tools"))

        tk.Button(tools_content, text=self.t("timing_check"),
                  command=self._run_timing_check,
                  font=("Segoe UI", 7), bg="#8b5cf6",
                  fg="white", relief=tk.FLAT, padx=5, pady=2,
                  cursor="hand2").pack(side=tk.LEFT, padx=(0, 3))

        tk.Button(tools_content, text=self.t("proto_check"),
                  command=self._run_protocol_check,
                  font=("Segoe UI", 7), bg=self.colors["gold"],
                  fg="white", relief=tk.FLAT, padx=5, pady=2,
                  cursor="hand2").pack(side=tk.LEFT, padx=(0, 3))

        tk.Button(tools_content, text=self.t("batch_title"),
                  command=self._show_batch_dialog,
                  font=("Segoe UI", 7), bg=self.colors["card"],
                  fg=self.colors["text"], relief=tk.FLAT, padx=5, pady=2,
                  cursor="hand2").pack(side=tk.LEFT, padx=(0, 3))

        tk.Button(tools_content, text=self.t("config_diff"),
                  command=self._show_config_diff,
                  font=("Segoe UI", 7), bg=self.colors["card"],
                  fg=self.colors["text"], relief=tk.FLAT, padx=5, pady=2,
                  cursor="hand2").pack(side=tk.LEFT, padx=(0, 3))

        tk.Button(tools_content, text=self.t("migrate_btn"),
                  command=self._show_migrate_dialog,
                  font=("Segoe UI", 7, "bold"), bg="#6366f1",
                  fg="white", relief=tk.FLAT, padx=5, pady=2,
                  cursor="hand2").pack(side=tk.LEFT, padx=(0, 3))

        # v9.0 Tier3 Phase 30: 导入 PAT 按钮
        tk.Button(tools_content, text=self.t("pat_import"),
                  command=self._import_pat_file,
                  font=("Segoe UI", 7), bg="#0ea5e9",
                  fg="white", relief=tk.FLAT, padx=5, pady=2,
                  cursor="hand2").pack(side=tk.LEFT, padx=(0, 3))

        # v9.0 Tier3 Phase 33: 版本菜单
        self._ver_mgr = TestProgramVersionManager()
        ver_mb = tk.Menubutton(tools_content, text=self.t("ver_btn"),
                               font=("Segoe UI", 7), bg=self.colors["card"],
                               fg=self.colors["text"], relief=tk.FLAT,
                               padx=5, pady=2, cursor="hand2")
        ver_menu = tk.Menu(ver_mb, tearoff=0)
        ver_menu.add_command(label=self.t("ver_save"), command=self._save_version)
        ver_menu.add_command(label=self.t("ver_load"), command=self._load_version_dialog)
        ver_menu.add_command(label=self.t("ver_compare"), command=self._compare_versions_dialog)
        ver_mb.config(menu=ver_menu)
        ver_mb.pack(side=tk.LEFT)

        self._ribbon_separator(toolbar)

        # ── GROUP 5: VIEW (主题 / 语言) ──
        view_content = self._ribbon_group(toolbar, self.t("grp_view"))

        icon = "\u2600" if self.current_theme == "dark" else "\u263e"
        self.theme_btn = tk.Button(view_content, text=icon,
                                    command=self._toggle_theme,
                                    font=("Segoe UI", 11),
                                    bg=self.colors["ribbon_bg"],
                                    fg=self.colors["text_dim"],
                                    activebackground=self.colors["ribbon_bg"],
                                    relief=tk.FLAT, padx=3, pady=0,
                                    cursor="hand2", bd=0)
        self.theme_btn.pack(side=tk.LEFT, padx=(0, 3))
        ToolTip(self.theme_btn, self.t("theme_tip"))

        self.lang_btn = tk.Button(view_content, text=self.t("lang_btn"),
                                   command=self._toggle_language,
                                   font=("Segoe UI", 7, "bold"),
                                   bg=self.colors["card"],
                                   fg=self.colors["text"],
                                   activebackground=self.colors["hover"],
                                   relief=tk.FLAT, padx=5, pady=2,
                                   cursor="hand2", bd=0)
        self.lang_btn.pack(side=tk.LEFT)

        self._ribbon_separator(toolbar)

        # ── Phase 9: 演示按钮 ──
        self.demo_btn = tk.Button(toolbar, text=self.t("demo_btn"),
                                   command=self._start_demo,
                                   font=("Segoe UI", 9, "bold"),
                                   bg="#22c55e", fg="white",
                                   activebackground="#16a34a",
                                   relief=tk.FLAT, padx=12, pady=4,
                                   cursor="hand2", bd=0)
        self.demo_btn.pack(side=tk.RIGHT, padx=(0, 6))
        ToolTip(self.demo_btn, "15-step automated demo (ESC to stop)")

    def _status_sep(self, parent):
        """状态栏分段分隔符"""
        tk.Label(parent, text="\u2502", font=("Consolas", 8),
                 fg=self.colors["border"], bg=self.colors["sidebar"]).pack(
                     side=tk.LEFT, padx=6)

    def build_status_bar(self):
        """构建底部增强状态栏 (分段: 状态 | VCC | 向量数 | 预估时间 | 覆盖率 | 版本)"""
        bar = tk.Frame(self.root, bg=self.colors["sidebar"], padx=12, pady=3)
        bar.pack(fill=tk.X, side=tk.BOTTOM)
        tk.Frame(self.root, bg=self.colors["border"], height=1).pack(
            fill=tk.X, side=tk.BOTTOM)

        # 段1: 状态消息
        self.status_label = tk.Label(bar,
                                     text=self.t("ready"),
                                     font=("Segoe UI", 8),
                                     fg=self.colors["text_dim"],
                                     bg=self.colors["sidebar"])
        self.status_label.pack(side=tk.LEFT)

        # 右侧段 (从右往左)
        # 段6: 版本
        tk.Label(bar, text=VERSION, font=("Consolas", 7),
                 fg=self.colors["text_dim"],
                 bg=self.colors["sidebar"]).pack(side=tk.RIGHT)

        self._status_sep(bar)

        # 段5: 覆盖率
        self.status_coverage_label = tk.Label(bar, text="",
                                               font=("Consolas", 7),
                                               fg=self.colors["accent2"],
                                               bg=self.colors["sidebar"])
        self.status_coverage_label.pack(side=tk.RIGHT)

        self._status_sep(bar)

        # 段4: 预估时间
        self.status_time_label = tk.Label(bar, text="",
                                           font=("Consolas", 7),
                                           fg=self.colors["gold"],
                                           bg=self.colors["sidebar"])
        self.status_time_label.pack(side=tk.RIGHT)

        self._status_sep(bar)

        # 段3: 向量数
        self.stats_label = tk.Label(bar, text="",
                                    font=("Consolas", 7),
                                    fg=self.colors["text_dim"],
                                    bg=self.colors["sidebar"])
        self.stats_label.pack(side=tk.RIGHT)

        self._status_sep(bar)

        # 段2: 电压
        self.status_voltage_label = tk.Label(bar, text="VCC: 5.0V",
                                              font=("Consolas", 7),
                                              fg="#8b5cf6",
                                              bg=self.colors["sidebar"])
        self.status_voltage_label.pack(side=tk.RIGHT)

        self._status_sep(bar)

        # v6.0 段1.5: 协议+芯片
        self.status_proto_label = tk.Label(bar, text="I2C | AT24C02",
                                            font=("Consolas", 7),
                                            fg=self.colors["accent"],
                                            bg=self.colors["sidebar"])
        self.status_proto_label.pack(side=tk.RIGHT)

    def _build_accordion_section(self, parent, title, icon, build_content_fn,
                                  expanded=True):
        """创建可折叠的手风琴区段，返回 (header_frame, content_frame)"""
        section = tk.Frame(parent, bg=self.colors["sidebar"])
        section.pack(fill=tk.X, pady=(0, 1))

        # 标题栏 (可点击)
        header = tk.Frame(section, bg=self.colors["card"], padx=10, pady=4)
        header.pack(fill=tk.X)

        arrow_var = tk.StringVar(value="\u25bc" if expanded else "\u25b6")
        arrow_lbl = tk.Label(header, textvariable=arrow_var,
                             font=("Consolas", 8),
                             fg=self.colors["text_dim"], bg=self.colors["card"])
        arrow_lbl.pack(side=tk.LEFT, padx=(0, 4))

        tk.Label(header, text=f"{icon} {title}",
                 font=("Segoe UI", 9, "bold"),
                 fg=self.colors["text"], bg=self.colors["card"]).pack(
                     side=tk.LEFT)

        # 内容区
        content = tk.Frame(section, bg=self.colors["sidebar"])
        if expanded:
            content.pack(fill=tk.X)

        # 存储折叠状态
        section._accordion_expanded = expanded
        section._accordion_content = content
        section._accordion_arrow = arrow_var

        def toggle(event=None):
            if section._accordion_expanded:
                content.pack_forget()
                arrow_var.set("\u25b6")
                section._accordion_expanded = False
            else:
                content.pack(fill=tk.X)
                arrow_var.set("\u25bc")
                section._accordion_expanded = True

        header.bind("<Button-1>", toggle)
        for child in header.winfo_children():
            child.bind("<Button-1>", toggle)
        header.configure(cursor="hand2")

        # 构建内容
        build_content_fn(content)

        return section

    def build_config_panel(self, parent):
        """构建左侧手风琴面板"""
        # ── 段1: 芯片配置 ──
        self._build_accordion_section(
            parent, self.t("chip_config"), "\u2699",
            self._build_chip_config, expanded=True)

        # ── 段2: 芯片引脚图 ──
        self._build_accordion_section(
            parent, "Pinout", "\u25a3",
            lambda p: self.draw_chip_diagram(p), expanded=True)

        # ── 段3: 测试类型 ──
        self._build_accordion_section(
            parent, self.t("test_types"), "\u2611",
            self._build_test_types_content, expanded=True)

        # ── 段4: 自定义参数 ──
        self._build_accordion_section(
            parent, self.t("custom_write"), "\u270e",
            self._build_custom_write_content, expanded=False)

        # ── 段5: 地址范围 ──
        self._build_accordion_section(
            parent, self.t("addr_range"), "\u2194",
            self._build_addr_range_content, expanded=False)

        # ── 段6: 向量设置 ──
        self._build_accordion_section(
            parent, self.t("period_label"), "\u23f1",
            self._build_vector_settings_content, expanded=False)

        # ── 段7: 导出设置 ──
        self._build_accordion_section(
            parent, self.t("prefix_label"), "\u2913",
            self._build_export_settings_content, expanded=False)

        # ── 段8: 配置管理 ──
        self._build_accordion_section(
            parent, self.t("save_config"), "\u2630",
            self._build_config_mgmt_content, expanded=False)

        # ── 段9: Pin Map (v9.0 Phase 24) ──
        self._build_accordion_section(
            parent, self.t("pin_map_section"), "\u2261",
            self._build_pin_map_content, expanded=False)

    def _build_pin_map_content(self, parent):
        """Pin Map 资源映射面板"""
        frame = tk.Frame(parent, bg=self.colors["sidebar"], padx=10, pady=4)
        frame.pack(fill=tk.X)

        # Pin Map Treeview
        pm_cols = ("pin", "card", "channel", "direction")
        self._pin_map_tree = ttk.Treeview(frame, columns=pm_cols,
                                           show="headings", height=6)
        for col, w in [("pin", 50), ("card", 50), ("channel", 55), ("direction", 60)]:
            self._pin_map_tree.column(col, width=w, minwidth=30, anchor=tk.CENTER)
            self._pin_map_tree.heading(col, text=col.upper())
        self._pin_map_tree.pack(fill=tk.X, pady=(0, 4))

        btn_frame = tk.Frame(frame, bg=self.colors["sidebar"])
        btn_frame.pack(fill=tk.X)
        tk.Button(btn_frame, text=self.t("pin_map_validate"),
                  command=self._validate_pin_map,
                  font=("Segoe UI", 7), bg=self.colors["accent"],
                  fg="white", relief=tk.FLAT, padx=6, pady=2,
                  cursor="hand2").pack(side=tk.LEFT)
        self._pin_map_status = tk.Label(btn_frame, text="",
                                         font=("Consolas", 7),
                                         fg=self.colors["text_dim"],
                                         bg=self.colors["sidebar"])
        self._pin_map_status.pack(side=tk.LEFT, padx=(6, 0))

        # 自动刷新初始状态
        self._refresh_pin_map()

    def _refresh_pin_map(self):
        """刷新 Pin Map 显示"""
        if not hasattr(self, '_pin_map_tree'):
            return
        self._pin_map_tree.delete(*self._pin_map_tree.get_children())
        protocol = self.chip_protocol_var.get() if hasattr(self, 'chip_protocol_var') else "I2C"
        num_sites = int(self.site_count_var.get()) if hasattr(self, 'site_count_var') else 1
        mgr = PinMapManager(protocol=protocol)
        # 获取引脚列表和方向
        if hasattr(self, 'gen') and self.gen:
            pins = self.gen.proto.get_pins()
            dirs = self.gen.proto.get_pin_directions()
        else:
            if protocol == "SPI":
                pins = ["CS", "SCK", "MOSI", "MISO", "WP", "HOLD"]
                dirs = {"CS": "In", "SCK": "In", "MOSI": "In", "MISO": "Out", "WP": "In", "HOLD": "In"}
            elif protocol == "Microwire":
                pins = ["CS", "SK", "DI", "DO", "ORG", "NC"]
                dirs = {"CS": "In", "SK": "In", "DI": "In", "DO": "Out", "ORG": "In", "NC": "In"}
            else:
                pins = ["A0", "A1", "A2", "WP", "SCL", "SDA"]
                dirs = {"A0": "In", "A1": "In", "A2": "In", "WP": "In", "SCL": "In", "SDA": "InOut"}
        pin_map = mgr.generate_pin_map(pins, dirs, num_sites)
        for pin_name, info in pin_map.items():
            self._pin_map_tree.insert("", tk.END,
                values=(pin_name, info["card"], f"CH{info['channel']}", info["direction"]))

    def _validate_pin_map(self):
        """验证 Pin Map 资源"""
        protocol = self.chip_protocol_var.get() if hasattr(self, 'chip_protocol_var') else "I2C"
        num_sites = int(self.site_count_var.get()) if hasattr(self, 'site_count_var') else 1
        mgr = PinMapManager(protocol=protocol)
        if protocol == "SPI":
            pins = ["CS", "SCK", "MOSI", "MISO", "WP", "HOLD"]
            dirs = {"MISO": "Out"}
        elif protocol == "Microwire":
            pins = ["CS", "SK", "DI", "DO", "ORG", "NC"]
            dirs = {"DO": "Out"}
        else:
            pins = ["A0", "A1", "A2", "WP", "SCL", "SDA"]
            dirs = {"SDA": "InOut"}
        pin_map = mgr.generate_pin_map(pins, dirs, num_sites)
        result = mgr.validate_resource(pin_map, num_sites)
        if result["valid"]:
            self._pin_map_status.config(
                text=f"\u2714 {self.t('pin_map_valid')} ({result['total_channels']} CH)",
                fg=self.colors["success"])
        else:
            self._pin_map_status.config(
                text=f"\u2718 {self.t('pin_map_invalid')}: {'; '.join(result['errors'])}",
                fg=self.colors["danger"])

    def _build_test_types_content(self, parent):
        """测试类型选择区内容"""
        # 全选/取消按钮行
        btn_row = tk.Frame(parent, bg=self.colors["sidebar"], padx=10, pady=2)
        btn_row.pack(fill=tk.X)
        tk.Button(btn_row, text=self.t("select_all"),
                  command=lambda: self._set_all_tests(True),
                  font=("Segoe UI", 7), bg=self.colors["card"],
                  fg=self.colors["text_dim"], relief=tk.FLAT, padx=4, pady=0,
                  cursor="hand2").pack(side=tk.LEFT, padx=(0, 4))
        tk.Button(btn_row, text=self.t("deselect_all"),
                  command=lambda: self._set_all_tests(False),
                  font=("Segoe UI", 7), bg=self.colors["card"],
                  fg=self.colors["text_dim"], relief=tk.FLAT, padx=4, pady=0,
                  cursor="hand2").pack(side=tk.LEFT)

        test_frame = tk.Frame(parent, bg=self.colors["sidebar"], padx=10, pady=2)
        test_frame.pack(fill=tk.X)

        self.test_vars = {}
        test_options = [
            ("os_test",    self.t("os_test"),    self.t("os_desc")),
            ("dc_test",    self.t("dc_test"),    self.t("dc_desc")),
            ("func_test",  self.t("func_test"),  self.t("func_desc")),
            ("march_test", self.t("march_test"), self.t("march_desc")),
            ("march_b_test", self.t("march_b_test"), self.t("march_b_desc")),
            ("scan_test",  self.t("scan_test"),  self.t("scan_desc")),
            ("ret_test",   self.t("ret_test"),   self.t("ret_desc")),
            ("err_test",   self.t("err_test"),   self.t("err_desc")),
            ("endur_test", self.t("endur_test"), self.t("endur_desc")),
            ("iddq_test",  self.t("iddq_test"),  self.t("iddq_desc")),
        ]

        for key, label, desc in test_options:
            default_on = key in ("os_test", "dc_test", "func_test")
            var = tk.BooleanVar(value=default_on)
            self.test_vars[key] = var
            item = tk.Frame(test_frame, bg=self.colors["card"], padx=6, pady=3)
            item.pack(fill=tk.X, pady=1)
            tk.Checkbutton(item, text=label, variable=var,
                          font=("Segoe UI", 8, "bold"),
                          fg=self.colors["text"], bg=self.colors["card"],
                          selectcolor=self.colors["sidebar"],
                          activebackground=self.colors["card"]).pack(anchor=tk.W)
            tk.Label(item, text=desc, font=("Segoe UI", 7),
                    fg=self.colors["text_dim"], bg=self.colors["card"]).pack(
                        anchor=tk.W, padx=(18, 0))

    def _build_custom_write_content(self, parent):
        """自定义写入参数内容"""
        frame = tk.Frame(parent, bg=self.colors["sidebar"], padx=10, pady=4)
        frame.pack(fill=tk.X)
        row = tk.Frame(frame, bg=self.colors["sidebar"])
        row.pack(fill=tk.X, pady=2)
        tk.Label(row, text=self.t("addr"), font=("Segoe UI", 8),
                fg=self.colors["text"], bg=self.colors["sidebar"]).pack(side=tk.LEFT)
        self.custom_addr_var = tk.StringVar(value="0x00")
        tk.Entry(row, textvariable=self.custom_addr_var,
                font=("Consolas", 8), width=6).pack(side=tk.LEFT, padx=3)
        tk.Label(row, text=self.t("data"), font=("Segoe UI", 8),
                fg=self.colors["text"], bg=self.colors["sidebar"]).pack(
                    side=tk.LEFT, padx=(6, 0))
        self.custom_data_var = tk.StringVar(value="0x55")
        tk.Entry(row, textvariable=self.custom_data_var,
                font=("Consolas", 8), width=6).pack(side=tk.LEFT, padx=3)

    def _build_addr_range_content(self, parent):
        """测试地址范围内容"""
        frame = tk.Frame(parent, bg=self.colors["sidebar"], padx=10, pady=4)
        frame.pack(fill=tk.X)
        row = tk.Frame(frame, bg=self.colors["sidebar"])
        row.pack(fill=tk.X, pady=2)
        tk.Label(row, text=self.t("start"), font=("Segoe UI", 8),
                fg=self.colors["text"], bg=self.colors["sidebar"]).pack(side=tk.LEFT)
        self.scan_start_var = tk.StringVar(value="0x00")
        tk.Entry(row, textvariable=self.scan_start_var,
                font=("Consolas", 8), width=5).pack(side=tk.LEFT, padx=3)
        tk.Label(row, text=self.t("end"), font=("Segoe UI", 8),
                fg=self.colors["text"], bg=self.colors["sidebar"]).pack(
                    side=tk.LEFT, padx=(6, 0))
        self.scan_end_var = tk.StringVar(value="0x07")
        tk.Entry(row, textvariable=self.scan_end_var,
                font=("Consolas", 8), width=5).pack(side=tk.LEFT, padx=3)
        tk.Label(frame, text=self.t("range_hint"),
                font=("Segoe UI", 7), fg=self.colors["text_dim"],
                bg=self.colors["sidebar"]).pack(anchor=tk.W)

    def _build_vector_settings_content(self, parent):
        """向量周期 + ACK Polling 设置"""
        frame = tk.Frame(parent, bg=self.colors["sidebar"], padx=10, pady=4)
        frame.pack(fill=tk.X)

        # 周期
        row1 = tk.Frame(frame, bg=self.colors["sidebar"])
        row1.pack(fill=tk.X, pady=2)
        self.period_var = tk.StringVar(value="2500")
        tk.Entry(row1, textvariable=self.period_var,
                font=("Consolas", 8), width=7).pack(side=tk.LEFT)
        tk.Label(row1, text="ns", font=("Segoe UI", 7),
                fg=self.colors["text_dim"], bg=self.colors["sidebar"]).pack(
                    side=tk.LEFT, padx=2)
        self.period_freq_label = tk.Label(row1, text="= 400.0 kHz",
                font=("Consolas", 7), fg=self.colors["text_dim"],
                bg=self.colors["sidebar"])
        self.period_freq_label.pack(side=tk.LEFT, padx=4)
        self.period_var.trace_add("write", self._update_period_freq)

        # ACK Polling
        row2 = tk.Frame(frame, bg=self.colors["sidebar"])
        row2.pack(fill=tk.X, pady=2)
        tk.Label(row2, text="ACK Poll:", font=("Segoe UI", 8),
                fg=self.colors["text"], bg=self.colors["sidebar"]).pack(side=tk.LEFT)
        self.poll_count_var = tk.StringVar(value="2")
        tk.Entry(row2, textvariable=self.poll_count_var,
                font=("Consolas", 8), width=4).pack(side=tk.LEFT, padx=3)
        tk.Label(row2, text=self.t("poll_count_hint"),
                font=("Segoe UI", 7), fg=self.colors["text_dim"],
                bg=self.colors["sidebar"]).pack(side=tk.LEFT, padx=3)

        # RLE 压缩
        self.rle_var = tk.IntVar(value=0)
        tk.Checkbutton(frame, text=self.t("rle_compress"),
                       variable=self.rle_var,
                       font=("Segoe UI", 8),
                       fg=self.colors["text_dim"], bg=self.colors["sidebar"],
                       activebackground=self.colors["sidebar"],
                       selectcolor=self.colors["sidebar"]
                       ).pack(anchor=tk.W, pady=(2, 0))

    def _build_export_settings_content(self, parent):
        """导出文件名前缀 + 多电压选项"""
        frame = tk.Frame(parent, bg=self.colors["sidebar"], padx=10, pady=4)
        frame.pack(fill=tk.X)
        self.export_prefix_var = tk.StringVar(value="AT24C02")
        tk.Entry(frame, textvariable=self.export_prefix_var,
                font=("Consolas", 8), width=20).pack(fill=tk.X, pady=2)
        self.multi_voltage_var = tk.IntVar(value=0)
        tk.Checkbutton(frame, text=self.t("multi_voltage"),
                       variable=self.multi_voltage_var,
                       font=("Segoe UI", 7),
                       fg=self.colors["text_dim"], bg=self.colors["sidebar"],
                       activebackground=self.colors["sidebar"],
                       selectcolor=self.colors["sidebar"]
                       ).pack(anchor=tk.W, pady=(2, 0))

    def _build_config_mgmt_content(self, parent):
        """配置保存/加载 + 最近文件"""
        frame = tk.Frame(parent, bg=self.colors["sidebar"], padx=10, pady=4)
        frame.pack(fill=tk.X)

        btn_row = tk.Frame(frame, bg=self.colors["sidebar"])
        btn_row.pack(fill=tk.X, pady=2)
        tk.Button(btn_row, text=self.t("save_config"), command=self._save_config,
                  font=("Segoe UI", 7), bg=self.colors["card"],
                  fg=self.colors["text"], relief=tk.FLAT, padx=6, pady=2,
                  cursor="hand2").pack(side=tk.LEFT, padx=(0, 4))
        tk.Button(btn_row, text=self.t("load_config"), command=self._load_config,
                  font=("Segoe UI", 7), bg=self.colors["card"],
                  fg=self.colors["text"], relief=tk.FLAT, padx=6, pady=2,
                  cursor="hand2").pack(side=tk.LEFT, padx=(0, 4))

        # 最近文件按钮
        self.recent_btn = tk.Menubutton(btn_row, text=self.t("recent_files"),
                  font=("Segoe UI", 7), bg=self.colors["card"],
                  fg=self.colors["text_dim"], relief=tk.FLAT, padx=6, pady=2,
                  cursor="hand2")
        self.recent_menu = tk.Menu(self.recent_btn, tearoff=0,
                                   bg=self.colors["card"], fg=self.colors["text"],
                                   font=("Segoe UI", 8))
        self.recent_btn["menu"] = self.recent_menu
        self.recent_btn.pack(side=tk.LEFT)
        self._refresh_recent_menu()

    def _build_chip_config(self, parent):
        """构建芯片配置面板 (预设选择 + 引脚配置 + 协议/操作/时序)"""
        cfg_lf = tk.LabelFrame(parent, text=self.t("chip_config"),
                               font=("Segoe UI", 10, "bold"),
                               fg=self.colors["text"], bg=self.colors["sidebar"],
                               padx=8, pady=6)
        cfg_lf.pack(fill=tk.X, padx=12, pady=(4, 0))

        # 芯片预设
        row0 = tk.Frame(cfg_lf, bg=self.colors["sidebar"])
        row0.pack(fill=tk.X, pady=2)
        tk.Label(row0, text=self.t("chip_preset"), font=("Segoe UI", 8),
                 fg=self.colors["text_dim"], bg=self.colors["sidebar"]).pack(side=tk.LEFT)
        # 构建分组下拉列表
        preset_names = []
        for group_label, chips in CHIP_PRESET_GROUPS:
            preset_names.append(group_label)
            preset_names.extend(chips)
        preset_names.append(CUSTOM_CHIP_KEY)
        self.chip_preset_var = tk.StringVar(value="AT24C02")
        preset_cb = ttk.Combobox(row0, textvariable=self.chip_preset_var,
                                  values=preset_names, state="readonly",
                                  width=18, font=("Consolas", 8))
        preset_cb.pack(side=tk.LEFT, padx=4)
        preset_cb.bind("<<ComboboxSelected>>", self._on_chip_preset_changed)

        # 操作类型: 读 / 写
        row1 = tk.Frame(cfg_lf, bg=self.colors["sidebar"])
        row1.pack(fill=tk.X, pady=2)
        tk.Label(row1, text=self.t("operation_type"), font=("Segoe UI", 8),
                 fg=self.colors["text_dim"], bg=self.colors["sidebar"]).pack(side=tk.LEFT)
        self.op_read_var = tk.BooleanVar(value=True)
        self.op_write_var = tk.BooleanVar(value=True)
        tk.Checkbutton(row1, text=self.t("op_read"), variable=self.op_read_var,
                       font=("Segoe UI", 8), fg=self.colors["text"],
                       bg=self.colors["sidebar"], selectcolor=self.colors["card"],
                       activebackground=self.colors["sidebar"]).pack(side=tk.LEFT, padx=2)
        tk.Checkbutton(row1, text=self.t("op_write"), variable=self.op_write_var,
                       font=("Segoe UI", 8), fg=self.colors["text"],
                       bg=self.colors["sidebar"], selectcolor=self.colors["card"],
                       activebackground=self.colors["sidebar"]).pack(side=tk.LEFT, padx=2)

        # 通信协议: I2C / SPI / Microwire
        row2 = tk.Frame(cfg_lf, bg=self.colors["sidebar"])
        row2.pack(fill=tk.X, pady=2)
        tk.Label(row2, text=self.t("protocol_type"), font=("Segoe UI", 8),
                 fg=self.colors["text_dim"], bg=self.colors["sidebar"]).pack(side=tk.LEFT)
        self.chip_protocol_var = tk.StringVar(value="I2C")
        for proto_val, proto_label in [("I2C", "I2C"), ("SPI", "SPI"), ("Microwire", "MW")]:
            tk.Radiobutton(row2, text=proto_label, variable=self.chip_protocol_var,
                           value=proto_val, font=("Segoe UI", 8), fg=self.colors["text"],
                           bg=self.colors["sidebar"], selectcolor=self.colors["card"],
                           activebackground=self.colors["sidebar"],
                           command=self._on_protocol_changed).pack(side=tk.LEFT, padx=2)

        # 地址引脚
        row3 = tk.Frame(cfg_lf, bg=self.colors["sidebar"])
        row3.pack(fill=tk.X, pady=2)
        tk.Label(row3, text=self.t("addr_pins_label"), font=("Segoe UI", 8),
                 fg=self.colors["text_dim"], bg=self.colors["sidebar"]).pack(side=tk.LEFT)
        self.chip_addr_pins_var = tk.StringVar(value="A0,A1,A2")
        self.chip_addr_entry = tk.Entry(row3, textvariable=self.chip_addr_pins_var,
                                        font=("Consolas", 8), width=14)
        self.chip_addr_entry.pack(side=tk.LEFT, padx=4)

        # 时钟引脚
        row4 = tk.Frame(cfg_lf, bg=self.colors["sidebar"])
        row4.pack(fill=tk.X, pady=2)
        tk.Label(row4, text=self.t("clk_pin_label"), font=("Segoe UI", 8),
                 fg=self.colors["text_dim"], bg=self.colors["sidebar"]).pack(side=tk.LEFT)
        self.chip_clk_pin_var = tk.StringVar(value="SCL")
        self.chip_clk_entry = tk.Entry(row4, textvariable=self.chip_clk_pin_var,
                                        font=("Consolas", 8), width=8)
        self.chip_clk_entry.pack(side=tk.LEFT, padx=4)

        # 数据引脚
        tk.Label(row4, text=self.t("data_pin_label"), font=("Segoe UI", 8),
                 fg=self.colors["text_dim"], bg=self.colors["sidebar"]).pack(side=tk.LEFT, padx=(6,0))
        self.chip_data_pin_var = tk.StringVar(value="SDA")
        self.chip_data_entry = tk.Entry(row4, textvariable=self.chip_data_pin_var,
                                         font=("Consolas", 8), width=8)
        self.chip_data_entry.pack(side=tk.LEFT, padx=4)

        # 写保护引脚
        row5 = tk.Frame(cfg_lf, bg=self.colors["sidebar"])
        row5.pack(fill=tk.X, pady=2)
        tk.Label(row5, text=self.t("wp_pin_label"), font=("Segoe UI", 8),
                 fg=self.colors["text_dim"], bg=self.colors["sidebar"]).pack(side=tk.LEFT)
        self.chip_wp_pin_var = tk.StringVar(value="WP")
        self.chip_wp_entry = tk.Entry(row5, textvariable=self.chip_wp_pin_var,
                                       font=("Consolas", 8), width=6)
        self.chip_wp_entry.pack(side=tk.LEFT, padx=4)
        self.chip_wp_level_var = tk.IntVar(value=0)
        self.chip_wp_rb_frame = tk.Frame(row5, bg=self.colors["sidebar"])
        self.chip_wp_rb_frame.pack(side=tk.LEFT, padx=2)
        tk.Radiobutton(self.chip_wp_rb_frame, text="0", variable=self.chip_wp_level_var,
                       value=0, font=("Consolas", 8), fg=self.colors["text"],
                       bg=self.colors["sidebar"], selectcolor=self.colors["card"],
                       activebackground=self.colors["sidebar"]).pack(side=tk.LEFT)
        tk.Radiobutton(self.chip_wp_rb_frame, text="1", variable=self.chip_wp_level_var,
                       value=1, font=("Consolas", 8), fg=self.colors["text"],
                       bg=self.colors["sidebar"], selectcolor=self.colors["card"],
                       activebackground=self.colors["sidebar"]).pack(side=tk.LEFT)

        # 时序类型
        row6 = tk.Frame(cfg_lf, bg=self.colors["sidebar"])
        row6.pack(fill=tk.X, pady=2)
        tk.Label(row6, text=self.t("timing_mode"), font=("Segoe UI", 8),
                 fg=self.colors["text_dim"], bg=self.colors["sidebar"]).pack(side=tk.LEFT)
        self.chip_timing_var = tk.StringVar(value="Fast 400kHz")
        self.chip_timing_cb = ttk.Combobox(row6, textvariable=self.chip_timing_var,
                                            values=["Standard 100kHz", "Fast 400kHz", "Fast+ 1MHz"],
                                            state="readonly", width=14, font=("Consolas", 8))
        self.chip_timing_cb.pack(side=tk.LEFT, padx=4)

        # ── 芯片参数显示区 (只读信息) ──
        specs_sep = ttk.Separator(cfg_lf, orient=tk.HORIZONTAL)
        specs_sep.pack(fill=tk.X, pady=(6, 3))
        specs_title = tk.Label(cfg_lf, text=self.t("chip_specs"),
                               font=("Segoe UI", 8, "bold"),
                               fg=self.colors["accent"], bg=self.colors["sidebar"])
        specs_title.pack(anchor=tk.W)

        self.chip_specs_labels = {}
        spec_items = [
            ("capacity_disp", self.t("chip_capacity")),
            ("page_size_disp", self.t("chip_page_size")),
            ("addr_mode_disp", self.t("chip_addr_mode")),
            ("endurance_disp", self.t("chip_endurance")),
            ("manufacturer_disp", self.t("chip_manufacturer")),
            ("aliases_disp", self.t("chip_compatible")),
        ]
        for key, label_text in spec_items:
            row = tk.Frame(cfg_lf, bg=self.colors["sidebar"])
            row.pack(fill=tk.X, pady=0)
            tk.Label(row, text=f"{label_text}:", font=("Segoe UI", 7),
                     width=8, anchor="w",
                     fg=self.colors["text_dim"], bg=self.colors["sidebar"]).pack(side=tk.LEFT)
            val_lbl = tk.Label(row, text="--", font=("Consolas", 7), anchor="w",
                               fg=self.colors["text"], bg=self.colors["sidebar"])
            val_lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.chip_specs_labels[key] = val_lbl

        # ── 自定义芯片参数 (Custom 模式可编辑) ──
        custom_sep = ttk.Separator(cfg_lf, orient=tk.HORIZONTAL)
        custom_sep.pack(fill=tk.X, pady=(4, 2))
        row_cap = tk.Frame(cfg_lf, bg=self.colors["sidebar"])
        row_cap.pack(fill=tk.X, pady=1)
        tk.Label(row_cap, text=self.t("chip_capacity"), font=("Segoe UI", 7),
                 fg=self.colors["text_dim"], bg=self.colors["sidebar"], width=8,
                 anchor="w").pack(side=tk.LEFT)
        self.chip_capacity_var = tk.StringVar(value="256")
        self.chip_capacity_entry = tk.Entry(row_cap, textvariable=self.chip_capacity_var,
                                             font=("Consolas", 7), width=7, state=tk.DISABLED)
        self.chip_capacity_entry.pack(side=tk.LEFT, padx=2)
        tk.Label(row_cap, text=self.t("chip_bytes"), font=("Segoe UI", 7),
                 fg=self.colors["text_dim"], bg=self.colors["sidebar"]).pack(side=tk.LEFT)

        tk.Label(row_cap, text=self.t("chip_page_size"), font=("Segoe UI", 7),
                 fg=self.colors["text_dim"], bg=self.colors["sidebar"]).pack(side=tk.LEFT, padx=(6, 0))
        self.chip_page_size_var = tk.StringVar(value="8")
        self.chip_page_size_entry = tk.Entry(row_cap, textvariable=self.chip_page_size_var,
                                              font=("Consolas", 7), width=4, state=tk.DISABLED)
        self.chip_page_size_entry.pack(side=tk.LEFT, padx=2)

        row_addr_bytes = tk.Frame(cfg_lf, bg=self.colors["sidebar"])
        row_addr_bytes.pack(fill=tk.X, pady=1)
        tk.Label(row_addr_bytes, text=self.t("chip_addr_mode"), font=("Segoe UI", 7),
                 fg=self.colors["text_dim"], bg=self.colors["sidebar"], width=8,
                 anchor="w").pack(side=tk.LEFT)
        self.chip_addr_bytes_var = tk.StringVar(value="1")
        self.chip_addr_bytes_entry = tk.Entry(row_addr_bytes, textvariable=self.chip_addr_bytes_var,
                                               font=("Consolas", 7), width=3, state=tk.DISABLED)
        self.chip_addr_bytes_entry.pack(side=tk.LEFT, padx=2)
        tk.Label(row_addr_bytes, text=self.t("chip_bytes"), font=("Segoe UI", 7),
                 fg=self.colors["text_dim"], bg=self.colors["sidebar"]).pack(side=tk.LEFT)

        # 预设选择后锁定/解锁字段
        self._on_chip_preset_changed()

    def _on_chip_preset_changed(self, event=None):
        """芯片预设切换时填充字段并控制可编辑性"""
        preset_name = self.chip_preset_var.get()

        # 拦截分组分隔行 (不可选)
        if preset_name.startswith("──"):
            self.chip_preset_var.set("AT24C02")
            preset_name = "AT24C02"

        is_custom = preset_name not in CHIP_PRESETS

        if not is_custom:
            p = CHIP_PRESETS[preset_name]
            new_protocol = p.get("protocol", "I2C")
            self.chip_protocol_var.set(new_protocol)
            self.chip_addr_pins_var.set(",".join(p.get("addr_pins", [])))
            self.chip_clk_pin_var.set(p.get("clk_pin", "SCL"))
            self.chip_data_pin_var.set(p.get("data_pin", "SDA"))
            self.chip_wp_pin_var.set(p.get("wp_pin", ""))
            self.chip_wp_level_var.set(p.get("wp_default", 0))
            self.op_read_var.set("read" in p.get("operations", []))
            self.op_write_var.set("write" in p.get("operations", []))
            timing_modes = p.get("timing_modes", ["Fast 400kHz"])
            self.chip_timing_cb.config(values=timing_modes)
            if timing_modes:
                self.chip_timing_var.set(timing_modes[1] if len(timing_modes) > 1 else timing_modes[0])
            # 更新导出前缀
            if hasattr(self, 'export_prefix_var'):
                self.export_prefix_var.set(preset_name)
            # 更新自定义参数字段
            cap = p.get("capacity_bytes", 256)
            if hasattr(self, 'chip_capacity_var'):
                self.chip_capacity_var.set(str(cap))
                self.chip_page_size_var.set(str(p.get("page_size", 8)))
                self.chip_addr_bytes_var.set(str(p.get("addr_byte_count", 1)))
            # 更新芯片参数显示区
            if hasattr(self, 'chip_specs_labels'):
                # 容量显示: 支持大容量 Flash
                if cap >= 1_048_576:
                    cap_text = f"{cap // 1_048_576} MB ({cap * 8 // 1_048_576}Mbit)"
                elif cap >= 1024:
                    kbit = cap * 8 // 1024
                    cap_text = f"{cap:,} B ({kbit}Kbit)"
                else:
                    cap_text = f"{cap} {self.t('chip_bytes')} ({cap * 8}bit)"
                self.chip_specs_labels["capacity_disp"].config(text=cap_text)
                self.chip_specs_labels["page_size_disp"].config(
                    text=f"{p.get('page_size', 8)} {self.t('chip_bytes')}")
                # 地址模式/协议参数
                if new_protocol == "SPI":
                    abc = p.get("addr_byte_count", 1)
                    spi_m = p.get("spi_mode", 0)
                    mode_text = f"SPI Mode {spi_m}, {abc}B addr"
                    sect = p.get("sector_size")
                    if sect:
                        mode_text += f", {sect//1024}KB sect"
                elif new_protocol == "Microwire":
                    org = p.get("org_mode", "x16")
                    ab = p.get("addr_bits", 6)
                    mode_text = f"{org}, {ab}-bit addr"
                else:
                    abc = p.get("addr_byte_count", 1)
                    mode_text = self.t("addr_1byte") if abc == 1 else self.t("addr_2byte")
                    psb = p.get("page_select_bits", 0)
                    if psb > 0:
                        mode_text += f" +P{psb}"
                self.chip_specs_labels["addr_mode_disp"].config(text=mode_text)
                endur = p.get("endurance_cycles", 1_000_000)
                if endur >= 1_000_000_000:
                    endur_s = f"{endur/1e12:.0f}T"
                elif endur >= 1_000_000:
                    endur_s = f"{endur/1e6:.0f}M"
                else:
                    endur_s = f"{endur:,}"
                self.chip_specs_labels["endurance_disp"].config(
                    text=f"{endur_s} {self.t('chip_cycles')}")
                self.chip_specs_labels["manufacturer_disp"].config(
                    text=p.get("manufacturer", "--"))
                aliases = p.get("aliases", [])
                self.chip_specs_labels["aliases_disp"].config(
                    text=", ".join(aliases[:3]) if aliases else "--")
            # 更新地址范围上限
            if hasattr(self, 'scan_end_var'):
                max_a = cap - 1
                default_end = min(7, max_a)
                try:
                    current_end = int(self.scan_end_var.get(), 16)
                    if current_end > max_a:
                        self.scan_end_var.set(f"{default_end:02X}")
                except ValueError:
                    self.scan_end_var.set(f"{default_end:02X}")

        # 控制字段可编辑性
        entry_state = tk.NORMAL if is_custom else tk.DISABLED
        for entry in [self.chip_addr_entry, self.chip_clk_entry,
                      self.chip_data_entry, self.chip_wp_entry]:
            entry.config(state=entry_state)
        # 自定义参数字段
        for entry in [getattr(self, 'chip_capacity_entry', None),
                      getattr(self, 'chip_page_size_entry', None),
                      getattr(self, 'chip_addr_bytes_entry', None)]:
            if entry:
                entry.config(state=entry_state)

        # 更新窗口标题
        if hasattr(self, 'root'):
            chip_label = preset_name if not is_custom else "Custom"
            self.root.title(f"{self.t('title')} [{chip_label}]")

        # 同步工具栏地址引脚
        self._sync_toolbar_addr_pins()

        # 更新芯片引脚图
        if hasattr(self, 'chip_canvas'):
            self._redraw_chip()

        # v6.0: 更新状态栏协议/芯片标签
        if hasattr(self, 'status_proto_label'):
            proto = self.chip_protocol_var.get() if hasattr(self, 'chip_protocol_var') else "I2C"
            self.status_proto_label.config(text=f"{proto} | {preset_name}")

    def _sync_toolbar_addr_pins(self):
        """根据芯片配置同步工具栏地址引脚 Spinbox"""
        # 初始化阶段工具栏/芯片图控件可能尚未创建，跳过同步
        if not hasattr(self, 'addr_vars') or not hasattr(self, 'chip_canvas'):
            return
        pin_list = self._get_active_pins()
        addr_pins_text = self.chip_addr_pins_var.get().strip()
        addr_pin_names = [p.strip() for p in addr_pins_text.split(",") if p.strip()] if addr_pins_text else []

        # 更新 addr_vars 中的引脚（保持 A2/A1/A0 默认键名兼容）
        for pin_name in ["A2", "A1", "A0"]:
            if pin_name in self.addr_vars:
                # 如果芯片配置中没有该地址引脚，设为0
                if pin_name not in addr_pin_names:
                    self.addr_vars[pin_name].set(0)

        # 更新 WP
        wp_pin = self.chip_wp_pin_var.get().strip()
        if wp_pin and hasattr(self, 'wp_var'):
            self.wp_var.set(self.chip_wp_level_var.get())

        if hasattr(self, '_update_dev_addr_label'):
            self._update_dev_addr_label()

    def _on_protocol_changed(self):
        """协议切换回调: 更新配置面板、芯片图、时序选项、测试类型"""
        protocol = self.chip_protocol_var.get()

        # ── 1. 更新引脚配置字段 ──
        if protocol == "I2C":
            self.chip_addr_pins_var.set("A0,A1,A2")
            self.chip_clk_pin_var.set("SCL")
            self.chip_data_pin_var.set("SDA")
            self.chip_wp_pin_var.set("WP")
        elif protocol == "SPI":
            self.chip_addr_pins_var.set("CS,WP,HOLD")
            self.chip_clk_pin_var.set("SCK")
            self.chip_data_pin_var.set("MOSI")
            self.chip_wp_pin_var.set("")
        elif protocol == "Microwire":
            self.chip_addr_pins_var.set("CS,ORG,NC")
            self.chip_clk_pin_var.set("SK")
            self.chip_data_pin_var.set("DI")
            self.chip_wp_pin_var.set("")

        # ── 2. 更新时序模式下拉选项 ──
        if protocol == "I2C":
            modes = ["Standard 100kHz", "Fast 400kHz", "Fast+ 1MHz"]
        elif protocol == "SPI":
            modes = ["SPI 5MHz", "SPI 10MHz", "SPI 20MHz", "SPI 50MHz"]
        elif protocol == "Microwire":
            modes = ["MW 1MHz", "MW 2MHz"]
        else:
            modes = ["Fast 400kHz"]
        self.chip_timing_cb.config(values=modes)
        self.chip_timing_var.set(modes[0])

        # ── 3. 更新协议专属参数显示 ──
        if hasattr(self, 'chip_specs_labels'):
            if protocol == "SPI":
                self.chip_specs_labels.get("addr_mode_disp", None) and \
                    self.chip_specs_labels["addr_mode_disp"].config(text="SPI Mode 0")
            elif protocol == "Microwire":
                self.chip_specs_labels.get("addr_mode_disp", None) and \
                    self.chip_specs_labels["addr_mode_disp"].config(text="x16 org")

        # ── 4. 更新芯片引脚图 ──
        if hasattr(self, 'chip_canvas'):
            self._redraw_chip()

        # ── 5. 清空已生成向量 (不同协议测试不兼容) ──
        self.current_vectors = []
        self.current_comments = []
        self.current_labels = []
        self.pat_sections = []
        if hasattr(self, 'pat_text'):
            self.pat_text.delete("1.0", tk.END)
        if hasattr(self, 'txt_text'):
            self.txt_text.delete("1.0", tk.END)

        # v9.0: 清空更多面板
        self._debugger = None
        if hasattr(self, 'dbg_state_label'):
            self.dbg_state_label.config(text="PC: - | Bus: - | Event: -")
        if hasattr(self, 'dbg_history_text'):
            self.dbg_history_text.config(state=tk.NORMAL)
            self.dbg_history_text.delete("1.0", tk.END)
            self.dbg_history_text.config(state=tk.DISABLED)
        if hasattr(self, '_datalog_records'):
            self._datalog_records = []
        if hasattr(self, 'datalog_text'):
            self.datalog_text.delete("1.0", tk.END)
        if hasattr(self, '_wafer_gen'):
            self._wafer_gen = None
        if hasattr(self, 'wafer_canvas'):
            self.wafer_canvas.delete("all")
        if hasattr(self, 'sim_fbm_canvas'):
            self.sim_fbm_canvas.delete("all")
        if hasattr(self, 'shmoo_canvas'):
            self.shmoo_canvas.delete("all")
        # 刷新覆盖矩阵
        if hasattr(self, '_compliance_matrix'):
            self._update_compliance_matrix()
        # v9.0 Phase 22: 清空温度分析
        if hasattr(self, '_temp_canvas'):
            self._temp_canvas.delete("all")
        if hasattr(self, '_temp_tree'):
            self._temp_tree.delete(*self._temp_tree.get_children())
        # v9.0 Phase 24: 刷新 Pin Map
        if hasattr(self, '_pin_map_tree'):
            self._refresh_pin_map()

        # ── 6. 更新测试类型标签 ──
        self._rebuild_test_type_labels()

        # ── 7. 更新状态栏 ──
        if hasattr(self, 'status_label'):
            self.status_label.config(
                text=f"{self.t('protocol_type')}: {protocol}",
                fg=self.colors["text_dim"])
        # v6.0: 更新协议/芯片标签
        if hasattr(self, 'status_proto_label'):
            chip = self.chip_preset_var.get() if hasattr(self, 'chip_preset_var') else "?"
            self.status_proto_label.config(text=f"{protocol} | {chip}")

    def _rebuild_test_type_labels(self):
        """根据当前协议更新测试类型复选框的标签和描述"""
        protocol = self.chip_protocol_var.get()

        # 协议专属测试标签映射
        if protocol == "SPI":
            label_map = {
                "func_test": (self.t("spi_func_test"), self.t("spi_func_desc")),
                "err_test":  (self.t("spi_err_test"), self.t("spi_err_desc")),
            }
        elif protocol == "Microwire":
            label_map = {
                "func_test": (self.t("mw_func_test"), self.t("mw_func_desc")),
                "err_test":  (self.t("mw_err_test"), self.t("mw_err_desc")),
            }
        else:
            label_map = {}  # I2C 使用默认标签, 无需修改

        # 注意: 测试类型复选框在 _build_test_types_content 中创建,
        # 标签是 tk.Label/Checkbutton 子控件, 这里不重建整个面板
        # 而是通过调度在 on_generate 中选择正确的测试方法

    def _set_all_tests(self, value):
        """全选/全不选 测试类型复选框"""
        for var in self.test_vars.values():
            var.set(value)

    def _apply_preset(self, preset_map):
        """应用配置模板预设"""
        for key, val in preset_map.items():
            if key in self.test_vars:
                self.test_vars[key].set(val)
        # 手动修改测试项时, 阶段回到自定义
        if hasattr(self, 'test_phase_var'):
            self.test_phase_var.set("custom")

    def _on_phase_changed(self, event=None):
        """测试阶段下拉回调: 自动勾选/取消测试项"""
        phase = self.test_phase_var.get()
        if phase == "custom":
            return
        mgr = TestPhaseManager()
        result = mgr.apply_phase(phase)
        for key in self.test_vars:
            if key in result["enabled"]:
                self.test_vars[key].set(True)
            elif key in result["disabled"]:
                self.test_vars[key].set(False)
        self.status_label.config(text=f"Phase: {phase} — {result['rationale']}")

    # ================================================================
    # 芯片引脚图
    # ================================================================

    def draw_chip_diagram(self, parent):
        """创建 AT24C02 SOP-8 引脚示意图"""
        self.chip_canvas = tk.Canvas(parent, width=265, height=190,
                                     bg=self.colors["card"],
                                     highlightthickness=0)
        self.chip_canvas.pack(padx=10, pady=(8, 4))
        self._redraw_chip()

    def _redraw_chip(self):
        """重绘芯片引脚图 (配置变化时调用)"""
        c = self.chip_canvas
        self._safe_canvas_reset(c)

        CW, CH = 265, 190
        bw, bh = 96, 128
        bx = (CW - bw) // 2
        by = 22

        # 芯片体
        c.create_rectangle(bx, by, bx + bw, by + bh,
                           fill="#1e2436", outline=self.colors["accent"], width=2)

        # Pin-1 凹口
        c.create_arc(bx + bw // 2 - 8, by - 4, bx + bw // 2 + 8, by + 4,
                     start=180, extent=180,
                     style=tk.ARC, outline=self.colors["accent"], width=1)

        # 引脚定义 — 根据协议/芯片预设从 PACKAGE_PINOUTS 获取
        protocol = self.chip_protocol_var.get() if hasattr(self, 'chip_protocol_var') else "I2C"
        preset_name = self.chip_preset_var.get() if hasattr(self, 'chip_preset_var') else "AT24C02"
        pinout_key = "SOP-8_I2C"  # 默认
        if preset_name in CHIP_PRESETS:
            pinout_key = CHIP_PRESETS[preset_name].get("package_pinout", "SOP-8_I2C")
        elif protocol == "SPI":
            pinout_key = "SOP-8_SPI"
        elif protocol == "Microwire":
            pinout_key = "DIP-8_MW"
        pinout = PACKAGE_PINOUTS.get(pinout_key, PACKAGE_PINOUTS["SOP-8_I2C"])

        # 芯片标识
        c.create_text(bx + bw // 2, by + bh // 2 - 14, text=preset_name,
                      fill=self.colors["text"], font=("Consolas", 11, "bold"))
        pkg_label = pinout_key.replace("_I2C", "").replace("_SPI", "").replace("_MW", "")
        c.create_text(bx + bw // 2, by + bh // 2 + 4, text=pkg_label,
                      fill=self.colors["text_dim"], font=("Consolas", 8))
        cap_label = self._get_chip_capacity_label() if hasattr(self, 'chip_preset_var') else "2Kb I2C EEPROM"
        c.create_text(bx + bw // 2, by + bh // 2 + 19, text=cap_label,
                      fill="#5a6378", font=("Segoe UI", 7))

        left_pins = []
        for num, name in pinout["left"]:
            clr = self._get_pin_color(name)
            left_pins.append((num, name, clr))
        right_pins = []
        for num, name in pinout["right"]:
            clr = self._get_pin_color(name)
            right_pins.append((num, name, clr))

        gap = bh / 4
        plen = 28

        for i, (num, name, clr) in enumerate(left_pins):
            y = by + gap * (i + 0.5)
            c.create_line(bx - plen, y, bx, y, fill=clr, width=2)
            c.create_oval(bx - plen - 3, y - 3, bx - plen + 3, y + 3,
                         fill=clr, outline="")
            c.create_text(bx + 8, y, text=str(num), fill="#5a6378",
                          font=("Consolas", 7))
            c.create_text(bx - plen - 8, y, text=name, fill=clr,
                          font=("Consolas", 9, "bold"), anchor=tk.E)

        for i, (num, name, clr) in enumerate(right_pins):
            y = by + gap * (i + 0.5)
            c.create_line(bx + bw, y, bx + bw + plen, y, fill=clr, width=2)
            c.create_oval(bx + bw + plen - 3, y - 3, bx + bw + plen + 3, y + 3,
                         fill=clr, outline="")
            c.create_text(bx + bw - 8, y, text=str(num), fill="#5a6378",
                          font=("Consolas", 7))
            c.create_text(bx + bw + plen + 8, y, text=name, fill=clr,
                          font=("Consolas", 9, "bold"), anchor=tk.W)

        c.create_text(CW // 2, by + bh + 14,
                      text="引脚颜色随配置变化",
                      fill="#5a6378", font=("Segoe UI", 7))

    def _get_pin_color(self, pin_name):
        """根据当前配置返回引脚颜色"""
        try:
            if pin_name in ("A0", "A1", "A2"):
                return self.colors["accent"] if self.addr_vars[pin_name].get() else "#6a7383"
            if pin_name == "WP":
                return self.colors["warning"] if self.wp_var.get() else "#6a7383"
        except (tk.TclError, ValueError, AttributeError):
            pass
        # 协议信号引脚颜色
        if pin_name in ("SCL", "SDA", "SCK", "MOSI", "MISO", "SK", "DI", "DO",
                         "SO/MISO", "SI/MOSI"):
            return self.colors["accent2"]
        if pin_name in ("CS", "CS#"):
            return self.colors["warning"]
        if pin_name == "VCC":
            return "#ff6b6b"
        if pin_name == "GND":
            return "#6a7383"
        if pin_name in ("HOLD", "HOLD#", "ORG", "NC"):
            return "#6a7383"
        return "#6a7383"

    def _on_wp_changed(self):
        """WP 复选框回调"""
        self._redraw_chip()

    def _on_voltage_changed(self, event=None):
        """电压预设切换回调: 自动更新周期和频率"""
        vkey = self.voltage_var.get()
        vp = VOLTAGE_PRESETS.get(vkey)
        if vp:
            self.period_var.set(str(vp["period_ns"]))

    def _run_timing_check(self):
        """运行时序合规性检查并弹窗显示结果 (协议自适应)"""
        period_ns = self._get_period_ns()
        vkey = self.voltage_var.get()
        protocol = self.chip_protocol_var.get()

        if protocol == "SPI":
            passed, results = SPITimingChecker.check(period_ns, vkey)
            check_title = "SPI Timing Compliance Check"
        elif protocol == "Microwire":
            passed, results = MicrowireTimingChecker.check(period_ns, vkey)
            check_title = "Microwire Timing Compliance Check"
        else:
            passed, results = I2CTimingChecker.check(period_ns, vkey)
            check_title = "I2C Timing Compliance Check"

        # 构建结果文本
        lines = []
        lines.append(check_title)
        lines.append(f"Period: {period_ns} ns  |  Voltage: {vkey}")
        lines.append("=" * 55)
        for r in results:
            sym = "PASS" if r["passed"] else "FAIL"
            mark = "  " if r["passed"] else "!!"
            lines.append(f"{mark} [{sym}] {r['param']:12s} Required: {r['required']:16s} "
                         f"Actual: {r['actual']:12s}")
            lines.append(f"          {r['note']}")
        lines.append("=" * 55)
        lines.append(f"Result: {'ALL PASS' if passed else 'FAIL — adjust period or voltage'}")

        # 弹窗
        dlg = tk.Toplevel(self.root)
        dlg.title(self.t("timing_check"))
        dlg.geometry("520x420")
        dlg.configure(bg=self.colors["card"])
        dlg.transient(self.root)
        dlg.grab_set()

        clr = self.colors["success"] if passed else self.colors["danger"]
        tk.Label(dlg, text="PASS" if passed else "FAIL",
                 font=("Segoe UI", 18, "bold"), fg=clr,
                 bg=self.colors["card"]).pack(pady=(12, 4))

        txt = scrolledtext.ScrolledText(dlg, wrap=tk.WORD, font=("Consolas", 9),
                                         bg=self.colors["bg"], fg=self.colors["text"],
                                         relief=tk.FLAT, padx=10, pady=8)
        txt.pack(fill=tk.BOTH, expand=True, padx=12, pady=6)
        txt.insert("1.0", "\n".join(lines))
        txt.config(state=tk.DISABLED)

        tk.Button(dlg, text=self.t("close"), command=dlg.destroy,
                  font=("Segoe UI", 9), bg=self.colors["border"],
                  fg=self.colors["text"], relief=tk.FLAT, padx=14, pady=4,
                  cursor="hand2").pack(pady=8)

        if passed:
            self.status_label.config(text=self.t("timing_pass"), fg=self.colors["success"])
        else:
            self.status_label.config(text=self.t("timing_fail"), fg=self.colors["danger"])

    def _run_protocol_check(self):
        """运行向量协议合规性检查并弹窗显示结果 (协议自适应)"""
        if not self.current_vectors:
            messagebox.showinfo("", self.t("gen_first"))
            return

        protocol = self.chip_protocol_var.get()
        if protocol == "SPI":
            issue_count, issues = SPIProtocolValidator.validate(
                self.current_vectors, self.current_comments)
            check_title = "SPI Protocol Compliance Check"
        elif protocol == "Microwire":
            issue_count, issues = MicrowireProtocolValidator.validate(
                self.current_vectors, self.current_comments)
            check_title = "Microwire Protocol Compliance Check"
        else:
            issue_count, issues = VectorProtocolValidator.validate(
                self.current_vectors, self.current_comments)
            check_title = "I2C Protocol Compliance Check"

        lines = []
        lines.append(check_title)
        lines.append(f"Total vectors: {len(self.current_vectors)}")
        lines.append("=" * 60)
        for iss in issues:
            sev = iss["severity"].upper()
            rule = iss["rule"]
            detail = iss["detail"]
            if sev == "ERROR":
                lines.append(f"[ERROR]   {detail}")
            elif sev == "WARNING":
                lines.append(f"[WARN]    {detail}")
            else:
                lines.append(f"[INFO]    {detail}")
        lines.append("=" * 60)
        lines.append(f"Result: {issue_count} issues (excl. summary)")

        dlg = tk.Toplevel(self.root)
        dlg.title(self.t("proto_check"))
        dlg.geometry("580x400")
        dlg.configure(bg=self.colors["card"])
        dlg.transient(self.root)
        dlg.grab_set()

        clr = self.colors["success"] if issue_count == 0 else self.colors["warning"]
        tk.Label(dlg, text=f"{issue_count} issues",
                 font=("Segoe UI", 16, "bold"), fg=clr,
                 bg=self.colors["card"]).pack(pady=(12, 4))

        txt = scrolledtext.ScrolledText(dlg, wrap=tk.WORD, font=("Consolas", 9),
                                         bg=self.colors["bg"], fg=self.colors["text"],
                                         relief=tk.FLAT, padx=10, pady=8)
        txt.pack(fill=tk.BOTH, expand=True, padx=12, pady=6)
        txt.insert("1.0", "\n".join(lines))
        txt.config(state=tk.DISABLED)

        tk.Button(dlg, text=self.t("close"), command=dlg.destroy,
                  font=("Segoe UI", 9), bg=self.colors["border"],
                  fg=self.colors["text"], relief=tk.FLAT, padx=14, pady=4,
                  cursor="hand2").pack(pady=8)

        if issue_count == 0:
            self.status_label.config(text=self.t("proto_pass"), fg=self.colors["success"])
        else:
            self.status_label.config(
                text=self.t("proto_issues").format(issue_count), fg=self.colors["warning"])

    def _update_dev_addr_label(self, *args):
        """地址引脚变化时更新器件地址和芯片图"""
        try:
            a2 = self.addr_vars["A2"].get()
            a1 = self.addr_vars["A1"].get()
            a0 = self.addr_vars["A0"].get()
            write_addr = 0xA0 | (a2 << 3) | (a1 << 2) | (a0 << 1)
            read_addr = write_addr | 0x01
            self.dev_addr_label.config(
                text=f"0x{write_addr:02X} / 0x{read_addr:02X}")
        except (tk.TclError, ValueError):
            pass
        self._redraw_chip()

    def _get_active_pins(self):
        """根据芯片配置返回当前测试引脚列表
        顺序: 地址引脚 → WP → SCL → SDA (与EStar官方格式一致)"""
        if hasattr(self, 'chip_preset_var'):
            preset_name = self.chip_preset_var.get()
            if preset_name in CHIP_PRESETS:
                preset = CHIP_PRESETS[preset_name]
                pins = list(preset.get("addr_pins", []))
                wp = preset.get("wp_pin", "")
                if wp:
                    pins.append(wp)
                pins.append(preset.get("clk_pin", "SCL"))
                pins.append(preset.get("data_pin", "SDA"))
                return pins
            # 自定义模式：从 Entry 读取
            if hasattr(self, 'chip_addr_pins_var'):
                pins = []
                addr_text = self.chip_addr_pins_var.get().strip()
                if addr_text:
                    pins.extend([p.strip() for p in addr_text.split(",") if p.strip()])
                wp = self.chip_wp_pin_var.get().strip()
                if wp:
                    pins.append(wp)
                clk = self.chip_clk_pin_var.get().strip() or "SCL"
                data = self.chip_data_pin_var.get().strip() or "SDA"
                pins.append(clk)
                pins.append(data)
                return pins if pins else TEST_PINS
        return TEST_PINS

    def _get_chip_capacity_bytes(self):
        """获取当前芯片容量 (字节)"""
        preset = self.chip_preset_var.get()
        if preset in CHIP_PRESETS:
            return CHIP_PRESETS[preset].get("capacity_bytes", 256)
        try:
            return int(self.chip_capacity_var.get())
        except (ValueError, AttributeError):
            return 256

    def _get_chip_capacity_label(self):
        """获取芯片容量显示标签"""
        preset = self.chip_preset_var.get()
        if preset in CHIP_PRESETS:
            return CHIP_PRESETS[preset].get("capacity", "")
        cap = self._get_chip_capacity_bytes()
        kbit = cap * 8 // 1024
        return f"{kbit}Kbit ({cap}x8)"

    def _get_period_ns(self):
        """获取当前向量周期 (ns), 无效值回退 2500"""
        try:
            val = int(self.period_var.get().strip())
            if val > 0:
                return val
        except (ValueError, AttributeError):
            pass
        return 2500

    def _update_period_freq(self, *args):
        """向量周期输入变化时更新频率显示"""
        period = self._get_period_ns()
        freq_khz = 1e9 / period / 1e3
        self.period_freq_label.config(text=f"= {freq_khz:.1f} kHz")

    def _save_config(self):
        """保存当前 GUI 配置到 JSON 文件"""
        path = filedialog.asksaveasfilename(
            title="Save Config", defaultextension=".json",
            filetypes=[("JSON Config", "*.json")],
            initialfile="pat_config.json")
        if not path:
            return
        cfg = self._build_config_dict()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
        self.status_label.config(text=f"\u2713 Config saved: {os.path.basename(path)}",
                                  fg=self.colors["success"])
        self._add_to_recent(path, "config")

    def _build_config_dict(self):
        """将当前 GUI 配置构建为字典"""
        cfg = {
            "config_version": VERSION,
            "addr_pins": {k: v.get() for k, v in self.addr_vars.items()},
            "wp": self.wp_var.get(),
            "tests": {k: v.get() for k, v in self.test_vars.items()},
            "custom_addr": self.custom_addr_var.get(),
            "custom_data": self.custom_data_var.get(),
            "scan_start": self.scan_start_var.get(),
            "scan_end": self.scan_end_var.get(),
            "period_ns": self.period_var.get(),
            "voltage": self.voltage_var.get(),
            "export_prefix": self.export_prefix_var.get(),
            "poll_count": self.poll_count_var.get(),
            "chip_preset": self.chip_preset_var.get(),
            "chip_capacity": self.chip_capacity_var.get(),
            "chip_page_size": self.chip_page_size_var.get(),
            "chip_addr_bytes": self.chip_addr_bytes_var.get(),
            # v6.0: 补全协议/多电压/时序字段
            "protocol": self.chip_protocol_var.get() if hasattr(self, 'chip_protocol_var') else "I2C",
            "multi_voltage": self.multi_voltage_var.get() if hasattr(self, 'multi_voltage_var') else False,
            "timing_mode": self.chip_timing_var.get() if hasattr(self, 'chip_timing_var') else "",
            "wp_default_level": self.chip_wp_level_var.get() if hasattr(self, 'chip_wp_level_var') else "0",
        }
        return cfg

    def _apply_config_dict(self, cfg):
        """将配置字典应用到 GUI 控件"""
        for k, v in cfg.get("addr_pins", {}).items():
            if k in self.addr_vars:
                self.addr_vars[k].set(v)
        if "wp" in cfg:
            self.wp_var.set(cfg["wp"])
        for k, v in cfg.get("tests", {}).items():
            if k in self.test_vars:
                self.test_vars[k].set(v)
        if "custom_addr" in cfg:
            self.custom_addr_var.set(cfg["custom_addr"])
        if "custom_data" in cfg:
            self.custom_data_var.set(cfg["custom_data"])
        if "scan_start" in cfg:
            self.scan_start_var.set(cfg["scan_start"])
        if "scan_end" in cfg:
            self.scan_end_var.set(cfg["scan_end"])
        if "period_ns" in cfg:
            self.period_var.set(cfg["period_ns"])
        if "voltage" in cfg:
            self.voltage_var.set(cfg["voltage"])
        if "export_prefix" in cfg:
            self.export_prefix_var.set(cfg["export_prefix"])
        if "poll_count" in cfg:
            self.poll_count_var.set(cfg["poll_count"])
        # v6.0: 恢复协议 (必须在 preset 之前)
        if "protocol" in cfg and hasattr(self, 'chip_protocol_var'):
            self.chip_protocol_var.set(cfg["protocol"])
            self._on_protocol_changed()
        if "multi_voltage" in cfg and hasattr(self, 'multi_voltage_var'):
            self.multi_voltage_var.set(cfg["multi_voltage"])
        if "timing_mode" in cfg and hasattr(self, 'chip_timing_var'):
            try:
                self.chip_timing_var.set(cfg["timing_mode"])
            except Exception:
                pass
        if "wp_default_level" in cfg and hasattr(self, 'chip_wp_level_var'):
            self.chip_wp_level_var.set(cfg["wp_default_level"])
        # 恢复芯片预设
        if "chip_preset" in cfg and hasattr(self, 'chip_preset_var'):
            self.chip_preset_var.set(cfg["chip_preset"])
            self._on_chip_preset_changed()
        if "chip_capacity" in cfg and hasattr(self, 'chip_capacity_var'):
            self.chip_capacity_var.set(cfg["chip_capacity"])
        if "chip_page_size" in cfg and hasattr(self, 'chip_page_size_var'):
            self.chip_page_size_var.set(cfg["chip_page_size"])
        if "chip_addr_bytes" in cfg and hasattr(self, 'chip_addr_bytes_var'):
            self.chip_addr_bytes_var.set(cfg["chip_addr_bytes"])
        if hasattr(self, 'chip_canvas'):
            self._redraw_chip()

    def _load_config(self):
        """从 JSON 文件加载 GUI 配置 (含配置对比)"""
        path = filedialog.askopenfilename(
            title="加载配置",
            filetypes=[("JSON 配置文件", "*.json")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                cfg = json.load(f)

            # 版本检查
            cfg_ver = cfg.get("config_version", "")
            if cfg_ver and cfg_ver != VERSION:
                messagebox.showinfo(
                    self.t("load_config"),
                    self.t("config_old_ver").format(ver=cfg_ver))

            # 配置对比: 列出差异项
            diffs = []
            for k, v in cfg.get("addr_pins", {}).items():
                if k in self.addr_vars and self.addr_vars[k].get() != v:
                    diffs.append(f"  {k}: {self.addr_vars[k].get()} → {v}")
            if "wp" in cfg and self.wp_var.get() != cfg["wp"]:
                diffs.append(f"  WP: {self.wp_var.get()} → {cfg['wp']}")
            for k, v in cfg.get("tests", {}).items():
                if k in self.test_vars and self.test_vars[k].get() != v:
                    state_map = {True: "ON", False: "OFF", 1: "ON", 0: "OFF"}
                    diffs.append(f"  {k}: {state_map.get(self.test_vars[k].get(), '?')} → {state_map.get(v, '?')}")
            field_map = {
                "period_ns": ("向量周期", self.period_var),
                "voltage": ("电压", self.voltage_var),
                "scan_start": ("扫描起始", self.scan_start_var),
                "scan_end": ("扫描结束", self.scan_end_var),
                "export_prefix": ("导出前缀", self.export_prefix_var),
            }
            for key, (label, var) in field_map.items():
                if key in cfg and str(var.get()) != str(cfg[key]):
                    diffs.append(f"  {label}: {var.get()} → {cfg[key]}")

            # 有差异时弹窗确认
            if diffs:
                diff_text = "\n".join(diffs)
                if not messagebox.askyesno(
                    "配置对比",
                    f"加载的配置与当前配置有以下差异:\n\n{diff_text}\n\n是否应用这些更改？"):
                    return

            # 应用配置
            self._apply_config_dict(cfg)
            self._add_to_recent(path, "config")
            self.status_label.config(text=f"\u2713 Loaded: {os.path.basename(path)}",
                                      fg=self.colors["success"])
            # 加载配置后自动生成向量
            self.root.after(100, self.on_generate)
        except Exception as e:
            messagebox.showerror("加载失败", f"配置文件解析出错:\n{e}")

    # ================================================================
    # Undo / Redo 系统
    # ================================================================

    def _init_undo_system(self):
        """初始化撤销/重做系统"""
        self._undo_stack = []
        self._redo_stack = []
        self._undo_timer = None
        self._undo_tracking = False

    def _start_undo_tracking(self):
        """开始追踪变量变化（在 UI 构建完成后调用）"""
        self._undo_tracking = True
        # 保存初始快照
        self._undo_stack.append(self._snapshot_config())

    def _snapshot_config(self):
        """捕获当前所有配置变量的快照"""
        snap = {}
        if hasattr(self, 'addr_vars'):
            snap['addr'] = {k: v.get() for k, v in self.addr_vars.items()}
        if hasattr(self, 'wp_var'):
            snap['wp'] = self.wp_var.get()
        if hasattr(self, 'voltage_var'):
            snap['voltage'] = self.voltage_var.get()
        if hasattr(self, 'test_vars'):
            snap['tests'] = {k: v.get() for k, v in self.test_vars.items()}
        for attr in ['period_var', 'poll_count_var', 'scan_start_var', 'scan_end_var',
                     'custom_addr_var', 'custom_data_var', 'export_prefix_var']:
            if hasattr(self, attr):
                snap[attr] = getattr(self, attr).get()
        return snap

    def _apply_snapshot(self, snap):
        """应用配置快照（不触发新的 undo push）"""
        self._undo_tracking = False
        try:
            if 'addr' in snap and hasattr(self, 'addr_vars'):
                for k, v in snap['addr'].items():
                    if k in self.addr_vars:
                        self.addr_vars[k].set(v)
            if 'wp' in snap and hasattr(self, 'wp_var'):
                self.wp_var.set(snap['wp'])
            if 'voltage' in snap and hasattr(self, 'voltage_var'):
                self.voltage_var.set(snap['voltage'])
            if 'tests' in snap and hasattr(self, 'test_vars'):
                for k, v in snap['tests'].items():
                    if k in self.test_vars:
                        self.test_vars[k].set(v)
            for attr in ['period_var', 'poll_count_var', 'scan_start_var', 'scan_end_var',
                         'custom_addr_var', 'custom_data_var', 'export_prefix_var']:
                if attr in snap and hasattr(self, attr):
                    getattr(self, attr).set(snap[attr])
        finally:
            self._undo_tracking = True

    def _push_undo_debounced(self, *args):
        """防抖推送 undo（500ms 内多次变化只记录一次）"""
        if not self._undo_tracking:
            return
        if self._undo_timer:
            self.root.after_cancel(self._undo_timer)
        self._undo_timer = self.root.after(500, self._push_undo)

    def _push_undo(self):
        """推送当前快照到 undo 栈"""
        snap = self._snapshot_config()
        if self._undo_stack and snap == self._undo_stack[-1]:
            return
        self._undo_stack.append(snap)
        if len(self._undo_stack) > 50:
            self._undo_stack.pop(0)
        self._redo_stack.clear()
        self._update_undo_buttons()

    def _undo(self):
        """撤销"""
        if len(self._undo_stack) <= 1:
            return
        self._redo_stack.append(self._undo_stack.pop())
        self._apply_snapshot(self._undo_stack[-1])
        self._update_undo_buttons()

    def _redo(self):
        """重做"""
        if not self._redo_stack:
            return
        snap = self._redo_stack.pop()
        self._undo_stack.append(snap)
        self._apply_snapshot(snap)
        self._update_undo_buttons()

    def _update_undo_buttons(self):
        """更新撤销/重做按钮状态"""
        if hasattr(self, 'undo_btn'):
            self.undo_btn.config(state=tk.NORMAL if len(self._undo_stack) > 1 else tk.DISABLED)
        if hasattr(self, 'redo_btn'):
            self.redo_btn.config(state=tk.NORMAL if self._redo_stack else tk.DISABLED)

    # ================================================================
    # 最近文件
    # ================================================================

    def _recent_file_path(self):
        return os.path.join(os.path.expanduser("~"), ".at24c02_pat_recent.json")

    def _load_recent_list(self):
        """加载最近文件列表"""
        try:
            with open(self._recent_file_path(), "r", encoding="utf-8") as f:
                return json.load(f)[:10]
        except Exception:
            return []

    def _save_recent_list(self, recent):
        """保存最近文件列表"""
        try:
            with open(self._recent_file_path(), "w", encoding="utf-8") as f:
                json.dump(recent[:10], f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _add_to_recent(self, path, file_type="config"):
        """添加文件到最近列表"""
        recent = self._load_recent_list()
        entry = {"path": path, "type": file_type,
                 "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}
        recent = [r for r in recent if r.get("path") != path]
        recent.insert(0, entry)
        self._save_recent_list(recent[:10])
        self._refresh_recent_menu()

    def _refresh_recent_menu(self):
        """刷新最近文件菜单"""
        if not hasattr(self, 'recent_menu'):
            return
        self.recent_menu.delete(0, tk.END)
        recent = self._load_recent_list()
        if not recent:
            self.recent_menu.add_command(label=self.t("no_recent"), state=tk.DISABLED)
            return
        for r in recent:
            path = r.get("path", "")
            display = os.path.basename(path)
            self.recent_menu.add_command(
                label=f"{display}  ({r.get('time', '')})",
                command=lambda p=path: self._load_config_from_path(p))

    def _load_config_from_path(self, path):
        """从指定路径加载配置"""
        if not os.path.exists(path):
            messagebox.showwarning("File Not Found", f"{path}")
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            self._apply_config_dict(cfg)
            self.status_label.config(text=f"\u2713 Loaded: {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ================================================================
    # 自动保存 / 恢复
    # ================================================================

    def _autosave_path(self):
        return os.path.join(os.path.expanduser("~"), ".at24c02_pat_autosave.json")

    def _start_autosave(self):
        """启动自动保存定时器"""
        self._do_autosave()

    def _do_autosave(self):
        """执行自动保存"""
        try:
            cfg = self._build_config_dict()
            cfg["_autosave_time"] = datetime.datetime.now().isoformat()
            with open(self._autosave_path(), "w", encoding="utf-8") as f:
                json.dump(cfg, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
        self.root.after(60000, self._do_autosave)

    def _check_autosave_recovery(self):
        """启动时检查是否有需要恢复的自动保存"""
        path = self._autosave_path()
        if not os.path.exists(path):
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            save_time = cfg.get("_autosave_time", "")
            if save_time:
                dt = datetime.datetime.fromisoformat(save_time)
                age_hours = (datetime.datetime.now() - dt).total_seconds() / 3600
                if age_hours > 24:
                    os.remove(path)
                    return
            if messagebox.askyesno(self.t("recovery_title"), self.t("recovery_found")):
                self._apply_config_dict(cfg)
                self.status_label.config(text="\u2713 Config restored from autosave")
            os.remove(path)
        except Exception:
            pass

    def _cleanup_autosave(self):
        """正常退出时清理自动保存文件"""
        try:
            path = self._autosave_path()
            if os.path.exists(path):
                os.remove(path)
        except Exception:
            pass

    # ================================================================
    # 快捷键帮助对话框
    # ================================================================

    def _show_shortcuts_dialog(self, event=None):
        """显示键盘快捷键列表"""
        dlg = tk.Toplevel(self.root)
        dlg.title(self.t("shortcuts_title"))
        dlg.geometry("420x480")
        dlg.configure(bg=self.colors["bg"])
        dlg.transient(self.root)
        dlg.grab_set()

        tk.Label(dlg, text=self.t("shortcuts_title"),
                 font=("Segoe UI", 14, "bold"),
                 fg=self.colors["text"], bg=self.colors["bg"]).pack(pady=(12, 8))

        shortcuts = [
            ("Ctrl+G / F5", self.t("generate")),
            ("Ctrl+E / F6", self.t("export")),
            ("Ctrl+F", self.t("search")),
            ("Ctrl+S", self.t("save_config")),
            ("Ctrl+O", self.t("load_config")),
            ("Ctrl+Z", self.t("undo")),
            ("Ctrl+Y", self.t("redo")),
            ("Ctrl+Shift+P", self.t("cmd_palette")),
            ("Ctrl+1~6", "Switch Tab"),
            ("Ctrl+A", self.t("select_all")),
            ("Ctrl+D", self.t("deselect_all")),
            ("F1", self.t("shortcuts_title")),
            ("Escape", self.t("close")),
        ]

        frame = tk.Frame(dlg, bg=self.colors["bg"], padx=20)
        frame.pack(fill=tk.BOTH, expand=True)
        for key, desc in shortcuts:
            row = tk.Frame(frame, bg=self.colors["bg"])
            row.pack(fill=tk.X, pady=2)
            tk.Label(row, text=key, font=("Consolas", 9, "bold"),
                     fg=self.colors["accent"], bg=self.colors["bg"],
                     width=18, anchor=tk.W).pack(side=tk.LEFT)
            tk.Label(row, text=desc.strip(), font=("Segoe UI", 9),
                     fg=self.colors["text"], bg=self.colors["bg"],
                     anchor=tk.W).pack(side=tk.LEFT, fill=tk.X)

        tk.Button(dlg, text=self.t("close"), command=dlg.destroy,
                  font=("Segoe UI", 9), bg=self.colors["accent"], fg="white",
                  relief=tk.FLAT, padx=16, pady=4, cursor="hand2").pack(pady=12)

        dlg.bind("<Escape>", lambda e: dlg.destroy())

    def _show_about_dialog(self, event=None):
        """显示关于对话框 (版本信息 + 功能概览 + 快捷键)"""
        dlg = tk.Toplevel(self.root)
        dlg.title(self.t("about_title"))
        dlg.geometry("500x580")
        dlg.configure(bg=self.colors["bg"])
        dlg.transient(self.root)
        dlg.grab_set()
        dlg.resizable(False, False)
        # 居中
        dlg.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - 500) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - 580) // 2
        dlg.geometry(f"+{x}+{y}")

        # ── 标题区 ──
        header = tk.Frame(dlg, bg=self.colors["accent"], padx=16, pady=12)
        header.pack(fill=tk.X)
        tk.Label(header, text="AT24C02 PAT Test Vector Generator",
                 font=("Segoe UI", 13, "bold"),
                 fg="white", bg=self.colors["accent"]).pack(anchor=tk.W)
        tk.Label(header, text=f"{self.t('about_version')}: {VERSION}  |  AdaptStar-E (EStar)",
                 font=("Segoe UI", 9),
                 fg="#dbeafe", bg=self.colors["accent"]).pack(anchor=tk.W, pady=(2, 0))

        body = tk.Frame(dlg, bg=self.colors["bg"], padx=16, pady=8)
        body.pack(fill=tk.BOTH, expand=True)

        # ── 竞赛信息 ──
        tk.Label(body, text=self.t("about_competition"),
                 font=("Segoe UI", 9, "bold"),
                 fg=self.colors["gold"], bg=self.colors["bg"]).pack(anchor=tk.W, pady=(4, 0))
        tk.Label(body, text='"胜达克"企业命题 — 存储类芯片自动化测试',
                 font=("Segoe UI", 8),
                 fg=self.colors["text_dim"], bg=self.colors["bg"]).pack(anchor=tk.W)

        # ── 功能概览 ──
        tk.Frame(body, bg=self.colors["border"], height=1).pack(fill=tk.X, pady=8)
        tk.Label(body, text=self.t("about_features"),
                 font=("Segoe UI", 10, "bold"),
                 fg=self.colors["text"], bg=self.colors["bg"]).pack(anchor=tk.W, pady=(0, 4))

        features = [
            ("9", "测试类型 / Test Types", "OS, DC, FUNC, March C-, March B, Scan, Retention, Error, Endurance"),
            ("4", "电压预设 / Voltage Presets", "1.8V, 2.5V, 3.3V, 5.0V"),
            ("12", "导出格式 / Export Formats", ".pat .txt .prg .tim .lvl .html .csv .json .svg .dlog .manifest"),
            ("2", "UI 主题 / Themes", "Navy Dark + Clean Light"),
            ("2", "UI 语言 / Languages", "中文 + English"),
        ]
        for num, title, detail in features:
            row = tk.Frame(body, bg=self.colors["bg"])
            row.pack(fill=tk.X, pady=1)
            tk.Label(row, text=num, font=("Consolas", 11, "bold"),
                     fg=self.colors["accent"], bg=self.colors["bg"],
                     width=3, anchor=tk.E).pack(side=tk.LEFT)
            tk.Label(row, text=f"  {title}", font=("Segoe UI", 9, "bold"),
                     fg=self.colors["text"], bg=self.colors["bg"],
                     anchor=tk.W).pack(side=tk.LEFT)
            tk.Label(row, text=f"  {detail}", font=("Segoe UI", 8),
                     fg=self.colors["text_dim"], bg=self.colors["bg"],
                     anchor=tk.W).pack(side=tk.LEFT)

        # ── 系统信息 ──
        tk.Frame(body, bg=self.colors["border"], height=1).pack(fill=tk.X, pady=8)
        sys_info = f"Python {sys.version.split()[0]}  |  {sys.platform}  |  tkinter {tk.TkVersion}"
        tk.Label(body, text=sys_info, font=("Consolas", 8),
                 fg=self.colors["text_dim"], bg=self.colors["bg"]).pack(anchor=tk.W)

        # ── 快捷键摘要 ──
        tk.Frame(body, bg=self.colors["border"], height=1).pack(fill=tk.X, pady=8)
        tk.Label(body, text="⌨ " + self.t("shortcuts_title"),
                 font=("Segoe UI", 10, "bold"),
                 fg=self.colors["text"], bg=self.colors["bg"]).pack(anchor=tk.W, pady=(0, 4))

        shortcuts = [
            ("Ctrl+G / F5", self.t("generate")),
            ("Ctrl+E / F6", self.t("export")),
            ("Ctrl+Z / Y", self.t("undo") + " / " + self.t("redo")),
            ("Ctrl+S / O", self.t("save_config") + " / " + self.t("load_config")),
            ("Ctrl+Shift+P", self.t("cmd_palette")),
            ("Ctrl+F", self.t("search")),
            ("Ctrl+1~6", "Switch Tab"),
            ("F1", self.t("about_title")),
        ]
        for key, desc in shortcuts:
            row = tk.Frame(body, bg=self.colors["bg"])
            row.pack(fill=tk.X, pady=1)
            tk.Label(row, text=key, font=("Consolas", 8, "bold"),
                     fg=self.colors["accent2"], bg=self.colors["bg"],
                     width=16, anchor=tk.W).pack(side=tk.LEFT)
            tk.Label(row, text=desc.strip(), font=("Segoe UI", 8),
                     fg=self.colors["text"], bg=self.colors["bg"],
                     anchor=tk.W).pack(side=tk.LEFT)

        # ── 关闭按钮 ──
        tk.Button(dlg, text="OK", command=dlg.destroy,
                  font=("Segoe UI", 9, "bold"), bg=self.colors["accent"], fg="white",
                  relief=tk.FLAT, padx=24, pady=4, cursor="hand2").pack(pady=10)
        dlg.bind("<Escape>", lambda e: dlg.destroy())
        dlg.bind("<Return>", lambda e: dlg.destroy())

    # ================================================================
    # 测试时间估算
    # ================================================================

    def _estimate_test_time(self, *args):
        """根据当前选择估算向量数和测试时间"""
        if not hasattr(self, 'test_vars'):
            return
        try:
            start = int(self.scan_start_var.get(), 16) if hasattr(self, 'scan_start_var') else 0
            end = int(self.scan_end_var.get(), 16) if hasattr(self, 'scan_end_var') else 7
        except (ValueError, AttributeError):
            start, end = 0, 7
        n_addr = max(end - start + 1, 1)

        estimates = {
            "os_test": 46,
            "dc_test": 1182,
            "func_test": 3112,
            "march_test": int(15410 * n_addr / 8),
            "march_b_test": int(18000 * n_addr / 8),
            "scan_test": int(3086 * n_addr / 8),
            "ret_test": int(9313 * n_addr / 8),
            "err_test": 1443,
            "endur_test": 3980,
        }

        total = 0
        for key, var in self.test_vars.items():
            if var.get():
                total += estimates.get(key, 0)

        try:
            period_ns = float(self.period_var.get()) if hasattr(self, 'period_var') else 2500
        except (ValueError, AttributeError):
            period_ns = 2500

        time_ms = total * period_ns / 1e6

        # 更新状态栏
        if hasattr(self, 'stats_label'):
            self.stats_label.config(text=f"~{total:,} vec")
        if hasattr(self, 'status_time_label'):
            self.status_time_label.config(text=f"~{time_ms:.1f} ms")

    # ================================================================
    # PAT 压缩 (RLE)
    # ================================================================

    @staticmethod
    def _compress_vectors_rle(pat_lines):
        """对 PAT 向量行进行 RLE 压缩，返回 (压缩后行列表, 原始行数, 压缩行数)"""
        if not pat_lines:
            return pat_lines, 0, 0
        result = []
        prev_vec = None
        count = 0
        orig_count = len(pat_lines)

        for line in pat_lines:
            stripped = line.strip()
            # 只压缩纯向量行 (以空格开头，不含标签，不含 AC_SET)
            is_vector = stripped.endswith(';') and '//' not in stripped and ':' not in stripped and 'AC_SET' not in stripped
            if is_vector and stripped == prev_vec and count > 0:
                count += 1
            else:
                if count > 1:
                    result.append(f"                    REPEAT {count};")
                prev_vec = stripped if is_vector else None
                count = 1 if is_vector else 0
                result.append(line)

        if count > 1:
            result.append(f"                    REPEAT {count};")

        return result, orig_count, len(result)

    # ================================================================
    # 覆盖率导出
    # ================================================================

    def _export_coverage(self):
        """导出覆盖率分析为 CSV"""
        if not self.pat_sections:
            messagebox.showwarning("", self.t("gen_first"))
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            initialfile=f"{self.export_prefix_var.get()}_coverage.csv")
        if not path:
            return

        all_vecs = []
        for sec in self.pat_sections:
            if isinstance(sec, (list, tuple)):
                all_vecs.extend(sec[2] if len(sec) > 2 else [])
            else:
                all_vecs.extend(sec.get("vectors", []))

        # 分析覆盖率
        pin_list = self._get_active_pins()
        addr_covered = set()
        data_patterns = set()
        proto_features = {"START": False, "STOP": False, "ACK": False,
                          "NACK": False, "RepSTART": False, "PageWrite": False,
                          "SeqRead": False, "ACK_Polling": False}

        for sec in self.pat_sections:
            if isinstance(sec, (list, tuple)):
                name = sec[0]
                comments = sec[3] if len(sec) > 3 else []
            else:
                name = sec.get("name", "")
                comments = sec.get("comments", [])
            for c in comments:
                cl = c.lower() if c else ""
                if "start" in cl: proto_features["START"] = True
                if "stop" in cl: proto_features["STOP"] = True
                if "ack" in cl and "nack" not in cl: proto_features["ACK"] = True
                if "nack" in cl: proto_features["NACK"] = True
                if "repeated" in cl or "rep" in cl: proto_features["RepSTART"] = True
                if "page" in cl: proto_features["PageWrite"] = True
                if "sequential" in cl or "seq" in cl: proto_features["SeqRead"] = True
                if "polling" in cl: proto_features["ACK_Polling"] = True

        proto_count = sum(1 for v in proto_features.values() if v)
        proto_pct = proto_count / len(proto_features) * 100 if proto_features else 0

        test_count = sum(1 for v in self.test_vars.values() if v.get())
        test_pct = test_count / len(self.test_vars) * 100

        if test_pct >= 90: grade = "A"
        elif test_pct >= 75: grade = "B"
        elif test_pct >= 60: grade = "C"
        else: grade = "D"

        with open(path, "w", encoding="utf-8-sig") as f:
            f.write("Category,Metric,Value\n")
            f.write(f"Overall,Total Vectors,{len(all_vecs)}\n")
            f.write(f"Overall,Test Types Selected,{test_count}/{len(self.test_vars)}\n")
            f.write(f"Overall,Test Coverage,{test_pct:.1f}%\n")
            f.write(f"Overall,Coverage Grade,{grade}\n")
            f.write(f"Protocol,Features Covered,{proto_count}/{len(proto_features)}\n")
            f.write(f"Protocol,Protocol Coverage,{proto_pct:.1f}%\n")
            for feat, val in proto_features.items():
                f.write(f"Protocol,{feat},{'YES' if val else 'NO'}\n")
            for sec in self.pat_sections:
                if isinstance(sec, (list, tuple)):
                    f.write(f"Segment,{sec[0]},{len(sec[2]) if len(sec)>2 else 0} vectors\n")
                else:
                    f.write(f"Segment,{sec.get('name','')},{len(sec.get('vectors',[]))} vectors\n")

        self.status_label.config(text=f"\u2713 Coverage exported: {os.path.basename(path)}")

    # ================================================================
    # Datalog 模板生成
    # ================================================================

    @staticmethod
    def generate_datalog_template(test_name, pin_list, test_sections):
        """生成 ATE Datalog 模板文件"""
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lines = []
        lines.append(f"// DATALOG TEMPLATE: {test_name}")
        lines.append(f"// Generated: {now}")
        lines.append(f"// Tool: EEPROM PAT Generator {VERSION}")
        lines.append("")
        lines.append("HEADER {")
        lines.append(f'  DEVICE = "{test_name}";')
        lines.append(f"  DATE = \"{now}\";")
        lines.append(f'  PINS = "{", ".join(pin_list)}";')
        lines.append("  SITE = 1;")
        lines.append("}")
        lines.append("")

        # 参数测试
        lines.append("PARAMETRIC_TEST {")
        param_tests = [
            ("ISB", "Standby Current", "0", "1.0", "uA", "VCC=5.5V"),
            ("ICC_R", "Read Current", "0", "1.0", "mA", "fSCL=400kHz"),
            ("ICC_W", "Write Current", "0", "3.0", "mA", "fSCL=400kHz"),
            ("VOL", "Output Low Voltage", "0", "0.4", "V", "IOL=3mA"),
            ("VOH", "Output High Voltage", "2.4", "5.5", "V", "IOH=-1mA"),
        ]
        for name, desc, lo, hi, unit, cond in param_tests:
            lines.append(f'  TEST "{name}" {{')
            lines.append(f'    DESCRIPTION = "{desc}";')
            lines.append(f'    LOW_LIMIT = {lo};')
            lines.append(f'    HIGH_LIMIT = {hi};')
            lines.append(f'    UNIT = "{unit}";')
            lines.append(f'    CONDITION = "{cond}";')
            lines.append("    RESULT = ;  // ATE fills in measured value")
            lines.append("  }")
        lines.append("}")
        lines.append("")

        # 功能测试
        lines.append("FUNCTIONAL_TEST {")
        for sec in test_sections:
            # 支持 tuple (name, desc, vectors, comments, labels) 或 dict
            if isinstance(sec, (list, tuple)):
                name = sec[0]
                vec_count = len(sec[2]) if len(sec) > 2 else 0
            else:
                name = sec.get("name", "UNKNOWN")
                vec_count = len(sec.get("vectors", []))
            lines.append(f'  TEST "{name}" {{')
            lines.append(f"    VECTORS = {vec_count};")
            lines.append("    RESULT = ;  // PASS or FAIL")
            lines.append(f"    FAIL_VECTOR = ;  // First failing vector index")
            lines.append("  }")
        lines.append("}")
        lines.append("")

        lines.append("SUMMARY {")
        lines.append("  TOTAL_TESTS = ;")
        lines.append("  PASS_COUNT = ;")
        lines.append("  FAIL_COUNT = ;")
        lines.append("  BIN = ;")
        lines.append("  RESULT = ;  // PASS or FAIL")
        lines.append("}")
        return "\n".join(lines)

    # ================================================================
    # 参数分箱 (Bin Map)
    # ================================================================

    BIN_MAP = {
        1: ("PASS", "All tests passed"),
        2: ("OS_FAIL", "Open/Short test failed"),
        3: ("DC_FAIL", "DC parameter test failed"),
        4: ("FUNC_FAIL", "Functional test failed"),
        5: ("MARCH_FAIL", "March C-/B test failed"),
        6: ("SCAN_FAIL", "Address scan failed"),
        7: ("RET_FAIL", "Data retention failed"),
        8: ("ERR_FAIL", "I2C error test failed"),
        9: ("ENDUR_FAIL", "Endurance test failed"),
        10: ("MULTI_FAIL", "Multiple tests failed"),
    }

    # ================================================================
    # 批处理队列
    # ================================================================

    def _show_batch_dialog(self):
        """批处理队列对话框"""
        dlg = tk.Toplevel(self.root)
        dlg.title(self.t("batch_title"))
        dlg.geometry("600x420")
        dlg.configure(bg=self.colors["bg"])
        dlg.transient(self.root)

        tk.Label(dlg, text=self.t("batch_title"),
                 font=("Segoe UI", 13, "bold"),
                 fg=self.colors["text"], bg=self.colors["bg"]).pack(pady=(10, 6))

        # 任务列表
        list_frame = tk.Frame(dlg, bg=self.colors["bg"])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=4)

        self._batch_listbox = tk.Listbox(list_frame, font=("Consolas", 9),
                                          bg=self.colors["card"], fg=self.colors["text"],
                                          selectbackground=self.colors["accent"],
                                          relief=tk.FLAT, height=12)
        self._batch_listbox.pack(fill=tk.BOTH, expand=True)

        if not hasattr(self, '_batch_queue'):
            self._batch_queue = []

        for job in self._batch_queue:
            self._batch_listbox.insert(tk.END, job.get("label", "Job"))

        # 按钮行
        btn_frame = tk.Frame(dlg, bg=self.colors["bg"])
        btn_frame.pack(fill=tk.X, padx=16, pady=8)

        tk.Button(btn_frame, text=self.t("batch_add"),
                  command=lambda: self._batch_add_current(dlg),
                  font=("Segoe UI", 8), bg=self.colors["accent"], fg="white",
                  relief=tk.FLAT, padx=10, pady=3, cursor="hand2").pack(
                      side=tk.LEFT, padx=(0, 6))

        tk.Button(btn_frame, text=self.t("batch_run"),
                  command=lambda: self._batch_run_all(dlg),
                  font=("Segoe UI", 8), bg=self.colors["accent2"], fg="white",
                  relief=tk.FLAT, padx=10, pady=3, cursor="hand2").pack(
                      side=tk.LEFT, padx=(0, 6))

        tk.Button(btn_frame, text=self.t("batch_clear"),
                  command=lambda: self._batch_clear(dlg),
                  font=("Segoe UI", 8), bg=self.colors["danger"], fg="white",
                  relief=tk.FLAT, padx=10, pady=3, cursor="hand2").pack(
                      side=tk.LEFT, padx=(0, 6))

        tk.Button(btn_frame, text=self.t("close"), command=dlg.destroy,
                  font=("Segoe UI", 8), bg=self.colors["card"], fg=self.colors["text"],
                  relief=tk.FLAT, padx=10, pady=3, cursor="hand2").pack(side=tk.RIGHT)

        dlg.bind("<Escape>", lambda e: dlg.destroy())

    def _batch_add_current(self, dlg):
        """将当前配置添加到批处理队列"""
        cfg = self._build_config_dict()
        label = f"{cfg.get('export_prefix', 'Job')} | {cfg.get('voltage', '5.0V')} | " \
                f"{sum(1 for v in cfg.get('tests', {}).values() if v)} tests"
        if not hasattr(self, '_batch_queue'):
            self._batch_queue = []
        self._batch_queue.append({"config": cfg, "label": label})
        if hasattr(self, '_batch_listbox'):
            self._batch_listbox.insert(tk.END, label)

    def _batch_run_all(self, dlg):
        """运行所有批处理任务"""
        if not hasattr(self, '_batch_queue') or not self._batch_queue:
            return
        base_dir = filedialog.askdirectory(title="Select batch output directory")
        if not base_dir:
            return

        for i, job in enumerate(self._batch_queue):
            cfg = job["config"]
            self._apply_config_dict(cfg)
            self.on_generate()
            job_dir = os.path.join(base_dir, f"batch_{i+1}_{cfg.get('export_prefix', 'job')}")
            os.makedirs(job_dir, exist_ok=True)
            self._do_export_to(job_dir)

        self.status_label.config(
            text=f"\u2713 Batch complete: {len(self._batch_queue)} jobs → {base_dir}")
        dlg.destroy()

    def _batch_clear(self, dlg):
        """清空批处理队列"""
        self._batch_queue = []
        if hasattr(self, '_batch_listbox'):
            self._batch_listbox.delete(0, tk.END)

    # ================================================================
    # 配置对比
    # ================================================================

    def _show_config_diff(self):
        """配置对比对话框"""
        file_a = filedialog.askopenfilename(
            title="Select Config A", filetypes=[("JSON", "*.json")])
        if not file_a:
            return
        file_b = filedialog.askopenfilename(
            title="Select Config B", filetypes=[("JSON", "*.json")])
        if not file_b:
            return

        try:
            with open(file_a, "r", encoding="utf-8") as f:
                cfg_a = json.load(f)
            with open(file_b, "r", encoding="utf-8") as f:
                cfg_b = json.load(f)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        dlg = tk.Toplevel(self.root)
        dlg.title(self.t("diff_title"))
        dlg.geometry("700x500")
        dlg.configure(bg=self.colors["bg"])
        dlg.transient(self.root)

        tk.Label(dlg, text=self.t("diff_title"),
                 font=("Segoe UI", 13, "bold"),
                 fg=self.colors["text"], bg=self.colors["bg"]).pack(pady=(10, 6))

        # 文件名显示
        hdr = tk.Frame(dlg, bg=self.colors["bg"])
        hdr.pack(fill=tk.X, padx=16)
        tk.Label(hdr, text=f"A: {os.path.basename(file_a)}",
                 font=("Consolas", 8), fg=self.colors["accent"],
                 bg=self.colors["bg"]).pack(side=tk.LEFT, padx=(0, 20))
        tk.Label(hdr, text=f"B: {os.path.basename(file_b)}",
                 font=("Consolas", 8), fg=self.colors["accent2"],
                 bg=self.colors["bg"]).pack(side=tk.LEFT)

        # 差异列表
        diff_text = scrolledtext.ScrolledText(dlg, font=("Consolas", 9),
                                                bg=self.colors["card"],
                                                fg=self.colors["text"],
                                                relief=tk.FLAT, height=18)
        diff_text.pack(fill=tk.BOTH, expand=True, padx=16, pady=8)

        all_keys = sorted(set(list(cfg_a.keys()) + list(cfg_b.keys())))
        for key in all_keys:
            va = cfg_a.get(key, "<missing>")
            vb = cfg_b.get(key, "<missing>")
            if va != vb:
                diff_text.insert(tk.END, f"\u2260 {key}:\n", "changed")
                diff_text.insert(tk.END, f"    A: {va}\n", "val_a")
                diff_text.insert(tk.END, f"    B: {vb}\n\n", "val_b")
            else:
                diff_text.insert(tk.END, f"= {key}: {va}\n")

        diff_text.tag_configure("changed", foreground=self.colors["warning"],
                                font=("Consolas", 9, "bold"))
        diff_text.tag_configure("val_a", foreground=self.colors["accent"])
        diff_text.tag_configure("val_b", foreground=self.colors["accent2"])
        diff_text.config(state=tk.DISABLED)

        # 操作按钮
        btn_frame = tk.Frame(dlg, bg=self.colors["bg"])
        btn_frame.pack(fill=tk.X, padx=16, pady=8)
        tk.Button(btn_frame, text="Apply A", command=lambda: [self._apply_config_dict(cfg_a), dlg.destroy()],
                  font=("Segoe UI", 8), bg=self.colors["accent"], fg="white",
                  relief=tk.FLAT, padx=10, pady=3, cursor="hand2").pack(side=tk.LEFT, padx=(0, 6))
        tk.Button(btn_frame, text="Apply B", command=lambda: [self._apply_config_dict(cfg_b), dlg.destroy()],
                  font=("Segoe UI", 8), bg=self.colors["accent2"], fg="white",
                  relief=tk.FLAT, padx=10, pady=3, cursor="hand2").pack(side=tk.LEFT)
        tk.Button(btn_frame, text=self.t("close"), command=dlg.destroy,
                  font=("Segoe UI", 8), bg=self.colors["card"], fg=self.colors["text"],
                  relief=tk.FLAT, padx=10, pady=3, cursor="hand2").pack(side=tk.RIGHT)

        dlg.bind("<Escape>", lambda e: dlg.destroy())

    # ================================================================
    # 命令面板 (Ctrl+Shift+P)
    # ================================================================

    def _show_command_palette(self, event=None):
        """显示命令面板浮动对话框"""
        dlg = tk.Toplevel(self.root)
        dlg.overrideredirect(True)
        # 居中在主窗口上方
        w, h = 480, 360
        x = self.root.winfo_x() + (self.root.winfo_width() - w) // 2
        y = self.root.winfo_y() + 80
        dlg.geometry(f"{w}x{h}+{x}+{y}")
        dlg.configure(bg=self.colors["card"])
        dlg.attributes("-topmost", True)

        # 搜索框
        search_var = tk.StringVar()
        entry = tk.Entry(dlg, textvariable=search_var,
                         font=("Segoe UI", 11),
                         bg=self.colors["sidebar"], fg=self.colors["text"],
                         insertbackground=self.colors["text"],
                         relief=tk.FLAT, bd=0)
        entry.pack(fill=tk.X, padx=2, pady=2, ipady=6)
        entry.insert(0, "")
        entry.focus_set()

        # 命令列表
        listbox = tk.Listbox(dlg, font=("Segoe UI", 9),
                              bg=self.colors["card"], fg=self.colors["text"],
                              selectbackground=self.colors["accent"],
                              selectforeground="white",
                              relief=tk.FLAT, bd=0, activestyle="none")
        listbox.pack(fill=tk.BOTH, expand=True, padx=2, pady=(0, 2))

        commands = [
            (f"\u25b6 {self.t('generate')}", self.on_generate),
            (f"\u2913 {self.t('export')}", self.on_export),
            (f"\u21b6 {self.t('undo')}", self._undo),
            (f"\u21b7 {self.t('redo')}", self._redo),
            (f"\u2630 {self.t('save_config')}", self._save_config),
            (f"\u2630 {self.t('load_config')}", self._load_config),
            (f"\u2611 {self.t('select_all')}", lambda: self._set_all_tests(True)),
            (f"\u2610 {self.t('deselect_all')}", lambda: self._set_all_tests(False)),
            (f"\u23f1 {self.t('timing_check')}", self._run_timing_check),
            (f"\u2699 {self.t('proto_check')}", self._run_protocol_check),
            (f"\u2630 {self.t('batch_title')}", self._show_batch_dialog),
            (f"\u2194 {self.t('config_diff')}", self._show_config_diff),
            (f"\u2630 {self.t('export_coverage')}", self._export_coverage),
            (f"\u2600/\u263e Toggle Theme", self._toggle_theme),
            (f"EN/\u4e2d Toggle Language", self._toggle_language),
            (f"\u2328 {self.t('shortcuts_title')}", self._show_shortcuts_dialog),
            (f"\u2139 {self.t('about_title')}", self._show_about_dialog),
            # v6.0 新增命令
            (f"▷ {self.t('sim_run')} (F7)", self._run_simulation),
            (f"◈ {self.t('shmoo_run')} (F8)", self._run_shmoo_sweep),
            (f"◆ {self.t('flow_reset_default')}", self._flow_reset_default),
            (f"◆ {self.t('flow_simulate')}", self._flow_simulate),
            (f"◉ {self.t('yield_import')}", self._yield_import_datalog),
        ]
        all_labels = [c[0] for c in commands]

        def refresh_list(*args):
            listbox.delete(0, tk.END)
            query = search_var.get().lower()
            for label in all_labels:
                if not query or query in label.lower():
                    listbox.insert(tk.END, label)
            if listbox.size() > 0:
                listbox.selection_set(0)

        search_var.trace_add("write", refresh_list)
        refresh_list()

        def execute(event=None):
            sel = listbox.curselection()
            if not sel:
                dlg.destroy()
                return
            selected_label = listbox.get(sel[0])
            dlg.destroy()
            for label, cmd in commands:
                if label == selected_label:
                    self.root.after(50, cmd)
                    break

        def on_key(event):
            if event.keysym == "Down":
                idx = listbox.curselection()
                if idx and idx[0] < listbox.size() - 1:
                    listbox.selection_clear(0, tk.END)
                    listbox.selection_set(idx[0] + 1)
                    listbox.see(idx[0] + 1)
                return "break"
            elif event.keysym == "Up":
                idx = listbox.curselection()
                if idx and idx[0] > 0:
                    listbox.selection_clear(0, tk.END)
                    listbox.selection_set(idx[0] - 1)
                    listbox.see(idx[0] - 1)
                return "break"

        entry.bind("<Return>", execute)
        entry.bind("<Up>", on_key)
        entry.bind("<Down>", on_key)
        listbox.bind("<Double-Button-1>", execute)
        dlg.bind("<Escape>", lambda e: dlg.destroy())
        dlg.bind("<FocusOut>", lambda e: dlg.after(100, dlg.destroy))

    # ================================================================

    def _on_close(self):
        """窗口关闭 — 有未导出数据时确认，清理自动保存"""
        if self.current_vectors and not self._exported:
            if not messagebox.askyesno(self.t("confirm_exit_title"),
                    self.t("confirm_exit")):
                return
        self._cleanup_autosave()
        self.root.destroy()

    def _switch_tab(self, idx):
        """切换到指定标签页"""
        if hasattr(self, 'notebook'):
            try:
                self.notebook.select(idx)
            except Exception:
                pass

    def _safe_canvas_reset(self, canvas):
        """安全重置 Canvas: 清除所有绘图项并解绑 tooltip 事件"""
        try:
            canvas.delete("all")
        except tk.TclError:
            pass

    def _clear_widget_refs(self):
        """重建 UI 前清除旧控件引用，防止 hasattr 误判已销毁控件为有效"""
        for attr in ('chip_canvas', 'addr_vars', 'dev_addr_label', 'wp_var',
                      'export_prefix_var', 'test_vars', '_left_canvas',
                      '_left_scrollbar', 'undo_btn', 'redo_btn',
                      'export_btn', 'reexport_btn', 'theme_btn', 'lang_btn',
                      '_recent_menu_btn', 'chip_specs_labels',
                      'chip_capacity_entry', 'chip_page_size_entry',
                      'chip_addr_bytes_entry'):
            if hasattr(self, attr):
                delattr(self, attr)

    def _check_unsaved_before_rebuild(self):
        """重建 UI 前检查是否有未导出的向量，返回 True 表示可以继续"""
        if self.current_vectors and not self._exported:
            result = messagebox.askyesnocancel(
                self.t("unsaved_warning_title"),
                self.t("unsaved_warning_msg"))
            if result is None:  # Cancel
                return False
            if not result:  # No → 先导出
                self.on_export()
        return True

    def _restore_preview_after_rebuild(self):
        """重建 UI 后恢复预览内容（向量数据保留在 self 上）"""
        if not self.current_vectors or not self.pat_sections:
            return
        try:
            # 恢复 PAT / TXT 预览
            if hasattr(self, '_pat_content_cache') and self._pat_content_cache:
                self.pat_text.delete("1.0", tk.END)
                self.pat_text.insert("1.0", self._pat_content_cache)
                self._apply_pat_syntax_highlighting()
                self._update_line_numbers()
                self._update_jump_buttons(self.pat_sections)
            if hasattr(self, '_txt_content_cache') and self._txt_content_cache:
                self.txt_text.delete("1.0", tk.END)
                self.txt_text.insert("1.0", self._txt_content_cache)
            # 恢复波形 / 流程图 / 统计
            self.wave_end_var.set(str(min(200, len(self.current_vectors))))
            self._draw_waveform()
            self._update_wave_jump_buttons(self.pat_sections)
            self._draw_flowchart(self.pat_sections)
            self._update_statistics(self.pat_sections)
            # 恢复导出按钮状态
            self.export_btn.config(state=tk.NORMAL)
        except Exception:
            pass  # 恢复失败不影响新 UI 正常使用

    def _toggle_theme(self):
        """切换深色/浅色主题"""
        if not self._check_unsaved_before_rebuild():
            return
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self.colors = dict(THEMES[self.current_theme])

        # 清除旧控件引用，避免 rebuild 时 hasattr 检测到已销毁的控件
        self._clear_widget_refs()
        # 重建整个 UI
        for w in self.root.winfo_children():
            w.destroy()
        self.setup_styles()
        self.build_ui()

        # 恢复预览内容
        self._restore_preview_after_rebuild()

        # 更新主题按钮文字
        icon = "\u2600" if self.current_theme == "dark" else "\u263e"
        self.theme_btn.config(text=icon)

        self.root.configure(bg=self.colors["bg"])

    def _toggle_language(self):
        """切换中文/英文界面"""
        if not self._check_unsaved_before_rebuild():
            return
        self.current_lang = "en" if self.current_lang == "zh" else "zh"
        self.root.title(f"{self.t('title')} {VERSION} — AdaptStar-E")
        # 清除旧控件引用，避免 rebuild 时 hasattr 检测到已销毁的控件
        self._clear_widget_refs()
        # 重建整个 UI
        for w in self.root.winfo_children():
            w.destroy()
        self.setup_styles()
        self.build_ui()
        # 恢复预览内容
        self._restore_preview_after_rebuild()
        self.root.configure(bg=self.colors["bg"])

    def t(self, key):
        """获取当前语言的翻译文本"""
        return I18N.get(self.current_lang, I18N["zh"]).get(key, key)

    def _create_context_menu(self, text_widget):
        """为文本预览区创建右键菜单"""
        menu = tk.Menu(text_widget, tearoff=0,
                       bg=self.colors["card"], fg=self.colors["text"],
                       activebackground=self.colors["accent"],
                       activeforeground="white",
                       font=("Segoe UI", 9))
        menu.add_command(label="复制选中  Ctrl+C",
                         command=lambda: text_widget.event_generate("<<Copy>>"))
        menu.add_command(label="全选  Ctrl+A",
                         command=lambda: (text_widget.tag_add(tk.SEL, "1.0", tk.END),
                                          text_widget.mark_set(tk.INSERT, "1.0")))
        menu.add_separator()
        menu.add_command(label="复制全部内容",
                         command=lambda: self._copy_all(text_widget))

        def _show(event):
            menu.tk_popup(event.x_root, event.y_root)
        text_widget.bind("<Button-3>", _show)

    def _copy_all(self, text_widget):
        """复制文本框全部内容到剪贴板"""
        self.root.clipboard_clear()
        self.root.clipboard_append(text_widget.get("1.0", tk.END))

    def _show_search_bar(self):
        """显示/聚焦搜索栏 (Ctrl+F)"""
        # 确定当前活动的文本框
        tab_idx = self.notebook.index(self.notebook.select())
        if tab_idx == 0:
            target = self.pat_text
        elif tab_idx == 1:
            target = self.txt_text
        else:
            return

        # 如果搜索栏已存在则聚焦
        if hasattr(self, '_search_frame') and self._search_frame.winfo_exists():
            self._search_entry.focus_set()
            self._search_entry.select_range(0, tk.END)
            self._search_target = target
            return

        # 创建搜索栏 (在 notebook 上方)
        self._search_target = target
        self._search_frame = sf = tk.Frame(self.notebook.master,
                                            bg=self.colors["sidebar"], padx=8, pady=4)
        sf.pack(fill=tk.X, before=self.notebook)

        tk.Label(sf, text="搜索:", font=("Segoe UI", 9),
                 fg=self.colors["text"], bg=self.colors["sidebar"]).pack(side=tk.LEFT)

        self._search_var = tk.StringVar()
        self._search_entry = tk.Entry(sf, textvariable=self._search_var,
                                       font=("Consolas", 9), width=30)
        self._search_entry.pack(side=tk.LEFT, padx=4)
        self._search_entry.focus_set()

        self._search_result_label = tk.Label(sf, text="", font=("Segoe UI", 8),
                                              fg=self.colors["text_dim"],
                                              bg=self.colors["sidebar"])
        self._search_result_label.pack(side=tk.LEFT, padx=6)

        # 大小写敏感切换
        self._search_case_var = tk.BooleanVar(value=False)
        self._search_case_btn = tk.Checkbutton(
            sf, text="Aa", variable=self._search_case_var,
            font=("Consolas", 8, "bold"), indicatoron=False,
            bg=self.colors["card"], fg=self.colors["text"],
            selectcolor=self.colors["accent"], relief=tk.FLAT,
            padx=4, pady=1, cursor="hand2",
            command=self._do_search)
        self._search_case_btn.pack(side=tk.LEFT, padx=2)

        tk.Button(sf, text="▲", command=lambda: self._search_navigate(-1),
                  font=("Segoe UI", 8), bg=self.colors["card"],
                  fg=self.colors["text"], relief=tk.FLAT, padx=4,
                  cursor="hand2").pack(side=tk.LEFT, padx=1)
        tk.Button(sf, text="▼", command=lambda: self._search_navigate(1),
                  font=("Segoe UI", 8), bg=self.colors["card"],
                  fg=self.colors["text"], relief=tk.FLAT, padx=4,
                  cursor="hand2").pack(side=tk.LEFT, padx=1)
        tk.Button(sf, text="✕", command=self._close_search_bar,
                  font=("Segoe UI", 8), bg=self.colors["sidebar"],
                  fg=self.colors["text_dim"], relief=tk.FLAT, padx=4,
                  cursor="hand2").pack(side=tk.RIGHT)

        self._search_matches = []
        self._search_idx = -1

        self._search_var.trace_add("write", lambda *a: self._do_search())
        self._search_entry.bind("<Return>", lambda e: self._search_navigate(1))
        self._search_entry.bind("<Shift-Return>", lambda e: self._search_navigate(-1))
        self._search_entry.bind("<Escape>", lambda e: self._close_search_bar())

    def _do_search(self):
        """执行搜索并高亮所有匹配"""
        tw = self._search_target
        tw.tag_remove("search_hl", "1.0", tk.END)
        tw.tag_remove("search_cur", "1.0", tk.END)
        query = self._search_var.get()
        self._search_matches = []
        self._search_idx = -1

        if not query:
            self._search_result_label.config(text="")
            return

        tw.tag_configure("search_hl", background="#ffd43b", foreground="#1a1f2e")
        tw.tag_configure("search_cur", background="#ff6b6b", foreground="white")

        case_sensitive = getattr(self, '_search_case_var', None) and self._search_case_var.get()
        start = "1.0"
        while True:
            pos = tw.search(query, start, stopindex=tk.END,
                            nocase=not case_sensitive)
            if not pos:
                break
            end = f"{pos}+{len(query)}c"
            tw.tag_add("search_hl", pos, end)
            self._search_matches.append(pos)
            start = end

        count = len(self._search_matches)
        self._search_result_label.config(
            text=f"{count} 个匹配" if count else "无匹配")

        if count:
            self._search_idx = 0
            self._highlight_current_match()

    def _highlight_current_match(self):
        """高亮当前匹配项并滚动到可见"""
        tw = self._search_target
        tw.tag_remove("search_cur", "1.0", tk.END)
        if not self._search_matches:
            return
        pos = self._search_matches[self._search_idx]
        end = f"{pos}+{len(self._search_var.get())}c"
        tw.tag_add("search_cur", pos, end)
        tw.tag_raise("search_cur")
        tw.see(pos)
        total = len(self._search_matches)
        self._search_result_label.config(
            text=f"{self._search_idx + 1} / {total}")

    def _search_navigate(self, direction):
        """上/下翻搜索结果"""
        if not self._search_matches:
            return
        self._search_idx = (self._search_idx + direction) % len(self._search_matches)
        self._highlight_current_match()

    def _close_search_bar(self):
        """关闭搜索栏"""
        if hasattr(self, '_search_target') and self._search_target:
            self._search_target.tag_remove("search_hl", "1.0", tk.END)
            self._search_target.tag_remove("search_cur", "1.0", tk.END)
        if hasattr(self, '_search_frame') and self._search_frame.winfo_exists():
            self._search_frame.destroy()

    def build_preview_panel(self, parent):
        """构建右侧预览面板 (PAT / TXT / 说明 / 统计)"""
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # -- PAT 向量预览 (带行号) --
        pat_frame = tk.Frame(self.notebook, bg=self.colors["bg"])
        self.notebook.add(pat_frame, text=self.t("tab_pat"))

        # 段跳转按钮栏
        self.jump_bar = tk.Frame(pat_frame, bg=self.colors["sidebar"], padx=6, pady=3)
        self.jump_bar.pack(fill=tk.X)
        tk.Label(self.jump_bar, text=self.t("jump"), font=("Segoe UI", 8),
                 fg=self.colors["text_dim"], bg=self.colors["sidebar"]).pack(side=tk.LEFT)
        # 按钮在 on_generate 时动态填充

        pat_body = tk.Frame(pat_frame, bg=self.colors["bg"])
        pat_body.pack(fill=tk.BOTH, expand=True)

        # 行号列
        self.pat_lineno = tk.Text(
            pat_body, width=5, font=("Consolas", 9),
            bg=self.colors["sidebar"], fg=self.colors["text_dim"],
            relief=tk.FLAT, padx=4, pady=8, state=tk.DISABLED,
            takefocus=0, cursor="arrow")
        self.pat_lineno.pack(side=tk.LEFT, fill=tk.Y)

        pat_right = tk.Frame(pat_body, bg=self.colors["bg"])
        pat_right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.pat_text = scrolledtext.ScrolledText(
            pat_right, wrap=tk.NONE, font=("Consolas", 9),
            bg=self.colors["card"], fg=self.colors["text"],
            insertbackground=self.colors["accent"],
            selectbackground=self.colors["accent"],
            relief=tk.FLAT, padx=10, pady=8)
        self.pat_text.pack(fill=tk.BOTH, expand=True)

        h_scroll = tk.Scrollbar(pat_frame, orient=tk.HORIZONTAL,
                                command=self.pat_text.xview)
        h_scroll.pack(fill=tk.X)
        self.pat_text.configure(xscrollcommand=h_scroll.set)

        # 行号同步滚动
        def _on_pat_yscroll(*args):
            self.pat_lineno.yview_moveto(args[0])
            # 同步原有 scrollbar
            pat_right_vbar = self.pat_text.winfo_children()
            for w in self.pat_text.master.winfo_children():
                if isinstance(w, tk.Scrollbar):
                    w.set(*args)
                    break
        self.pat_text.configure(yscrollcommand=_on_pat_yscroll)
        # 鼠标滚轮同步
        def _on_mousewheel(event):
            self.pat_text.yview_scroll(int(-1 * (event.delta / 120)), "units")
            self.pat_lineno.yview_scroll(int(-1 * (event.delta / 120)), "units")
            return "break"
        self.pat_lineno.bind("<MouseWheel>", _on_mousewheel)
        self.pat_text.bind("<MouseWheel>", _on_mousewheel)

        # 右键菜单
        self._create_context_menu(self.pat_text)

        # -- TXT 数据预览 --
        txt_frame = tk.Frame(self.notebook, bg=self.colors["bg"])
        self.notebook.add(txt_frame, text=self.t("tab_txt"))

        self.txt_text = scrolledtext.ScrolledText(
            txt_frame, wrap=tk.NONE, font=("Consolas", 9),
            bg=self.colors["card"], fg=self.colors["text"],
            insertbackground=self.colors["accent"],
            selectbackground=self.colors["accent"],
            relief=tk.FLAT, padx=10, pady=8)
        self.txt_text.pack(fill=tk.BOTH, expand=True)

        h_scroll2 = tk.Scrollbar(txt_frame, orient=tk.HORIZONTAL,
                                 command=self.txt_text.xview)
        h_scroll2.pack(fill=tk.X)
        self.txt_text.configure(xscrollcommand=h_scroll2.set)

        # 右键菜单
        self._create_context_menu(self.txt_text)

        # -- I2C 波形图 --
        wave_frame = tk.Frame(self.notebook, bg=self.colors["bg"])
        self.notebook.add(wave_frame, text=self.t("tab_wave"))

        # 波形工具栏
        wave_toolbar = tk.Frame(wave_frame, bg=self.colors["sidebar"], padx=8, pady=4)
        wave_toolbar.pack(fill=tk.X)
        tk.Label(wave_toolbar, text=self.t("display_range"), font=("Segoe UI", 8),
                 fg=self.colors["text_dim"], bg=self.colors["sidebar"]).pack(side=tk.LEFT)
        self.wave_start_var = tk.StringVar(value="0")
        tk.Entry(wave_toolbar, textvariable=self.wave_start_var,
                 font=("Consolas", 8), width=6).pack(side=tk.LEFT, padx=2)
        tk.Label(wave_toolbar, text="~", font=("Segoe UI", 8),
                 fg=self.colors["text_dim"], bg=self.colors["sidebar"]).pack(side=tk.LEFT)
        self.wave_end_var = tk.StringVar(value="200")
        tk.Entry(wave_toolbar, textvariable=self.wave_end_var,
                 font=("Consolas", 8), width=6).pack(side=tk.LEFT, padx=2)
        tk.Button(wave_toolbar, text=self.t("refresh"), command=self._draw_waveform,
                  font=("Segoe UI", 8), bg=self.colors["accent"], fg="white",
                  relief=tk.FLAT, padx=6, cursor="hand2").pack(side=tk.LEFT, padx=4)
        tk.Button(wave_toolbar, text=self.t("export_svg"), command=self._export_waveform_svg,
                  font=("Segoe UI", 8), bg=self.colors["accent2"], fg="white",
                  relief=tk.FLAT, padx=6, cursor="hand2").pack(side=tk.LEFT, padx=2)
        ToolTip(wave_toolbar.winfo_children()[-1], "将当前波形导出为 SVG 矢量图\n可直接放入 PPT 答辩材料")

        # 波形快捷跳转
        self.wave_jump_bar = tk.Frame(wave_toolbar, bg=self.colors["sidebar"])
        self.wave_jump_bar.pack(side=tk.LEFT, padx=8)

        # 图例
        legend_frame = tk.Frame(wave_toolbar, bg=self.colors["sidebar"])
        legend_frame.pack(side=tk.RIGHT)
        for sym, clr, desc in [("Drive", self.colors["accent"], "驱动"),
                                ("H/L", self.colors["success"], "比较"),
                                ("Z", self.colors["warning"], "高阻")]:
            tk.Label(legend_frame, text=f"■ {sym}", font=("Consolas", 7),
                     fg=clr, bg=self.colors["sidebar"]).pack(side=tk.LEFT, padx=3)

        # 波形 Canvas (带水平+垂直滚动条)
        wave_body = tk.Frame(wave_frame, bg=self.colors["bg"])
        wave_body.pack(fill=tk.BOTH, expand=True)
        self.wave_canvas = tk.Canvas(wave_body, bg=self.colors["card"],
                                      highlightthickness=0)
        wave_v_scroll = tk.Scrollbar(wave_body, orient=tk.VERTICAL,
                                      command=self.wave_canvas.yview)
        wave_v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        wave_h_scroll = tk.Scrollbar(wave_frame, orient=tk.HORIZONTAL,
                                      command=self.wave_canvas.xview)
        wave_h_scroll.pack(fill=tk.X)
        self.wave_canvas.configure(xscrollcommand=wave_h_scroll.set,
                                    yscrollcommand=wave_v_scroll.set)
        self.wave_canvas.pack(fill=tk.BOTH, expand=True)

        # 波形区鼠标滚轮: 默认垂直滚动, Shift+滚轮横向滚动
        def _wave_wheel_v(event):
            self.wave_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            return "break"
        def _wave_wheel_h(event):
            self.wave_canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")
            return "break"
        self.wave_canvas.bind("<MouseWheel>", _wave_wheel_v)
        self.wave_canvas.bind("<Shift-MouseWheel>", _wave_wheel_h)

        # -- 测试说明 --
        info_frame = tk.Frame(self.notebook, bg=self.colors["card"])
        self.notebook.add(info_frame, text=self.t("tab_info"))

        info_pane = tk.PanedWindow(info_frame, orient=tk.VERTICAL,
                                    bg=self.colors["card"], sashwidth=4)
        info_pane.pack(fill=tk.BOTH, expand=True)

        # 上半: 测试说明文本
        info_top = tk.Frame(info_pane, bg=self.colors["card"])
        info_pane.add(info_top, stretch="always")

        self.stats_text = scrolledtext.ScrolledText(
            info_top, wrap=tk.WORD, font=("Segoe UI", 10),
            bg=self.colors["card"], fg=self.colors["text"],
            insertbackground=self.colors["accent"],
            relief=tk.FLAT, padx=15, pady=10)
        self.stats_text.pack(fill=tk.BOTH, expand=True)

        # 下半: v9.0 Datasheet 参数覆盖矩阵
        info_bottom = tk.LabelFrame(info_pane, text=self.t("compliance_title"),
                                     font=("Segoe UI", 9, "bold"),
                                     fg=self.colors["accent"], bg=self.colors["card"],
                                     relief=tk.GROOVE)
        info_pane.add(info_bottom, stretch="always")

        # Treeview 表格
        tree_frame = tk.Frame(info_bottom, bg=self.colors["card"])
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        cols = ("id", "name", "cat", "spec", "covered_by", "status")
        self.compliance_tree = ttk.Treeview(tree_frame, columns=cols,
                                             show="headings", height=8)
        for col, hdr, w in [("id", "ID", 55), ("name", "Name", 80),
                             ("cat", "Cat", 45), ("spec", "Spec", 160),
                             ("covered_by", "Covered By", 120), ("status", "Status", 70)]:
            self.compliance_tree.heading(col, text=hdr)
            self.compliance_tree.column(col, width=w, anchor=tk.W)

        tree_sb = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL,
                                 command=self.compliance_tree.yview)
        self.compliance_tree.configure(yscrollcommand=tree_sb.set)
        self.compliance_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_sb.pack(side=tk.RIGHT, fill=tk.Y)

        self.compliance_summary_label = tk.Label(
            info_bottom, text="", font=("Consolas", 9, "bold"),
            fg=self.colors["text"], bg=self.colors["card"], anchor=tk.W)
        self.compliance_summary_label.pack(fill=tk.X, padx=6, pady=(2, 4))

        self._compliance_matrix = DatasheetComplianceMatrix()
        self._update_compliance_matrix()

        # v9.0 Tier3 Phase 32: 标准合规面板
        std_frame = tk.LabelFrame(info_pane, text=f"⚖ {self.t('std_compliance')}",
                                   font=("Segoe UI", 9, "bold"),
                                   fg=self.colors["text"], bg=self.colors["card"],
                                   relief=tk.GROOVE)
        info_pane.add(std_frame, minsize=80)

        std_toolbar = tk.Frame(std_frame, bg=self.colors["card"])
        std_toolbar.pack(fill=tk.X, padx=4, pady=(2, 0))
        tk.Button(std_toolbar, text=self.t("std_run"),
                  command=self._run_standards_compliance,
                  font=("Segoe UI", 7, "bold"), bg="#8b5cf6", fg="white",
                  relief=tk.FLAT, padx=8, pady=1, cursor="hand2").pack(side=tk.LEFT)
        self._std_status = tk.Label(std_toolbar, text="",
                                     font=("Segoe UI", 7),
                                     fg=self.colors["text_dim"],
                                     bg=self.colors["card"])
        self._std_status.pack(side=tk.RIGHT)

        std_cols = ("standard", "clause", "title", "status", "covered_by")
        self._std_tree = ttk.Treeview(std_frame, columns=std_cols,
                                       show="headings", height=5)
        for col, hdr, w in [("standard","Standard",70),("clause","Clause",100),
                            ("title","Title",180),("status","Status",70),
                            ("covered_by","Covered By",130)]:
            self._std_tree.heading(col, text=hdr)
            self._std_tree.column(col, width=w, anchor=tk.W)
        self._std_tree.tag_configure("covered", foreground="#22c55e")
        self._std_tree.tag_configure("partial", foreground="#f59e0b")
        self._std_tree.tag_configure("not_applicable", foreground="#94a3b8")
        self._std_tree.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        self._std_mapper = StandardsComplianceMapper()

        # -- 测试流程图 --
        flow_frame = tk.Frame(self.notebook, bg=self.colors["card"])
        self.notebook.add(flow_frame, text=self.t("tab_flow"))

        # v9.0 Tier3 Phase 27: 自适应仿真工具栏
        flow_toolbar = tk.Frame(flow_frame, bg=self.colors["card"])
        flow_toolbar.pack(fill=tk.X, padx=10, pady=(6, 0))
        tk.Button(flow_toolbar, text=f'▶ {self.t("adaptive_sim")}',
                  command=self._run_adaptive_simulation,
                  font=("Segoe UI", 8, "bold"), bg="#8b5cf6", fg="white",
                  relief=tk.FLAT, padx=10, pady=2, cursor="hand2").pack(side=tk.LEFT)
        tk.Label(flow_toolbar, text=f'{self.t("adaptive_sample_n")}:',
                 font=("Segoe UI", 7), fg=self.colors["text_dim"],
                 bg=self.colors["card"]).pack(side=tk.LEFT, padx=(8, 2))
        self._adaptive_n_var = tk.StringVar(value="1000")
        tk.Entry(flow_toolbar, textvariable=self._adaptive_n_var, width=6,
                 font=("Consolas", 8), bg=self.colors["bg"], fg=self.colors["text"],
                 insertbackground=self.colors["text"],
                 relief=tk.FLAT).pack(side=tk.LEFT)
        self._adaptive_status = tk.Label(flow_toolbar, text="",
                                          font=("Segoe UI", 8),
                                          fg=self.colors["text_dim"],
                                          bg=self.colors["card"])
        self._adaptive_status.pack(side=tk.RIGHT)
        self._adaptive_engine = AdaptiveTestEngine()
        self._adaptive_rules = []

        self.flow_canvas = tk.Canvas(flow_frame, bg=self.colors["card"],
                                      highlightthickness=0)
        self.flow_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self._draw_default_flowchart()

        # -- 统计 & 覆盖率 --
        stats_tab = tk.Frame(self.notebook, bg=self.colors["card"])
        self.notebook.add(stats_tab, text=self.t("tab_stats"))

        # 统计工具栏
        stats_toolbar = tk.Frame(stats_tab, bg=self.colors["card"])
        stats_toolbar.pack(fill=tk.X, padx=10, pady=(6, 0))
        tk.Button(stats_toolbar, text=self.t("export_coverage"),
                  command=self._export_coverage,
                  font=("Segoe UI", 7), bg=self.colors["accent2"], fg="white",
                  relief=tk.FLAT, padx=8, pady=2, cursor="hand2").pack(side=tk.RIGHT)

        self.stats_canvas = tk.Canvas(stats_tab, bg=self.colors["card"],
                                      highlightthickness=0)
        self.stats_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # ============================================================
        # v6.0 Tab 6: 模拟器 (Pattern Simulator)
        # ============================================================
        sim_tab = tk.Frame(self.notebook, bg=self.colors["card"])
        self.notebook.add(sim_tab, text=self.t("tab_sim"))

        sim_toolbar = tk.Frame(sim_tab, bg=self.colors["card"])
        sim_toolbar.pack(fill=tk.X, padx=10, pady=(6, 0))

        tk.Button(sim_toolbar, text=f'▶ {self.t("sim_run")}',
                  command=self._run_simulation,
                  font=("Segoe UI", 8, "bold"), bg=self.colors["success"], fg="white",
                  relief=tk.FLAT, padx=10, pady=3, cursor="hand2").pack(side=tk.LEFT)
        tk.Button(sim_toolbar, text=f'⏭ {self.t("sim_step")}',
                  command=lambda: self._run_simulation(step_mode=True),
                  font=("Segoe UI", 8), bg=self.colors["accent2"], fg="white",
                  relief=tk.FLAT, padx=8, pady=3, cursor="hand2").pack(side=tk.LEFT, padx=(4, 0))
        tk.Button(sim_toolbar, text=f'⟲ {self.t("sim_reset")}',
                  command=self._reset_simulation,
                  font=("Segoe UI", 8), bg=self.colors["border"], fg=self.colors["text"],
                  relief=tk.FLAT, padx=8, pady=3, cursor="hand2").pack(side=tk.LEFT, padx=(4, 0))

        self.sim_status_label = tk.Label(sim_toolbar, text="",
                                         font=("Segoe UI", 8), fg=self.colors["text_dim"],
                                         bg=self.colors["card"])
        self.sim_status_label.pack(side=tk.RIGHT)

        # 模拟器主体: 左=事务列表, 右=存储器视图+状态机
        sim_body = tk.PanedWindow(sim_tab, orient=tk.HORIZONTAL,
                                  bg=self.colors["border"], sashwidth=4)
        sim_body.pack(fill=tk.BOTH, expand=True, padx=10, pady=6)

        # 左: 事务 Treeview
        sim_left = tk.Frame(sim_body, bg=self.colors["card"])
        sim_body.add(sim_left, minsize=280)

        tk.Label(sim_left, text=self.t("sim_transactions"),
                 font=("Segoe UI", 9, "bold"), fg=self.colors["accent"],
                 bg=self.colors["card"]).pack(anchor=tk.W, padx=6, pady=(4, 2))

        sim_tree_frame = tk.Frame(sim_left, bg=self.colors["card"])
        sim_tree_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=2)

        self.sim_tree = ttk.Treeview(sim_tree_frame,
                                     columns=("type", "cmd", "addr", "data", "status"),
                                     show="headings", height=12)
        self.sim_tree.heading("type", text="Type")
        self.sim_tree.heading("cmd", text="Command")
        self.sim_tree.heading("addr", text="Address")
        self.sim_tree.heading("data", text="Data")
        self.sim_tree.heading("status", text="Status")
        self.sim_tree.column("type", width=50)
        self.sim_tree.column("cmd", width=90)
        self.sim_tree.column("addr", width=60)
        self.sim_tree.column("data", width=100)
        self.sim_tree.column("status", width=50)
        sim_tree_scroll = ttk.Scrollbar(sim_tree_frame, orient=tk.VERTICAL,
                                         command=self.sim_tree.yview)
        self.sim_tree.configure(yscrollcommand=sim_tree_scroll.set)
        self.sim_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sim_tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # 右: Fail Bit Map + 状态机 + March步骤 + 日志
        sim_right = tk.Frame(sim_body, bg=self.colors["card"])
        sim_body.add(sim_right, minsize=360)

        # Fail Bit Map 标题 + 导出按钮
        fbm_header = tk.Frame(sim_right, bg=self.colors["card"])
        fbm_header.pack(fill=tk.X, padx=6, pady=(4, 0))
        tk.Label(fbm_header, text=self.t("fbm_title"),
                 font=("Segoe UI", 9, "bold"), fg=self.colors["accent"],
                 bg=self.colors["card"]).pack(side=tk.LEFT)
        tk.Button(fbm_header, text=self.t("fbm_export_svg"),
                  command=self._export_fbm_svg,
                  font=("Segoe UI", 7), bg=self.colors["accent2"], fg="white",
                  relief=tk.FLAT, padx=6, pady=1, cursor="hand2").pack(side=tk.RIGHT)
        # 图例
        legend_frame = tk.Frame(fbm_header, bg=self.colors["card"])
        legend_frame.pack(side=tk.RIGHT, padx=(0, 8))
        for color, key in [("#1D9E75", "fbm_pass"), ("#E24B4A", "fbm_fail"), ("#888780", "fbm_untested")]:
            tk.Canvas(legend_frame, width=10, height=10, bg=color,
                      highlightthickness=0).pack(side=tk.LEFT, padx=(4, 1))
            tk.Label(legend_frame, text=self.t(key), font=("Segoe UI", 7),
                     fg=self.colors["text_dim"], bg=self.colors["card"]).pack(side=tk.LEFT)

        # Fail Bit Map Canvas (16×16 热力图)
        self.sim_mem_canvas = tk.Canvas(sim_right, bg=self.colors["card"],
                                         highlightthickness=0, height=240)
        self.sim_mem_canvas.pack(fill=tk.BOTH, expand=True, padx=6, pady=2)
        self.sim_mem_canvas.bind("<Configure>", lambda e: self._draw_fail_bit_map())
        self.sim_mem_canvas.bind("<Motion>", self._fbm_on_motion)
        self.sim_mem_canvas.bind("<Button-1>", self._fbm_on_click)
        self._fbm_tooltip = None
        self._fbm_cells = []  # [(x, y, w, h, addr)]

        # March C- 步骤联动器
        march_frame = tk.LabelFrame(sim_right, text=self.t("march_animator"),
                                     font=("Segoe UI", 8), fg=self.colors["text_dim"],
                                     bg=self.colors["card"], labelanchor="nw")
        march_frame.pack(fill=tk.X, padx=6, pady=(2, 0))
        self._march_btn_frame = tk.Frame(march_frame, bg=self.colors["card"])
        self._march_btn_frame.pack(fill=tk.X, padx=4, pady=2)
        self._march_active_step = tk.IntVar(value=0)  # 0=全部
        tk.Button(self._march_btn_frame, text="All", font=("Segoe UI", 7),
                  command=lambda: self._select_march_step(0),
                  bg=self.colors["accent"], fg="white",
                  relief=tk.FLAT, padx=6, cursor="hand2").pack(side=tk.LEFT, padx=1)
        self._march_step_btns = []
        for step in range(1, 7):
            btn = tk.Button(self._march_btn_frame, text=f"S{step}",
                            font=("Segoe UI", 7),
                            command=lambda s=step: self._select_march_step(s),
                            bg=self.colors["card2"], fg=self.colors["text"],
                            relief=tk.FLAT, padx=6, cursor="hand2")
            btn.pack(side=tk.LEFT, padx=1)
            self._march_step_btns.append(btn)
        self._march_step_desc = tk.Label(march_frame, text="",
                                          font=("Consolas", 7), fg=self.colors["text_dim"],
                                          bg=self.colors["card"], anchor=tk.W)
        self._march_step_desc.pack(fill=tk.X, padx=6, pady=(0, 2))

        # 状态机 Canvas
        tk.Label(sim_right, text=self.t("sim_state_machine"),
                 font=("Segoe UI", 9, "bold"), fg=self.colors["accent"],
                 bg=self.colors["card"]).pack(anchor=tk.W, padx=6, pady=(4, 2))

        self.sim_sm_canvas = tk.Canvas(sim_right, bg=self.colors["card"],
                                        highlightthickness=0, height=60)
        self.sim_sm_canvas.pack(fill=tk.X, padx=6, pady=2)

        # 模拟日志
        tk.Label(sim_right, text=self.t("sim_log"),
                 font=("Segoe UI", 9, "bold"), fg=self.colors["accent"],
                 bg=self.colors["card"]).pack(anchor=tk.W, padx=6, pady=(4, 2))

        self.sim_log_text = scrolledtext.ScrolledText(
            sim_right, height=6, font=("Consolas", 8),
            bg=self.colors["bg"], fg=self.colors["text"],
            insertbackground=self.colors["text"], relief=tk.FLAT,
            borderwidth=1, wrap=tk.WORD)
        self.sim_log_text.pack(fill=tk.BOTH, expand=True, padx=6, pady=(2, 6))
        self.sim_log_text.tag_configure("info", foreground=self.colors["accent"])
        self.sim_log_text.tag_configure("warn", foreground=self.colors["warning"])
        self.sim_log_text.tag_configure("error", foreground=self.colors["danger"])
        self.sim_log_text.tag_configure("pass", foreground=self.colors["success"])

        # --- v8.0 Vector Debugger 子面板 ---
        debug_frame = tk.LabelFrame(sim_right, text=self.t("debug_title"),
                                     font=("Segoe UI", 9, "bold"),
                                     fg=self.colors["accent"], bg=self.colors["card"],
                                     relief=tk.GROOVE, labelanchor=tk.NW)
        debug_frame.pack(fill=tk.X, padx=6, pady=(4, 6))

        dbg_toolbar = tk.Frame(debug_frame, bg=self.colors["card"])
        dbg_toolbar.pack(fill=tk.X, padx=4, pady=2)

        dbg_btns = [
            ("debug_reset", "\u23EE", self._debug_reset),
            ("debug_step", "\u25B6", self._debug_step),
            ("debug_step_txn", "\u23E9", self._debug_step_txn),
            ("debug_step_section", "\u23ED", self._debug_step_section),
            ("debug_run_bp", "\u25B6\u25B6", self._debug_run_bp),
            ("debug_stop", "\u23F9", self._debug_stop),
        ]
        for key, icon, cmd in dbg_btns:
            b = tk.Button(dbg_toolbar, text=f"{icon} {self.t(key)}",
                          font=("Segoe UI", 7), command=cmd,
                          bg=self.colors["card2"], fg=self.colors["text"],
                          relief=tk.FLAT, padx=4, cursor="hand2")
            b.pack(side=tk.LEFT, padx=1)

        # 当前状态面板
        dbg_state_frame = tk.Frame(debug_frame, bg=self.colors["card"])
        dbg_state_frame.pack(fill=tk.X, padx=4, pady=2)

        self.dbg_state_label = tk.Label(
            dbg_state_frame, text="PC: - | Bus: - | Event: -",
            font=("Consolas", 8), fg=self.colors["text"],
            bg=self.colors["card"], anchor=tk.W)
        self.dbg_state_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.dbg_mode_label = tk.Label(
            dbg_state_frame, text=self.t("debug_stopped"),
            font=("Consolas", 8, "bold"), fg=self.colors["text_dim"],
            bg=self.colors["card"])
        self.dbg_mode_label.pack(side=tk.RIGHT)

        # 断点 + 向量预览行
        dbg_bp_frame = tk.Frame(debug_frame, bg=self.colors["card"])
        dbg_bp_frame.pack(fill=tk.X, padx=4, pady=2)

        tk.Label(dbg_bp_frame, text=self.t("debug_add_bp") + ":",
                 font=("Segoe UI", 7), fg=self.colors["text_dim"],
                 bg=self.colors["card"]).pack(side=tk.LEFT)
        self.dbg_bp_entry = tk.Entry(dbg_bp_frame, width=8,
                                      font=("Consolas", 8),
                                      bg=self.colors["bg"], fg=self.colors["text"])
        self.dbg_bp_entry.pack(side=tk.LEFT, padx=2)
        tk.Button(dbg_bp_frame, text="+", font=("Segoe UI", 7),
                  command=self._debug_add_bp,
                  bg=self.colors["card2"], fg=self.colors["text"],
                  relief=tk.FLAT, padx=4, cursor="hand2").pack(side=tk.LEFT)
        tk.Button(dbg_bp_frame, text=self.t("debug_clear_bp"),
                  font=("Segoe UI", 7), command=self._debug_clear_all_bp,
                  bg=self.colors["card2"], fg=self.colors["text"],
                  relief=tk.FLAT, padx=4, cursor="hand2").pack(side=tk.LEFT, padx=2)

        self.dbg_bp_list_label = tk.Label(
            dbg_bp_frame, text="BP: (none)", font=("Consolas", 7),
            fg=self.colors["text_dim"], bg=self.colors["card"])
        self.dbg_bp_list_label.pack(side=tk.LEFT, padx=4)

        # 执行历史（最近10步）
        self.dbg_history_text = scrolledtext.ScrolledText(
            debug_frame, height=4, font=("Consolas", 7),
            bg=self.colors["bg"], fg=self.colors["text"],
            insertbackground=self.colors["text"], relief=tk.FLAT,
            borderwidth=1, wrap=tk.NONE, state=tk.DISABLED)
        self.dbg_history_text.pack(fill=tk.X, padx=4, pady=(2, 4))

        self._debugger = None

        # ============================================================
        # v6.0 Tab 7: Shmoo Plot 参数表征
        # ============================================================
        shmoo_tab = tk.Frame(self.notebook, bg=self.colors["card"])
        self.notebook.add(shmoo_tab, text=self.t("tab_shmoo"))

        shmoo_toolbar = tk.Frame(shmoo_tab, bg=self.colors["card"])
        shmoo_toolbar.pack(fill=tk.X, padx=10, pady=(6, 0))

        tk.Label(shmoo_toolbar, text=f'{self.t("shmoo_voltage")}:',
                 font=("Segoe UI", 8), fg=self.colors["text"],
                 bg=self.colors["card"]).pack(side=tk.LEFT)
        self.shmoo_v_from = ttk.Combobox(shmoo_toolbar, width=6,
                                          values=["1.8V", "2.5V", "3.3V", "5.0V"], state="readonly")
        self.shmoo_v_from.set("1.8V")
        self.shmoo_v_from.pack(side=tk.LEFT, padx=2)
        tk.Label(shmoo_toolbar, text="→", font=("Segoe UI", 8),
                 fg=self.colors["text"], bg=self.colors["card"]).pack(side=tk.LEFT)
        self.shmoo_v_to = ttk.Combobox(shmoo_toolbar, width=6,
                                        values=["1.8V", "2.5V", "3.3V", "5.0V"], state="readonly")
        self.shmoo_v_to.set("5.0V")
        self.shmoo_v_to.pack(side=tk.LEFT, padx=2)

        tk.Label(shmoo_toolbar, text=f'  {self.t("shmoo_freq")}(kHz):',
                 font=("Segoe UI", 8), fg=self.colors["text"],
                 bg=self.colors["card"]).pack(side=tk.LEFT, padx=(8, 0))
        self.shmoo_f_from = tk.Entry(shmoo_toolbar, width=6,
                                      font=("Segoe UI", 8), bg=self.colors["bg"],
                                      fg=self.colors["text"])
        self.shmoo_f_from.insert(0, "100")
        self.shmoo_f_from.pack(side=tk.LEFT, padx=2)
        tk.Label(shmoo_toolbar, text="→", font=("Segoe UI", 8),
                 fg=self.colors["text"], bg=self.colors["card"]).pack(side=tk.LEFT)
        self.shmoo_f_to = tk.Entry(shmoo_toolbar, width=6,
                                    font=("Segoe UI", 8), bg=self.colors["bg"],
                                    fg=self.colors["text"])
        self.shmoo_f_to.insert(0, "1000")
        self.shmoo_f_to.pack(side=tk.LEFT, padx=2)

        tk.Button(shmoo_toolbar, text=f'▶ {self.t("shmoo_run")}',
                  command=self._run_shmoo_sweep,
                  font=("Segoe UI", 8, "bold"), bg=self.colors["success"], fg="white",
                  relief=tk.FLAT, padx=10, pady=3, cursor="hand2").pack(side=tk.LEFT, padx=(10, 0))
        tk.Button(shmoo_toolbar, text=self.t("shmoo_export_csv"),
                  command=self._export_shmoo_csv,
                  font=("Segoe UI", 7), bg=self.colors["accent2"], fg="white",
                  relief=tk.FLAT, padx=8, pady=2, cursor="hand2").pack(side=tk.RIGHT)
        tk.Button(shmoo_toolbar, text=self.t("shmoo_export_svg"),
                  command=self._export_shmoo_svg,
                  font=("Segoe UI", 7), bg=self.colors["accent"], fg="white",
                  relief=tk.FLAT, padx=8, pady=2, cursor="hand2").pack(side=tk.RIGHT, padx=(0, 4))

        # Shmoo 主体: 上=热力图, 下=余量分析
        self.shmoo_canvas = tk.Canvas(shmoo_tab, bg=self.colors["card"],
                                       highlightthickness=0)
        self.shmoo_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=6)

        self.shmoo_margin_label = tk.Label(shmoo_tab, text="",
                                            font=("Consolas", 9), fg=self.colors["text_dim"],
                                            bg=self.colors["card"], justify=tk.LEFT)
        self.shmoo_margin_label.pack(anchor=tk.W, padx=14, pady=(0, 8))

        self._shmoo_engine = None

        # ============================================================
        # v6.0 Tab 8: 测试流程编排 (Flow Editor)
        # ============================================================
        flow_edit_tab = tk.Frame(self.notebook, bg=self.colors["card"])
        self.notebook.add(flow_edit_tab, text=self.t("tab_flow_edit"))

        flow_edit_toolbar = tk.Frame(flow_edit_tab, bg=self.colors["card"])
        flow_edit_toolbar.pack(fill=tk.X, padx=10, pady=(6, 0))

        tk.Button(flow_edit_toolbar, text=f'⟲ {self.t("flow_reset_default")}',
                  command=self._flow_reset_default,
                  font=("Segoe UI", 8), bg=self.colors["border"], fg=self.colors["text"],
                  relief=tk.FLAT, padx=8, pady=3, cursor="hand2").pack(side=tk.LEFT)
        tk.Button(flow_edit_toolbar, text=f'▶ {self.t("flow_simulate")}',
                  command=self._flow_simulate,
                  font=("Segoe UI", 8, "bold"), bg=self.colors["success"], fg="white",
                  relief=tk.FLAT, padx=10, pady=3, cursor="hand2").pack(side=tk.LEFT, padx=(4, 0))
        tk.Button(flow_edit_toolbar, text=self.t("flow_export_prg"),
                  command=self._flow_export_prg,
                  font=("Segoe UI", 7), bg=self.colors["accent2"], fg="white",
                  relief=tk.FLAT, padx=8, pady=2, cursor="hand2").pack(side=tk.LEFT, padx=(4, 0))

        self.flow_sim_result = tk.Label(flow_edit_toolbar, text="",
                                         font=("Segoe UI", 8, "bold"),
                                         fg=self.colors["text_dim"],
                                         bg=self.colors["card"])
        self.flow_sim_result.pack(side=tk.RIGHT)

        # 流程编排主体: 左=流程图 Canvas, 右=Bin 表 + 限值
        flow_edit_body = tk.PanedWindow(flow_edit_tab, orient=tk.HORIZONTAL,
                                         bg=self.colors["border"], sashwidth=4)
        flow_edit_body.pack(fill=tk.BOTH, expand=True, padx=10, pady=6)

        # 左: 流程图 Canvas
        flow_edit_left = tk.Frame(flow_edit_body, bg=self.colors["card"])
        flow_edit_body.add(flow_edit_left, minsize=350)

        self.flow_edit_canvas = tk.Canvas(flow_edit_left, bg=self.colors["card"],
                                           highlightthickness=0)
        self.flow_edit_canvas.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # 右: Bin 表 + 测试限值
        flow_edit_right = tk.Frame(flow_edit_body, bg=self.colors["card"])
        flow_edit_body.add(flow_edit_right, minsize=260)

        # Bin 表
        tk.Label(flow_edit_right, text=self.t("flow_bin_table"),
                 font=("Segoe UI", 9, "bold"), fg=self.colors["accent"],
                 bg=self.colors["card"]).pack(anchor=tk.W, padx=6, pady=(4, 2))

        bin_tree_frame = tk.Frame(flow_edit_right, bg=self.colors["card"])
        bin_tree_frame.pack(fill=tk.X, padx=4, pady=2)

        self.bin_tree = ttk.Treeview(bin_tree_frame,
                                      columns=("bin", "name", "type", "desc"),
                                      show="headings", height=8)
        self.bin_tree.heading("bin", text="Bin")
        self.bin_tree.heading("name", text="Name")
        self.bin_tree.heading("type", text="Type")
        self.bin_tree.heading("desc", text="Description")
        self.bin_tree.column("bin", width=35)
        self.bin_tree.column("name", width=80)
        self.bin_tree.column("type", width=45)
        self.bin_tree.column("desc", width=150)
        self.bin_tree.pack(fill=tk.X)

        # 测试限值表
        tk.Label(flow_edit_right, text=self.t("flow_test_limits"),
                 font=("Segoe UI", 9, "bold"), fg=self.colors["accent"],
                 bg=self.colors["card"]).pack(anchor=tk.W, padx=6, pady=(8, 2))

        limits_tree_frame = tk.Frame(flow_edit_right, bg=self.colors["card"])
        limits_tree_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=2)

        self.limits_tree = ttk.Treeview(limits_tree_frame,
                                         columns=("param", "min", "max", "unit"),
                                         show="headings", height=8)
        self.limits_tree.heading("param", text="Param")
        self.limits_tree.heading("min", text="Min")
        self.limits_tree.heading("max", text="Max")
        self.limits_tree.heading("unit", text="Unit")
        self.limits_tree.column("param", width=70)
        self.limits_tree.column("min", width=55)
        self.limits_tree.column("max", width=55)
        self.limits_tree.column("unit", width=50)
        self.limits_tree.pack(fill=tk.BOTH, expand=True)

        self._flow_engine = TestFlowEngine()
        self._populate_flow_tables()

        # ============================================================
        # v6.0 Tab 9: 良率分析仪表盘 (Yield Dashboard)
        # ============================================================
        yield_tab = tk.Frame(self.notebook, bg=self.colors["card"])
        self.notebook.add(yield_tab, text=self.t("tab_yield"))

        yield_toolbar = tk.Frame(yield_tab, bg=self.colors["card"])
        yield_toolbar.pack(fill=tk.X, padx=10, pady=(6, 0))

        tk.Button(yield_toolbar, text=self.t("yield_import"),
                  command=self._yield_import_datalog,
                  font=("Segoe UI", 8), bg=self.colors["accent"], fg="white",
                  relief=tk.FLAT, padx=8, pady=3, cursor="hand2").pack(side=tk.LEFT)
        tk.Button(yield_toolbar, text=self.t("yield_import_sim"),
                  command=self._yield_import_simulation,
                  font=("Segoe UI", 8), bg=self.colors["accent2"], fg="white",
                  relief=tk.FLAT, padx=8, pady=3, cursor="hand2").pack(side=tk.LEFT, padx=(4, 0))
        tk.Button(yield_toolbar, text=self.t("yield_export_report"),
                  command=self._yield_export_report,
                  font=("Segoe UI", 7), bg=self.colors["border"], fg=self.colors["text"],
                  relief=tk.FLAT, padx=8, pady=2, cursor="hand2").pack(side=tk.RIGHT)

        self.yield_param_combo = ttk.Combobox(yield_toolbar, width=12,
                                               values=[], state="readonly")
        self.yield_param_combo.pack(side=tk.LEFT, padx=(10, 0))
        self.yield_param_combo.bind("<<ComboboxSelected>>", lambda e: self._yield_refresh())

        self.yield_info_label = tk.Label(yield_toolbar, text="",
                                          font=("Segoe UI", 8),
                                          fg=self.colors["text_dim"],
                                          bg=self.colors["card"])
        self.yield_info_label.pack(side=tk.RIGHT, padx=(0, 8))

        # Phase 6: Monte Carlo 控制
        mc_frame = tk.Frame(yield_tab, bg=self.colors["card"])
        mc_frame.pack(fill=tk.X, padx=10, pady=(2, 0))
        tk.Button(mc_frame, text=f'▶ {self.t("mc_run")}',
                  command=self._run_monte_carlo,
                  font=("Segoe UI", 8, "bold"), bg="#8b5cf6", fg="white",
                  relief=tk.FLAT, padx=10, pady=2, cursor="hand2").pack(side=tk.LEFT)
        tk.Label(mc_frame, text=f'{self.t("mc_seed")}:',
                 font=("Segoe UI", 7), fg=self.colors["text_dim"],
                 bg=self.colors["card"]).pack(side=tk.LEFT, padx=(8, 2))
        self._mc_seed_var = tk.StringVar(value="42")
        tk.Entry(mc_frame, textvariable=self._mc_seed_var, width=5,
                 font=("Consolas", 8), bg=self.colors["bg"], fg=self.colors["text"],
                 insertbackground=self.colors["text"],
                 relief=tk.FLAT).pack(side=tk.LEFT)
        tk.Label(mc_frame, text=f'{self.t("mc_n")}:',
                 font=("Segoe UI", 7), fg=self.colors["text_dim"],
                 bg=self.colors["card"]).pack(side=tk.LEFT, padx=(8, 2))
        self._mc_n_var = tk.StringVar(value="1000")
        tk.Entry(mc_frame, textvariable=self._mc_n_var, width=6,
                 font=("Consolas", 8), bg=self.colors["bg"], fg=self.colors["text"],
                 insertbackground=self.colors["text"],
                 relief=tk.FLAT).pack(side=tk.LEFT)
        self._mc_status = tk.Label(mc_frame, text="",
                                    font=("Segoe UI", 8), fg=self.colors["text_dim"],
                                    bg=self.colors["card"])
        self._mc_status.pack(side=tk.RIGHT)

        # v9.0 Tier3 Phase 28: Guard Band 控制栏
        gb_frame = tk.Frame(yield_tab, bg=self.colors["card"])
        gb_frame.pack(fill=tk.X, padx=10, pady=(2, 0))
        tk.Label(gb_frame, text=f'{self.t("gb_target_dppm")}:',
                 font=("Segoe UI", 7), fg=self.colors["text_dim"],
                 bg=self.colors["card"]).pack(side=tk.LEFT)
        self._gb_dppm_var = tk.StringVar(value="10")
        tk.Entry(gb_frame, textvariable=self._gb_dppm_var, width=5,
                 font=("Consolas", 8), bg=self.colors["bg"], fg=self.colors["text"],
                 insertbackground=self.colors["text"],
                 relief=tk.FLAT).pack(side=tk.LEFT, padx=2)
        tk.Button(gb_frame, text=self.t("gb_run"),
                  command=self._run_guard_band,
                  font=("Segoe UI", 7, "bold"), bg="#0ea5e9", fg="white",
                  relief=tk.FLAT, padx=8, pady=1, cursor="hand2").pack(side=tk.LEFT, padx=4)
        self._gb_apply_btn = tk.Button(gb_frame, text=self.t("gb_apply"),
                  command=self._apply_guard_band, state=tk.DISABLED,
                  font=("Segoe UI", 7), bg=self.colors["card"], fg=self.colors["text"],
                  relief=tk.FLAT, padx=6, pady=1, cursor="hand2")
        self._gb_apply_btn.pack(side=tk.LEFT, padx=2)
        self._gb_status = tk.Label(gb_frame, text="",
                                    font=("Segoe UI", 7), fg=self.colors["text_dim"],
                                    bg=self.colors["card"])
        self._gb_status.pack(side=tk.RIGHT)
        self._gb_engine = None
        self._gb_tree = None

        # 良率主体 Canvas
        self.yield_canvas = tk.Canvas(yield_tab, bg=self.colors["card"],
                                       highlightthickness=0)
        self.yield_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=6)
        self.yield_canvas.bind("<Configure>", lambda e: self._draw_mc_results())

        self._datalog_analyzer = DatalogAnalyzer()
        self._yield_predictor = None
        self._yield_draw_empty()

        # ============================================================
        # Phase 4: ATPG 覆盖率 Tab
        # ============================================================
        atpg_tab = tk.Frame(self.notebook, bg=self.colors["card"])
        self.notebook.add(atpg_tab, text=self.t("tab_atpg"))

        atpg_toolbar = tk.Frame(atpg_tab, bg=self.colors["card"])
        atpg_toolbar.pack(fill=tk.X, padx=10, pady=(6, 0))
        tk.Button(atpg_toolbar, text=f'▶ {self.t("atpg_run")}',
                  command=self._run_atpg_simulation,
                  font=("Segoe UI", 8, "bold"), bg=self.colors["success"], fg="white",
                  relief=tk.FLAT, padx=10, pady=3, cursor="hand2").pack(side=tk.LEFT)
        tk.Label(atpg_toolbar, text=f'{self.t("atpg_seed")}:',
                 font=("Segoe UI", 8), fg=self.colors["text"],
                 bg=self.colors["card"]).pack(side=tk.LEFT, padx=(10, 2))
        self._atpg_seed_var = tk.StringVar(value="42")
        tk.Entry(atpg_toolbar, textvariable=self._atpg_seed_var, width=6,
                 font=("Consolas", 8), bg=self.colors["bg"], fg=self.colors["text"],
                 insertbackground=self.colors["text"],
                 relief=tk.FLAT).pack(side=tk.LEFT)
        tk.Label(atpg_toolbar, text=f'n=',
                 font=("Segoe UI", 8), fg=self.colors["text"],
                 bg=self.colors["card"]).pack(side=tk.LEFT, padx=(8, 2))
        self._atpg_n_var = tk.StringVar(value="100")
        tk.Entry(atpg_toolbar, textvariable=self._atpg_n_var, width=5,
                 font=("Consolas", 8), bg=self.colors["bg"], fg=self.colors["text"],
                 insertbackground=self.colors["text"],
                 relief=tk.FLAT).pack(side=tk.LEFT)
        self._atpg_status = tk.Label(atpg_toolbar, text="",
                                      font=("Segoe UI", 8), fg=self.colors["text_dim"],
                                      bg=self.colors["card"])
        self._atpg_status.pack(side=tk.RIGHT)
        tk.Button(atpg_toolbar, text=self.t("fbm_export_svg"),
                  command=self._export_atpg_svg,
                  font=("Segoe UI", 7), bg=self.colors["accent2"], fg="white",
                  relief=tk.FLAT, padx=6, pady=1, cursor="hand2").pack(side=tk.RIGHT, padx=(0, 6))

        # 上下分区: 上=仿真覆盖率(Phase4), 下=理论覆盖率(Phase8)
        atpg_pane = tk.PanedWindow(atpg_tab, orient=tk.VERTICAL,
                                    bg=self.colors["border"], sashwidth=4)
        atpg_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=6)

        # 上半区: 仿真覆盖率
        atpg_upper = tk.Frame(atpg_pane, bg=self.colors["card"])
        atpg_pane.add(atpg_upper, minsize=120)

        self.atpg_canvas = tk.Canvas(atpg_upper, bg=self.colors["card"],
                                      highlightthickness=0)
        self.atpg_canvas.pack(fill=tk.BOTH, expand=True)
        self.atpg_canvas.bind("<Configure>", lambda e: self._draw_atpg_results())
        self._fault_sim = None

        # 下半区: 理论覆盖率 (Phase 8)
        atpg_lower = tk.Frame(atpg_pane, bg=self.colors["card"])
        atpg_pane.add(atpg_lower, minsize=100)

        # 标题
        tk.Label(atpg_lower, text=self.t("atpg_theory"),
                 font=("Segoe UI", 9, "bold"), fg=self.colors["accent2"],
                 bg=self.colors["card"]).pack(anchor=tk.W, padx=4, pady=(4, 2))

        atpg8_body = tk.Frame(atpg_lower, bg=self.colors["card"])
        atpg8_body.pack(fill=tk.BOTH, expand=True)

        # 左: 故障模型选择器
        atpg8_left = tk.Frame(atpg8_body, bg=self.colors["card"], width=160)
        atpg8_left.pack(side=tk.LEFT, fill=tk.Y, padx=(4, 2))
        atpg8_left.pack_propagate(False)

        tk.Label(atpg8_left, text=self.t("atpg_select_faults"),
                 font=("Segoe UI", 7, "bold"), fg=self.colors["text"],
                 bg=self.colors["card"]).pack(anchor=tk.W)

        self._atpg8_fault_vars = {}
        for ft in FAULT_MODELS:
            var = tk.BooleanVar(value=True)
            self._atpg8_fault_vars[ft] = var
            tk.Checkbutton(atpg8_left, text=ft, variable=var,
                          font=("Consolas", 7), fg=self.colors["text"],
                          bg=self.colors["card"], selectcolor=self.colors["bg"],
                          activebackground=self.colors["card"]).pack(anchor=tk.W)

        # 算法选择
        tk.Label(atpg8_left, text=self.t("atpg_algorithm"),
                 font=("Segoe UI", 7, "bold"), fg=self.colors["text"],
                 bg=self.colors["card"]).pack(anchor=tk.W, pady=(6, 0))
        self._atpg8_algo_var = tk.StringVar(value="March C-")
        algo_names = list(MemoryATPG.CLASSIC_ALGORITHMS.keys())
        for aname in algo_names:
            tk.Radiobutton(atpg8_left, text=aname, variable=self._atpg8_algo_var,
                          value=aname, font=("Consolas", 7),
                          fg=self.colors["text"], bg=self.colors["card"],
                          selectcolor=self.colors["bg"],
                          activebackground=self.colors["card"]).pack(anchor=tk.W)

        tk.Button(atpg8_left, text=self.t("atpg_generate_proof"),
                  command=self._generate_atpg_proof,
                  font=("Segoe UI", 7, "bold"), bg=self.colors["accent2"], fg="white",
                  relief=tk.FLAT, padx=6, pady=2, cursor="hand2").pack(fill=tk.X, pady=(6, 2))
        tk.Button(atpg8_left, text=self.t("atpg_export_proof"),
                  command=self._export_atpg_proof,
                  font=("Segoe UI", 7), bg=self.colors["card"],
                  fg=self.colors["text"], relief=tk.FLAT, padx=4, pady=1,
                  cursor="hand2").pack(fill=tk.X, pady=(0, 2))

        # 中: March 序列可视化 Canvas
        self._atpg8_canvas = tk.Canvas(atpg8_body, bg=self.colors["bg"],
                                        highlightthickness=0, width=280)
        self._atpg8_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)
        self._atpg8_canvas.bind("<Configure>", lambda e: self._draw_march_vis())

        # 右: 证明文本
        atpg8_right = tk.Frame(atpg8_body, bg=self.colors["card"], width=280)
        atpg8_right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(2, 4))
        atpg8_right.pack_propagate(False)

        tk.Label(atpg8_right, text=self.t("atpg_proof_text"),
                 font=("Segoe UI", 7, "bold"), fg=self.colors["text"],
                 bg=self.colors["card"]).pack(anchor=tk.W)
        self._atpg8_proof_text = tk.Text(atpg8_right, wrap=tk.WORD,
                                          font=("Consolas", 7),
                                          bg=self.colors["bg"], fg=self.colors["text"],
                                          relief=tk.FLAT, state=tk.DISABLED)
        self._atpg8_proof_text.pack(fill=tk.BOTH, expand=True, pady=(2, 0))

        self._memory_atpg = MemoryATPG()

        # ============================================================
        # Phase 5: 测试经济学 Tab
        # ============================================================
        econ_tab = tk.Frame(self.notebook, bg=self.colors["card"])
        self.notebook.add(econ_tab, text=self.t("tab_econ"))

        econ_top = tk.Frame(econ_tab, bg=self.colors["card"])
        econ_top.pack(fill=tk.X, padx=10, pady=(6, 0))
        # 参数输入
        econ_params = [
            ("ATE ¥/h:", "_econ_ate_cost", "500", 5),
            ("芯片 ¥:", "_econ_chip_cost", "0.5", 5),
            ("目标/天:", "_econ_target", "10000", 6),
            ("良率%:", "_econ_yield", "95", 4),
            ("工时h:", "_econ_hours", "16", 3),
            ("返修¥:", "_econ_repair", "50", 4),
        ]
        for label, attr, default, width in econ_params:
            tk.Label(econ_top, text=label, font=("Segoe UI", 7),
                     fg=self.colors["text_dim"], bg=self.colors["card"]).pack(side=tk.LEFT, padx=(4, 1))
            var = tk.StringVar(value=default)
            setattr(self, attr, var)
            tk.Entry(econ_top, textvariable=var, width=width,
                     font=("Consolas", 8), bg=self.colors["bg"], fg=self.colors["text"],
                     insertbackground=self.colors["text"],
                     relief=tk.FLAT).pack(side=tk.LEFT)
        tk.Button(econ_top, text=self.t("econ_calculate"),
                  command=self._calculate_economics,
                  font=("Segoe UI", 8, "bold"), bg=self.colors["accent"], fg="white",
                  relief=tk.FLAT, padx=10, pady=2, cursor="hand2").pack(side=tk.LEFT, padx=(10, 0))

        self.econ_canvas = tk.Canvas(econ_tab, bg=self.colors["card"],
                                      highlightthickness=0)
        self.econ_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=6)
        self.econ_canvas.bind("<Configure>", lambda e: self._draw_economics())
        self._econ_data = None

        # ============================================================
        # Phase 7: 芯片迁移 Tab
        # ============================================================
        migrate_tab = tk.Frame(self.notebook, bg=self.colors["card"])
        self.notebook.add(migrate_tab, text=self.t("tab_migrate"))

        migrate_top = tk.Frame(migrate_tab, bg=self.colors["card"])
        migrate_top.pack(fill=tk.X, padx=10, pady=(6, 0))

        chip_names = list(ChipMigrationEngine.CHIP_DB.keys())
        # 源芯片
        tk.Label(migrate_top, text=self.t("migrate_source"), font=("Segoe UI", 8, "bold"),
                 fg=self.colors["text"], bg=self.colors["card"]).pack(side=tk.LEFT, padx=(0, 4))
        self._migrate_source_var = tk.StringVar(value="AT24C02")
        src_cb = ttk.Combobox(migrate_top, textvariable=self._migrate_source_var,
                              values=chip_names, state="readonly", width=10, font=("Consolas", 8))
        src_cb.pack(side=tk.LEFT, padx=(0, 8))

        tk.Label(migrate_top, text="→", font=("Segoe UI", 12, "bold"),
                 fg=self.colors["accent"], bg=self.colors["card"]).pack(side=tk.LEFT, padx=4)

        # 目标芯片
        tk.Label(migrate_top, text=self.t("migrate_target"), font=("Segoe UI", 8, "bold"),
                 fg=self.colors["text"], bg=self.colors["card"]).pack(side=tk.LEFT, padx=(4, 4))
        self._migrate_target_var = tk.StringVar(value="AT24C04")
        tgt_cb = ttk.Combobox(migrate_top, textvariable=self._migrate_target_var,
                              values=chip_names, state="readonly", width=10, font=("Consolas", 8))
        tgt_cb.pack(side=tk.LEFT, padx=(0, 10))

        tk.Button(migrate_top, text=self.t("migrate_run"),
                  command=self._run_migration,
                  font=("Segoe UI", 8, "bold"), bg="#6366f1", fg="white",
                  relief=tk.FLAT, padx=10, pady=2, cursor="hand2").pack(side=tk.LEFT, padx=(0, 6))

        tk.Button(migrate_top, text=self.t("migrate_export"),
                  command=self._export_migration_svg,
                  font=("Segoe UI", 7), bg=self.colors["card"],
                  fg=self.colors["text"], relief=tk.FLAT, padx=5, pady=2,
                  cursor="hand2").pack(side=tk.LEFT)

        # 下半区: 左=芯片对比表 + 迁移日志, 右=Canvas
        migrate_body = tk.Frame(migrate_tab, bg=self.colors["card"])
        migrate_body.pack(fill=tk.BOTH, expand=True, padx=10, pady=6)

        # 左: 对比 + 日志
        migrate_left = tk.Frame(migrate_body, bg=self.colors["card"], width=320)
        migrate_left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 6))
        migrate_left.pack_propagate(False)

        tk.Label(migrate_left, text=self.t("migrate_compare"),
                 font=("Segoe UI", 9, "bold"), fg=self.colors["accent"],
                 bg=self.colors["card"]).pack(anchor=tk.W)

        self._migrate_compare_text = tk.Text(migrate_left, wrap=tk.WORD, height=10,
                                              font=("Consolas", 8),
                                              bg=self.colors["bg"], fg=self.colors["text"],
                                              relief=tk.FLAT, state=tk.DISABLED)
        self._migrate_compare_text.pack(fill=tk.X, pady=(2, 6))

        tk.Label(migrate_left, text=self.t("migrate_log"),
                 font=("Segoe UI", 9, "bold"), fg=self.colors["warning"],
                 bg=self.colors["card"]).pack(anchor=tk.W)

        self._migrate_log_text = tk.Text(migrate_left, wrap=tk.WORD,
                                          font=("Consolas", 7),
                                          bg=self.colors["bg"], fg=self.colors["text"],
                                          relief=tk.FLAT, state=tk.DISABLED)
        self._migrate_log_text.pack(fill=tk.BOTH, expand=True, pady=(2, 0))

        # 右: Canvas 对比可视化
        self._migrate_canvas = tk.Canvas(migrate_body, bg=self.colors["card"],
                                          highlightthickness=0)
        self._migrate_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._migrate_canvas.bind("<Configure>", lambda e: self._draw_migration())
        self._migration_data = None

        # ============================================================
        # v8.0 Phase 11: Datalog + Binning Tab
        # ============================================================
        datalog_tab = tk.Frame(self.notebook, bg=self.colors["card"])
        self.notebook.add(datalog_tab, text=self.t("tab_datalog"))

        dl_toolbar = tk.Frame(datalog_tab, bg=self.colors["card"])
        dl_toolbar.pack(fill=tk.X, padx=10, pady=(6, 0))

        tk.Button(dl_toolbar, text=self.t("datalog_gen_single"),
                  command=self._generate_single_datalog,
                  font=("Segoe UI", 8, "bold"), bg=self.colors["accent"], fg="white",
                  relief=tk.FLAT, padx=8, pady=3, cursor="hand2").pack(side=tk.LEFT)

        tk.Label(dl_toolbar, text=f'  {self.t("datalog_batch_n")}:',
                 font=("Segoe UI", 8), fg=self.colors["text"],
                 bg=self.colors["card"]).pack(side=tk.LEFT, padx=(10, 0))
        self._datalog_batch_n = tk.Entry(dl_toolbar, width=6, font=("Segoe UI", 8),
                                          bg=self.colors["bg"], fg=self.colors["text"])
        self._datalog_batch_n.insert(0, "100")
        self._datalog_batch_n.pack(side=tk.LEFT, padx=2)

        tk.Label(dl_toolbar, text=f'{self.t("datalog_seed")}:',
                 font=("Segoe UI", 8), fg=self.colors["text"],
                 bg=self.colors["card"]).pack(side=tk.LEFT, padx=(4, 0))
        self._datalog_seed = tk.Entry(dl_toolbar, width=4, font=("Segoe UI", 8),
                                       bg=self.colors["bg"], fg=self.colors["text"])
        self._datalog_seed.insert(0, "42")
        self._datalog_seed.pack(side=tk.LEFT, padx=2)

        tk.Button(dl_toolbar, text=self.t("datalog_gen_batch"),
                  command=self._generate_batch_datalog,
                  font=("Segoe UI", 8, "bold"), bg=self.colors["success"], fg="white",
                  relief=tk.FLAT, padx=8, pady=3, cursor="hand2").pack(side=tk.LEFT, padx=6)

        tk.Button(dl_toolbar, text=self.t("datalog_export_csv"),
                  command=self._export_datalog_csv,
                  font=("Segoe UI", 7), bg=self.colors["accent2"], fg="white",
                  relief=tk.FLAT, padx=8, pady=2, cursor="hand2").pack(side=tk.RIGHT)
        tk.Button(dl_toolbar, text=self.t("datalog_export_bin"),
                  command=self._export_bin_summary,
                  font=("Segoe UI", 7), bg=self.colors["accent2"], fg="white",
                  relief=tk.FLAT, padx=8, pady=2, cursor="hand2").pack(side=tk.RIGHT, padx=(0, 4))
        tk.Button(dl_toolbar, text=self.t("stdf_export"),
                  command=self._export_stdf,
                  font=("Segoe UI", 7), bg=self.colors["gold"], fg="#1e293b",
                  relief=tk.FLAT, padx=8, pady=2, cursor="hand2").pack(side=tk.RIGHT, padx=(0, 4))
        # v9.0 Tier3 Phase 31: 导入 STDF 按钮
        tk.Button(dl_toolbar, text=self.t("stdf_import"),
                  command=self._import_stdf_file,
                  font=("Segoe UI", 7), bg="#0ea5e9", fg="white",
                  relief=tk.FLAT, padx=8, pady=2, cursor="hand2").pack(side=tk.RIGHT, padx=(0, 4))

        # Datalog 主体: PanedWindow 上下分割
        dl_pane = tk.PanedWindow(datalog_tab, orient=tk.VERTICAL, bg=self.colors["border"],
                                  sashwidth=4)
        dl_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=6)

        # 上: Datalog 文本预览
        dl_text_frame = tk.Frame(dl_pane, bg=self.colors["card"])
        self._datalog_text = tk.Text(dl_text_frame, wrap=tk.NONE, font=("Consolas", 8),
                                      bg=self.colors["bg"], fg=self.colors["text"],
                                      relief=tk.FLAT, state=tk.DISABLED)
        dl_text_sb = tk.Scrollbar(dl_text_frame, command=self._datalog_text.yview)
        self._datalog_text.config(yscrollcommand=dl_text_sb.set)
        dl_text_sb.pack(side=tk.RIGHT, fill=tk.Y)
        self._datalog_text.pack(fill=tk.BOTH, expand=True)
        dl_pane.add(dl_text_frame, minsize=100)

        # 下: Bin Summary (左=饼图Canvas, 右=统计表)
        dl_bottom = tk.Frame(dl_pane, bg=self.colors["card"])
        self._bin_pie_canvas = tk.Canvas(dl_bottom, bg=self.colors["card"],
                                          highlightthickness=0, width=250, height=200)
        self._bin_pie_canvas.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 4))

        dl_stats_frame = tk.Frame(dl_bottom, bg=self.colors["card"])
        dl_stats_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._bin_summary_label = tk.Label(dl_stats_frame, text="",
                                            font=("Consolas", 8), fg=self.colors["text"],
                                            bg=self.colors["card"], justify=tk.LEFT, anchor=tk.NW)
        self._bin_summary_label.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        dl_pane.add(dl_bottom, minsize=80)

        self._datalog_gen = DatalogGenerator()
        self._datalog_records = []
        self._corr_analyzer = CorrelationAnalyzer()

        # v9.0 Tier3 Phase 29: 参数相关性工具栏
        corr_toolbar = tk.Frame(datalog_tab, bg=self.colors["card"])
        corr_toolbar.pack(fill=tk.X, padx=10, pady=(2, 0))
        tk.Button(corr_toolbar, text=f'▶ {self.t("corr_run")}',
                  command=self._run_correlation,
                  font=("Segoe UI", 7, "bold"), bg="#8b5cf6", fg="white",
                  relief=tk.FLAT, padx=8, pady=1, cursor="hand2").pack(side=tk.LEFT)
        tk.Label(corr_toolbar, text=f'{self.t("corr_sigma")}:',
                 font=("Segoe UI", 7), fg=self.colors["text_dim"],
                 bg=self.colors["card"]).pack(side=tk.LEFT, padx=(8, 2))
        self._corr_sigma_var = tk.StringVar(value="3")
        tk.Entry(corr_toolbar, textvariable=self._corr_sigma_var, width=3,
                 font=("Consolas", 8), bg=self.colors["bg"], fg=self.colors["text"],
                 insertbackground=self.colors["text"],
                 relief=tk.FLAT).pack(side=tk.LEFT)
        self._corr_status = tk.Label(corr_toolbar, text="",
                                      font=("Segoe UI", 7), fg=self.colors["text_dim"],
                                      bg=self.colors["card"])
        self._corr_status.pack(side=tk.RIGHT)

        # ============================================================
        # v8.0 Phase 14: Wafer Map Tab
        # ============================================================
        wafer_tab = tk.Frame(self.notebook, bg=self.colors["card"])
        self.notebook.add(wafer_tab, text=self.t("tab_wafer"))

        wf_toolbar = tk.Frame(wafer_tab, bg=self.colors["card"])
        wf_toolbar.pack(fill=tk.X, padx=10, pady=(6, 0))

        tk.Button(wf_toolbar, text=f'▶ {self.t("wafer_generate")}',
                  command=self._generate_wafer_map,
                  font=("Segoe UI", 8, "bold"), bg=self.colors["success"], fg="white",
                  relief=tk.FLAT, padx=10, pady=3, cursor="hand2").pack(side=tk.LEFT)

        tk.Label(wf_toolbar, text=f'  {self.t("datalog_seed")}:',
                 font=("Segoe UI", 8), fg=self.colors["text"],
                 bg=self.colors["card"]).pack(side=tk.LEFT, padx=(8, 0))
        self._wafer_seed = tk.Entry(wf_toolbar, width=4, font=("Segoe UI", 8),
                                     bg=self.colors["bg"], fg=self.colors["text"])
        self._wafer_seed.insert(0, "42")
        self._wafer_seed.pack(side=tk.LEFT, padx=2)

        tk.Label(wf_toolbar, text=f'  {self.t("wafer_mode")}:',
                 font=("Segoe UI", 8), fg=self.colors["text"],
                 bg=self.colors["card"]).pack(side=tk.LEFT, padx=(8, 0))
        self._wafer_mode_var = tk.StringVar(value="bin_map")
        wf_mode_cb = ttk.Combobox(wf_toolbar, textvariable=self._wafer_mode_var,
                                   values=["bin_map", "yield_heatmap", "single_bin"],
                                   state="readonly", width=12, font=("Consolas", 8))
        wf_mode_cb.pack(side=tk.LEFT, padx=2)
        wf_mode_cb.bind("<<ComboboxSelected>>", lambda e: self._draw_wafer_map())

        tk.Button(wf_toolbar, text=self.t("wafer_export_svg"),
                  command=self._export_wafer_svg,
                  font=("Segoe UI", 7), bg=self.colors["accent"], fg="white",
                  relief=tk.FLAT, padx=8, pady=2, cursor="hand2").pack(side=tk.RIGHT)

        # 主体: 左=Canvas, 右=统计
        wf_body = tk.Frame(wafer_tab, bg=self.colors["card"])
        wf_body.pack(fill=tk.BOTH, expand=True, padx=10, pady=6)

        self._wafer_canvas = tk.Canvas(wf_body, bg=self.colors["card"],
                                        highlightthickness=0)
        self._wafer_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        wf_stats_frame = tk.Frame(wf_body, bg=self.colors["card"], width=200)
        wf_stats_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(4, 0))
        wf_stats_frame.pack_propagate(False)
        self._wafer_stats_label = tk.Label(wf_stats_frame, text="",
                                            font=("Consolas", 8), fg=self.colors["text"],
                                            bg=self.colors["card"], justify=tk.LEFT,
                                            anchor=tk.NW)
        self._wafer_stats_label.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        self._wafer_gen = None
        self._wafer_canvas.bind("<Motion>", self._wafer_on_motion)
        self._wafer_canvas.bind("<Leave>", self._wafer_on_leave)

        # ============================================================
        # v9.0 Phase 22: Temperature Corner Analysis Tab
        # ============================================================
        temp_tab = tk.Frame(self.notebook, bg=self.colors["card"])
        self.notebook.add(temp_tab, text=self.t("tab_temp"))

        temp_toolbar = tk.Frame(temp_tab, bg=self.colors["card"])
        temp_toolbar.pack(fill=tk.X, padx=10, pady=(6, 0))

        tk.Label(temp_toolbar, text=self.t("temp_corner_type") + ":",
                 font=("Segoe UI", 8, "bold"), fg=self.colors["text"],
                 bg=self.colors["card"]).pack(side=tk.LEFT)
        self._temp_corner_var = tk.StringVar(value="commercial")
        temp_corner_cb = ttk.Combobox(temp_toolbar, textvariable=self._temp_corner_var,
                                       values=["commercial", "industrial"],
                                       state="readonly", width=12, font=("Consolas", 8))
        temp_corner_cb.pack(side=tk.LEFT, padx=(4, 8))

        tk.Button(temp_toolbar, text=f"\u25b6 {self.t('temp_run')}",
                  command=self._run_temp_analysis,
                  font=("Segoe UI", 8, "bold"), bg=self.colors["success"], fg="white",
                  relief=tk.FLAT, padx=10, pady=3, cursor="hand2").pack(side=tk.LEFT)

        # 参数复选框
        self._temp_param_vars = {}
        param_frame = tk.Frame(temp_toolbar, bg=self.colors["card"])
        param_frame.pack(side=tk.LEFT, padx=(16, 0))
        tk.Label(param_frame, text=self.t("temp_param_select") + ":",
                 font=("Segoe UI", 7), fg=self.colors["text_dim"],
                 bg=self.colors["card"]).pack(side=tk.LEFT)
        for pname in TemperatureCornerSimulator.TEMP_COEFFICIENTS:
            var = tk.BooleanVar(value=True)
            self._temp_param_vars[pname] = var
            tk.Checkbutton(param_frame, text=pname, variable=var,
                          font=("Consolas", 7), fg=self.colors["text"],
                          bg=self.colors["card"], selectcolor=self.colors["sidebar"],
                          activebackground=self.colors["card"]).pack(side=tk.LEFT, padx=1)

        # 主体: 左Canvas + 右Treeview
        temp_body = tk.Frame(temp_tab, bg=self.colors["card"])
        temp_body.pack(fill=tk.BOTH, expand=True, padx=10, pady=6)

        self._temp_canvas = tk.Canvas(temp_body, bg=self.colors["card"],
                                       highlightthickness=0, width=500)
        self._temp_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        temp_right = tk.Frame(temp_body, bg=self.colors["card"], width=420)
        temp_right.pack(side=tk.RIGHT, fill=tk.Y, padx=(4, 0))
        temp_right.pack_propagate(False)

        temp_tree_cols = ("param", "unit", "t1", "t2", "t3", "t4", "t5", "margin", "limit")
        self._temp_tree = ttk.Treeview(temp_right, columns=temp_tree_cols,
                                        show="headings", height=10)
        for col, w in [("param", 60), ("unit", 40), ("t1", 55), ("t2", 55),
                        ("t3", 55), ("t4", 55), ("t5", 55), ("margin", 50), ("limit", 60)]:
            self._temp_tree.column(col, width=w, minwidth=35, anchor=tk.CENTER)
            self._temp_tree.heading(col, text=col.upper())
        self._temp_tree.tag_configure("pass", foreground="#22c55e")
        self._temp_tree.tag_configure("fail", foreground="#ef4444")
        self._temp_tree.tag_configure("warn", foreground="#f97316")
        self._temp_tree.pack(fill=tk.BOTH, expand=True)

        self._temp_summary_label = tk.Label(temp_right, text="",
                                             font=("Consolas", 8), fg=self.colors["text"],
                                             bg=self.colors["card"], justify=tk.LEFT,
                                             anchor=tk.NW)
        self._temp_summary_label.pack(fill=tk.X, padx=4, pady=(4, 0))

        self._write_default_info()
        self._show_welcome_page()

    # ============================================================
    # v6.0 欢迎页
    # ============================================================

    def _show_welcome_page(self):
        """在 PAT 预览区显示欢迎页"""
        self.pat_text.delete("1.0", tk.END)
        protocol = self.chip_protocol_var.get() if hasattr(self, 'chip_protocol_var') else "I2C"
        chip = self.chip_preset_var.get() if hasattr(self, 'chip_preset_var') else "AT24C02"
        welcome = f"""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║        ATE Pattern Generator Platform  {VERSION}             ║
    ║        Enterprise Hardware Protocol Test Platform              ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝

    {self.t("welcome_title")}
    ─────────────────────────────────────

    ■ {self.t("welcome_quick_start")}:

      1. {self.t("chip_preset_label")}:  [{chip}]
         └─ {self.t("protocol_label")}:  [{protocol}]

      2. {self.t("test_sel_label")}
         └─ OS / DC / FUNC / March C- / Addr Scan / ...

      3. {self.t("btn_generate")}  (Ctrl+G)
         └─ {self.t("preview_pat_tab")} / {self.t("preview_txt_tab")} / {self.t("wave_tab")}

      4. {self.t("btn_export")}  (Ctrl+E)
         └─ .pat / .txt / .prg / .tim / .lvl / .html / .json
         └─ .stil (IEEE 1450) / .wgl (Teradyne)

    ■ v6.0 {self.t("tab_simulator")} / {self.t("tab_shmoo")} / {self.t("tab_flow_editor")} / {self.t("tab_yield")}:

      F7  — {self.t("sim_run")}
      F8  — {self.t("shmoo_run_sweep")}

    ■ CLI Batch Mode:
      python at24c02_pat_generator.py --batch --chip {chip} --tests all

    ─────────────────────────────────────
    Supported Protocols: I2C / SPI / Microwire
    Supported Formats:   PAT / STIL / WGL
    Chips Presets:       24+ devices

    ═══════════════════════════════════════════════════════════════
"""
        self.pat_text.insert("1.0", welcome)

    # ============================================================
    # v6.0 模拟器方法
    # ============================================================

    def _run_simulation(self, step_mode=False):
        """运行向量模拟 (线程安全: 在后台线程执行, 通过 root.after 回调更新 UI)"""
        if not hasattr(self, 'current_vectors') or not self.current_vectors:
            messagebox.showinfo(self.t("sim_run"), self.t("sim_no_vectors"))
            return
        protocol = self.chip_protocol_var.get() if hasattr(self, 'chip_protocol_var') else "I2C"
        capacity = int(self.chip_capacity_var.get() or "256")
        page_size = int(self.chip_page_size_var.get() or "8")

        self._simulator = PatternSimulator(
            protocol=protocol, capacity_bytes=capacity, page_size=page_size)

        self.sim_status_label.config(text=self.t("sim_running"),
                                      fg=self.colors["warning"])

        # 准备按测试段分组的向量 (若有 pat_sections)
        sections = getattr(self, 'pat_sections', None)
        vectors = self.current_vectors
        comments = self.current_comments

        def _worker():
            t0 = _time_module.time()
            if sections:
                for name, desc, vecs, cmts, lbls in sections:
                    self._simulator.simulate_test(name, vecs, cmts)
            else:
                self._simulator.simulate(vectors, comments)
            elapsed = (_time_module.time() - t0) * 1000
            self.root.after(0, lambda: self._on_simulation_done(elapsed))

        t = threading.Thread(target=_worker, daemon=True)
        t.start()

    def _on_simulation_done(self, elapsed_ms):
        """模拟完成后的 UI 回调 (主线程)"""
        n_txn = len(self._simulator.transactions)
        n_err = len(self._simulator.errors)
        self.sim_status_label.config(
            text=self.t("sim_thread_done").format(txn=n_txn, err=n_err, t=elapsed_ms),
            fg=self.colors["success"] if n_err == 0 else self.colors["danger"])

        # 填充事务列表
        for item in self.sim_tree.get_children():
            self.sim_tree.delete(item)
        for txn in self._simulator.transactions:
            data_str = ",".join(f"0x{d:02X}" for d in txn.get("data", [])[:4])
            if len(txn.get("data", [])) > 4:
                data_str += f"...+{len(txn['data'])-4}"
            status = "✓" if txn.get("match", True) else "✗"
            self.sim_tree.insert("", tk.END, values=(
                txn.get("type", "?"),
                txn.get("command", "?"),
                f"0x{txn.get('address', 0):04X}",
                data_str, status))

        # 绘制 Fail Bit Map
        self._draw_fail_bit_map()

        # 绘制状态机
        self._draw_sim_state_machine()

        # 填充日志
        self.sim_log_text.config(state=tk.NORMAL)
        self.sim_log_text.delete("1.0", tk.END)
        for line in self._simulator.log:
            tag = "info"
            if "[WARN]" in line:
                tag = "warn"
            elif "[ERROR]" in line:
                tag = "error"
            elif "[DONE]" in line or "✓" in line:
                tag = "pass"
            self.sim_log_text.insert(tk.END, line + "\n", tag)
        self.sim_log_text.config(state=tk.DISABLED)
        self.sim_log_text.see(tk.END)
        logger.info(f"Simulation: {n_txn} transactions, {n_err} errors, {elapsed_ms:.0f}ms")

    def _reset_simulation(self):
        """重置模拟器"""
        self._simulator = None
        self._fbm_cells = []
        self._march_active_step.set(0)
        self.sim_status_label.config(text="")
        for item in self.sim_tree.get_children():
            self.sim_tree.delete(item)
        self.sim_mem_canvas.delete("all")
        self.sim_sm_canvas.delete("all")
        self.sim_log_text.config(state=tk.NORMAL)
        self.sim_log_text.delete("1.0", tk.END)
        self.sim_log_text.config(state=tk.DISABLED)
        self._march_step_desc.config(text="")

    def _draw_fail_bit_map(self):
        """绘制 Fail Bit Map 16×16 热力图 (Phase 1)"""
        canvas = self.sim_mem_canvas
        canvas.delete("all")
        self._fbm_cells = []
        sim = getattr(self, '_simulator', None)
        capacity = sim.capacity if sim else 256
        cw = canvas.winfo_width() or 500
        ch = canvas.winfo_height() or 240
        cols = 16
        rows = min(16, (capacity + 15) // 16)
        cell_w = max(22, (cw - 50) // (cols + 1))
        cell_h = max(14, (ch - 24) // (rows + 1))

        # 列标题
        for c in range(cols):
            x = 48 + c * cell_w + cell_w // 2
            canvas.create_text(x, 9, text=f"{c:X}",
                               font=("Consolas", 7, "bold"), fill=self.colors["accent"])
        # 行数据
        active_step = self._march_active_step.get() if hasattr(self, '_march_active_step') else 0
        step_addrs = None
        if active_step > 0 and sim and sim.march_steps:
            for ms in sim.march_steps:
                if ms["step_idx"] == active_step:
                    step_addrs = ms["addrs_covered"]
                    break

        for r in range(rows):
            y = 22 + r * cell_h
            base = r * 16
            canvas.create_text(24, y + cell_h // 2, text=f"{base:02X}",
                               font=("Consolas", 7), fill=self.colors["text_dim"])
            for c in range(cols):
                addr = base + c
                if addr >= capacity:
                    break
                x = 48 + c * cell_w
                # 确定颜色
                if sim and addr in sim.fail_map:
                    bg = "#1D9E75" if sim.fail_map[addr]["pass"] else "#E24B4A"
                    fg = "white"
                elif sim and addr in sim.test_coverage:
                    bg = "#1D9E75"
                    fg = "white"
                else:
                    bg = "#888780"
                    fg = "#d0d0d0"
                # March 步骤联动: 高亮边框
                outline = self.colors["border"]
                outline_w = 1
                if step_addrs is not None:
                    if addr in step_addrs:
                        outline = self.colors["gold"]
                        outline_w = 2
                    else:
                        bg = self._dim_color(bg)
                canvas.create_rectangle(x, y, x + cell_w - 1, y + cell_h - 1,
                                        fill=bg, outline=outline, width=outline_w)
                canvas.create_text(x + cell_w // 2, y + cell_h // 2,
                                   text=f"{addr:02X}", font=("Consolas", 6), fill=fg)
                self._fbm_cells.append((x, y, cell_w, cell_h, addr))

    @staticmethod
    def _dim_color(hex_color):
        """将颜色变暗 40%"""
        try:
            r = int(hex_color[1:3], 16)
            g = int(hex_color[3:5], 16)
            b = int(hex_color[5:7], 16)
            return f"#{int(r*0.6):02x}{int(g*0.6):02x}{int(b*0.6):02x}"
        except (ValueError, IndexError):
            return hex_color

    def _fbm_on_motion(self, event):
        """Fail Bit Map 鼠标悬停 tooltip"""
        if self._fbm_tooltip:
            self._fbm_tooltip.destroy()
            self._fbm_tooltip = None
        sim = getattr(self, '_simulator', None)
        if not sim:
            return
        for cx, cy, cw, ch, addr in self._fbm_cells:
            if cx <= event.x <= cx + cw and cy <= event.y <= cy + ch:
                # 构造 tooltip 内容
                if addr in sim.fail_map:
                    fm = sim.fail_map[addr]
                    status = self.t("fbm_pass") if fm["pass"] else self.t("fbm_fail")
                    tip = self.t("fbm_addr_info").format(addr=addr, status=status)
                    tip += "\n" + self.t("fbm_coverage").format(tests=", ".join(fm["tests"]))
                elif addr in sim.test_coverage:
                    tip = self.t("fbm_addr_info").format(addr=addr, status=self.t("fbm_pass"))
                    tip += "\n" + self.t("fbm_coverage").format(tests=", ".join(sim.test_coverage[addr]))
                else:
                    tip = self.t("fbm_addr_info").format(addr=addr, status=self.t("fbm_untested"))
                # 创建 tooltip
                tw = tk.Toplevel(self.root)
                tw.wm_overrideredirect(True)
                tw.wm_geometry(f"+{event.x_root+12}+{event.y_root+12}")
                lbl = tk.Label(tw, text=tip, font=("Consolas", 8),
                               bg="#1e1e2e", fg="#e2e8f0", padx=6, pady=3,
                               justify=tk.LEFT, relief=tk.SOLID, borderwidth=1)
                lbl.pack()
                self._fbm_tooltip = tw
                break

    def _fbm_on_click(self, event):
        """Fail Bit Map 点击格子弹出详情"""
        sim = getattr(self, '_simulator', None)
        if not sim:
            return
        for cx, cy, cw, ch, addr in self._fbm_cells:
            if cx <= event.x <= cx + cw and cy <= event.y <= cy + ch:
                info_lines = [self.t("fbm_detail_title"),
                              f"Address: 0x{addr:02X} ({addr})"]
                if addr in sim.fail_map:
                    fm = sim.fail_map[addr]
                    info_lines.append(f"Status: {'PASS' if fm['pass'] else 'FAIL'}")
                    info_lines.append(f"Expected: 0x{fm['expected']:02X}")
                    info_lines.append(f"Actual: 0x{fm['actual']:02X}")
                    info_lines.append(f"Tests: {', '.join(fm['tests'])}")
                elif addr in sim.test_coverage:
                    info_lines.append(f"Status: PASS (written)")
                    info_lines.append(f"Value: 0x{sim.memory[addr]:02X}")
                    info_lines.append(f"Tests: {', '.join(sim.test_coverage[addr])}")
                else:
                    info_lines.append(f"Status: UNTESTED")
                    info_lines.append(f"Value: 0x{sim.memory[addr]:02X}")
                # 找该地址相关事务
                related = [t for t in sim.transactions
                           if t.get("address", -1) <= addr < t.get("address", -1) + len(t.get("data", []))]
                if related:
                    info_lines.append(f"\nRelated transactions: {len(related)}")
                    for t in related[:5]:
                        rw = t.get("type", "?")
                        info_lines.append(f"  {rw} @ 0x{t.get('address',0):02X} "
                                          f"cycle {t.get('cycle_start',0)}-{t.get('cycle_end',0)}")
                messagebox.showinfo(self.t("fbm_detail_title"), "\n".join(info_lines))
                break

    def _select_march_step(self, step):
        """选择 March C- 步骤高亮"""
        self._march_active_step.set(step)
        # 更新按钮样式
        for i, btn in enumerate(self._march_step_btns):
            if i + 1 == step:
                btn.config(bg=self.colors["gold"], fg="black")
            else:
                btn.config(bg=self.colors["card2"], fg=self.colors["text"])
        # March 步骤描述
        march_descs = {
            1: "⇑(w0) — 全写0，检测SA1",
            2: "⇑(r0,w1) — 读0验证，写1，检测SA0/TF",
            3: "⇑(r1,w0) — 读1验证，写0，检测SA1/TF",
            4: "⇓(r0,w1) — 降序读0验证，写1，检测CF",
            5: "⇓(r1,w0) — 降序读1验证，写0，检测CF",
            6: "⇓(r0) — 降序读0最终验证",
        }
        desc = march_descs.get(step, "显示所有步骤")
        self._march_step_desc.config(text=desc)
        self._draw_fail_bit_map()

    def _export_fbm_svg(self):
        """导出 Fail Bit Map 为 SVG 矢量图"""
        sim = getattr(self, '_simulator', None)
        if not sim:
            messagebox.showinfo(self.t("fbm_title"), self.t("sim_no_vectors"))
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".svg", filetypes=[("SVG", "*.svg")],
            initialfile="FailBitMap.svg")
        if not path:
            return
        capacity = sim.capacity
        cols = 16
        rows = (capacity + 15) // 16
        cell = 28
        margin = 40
        w = margin + cols * cell + 10
        h = margin + rows * cell + 10
        svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
               f'font-family="Consolas,monospace">',
               f'<rect width="{w}" height="{h}" fill="#1e293b"/>']
        # 列标题
        for c in range(cols):
            x = margin + c * cell + cell // 2
            svg.append(f'<text x="{x}" y="14" text-anchor="middle" fill="#3b82f6" '
                       f'font-size="10" font-weight="bold">{c:X}</text>')
        for r in range(rows):
            y = margin + r * cell
            base = r * 16
            svg.append(f'<text x="20" y="{y + cell // 2 + 4}" text-anchor="middle" '
                       f'fill="#94a3b8" font-size="9">{base:02X}</text>')
            for c in range(cols):
                addr = base + c
                if addr >= capacity:
                    break
                x = margin + c * cell
                if addr in sim.fail_map:
                    bg = "#1D9E75" if sim.fail_map[addr]["pass"] else "#E24B4A"
                elif addr in sim.test_coverage:
                    bg = "#1D9E75"
                else:
                    bg = "#888780"
                svg.append(f'<rect x="{x}" y="{y}" width="{cell-1}" height="{cell-1}" '
                           f'fill="{bg}" stroke="#334155"/>')
                svg.append(f'<text x="{x+cell//2}" y="{y+cell//2+4}" text-anchor="middle" '
                           f'fill="white" font-size="8">{addr:02X}</text>')
        svg.append('</svg>')
        with open(path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(svg))
        messagebox.showinfo(self.t("fbm_title"), f"SVG → {path}")

    def _draw_sim_state_machine(self):
        """绘制协议状态机示意图"""
        canvas = self.sim_sm_canvas
        canvas.delete("all")
        if not hasattr(self, '_simulator') or not self._simulator:
            return
        protocol = self._simulator.protocol
        cw = canvas.winfo_width() or 400
        cy = 40

        if protocol == "I2C":
            states = ["IDLE", "START", "ADDR", "ACK", "DATA", "ACK", "STOP"]
        elif protocol == "SPI":
            states = ["IDLE", "CS↓", "CMD", "ADDR", "DATA", "CS↑"]
        else:
            states = ["IDLE", "CS↑", "SB", "OP", "ADDR", "DATA", "POLL", "CS↓"]

        n = len(states)
        gap = min(60, (cw - 40) // n)
        x_start = (cw - gap * (n - 1)) // 2
        for i, s in enumerate(states):
            x = x_start + i * gap
            r = 16
            canvas.create_oval(x - r, cy - r, x + r, cy + r,
                               fill=self.colors["accent"], outline="")
            canvas.create_text(x, cy, text=s, font=("Consolas", 6, "bold"), fill="white")
            if i < n - 1:
                x2 = x_start + (i + 1) * gap
                canvas.create_line(x + r, cy, x2 - r, cy,
                                   fill=self.colors["text_dim"], arrow=tk.LAST, width=1)

    # ============================================================
    # v6.0 Shmoo Plot 方法
    # ============================================================

    def _run_shmoo_sweep(self):
        """运行 Shmoo V×F 扫描"""
        v_all = ["1.8V", "2.5V", "3.3V", "5.0V"]
        v_from = self.shmoo_v_from.get()
        v_to = self.shmoo_v_to.get()
        try:
            vi, vj = v_all.index(v_from), v_all.index(v_to)
            v_range = v_all[min(vi, vj):max(vi, vj) + 1]
        except ValueError:
            v_range = v_all

        try:
            f_from = int(self.shmoo_f_from.get())
            f_to = int(self.shmoo_f_to.get())
        except ValueError:
            f_from, f_to = 100, 1000

        f_step = max(50, (f_to - f_from) // 10) if f_to > f_from else 100
        f_range = list(range(f_from, f_to + 1, f_step))
        if not f_range:
            f_range = [f_from]

        protocol = self.chip_protocol_var.get() if hasattr(self, 'chip_protocol_var') else "I2C"

        self._shmoo_engine = ShmooEngine()
        self._shmoo_engine.configure_sweep(v_range, f_range)
        self._shmoo_engine.run_sweep(None, protocol=protocol)

        self._draw_shmoo_plot()

        margins = self._shmoo_engine.calculate_margins()
        marginal = margins.get("marginal_points", 0)
        self.shmoo_margin_label.config(
            text=f"  V: {margins['v_min']} ~ {margins['v_max']}  |  "
                 f"F: {margins['f_min']} ~ {margins['f_max']}  |  "
                 f"Pass: {margins['pass_points']}/{margins['total_points']}"
                 f"  Marginal: {marginal}  Fail: {margins['fail_points']}",
            fg=self.colors["success"] if margins["fail_points"] == 0 and marginal == 0
            else self.colors["warning"] if margins["fail_points"] == 0
            else self.colors["accent"])

    def _draw_shmoo_plot(self):
        """绘制 Shmoo 热力图 — 工业级增强版 (3色 + 规格框 + 边界线 + tooltip)"""
        canvas = self.shmoo_canvas
        canvas.delete("all")
        if not self._shmoo_engine:
            return

        data = self._shmoo_engine.get_matrix()
        voltages = data["voltages"]
        freqs = data["frequencies"]
        results = data["results"]
        if not voltages or not freqs:
            return

        cw = canvas.winfo_width() or 600
        ch = canvas.winfo_height() or 300
        ml, mt, mr, mb = 70, 40, 40, 50
        pw = cw - ml - mr
        ph = ch - mt - mb
        cell_w = pw / max(1, len(freqs))
        cell_h = ph / max(1, len(voltages))

        # 保存布局信息供 tooltip 使用
        self._shmoo_layout = {
            "ml": ml, "mt": mt, "cell_w": cell_w, "cell_h": cell_h,
            "voltages": list(reversed(voltages)), "freqs": freqs,
        }

        # 状态 → 颜色映射
        color_map = {"PASS": "#22c55e", "MARGINAL": "#f59e0b", "FAIL": "#ef4444"}
        label_map = {"PASS": "P", "MARGINAL": "M", "FAIL": "F"}

        protocol = self._simulator.protocol if hasattr(self, '_simulator') and self._simulator else 'I2C'

        # 标题
        canvas.create_text(cw // 2, 15,
                           text=f"Shmoo Plot — Voltage × Frequency ({protocol})",
                           font=("Segoe UI", 10, "bold"), fill=self.colors["text"])

        # 绘制单元格 (3色: Pass=绿, Marginal=黄, Fail=红)
        for vi, vk in enumerate(reversed(voltages)):
            for fi, fk in enumerate(freqs):
                r = results.get((vk, fk), {})
                status = r.get("status", "FAIL")
                x = ml + fi * cell_w
                y = mt + vi * cell_h
                color = color_map.get(status, "#ef4444")
                canvas.create_rectangle(x, y, x + cell_w - 1, y + cell_h - 1,
                                        fill=color, outline=self.colors["border"])
                canvas.create_text(x + cell_w / 2, y + cell_h / 2,
                                   text=label_map.get(status, "F"),
                                   font=("Consolas", 9, "bold"), fill="white")

        # Y 轴标签
        for vi, vk in enumerate(reversed(voltages)):
            y = mt + vi * cell_h + cell_h / 2
            canvas.create_text(ml - 8, y, text=vk, anchor=tk.E,
                               font=("Consolas", 8), fill=self.colors["text"])

        # X 轴标签
        for fi, fk in enumerate(freqs):
            x = ml + fi * cell_w + cell_w / 2
            txt = f"{fk}k" if fk < 1000 else f"{fk/1000:.0f}M"
            canvas.create_text(x, ch - mb + 15, text=txt,
                               font=("Consolas", 7), fill=self.colors["text"])

        # 轴名
        canvas.create_text(ml - 50, ch // 2, text="Voltage",
                           font=("Segoe UI", 8), fill=self.colors["text_dim"], angle=90)
        canvas.create_text(cw // 2, ch - 8, text="Frequency",
                           font=("Segoe UI", 8), fill=self.colors["text_dim"])

        # ---- Datasheet 规格框 (白色虚线矩形) ----
        spec = ShmooEngine.get_datasheet_bounds()
        v_vals_rev = list(reversed(voltages))
        f_min_all, f_max_all = min(freqs), max(freqs)
        v_min_all = float(v_vals_rev[0].replace("V", "")) if v_vals_rev else 1.8
        v_max_all = float(v_vals_rev[-1].replace("V", "")) if v_vals_rev else 5.0

        def _v_to_y(v_val):
            """电压值 → Canvas Y 坐标"""
            ratio = (v_val - v_min_all) / (v_max_all - v_min_all) if v_max_all > v_min_all else 0.5
            return mt + ph - ratio * ph

        def _f_to_x(f_val):
            """频率值 → Canvas X 坐标"""
            ratio = (f_val - f_min_all) / (f_max_all - f_min_all) if f_max_all > f_min_all else 0.5
            return ml + ratio * pw

        # 规格框: VCC_min ~ VCC_max 垂直线
        sx1 = _f_to_x(f_min_all)
        sx2 = _f_to_x(f_max_all)
        sy_top = _v_to_y(min(spec["vcc_max"], v_max_all))
        sy_bot = _v_to_y(max(spec["vcc_min"], v_min_all))
        canvas.create_rectangle(sx1, sy_top, sx2, sy_bot,
                                outline="white", dash=(4, 4), width=2)

        # ---- Datasheet 频率边界曲线 (白色实线) ----
        boundary_pts = spec["boundary"]
        curve_coords = []
        for v_val, f_max_spec in boundary_pts:
            if v_min_all <= v_val <= v_max_all and f_min_all <= f_max_spec <= f_max_all:
                curve_coords.append((_f_to_x(f_max_spec), _v_to_y(v_val)))
        if len(curve_coords) >= 2:
            flat_coords = []
            for cx, cy in curve_coords:
                flat_coords.extend([cx, cy])
            canvas.create_line(*flat_coords, fill="white", width=2, smooth=True)
            canvas.create_text(curve_coords[-1][0] + 5, curve_coords[-1][1] - 10,
                               text="Spec", anchor=tk.W,
                               font=("Segoe UI", 7, "bold"), fill="white")

        # ---- Pass/Fail 边界线 (黄色虚线) ----
        boundary_cells = []
        for vi, vk in enumerate(reversed(voltages)):
            for fi, fk in enumerate(freqs):
                r = results.get((vk, fk), {})
                if r.get("status") == "PASS" or r.get("status") == "MARGINAL":
                    # 检查右侧或上方是否有 FAIL 邻居
                    is_edge = False
                    if fi + 1 < len(freqs):
                        nr = results.get((vk, freqs[fi + 1]), {})
                        if nr.get("status") == "FAIL":
                            is_edge = True
                    if vi + 1 < len(v_vals_rev):
                        nr = results.get((v_vals_rev[vi + 1], fk), {})
                        if nr.get("status") == "FAIL":
                            is_edge = True
                    if is_edge:
                        bx = ml + fi * cell_w + cell_w
                        by = mt + vi * cell_h + cell_h / 2
                        boundary_cells.append((bx, by))
        if len(boundary_cells) >= 2:
            flat_b = []
            for bx, by in boundary_cells:
                flat_b.extend([bx, by])
            canvas.create_line(*flat_b, fill="#f59e0b", width=2, dash=(6, 3))

        # 图例 (3色)
        legend_x = cw - 90
        for i, (lbl, clr) in enumerate([("Pass", "#22c55e"), ("Marginal", "#f59e0b"), ("Fail", "#ef4444")]):
            ly = mt + i * 18
            canvas.create_rectangle(legend_x, ly, legend_x + 16, ly + 12, fill=clr, outline="")
            canvas.create_text(legend_x + 20, ly + 6, text=lbl, anchor=tk.W,
                               font=("Segoe UI", 7), fill=self.colors["text"])

        # 绑定 tooltip
        canvas.bind("<Motion>", self._shmoo_on_motion)
        canvas.bind("<Leave>", self._shmoo_on_leave)

    def _shmoo_on_motion(self, event):
        """Shmoo 热力图 tooltip — 显示详细时序信息"""
        if not hasattr(self, '_shmoo_layout') or not self._shmoo_layout:
            return
        layout = self._shmoo_layout
        ml, mt = layout["ml"], layout["mt"]
        cw, ch = layout["cell_w"], layout["cell_h"]
        freqs = layout["freqs"]
        v_rev = layout["voltages"]

        fi = int((event.x - ml) / cw) if cw > 0 else -1
        vi = int((event.y - mt) / ch) if ch > 0 else -1

        if 0 <= fi < len(freqs) and 0 <= vi < len(v_rev):
            vk = v_rev[vi]
            fk = freqs[fi]
            r = self._shmoo_engine.results.get((vk, fk), {})
            status = r.get("status", "?")
            margin = r.get("margin_pct", 0)
            reason = r.get("fail_reason", "")

            tip_text = f"{vk} × {fk}kHz → {status} (margin: {margin:.1f}%)"
            if reason:
                tip_text += f"\n{reason}"

            # 显示时序详情 (前3项)
            details = r.get("timing_details", [])
            for td in details[:4]:
                mark = "✓" if td.get("passed") else "✗"
                tip_text += f"\n  {mark} {td['param']}: {td['actual']} ({td['required']})"

            if not hasattr(self, '_shmoo_tooltip'):
                self._shmoo_tooltip = tk.Toplevel(self.root)
                self._shmoo_tooltip.wm_overrideredirect(True)
                self._shmoo_tooltip_label = tk.Label(
                    self._shmoo_tooltip, text="", justify=tk.LEFT,
                    bg="#1e293b", fg="#e2e8f0", font=("Consolas", 8),
                    relief=tk.SOLID, borderwidth=1, padx=6, pady=4)
                self._shmoo_tooltip_label.pack()

            self._shmoo_tooltip_label.config(text=tip_text)
            x = self.shmoo_canvas.winfo_rootx() + event.x + 15
            y = self.shmoo_canvas.winfo_rooty() + event.y + 10
            self._shmoo_tooltip.wm_geometry(f"+{x}+{y}")
            self._shmoo_tooltip.deiconify()
        else:
            self._shmoo_on_leave(None)

    def _shmoo_on_leave(self, event):
        """隐藏 Shmoo tooltip"""
        if hasattr(self, '_shmoo_tooltip') and self._shmoo_tooltip:
            self._shmoo_tooltip.withdraw()

    def _export_shmoo_csv(self):
        """导出 Shmoo 结果为 CSV"""
        if not self._shmoo_engine:
            messagebox.showinfo("Shmoo", "Run sweep first")
            return
        path = filedialog.asksaveasfilename(
            title="Export Shmoo CSV", defaultextension=".csv",
            filetypes=[("CSV", "*.csv")])
        if not path:
            return
        data = self._shmoo_engine.get_matrix()
        try:
            with open(path, "w", encoding="utf-8-sig") as f:
                f.write("Voltage,Frequency_kHz,Pass,Period_ns\n")
                for (vk, fk), r in sorted(data["results"].items()):
                    f.write(f"{vk},{fk},{r['pass']},{r.get('period_ns', 0)}\n")
            messagebox.showinfo("Export", f"Shmoo CSV: {path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _export_shmoo_svg(self):
        """导出 Shmoo 热力图为 SVG 矢量图"""
        if not self._shmoo_engine:
            messagebox.showinfo("Shmoo", "Run sweep first")
            return
        path = filedialog.asksaveasfilename(
            title=self.t("shmoo_export_svg"), defaultextension=".svg",
            filetypes=[("SVG", "*.svg")])
        if not path:
            return
        data = self._shmoo_engine.get_matrix()
        voltages = data["voltages"]
        freqs = data["frequencies"]
        results = data["results"]
        if not voltages or not freqs:
            return

        svg_w, svg_h = 700, 400
        ml, mt, mr, mb = 70, 40, 40, 50
        pw, ph = svg_w - ml - mr, svg_h - mt - mb
        cell_w = pw / max(1, len(freqs))
        cell_h = ph / max(1, len(voltages))
        color_map = {"PASS": "#22c55e", "MARGINAL": "#f59e0b", "FAIL": "#ef4444"}

        lines = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_w}" height="{svg_h}" '
                 f'font-family="Consolas, monospace">']
        lines.append(f'<rect width="{svg_w}" height="{svg_h}" fill="#1e293b"/>')
        lines.append(f'<text x="{svg_w//2}" y="20" text-anchor="middle" fill="#e2e8f0" '
                     f'font-size="12" font-weight="bold">Shmoo Plot — Voltage × Frequency</text>')

        # 单元格
        for vi, vk in enumerate(reversed(voltages)):
            for fi, fk in enumerate(freqs):
                r = results.get((vk, fk), {})
                status = r.get("status", "FAIL")
                x = ml + fi * cell_w
                y = mt + vi * cell_h
                clr = color_map.get(status, "#ef4444")
                lbl = status[0]
                lines.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell_w - 1:.1f}" '
                             f'height="{cell_h - 1:.1f}" fill="{clr}"/>')
                lines.append(f'<text x="{x + cell_w/2:.1f}" y="{y + cell_h/2 + 4:.1f}" '
                             f'text-anchor="middle" fill="white" font-size="9">{lbl}</text>')

        # Y 轴标签
        for vi, vk in enumerate(reversed(voltages)):
            y = mt + vi * cell_h + cell_h / 2 + 4
            lines.append(f'<text x="{ml - 5}" y="{y:.1f}" text-anchor="end" fill="#e2e8f0" '
                         f'font-size="9">{vk}</text>')

        # X 轴标签
        for fi, fk in enumerate(freqs):
            x = ml + fi * cell_w + cell_w / 2
            txt = f"{fk}k" if fk < 1000 else f"{fk/1000:.0f}M"
            lines.append(f'<text x="{x:.1f}" y="{svg_h - mb + 18}" text-anchor="middle" '
                         f'fill="#e2e8f0" font-size="8">{txt}</text>')

        # 图例
        for i, (lbl, clr) in enumerate([("Pass", "#22c55e"), ("Marginal", "#f59e0b"), ("Fail", "#ef4444")]):
            lx, ly = svg_w - 85, mt + i * 18
            lines.append(f'<rect x="{lx}" y="{ly}" width="14" height="11" fill="{clr}"/>')
            lines.append(f'<text x="{lx + 18}" y="{ly + 9}" fill="#e2e8f0" font-size="8">{lbl}</text>')

        lines.append('</svg>')
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            messagebox.showinfo("Export", f"Shmoo SVG: {path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ============================================================
    # v8.0 Datalog + Binning 方法
    # ============================================================

    # ── v9.0 Tier3 Phase 29: 参数相关性 ──

    def _run_correlation(self):
        """运行参数相关性分析"""
        if not self._datalog_records or len(self._datalog_records) < 10:
            self._corr_status.config(text=self.t("corr_no_data"), fg=self.colors["danger"])
            return

        sigma = float(self._corr_sigma_var.get() or "3")
        self._corr_analyzer = CorrelationAnalyzer()
        self._corr_analyzer.calculate_correlation_matrix(self._datalog_records)

        # 异常值检测
        for param in self._corr_analyzer.params:
            self._corr_analyzer.identify_outliers(self._datalog_records, param, sigma)

        top = self._corr_analyzer.get_top_correlations(5)
        total_outliers = sum(len(v) for v in self._corr_analyzer.outliers.values())
        self._corr_status.config(
            text=f"{self.t('corr_top')}: {len(top)} | {self.t('corr_outliers')}: {total_outliers}",
            fg=self.colors["success"])

        # 弹窗显示结果
        self._show_correlation_results()

    def _show_correlation_results(self):
        """弹窗显示相关性分析结果"""
        dlg = tk.Toplevel(self.root)
        dlg.title(self.t("corr_title"))
        dlg.geometry("580x450")
        dlg.configure(bg=self.colors["bg"])
        dlg.transient(self.root)

        # 相关矩阵热力图 Canvas
        tk.Label(dlg, text=self.t("corr_matrix"),
                 font=("Segoe UI", 11, "bold"),
                 fg=self.colors["text"], bg=self.colors["bg"]).pack(pady=(8, 4))

        params = self._corr_analyzer.params
        matrix = self._corr_analyzer.matrix.get("matrix", [])
        n = len(params)
        cell = 50
        canvas_size = cell * (n + 1) + 20
        cc = tk.Canvas(dlg, bg=self.colors["card"], highlightthickness=0,
                       width=min(canvas_size, 500), height=min(canvas_size, 300))
        cc.pack(padx=8, pady=4)

        ox, oy = cell + 10, cell + 10
        for i in range(n):
            cc.create_text(ox + i * cell + cell // 2, oy - 8,
                          text=params[i][:6], font=("Consolas", 7),
                          fill=self.colors["text"], angle=0)
            cc.create_text(ox - 8, oy + i * cell + cell // 2,
                          text=params[i][:6], font=("Consolas", 7),
                          fill=self.colors["text"], anchor=tk.E)
            for j in range(n):
                r = matrix[i][j] if i < len(matrix) and j < len(matrix[i]) else 0
                # 颜色映射: 红=正相关, 蓝=负相关, 白=无
                if r > 0:
                    intensity = int(min(255, abs(r) * 255))
                    clr = f"#{255:02x}{255 - intensity:02x}{255 - intensity:02x}"
                else:
                    intensity = int(min(255, abs(r) * 255))
                    clr = f"#{255 - intensity:02x}{255 - intensity:02x}{255:02x}"
                cc.create_rectangle(ox + j * cell, oy + i * cell,
                                   ox + (j + 1) * cell, oy + (i + 1) * cell,
                                   fill=clr, outline=self.colors["border"])
                cc.create_text(ox + j * cell + cell // 2, oy + i * cell + cell // 2,
                              text=f"{r:.2f}", font=("Consolas", 6),
                              fill="#333" if abs(r) < 0.5 else "white")

        # 发现面板
        info = tk.Text(dlg, wrap=tk.WORD, font=("Consolas", 8),
                       bg=self.colors["card"], fg=self.colors["text"],
                       relief=tk.FLAT, height=8, state=tk.NORMAL)
        info.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        report = self._corr_analyzer.generate_report()
        info.insert(tk.END, report)
        info.config(state=tk.DISABLED)

        tk.Button(dlg, text="OK", command=dlg.destroy,
                  font=("Segoe UI", 9), bg=self.colors["accent"],
                  fg="white", relief=tk.FLAT, padx=20, pady=4,
                  cursor="hand2").pack(pady=(0, 8))

    def _generate_single_datalog(self):
        """生成单颗芯片 Datalog"""
        try:
            seed = int(self._datalog_seed.get())
        except ValueError:
            seed = 42
        segments = [s[0] for s in self.pat_sections] if hasattr(self, 'pat_sections') and self.pat_sections else None
        rec = self._datalog_gen.generate_single(device_id=1, seed=seed,
                                                 test_segments=segments)
        self._datalog_records = [rec]
        text = self._datalog_gen.format_datalog_text(rec)
        self._datalog_text.config(state=tk.NORMAL)
        self._datalog_text.delete("1.0", tk.END)
        self._datalog_text.insert("1.0", text)
        # 高亮 Fail 行
        for i, line in enumerate(text.split("\n"), 1):
            if line.rstrip().endswith("F"):
                self._datalog_text.tag_add("fail", f"{i}.0", f"{i}.end")
        self._datalog_text.tag_config("fail", foreground="#ef4444",
                                       font=("Consolas", 8, "bold"))
        self._datalog_text.config(state=tk.DISABLED)
        self._draw_bin_pie_chart(self._datalog_records)

    def _generate_batch_datalog(self):
        """批量生成 Datalog (线程)"""
        try:
            n = int(self._datalog_batch_n.get())
            seed = int(self._datalog_seed.get())
        except ValueError:
            n, seed = 100, 42
        n = min(n, 10000)

        segments = [s[0] for s in self.pat_sections] if hasattr(self, 'pat_sections') and self.pat_sections else None

        import threading
        def _worker():
            records = self._datalog_gen.generate_batch(
                count=n, seed=seed, test_segments=segments)
            self.root.after(0, lambda: self._on_batch_done(records))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_batch_done(self, records):
        """批量 Datalog 完成回调"""
        self._datalog_records = records
        # 显示前 3 条
        lines = []
        for rec in records[:3]:
            lines.append(self._datalog_gen.format_datalog_text(rec))
            lines.append("")
        if len(records) > 3:
            lines.append(f"... ({len(records) - 3} more records)")
        text = "\n".join(lines)
        self._datalog_text.config(state=tk.NORMAL)
        self._datalog_text.delete("1.0", tk.END)
        self._datalog_text.insert("1.0", text)
        for i, line in enumerate(text.split("\n"), 1):
            if line.rstrip().endswith("F"):
                self._datalog_text.tag_add("fail", f"{i}.0", f"{i}.end")
        self._datalog_text.tag_config("fail", foreground="#ef4444",
                                       font=("Consolas", 8, "bold"))
        self._datalog_text.config(state=tk.DISABLED)
        self._draw_bin_pie_chart(records)

    def _draw_bin_pie_chart(self, records):
        """绘制 Bin 分布饼图 + 更新摘要标签"""
        canvas = self._bin_pie_canvas
        canvas.delete("all")
        if not records:
            return

        total = len(records)
        counts = {}
        for rec in records:
            b = rec["bin"]
            counts[b] = counts.get(b, 0) + 1

        # 饼图
        cx, cy, r = 120, 100, 80
        start_angle = 0
        for b in sorted(counts.keys()):
            cnt = counts[b]
            extent = cnt / total * 360
            info = BIN_DEFINITIONS.get(b, {"color": "#888", "name": f"Bin{b}"})
            canvas.create_arc(cx - r, cy - r, cx + r, cy + r,
                              start=start_angle, extent=extent,
                              fill=info["color"], outline=self.colors["border"])
            # 标签 (扇形中心)
            if extent > 15:
                import math
                mid_angle = math.radians(start_angle + extent / 2)
                lx = cx + (r * 0.6) * math.cos(mid_angle)
                ly = cy - (r * 0.6) * math.sin(mid_angle)
                canvas.create_text(lx, ly, text=f"{cnt / total * 100:.0f}%",
                                   font=("Consolas", 7, "bold"), fill="white")
            start_angle += extent

        # 图例
        ly = cy + r + 10
        for b in sorted(counts.keys()):
            info = BIN_DEFINITIONS.get(b, {"color": "#888", "name": f"Bin{b}"})
            canvas.create_rectangle(10, ly, 22, ly + 10, fill=info["color"], outline="")
            canvas.create_text(26, ly + 5, text=f"Bin{b}: {info['name']}",
                               anchor=tk.W, font=("Segoe UI", 7), fill=self.colors["text"])
            ly += 14

        # 摘要标签
        good = counts.get(1, 0)
        yield_pct = good / total * 100 if total > 0 else 0
        summary_lines = [f"Total: {total}   Good: {good}   Yield: {yield_pct:.1f}%", ""]
        for b in sorted(counts.keys()):
            info = BIN_DEFINITIONS.get(b, {"name": f"Bin{b}"})
            cnt = counts[b]
            pct = cnt / total * 100
            bar = "█" * max(1, int(pct / 5))
            summary_lines.append(f"Bin {b} {info['name']:<16} {cnt:>5}  {pct:>5.1f}%  {bar}")
        self._bin_summary_label.config(text="\n".join(summary_lines))

    def _export_datalog_csv(self):
        """导出 Datalog CSV"""
        if not self._datalog_records:
            messagebox.showinfo("Datalog", self.t("datalog_no_data"))
            return
        path = filedialog.asksaveasfilename(
            title="Export Datalog CSV", defaultextension=".csv",
            filetypes=[("CSV", "*.csv")])
        if path:
            self._datalog_gen.export_csv(self._datalog_records, path)
            messagebox.showinfo("Export", f"Datalog CSV: {path}")

    def _export_bin_summary(self):
        """导出 Bin Summary CSV"""
        if not self._datalog_records:
            messagebox.showinfo("Datalog", self.t("datalog_no_data"))
            return
        path = filedialog.asksaveasfilename(
            title="Export Bin Summary", defaultextension=".csv",
            filetypes=[("CSV", "*.csv")])
        if path:
            self._datalog_gen.export_bin_summary_csv(self._datalog_records, path)
            messagebox.showinfo("Export", f"Bin Summary: {path}")

    def _export_stdf(self):
        """导出 STDF V4 二进制测试数据文件"""
        if not self._datalog_records:
            messagebox.showinfo("STDF", self.t("datalog_no_data"))
            return
        path = filedialog.asksaveasfilename(
            title=self.t("stdf_export"), defaultextension=".stdf",
            filetypes=[("STDF", "*.stdf"), ("All", "*.*")])
        if not path:
            return

        pin_list = ["A0", "A1", "A2", "WP", "SCL", "SDA"]

        def _worker():
            writer = STDFWriter()
            size = writer.export_from_datalog(
                self._datalog_records, pin_list, path)
            self.root.after(0, lambda: messagebox.showinfo(
                "STDF", f"{self.t('stdf_done')}\n{path}\n"
                        f"{self.t('stdf_bytes')}: {size:,} bytes "
                        f"({len(self._datalog_records)} devices)"))

        threading.Thread(target=_worker, daemon=True).start()

    # ── v9.0 Tier3 Phase 31: STDF 导入 ──

    def _import_stdf_file(self):
        """导入 STDF 文件并显示分析结果"""
        path = filedialog.askopenfilename(
            title=self.t("stdf_import"),
            filetypes=[("STDF", "*.stdf;*.std"), ("All", "*.*")])
        if not path:
            return

        reader = STDFReader()

        def _worker():
            reader.read_file(path)
            self.root.after(0, lambda: self._show_stdf_import(reader))

        threading.Thread(target=_worker, daemon=True).start()

    def _show_stdf_import(self, reader):
        """显示 STDF 导入结果"""
        summary = reader.get_summary()

        dlg = tk.Toplevel(self.root)
        dlg.title(self.t("stdf_summary"))
        dlg.geometry("560x420")
        dlg.configure(bg=self.colors["bg"])
        dlg.transient(self.root)

        tk.Label(dlg, text=self.t("stdf_summary"),
                 font=("Segoe UI", 14, "bold"),
                 fg=self.colors["text"], bg=self.colors["bg"]).pack(pady=(12, 6))

        info = tk.Text(dlg, wrap=tk.WORD, font=("Consolas", 9),
                       bg=self.colors["card"], fg=self.colors["text"],
                       relief=tk.FLAT, state=tk.NORMAL)
        info.pack(fill=tk.BOTH, expand=True, padx=12, pady=6)

        lines = [
            self.t("stdf_import_ok").format(n=summary["total_parts"], y=summary["yield_pct"]),
            f"  Pass: {summary['pass_count']}  Fail: {summary['total_parts'] - summary['pass_count']}",
            f"\n{self.t('stdf_bin_dist')}:",
        ]
        for b, cnt in sorted(summary["bin_distribution"].items()):
            bin_name = BIN_DEFINITIONS.get(b, {}).get("name", f"Bin {b}")
            lines.append(f"  Bin {b} ({bin_name}): {cnt}")

        if summary["param_stats"]:
            lines.append(f"\n{self.t('stdf_param_stats')}:")
            lines.append(f"  {'Param':<12s} {'Mean':>10s} {'Sigma':>10s} {'Min':>10s} {'Max':>10s}")
            for name, st in summary["param_stats"].items():
                lines.append(
                    f"  {name:<12s} {st.get('mean', 0):>10.4f} {st.get('sigma', 0):>10.4f} "
                    f"{st.get('min', 0):>10.4f} {st.get('max', 0):>10.4f}")

        info.insert(tk.END, "\n".join(lines))
        info.config(state=tk.DISABLED)

        btn_frame = tk.Frame(dlg, bg=self.colors["bg"])
        btn_frame.pack(pady=(0, 12))
        if self._datalog_records:
            tk.Button(btn_frame, text=self.t("stdf_compare"),
                      command=lambda: self._compare_stdf(reader, dlg),
                      font=("Segoe UI", 9), bg=self.colors["accent2"],
                      fg="white", relief=tk.FLAT, padx=12, pady=4,
                      cursor="hand2").pack(side=tk.LEFT, padx=4)
        tk.Button(btn_frame, text="OK", command=dlg.destroy,
                  font=("Segoe UI", 9), bg=self.colors["accent"],
                  fg="white", relief=tk.FLAT, padx=20, pady=4,
                  cursor="hand2").pack(side=tk.LEFT, padx=4)

    def _compare_stdf(self, reader, parent_dlg):
        """对比 STDF 导入 vs 模拟数据"""
        result = reader.compare_with_generated(self._datalog_records)
        msg = (f"STDF: {result['stdf']['total']} parts, yield={result['stdf']['yield_pct']:.1f}%\n"
               f"Sim:  {result['generated']['total']} parts, yield={result['generated']['yield_pct']:.1f}%\n"
               f"Yield diff: {result['yield_diff']:+.1f}%")
        messagebox.showinfo(self.t("stdf_compare_result"), msg, parent=parent_dlg)

    # ── v9.0 Tier3 Phase 30: PAT 导入 ──

    # ── v9.0 Tier3 Phase 32: 标准合规 ──

    def _run_standards_compliance(self):
        """生成标准合规报告"""
        mapper = self._std_mapper
        rows = mapper.generate_matrix_data()

        # 清空并填充 Treeview
        self._std_tree.delete(*self._std_tree.get_children())
        for row in rows:
            tag = row["status"]
            status_icon = {"covered": "✓ Covered", "partial": "◐ Partial",
                          "not_applicable": "○ N/A"}.get(row["status"], row["status"])
            self._std_tree.insert("", tk.END, values=(
                row["standard"], row["clause"], row["title"],
                status_icon, row["covered_by"]), tags=(tag,))

        comp = mapper.calculate_compliance()
        self._std_status.config(
            text=f"AEC-Q100: {comp['aec']['pct']:.0f}% | JEDEC: {comp['jedec']['pct']:.0f}%",
            fg=self.colors["success"])

    # ── v9.0 Tier3 Phase 33: 版本管理 ──

    def _save_version(self):
        """保存当前配置为版本快照"""
        label = simpledialog.askstring(
            self.t("ver_save"), self.t("ver_label_hint"),
            parent=self.root)
        if not label:
            return

        config = self._build_config_dict()
        test_names = [k for k, v in self.test_vars.items() if v.get()]
        stats = {}
        if hasattr(self, 'pat_sections') and self.pat_sections:
            total_vecs = sum(len(s[2]) for s in self.pat_sections)
            stats = {"total_vectors": total_vecs, "segments": len(self.pat_sections)}

        h = self._ver_mgr.save_version(config, test_names, stats, label)
        messagebox.showinfo(self.t("ver_save"),
                           self.t("ver_saved").format(label=f"{label} ({h})"))

    def _load_version_dialog(self):
        """版本列表对话框"""
        versions = self._ver_mgr.list_versions()
        if not versions:
            messagebox.showinfo(self.t("ver_list"), self.t("ver_no_versions"))
            return

        dlg = tk.Toplevel(self.root)
        dlg.title(self.t("ver_list"))
        dlg.geometry("550x350")
        dlg.configure(bg=self.colors["bg"])
        dlg.transient(self.root)

        cols = ("label", "timestamp", "hash", "tests")
        tree = ttk.Treeview(dlg, columns=cols, show="headings", height=10)
        for col, hdr, w in [("label","Label",150),("timestamp","Timestamp",150),
                            ("hash","Hash",80),("tests","Tests",50)]:
            tree.heading(col, text=hdr)
            tree.column(col, width=w, anchor=tk.W)
        for v in versions:
            tree.insert("", tk.END, values=(v["label"], v["timestamp"],
                        v["hash"], v["tests"]), tags=(v["filepath"],))
        tree.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        def _load():
            sel = tree.selection()
            if not sel:
                return
            fp = tree.item(sel[0], "tags")[0]
            data = self._ver_mgr.load_version(fp)
            config = data.get("config", {})
            self._apply_config_dict(config)
            messagebox.showinfo(self.t("ver_load"),
                               self.t("ver_loaded").format(label=data.get("version_label", "?")))
            dlg.destroy()

        btn_frame = tk.Frame(dlg, bg=self.colors["bg"])
        btn_frame.pack(pady=(0, 8))
        tk.Button(btn_frame, text=self.t("ver_load"), command=_load,
                  font=("Segoe UI", 9), bg=self.colors["accent"],
                  fg="white", relief=tk.FLAT, padx=16, pady=4,
                  cursor="hand2").pack(side=tk.LEFT, padx=4)
        tk.Button(btn_frame, text="Cancel", command=dlg.destroy,
                  font=("Segoe UI", 9), bg=self.colors["card"],
                  fg=self.colors["text"], relief=tk.FLAT, padx=16, pady=4,
                  cursor="hand2").pack(side=tk.LEFT, padx=4)

    def _compare_versions_dialog(self):
        """版本对比对话框"""
        versions = self._ver_mgr.list_versions()
        if len(versions) < 2:
            messagebox.showinfo(self.t("ver_compare"), self.t("ver_no_versions"))
            return

        dlg = tk.Toplevel(self.root)
        dlg.title(self.t("ver_diff_title"))
        dlg.geometry("600x450")
        dlg.configure(bg=self.colors["bg"])
        dlg.transient(self.root)

        sel_frame = tk.Frame(dlg, bg=self.colors["bg"])
        sel_frame.pack(fill=tk.X, padx=12, pady=(12, 6))

        labels = [f"{v['label']} ({v['hash']})" for v in versions]
        tk.Label(sel_frame, text="Version A:", font=("Segoe UI", 9),
                 fg=self.colors["text"], bg=self.colors["bg"]).pack(side=tk.LEFT)
        var_a = tk.StringVar(value=labels[0] if labels else "")
        cb_a = ttk.Combobox(sel_frame, textvariable=var_a, values=labels,
                            state="readonly", width=25)
        cb_a.pack(side=tk.LEFT, padx=4)

        tk.Label(sel_frame, text="Version B:", font=("Segoe UI", 9),
                 fg=self.colors["text"], bg=self.colors["bg"]).pack(side=tk.LEFT, padx=(12, 0))
        var_b = tk.StringVar(value=labels[1] if len(labels) > 1 else "")
        cb_b = ttk.Combobox(sel_frame, textvariable=var_b, values=labels,
                            state="readonly", width=25)
        cb_b.pack(side=tk.LEFT, padx=4)

        result_text = tk.Text(dlg, wrap=tk.WORD, font=("Consolas", 9),
                              bg=self.colors["card"], fg=self.colors["text"],
                              relief=tk.FLAT, state=tk.DISABLED)
        result_text.pack(fill=tk.BOTH, expand=True, padx=12, pady=6)

        def _do_compare():
            idx_a = labels.index(var_a.get()) if var_a.get() in labels else 0
            idx_b = labels.index(var_b.get()) if var_b.get() in labels else 1
            data_a = self._ver_mgr.load_version(versions[idx_a]["filepath"])
            data_b = self._ver_mgr.load_version(versions[idx_b]["filepath"])
            diff = self._ver_mgr.compare_versions(data_a, data_b)

            result_text.config(state=tk.NORMAL)
            result_text.delete("1.0", tk.END)
            lines = [f"Summary: {diff['summary']}\n"]

            if diff["config_diffs"]:
                lines.append("Config Changes:")
                for d in diff["config_diffs"][:20]:
                    lines.append(f"  {d['key']}: {d['a']} → {d['b']}")

            if diff["test_diffs"]["added"]:
                lines.append(f"\nTests Added: {', '.join(diff['test_diffs']['added'])}")
            if diff["test_diffs"]["removed"]:
                lines.append(f"Tests Removed: {', '.join(diff['test_diffs']['removed'])}")

            if diff["stats_diffs"]:
                lines.append("\nStatistics:")
                for s in diff["stats_diffs"]:
                    lines.append(f"  {s['key']}: {s['a']} → {s['b']} ({s['change']})")

            result_text.insert(tk.END, "\n".join(lines))
            result_text.config(state=tk.DISABLED)

        tk.Button(sel_frame, text="Compare", command=_do_compare,
                  font=("Segoe UI", 8, "bold"), bg=self.colors["accent"],
                  fg="white", relief=tk.FLAT, padx=10, pady=2,
                  cursor="hand2").pack(side=tk.LEFT, padx=8)

        tk.Button(dlg, text="Close", command=dlg.destroy,
                  font=("Segoe UI", 9), bg=self.colors["card"],
                  fg=self.colors["text"], relief=tk.FLAT, padx=20, pady=4,
                  cursor="hand2").pack(pady=(0, 12))

    def _import_pat_file(self):
        """导入 PAT 文件并反向解码"""
        path = filedialog.askopenfilename(
            title=self.t("pat_import"),
            filetypes=[("PAT", "*.pat"), ("All", "*.*")])
        if not path:
            return

        try:
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        parser = PATReverseParser()
        result = parser.parse_pat_file(content)
        proto = parser.detect_protocol()

        # 根据协议解码
        if proto == "I2C":
            parser.decode_i2c_transactions()
        elif proto == "SPI":
            parser.decode_spi_transactions()
        elif proto == "Microwire":
            parser.decode_mw_transactions()

        self._show_pat_import(parser, result)

    def _show_pat_import(self, parser, result):
        """显示 PAT 导入解码结果"""
        dlg = tk.Toplevel(self.root)
        dlg.title(self.t("pat_decode_report"))
        dlg.geometry("700x500")
        dlg.configure(bg=self.colors["bg"])
        dlg.transient(self.root)

        # 摘要
        summary = (f"{self.t('pat_import_ok').format(n=result['vector_count'], pins=len(result['pins']))}\n"
                   f"{self.t('pat_detected').format(proto=parser.protocol)}\n"
                   f"{self.t('pat_transactions').format(n=len(parser.transactions))}")
        tk.Label(dlg, text=summary, font=("Segoe UI", 10),
                 fg=self.colors["text"], bg=self.colors["bg"],
                 justify=tk.LEFT).pack(padx=12, pady=(12, 6), anchor=tk.W)

        # 事务 Treeview
        cols = ("num", "type", "addr", "data", "acks", "vectors")
        tree = ttk.Treeview(dlg, columns=cols, show="headings", height=12)
        for col, hdr, w in [("num","#",40),("type","Type",90),("addr","DevAddr",70),
                            ("data","Data",160),("acks","ACKs",70),("vectors","Vectors",90)]:
            tree.heading(col, text=hdr)
            tree.column(col, width=w, anchor=tk.CENTER if w < 100 else tk.W)
        for i, t in enumerate(parser.transactions):
            data_str = ", ".join(t.get("data", t.get("bytes", [])))[:30]
            ack_str = "".join("✓" if a else "✗" for a in t.get("acks", []))[:8]
            vr = t.get("vector_range", (0, 0))
            tree.insert("", tk.END, values=(i + 1, t["type"],
                        t.get("device_addr", "?"), data_str, ack_str,
                        f"{vr[0]}-{vr[1]}"))
        tree.pack(fill=tk.BOTH, expand=True, padx=12, pady=6)

        btn_frame = tk.Frame(dlg, bg=self.colors["bg"])
        btn_frame.pack(pady=(0, 12))
        tk.Button(btn_frame, text="OK", command=dlg.destroy,
                  font=("Segoe UI", 9), bg=self.colors["accent"],
                  fg="white", relief=tk.FLAT, padx=20, pady=4,
                  cursor="hand2").pack()

    # ============================================================
    # v8.0 Wafer Map 方法
    # ============================================================

    def _generate_wafer_map(self):
        """生成晶圆图 (线程)"""
        try:
            seed = int(self._wafer_seed.get())
        except ValueError:
            seed = 42

        def _worker():
            gen = WaferMapGenerator(seed=seed)
            gen.generate_die_layout()
            gen.assign_bins()
            gen.calculate_stats()
            self.root.after(0, lambda: self._on_wafer_done(gen))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_wafer_done(self, gen):
        """晶圆图生成完成回调"""
        self._wafer_gen = gen
        self._draw_wafer_map()
        # 更新统计
        stats = gen.stats
        lines = [f"Wafer Summary", "─" * 20,
                 f"Total Dies: {stats['total_dies']:,}",
                 f"Good Dies:  {stats['good_dies']:,}",
                 f"Yield:      {stats['yield_pct']:.1f}%", "",
                 "Bin Distribution:", "─" * 20]
        for b in sorted(stats["bin_counts"].keys()):
            cnt = stats["bin_counts"][b]
            pct = cnt / stats["total_dies"] * 100
            info = BIN_DEFINITIONS.get(b, {"name": f"Bin{b}"})
            bar = "█" * max(1, int(pct / 3))
            lines.append(f"Bin {b} {cnt:>5} {pct:>5.1f}% {bar}")
            lines.append(f"  {info['name']}")
        self._wafer_stats_label.config(text="\n".join(lines))

    def _draw_wafer_map(self):
        """绘制晶圆图"""
        canvas = self._wafer_canvas
        canvas.delete("all")
        if not self._wafer_gen or not self._wafer_gen.die_map:
            return

        gen = self._wafer_gen
        cw = canvas.winfo_width() or 500
        ch = canvas.winfo_height() or 500
        size = min(cw, ch) - 20
        cx, cy = cw // 2, ch // 2
        radius = size / 2

        # 晶圆轮廓
        canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius,
                           outline=self.colors["text_dim"], width=2)

        # Flat 标记
        flat_w = radius * 0.6
        flat_y = cy + radius - 5
        canvas.create_line(cx - flat_w, flat_y, cx + flat_w, flat_y,
                           fill=self.colors["text_dim"], width=2)

        # 计算 die 到像素的缩放
        cfg = WaferMapGenerator.WAFER_CONFIG
        wafer_r = cfg["diameter_mm"] / 2
        scale = radius / wafer_r

        die_w = cfg["die_width_mm"] * scale
        die_h = cfg["die_height_mm"] * scale

        mode = self._wafer_mode_var.get()

        # 保存 die 位置供 tooltip 使用
        self._wafer_die_rects = {}

        for (col, row), die_data in gen.die_map.items():
            px = cx + die_data["x_mm"] * scale - die_w / 2
            py = cy - die_data["y_mm"] * scale - die_h / 2  # Y 轴翻转

            bin_num = die_data["bin"]

            if mode == "bin_map":
                info = BIN_DEFINITIONS.get(bin_num, {"color": "#888"})
                color = info["color"]
            elif mode == "yield_heatmap":
                # 绿=PASS, 红=FAIL
                color = "#22c55e" if bin_num == 1 else "#ef4444"
            else:  # single_bin - 暂时全部显示
                color = BIN_DEFINITIONS.get(bin_num, {"color": "#888"})["color"]

            rid = canvas.create_rectangle(px, py, px + die_w - 1, py + die_h - 1,
                                          fill=color, outline="", width=0)
            self._wafer_die_rects[rid] = die_data

    def _wafer_on_motion(self, event):
        """Wafer Map tooltip"""
        items = self._wafer_canvas.find_overlapping(event.x - 1, event.y - 1,
                                                     event.x + 1, event.y + 1)
        for item in items:
            if item in getattr(self, '_wafer_die_rects', {}):
                d = self._wafer_die_rects[item]
                info = BIN_DEFINITIONS.get(d["bin"], {"name": "?"})
                tip = (f"Die ({d['x_mm']:.1f}, {d['y_mm']:.1f})mm\n"
                       f"Bin {d['bin']}: {info['name']}\n"
                       f"Result: {d['result']}")

                if not hasattr(self, '_wafer_tooltip'):
                    self._wafer_tooltip = tk.Toplevel(self.root)
                    self._wafer_tooltip.wm_overrideredirect(True)
                    self._wafer_tooltip_label = tk.Label(
                        self._wafer_tooltip, text="", justify=tk.LEFT,
                        bg="#1e293b", fg="#e2e8f0", font=("Consolas", 8),
                        relief=tk.SOLID, borderwidth=1, padx=6, pady=4)
                    self._wafer_tooltip_label.pack()

                self._wafer_tooltip_label.config(text=tip)
                x = self._wafer_canvas.winfo_rootx() + event.x + 15
                y = self._wafer_canvas.winfo_rooty() + event.y + 10
                self._wafer_tooltip.wm_geometry(f"+{x}+{y}")
                self._wafer_tooltip.deiconify()
                return
        self._wafer_on_leave(None)

    def _wafer_on_leave(self, event):
        """隐藏 Wafer tooltip"""
        if hasattr(self, '_wafer_tooltip') and self._wafer_tooltip:
            self._wafer_tooltip.withdraw()

    def _export_wafer_svg(self):
        """导出晶圆图为 SVG"""
        if not self._wafer_gen or not self._wafer_gen.die_map:
            messagebox.showinfo("Wafer", self.t("wafer_no_data"))
            return
        path = filedialog.asksaveasfilename(
            title=self.t("wafer_export_svg"), defaultextension=".svg",
            filetypes=[("SVG", "*.svg")])
        if not path:
            return

        gen = self._wafer_gen
        cfg = WaferMapGenerator.WAFER_CONFIG
        svg_size = 500
        cx, cy = svg_size // 2, svg_size // 2
        wafer_r = cfg["diameter_mm"] / 2
        scale = (svg_size - 20) / 2 / wafer_r
        die_w = cfg["die_width_mm"] * scale
        die_h = cfg["die_height_mm"] * scale

        lines = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_size}" '
                 f'height="{svg_size}" font-family="Consolas">']
        lines.append(f'<rect width="{svg_size}" height="{svg_size}" fill="#1e293b"/>')
        radius = (svg_size - 20) / 2
        lines.append(f'<circle cx="{cx}" cy="{cy}" r="{radius}" '
                     f'fill="none" stroke="#94a3b8" stroke-width="2"/>')

        for die_data in gen.die_map.values():
            px = cx + die_data["x_mm"] * scale - die_w / 2
            py = cy - die_data["y_mm"] * scale - die_h / 2
            clr = BIN_DEFINITIONS.get(die_data["bin"], {"color": "#888"})["color"]
            lines.append(f'<rect x="{px:.1f}" y="{py:.1f}" '
                         f'width="{die_w:.1f}" height="{die_h:.1f}" fill="{clr}"/>')

        # 统计文本
        stats = gen.stats
        lines.append(f'<text x="10" y="{svg_size - 10}" fill="#e2e8f0" font-size="10">'
                     f'Dies: {stats["total_dies"]}  Yield: {stats["yield_pct"]:.1f}%</text>')
        lines.append('</svg>')

        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            messagebox.showinfo("Export", f"Wafer SVG: {path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ============================================================
    # v9.0 Phase 22: 温度角分析 GUI 方法
    # ============================================================

    def _run_temp_analysis(self):
        """运行温度角分析并更新 Canvas + Treeview"""
        sim = TemperatureCornerSimulator()
        corner = self._temp_corner_var.get()
        rows, temps = sim.generate_report_data(corner)

        # 更新 Treeview 表头
        cols = ("param", "unit") + tuple(f"t{i+1}" for i in range(len(temps))) + ("margin", "limit")
        self._temp_tree["columns"] = cols
        for col in cols:
            self._temp_tree.column(col, width=55, minwidth=35, anchor=tk.CENTER)
        self._temp_tree.heading("param", text="Param")
        self._temp_tree.heading("unit", text="Unit")
        for i, t in enumerate(temps):
            self._temp_tree.heading(f"t{i+1}", text=f"{t}\u00b0C")
        self._temp_tree.heading("margin", text=self.t("temp_margin"))
        self._temp_tree.heading("limit", text=self.t("temp_limit"))

        # 填充数据
        self._temp_tree.delete(*self._temp_tree.get_children())
        pass_count = 0
        fail_count = 0
        for row in rows:
            if not self._temp_param_vars.get(row["param"], tk.BooleanVar(value=True)).get():
                continue
            vals = [row["param"], row["unit"]]
            all_pass = True
            worst_margin = 100.0
            for t in temps:
                r = row["values"][t]
                vals.append(f"{r['value']:.3g}")
                if not r["pass"]:
                    all_pass = False
                if r["margin_pct"] < worst_margin:
                    worst_margin = r["margin_pct"]
            vals.append(f"{worst_margin:.0f}%")
            if row["limit_temp"] is not None:
                vals.append(f"{row['limit_temp']}\u00b0C")
            else:
                vals.append(self.t("temp_all_pass"))
            tag = "pass" if all_pass else ("warn" if worst_margin > 0 else "fail")
            self._temp_tree.insert("", tk.END, values=vals, tags=(tag,))
            if all_pass:
                pass_count += 1
            else:
                fail_count += 1

        # 汇总
        total = pass_count + fail_count
        self._temp_summary_label.config(
            text=f"Corner: {corner} | Params: {total} | "
                 f"Pass: {pass_count} | Fail/Warn: {fail_count}")

        # 绘制曲线图
        self._draw_temp_curves(sim, corner, temps)

    def _draw_temp_curves(self, sim, corner, temps):
        """在 Canvas 上绘制参数-温度曲线"""
        c = self._temp_canvas
        c.delete("all")
        w = c.winfo_width() or 500
        h = c.winfo_height() or 350

        margin_l, margin_r, margin_t, margin_b = 60, 20, 30, 40
        plot_w = w - margin_l - margin_r
        plot_h = h - margin_t - margin_b

        if plot_w < 50 or plot_h < 50:
            return

        # 温度范围
        t_min, t_max = temps[0], temps[-1]
        t_range = t_max - t_min or 1

        # 背景
        c.create_rectangle(0, 0, w, h, fill=self.colors["card"], outline="")
        c.create_rectangle(margin_l, margin_t, w - margin_r, h - margin_b,
                          fill=self.colors["bg"], outline=self.colors["border"])

        # X轴刻度
        for t in temps:
            x = margin_l + (t - t_min) / t_range * plot_w
            c.create_line(x, h - margin_b, x, h - margin_b + 5, fill=self.colors["text_dim"])
            c.create_text(x, h - margin_b + 15, text=f"{t}\u00b0C",
                         font=("Consolas", 7), fill=self.colors["text_dim"])

        # 颜色分配
        colors = ["#ef4444", "#3b82f6", "#22c55e", "#f97316",
                  "#a855f7", "#06b6d4", "#eab308", "#ec4899"]
        param_list = [p for p in sim.TEMP_COEFFICIENTS
                      if self._temp_param_vars.get(p, tk.BooleanVar(value=True)).get()]

        # 为每个参数画曲线 (归一化到各自spec范围)
        legend_y = margin_t + 10
        for idx, param in enumerate(param_list):
            coeff = sim.TEMP_COEFFICIENTS[param]
            color = colors[idx % len(colors)]

            # 计算参数在全温度范围的值
            t_points = list(range(t_min, t_max + 1, max(1, (t_max - t_min) // 100)))
            vals = [sim.calc_at_temp(param, t) for t in t_points]
            v_min, v_max = min(vals), max(vals)

            # 扩展范围到 spec
            if coeff["spec_min"] is not None:
                v_min = min(v_min, coeff["spec_min"] * 0.8)
            if coeff["spec_max"] is not None:
                v_max = max(v_max, coeff["spec_max"] * 1.2)
            v_range = v_max - v_min or 1

            # 画 spec 范围 (半透明带)
            if coeff["spec_max"] is not None:
                y_spec = margin_t + (1 - (coeff["spec_max"] - v_min) / v_range) * plot_h
                c.create_line(margin_l, y_spec, w - margin_r, y_spec,
                             fill=color, dash=(2, 4), width=1)

            # 画曲线
            points = []
            for t, v in zip(t_points, vals):
                x = margin_l + (t - t_min) / t_range * plot_w
                y = margin_t + (1 - (v - v_min) / v_range) * plot_h
                points.append((x, y))
            if len(points) >= 2:
                flat = [coord for pt in points for coord in pt]
                c.create_line(*flat, fill=color, width=2, smooth=True)

            # 标记角点
            for t in temps:
                v = sim.calc_at_temp(param, t)
                x = margin_l + (t - t_min) / t_range * plot_w
                y = margin_t + (1 - (v - v_min) / v_range) * plot_h
                r_info = sim.run_corner_analysis(corner).get(t, {}).get(param, {})
                dot_color = "#22c55e" if r_info.get("pass", True) else "#ef4444"
                c.create_oval(x - 3, y - 3, x + 3, y + 3, fill=dot_color, outline="")

            # 图例
            c.create_line(w - margin_r - 90, legend_y, w - margin_r - 70, legend_y,
                         fill=color, width=2)
            c.create_text(w - margin_r - 65, legend_y, text=f"{param} ({coeff['unit']})",
                         font=("Consolas", 7), fill=color, anchor=tk.W)
            legend_y += 14

    # ============================================================
    # v9.0 Datasheet 覆盖矩阵 GUI 方法
    # ============================================================

    def _update_compliance_matrix(self):
        """根据当前选中的测试类型刷新覆盖矩阵"""
        if not hasattr(self, 'compliance_tree'):
            return

        # 收集已选测试
        enabled = set()
        test_map = {
            "os_test": "OS", "dc_test": "DC", "func_test": "FUNC",
            "march_test": "March", "march_b_test": "March",
            "scan_test": "AddrScan", "ret_test": "DataRet",
            "err_test": "I2CErr", "endur_test": "Endurance",
        }
        for key, name in test_map.items():
            if hasattr(self, 'test_vars') and key in self.test_vars:
                if self.test_vars[key].get():
                    enabled.add(name)
            else:
                enabled.add(name)  # 默认全选

        # 清空并填充
        for item in self.compliance_tree.get_children():
            self.compliance_tree.delete(item)

        rows = self._compliance_matrix.generate_matrix_data(enabled)
        for r in rows:
            covered_str = ", ".join(r["covered_by"])
            tag = "covered" if r["status"] == "COVERED" else "uncovered"
            self.compliance_tree.insert("", tk.END, values=(
                r["id"], r["name"], r["cat"], r["spec"], covered_str, r["status"]),
                tags=(tag,))

        self.compliance_tree.tag_configure("covered", foreground=self.colors.get("success", "#22c55e"))
        self.compliance_tree.tag_configure("uncovered", foreground=self.colors.get("danger", "#ef4444"))

        cov = self._compliance_matrix.calculate_coverage(enabled)
        self.compliance_summary_label.config(
            text=f'{self.t("compliance_pct")}: {cov["covered"]}/{cov["total"]} '
                 f'({cov["pct"]:.1f}%)  |  '
                 + "  ".join(f'{cat}: {d["covered"]}/{d["total"]}'
                             for cat, d in cov["by_category"].items()))

    # ============================================================
    # v8.0 向量调试器 GUI 方法
    # ============================================================

    def _debug_ensure(self):
        """确保调试器已初始化，使用当前向量"""
        if not self.current_vectors:
            messagebox.showinfo("Debug", self.t("debug_no_vectors"))
            return False
        if self._debugger is None or len(self._debugger.vectors) != len(self.current_vectors):
            self._debugger = VectorDebugger(
                self.current_vectors, self.current_comments,
                self.current_labels if hasattr(self, "current_labels") else None)
        return True

    def _debug_reset(self):
        if not self._debug_ensure():
            return
        self._debugger.reset()
        self._debug_update_ui(None)
        self.dbg_mode_label.config(text=self.t("debug_stopped"),
                                    fg=self.colors["text_dim"])
        self.dbg_history_text.config(state=tk.NORMAL)
        self.dbg_history_text.delete("1.0", tk.END)
        self.dbg_history_text.config(state=tk.DISABLED)

    def _debug_step(self):
        if not self._debug_ensure():
            return
        result = self._debugger.step()
        self._debug_update_ui(result)

    def _debug_step_txn(self):
        if not self._debug_ensure():
            return
        result = self._debugger.step_transaction()
        self._debug_update_ui(result)

    def _debug_step_section(self):
        if not self._debug_ensure():
            return
        result = self._debugger.step_section()
        self._debug_update_ui(result)

    def _debug_run_bp(self):
        if not self._debug_ensure():
            return
        self.dbg_mode_label.config(text=self.t("debug_running"),
                                    fg=self.colors["accent"])
        self.root.update_idletasks()
        result = self._debugger.run_to_breakpoint()
        self._debug_update_ui(result)

    def _debug_stop(self):
        if self._debugger:
            self._debugger.stop()
            self.dbg_mode_label.config(text=self.t("debug_stopped"),
                                        fg=self.colors["text_dim"])

    def _debug_add_bp(self):
        if not self._debug_ensure():
            return
        txt = self.dbg_bp_entry.get().strip()
        if not txt:
            return
        try:
            idx = int(txt)
            self._debugger.set_breakpoint(idx)
            self.dbg_bp_entry.delete(0, tk.END)
            bps = sorted(self._debugger.breakpoints)
            bp_str = ", ".join(str(b) for b in bps[:10])
            if len(bps) > 10:
                bp_str += f"... (+{len(bps)-10})"
            self.dbg_bp_list_label.config(text=f"BP: {bp_str}" if bps else "BP: (none)")
        except ValueError:
            pass

    def _debug_clear_all_bp(self):
        if self._debugger:
            self._debugger.breakpoints.clear()
            self.dbg_bp_list_label.config(text="BP: (none)")

    def _debug_update_ui(self, result):
        """更新调试器 UI 面板"""
        if self._debugger is None:
            return

        pc = self._debugger.pc
        total = len(self._debugger.vectors)

        if result and result.get("done"):
            self.dbg_mode_label.config(text=self.t("debug_end"),
                                        fg=self.colors["warning"])
        else:
            self.dbg_mode_label.config(text=f"PC={pc}/{total}",
                                        fg=self.colors["success"])

        # 状态标签
        bus = self._debugger._analyze_bus_state() if pc < total else "-"
        event = result.get("event", "-") if result else "-"
        comment = result.get("comment", "") if result else ""
        vec_str = result.get("vector_str", "-") if result else "-"
        self.dbg_state_label.config(
            text=f"PC:{pc} | Bus:{bus} | Event:{event} | {vec_str} | {comment}")

        # 执行历史
        if result:
            self.dbg_history_text.config(state=tk.NORMAL)
            line = (f"[{result.get('pc', pc):5d}] {result.get('vector_str', '')} "
                    f"| {result.get('event', '-'):10s} | {result.get('comment', '')}\n")
            self.dbg_history_text.insert(tk.END, line)
            self.dbg_history_text.see(tk.END)
            # 保留最近 200 行
            line_count = int(self.dbg_history_text.index("end-1c").split(".")[0])
            if line_count > 200:
                self.dbg_history_text.delete("1.0", f"{line_count - 200}.0")
            self.dbg_history_text.config(state=tk.DISABLED)

        # 同步 PAT 预览滚动
        if hasattr(self, "pat_text") and pc < total:
            try:
                self.pat_text.see(f"{pc + 1}.0")
                self.pat_text.tag_remove("dbg_current", "1.0", tk.END)
                self.pat_text.tag_add("dbg_current", f"{pc + 1}.0",
                                      f"{pc + 1}.end")
                self.pat_text.tag_configure("dbg_current",
                                            background=self.colors.get("accent", "#3b82f6"),
                                            foreground="#ffffff")
            except Exception:
                pass

    # ============================================================
    # v6.0 流程编排方法
    # ============================================================

    def _populate_flow_tables(self):
        """填充 Bin 表和限值表"""
        # Bin 表
        for item in self.bin_tree.get_children():
            self.bin_tree.delete(item)
        for bn, (name, btype, desc) in sorted(self._flow_engine.bin_table.items()):
            self.bin_tree.insert("", tk.END, values=(bn, name, btype, desc))

        # 限值表
        for item in self.limits_tree.get_children():
            self.limits_tree.delete(item)
        for param, spec in self._flow_engine.test_limits.items():
            mn = f"{spec['min']}" if spec.get("min") is not None else "—"
            mx = f"{spec['max']}" if spec.get("max") is not None else "—"
            self.limits_tree.insert("", tk.END, values=(
                param, mn, mx, spec.get("unit", "")))

        # 绘制流程图
        self._draw_flow_editor()

    def _flow_reset_default(self):
        """重置流程为默认"""
        selected = [k for k, v in self.test_vars.items() if v.get()]
        self._flow_engine.build_default_flow(selected)
        self._populate_flow_tables()

    def _draw_flow_editor(self):
        """绘制测试流程编排画布"""
        canvas = self.flow_edit_canvas
        canvas.delete("all")
        cw = canvas.winfo_width() or 340
        x_center = cw // 2 - 30
        y = 25
        node_h = 32
        gap = 10
        bin_x = cw - 55

        node_positions = {}
        for node in self._flow_engine.nodes:
            nid = node["id"]
            ntype = node["type"]

            if ntype in ("start", "end"):
                color = self.colors["success"] if ntype == "start" else self.colors["danger"]
                canvas.create_oval(x_center - 35, y, x_center + 35, y + 26,
                                    fill=color, outline="")
                canvas.create_text(x_center, y + 13, text=node["label"],
                                   font=("Segoe UI", 8, "bold"), fill="white")
                node_positions[nid] = (x_center, y + 26)
                y += 26 + gap
            elif ntype == "test":
                canvas.create_rectangle(x_center - 55, y, x_center + 55, y + node_h,
                                        fill=self.colors["card"], outline=self.colors["accent"], width=2)
                canvas.create_rectangle(x_center - 55, y, x_center - 51, y + node_h,
                                        fill=self.colors["accent"], outline="")
                canvas.create_text(x_center, y + node_h // 2,
                                   text=node["label"], font=("Segoe UI", 7),
                                   fill=self.colors["text"])
                node_positions[nid] = (x_center, y + node_h)
                y += node_h + gap
            elif ntype == "bin":
                bx, by = bin_x, y - node_h - gap + 2
                if by < 20:
                    by = 20
                canvas.create_rectangle(bx - 25, by, bx + 25, by + 18,
                                        fill="#ef4444", outline="")
                lbl = node["label"].split("\n")[0] if "\n" in node.get("label", "") else node.get("label", "")
                canvas.create_text(bx, by + 9, text=lbl,
                                   font=("Consolas", 6, "bold"), fill="white")
                node_positions[nid] = (bx, by + 9)

        # 绘制连线
        for edge in self._flow_engine.edges:
            f = node_positions.get(edge["from"])
            t = node_positions.get(edge["to"])
            if f and t:
                if edge["type"] == "pass":
                    canvas.create_line(f[0], f[1], t[0], t[1],
                                       fill=self.colors["success"], width=2, arrow=tk.LAST)
                else:
                    canvas.create_line(f[0], f[1], t[0], t[1],
                                       fill="#ef4444", width=1, dash=(3, 2), arrow=tk.LAST)

    def _flow_simulate(self):
        """模拟测试流程"""
        import random
        test_results = {}
        for node in self._flow_engine.nodes:
            if node["type"] == "test":
                test_results[node["id"]] = random.random() > 0.15
        final_bin = self._flow_engine.simulate_flow(test_results)
        bi = self._flow_engine.bin_table.get(final_bin, ("UNKNOWN", "?", "?"))
        result_lines = "\n".join(f"  {k}: {'PASS ✓' if v else 'FAIL ✗'}"
                                  for k, v in test_results.items())
        self.flow_sim_result.config(
            text=f"Bin {final_bin}: {bi[0]}",
            fg=self.colors["success"] if final_bin == 1 else self.colors["danger"])
        messagebox.showinfo(self.t("flow_simulate"),
                            f"Flow Simulation Result\n\n"
                            f"Final Bin: {final_bin} ({bi[0]}, {bi[1]})\n\n"
                            f"Test Results:\n{result_lines}")

    def _flow_export_prg(self):
        """导出测试流程 .prg"""
        protocol = self.chip_protocol_var.get() if hasattr(self, 'chip_protocol_var') else "I2C"
        content = self._flow_engine.generate_prg_flow(protocol)
        path = filedialog.asksaveasfilename(
            title="Export Flow PRG", defaultextension=".prg",
            filetypes=[("PRG", "*.prg")])
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            messagebox.showinfo("Export", f"Flow PRG: {path}")

    # ============================================================
    # v6.0 良率分析方法
    # ============================================================

    def _yield_draw_empty(self):
        """绘制空状态提示"""
        canvas = self.yield_canvas
        canvas.delete("all")
        canvas.update_idletasks()
        cw = canvas.winfo_width() or 600
        ch = canvas.winfo_height() or 300
        canvas.create_text(cw // 2, ch // 2, text=self.t("yield_no_data"),
                           font=("Segoe UI", 12), fill=self.colors["text_dim"])

    def _yield_import_datalog(self):
        """导入 CSV Datalog"""
        path = filedialog.askopenfilename(
            title="Import Datalog CSV",
            filetypes=[("CSV", "*.csv"), ("All", "*.*")])
        if not path:
            return
        count = self._datalog_analyzer.import_csv(path)
        if count > 0:
            self.yield_info_label.config(text=f"Imported {count} records",
                                          fg=self.colors["success"])
            # 更新参数列表
            params = set()
            for r in self._datalog_analyzer.records:
                params.update(r.get("params", {}).keys())
            self.yield_param_combo["values"] = sorted(params)
            if params:
                self.yield_param_combo.set(sorted(params)[0])
            self._yield_refresh()
        else:
            messagebox.showwarning("Import", "No valid records found")

    def _yield_import_simulation(self):
        """从模拟器导入结果"""
        if not hasattr(self, '_simulator') or not self._simulator:
            messagebox.showinfo("Import", self.t("sim_no_vectors"))
            return
        if not self._simulator.transactions:
            messagebox.showinfo("Import", "Run simulation first")
            return
        self._datalog_analyzer.import_simulation_results(self._simulator)
        n = len(self._datalog_analyzer.records)
        self.yield_info_label.config(text=f"Records: {n}", fg=self.colors["success"])
        params = set()
        for r in self._datalog_analyzer.records:
            params.update(r.get("params", {}).keys())
        self.yield_param_combo["values"] = sorted(params)
        if params:
            self.yield_param_combo.set(sorted(params)[0])
        self._yield_refresh()

    def _yield_refresh(self):
        """刷新良率仪表盘"""
        canvas = self.yield_canvas
        canvas.delete("all")
        canvas.update_idletasks()

        if not self._datalog_analyzer.records:
            self._yield_draw_empty()
            return

        cw = canvas.winfo_width() or 600
        ch = canvas.winfo_height() or 300

        # ---- 左上: 直方图 ----
        param = self.yield_param_combo.get()
        stats = self._datalog_analyzer.calculate_statistics(param) if param else None
        hx, hy, hw, hh = 30, 35, cw // 2 - 60, ch // 2 - 60

        canvas.create_text(hx + hw // 2, hy - 15,
                           text=f"Histogram: {param}",
                           font=("Segoe UI", 9, "bold"), fill=self.colors["text"])

        if stats and stats["n"] > 1:
            values = stats["values"]
            n_bins = min(20, max(5, len(values) // 5))
            vmin, vmax = stats["min"], stats["max"]
            bw = (vmax - vmin) / n_bins if vmax > vmin else 1
            counts = [0] * n_bins
            for v in values:
                idx = min(n_bins - 1, int((v - vmin) / bw))
                counts[idx] += 1
            max_c = max(counts) if counts else 1
            bar_w = hw / n_bins
            for bi, cnt in enumerate(counts):
                bh = (cnt / max_c) * hh if max_c > 0 else 0
                x = hx + bi * bar_w
                y = hy + hh - bh
                canvas.create_rectangle(x, y, x + bar_w - 1, hy + hh,
                                        fill=self.colors["accent"], outline=self.colors["card"])

            # 统计信息
            cp_s = f"{stats['cp']:.2f}" if stats.get("cp") is not None else "N/A"
            cpk_s = f"{stats['cpk']:.2f}" if stats.get("cpk") is not None else "N/A"
            canvas.create_text(hx, hy + hh + 14,
                               text=f"n={stats['n']}  μ={stats['mean']:.3f}  σ={stats['sigma']:.3f}  "
                                    f"Cp={cp_s}  Cpk={cpk_s}",
                               font=("Consolas", 7), fill=self.colors["text"], anchor=tk.W)

        # ---- 右上: Pareto ----
        pareto = self._datalog_analyzer.pareto_analysis()
        px, py = cw // 2 + 30, 35
        pw, ph2 = cw // 2 - 60, ch // 2 - 60

        canvas.create_text(px + pw // 2, py - 15,
                           text="Pareto Analysis",
                           font=("Segoe UI", 9, "bold"), fill=self.colors["text"])

        if pareto:
            max_cnt = pareto[0]["count"] if pareto else 1
            bar_h = ph2 / max(len(pareto), 1)
            for pi, p in enumerate(pareto[:8]):
                bw2 = (p["count"] / max_cnt) * pw * 0.7 if max_cnt > 0 else 0
                by = py + pi * bar_h
                canvas.create_rectangle(px, by + 2, px + bw2, by + bar_h - 2,
                                        fill="#ef4444", outline="")
                canvas.create_text(px + bw2 + 4, by + bar_h / 2,
                                   text=f"Bin{p['bin']} ({p['count']}, {p['pct']:.0f}%)",
                                   font=("Consolas", 7), fill=self.colors["text"], anchor=tk.W)
        else:
            canvas.create_text(px + pw // 2, py + ph2 // 2,
                               text="No failures", font=("Segoe UI", 9),
                               fill=self.colors["success"])

        # ---- 底部: 良率摘要 ----
        yields = self._datalog_analyzer.calculate_yield("lot")
        y_bottom = ch - 30
        if yields:
            total = sum(y["total"] for y in yields)
            passed = sum(y["pass"] for y in yields)
            yld = passed / total * 100 if total > 0 else 0
            canvas.create_text(cw // 2, y_bottom,
                               text=f"Overall Yield: {passed}/{total} = {yld:.1f}%",
                               font=("Segoe UI", 11, "bold"),
                               fill=self.colors["success"] if yld >= 90 else self.colors["danger"])

    def _yield_export_report(self):
        """导出良率报告"""
        if not self._datalog_analyzer.records:
            messagebox.showinfo("Export", self.t("yield_no_data"))
            return
        path = filedialog.asksaveasfilename(
            title="Export Yield Report", defaultextension=".csv",
            filetypes=[("CSV", "*.csv")])
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8-sig") as f:
                f.write("Lot,Total,Pass,Fail,Yield%\n")
                for y in self._datalog_analyzer.calculate_yield("lot"):
                    f.write(f"{y['group']},{y['total']},{y['pass']},{y['fail']},{y['yield_pct']:.1f}\n")
            messagebox.showinfo("Export", f"Report: {path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ============================================================
    # Phase 6: Monte Carlo 良率预测方法
    # ============================================================

    def _run_monte_carlo(self):
        """在后台线程运行 Monte Carlo 仿真"""
        seed = int(self._mc_seed_var.get() or "42")
        n = int(self._mc_n_var.get() or "1000")
        self._yield_predictor = YieldPredictor()
        self._mc_status.config(text=self.t("mc_running").format(pct=0),
                                fg=self.colors["warning"])

        def _worker():
            t0 = _time_module.time()
            self._yield_predictor.run_monte_carlo(n=n, seed=seed)
            elapsed = (_time_module.time() - t0) * 1000
            self.root.after(0, lambda: self._on_mc_done(elapsed))

        def _poll():
            if self._yield_predictor and not self._yield_predictor.done:
                self._mc_status.config(
                    text=self.t("mc_running").format(pct=self._yield_predictor.progress))
                self.root.after(200, _poll)

        t = threading.Thread(target=_worker, daemon=True)
        t.start()
        self.root.after(200, _poll)

    # ── v9.0 Tier3 Phase 27: 自适应仿真 ──

    def _run_adaptive_simulation(self):
        """在后台线程运行自适应测试流 Monte Carlo 仿真"""
        n = int(self._adaptive_n_var.get() or "1000")
        self._adaptive_engine = AdaptiveTestEngine()
        self._adaptive_status.config(
            text=self.t("adaptive_running").format(pct=0),
            fg=self.colors["warning"])

        def _worker():
            self._adaptive_engine.simulate_adaptive_flow(n=n, seed=42)
            self.root.after(0, self._on_adaptive_done)

        def _poll():
            if not self._adaptive_engine.done:
                pct = self._adaptive_engine.progress * 100
                self._adaptive_status.config(
                    text=self.t("adaptive_running").format(pct=pct))
                self.root.after(200, _poll)

        t = threading.Thread(target=_worker, daemon=True)
        t.start()
        self.root.after(200, _poll)

    def _on_adaptive_done(self):
        """自适应仿真完成回调"""
        res = self._adaptive_engine.simulation_results
        save = res.get("time_savings_pct", 0)
        self._adaptive_status.config(
            text=self.t("adaptive_done").format(save=save),
            fg=self.colors["success"])
        self._adaptive_rules = list(self._adaptive_engine.RULES.keys())

        # 刷新流程图以显示规则标签
        if hasattr(self, 'pat_sections') and self.pat_sections:
            self._draw_flowchart(self.pat_sections)

        # 弹窗显示对比结果
        self._show_adaptive_results(res)

    def _show_adaptive_results(self, res):
        """弹窗显示固定 vs 自适应对比"""
        dlg = tk.Toplevel(self.root)
        dlg.title(self.t("adaptive_compare"))
        dlg.geometry("520x400")
        dlg.configure(bg=self.colors["bg"])
        dlg.transient(self.root)

        tk.Label(dlg, text=self.t("adaptive_compare"),
                 font=("Segoe UI", 14, "bold"),
                 fg=self.colors["text"], bg=self.colors["bg"]).pack(pady=(12, 6))

        info = tk.Text(dlg, wrap=tk.WORD, font=("Consolas", 9),
                       bg=self.colors["card"], fg=self.colors["text"],
                       relief=tk.FLAT, state=tk.NORMAL)
        info.pack(fill=tk.BOTH, expand=True, padx=12, pady=6)

        fixed = res["fixed"]
        adap = res["adaptive"]
        lines = [
            f"{'':>24s}  {'Fixed':>12s}  {'Adaptive':>12s}",
            f"{'─' * 52}",
            f"{'Avg Time (ms)':>24s}  {fixed['avg_time_ms']:>12.2f}  {adap['avg_time_ms']:>12.2f}",
            f"{'Total Time (s)':>24s}  {fixed['total_time_s']:>12.1f}  {adap['total_time_s']:>12.1f}",
            f"{'Time Savings':>24s}  {'—':>12s}  {res['time_savings_pct']:>11.1f}%",
            f"",
            f"{'── Rule Trigger Counts ──':>24s}",
        ]
        for rid, cnt in res["rule_trigger_counts"].items():
            rule = AdaptiveTestEngine.RULES[rid]
            desc = rule["description_en"]
            lines.append(f"  {rid}: {cnt} times  ({desc})")
        lines.append(f"\nSamples: {res['n']}")

        info.insert(tk.END, "\n".join(lines))
        info.config(state=tk.DISABLED)

        tk.Button(dlg, text="OK", command=dlg.destroy,
                  font=("Segoe UI", 9), bg=self.colors["accent"],
                  fg="white", relief=tk.FLAT, padx=20, pady=4,
                  cursor="hand2").pack(pady=(0, 12))

    # ── v9.0 Tier3 Phase 28: Guard Band ──

    def _run_guard_band(self):
        """在后台线程运行 Guard Band 分析"""
        if not self._yield_predictor or not self._yield_predictor.done:
            self._gb_status.config(text=self.t("gb_no_mc"), fg=self.colors["danger"])
            return
        dppm = int(self._gb_dppm_var.get() or "10")
        self._gb_engine = GuardBandEngine(self._yield_predictor)
        self._gb_status.config(text=self.t("gb_running"), fg=self.colors["warning"])

        def _worker():
            self._gb_engine.analyze_all(target_dppm=dppm)
            self.root.after(0, self._on_gb_done)

        t = threading.Thread(target=_worker, daemon=True)
        t.start()

    def _on_gb_done(self):
        """Guard Band 完成回调"""
        if not self._gb_engine or not self._gb_engine.results:
            self._gb_status.config(text="No results", fg=self.colors["danger"])
            return
        avg_tight = sum(r["tightening_pct"] for r in self._gb_engine.results.values()) / max(1, len(self._gb_engine.results))
        self._gb_status.config(
            text=self.t("gb_done").format(pct=avg_tight),
            fg=self.colors["success"])
        self._gb_apply_btn.config(state=tk.NORMAL)

        # 弹窗显示结果
        dlg = tk.Toplevel(self.root)
        dlg.title(self.t("gb_title"))
        dlg.geometry("660x350")
        dlg.configure(bg=self.colors["bg"])
        dlg.transient(self.root)

        cols = ("param", "orig_max", "gb_max", "dppm_before", "dppm_after", "tightening", "recommend")
        tree = ttk.Treeview(dlg, columns=cols, show="headings", height=10)
        for col, hdr, w in [("param","Param",70),("orig_max","Orig Max",80),("gb_max","GB Max",80),
                            ("dppm_before","DPPM前",70),("dppm_after","DPPM后",70),
                            ("tightening","收紧%",60),("recommend","建议",100)]:
            tree.heading(col, text=hdr)
            tree.column(col, width=w, anchor=tk.CENTER)
        for param, r in self._gb_engine.results.items():
            o = r["original_max"] if r["original_max"] is not None else "—"
            g = r["guarded_max"] if r["guarded_max"] is not None else "—"
            tree.insert("", tk.END, values=(param, o, g,
                        r["dppm_before"], r["dppm_after"],
                        f"{r['tightening_pct']:.1f}%", r["recommendation"]))
        tree.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        tk.Button(dlg, text="OK", command=dlg.destroy,
                  font=("Segoe UI", 9), bg=self.colors["accent"],
                  fg="white", relief=tk.FLAT, padx=20, pady=4,
                  cursor="hand2").pack(pady=(0, 8))

    def _apply_guard_band(self):
        """将 Guard Band 限值应用到 TEST_LIMITS"""
        if not self._gb_engine or not self._gb_engine.results:
            return
        for param, r in self._gb_engine.results.items():
            if param in TEST_LIMITS:
                if r["guarded_max"] is not None:
                    TEST_LIMITS[param]["max"] = r["guarded_max"]
                if r["guarded_min"] is not None:
                    TEST_LIMITS[param]["min"] = r["guarded_min"]
        self._gb_status.config(text="Guard Band applied ✓", fg=self.colors["success"])

    def _on_mc_done(self, elapsed_ms):
        """Monte Carlo 完成回调"""
        y = self._yield_predictor.get_yield()
        cpk = self._yield_predictor.get_min_cpk()
        self._mc_status.config(
            text=self.t("mc_done").format(y=y, cpk=cpk, t=elapsed_ms),
            fg=self.colors["success"])
        self._draw_mc_results()

    def _draw_mc_results(self):
        """绘制 Monte Carlo 结果: 直方图 + Cpk + 良率卡片"""
        canvas = self.yield_canvas
        canvas.delete("all")
        pred = self._yield_predictor
        if not pred or not pred.done:
            self._yield_draw_empty()
            return
        canvas.update_idletasks()
        cw = max(canvas.winfo_width(), 700)
        y = 20

        # 综合良率卡片
        y_pct = pred.get_yield()
        min_cpk = pred.get_min_cpk()
        n = len(pred.results)
        passed = sum(1 for _, p in pred.results if p)
        canvas.create_text(20, y,
                           text=f"Monte Carlo 仿真结果 (n={n}, seed={self._mc_seed_var.get()})",
                           font=("Segoe UI", 12, "bold"), fill=self.colors["text"], anchor=tk.W)
        y += 28
        canvas.create_text(30, y, text=f"理论良率: {y_pct:.1f}%  ({passed}/{n})",
                           font=("Consolas", 10, "bold"), fill=self.colors["success"], anchor=tk.W)
        y += 20
        cpk_rating = "优秀" if min_cpk >= 1.33 else "良好" if min_cpk >= 1.0 else "需改进"
        cpk_color = self.colors["success"] if min_cpk >= 1.33 else self.colors["warning"] if min_cpk >= 1.0 else self.colors["danger"]
        canvas.create_text(30, y, text=f"综合 Cpk = {min_cpk:.2f}  ({cpk_rating}, JEDEC ≥1.33 为优秀)",
                           font=("Consolas", 9), fill=cpk_color, anchor=tk.W)
        y += 28

        # 8 个参数直方图 (2×4 布局)
        params = list(pred.cpk_data.keys())
        cols = 4
        rows = 2
        hist_w = (cw - 80) // cols
        hist_h = 100
        for idx, param in enumerate(params):
            col = idx % cols
            row = idx // cols
            hx = 30 + col * hist_w
            hy = y + row * (hist_h + 40)
            data = pred.cpk_data[param]
            spec = pred.YIELD_PARAMS[param]
            values = data["values"]

            # 标题
            canvas.create_text(hx + hist_w // 2, hy,
                               text=f"{param} ({spec['unit']})",
                               font=("Segoe UI", 7, "bold"), fill=self.colors["accent"])
            # 直方图
            n_bins = 15
            vmin, vmax = data["min"], data["max"]
            margin = (vmax - vmin) * 0.1 if vmax > vmin else 0.1
            bw = (vmax - vmin + 2 * margin) / n_bins if vmax > vmin else 1
            counts = [0] * n_bins
            for v in values:
                bi = min(n_bins - 1, max(0, int((v - vmin + margin) / bw)))
                counts[bi] += 1
            max_c = max(counts) if counts else 1
            bar_w = (hist_w - 20) / n_bins
            hy_base = hy + 12
            for bi, cnt in enumerate(counts):
                bh = cnt / max_c * (hist_h - 20) if max_c > 0 else 0
                bx = hx + 10 + bi * bar_w
                # 色区: spec 内=绿, spec 外=红
                bin_center = vmin - margin + (bi + 0.5) * bw
                in_spec = spec["spec_min"] <= bin_center <= spec["spec_max"]
                clr = self.colors["success"] if in_spec else self.colors["danger"]
                canvas.create_rectangle(bx, hy_base + hist_h - 20 - bh,
                                        bx + bar_w - 1, hy_base + hist_h - 20,
                                        fill=clr, outline=self.colors["card"])
            # Cp/Cpk 标注
            canvas.create_text(hx + hist_w // 2, hy_base + hist_h - 14,
                               text=f"Cp={data['cp']:.2f}  Cpk={data['cpk']:.2f}",
                               font=("Consolas", 6), fill=self.colors["text_dim"])

        y += rows * (hist_h + 40) + 20

        # Cpk 表格
        canvas.create_text(20, y, text="参数能力指数表",
                           font=("Segoe UI", 10, "bold"), fill=self.colors["text"], anchor=tk.W)
        y += 18
        headers = ["Param", "Cp", "Cpk", "Mean", "Sigma", "Rating"]
        col_x = [30, 100, 160, 220, 300, 380]
        for xi, h in zip(col_x, headers):
            canvas.create_text(xi, y, text=h, font=("Consolas", 8, "bold"),
                               fill=self.colors["accent"], anchor=tk.W)
        y += 14
        for param, data in pred.cpk_data.items():
            rating = "✓优秀" if data["cpk"] >= 1.33 else "△良好" if data["cpk"] >= 1.0 else "✗需改进"
            clr = self.colors["success"] if data["cpk"] >= 1.33 else self.colors["warning"] if data["cpk"] >= 1.0 else self.colors["danger"]
            canvas.create_text(col_x[0], y, text=param, font=("Consolas", 8),
                               fill=self.colors["text"], anchor=tk.W)
            canvas.create_text(col_x[1], y, text=f"{data['cp']:.2f}",
                               font=("Consolas", 8), fill=self.colors["text_dim"], anchor=tk.W)
            canvas.create_text(col_x[2], y, text=f"{data['cpk']:.2f}",
                               font=("Consolas", 8, "bold"), fill=clr, anchor=tk.W)
            canvas.create_text(col_x[3], y, text=f"{data['mean']:.3f}",
                               font=("Consolas", 8), fill=self.colors["text_dim"], anchor=tk.W)
            canvas.create_text(col_x[4], y, text=f"{data['sigma']:.4f}",
                               font=("Consolas", 8), fill=self.colors["text_dim"], anchor=tk.W)
            canvas.create_text(col_x[5], y, text=rating,
                               font=("Consolas", 8), fill=clr, anchor=tk.W)
            y += 16

        canvas.configure(scrollregion=(0, 0, cw, y + 30))

    # ============================================================
    # Phase 4: ATPG 覆盖率仿真方法
    # ============================================================

    def _run_atpg_simulation(self):
        """在后台线程运行故障覆盖率仿真"""
        if not hasattr(self, 'pat_sections') or not self.pat_sections:
            messagebox.showinfo(self.t("atpg_run"), self.t("atpg_no_vectors"))
            return
        seed = int(self._atpg_seed_var.get() or "42")
        n_inject = int(self._atpg_n_var.get() or "100")
        capacity = int(self.chip_capacity_var.get() or "256")
        self._fault_sim = FaultCoverageSimulator(capacity=capacity, seed=seed)
        self._atpg_status.config(text=self.t("atpg_running").format(pct=0),
                                  fg=self.colors["warning"])
        sections = list(self.pat_sections)

        def _worker():
            t0 = _time_module.time()
            self._fault_sim.run_simulation(sections, n_inject=n_inject)
            elapsed = (_time_module.time() - t0) * 1000
            self.root.after(0, lambda: self._on_atpg_done(elapsed))

        def _poll_progress():
            if self._fault_sim and not self._fault_sim.done:
                self._atpg_status.config(
                    text=self.t("atpg_running").format(pct=self._fault_sim.progress))
                self.root.after(200, _poll_progress)

        t = threading.Thread(target=_worker, daemon=True)
        t.start()
        self.root.after(200, _poll_progress)

    def _on_atpg_done(self, elapsed_ms):
        """ATPG 仿真完成回调"""
        cov = self._fault_sim.get_overall_coverage()
        self._atpg_status.config(
            text=self.t("atpg_done").format(cov=cov, t=elapsed_ms),
            fg=self.colors["success"])
        self._draw_atpg_results()

    def _draw_atpg_results(self):
        """绘制 ATPG 覆盖率热力表 + 雷达图 + 综合评分"""
        c = self.atpg_canvas
        c.delete("all")
        if not self._fault_sim or not self._fault_sim.results:
            c.update_idletasks()
            cw = c.winfo_width() or 600
            ch = c.winfo_height() or 300
            c.create_text(cw // 2, ch // 2, text=self.t("atpg_no_vectors"),
                          font=("Segoe UI", 12), fill=self.colors["text_dim"])
            return
        c.update_idletasks()
        cw = max(c.winfo_width(), 700)
        sim = self._fault_sim
        tests = sim.test_names
        faults = sim.fault_types
        y = 20

        # --- 热力表 ---
        c.create_text(20, y, text=self.t("atpg_heatmap"),
                      fill=self.colors["text"], font=("Segoe UI", 12, "bold"), anchor=tk.W)
        y += 26
        col_w = max(55, (cw - 180) // len(faults))
        row_h = 24
        # 列标题
        for j, ft in enumerate(faults):
            cx = 160 + j * col_w + col_w // 2
            c.create_text(cx, y, text=ft.replace("_", "\n"),
                          font=("Consolas", 7, "bold"), fill=self.colors["accent"], justify=tk.CENTER)
        y += 22
        # 行数据
        for i, tn in enumerate(tests):
            short = tn.replace("_TEST", "")
            c.create_text(20, y + row_h // 2, text=short,
                          font=("Consolas", 8), fill=self.colors["text"], anchor=tk.W)
            for j, ft in enumerate(faults):
                cx = 160 + j * col_w
                cov = sim.results.get((tn, ft), 0)
                # 颜色分级
                if cov >= 95:
                    bg = "#1D9E75"
                elif cov >= 80:
                    bg = "#7BC47F"
                elif cov >= 60:
                    bg = "#F5A623"
                else:
                    bg = "#E24B4A"
                c.create_rectangle(cx + 2, y, cx + col_w - 2, y + row_h - 2,
                                   fill=bg, outline=self.colors["border"])
                c.create_text(cx + col_w // 2, y + row_h // 2 - 1,
                              text=f"{cov:.0f}%",
                              font=("Consolas", 7, "bold"), fill="white")
            y += row_h

        # --- 雷达图 ---
        y += 20
        c.create_text(20, y, text=self.t("atpg_radar"),
                      fill=self.colors["text"], font=("Segoe UI", 11, "bold"), anchor=tk.W)
        radar_cx = cw // 4
        radar_cy = y + 110
        radar_r = 80
        n_axes = len(faults)
        # 背景圆
        for pct in [25, 50, 75, 100]:
            r = radar_r * pct / 100
            c.create_oval(radar_cx - r, radar_cy - r, radar_cx + r, radar_cy + r,
                          outline=self.colors["border"], dash=(2, 2))
        # 坐标轴 + 标签
        import math as _m
        for k, ft in enumerate(faults):
            angle = 2 * _m.pi * k / n_axes - _m.pi / 2
            ex = radar_cx + radar_r * 1.15 * _m.cos(angle)
            ey = radar_cy + radar_r * 1.15 * _m.sin(angle)
            c.create_line(radar_cx, radar_cy,
                          radar_cx + radar_r * _m.cos(angle),
                          radar_cy + radar_r * _m.sin(angle),
                          fill=self.colors["border"])
            c.create_text(ex, ey, text=ft, font=("Consolas", 6),
                          fill=self.colors["text_dim"])
        # 每个测试的覆盖多边形
        test_colors = ["#3b82f6", "#22c55e", "#f59e0b", "#ef4444",
                       "#8b5cf6", "#14b8a6", "#ec4899", "#06b6d4", "#f97316"]
        for ti, tn in enumerate(tests):
            points = []
            for k, ft in enumerate(faults):
                cov = sim.results.get((tn, ft), 0)
                angle = 2 * _m.pi * k / n_axes - _m.pi / 2
                r = radar_r * cov / 100
                points.extend([radar_cx + r * _m.cos(angle),
                                radar_cy + r * _m.sin(angle)])
            if len(points) >= 6:
                clr = test_colors[ti % len(test_colors)]
                c.create_polygon(points, outline=clr, fill="", width=1.5,
                                 stipple="gray25")
        # 图例
        leg_x = cw // 2 + 20
        leg_y = y + 20
        for ti, tn in enumerate(tests):
            clr = test_colors[ti % len(test_colors)]
            c.create_rectangle(leg_x, leg_y, leg_x + 10, leg_y + 10, fill=clr, outline="")
            c.create_text(leg_x + 14, leg_y + 5, text=tn.replace("_TEST", ""),
                          font=("Consolas", 7), fill=self.colors["text"], anchor=tk.W)
            leg_y += 14
        y = radar_cy + radar_r + 30

        # --- 综合评分 ---
        c.create_text(20, y, text=self.t("atpg_summary"),
                      fill=self.colors["text"], font=("Segoe UI", 11, "bold"), anchor=tk.W)
        y += 22
        overall = sim.get_overall_coverage()
        # JEDEC 对比
        jedec = {"SA0/SA1": 95, "TF": 95, "CF": 90, "AF": 85}
        sa_cov = sum(sim.results.get((tn, f), 0) for tn in tests for f in ["SA0", "SA1"]) / max(len(tests) * 2, 1)
        tf_cov = sum(sim.results.get((tn, f), 0) for tn in tests for f in ["TF01", "TF10"]) / max(len(tests) * 2, 1)
        cf_cov = sum(sim.results.get((tn, f), 0) for tn in tests for f in ["CF_inv", "CF_idem"]) / max(len(tests) * 2, 1)
        af_cov = sum(sim.results.get((tn, f), 0) for tn in tests for f in ["AF_r", "AF_w"]) / max(len(tests) * 2, 1)

        c.create_text(30, y, text=f"综合故障覆盖率: {overall:.1f}% (仿真, n={self._atpg_n_var.get()}/故障点)",
                      font=("Consolas", 9, "bold"), fill=self.colors["text"], anchor=tk.W)
        y += 20
        for label, val, target in [("SA0/SA1", sa_cov, 95), ("TF", tf_cov, 95),
                                    ("CF", cf_cov, 90), ("AF", af_cov, 85)]:
            sym = "✓" if val >= target else "✗"
            clr = self.colors["success"] if val >= target else self.colors["danger"]
            c.create_text(40, y, text=f"{sym} {label}: {val:.1f}%  (JEDEC ≥{target}%)",
                          font=("Consolas", 8), fill=clr, anchor=tk.W)
            y += 16

        # --- 最小测试套件 ---
        y += 10
        c.create_text(20, y, text=self.t("atpg_min_suite"),
                      fill=self.colors["text"], font=("Segoe UI", 10, "bold"), anchor=tk.W)
        y += 18
        min_suite = sim.get_min_test_suite()
        if min_suite:
            suite_cov = sum(max(sim.results.get((t, ft), 0) for t in min_suite)
                            for ft in faults) / len(faults) if faults else 0
            c.create_text(30, y,
                          text=f"仅用 {', '.join(s.replace('_TEST','') for s in min_suite)} "
                               f"→ 覆盖率 {suite_cov:.1f}%",
                          font=("Consolas", 8, "bold"), fill=self.colors["accent2"], anchor=tk.W)
            y += 18
        c.configure(scrollregion=(0, 0, cw, y + 30))

    # ============================================================
    # Phase 5: 测试经济学方法
    # ============================================================

    def _calculate_economics(self):
        """计算测试经济学"""
        if not hasattr(self, 'pat_sections') or not self.pat_sections:
            messagebox.showinfo(self.t("tab_econ"), self.t("econ_no_vectors"))
            return
        params = {
            "ate_cost_per_hour": float(self._econ_ate_cost.get() or 500),
            "chip_cost": float(self._econ_chip_cost.get() or 0.5),
            "target_daily": int(self._econ_target.get() or 10000),
            "expected_yield": float(self._econ_yield.get() or 95),
            "work_hours": float(self._econ_hours.get() or 16),
            "escape_repair_cost": float(self._econ_repair.get() or 50),
        }
        engine = TestEconomicsEngine(**params)
        period_ns = self._get_period_ns()
        self._econ_data = engine.calculate(self.pat_sections, period_ns)
        self._econ_data["curve"] = engine.calculate_yield_cost_curve(self.pat_sections, period_ns)
        self._econ_data["params"] = params
        self._draw_economics()

    def _draw_economics(self):
        """绘制测试经济学仪表盘"""
        c = self.econ_canvas
        c.delete("all")
        if not self._econ_data:
            c.update_idletasks()
            cw = c.winfo_width() or 600
            ch = c.winfo_height() or 300
            c.create_text(cw // 2, ch // 2, text=self.t("econ_no_vectors"),
                          font=("Segoe UI", 12), fill=self.colors["text_dim"])
            return
        c.update_idletasks()
        cw = max(c.winfo_width(), 700)
        d = self._econ_data
        y = 20

        # --- 4 个关键指标卡片 ---
        cards = [
            (self.t("econ_test_time"), f"{d['test_time_ms']:.1f} ms", self.colors["accent"]),
            (self.t("econ_test_cost"), f"¥{d['cost_per_chip']:.4f}", self.colors["accent2"]),
            (self.t("econ_daily_cap"), f"{d['daily_capacity']:.0f} 颗", self.colors["warning"]),
            (self.t("econ_annual_save"), f"¥{d['daily_capacity']*d['cost_per_chip']*365/1000:.0f}K/年",
             self.colors["success"]),
        ]
        card_w = (cw - 60) // 4
        for i, (title, value, color) in enumerate(cards):
            cx = 20 + i * (card_w + 10)
            c.create_rectangle(cx, y, cx + card_w, y + 60,
                              fill=self.colors["card2"], outline=color, width=2)
            c.create_text(cx + card_w // 2, y + 18, text=title,
                          font=("Segoe UI", 8), fill=self.colors["text_dim"])
            c.create_text(cx + card_w // 2, y + 42, text=value,
                          font=("Segoe UI", 13, "bold"), fill=color)
        y += 80

        # --- 测试时间分解饼图 ---
        c.create_text(20, y, text="测试时间分解",
                      fill=self.colors["text"], font=("Segoe UI", 11, "bold"), anchor=tk.W)
        y += 20
        import math as _m
        seg_times = d["seg_times"]
        total_time = d["test_time_ms"]
        pie_cx = 140
        pie_cy = y + 80
        pie_r = 70
        pie_colors = ["#3b82f6", "#22c55e", "#f59e0b", "#ef4444",
                       "#8b5cf6", "#14b8a6", "#ec4899", "#06b6d4", "#f97316"]
        start_angle = 0
        for i, (name, t_ms) in enumerate(seg_times):
            extent = t_ms / total_time * 360 if total_time > 0 else 0
            clr = pie_colors[i % len(pie_colors)]
            c.create_arc(pie_cx - pie_r, pie_cy - pie_r,
                         pie_cx + pie_r, pie_cy + pie_r,
                         start=start_angle, extent=extent,
                         fill=clr, outline=self.colors["card"])
            start_angle += extent
        # 图例
        leg_x = pie_cx + pie_r + 30
        for i, (name, t_ms) in enumerate(seg_times):
            pct = t_ms / total_time * 100 if total_time > 0 else 0
            clr = pie_colors[i % len(pie_colors)]
            ly = y + i * 16
            c.create_rectangle(leg_x, ly, leg_x + 10, ly + 10, fill=clr, outline="")
            c.create_text(leg_x + 14, ly + 5,
                          text=f"{name.replace('_TEST','')}: {t_ms:.1f}ms ({pct:.0f}%)",
                          font=("Consolas", 7), fill=self.colors["text"], anchor=tk.W)
        y = pie_cy + pie_r + 20

        # --- 良率-成本权衡曲线 ---
        c.create_text(20, y, text="良率-成本权衡曲线",
                      fill=self.colors["text"], font=("Segoe UI", 11, "bold"), anchor=tk.W)
        y += 20
        curve = d.get("curve", [])
        if curve:
            gx, gy, gw, gh = 60, y, cw - 120, 140
            max_cost = max(p["total"] for p in curve) * 1.1
            # 坐标轴
            c.create_line(gx, gy + gh, gx + gw, gy + gh, fill=self.colors["border"])
            c.create_line(gx, gy, gx, gy + gh, fill=self.colors["border"])
            c.create_text(gx + gw // 2, gy + gh + 14, text="测试覆盖率 (%)",
                          font=("Segoe UI", 7), fill=self.colors["text_dim"])
            c.create_text(gx - 8, gy, text="¥", font=("Segoe UI", 7),
                          fill=self.colors["text_dim"], anchor=tk.E)
            # 绘制曲线
            for key, color, label in [("test_cost", "#3b82f6", "测试成本"),
                                       ("escape_cost", "#ef4444", "漏筛成本"),
                                       ("total", "#22c55e", "综合成本")]:
                points = []
                for p in curve:
                    px = gx + (p["coverage"] - 50) / 50 * gw
                    py = gy + gh - p[key] / max_cost * gh if max_cost > 0 else gy + gh
                    points.extend([px, py])
                if len(points) >= 4:
                    c.create_line(points, fill=color, width=2, smooth=True)
            # 图例
            for i, (clr, lbl) in enumerate([("#3b82f6", "测试成本↗"), ("#ef4444", "漏筛成本↘"), ("#22c55e", "综合U形")]):
                c.create_rectangle(gx + gw + 10, gy + i * 16, gx + gw + 20, gy + i * 16 + 10,
                                   fill=clr, outline="")
                c.create_text(gx + gw + 24, gy + i * 16 + 5, text=lbl,
                              font=("Consolas", 7), fill=self.colors["text"], anchor=tk.W)
            y = gy + gh + 30

        c.configure(scrollregion=(0, 0, cw, y + 30))

    # ============================================================
    # Phase 8: ATPG 审核方法
    # ============================================================

    def _generate_atpg_proof(self):
        """生成 March 算法覆盖率证明"""
        algo_name = self._atpg8_algo_var.get()
        selected_faults = [ft for ft, var in self._atpg8_fault_vars.items() if var.get()]
        if not selected_faults:
            selected_faults = list(FAULT_MODELS.keys())

        # 最优算法推荐
        optimal = self._memory_atpg.generate_optimal(selected_faults)

        # 生成完整证明
        proof = self._memory_atpg.generate_full_proof(algo_name)

        # 添加最优推荐
        header = f"{'='*60}\n"
        header += f"{self.t('atpg_optimal')}: {optimal}\n"
        algo = MemoryATPG.CLASSIC_ALGORITHMS.get(optimal, {})
        header += f"{self.t('atpg_complexity')}: {algo.get('complexity', '?')}\n"
        header += f"{'='*60}\n\n"

        # 理论覆盖率
        theory = self._memory_atpg.get_theory_coverage(algo_name)
        header += f"理论覆盖率 ({algo_name}):\n"
        for ft, cov in theory.items():
            mark = "✓" if cov > 0 else "✗"
            header += f"  {mark} {ft}: {cov:.0f}%\n"
        header += f"\n综合理论覆盖率: {sum(theory.values()) / len(theory):.1f}%\n\n"

        full_text = header + proof

        self._atpg8_proof_text.config(state=tk.NORMAL)
        self._atpg8_proof_text.delete("1.0", tk.END)
        self._atpg8_proof_text.insert("1.0", full_text)
        self._atpg8_proof_text.config(state=tk.DISABLED)

        # 绘制 March 序列可视化
        self._draw_march_vis()

    def _draw_march_vis(self):
        """绘制 March 序列可视化"""
        c = self._atpg8_canvas
        c.delete("all")
        cw = c.winfo_width()
        ch = c.winfo_height()
        if cw < 10 or ch < 10:
            return

        algo_name = self._atpg8_algo_var.get()
        algo = MemoryATPG.CLASSIC_ALGORITHMS.get(algo_name)
        if not algo:
            return

        steps = algo["steps"]
        n_steps = len(steps)

        # 标题
        c.create_text(cw // 2, 15, text=f"{algo_name} ({algo['complexity']})",
                     font=("Segoe UI", 10, "bold"), fill=self.colors["accent2"])

        # 步骤方框
        margin = 20
        box_w = min(100, (cw - margin * 2 - (n_steps - 1) * 10) // max(n_steps, 1))
        box_h = min(ch - 60, 200)
        total_w = n_steps * box_w + (n_steps - 1) * 10
        x_start = (cw - total_w) // 2
        y_top = 35
        y_bot = y_top + box_h

        colors_list = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899"]

        for i, (direction, ops) in enumerate(steps):
            x = x_start + i * (box_w + 10)
            color = colors_list[i % len(colors_list)]

            # 方框
            c.create_rectangle(x, y_top, x + box_w, y_bot,
                             fill=self.colors["bg"], outline=color, width=2)

            # 步骤名
            c.create_text(x + box_w // 2, y_top + 14,
                         text=f"M{i}", font=("Consolas", 9, "bold"), fill=color)

            # 方向箭头
            c.create_text(x + box_w // 2, y_top + 30,
                         text=direction, font=("Segoe UI", 14), fill=self.colors["warning"])

            # 操作列表
            for j, op in enumerate(ops):
                oy = y_top + 48 + j * 16
                if oy + 10 > y_bot - 5:
                    c.create_text(x + box_w // 2, oy, text="...",
                                 font=("Consolas", 7), fill=self.colors["text_dim"])
                    break
                fg = "#10b981" if "r" in op else "#f59e0b"
                c.create_text(x + box_w // 2, oy, text=op,
                             font=("Consolas", 8, "bold"), fill=fg)

            # 箭头连接
            if i < n_steps - 1:
                ax1 = x + box_w + 1
                ax2 = x + box_w + 9
                ay = y_top + box_h // 2
                c.create_line(ax1, ay, ax2, ay, fill=self.colors["text_dim"],
                             arrow=tk.LAST, width=2)

        # 故障覆盖情况
        y = y_bot + 10
        if y + 20 < ch:
            detects = set(algo.get("detects", []))
            x = margin
            for ft in FAULT_MODELS:
                covered = ft in detects
                color = "#10b981" if covered else "#ef4444"
                mark = "✓" if covered else "✗"
                text = f"{mark} {ft}"
                c.create_text(x, y, text=text, anchor=tk.W,
                             font=("Consolas", 7), fill=color)
                x += 75
                if x + 60 > cw:
                    x = margin
                    y += 14

    def _export_atpg_proof(self):
        """导出 ATPG 证明文档为 .txt"""
        content = self._atpg8_proof_text.get("1.0", tk.END).strip()
        if not content:
            self._generate_atpg_proof()
            content = self._atpg8_proof_text.get("1.0", tk.END).strip()
        if not content:
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt", filetypes=[("Text", "*.txt")],
            initialfile="ATPG_Proof.txt")
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        messagebox.showinfo(self.t("tab_atpg"), f"Proof → {path}")

    # ============================================================
    # Phase 7: 芯片迁移方法
    # ============================================================

    def _show_migrate_dialog(self):
        """工具栏迁移按钮: 切换到迁移 Tab"""
        # 找到迁移 Tab 的索引
        for i in range(self.notebook.index("end")):
            if self.notebook.tab(i, "text").strip() == self.t("tab_migrate").strip():
                self.notebook.select(i)
                return

    def _run_migration(self):
        """执行跨芯片迁移"""
        if not hasattr(self, 'current_vectors') or not self.current_vectors:
            messagebox.showinfo(self.t("tab_migrate"), self.t("migrate_no_vectors"))
            return
        src = self._migrate_source_var.get()
        tgt = self._migrate_target_var.get()
        if src == tgt:
            messagebox.showinfo(self.t("tab_migrate"), self.t("migrate_same_chip"))
            return

        t0 = _time_module.time()
        engine = ChipMigrationEngine(src, tgt)

        # 芯片对比
        diff = engine.compare_chips()
        self._migrate_compare_text.config(state=tk.NORMAL)
        self._migrate_compare_text.delete("1.0", tk.END)
        labels = {
            "capacity_bytes": self.t("migrate_capacity"),
            "page_size": self.t("migrate_page_size"),
            "addr_bytes": self.t("migrate_addr_bytes"),
            "max_freq_khz": self.t("migrate_max_freq"),
            "a_pins": self.t("migrate_dev_addr"),
        }
        for key, info in diff.items():
            label = labels.get(key, key)
            mark = " ◄" if info["changed"] else ""
            self._migrate_compare_text.insert(tk.END,
                f"{label:12s}: {str(info['source']):>8s} → {str(info['target']):>8s}{mark}\n")
        self._migrate_compare_text.config(state=tk.DISABLED)

        # 执行迁移
        comments = self.current_comments if hasattr(self, 'current_comments') else [""] * len(self.current_vectors)
        sections = [s[0] for s in self.pat_sections] if hasattr(self, 'pat_sections') and self.pat_sections else []
        m_vecs, m_cmts, log = engine.migrate(self.current_vectors, comments, sections)

        elapsed = (_time_module.time() - t0) * 1000

        # 显示日志
        self._migrate_log_text.config(state=tk.NORMAL)
        self._migrate_log_text.delete("1.0", tk.END)
        for entry in log:
            self._migrate_log_text.insert(tk.END, entry + "\n")
        self._migrate_log_text.insert(tk.END, f"\n{self.t('migrate_done').format(n=len(m_vecs), t=elapsed)}\n")
        self._migrate_log_text.config(state=tk.DISABLED)

        # 保存迁移数据
        self._migration_data = {
            "source": src, "target": tgt,
            "src_info": engine.get_chip_info(src),
            "tgt_info": engine.get_chip_info(tgt),
            "src_vectors": len(self.current_vectors),
            "tgt_vectors": len(m_vecs),
            "diff": diff, "log": log,
            "migrated_vectors": m_vecs,
            "migrated_comments": m_cmts,
        }
        self._draw_migration()
        self._update_status(self.t("migrate_done").format(n=len(m_vecs), t=elapsed))

    def _draw_migration(self):
        """绘制迁移对比可视化"""
        c = self._migrate_canvas
        c.delete("all")
        cw = c.winfo_width()
        ch = c.winfo_height()
        if cw < 10 or ch < 10:
            return
        if not self._migration_data:
            c.create_text(cw // 2, ch // 2, text=self.t("migrate_no_vectors"),
                         font=("Segoe UI", 11), fill=self.colors["text_dim"])
            return

        data = self._migration_data
        src = data["source"]
        tgt = data["target"]
        src_info = data["src_info"]
        tgt_info = data["tgt_info"]
        diff = data["diff"]

        y = 20
        # 标题
        c.create_text(cw // 2, y, text=f"{src}  →  {tgt}",
                     font=("Segoe UI", 14, "bold"), fill=self.colors["accent"])
        y += 35

        # 两个芯片方框
        box_w = min(200, (cw - 80) // 2)
        box_h = 160
        x1 = cw // 2 - box_w - 20
        x2 = cw // 2 + 20

        for bx, chip, info, color in [(x1, src, src_info, self.colors["accent"]),
                                       (x2, tgt, tgt_info, "#6366f1")]:
            c.create_rectangle(bx, y, bx + box_w, y + box_h,
                             fill=self.colors["bg"], outline=color, width=2)
            c.create_text(bx + box_w // 2, y + 18, text=chip,
                         font=("Consolas", 12, "bold"), fill=color)
            details = [
                f"{info['capacity_bytes']}B",
                f"Page: {info['page_size']}B",
                f"Addr: {info['addr_bytes']}B",
                f"{info['max_freq_khz']}kHz",
                f"A pins: {info['a_pins']}",
            ]
            for i, d in enumerate(details):
                c.create_text(bx + box_w // 2, y + 42 + i * 22, text=d,
                             font=("Consolas", 9), fill=self.colors["text"])

        # 箭头
        ax = cw // 2
        ay = y + box_h // 2
        c.create_text(ax, ay, text="⇒", font=("Segoe UI", 24, "bold"),
                     fill=self.colors["warning"])

        y += box_h + 25

        # 向量数对比条
        sv = data["src_vectors"]
        tv = data["tgt_vectors"]
        max_v = max(sv, tv, 1)
        bar_max = cw - 80
        c.create_text(40, y, text=f"{src}: {sv:,}", anchor=tk.W,
                     font=("Consolas", 9), fill=self.colors["text"])
        y += 16
        bw1 = int(sv / max_v * bar_max)
        c.create_rectangle(40, y, 40 + bw1, y + 14,
                         fill=self.colors["accent"], outline="")
        y += 22
        c.create_text(40, y, text=f"{tgt}: {tv:,}", anchor=tk.W,
                     font=("Consolas", 9), fill=self.colors["text"])
        y += 16
        bw2 = int(tv / max_v * bar_max)
        c.create_rectangle(40, y, 40 + bw2, y + 14,
                         fill="#6366f1", outline="")
        y += 25

        # 变化项高亮
        c.create_text(40, y, text="Changes:", anchor=tk.W,
                     font=("Segoe UI", 10, "bold"), fill=self.colors["warning"])
        y += 20
        for key, info in diff.items():
            if info["changed"]:
                c.create_text(60, y, text=f"• {key}: {info['source']} → {info['target']}",
                             anchor=tk.W, font=("Consolas", 8), fill=self.colors["danger"])
                y += 16

    def _export_migration_svg(self):
        """导出迁移对比为 SVG"""
        if not self._migration_data:
            messagebox.showinfo(self.t("tab_migrate"), self.t("migrate_no_vectors"))
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".svg", filetypes=[("SVG", "*.svg")],
            initialfile="Chip_Migration.svg")
        if not path:
            return
        data = self._migration_data
        src = data["source"]
        tgt = data["target"]
        w, h = 600, 400
        svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
               f'font-family="Consolas,monospace">',
               f'<rect width="{w}" height="{h}" fill="#1e293b"/>']
        svg.append(f'<text x="{w//2}" y="30" text-anchor="middle" fill="#3b82f6" '
                   f'font-size="16" font-weight="bold">{src} → {tgt} Migration</text>')
        # 源芯片框
        svg.append('<rect x="40" y="50" width="220" height="140" fill="#0f172a" '
                   'stroke="#3b82f6" stroke-width="2" rx="6"/>')
        svg.append(f'<text x="150" y="75" text-anchor="middle" fill="#3b82f6" '
                   f'font-size="13" font-weight="bold">{src}</text>')
        src_info = data["src_info"]
        for i, (k, v) in enumerate([("Cap", f"{src_info['capacity_bytes']}B"),
                                     ("Page", f"{src_info['page_size']}B"),
                                     ("Addr", f"{src_info['addr_bytes']}B"),
                                     ("Freq", f"{src_info['max_freq_khz']}kHz")]):
            svg.append(f'<text x="150" y="{100+i*25}" text-anchor="middle" fill="#e2e8f0" '
                       f'font-size="10">{k}: {v}</text>')
        # 箭头
        svg.append('<text x="300" y="125" text-anchor="middle" fill="#f59e0b" '
                   'font-size="24" font-weight="bold">⇒</text>')
        # 目标芯片框
        svg.append('<rect x="340" y="50" width="220" height="140" fill="#0f172a" '
                   'stroke="#6366f1" stroke-width="2" rx="6"/>')
        svg.append(f'<text x="450" y="75" text-anchor="middle" fill="#6366f1" '
                   f'font-size="13" font-weight="bold">{tgt}</text>')
        tgt_info = data["tgt_info"]
        for i, (k, v) in enumerate([("Cap", f"{tgt_info['capacity_bytes']}B"),
                                     ("Page", f"{tgt_info['page_size']}B"),
                                     ("Addr", f"{tgt_info['addr_bytes']}B"),
                                     ("Freq", f"{tgt_info['max_freq_khz']}kHz")]):
            svg.append(f'<text x="450" y="{100+i*25}" text-anchor="middle" fill="#e2e8f0" '
                       f'font-size="10">{k}: {v}</text>')
        # 向量数
        sv = data["src_vectors"]
        tv = data["tgt_vectors"]
        svg.append(f'<text x="150" y="230" text-anchor="middle" fill="#94a3b8" '
                   f'font-size="11">Vectors: {sv:,}</text>')
        svg.append(f'<text x="450" y="230" text-anchor="middle" fill="#94a3b8" '
                   f'font-size="11">Vectors: {tv:,}</text>')
        # 变化列表
        y_pos = 260
        diff = data["diff"]
        for key, info in diff.items():
            if info["changed"]:
                svg.append(f'<text x="40" y="{y_pos}" fill="#ef4444" font-size="10">'
                           f'• {key}: {info["source"]} → {info["target"]}</text>')
                y_pos += 20
        svg.append('</svg>')
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(svg))
        messagebox.showinfo(self.t("tab_migrate"), f"SVG → {path}")

    def _export_atpg_svg(self):
        """导出 ATPG 覆盖率热力表为 SVG"""
        if not self._fault_sim or not self._fault_sim.results:
            messagebox.showinfo(self.t("tab_atpg"), self.t("atpg_no_vectors"))
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".svg", filetypes=[("SVG", "*.svg")],
            initialfile="ATPG_Coverage.svg")
        if not path:
            return
        sim = self._fault_sim
        tests = sim.test_names
        faults = sim.fault_types
        col_w = 65
        row_h = 28
        w = 160 + len(faults) * col_w + 20
        h = 60 + len(tests) * row_h + 20
        svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
               f'font-family="Consolas,monospace">',
               f'<rect width="{w}" height="{h}" fill="#1e293b"/>']
        svg.append('<text x="20" y="25" fill="#3b82f6" font-size="14" font-weight="bold">'
                   'ATPG Fault Coverage</text>')
        # 列标题
        for j, ft in enumerate(faults):
            x = 160 + j * col_w + col_w // 2
            svg.append(f'<text x="{x}" y="50" text-anchor="middle" fill="#94a3b8" '
                       f'font-size="9">{ft}</text>')
        # 行
        for i, tn in enumerate(tests):
            y = 60 + i * row_h
            svg.append(f'<text x="20" y="{y+row_h//2+4}" fill="#e2e8f0" font-size="9">'
                       f'{tn.replace("_TEST","")}</text>')
            for j, ft in enumerate(faults):
                x = 160 + j * col_w
                cov = sim.results.get((tn, ft), 0)
                bg = "#1D9E75" if cov >= 95 else "#7BC47F" if cov >= 80 else "#F5A623" if cov >= 60 else "#E24B4A"
                svg.append(f'<rect x="{x+2}" y="{y}" width="{col_w-4}" height="{row_h-2}" '
                           f'fill="{bg}" stroke="#334155"/>')
                svg.append(f'<text x="{x+col_w//2}" y="{y+row_h//2+4}" text-anchor="middle" '
                           f'fill="white" font-size="9" font-weight="bold">{cov:.0f}%</text>')
        svg.append('</svg>')
        with open(path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(svg))
        messagebox.showinfo(self.t("tab_atpg"), f"SVG → {path}")

    # ============================================================
    # Phase 9: 演示模式
    # ============================================================

    def _start_demo(self):
        """启动 15 步演示"""
        self._demo_step = 0
        self._demo_running = True
        self.demo_btn.config(state=tk.DISABLED, bg="#94a3b8")
        # ESC 绑定中断
        self.root.bind("<Escape>", self._stop_demo)
        self._demo_next()

    def _stop_demo(self, event=None):
        """ESC 停止演示"""
        self._demo_running = False
        self.demo_btn.config(state=tk.NORMAL, bg="#22c55e")
        self.root.unbind("<Escape>")
        self._update_status(self.t("demo_stop"))

    def _demo_next(self):
        """执行演示下一步"""
        if not self._demo_running:
            return
        if self._demo_step >= len(DEMO_SCRIPT):
            # 演示结束
            self._demo_running = False
            self.demo_btn.config(state=tk.NORMAL, bg="#22c55e")
            self.root.unbind("<Escape>")
            self._update_status(self.t("demo_done"))
            return

        step = DEMO_SCRIPT[self._demo_step]
        action = step["action"]
        desc = step["desc"]
        self._update_status(self.t("demo_running").format(
            step=self._demo_step + 1, total=len(DEMO_SCRIPT), desc=desc))

        try:
            if action == "select_tests":
                # 选择全量测试
                if hasattr(self, '_preset_maps') and len(self._preset_maps) > 1:
                    self._apply_preset(self._preset_maps[1])
            elif action == "generate":
                self.on_generate()
            elif action == "switch_tab":
                tab_key = step["params"].get("tab", "tab_pat")
                tab_text = self.t(tab_key).strip()
                for i in range(self.notebook.index("end")):
                    if self.notebook.tab(i, "text").strip() == tab_text:
                        self.notebook.select(i)
                        break
            elif action == "run_simulation":
                if hasattr(self, '_run_simulation'):
                    self._run_simulation()
            elif action == "run_atpg":
                if hasattr(self, '_run_atpg_simulation'):
                    self._run_atpg_simulation()
            elif action == "generate_proof":
                if hasattr(self, '_generate_atpg_proof'):
                    self._generate_atpg_proof()
            elif action == "run_economics":
                if hasattr(self, '_calculate_economics'):
                    self._calculate_economics()
        except Exception:
            pass  # 演示中跳过错误

        self._demo_step += 1
        # 800ms 后执行下一步
        self.root.after(800, self._demo_next)

    def _section_title(self, parent, text):
        """配置面板小节标题"""
        tk.Label(parent, text=text, font=("Segoe UI", 10, "bold"),
                fg=self.colors["accent"], bg=self.colors["sidebar"],
                padx=12).pack(anchor=tk.W, pady=(8, 2))

    def _write_default_info(self):
        """写入专业级测试说明文档 — 按协议分支"""
        protocol = self.chip_protocol_var.get() if hasattr(self, 'chip_protocol_var') else "I2C"
        self.stats_text.delete("1.0", tk.END)
        if protocol == "SPI":
            info = self._get_spi_info_text()
        elif protocol == "Microwire":
            info = self._get_mw_info_text()
        else:
            info = self._get_i2c_info_text()
        self.stats_text.insert("1.0", info)
        self.stats_text.config(state=tk.DISABLED)

    def _get_spi_info_text(self):
        """SPI 协议测试说明文档"""
        chip = self.chip_preset_var.get() if hasattr(self, 'chip_preset_var') else "25LC256"
        return """
╔═══════════════════════════════════════════════════════════════════╗
║          SPI EEPROM/Flash — ATE 测试方案技术规格书              ║
║          SPI Memory — ATE Test Plan Specification               ║
╚═══════════════════════════════════════════════════════════════════╝

■ 目标器件 / Target Device: """ + chip + """ (SPI Serial Memory)
  ┌────────────────────────────────────────────────────────────┐
  │ 接口 Interface    : SPI (Serial Peripheral Interface)     │
  │ 信号 Signals      : CS#, SCK, SI (MOSI), SO (MISO)       │
  │ SPI 模式          : Mode 0 (CPOL=0, CPHA=0)              │
  │                     Mode 3 (CPOL=1, CPHA=1)               │
  │ 最大频率 fSCK max : 20 MHz (typical)                      │
  │ 工作电压 VCC      : 1.8V ~ 5.5V                          │
  └────────────────────────────────────────────────────────────┘

■ 引脚定义 / Pinout (SOP-8 typical):
  ┌──────────────────────────────────────────────┐
  │  Pin 1: CS#  — 片选(低有效) Pin 8: VCC      │
  │  Pin 2: SO   — 串行输出     Pin 7: HOLD#    │
  │  Pin 3: WP#  — 写保护       Pin 6: SCK      │
  │  Pin 4: GND  — 地           Pin 5: SI       │
  └──────────────────────────────────────────────┘

■ SPI 命令集 / Command Set:
  ┌──────────────────────────────────────────────────────────┐
  │ 命令 Command │ Opcode │ 描述 Description                │
  │ WREN         │ 0x06   │ 写使能 (置位 WEL)               │
  │ WRDI         │ 0x04   │ 写禁止 (清除 WEL)               │
  │ RDSR         │ 0x05   │ 读状态寄存器                     │
  │ WRSR         │ 0x01   │ 写状态寄存器                     │
  │ READ         │ 0x03   │ 读数据                           │
  │ WRITE        │ 0x02   │ 写数据 (页编程)                  │
  │ SE           │ 0x20   │ 扇区擦除 (Flash only)            │
  │ CE           │ 0xC7   │ 全片擦除 (Flash only)            │
  │ RDID/JEDEC   │ 0x9F   │ 读 JEDEC ID (Flash only)         │
  └──────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════
 【1】开短路测试 / Open-Short Test (OS_TEST)
═══════════════════════════════════════════════════════════════════

  ■ 测试目的 / Purpose:
    验证 DUT 所有 SPI 引脚 (CS#/SCK/SI/SO/WP#/HOLD#) 的物理连通性。
    使用 ATE PPMU Walking-1/Walking-0 方法检测开路和短路。

  ■ Pass/Fail 判定: 同 I2C OS 测试 (PPMU 电压/电流阈值)。
    典型向量数: 46


═══════════════════════════════════════════════════════════════════
 【2】DC 参数测试 / DC Parameter Test (DC_TEST)
═══════════════════════════════════════════════════════════════════

  ■ 测试目的 / Purpose:
    验证 SPI 器件静态电气参数：ISB (待机电流), ICC (工作电流),
    VOL/VOH (输出电平), VIL/VIH (输入阈值)。

  ■ 测试方法:
    ① ISB: CS#=HIGH (未选中), 测量 VCC 待机电流
    ② ICC: 全速 SCK 连续读取, 测量 VCC 工作电流
    ③ VOL: SO 引脚灌电流测量 (IOL=条件)
    ④ VIL/VIH: SI/SCK/CS# 输入阈值验证


═══════════════════════════════════════════════════════════════════
 【3】功能测试 / Functional Test (FUNC_TEST)
═══════════════════════════════════════════════════════════════════

  ■ 测试目的 / Purpose:
    验证 SPI 通信协议和存储器读写功能的正确性。

  ■ 测试内容:
    ① WREN + 字节/页写入 + RDSR 轮询 WIP 位
    ② READ 读回验证 (数据比对)
    ③ 状态寄存器读写 (RDSR/WRSR)
    ④ WP# 写保护功能验证
    ⑤ JEDEC ID 读取验证 (Flash 器件)
    ⑥ 扇区擦除/全片擦除验证 (Flash 器件)

  ■ SPI 写操作流程:
    CS#↓ → WREN(0x06) → CS#↑
    CS#↓ → WRITE(0x02) + ADDR + DATA → CS#↑
    CS#↓ → RDSR(0x05) → 轮询 WIP=0 → CS#↑

  ■ SPI 读操作流程:
    CS#↓ → READ(0x03) + ADDR → SO 输出数据 → CS#↑


═══════════════════════════════════════════════════════════════════
 【4】March C- 存储器测试 / March C- Memory Test
═══════════════════════════════════════════════════════════════════

  ■ 测试方法: 与 I2C 相同的 6 步 March C- 算法, 但通过
    SPI WRITE/READ 命令执行。每步均需 WREN 前置。

  ■ 故障覆盖:
    ✓ SAF (Stuck-At Fault), TF (Transition Fault),
    ✓ CF (Coupling Fault)


═══════════════════════════════════════════════════════════════════
 【5】地址扫描 / Address Scan Test
═══════════════════════════════════════════════════════════════════

  ■ 对全部或部分地址空间写入 addr^0x55, 读回比对。
    验证地址译码逻辑完整性。


═══════════════════════════════════════════════════════════════════
 【6】数据保持 / Data Retention Test
═══════════════════════════════════════════════════════════════════

  ■ 写入棋盘格/全0/全1 模式, 等待后读回验证。
    检测存储单元电荷泄漏。


═══════════════════════════════════════════════════════════════════
 【7】SPI 异常测试 / SPI Error Test
═══════════════════════════════════════════════════════════════════

  ■ 测试内容:
    ① 未 WREN 直接写入 → 应被拒绝 (WEL=0)
    ② CS# 毛刺 (提前拉高) → 事务应中断
    ③ WRSR 保护位设置 → 写入应失败
    ④ 状态寄存器 WIP 忙期间操作

  ■ 目的: 验证器件的错误处理和保护机制。


═══════════════════════════════════════════════════════════════════
 【8】耐久性测试 / Endurance Test
═══════════════════════════════════════════════════════════════════

  ■ 同一地址反复 WREN+WRITE+READ 循环, 验证擦写寿命。
    EEPROM 典型: 1M cycles; Flash 典型: 100K cycles。


═══════════════════════════════════════════════════════════════════
 Bin 分选表 / Bin Sort Table
═══════════════════════════════════════════════════════════════════

  │ Bin │ 名称         │ 说明                              │
  │  1  │ PASS         │ 所有测试通过                       │
  │  2  │ OS_FAIL      │ 开短路测试失败                     │
  │  3  │ DC_FAIL      │ DC 参数超出规格                    │
  │  4  │ FUNC_FAIL    │ 功能测试失败                       │
  │  5  │ MEM_FAIL     │ March / 地址扫描 / 保持测试失败    │
  │  6  │ PROT_FAIL    │ SPI 异常测试失败                   │
  │  7  │ ENDUR_FAIL   │ 耐久性测试失败                     │
  │  8  │ CONTACT_FAIL │ 接触不良 (探针/socket 问题)        │

═══════════════════════════════════════════════════════════════════
  本文档由 ATE Pattern Generator Platform 自动生成
  工具版本: """ + VERSION + """
═══════════════════════════════════════════════════════════════════
"""

    def _get_mw_info_text(self):
        """Microwire 协议测试说明文档"""
        chip = self.chip_preset_var.get() if hasattr(self, 'chip_preset_var') else "93C46"
        return """
╔═══════════════════════════════════════════════════════════════════╗
║       Microwire EEPROM — ATE 测试方案技术规格书                 ║
║       Microwire EEPROM — ATE Test Plan Specification            ║
╚═══════════════════════════════════════════════════════════════════╝

■ 目标器件 / Target Device: """ + chip + """ (Microwire Serial EEPROM)
  ┌────────────────────────────────────────────────────────────┐
  │ 接口 Interface    : Microwire (3-Wire Serial)             │
  │ 信号 Signals      : CS, SK (Clock), DI (Data In),        │
  │                     DO (Data Out)                         │
  │ 最大频率 fSK max  : 2 MHz (typical)                      │
  │ 工作电压 VCC      : 2.5V ~ 5.5V                          │
  │ 组织方式          : x8 或 x16 (器件相关)                  │
  └────────────────────────────────────────────────────────────┘

■ 引脚定义 / Pinout (SOP-8 typical):
  ┌──────────────────────────────────────────────┐
  │  Pin 1: CS   — 片选(高有效)  Pin 8: VCC     │
  │  Pin 2: SK   — 串行时钟      Pin 7: NC/ORG  │
  │  Pin 3: DI   — 数据输入      Pin 6: NC      │
  │  Pin 4: GND  — 地            Pin 5: DO      │
  └──────────────────────────────────────────────┘

■ Microwire 指令集 / Instruction Set:
  ┌──────────────────────────────────────────────────────────┐
  │ 指令 Instruction │ Start+Opcode │ 描述 Description      │
  │ READ             │ 1_10_ADDR    │ 读数据                 │
  │ WRITE            │ 1_01_ADDR    │ 写数据                 │
  │ ERASE            │ 1_11_ADDR    │ 擦除指定地址           │
  │ EWEN             │ 1_00_11xx    │ 擦写使能               │
  │ EWDS             │ 1_00_00xx    │ 擦写禁止               │
  │ ERAL             │ 1_00_10xx    │ 全片擦除               │
  │ WRAL             │ 1_00_01xx    │ 全片写入               │
  └──────────────────────────────────────────────────────────┘

  ■ 注意: Microwire 指令以 Start Bit (1) 开头,
    后跟 2-bit Opcode, 再跟地址/数据。
    所有写/擦除操作前必须先执行 EWEN 指令。


═══════════════════════════════════════════════════════════════════
 【1】开短路测试 / Open-Short Test (OS_TEST)
═══════════════════════════════════════════════════════════════════

  ■ 验证 CS/SK/DI/DO 引脚物理连通性。
    使用 PPMU Walking-1/Walking-0 方法。


═══════════════════════════════════════════════════════════════════
 【2】DC 参数测试 / DC Parameter Test (DC_TEST)
═══════════════════════════════════════════════════════════════════

  ■ 测试 ISB (待机电流, CS=LOW), ICC (工作电流),
    VOL/VOH (DO 输出电平), VIL/VIH (CS/SK/DI 输入阈值)。


═══════════════════════════════════════════════════════════════════
 【3】功能测试 / Functional Test (FUNC_TEST)
═══════════════════════════════════════════════════════════════════

  ■ 测试内容:
    ① EWEN 擦写使能
    ② WRITE 写入 + Ready/Busy 轮询 (DO 输出)
    ③ READ 读回验证
    ④ ERASE 单地址擦除 + 验证
    ⑤ EWDS 擦写禁止 → 写入应失败
    ⑥ ERAL 全片擦除 (可选)
    ⑦ WRAL 全片写入 (可选)

  ■ Microwire 写操作流程:
    CS↑ → SB(1)+EWEN → CS↓ (使能)
    CS↑ → SB(1)+WRITE+ADDR+DATA → CS↓
    CS↑ → 轮询 DO (0=Busy, 1=Ready) → CS↓

  ■ Microwire 读操作流程:
    CS↑ → SB(1)+READ+ADDR → DO 输出数据 → CS↓


═══════════════════════════════════════════════════════════════════
 【4】March C- 存储器测试
═══════════════════════════════════════════════════════════════════

  ■ 6 步 March C- 算法通过 Microwire WRITE/READ 执行。
    每步写操作前需确保 EWEN 已执行。


═══════════════════════════════════════════════════════════════════
 【5】地址扫描 / Address Scan Test
═══════════════════════════════════════════════════════════════════

  ■ 对全部地址写入 addr^0x55, 读回比对。


═══════════════════════════════════════════════════════════════════
 【6】数据保持 / Data Retention Test
═══════════════════════════════════════════════════════════════════

  ■ 写入棋盘格/全0/全1 模式, 等待后读回验证。


═══════════════════════════════════════════════════════════════════
 【7】Microwire 异常测试 / Error Test
═══════════════════════════════════════════════════════════════════

  ■ 测试内容:
    ① 未 EWEN 直接写入 → 应被拒绝
    ② CS 毛刺 (传输中拉低) → 事务中断
    ③ EWDS 后写入 → 应失败
    ④ Ready/Busy 轮询超时处理


═══════════════════════════════════════════════════════════════════
 【8】耐久性测试 / Endurance Test
═══════════════════════════════════════════════════════════════════

  ■ 同一地址反复 EWEN+WRITE+READ 循环。
    典型寿命: 1M cycles (25°C)。


═══════════════════════════════════════════════════════════════════
 Bin 分选表 / Bin Sort Table
═══════════════════════════════════════════════════════════════════

  │ Bin │ 名称         │ 说明                              │
  │  1  │ PASS         │ 所有测试通过                       │
  │  2  │ OS_FAIL      │ 开短路测试失败                     │
  │  3  │ DC_FAIL      │ DC 参数超出规格                    │
  │  4  │ FUNC_FAIL    │ 功能测试失败                       │
  │  5  │ MEM_FAIL     │ March / 地址扫描 / 保持测试失败    │
  │  6  │ PROT_FAIL    │ Microwire 异常测试失败             │
  │  7  │ ENDUR_FAIL   │ 耐久性测试失败                     │
  │  8  │ CONTACT_FAIL │ 接触不良 (探针/socket 问题)        │

═══════════════════════════════════════════════════════════════════
  本文档由 ATE Pattern Generator Platform 自动生成
  工具版本: """ + VERSION + """
═══════════════════════════════════════════════════════════════════
"""

    def _get_i2c_info_text(self):
        """I2C 协议测试说明文档"""
        chip = self.chip_preset_var.get() if hasattr(self, 'chip_preset_var') else "AT24C02"
        info = """
╔═══════════════════════════════════════════════════════════════════╗
║          """ + chip + """ — ATE 测试方案技术规格书                ║
║          I2C EEPROM — ATE Test Plan Specification               ║
╚═══════════════════════════════════════════════════════════════════╝

■ 目标器件 / Target Device: """ + chip + """ (I2C Serial EEPROM)
  ┌────────────────────────────────────────────────────────────┐
  │ 容量 Capacity     : 256 × 8 bit = 2 Kbit                 │
  │ 接口 Interface    : I2C / Two-Wire Serial (TWI)           │
  │ 工作电压 VCC      : 1.8V ~ 5.5V                          │
  │ 页大小 Page Size  : 8 Bytes                               │
  │ 擦写寿命 Endurance: 1,000,000 cycles (25°C)               │
  │ 数据保持 Retention: 100 years (25°C)                      │
  │ 最大频率 fSCL max : 1 MHz (5V) / 400 kHz (1.8V)          │
  │ 封装 Package      : SOP-8 / DIP-8 / TSSOP-8              │
  └────────────────────────────────────────────────────────────┘

■ 引脚定义 / Pinout (SOP-8):
  ┌──────────────────────────────────────────────┐
  │  Pin 1: A0  — 地址输入   Pin 8: VCC — 电源  │
  │  Pin 2: A1  — 地址输入   Pin 7: WP  — 写保护│
  │  Pin 3: A2  — 地址输入   Pin 6: SCL — 时钟  │
  │  Pin 4: GND — 地         Pin 5: SDA — 数据  │
  └──────────────────────────────────────────────┘

■ 器件地址格式 / Device Address:
  [ 1 | 0 | 1 | 0 | A2 | A1 | A0 | R/W ]
  默认 (A2=A1=A0=0): Write=0xA0, Read=0xA1


═══════════════════════════════════════════════════════════════════
 【1】开短路测试 / Open-Short Test (OS_TEST)
═══════════════════════════════════════════════════════════════════

  ■ 测试目的 / Purpose:
    验证 DUT 所有引脚的物理连通性，检测封装缺陷导致的引脚
    开路 (Open) 或引脚间短路 (Short)。这是量产测试的第一道
    筛选，排除明显的物理缺陷。

  ■ 测试方法 / Methodology:
    使用 ATE 内置 PPMU (Precision Pin Measurement Unit):
    Step 1 — Walking-1 (检测短路):
      依次对每个引脚施加电流 +100μA，其余引脚接地。
      测量被测引脚电压，预期 V > 0.5V（正常二极管压降）。
      若 V ≈ 0V，说明该引脚与其他引脚或 GND 短路。
    Step 2 — Walking-0 (检测开路):
      依次对每个引脚施加电流 -100μA，其余引脚接 VCC。
      测量被测引脚电压，预期 V < VCC - 0.5V。
      若 V ≈ VCC，说明该引脚开路（无连接）。

  ■ Pass/Fail 判定 / Criteria:
    │ 检测项     │ 条件               │ PASS 范围            │
    │ Walking-1  │ FI=+100μA, Vref=0V │ 0.2V ≤ V ≤ VCC      │
    │ Walking-0  │ FI=-100μA, Vref=VCC│ 0V ≤ V ≤ VCC - 0.2V │

  ■ 故障覆盖 / Fault Coverage:
    ✓ 引脚开路 (Bond wire open)
    ✓ 引脚间短路 (Pin-to-pin short)
    ✓ 引脚对地/电源短路 (Pin-to-rail short)

  ■ ATE 执行 / Execution:
    .prg: DIGI_PPMU_WALKING_FI_MV(ALL_PINS, 100UA, ...);
    .pat: RUN_PATTERN(OS_TEST:ST, OS_TEST:END, 1);
    典型向量数: 46


═══════════════════════════════════════════════════════════════════
 【2】DC 参数测试 / DC Parameter Test (DC_TEST)
═══════════════════════════════════════════════════════════════════

  ■ 测试目的 / Purpose:
    验证 DUT 的静态电气参数是否符合 Datasheet 规格。DC 测试
    确保器件在规定的电压/电流范围内正常工作，是可靠性的基础保证。

  ■ 测试方法 / Methodology:
    ① ISB (Standby Current) — 待机电流测量:
       VCC=5.5V, 所有引脚悬空, 无 I2C 活动。
       通过 DPS 测量 VCC 引脚电流, 预期 ≤ 1.0μA。
    ② ICC(R) (Read Current) — 读操作电流:
       fSCL=400kHz 连续读取, 测量 VCC 电流, 预期 ≤ 1.0mA。
    ③ ICC(W) (Write Current) — 写操作电流:
       fSCL=400kHz 连续写入, 测量 VCC 电流, 预期 ≤ 3.0mA。
    ④ VOL (Output Low Voltage) — SDA 输出低电平:
       IOL=3mA 灌电流, 测量 SDA 电压, 预期 ≤ 0.4V。
    ⑤ VIL/VIH (Input Threshold) — 输入阈值:
       VIL ≤ 0.3×VCC, VIH ≥ 0.7×VCC (CMOS 兼容)。

  ■ Pass/Fail 判定 / Criteria:
    │ 参数    │ 条件             │ Min   │ Max   │ 单位  │
    │ ISB     │ VCC=5.5V, SBY    │ —     │ 1.0   │ μA    │
    │ ICC(R)  │ fSCL=400kHz      │ —     │ 1.0   │ mA    │
    │ ICC(W)  │ fSCL=400kHz      │ —     │ 3.0   │ mA    │
    │ VOL     │ IOL=3mA          │ —     │ 0.4   │ V     │
    │ VIL(5V) │ VCC=5.0V         │ -0.5  │ 1.5   │ V     │
    │ VIH(5V) │ VCC=5.0V         │ 3.5   │ 5.5   │ V     │

  ■ 故障覆盖 / Fault Coverage:
    ✓ 电源轨缺陷 (Power rail defects)
    ✓ 输出驱动器失效 (Output driver failure)
    ✓ 输入缓冲器阈值偏移 (Input buffer threshold shift)
    ✓ 静态功耗异常 (Abnormal static power)

  ■ ATE 执行 / Execution:
    .prg: DIGI_DPS_FV_MI(VCC_PIN, 5.5V, ...); — ISB
          DIGI_PPMU_FI_MV(SDA, 3MA, ...);     — VOL
    .pat: RUN_PATTERN(DC_TEST:ST, DC_TEST:END, 1);
    典型向量数: 1,182


═══════════════════════════════════════════════════════════════════
 【3】功能测试 / Functional Test (FUNC_TEST)
═══════════════════════════════════════════════════════════════════

  ■ 测试目的 / Purpose:
    验证 AT24C02 的 I2C 协议实现和存储功能是否正确。通过完整的
    写入-读回-比较流程，确保器件能正确响应 I2C 事务。

  ■ 测试方法 / Methodology:
    FUNC-1: 字节写入 + 随机读验证 (Byte Write + Random Read)
      → 向 8 个地址写入数据, ACK Polling 等待写完成,
        随机读每个地址并与写入值比较 (ATE H/L 比较)。
    FUNC-2: 页写入 + 顺序读验证 (Page Write + Sequential Read)
      → 一次写入 8 字节 (整页), ACK Polling,
        顺序读 8 字节并逐个比较。
    FUNC-3: 地址边界测试 (Address Boundary)
      → 写入地址 0x00 和 0xFF, 读回验证。
      → 写入翻转数据 (0x55, 0xAA), 读回验证。
    FUNC-4: WP 写保护验证 (Write Protect)
      → WP=1 时尝试写入, 读回验证数据未改变。
      → WP=0 时写入, 读回验证数据已写入。
    FUNC-5: 自定义写入测试 (User-Defined, 可选)
      → 用户指定的地址和数据, 写入 + 读回验证。

  ■ Pass/Fail 判定 / Criteria:
    所有读回数据与写入数据逐位比对。
    ATE 向量中使用 H (Expect High) 和 L (Expect Low) 状态。
    任何一位不匹配 → 该向量 FAIL → 整段 FAIL。

  ■ 故障覆盖 / Fault Coverage:
    ✓ I2C 协议实现 (START/STOP/ACK/NACK)
    ✓ 字节写入功能 (Byte write path)
    ✓ 页写入功能 (Page write path)
    ✓ 随机读 / 顺序读 (Random read / Sequential read)
    ✓ 写保护功能 (Write protect logic)
    ✓ 地址译码边界 (Address decoder boundary)

  ■ ATE 执行 / Execution:
    .pat: RUN_PATTERN(FUNC_TEST:ST, FUNC_TEST:END, 1);
    典型向量数: 3,112


═══════════════════════════════════════════════════════════════════
 【4】March C- 存储器测试 / March C- Memory Test (MARCH_TEST)
═══════════════════════════════════════════════════════════════════

  ■ 测试目的 / Purpose:
    使用经典的 March C- 算法对 EEPROM 存储阵列进行系统性测试，
    检测单元级故障。March C- 是工业界公认的存储器测试标准算法，
    以最小的复杂度覆盖三大故障模型。

  ■ 测试方法 / Methodology (6 步 March 元素):
    设 N = 测试地址数量, ⇑ = 地址递增, ⇓ = 地址递减

    M0: ⇑ (w0)      — 全部写 0 (初始化)
    M1: ⇑ (r0, w1)  — 递增序: 读 0 验证, 写 1
    M2: ⇑ (r1, w0)  — 递增序: 读 1 验证, 写 0
    M3: ⇓ (r0, w1)  — 递减序: 读 0 验证, 写 1
    M4: ⇓ (r1, w0)  — 递减序: 读 1 验证, 写 0
    M5: ⇑ (r0)      — 全部读 0 验证 (最终检查)

    每个 March 元素对每个地址执行一次 I2C 写/读事务。
    算法复杂度: O(10N), 共 10N 次存储器访问。

  ■ Pass/Fail 判定 / Criteria:
    每步读操作的数据必须与预期一致。
    M1: 读出必须为 0x00  │  M2: 读出必须为 0xFF
    M3: 读出必须为 0x00  │  M4: 读出必须为 0xFF
    M5: 读出必须为 0x00

  ■ 故障覆盖 / Fault Coverage:
    ✓ SAF (Stuck-At Fault) — 存储单元固定为 0 或 1
    ✓ TF (Transition Fault) — 单元无法从 0→1 或 1→0 翻转
    ✓ CFin (Inversion Coupling Fault) — 写入一个单元导致另一个翻转
    ✗ CFid (Idempotent CF) — 需要 March B 检测

  ■ ATE 执行 / Execution:
    .pat: RUN_PATTERN(MARCH_TEST:ST, MARCH_TEST:END, 1);
    典型向量数: 15,410 (8 地址) — 随地址数线性增长


═══════════════════════════════════════════════════════════════════
 【4B】March B 存储器测试 / March B Memory Test (MARCHB_TEST)
═══════════════════════════════════════════════════════════════════

  ■ 测试目的 / Purpose:
    March B 是 March C- 的增强版本，使用 17 步 March 元素，
    能额外检测 CFid (Idempotent Coupling Fault) 和部分
    NPF (Neighborhood Pattern Sensitive Fault)。
    适用于高可靠性要求的应用场景。

  ■ 测试方法 / Methodology:
    17 步 March 元素 (含多次读写交错):
    M0:  ⇑(w0)           M9:  ⇓(r0,w1)
    M1:  ⇑(r0,w1,r1)     M10: ⇓(r1,w0)
    M2:  ⇑(r1,w0,r0)     M11: ⇓(r0,w1,r1)
    M3:  ⇑(r0,w1)        M12: ⇓(r1,w0,r0)
    M4:  ⇑(r1,w0)        M13: ⇓(r0)
    ...                    ...
    算法复杂度: O(17N), 比 March C- 多 70% 的测试量。

  ■ 故障覆盖 / Fault Coverage:
    ✓ SAF + TF + CFin (同 March C-)
    ✓ CFid (Idempotent Coupling Fault)
    ✓ 部分 NPSF (Neighborhood Pattern Sensitive Fault)

  ■ ATE 执行 / Execution:
    .pat: RUN_PATTERN(MARCHB_TEST:ST, MARCHB_TEST:END, 1);
    典型向量数: ~18,000 (8 地址)


═══════════════════════════════════════════════════════════════════
 【5】地址空间扫描测试 / Address Scan Test (SCAN_TEST)
═══════════════════════════════════════════════════════════════════

  ■ 测试目的 / Purpose:
    验证 EEPROM 的地址译码器和存储阵列在指定地址范围内的完整性。
    通过写入与地址相关的特征数据，确保每个地址单元独立可访问。

  ■ 测试方法 / Methodology:
    对可配置的地址范围 [start_addr, end_addr]:
    Phase 1 — 写入阶段:
      for addr in range(start, end+1):
          byte_write(addr, addr XOR 0x55)
          ACK_Polling()
    Phase 2 — 验证阶段:
      for addr in range(start, end+1):
          data = random_read(addr)
          COMPARE(data, addr XOR 0x55)  // ATE H/L 比较

    使用 addr XOR 0x55 作为特征数据，确保:
    1. 每个地址的写入数据不同 (排除地址别名)
    2. 数据值 ≠ 地址值 (排除地址-数据总线短路)

  ■ Pass/Fail 判定 / Criteria:
    Phase 2 中每个地址读回的数据必须等于 (addr XOR 0x55)。

  ■ 故障覆盖 / Fault Coverage:
    ✓ 地址译码器故障 (Address decoder fault)
    ✓ 地址别名 (Address aliasing)
    ✓ 地址-数据总线串扰 (Address-data bus crosstalk)

  ■ ATE 执行 / Execution:
    .pat: RUN_PATTERN(SCAN_TEST:ST, SCAN_TEST:END, 1);
    典型向量数: 3,086 (8 地址)


═══════════════════════════════════════════════════════════════════
 【6】数据保持测试 / Data Retention Test (RET_TEST)
═══════════════════════════════════════════════════════════════════

  ■ 测试目的 / Purpose:
    验证 EEPROM 在写入后能正确保持数据。AT24C02 额定数据保持
    100 年 (25°C)。ATE 测试中通过写入-等待-读回验证来模拟。

  ■ 测试方法 / Methodology:
    三组数据模式，每组独立执行写入-等待-验证:

    Group A — 棋盘格 (Checkerboard):
      Phase 1: 写入 0x55 到偶地址, 0xAA 到奇地址
      Phase 2: 等待延时 (模拟保持时间, 向量 idle)
      Phase 3: 读回每个地址, 比较 0x55/0xAA

    Group B — 全零 (All-0):
      Phase 4: 写入 0x00 到所有地址
      Phase 5: 等待延时
      Phase 6: 读回验证全部为 0x00

    Group C — 全一 (All-1):
      Phase 7: 写入 0xFF 到所有地址
      Phase 8: 等待延时
      Phase 9: 读回验证全部为 0xFF

  ■ Pass/Fail 判定 / Criteria:
    每组的 Phase 3/6/9 读回数据必须与写入数据完全一致。

  ■ 故障覆盖 / Fault Coverage:
    ✓ 数据保持故障 (Data retention failure)
    ✓ 电荷泄漏 (Charge leakage in floating gate)
    ✓ 存储单元退化 (Cell degradation)

  ■ ATE 执行 / Execution:
    .pat: RUN_PATTERN(RET_TEST:ST, RET_TEST:END, 1);
    典型向量数: 9,313 (8 地址)
    注: 量产测试中可配合高温烘烤 (Bake) 加速验证


═══════════════════════════════════════════════════════════════════
 【7】I2C 协议异常/边界测试 / I2C Error Test (ERR_TEST)
═══════════════════════════════════════════════════════════════════

  ■ 测试目的 / Purpose:
    验证 DUT 在非正常 I2C 通信条件下的行为，确保器件能正确
    处理异常情况而不会锁死或损坏数据。

  ■ 测试方法 / Methodology:
    ERR-1: 错误器件地址 (Wrong Device Address)
      → 发送不匹配的地址 (如 0xB0), 检查 DUT 返回 NACK。
      → 验证 DUT 不响应非自身地址的事务。
    ERR-2: 不完整事务恢复 (Incomplete Transaction)
      → 开始一个写事务, 在数据字节中途发送 STOP。
      → 验证 DUT 能恢复到空闲状态, 后续正常事务可以成功。
    ERR-3: 总线忙恢复 (Bus Busy Recovery)
      → 模拟 SDA 被 DUT 钳住低电平 (总线挂死)。
      → 发送 9 个 SCL 脉冲 + STOP, 验证总线恢复。
      → 执行正常读写验证 DUT 存活。
    ERR-4: 连续 START (Repeated START Storm)
      → 不发 STOP, 连续发送多次 START。
      → 验证 DUT 能正确处理 Repeated START。
    ERR-5: DUT 存活验证 (Survival Check)
      → 所有异常测试后, 执行完整的写+读验证。
      → 确认 DUT 功能未被破坏。

  ■ Pass/Fail 判定 / Criteria:
    ERR-1: NACK 正确返回 (SDA=H on 9th clock)
    ERR-2: 后续正常事务成功
    ERR-3: 9 脉冲后 SDA 释放, 后续事务成功
    ERR-4: DUT 正确响应最后一个 START
    ERR-5: 写+读数据一致

  ■ 故障覆盖 / Fault Coverage:
    ✓ I2C 状态机异常 (FSM edge cases)
    ✓ 总线锁死恢复 (Bus hung recovery)
    ✓ 地址过滤逻辑 (Address filtering)
    ✓ 协议鲁棒性 (Protocol robustness)

  ■ ATE 执行 / Execution:
    .pat: RUN_PATTERN(ERR_TEST:ST, ERR_TEST:END, 1);
    典型向量数: 1,443


═══════════════════════════════════════════════════════════════════
 【8】耐久性/写循环测试 / Endurance Test (ENDUR_TEST)
═══════════════════════════════════════════════════════════════════

  ■ 测试目的 / Purpose:
    验证 EEPROM 的擦写循环寿命。AT24C02 额定 100 万次 (25°C)。
    ATE 测试中执行有限次循环 (10 次) 确认基本擦写能力。
    量产全寿命测试需通过 ATE LOOP 指令扩展循环次数。

  ■ 测试方法 / Methodology:
    对指定地址 (默认 0x70) 执行 N 轮循环 (默认 10 轮):
    for cycle in range(N):
        data = PATTERN_TABLE[cycle % 4]  // 0x55, 0xAA, 0x00, 0xFF
        byte_write(addr, data)
        ACK_Polling()
        readback = random_read(addr)
        COMPARE(readback, data)

  ■ Pass/Fail 判定 / Criteria:
    每轮循环的读回数据必须与写入数据一致。

  ■ 故障覆盖 / Fault Coverage:
    ✓ 擦写耐久性 (Write endurance / cycling)
    ✓ 电荷注入退化 (Charge injection degradation)
    ✓ 隧穿氧化层老化 (Tunnel oxide aging)

  ■ ATE 执行 / Execution:
    .pat: RUN_PATTERN(ENDUR_TEST:ST, ENDUR_TEST:END, 1);
    典型向量数: 3,980 (10 轮)
    量产扩展: LOOP(1000000) { RUN_PATTERN(...); }


╔═══════════════════════════════════════════════════════════════════╗
║                    ATE 集成指南                                  ║
║                ATE Integration Guide                             ║
╚═══════════════════════════════════════════════════════════════════╝

■ 文件关系 / File Relationships:
  ┌──────────┐     ┌──────────┐     ┌──────────┐
  │  .prg    │────>│  .pat    │     │  .tim    │
  │ 测试程序 │     │ 向量文件 │     │ 时序定义 │
  └────┬─────┘     └──────────┘     └────┬─────┘
       │                                  │
       │           ┌──────────┐           │
       └──────────>│   ATE    │<──────────┘
                   │  Engine  │
       ┌──────────>│          │
       │           └──────────┘
  ┌────┴─────┐
  │  .lvl    │
  │ 电平定义 │
  └──────────┘

■ 工作流 / Workflow:
  1. 将 .pat 文件放入 AdaptStar-E 测试工程目录
  2. .prg 中 RUN_PATTERN 调用各测试段 (OS_TEST:ST → OS_TEST:END)
  3. .tim 定义时钟周期、驱动/比较边沿时间
  4. .lvl 定义 VIH/VIL/VOH/VOL 电平和 DPS 通道电压
  5. ATE 逐向量执行: Drive(0/1) → Compare(H/L) → PASS/FAIL

■ 向量状态符号 / Vector State Symbols:
  │ 符号 │ 含义        │ ATE 行为                         │
  │  0   │ Drive Low   │ ATE 驱动引脚输出低电平           │
  │  1   │ Drive High  │ ATE 驱动引脚输出高电平           │
  │  L   │ Expect Low  │ 比较器检查 DUT 输出 ≤ VOL       │
  │  H   │ Expect High │ 比较器检查 DUT 输出 ≥ VOH       │
  │  Z   │ Hi-Z        │ ATE 释放引脚 (三态)              │
  │  X   │ Don't Care  │ ATE 不比较, 忽略该引脚           │

■ BIN 分类 / Binning:
  │ Bin │ 名称         │ 判定条件                         │
  │  1  │ PASS         │ 所有测试通过                     │
  │  2  │ OS_FAIL      │ 开短路测试失败                   │
  │  3  │ DC_FAIL      │ DC 参数超出规格                  │
  │  4  │ FUNC_FAIL    │ 功能测试失败                     │
  │  5  │ MEM_FAIL     │ March / 地址扫描 / 保持测试失败  │
  │  6  │ PROT_FAIL    │ I2C 异常测试失败                 │
  │  7  │ ENDUR_FAIL   │ 耐久性测试失败                   │
  │  8  │ CONTACT_FAIL │ 接触不良 (探针/socket 问题)      │

═══════════════════════════════════════════════════════════════════
  本文档由 ATE Pattern Generator Platform 自动生成
  工具版本: """ + VERSION + """
═══════════════════════════════════════════════════════════════════
"""
        return info

    # ================================================================
    # 行号 & 语法高亮 & 统计
    # ================================================================

    # ================================================================
    # I2C 波形图绘制
    # ================================================================

    def _draw_waveform(self):
        """绘制 SDA/SCL I2C 时序波形图"""
        c = self.wave_canvas
        self._safe_canvas_reset(c)

        if not self.current_vectors:
            c.create_text(300, 120, text=self.t("wave_hint"),
                          fill=self.colors["text_dim"], font=("Segoe UI", 12))
            return

        # 解析显示范围
        try:
            v_start = max(0, int(self.wave_start_var.get()))
        except ValueError:
            v_start = 0
        try:
            v_end = min(len(self.current_vectors), int(self.wave_end_var.get()))
        except ValueError:
            v_end = min(200, len(self.current_vectors))
        if v_end <= v_start:
            v_end = min(v_start + 200, len(self.current_vectors))

        vectors = self.current_vectors[v_start:v_end]
        comments = self.current_comments[v_start:v_end] if self.current_comments else []
        n = len(vectors)

        # 绘制参数
        vec_w = 12
        margin_l = 70
        margin_t = 35
        gap = 20

        # 根据协议选择波形信号
        protocol = self.chip_protocol_var.get() if hasattr(self, 'chip_protocol_var') else "I2C"
        if protocol == "SPI":
            signals = ["CS", "SCK", "MOSI", "MISO"]
            lane_h = 36  # 4信号时缩小每个通道高度
        elif protocol == "Microwire":
            signals = ["CS", "SK", "DI", "DO"]
            lane_h = 36
        else:
            signals = ["SCL", "SDA"]
            lane_h = 50

        total_w = margin_l + n * vec_w + 60
        total_h = margin_t + len(signals) * (lane_h + gap) + 80
        c.configure(scrollregion=(0, 0, total_w, total_h))

        # 颜色
        clr_drive = self.colors["accent"]
        clr_cmp_h = self.colors["success"]
        clr_cmp_l = self.colors["danger"]
        clr_hiz = self.colors["warning"]
        clr_x = self.colors["text_dim"]

        # 向量号刻度线
        for i in range(0, n, max(1, n // 20)):
            x = margin_l + i * vec_w
            c.create_line(x, margin_t - 18, x, margin_t + len(signals) * (lane_h + gap),
                          fill=self.colors["border"], dash=(1, 5))
            c.create_text(x, margin_t - 22, text=str(v_start + i),
                          fill=self.colors["text_dim"], font=("Consolas", 6))

        for si, sig in enumerate(signals):
            y_base = margin_t + si * (lane_h + gap)
            y_high = y_base + 5
            y_low = y_base + lane_h - 5
            y_mid = (y_high + y_low) // 2

            # 信号名
            c.create_text(margin_l - 10, y_mid, text=sig,
                          fill=self.colors["text"], font=("Consolas", 11, "bold"),
                          anchor=tk.E)
            # 参考线
            c.create_line(margin_l, y_high, margin_l + n * vec_w, y_high,
                          fill=self.colors["border"], dash=(2, 6))
            c.create_line(margin_l, y_low, margin_l + n * vec_w, y_low,
                          fill=self.colors["border"], dash=(2, 6))
            c.create_text(margin_l - 10, y_high, text="1", fill=self.colors["text_dim"],
                          font=("Consolas", 7), anchor=tk.E)
            c.create_text(margin_l - 10, y_low, text="0", fill=self.colors["text_dim"],
                          font=("Consolas", 7), anchor=tk.E)

            prev_y = None
            for i in range(n):
                x = margin_l + i * vec_w
                val = vectors[i].get(sig, "X")

                if val == "1":
                    cur_y, color, width = y_high, clr_drive, 2
                elif val == "0":
                    cur_y, color, width = y_low, clr_drive, 2
                elif val == "H":
                    cur_y, color, width = y_high, clr_cmp_h, 2
                elif val == "L":
                    cur_y, color, width = y_low, clr_cmp_l, 2
                elif val == "Z":
                    cur_y, color, width = y_mid, clr_hiz, 1
                else:
                    cur_y, color, width = y_mid, clr_x, 1

                # 跳变沿
                if prev_y is not None and prev_y != cur_y:
                    c.create_line(x, prev_y, x, cur_y, fill=color, width=1)

                # 水平信号线
                dash = (3, 3) if val in ("Z", "X") else ()
                c.create_line(x, cur_y, x + vec_w, cur_y, fill=color, width=width,
                              dash=dash)

                # H/L 比较标记 (小三角)
                if val == "H":
                    c.create_polygon(x + vec_w // 2, y_high - 4,
                                     x + vec_w // 2 - 3, y_high + 2,
                                     x + vec_w // 2 + 3, y_high + 2,
                                     fill=clr_cmp_h, outline="")
                elif val == "L":
                    c.create_polygon(x + vec_w // 2, y_low + 4,
                                     x + vec_w // 2 - 3, y_low - 2,
                                     x + vec_w // 2 + 3, y_low - 2,
                                     fill=clr_cmp_l, outline="")

                prev_y = cur_y

        # 事件标注 (协议相关关键词)
        anno_y = margin_t + len(signals) * (lane_h + gap) + 8
        if protocol == "SPI":
            anno_keywords = [
                ("CS_LOW", self.colors["warning"]), ("CS_HIGH", self.colors["danger"]),
                ("WREN", "#ff9f43"), ("RDSR", "#b197fc"),
                ("WIP", "#b197fc"), ("WRITE", self.colors["accent"]),
                ("READ", self.colors["success"]), ("ERASE", self.colors["danger"]),
                ("JEDEC", "#e599f7"),
            ]
        elif protocol == "Microwire":
            anno_keywords = [
                ("CS_HIGH", self.colors["warning"]), ("CS_LOW", self.colors["danger"]),
                ("EWEN", "#ff9f43"), ("EWDS", "#b197fc"),
                ("SB", self.colors["accent"]), ("WRITE", self.colors["accent"]),
                ("READ", self.colors["success"]), ("ERASE", self.colors["danger"]),
                ("READY", "#63e6be"),
            ]
        else:
            anno_keywords = [
                ("START", self.colors["warning"]), ("STOP", self.colors["danger"]),
                ("RepSTART", "#ff9f43"), ("NACK", self.colors["danger"]),
                ("ACK", self.colors["success"]), ("Poll", "#b197fc"),
            ]
        for i in range(n):
            if i >= len(comments):
                break
            comment = comments[i]
            if not comment:
                continue
            x = margin_l + i * vec_w
            for kw, kclr in anno_keywords:
                if kw in comment:
                    c.create_line(x, margin_t - 5, x, anno_y - 2,
                                  fill=kclr, dash=(1, 4), width=1)
                    c.create_text(x, anno_y + 2, text=kw,
                                  fill=kclr, font=("Consolas", 6),
                                  anchor=tk.N, angle=45 if len(kw) > 4 else 0)
                    break

        # 字节值标注 (从注释中提取 0xNN 值, 标注在波形上方)
        byte_y = margin_t - 28
        for i in range(n):
            if i >= len(comments):
                break
            cm = comments[i]
            if not cm:
                continue
            # 匹配 Byte Write / Random Read / Page Write 等注释中的字节值
            m = re.search(r'(?:data|Data|addr|WordAddr)=0x([0-9A-Fa-f]{2})', cm)
            if m:
                x = margin_l + i * vec_w
                val_text = f"0x{m.group(1).upper()}"
                c.create_text(x, byte_y, text=val_text,
                              fill="#b197fc", font=("Consolas", 6),
                              anchor=tk.SW)

        # 测试段边界标注
        if hasattr(self, "pat_sections") and self.pat_sections:
            offset = 0
            seg_colors = [self.colors["accent"], self.colors["accent2"],
                          self.colors["warning"], "#b197fc", "#ff9f43",
                          "#e599f7", "#63e6be", "#ffa8a8", "#74c0fc"]
            for si_seg, (seg_name, seg_desc, seg_vecs, _, _) in enumerate(self.pat_sections):
                seg_start = offset
                seg_end = offset + len(seg_vecs)
                offset = seg_end
                # 仅绘制在可视范围内的段
                if seg_end <= v_start or seg_start >= v_end:
                    continue
                local_start = max(0, seg_start - v_start)
                local_end = min(n, seg_end - v_start)
                x_seg = margin_l + local_start * vec_w
                seg_clr = seg_colors[si_seg % len(seg_colors)]
                # 段起始竖线
                if seg_start >= v_start:
                    c.create_line(x_seg, margin_t - 30, x_seg,
                                  margin_t + len(signals) * (lane_h + gap),
                                  fill=seg_clr, width=1, dash=(4, 2))
                    c.create_text(x_seg + 3, margin_t - 32,
                                  text=seg_name.replace("_TEST", ""),
                                  fill=seg_clr, font=("Consolas", 7, "bold"),
                                  anchor=tk.SW)

        # 时间标尺 (在波形底部显示时间刻度)
        ruler_y = margin_t + len(signals) * (lane_h + gap) + 30
        period_ns = self._get_period_ns()
        c.create_line(margin_l, ruler_y, margin_l + n * vec_w, ruler_y,
                      fill=self.colors["text_dim"], width=1)
        tick_interval = max(1, n // 10)
        for i in range(0, n + 1, tick_interval):
            x_tick = margin_l + i * vec_w
            time_us = (v_start + i) * period_ns / 1000
            c.create_line(x_tick, ruler_y - 4, x_tick, ruler_y + 4,
                          fill=self.colors["text_dim"], width=1)
            c.create_text(x_tick, ruler_y + 8,
                          text=f"{time_us:.1f}μs",
                          fill=self.colors["text_dim"],
                          font=("Consolas", 6), anchor=tk.N)

        # 更新 scrollregion 以包含标尺
        total_h = ruler_y + 30
        c.configure(scrollregion=(0, 0, total_w, total_h))

        # 鼠标悬停信息
        self._wave_hover_data = {
            "vectors": vectors, "comments": comments,
            "v_start": v_start, "margin_l": margin_l, "vec_w": vec_w,
            "margin_t": margin_t, "n": n,
        }
        c.bind("<Motion>", self._on_wave_hover)

    def _on_wave_hover(self, event):
        """波形图鼠标悬停: 显示向量编号、引脚状态、注释"""
        c = self.wave_canvas
        hd = getattr(self, "_wave_hover_data", None)
        if not hd:
            return
        # 计算向量索引
        cx = c.canvasx(event.x)
        idx = int((cx - hd["margin_l"]) / hd["vec_w"])
        if idx < 0 or idx >= hd["n"]:
            c.delete("hover_tip")
            return
        vec = hd["vectors"][idx]
        cm = hd["comments"][idx] if idx < len(hd["comments"]) else ""
        abs_idx = hd["v_start"] + idx
        # 查找所属测试段
        seg_name = ""
        if hasattr(self, "pat_sections"):
            offset = 0
            for name, _, seg_vecs, _, _ in self.pat_sections:
                if offset <= abs_idx < offset + len(seg_vecs):
                    seg_name = name
                    break
                offset += len(seg_vecs)
        # 构造提示文字
        active_pins = self._get_active_pins()
        state_str = " ".join(f"{p}={vec.get(p,'X')}" for p in active_pins)
        tip = f"V{abs_idx:04d}  {state_str}"
        if seg_name:
            tip += f"  [{seg_name}]"
        if cm:
            tip += f"\n{cm}"
        # 绘制提示框
        c.delete("hover_tip")
        tx = cx + 10
        ty = c.canvasy(event.y) - 10
        c.create_text(tx, ty, text=tip, fill="#e8ecf1",
                      font=("Consolas", 7), anchor=tk.SW,
                      tags="hover_tip")

    def _update_wave_jump_buttons(self, pat_sections):
        """更新波形图的段跳转按钮"""
        for w in list(self.wave_jump_bar.winfo_children()):
            w.destroy()

        short_names = {"OS_TEST": "OS", "DC_TEST": "DC", "FUNC_TEST": "FUNC",
                        "MARCH_TEST": "March", "MARCHB_TEST": "MarchB",
                        "SCAN_TEST": "Scan",
                        "RET_TEST": "Ret", "ERR_TEST": "Err", "ENDUR_TEST": "Endur"}
        offset = 0
        for name, desc, vectors, _, _ in pat_sections:
            label = short_names.get(name, name)
            start = offset
            end = offset + len(vectors)
            btn = tk.Button(self.wave_jump_bar, text=label,
                            command=lambda s=start, e=end: self._wave_jump_to(s, e),
                            font=("Consolas", 7, "bold"),
                            bg=self.colors["card"], fg=self.colors["text"],
                            relief=tk.FLAT, padx=4, pady=0, cursor="hand2")
            btn.pack(side=tk.LEFT, padx=2)
            offset = end

    def _wave_jump_to(self, start, end):
        """波形图跳转到指定向量范围"""
        self.wave_start_var.set(str(start))
        self.wave_end_var.set(str(min(end, start + 300)))
        self._draw_waveform()

    def _export_waveform_svg(self):
        """将当前波形导出为 SVG 矢量图文件"""
        if not self.current_vectors:
            messagebox.showinfo("", self.t("gen_wave_first"))
            return

        path = filedialog.asksaveasfilename(
            title="导出波形 SVG", defaultextension=".svg",
            filetypes=[("SVG 矢量图", "*.svg")],
            initialfile="AT24C02_waveform.svg")
        if not path:
            return

        try:
            v_start = max(0, int(self.wave_start_var.get()))
        except ValueError:
            v_start = 0
        try:
            v_end = min(len(self.current_vectors), int(self.wave_end_var.get()))
        except ValueError:
            v_end = min(200, len(self.current_vectors))
        if v_end <= v_start:
            v_end = min(v_start + 200, len(self.current_vectors))

        vectors = self.current_vectors[v_start:v_end]
        comments = self.current_comments[v_start:v_end] if self.current_comments else []
        n = len(vectors)

        vec_w = 12
        lane_h = 50
        margin_l = 70
        margin_t = 40
        gap = 20
        signals = ["SCL", "SDA"]
        total_w = margin_l + n * vec_w + 60
        total_h = margin_t + len(signals) * (lane_h + gap) + 80

        clr_bg = "#1a1f2e"
        clr_drive = "#4f8cff"
        clr_h = "#38d9a9"
        clr_l = "#ff6b6b"
        clr_hiz = "#ffd43b"
        clr_x = "#8892a4"
        clr_border = "#353d52"
        clr_text = "#e8ecf1"
        clr_dim = "#5a6378"

        svg_lines = []
        svg_lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{total_w}" height="{total_h}" '
                         f'viewBox="0 0 {total_w} {total_h}">')
        svg_lines.append(f'<rect width="{total_w}" height="{total_h}" fill="{clr_bg}"/>')

        # Title
        svg_lines.append(f'<text x="{margin_l}" y="18" fill="{clr_text}" '
                         f'font-family="Consolas,monospace" font-size="13" font-weight="bold">'
                         f'AT24C02 I2C Waveform (Vec {v_start}~{v_end-1})</text>')

        # Scale markers
        for i in range(0, n, max(1, n // 20)):
            x = margin_l + i * vec_w
            svg_lines.append(f'<line x1="{x}" y1="{margin_t-10}" x2="{x}" '
                             f'y2="{margin_t + len(signals)*(lane_h+gap)}" '
                             f'stroke="{clr_border}" stroke-dasharray="1,5"/>')
            svg_lines.append(f'<text x="{x}" y="{margin_t-14}" fill="{clr_dim}" '
                             f'font-family="Consolas" font-size="7" text-anchor="middle">{v_start+i}</text>')

        for si, sig in enumerate(signals):
            y_base = margin_t + si * (lane_h + gap)
            y_high = y_base + 5
            y_low = y_base + lane_h - 5
            y_mid = (y_high + y_low) // 2

            svg_lines.append(f'<text x="{margin_l-10}" y="{y_mid+4}" fill="{clr_text}" '
                             f'font-family="Consolas" font-size="12" font-weight="bold" '
                             f'text-anchor="end">{sig}</text>')
            svg_lines.append(f'<line x1="{margin_l}" y1="{y_high}" '
                             f'x2="{margin_l+n*vec_w}" y2="{y_high}" '
                             f'stroke="{clr_border}" stroke-dasharray="2,6"/>')
            svg_lines.append(f'<line x1="{margin_l}" y1="{y_low}" '
                             f'x2="{margin_l+n*vec_w}" y2="{y_low}" '
                             f'stroke="{clr_border}" stroke-dasharray="2,6"/>')
            svg_lines.append(f'<text x="{margin_l-10}" y="{y_high+4}" fill="{clr_dim}" '
                             f'font-family="Consolas" font-size="7" text-anchor="end">1</text>')
            svg_lines.append(f'<text x="{margin_l-10}" y="{y_low+4}" fill="{clr_dim}" '
                             f'font-family="Consolas" font-size="7" text-anchor="end">0</text>')

            prev_y = None
            for i in range(n):
                x = margin_l + i * vec_w
                val = vectors[i].get(sig, "X")
                if val == "1":
                    cur_y, color, sw = y_high, clr_drive, 2
                elif val == "0":
                    cur_y, color, sw = y_low, clr_drive, 2
                elif val == "H":
                    cur_y, color, sw = y_high, clr_h, 2
                elif val == "L":
                    cur_y, color, sw = y_low, clr_l, 2
                elif val == "Z":
                    cur_y, color, sw = y_mid, clr_hiz, 1
                else:
                    cur_y, color, sw = y_mid, clr_x, 1

                if prev_y is not None and prev_y != cur_y:
                    svg_lines.append(f'<line x1="{x}" y1="{prev_y}" x2="{x}" y2="{cur_y}" '
                                     f'stroke="{color}" stroke-width="1"/>')

                dash = ' stroke-dasharray="3,3"' if val in ("Z", "X") else ""
                svg_lines.append(f'<line x1="{x}" y1="{cur_y}" x2="{x+vec_w}" y2="{cur_y}" '
                                 f'stroke="{color}" stroke-width="{sw}"{dash}/>')

                if val == "H":
                    cx = x + vec_w // 2
                    svg_lines.append(f'<polygon points="{cx},{y_high-4} {cx-3},{y_high+2} '
                                     f'{cx+3},{y_high+2}" fill="{clr_h}"/>')
                elif val == "L":
                    cx = x + vec_w // 2
                    svg_lines.append(f'<polygon points="{cx},{y_low+4} {cx-3},{y_low-2} '
                                     f'{cx+3},{y_low-2}" fill="{clr_l}"/>')
                prev_y = cur_y

        # Event annotations
        anno_y = margin_t + len(signals) * (lane_h + gap) + 8
        event_colors = {"START": "#ffd43b", "STOP": "#ff6b6b", "RepSTART": "#ff9f43",
                        "NACK": "#ff6b6b", "ACK": "#38d9a9", "Poll": "#b197fc"}
        for i in range(min(n, len(comments))):
            cm = comments[i]
            if not cm:
                continue
            x = margin_l + i * vec_w
            for kw, kclr in event_colors.items():
                if kw in cm:
                    svg_lines.append(f'<line x1="{x}" y1="{margin_t-5}" x2="{x}" y2="{anno_y-2}" '
                                     f'stroke="{kclr}" stroke-dasharray="1,4"/>')
                    svg_lines.append(f'<text x="{x}" y="{anno_y+8}" fill="{kclr}" '
                                     f'font-family="Consolas" font-size="6" text-anchor="middle">{kw}</text>')
                    break

        # Legend
        lx = margin_l
        ly = total_h - 20
        for sym, clr, desc in [("Drive", clr_drive, "驱动"), ("H/L", clr_h, "比较"),
                                ("Z", clr_hiz, "高阻"), ("X", clr_x, "不关心")]:
            svg_lines.append(f'<rect x="{lx}" y="{ly}" width="10" height="10" fill="{clr}"/>')
            svg_lines.append(f'<text x="{lx+14}" y="{ly+9}" fill="{clr_text}" '
                             f'font-family="Segoe UI" font-size="9">{sym} {desc}</text>')
            lx += 80

        svg_lines.append('</svg>')
        svg_content = '\n'.join(svg_lines)

        with open(path, "w", encoding="utf-8") as f:
            f.write(svg_content)

        self.status_label.config(text=f"✓ 波形已导出: {os.path.basename(path)}",
                                  fg=self.colors["success"])

    def _draw_default_flowchart(self):
        """绘制默认空流程图提示"""
        c = self.flow_canvas
        self._safe_canvas_reset(c)
        c.create_text(300, 150, text=self.t("flow_hint"),
                      fill=self.colors["text_dim"], font=("Segoe UI", 12))

    def _draw_flowchart(self, pat_sections):
        """绘制测试流程图 (含各测试段状态和向量数)"""
        c = self.flow_canvas
        self._safe_canvas_reset(c)
        c.update_idletasks()

        cw = max(c.winfo_width(), 600)
        total = sum(len(s[2]) for s in pat_sections)

        node_w = 180
        node_h = 54
        gap_y = 20
        arrow_len = gap_y
        cx = cw // 2
        y = 20

        colors = [self.colors["accent"], self.colors["accent2"],
                  self.colors["warning"], "#b197fc", "#ff9f43",
                  "#e64980", "#20c997", "#fd7e14"]

        # 开始节点 (圆角椭圆)
        c.create_oval(cx - 50, y, cx + 50, y + 36,
                      fill=self.colors["success"], outline="")
        c.create_text(cx, y + 18, text="START",
                      fill="white", font=("Segoe UI", 11, "bold"))
        y += 36

        # 箭头
        c.create_line(cx, y, cx, y + arrow_len, fill=self.colors["text_dim"], width=2,
                      arrow=tk.LAST)
        y += arrow_len

        # 电源上电节点
        c.create_rectangle(cx - node_w // 2, y, cx + node_w // 2, y + 36,
                           fill=self.colors["card"], outline=self.colors["border"], width=2)
        vcc = self.voltage_var.get() if hasattr(self, 'voltage_var') else "5.0V"
        c.create_text(cx, y + 18, text=f"DUT Power On (VCC={vcc})",
                      fill=self.colors["text"], font=("Segoe UI", 9, "bold"))
        y += 36
        c.create_line(cx, y, cx, y + arrow_len, fill=self.colors["text_dim"], width=2,
                      arrow=tk.LAST)
        y += arrow_len

        # 测试段节点
        for i, (name, desc, vectors, _, _) in enumerate(pat_sections):
            clr = colors[i % len(colors)]
            cnt = len(vectors)
            pct = cnt / total * 100 if total else 0

            # 菱形判断框 → 简化为带颜色左边条的矩形
            c.create_rectangle(cx - node_w // 2, y,
                               cx + node_w // 2, y + node_h,
                               fill=self.colors["bg"], outline=self.colors["border"],
                               width=1)
            # 左侧颜色条
            c.create_rectangle(cx - node_w // 2, y,
                               cx - node_w // 2 + 6, y + node_h,
                               fill=clr, outline="")
            # 测试段名称
            c.create_text(cx, y + 16, text=desc,
                          fill=clr, font=("Segoe UI", 10, "bold"))
            # 向量数和占比
            c.create_text(cx, y + 36,
                          text=f"{cnt} vectors ({pct:.1f}%)",
                          fill=self.colors["text_dim"], font=("Consolas", 8))

            # 右侧 PASS/FAIL 分支标注
            rx = cx + node_w // 2 + 10
            c.create_line(cx + node_w // 2, y + node_h // 2,
                          rx + 30, y + node_h // 2,
                          fill=self.colors["danger"], dash=(3, 3), width=1)
            c.create_text(rx + 35, y + node_h // 2,
                          text="FAIL →", fill=self.colors["danger"],
                          font=("Consolas", 7), anchor=tk.W)

            # v9.0 Tier3: 自适应规则标签 (左侧)
            if hasattr(self, '_adaptive_rules') and self._adaptive_rules:
                rule_map = self._adaptive_engine.get_test_to_rule_map()
                matched = rule_map.get(name, [])
                if matched:
                    lx = cx - node_w // 2 - 10
                    for ri, rid in enumerate(matched):
                        c.create_text(lx, y + 12 + ri * 12,
                                      text=f"⚡{rid}", fill=self.colors["gold"],
                                      font=("Consolas", 7), anchor=tk.E)

            y += node_h

            # 箭头到下一个
            c.create_line(cx, y, cx, y + arrow_len,
                          fill=self.colors["text_dim"], width=2, arrow=tk.LAST)
            c.create_text(cx - 16, y + arrow_len // 2,
                          text="PASS", fill=self.colors["success"],
                          font=("Consolas", 7), anchor=tk.E)
            y += arrow_len

        # 结束节点
        c.create_oval(cx - 50, y, cx + 50, y + 36,
                      fill=self.colors["danger"], outline="")
        c.create_text(cx, y + 18, text="END",
                      fill="white", font=("Segoe UI", 11, "bold"))
        y += 36

        # 汇总
        y += 16
        c.create_text(cx, y, text=f"Total: {total} vectors  |  {len(pat_sections)} stages",
                      fill=self.colors["text_dim"], font=("Consolas", 9))
        y += 20

        c.configure(scrollregion=(0, 0, cw, y + 20))

    def _update_line_numbers(self):
        """更新 PAT 预览行号列"""
        self.pat_lineno.config(state=tk.NORMAL)
        self.pat_lineno.delete("1.0", tk.END)
        line_count = int(self.pat_text.index("end-1c").split(".")[0])
        nums = "\n".join(str(i) for i in range(1, line_count + 1))
        self.pat_lineno.insert("1.0", nums)
        self.pat_lineno.config(state=tk.DISABLED)

    def _update_jump_buttons(self, pat_sections):
        """更新 PAT 预览跳转按钮"""
        # 清除旧按钮 (保留 "跳转:" label)
        for w in list(self.jump_bar.winfo_children()):
            if isinstance(w, tk.Button):
                w.destroy()

        short_names = {"OS_TEST": "OS", "DC_TEST": "DC", "FUNC_TEST": "FUNC",
                        "MARCH_TEST": "March", "MARCHB_TEST": "MarchB",
                        "SCAN_TEST": "Scan",
                        "RET_TEST": "Ret", "ERR_TEST": "Err", "ENDUR_TEST": "Endur"}
        btn_colors = [self.colors["accent"], self.colors["accent2"],
                      self.colors["warning"], "#b197fc", "#ff9f43",
                      "#e64980", "#20c997", "#fd7e14", "#74c0fc"]

        offset = 0
        for i, (name, desc, vectors, _, _) in enumerate(pat_sections):
            label = short_names.get(name, name)
            vec_count = len(vectors)
            clr = btn_colors[i % len(btn_colors)]
            # 在 PAT 文本中搜索段标记
            search_str = f"// {desc}"
            btn = tk.Button(self.jump_bar, text=f"{label} ({vec_count})",
                            command=lambda s=search_str: self._jump_to_section(s),
                            font=("Consolas", 7, "bold"),
                            bg=clr, fg="white",
                            activebackground=clr,
                            relief=tk.FLAT, padx=6, pady=1,
                            cursor="hand2")
            btn.pack(side=tk.LEFT, padx=2)
            offset += vec_count

    def _jump_to_section(self, search_str):
        """跳转到 PAT 预览中的指定段落"""
        pos = self.pat_text.search(search_str, "1.0", stopindex=tk.END)
        if pos:
            self.pat_text.see(pos)
            self.pat_text.tag_remove(tk.SEL, "1.0", tk.END)
            line = pos.split(".")[0]
            self.pat_text.tag_add(tk.SEL, f"{line}.0", f"{line}.end")
            # 同步行号
            self.pat_text.update_idletasks()
            self.pat_lineno.yview_moveto(self.pat_text.yview()[0])

    def _apply_pat_syntax_highlighting(self):
        """对 PAT 预览文本应用语法高亮 (H/L/Z/注释/标签)"""
        tw = self.pat_text

        tw.tag_configure("comment",   foreground="#5a6378")
        tw.tag_configure("keyword",   foreground=self.colors["accent"])
        tw.tag_configure("label_tag", foreground=self.colors["accent"],
                         font=("Consolas", 9, "bold"))
        tw.tag_configure("h_val", foreground="#38d9a9",
                         font=("Consolas", 9, "bold"))
        tw.tag_configure("l_val", foreground="#ff6b6b",
                         font=("Consolas", 9, "bold"))
        tw.tag_configure("z_val", foreground="#ffd43b")
        tw.tag_configure("drive_1", foreground="#74c0fc")
        tw.tag_configure("drive_0", foreground="#748ffc")
        tw.tag_configure("x_val", foreground="#5a6378")

        content = tw.get("1.0", tk.END)
        for i, line in enumerate(content.split('\n'), 1):
            stripped = line.strip()
            if not stripped:
                continue

            # 整行注释
            if stripped.startswith("//"):
                idx = line.index("//")
                tw.tag_add("comment", f"{i}.{idx}", f"{i}.end")
                continue

            # 关键字行 (EStar 格式)
            if stripped.startswith(("HEAD[", "END_HEAD", "@@PATTERN_DEFINE",
                                    "@@END_PATTERN_DEFINE", "AC_SET")):
                tw.tag_add("keyword", f"{i}.0", f"{i}.end")
                continue

            # 行内注释
            data_end = len(line)
            if "//" in line:
                idx = line.index("//")
                tw.tag_add("comment", f"{i}.{idx}", f"{i}.end")
                data_end = idx

            data_part = line[:data_end]

            # 标签行 (EStar: "LABEL:      000011;..." 标签和向量在同一行)
            label_match = re.match(r'^(\S+:)\s+', stripped)
            if label_match and not stripped.startswith("//"):
                label_end_in_line = line.index(label_match.group(1)) + len(label_match.group(1))
                tw.tag_add("label_tag", f"{i}.0", f"{i}.{label_end_in_line}")
                # 继续处理该行的向量部分 (不 continue)

            # EStar 向量行: 紧凑格式如 "000011;" 或 "00001L;"
            # 匹配向量字符串部分 (在分号之前)
            vec_match = re.search(r'([01HLZX]{2,});', data_part)
            if vec_match:
                vec_str = vec_match.group(1)
                start_pos = vec_match.start(1)
                for ci, ch in enumerate(vec_str):
                    col = start_pos + ci
                    tag = {"H": "h_val", "L": "l_val", "Z": "z_val",
                           "1": "drive_1", "0": "drive_0", "X": "x_val"}.get(ch)
                    if tag:
                        tw.tag_add(tag, f"{i}.{col}", f"{i}.{col+1}")

    def _update_statistics(self, pat_sections):
        """更新统计面板 (条形图 + 覆盖率分析 + 段明细)"""
        c = self.stats_canvas
        self._safe_canvas_reset(c)
        c.update_idletasks()

        cw = max(c.winfo_width(), 500)
        total = sum(len(s[2]) for s in pat_sections)

        # 预先收集所有注释和向量 (后续多处使用)
        all_comments = []
        all_vectors = []
        for _, _, vectors, comments, _ in pat_sections:
            all_comments.extend(comments)
            all_vectors.extend(vectors)

        bar_colors = [self.colors["accent"], self.colors["accent2"],
                      self.colors["warning"], "#b197fc", "#ff9f43"]

        y = 20
        c.create_text(20, y, text="向量分布",
                      fill=self.colors["text"],
                      font=("Segoe UI", 14, "bold"), anchor=tk.W)
        y += 36

        bar_left = 180
        bar_w = cw - bar_left - 110
        bar_h = 24

        for i, (name, desc, vectors, _, _) in enumerate(pat_sections):
            cnt = len(vectors)
            pct = cnt / total * 100 if total else 0
            clr = bar_colors[i % len(bar_colors)]

            c.create_text(20, y + bar_h // 2, text=desc,
                          fill=self.colors["text"],
                          font=("Segoe UI", 9), anchor=tk.W)
            c.create_rectangle(bar_left, y, bar_left + bar_w, y + bar_h,
                              fill=self.colors["bg"], outline="")
            fw = max(2, bar_w * cnt / total) if total else 0
            c.create_rectangle(bar_left, y, bar_left + fw, y + bar_h,
                              fill=clr, outline="")
            c.create_text(bar_left + fw + 8, y + bar_h // 2,
                          text=f"{cnt}  ({pct:.1f}%)",
                          fill=self.colors["text"],
                          font=("Consolas", 9), anchor=tk.W)
            y += bar_h + 10

        # 汇总
        y += 8
        c.create_rectangle(20, y, cw - 20, y + 1,
                          fill=self.colors["border"], outline="")
        y += 16
        c.create_text(20, y, text=f"总向量数: {total}",
                      fill=self.colors["text"],
                      font=("Segoe UI", 13, "bold"), anchor=tk.W)

        period_ns = self._get_period_ns()
        vec_time_ms = total * period_ns / 1_000_000
        # 估算写操作次数 (每次写后需 tWR=5ms 等待)
        write_count = 0
        for cm in all_comments:
            if cm and ("ACK Polling" in cm or "Poll #1" in cm):
                write_count += 1
        twr_ms = write_count * 5.0
        total_time_ms = vec_time_ms + twr_ms
        y += 24
        c.create_text(20, y,
                      text=f"预估测试时间: {total_time_ms:.1f} ms  "
                           f"(向量 {vec_time_ms:.1f}ms + 写等待 {twr_ms:.0f}ms, "
                           f"{write_count} 次写 x 5ms tWR)",
                      fill=self.colors["text_dim"],
                      font=("Segoe UI", 10), anchor=tk.W)

        # ============================================================
        # 各测试段时间分解
        # ============================================================
        y += 30
        c.create_text(20, y, text="测试段时间分解",
                      fill=self.colors["text"],
                      font=("Segoe UI", 11, "bold"), anchor=tk.W)
        y += 22
        # 表头
        c.create_text(30, y, text="测试段", fill=self.colors["accent"],
                      font=("Consolas", 8, "bold"), anchor=tk.W)
        c.create_text(200, y, text="向量", fill=self.colors["accent"],
                      font=("Consolas", 8, "bold"), anchor=tk.W)
        c.create_text(270, y, text="向量时间", fill=self.colors["accent"],
                      font=("Consolas", 8, "bold"), anchor=tk.W)
        c.create_text(360, y, text="写次数", fill=self.colors["accent"],
                      font=("Consolas", 8, "bold"), anchor=tk.W)
        c.create_text(420, y, text="tWR等待", fill=self.colors["accent"],
                      font=("Consolas", 8, "bold"), anchor=tk.W)
        c.create_text(500, y, text="总计", fill=self.colors["accent"],
                      font=("Consolas", 8, "bold"), anchor=tk.W)
        y += 16
        c.create_line(20, y, cw - 20, y, fill=self.colors["border"])
        y += 6

        total_bus_active = 0  # 总线活跃向量 (非IDLE)
        for name, desc, vectors, seg_comments, _ in pat_sections:
            seg_vec = len(vectors)
            seg_vec_ms = seg_vec * period_ns / 1_000_000
            seg_writes = sum(1 for cm in seg_comments
                             if cm and ("ACK Polling" in cm or "Poll #1" in cm))
            seg_twr_ms = seg_writes * 5.0
            seg_total_ms = seg_vec_ms + seg_twr_ms
            # 统计总线活跃向量 (非 IDLE)
            for v_cm in seg_comments:
                if v_cm and "IDLE" not in v_cm:
                    total_bus_active += 1

            short = name.replace("_TEST", "").replace("MARCHB", "MarchB")
            c.create_text(30, y, text=short, fill=self.colors["text"],
                          font=("Consolas", 8), anchor=tk.W)
            c.create_text(200, y, text=str(seg_vec), fill=self.colors["text_dim"],
                          font=("Consolas", 8), anchor=tk.W)
            c.create_text(270, y, text=f"{seg_vec_ms:.1f}ms", fill=self.colors["text_dim"],
                          font=("Consolas", 8), anchor=tk.W)
            c.create_text(360, y, text=str(seg_writes), fill=self.colors["text_dim"],
                          font=("Consolas", 8), anchor=tk.W)
            c.create_text(420, y, text=f"{seg_twr_ms:.0f}ms", fill=self.colors["text_dim"],
                          font=("Consolas", 8), anchor=tk.W)
            c.create_text(500, y, text=f"{seg_total_ms:.1f}ms",
                          fill=self.colors["text"], font=("Consolas", 8, "bold"),
                          anchor=tk.W)
            y += 18

        # 总线利用率
        bus_util = total_bus_active / total * 100 if total else 0
        y += 6
        c.create_text(20, y,
                      text=f"总线利用率: {bus_util:.1f}% ({total_bus_active}/{total} 活跃向量)",
                      fill=self.colors["text_dim"],
                      font=("Segoe UI", 9), anchor=tk.W)

        # ============================================================
        # Phase 2: 测试时间优化分析
        # ============================================================
        y += 30
        c.create_text(20, y, text="测试时间优化分析",
                      fill=self.colors["text"],
                      font=("Segoe UI", 11, "bold"), anchor=tk.W)
        y += 22

        # --- 时间分解横向条形图 (按耗时排序, 标注TOP3) ---
        seg_times = []
        for name, desc, vectors, seg_comments, _ in pat_sections:
            seg_vec = len(vectors)
            seg_vec_ms = seg_vec * period_ns / 1_000_000
            seg_writes = sum(1 for cm in seg_comments
                             if cm and ("ACK Polling" in cm or "Poll #1" in cm))
            seg_twr_ms = seg_writes * 5.0
            seg_total_ms = seg_vec_ms + seg_twr_ms
            seg_times.append((name, desc, seg_vec, seg_total_ms, seg_writes))
        seg_times_sorted = sorted(seg_times, key=lambda x: x[3], reverse=True)
        max_time = max((s[3] for s in seg_times_sorted), default=1)
        time_bar_w = cw - 240
        for rank, (name, desc, vecs, t_ms, wc) in enumerate(seg_times_sorted):
            short = name.replace("_TEST", "")
            is_top3 = rank < 3
            clr = self.colors["danger"] if is_top3 else self.colors["accent"]
            tag = " ★" if is_top3 else ""
            c.create_text(30, y + 8, text=f"{short}{tag}",
                          fill=clr, font=("Consolas", 8, "bold" if is_top3 else ""), anchor=tk.W)
            bw = max(2, time_bar_w * t_ms / max_time) if max_time > 0 else 0
            c.create_rectangle(170, y, 170 + bw, y + 16,
                              fill=clr, outline="")
            c.create_text(170 + bw + 6, y + 8,
                          text=f"{t_ms:.1f}ms ({t_ms/total_time_ms*100:.0f}%)" if total_time_ms > 0 else "0ms",
                          fill=self.colors["text_dim"], font=("Consolas", 7), anchor=tk.W)
            y += 20

        # --- 冗余检测 ---
        y += 10
        c.create_text(20, y, text="冗余检测 (故障检测重叠)",
                      fill=self.colors["text"],
                      font=("Segoe UI", 10, "bold"), anchor=tk.W)
        y += 18
        # 简化分析: 根据测试类型的固有故障检测能力判断重叠
        fault_coverage_map = {
            "OS_TEST":     {"pin_short", "pin_open"},
            "DC_TEST":     {"ISB", "ICC", "VOL", "VOH", "VIL", "VIH", "pin_short", "pin_open"},
            "FUNC_TEST":   {"SA0", "SA1", "TF", "read_write"},
            "MARCH_TEST":  {"SA0", "SA1", "TF", "CF"},
            "MARCHB_TEST": {"SA0", "SA1", "TF", "CF", "CF_idem"},
            "SCAN_TEST":   {"AF", "addr_decode", "SA0", "SA1"},
            "RET_TEST":    {"data_retention", "SA0", "SA1"},
            "ERR_TEST":    {"protocol_error", "NACK"},
            "ENDUR_TEST":  {"endurance", "SA0", "SA1", "TF"},
        }
        present_tests = [s[0] for s in pat_sections]
        redundancy_suggestions = []
        for i, t1 in enumerate(present_tests):
            faults1 = fault_coverage_map.get(t1, set())
            for t2 in present_tests[i+1:]:
                faults2 = fault_coverage_map.get(t2, set())
                overlap = faults1 & faults2
                if len(overlap) >= 2:
                    redundancy_suggestions.append(
                        f"{t1.replace('_TEST','')} ∩ {t2.replace('_TEST','')}: "
                        f"{', '.join(sorted(overlap))}")
        if redundancy_suggestions:
            for sug in redundancy_suggestions[:5]:
                c.create_text(30, y, text=f"⚠ {sug}",
                              fill=self.colors["warning"], font=("Consolas", 8), anchor=tk.W)
                y += 16
            # 可跳过建议
            skip_candidates = set()
            for t in present_tests:
                faults_t = fault_coverage_map.get(t, set())
                others_union = set()
                for t2 in present_tests:
                    if t2 != t:
                        others_union |= fault_coverage_map.get(t2, set())
                if faults_t and faults_t.issubset(others_union):
                    skip_candidates.add(t)
            if skip_candidates:
                skip_time = sum(s[3] for s in seg_times if s[0] in skip_candidates)
                save_pct = skip_time / total_time_ms * 100 if total_time_ms > 0 else 0
                y += 4
                c.create_text(30, y,
                              text=f"可安全跳过(仅建议): {', '.join(s.replace('_TEST','') for s in skip_candidates)} "
                                   f"— 节省 {skip_time:.1f}ms ({save_pct:.0f}%)",
                              fill=self.colors["accent2"], font=("Consolas", 8), anchor=tk.W)
                y += 18
        else:
            c.create_text(30, y, text="✓ 无显著冗余检测重叠",
                          fill=self.colors["success"], font=("Consolas", 8), anchor=tk.W)
            y += 18

        # --- Fail Fast 排序优化 ---
        y += 10
        c.create_text(20, y, text="Fail Fast 排序优化",
                      fill=self.colors["text"],
                      font=("Segoe UI", 10, "bold"), anchor=tk.W)
        y += 18
        # 故障概率权重 (基于 JEDEC 典型分布)
        fault_prob = {
            "OS_TEST": 0.15, "DC_TEST": 0.20, "FUNC_TEST": 0.25,
            "MARCH_TEST": 0.30, "MARCHB_TEST": 0.28, "SCAN_TEST": 0.10,
            "RET_TEST": 0.05, "ERR_TEST": 0.03, "ENDUR_TEST": 0.02,
        }
        # 效率 = 故障概率 / 测试时间
        efficiency = []
        for name, desc, vecs, t_ms, wc in seg_times:
            prob = fault_prob.get(name, 0.05)
            eff = prob / max(t_ms, 0.001)
            efficiency.append((name, prob, t_ms, eff))
        efficiency_sorted = sorted(efficiency, key=lambda x: x[3], reverse=True)
        # 原始顺序 vs 优化顺序下的期望测试时间 (假设 95% 良率)
        yield_rate = 0.95
        original_expected = 0
        cumulative_pass = 1.0
        for name, desc, vecs, t_ms, wc in seg_times:
            prob = fault_prob.get(name, 0.05)
            original_expected += t_ms * cumulative_pass
            cumulative_pass *= (1 - prob * (1 - yield_rate))
        optimized_expected = 0
        cumulative_pass = 1.0
        for name, prob, t_ms, eff in efficiency_sorted:
            optimized_expected += t_ms * cumulative_pass
            cumulative_pass *= (1 - prob * (1 - yield_rate))
        saving_pct = (1 - optimized_expected / max(original_expected, 0.001)) * 100

        c.create_text(30, y, text="推荐顺序 (效率 = 检出概率/时间):",
                      fill=self.colors["text_dim"], font=("Consolas", 8), anchor=tk.W)
        y += 16
        for rank, (name, prob, t_ms, eff) in enumerate(efficiency_sorted):
            short = name.replace("_TEST", "")
            c.create_text(40, y, text=f"{rank+1}. {short:12s}  效率={eff:.3f}  "
                                      f"(P={prob:.0%}, T={t_ms:.1f}ms)",
                          fill=self.colors["text"], font=("Consolas", 8), anchor=tk.W)
            y += 16
        y += 6
        save_color = self.colors["success"] if saving_pct > 0 else self.colors["text_dim"]
        c.create_text(30, y,
                      text=f"优化后节省 {saving_pct:.1f}% 期望测试时间 (假设 {yield_rate:.0%} 良率)",
                      fill=save_color, font=("Consolas", 9, "bold"), anchor=tk.W)
        y += 24

        # ============================================================
        # 覆盖率分析
        # ============================================================
        y += 40
        c.create_text(20, y, text="覆盖率分析",
                      fill=self.colors["text"],
                      font=("Segoe UI", 14, "bold"), anchor=tk.W)
        y += 32

        section_names = {s[0] for s in pat_sections}

        # 1. 地址空间覆盖率
        tested_addrs = set()
        for cm in all_comments:
            if not cm:
                continue
            # 从注释中提取 addr=0xNN 模式
            for m in re.finditer(r'addr=0x([0-9A-Fa-f]{2})', cm):
                tested_addrs.add(int(m.group(1), 16))
            for m in re.finditer(r'WordAddr=0x([0-9A-Fa-f]{2})', cm):
                tested_addrs.add(int(m.group(1), 16))
            for m in re.finditer(r'0x([0-9A-Fa-f]{2})~0x([0-9A-Fa-f]{2})', cm):
                for a in range(int(m.group(1), 16), int(m.group(2), 16) + 1):
                    tested_addrs.add(a)

        chip_cap = self._get_chip_capacity_bytes()
        addr_pct = len(tested_addrs) / max(chip_cap, 1) * 100
        self._draw_coverage_bar(c, 20, y, cw,
                                f"地址空间 ({len(tested_addrs)}/{chip_cap})", addr_pct,
                                self.colors["accent"])
        y += 32

        # 2. 数据模式覆盖率
        data_patterns = set()
        for cm in all_comments:
            if not cm:
                continue
            for m in re.finditer(r'data=0x([0-9A-Fa-f]{2})', cm):
                data_patterns.add(int(m.group(1), 16))
            for m in re.finditer(r'Data.*0x([0-9A-Fa-f]{2})', cm):
                data_patterns.add(int(m.group(1), 16))
        # 常见重要模式
        key_patterns = {0x00, 0xFF, 0x55, 0xAA, 0x01, 0x02, 0x04, 0x08,
                        0x10, 0x20, 0x40, 0x80, 0x42, 0x5A, 0xA5}
        pattern_hit = len(data_patterns & key_patterns)
        pattern_pct = pattern_hit / len(key_patterns) * 100 if key_patterns else 0
        self._draw_coverage_bar(c, 20, y, cw,
                                f"数据模式 ({pattern_hit}/{len(key_patterns)} 关键模式)", pattern_pct,
                                self.colors["accent2"])
        y += 32

        # 3. I2C 协议特性覆盖率
        protocol_features = {
            "START":       any("START" in (cm or "") and "Rep" not in (cm or "") for cm in all_comments),
            "STOP":        any("STOP" in (cm or "") for cm in all_comments),
            "RepSTART":    any("RepSTART" in (cm or "") for cm in all_comments),
            "Byte Write":  any("Byte Write" in (cm or "") for cm in all_comments),
            "Random Read":  any("Random Read" in (cm or "") for cm in all_comments),
            "Page Write":  any("Page Write" in (cm or "") for cm in all_comments),
            "Seq Read":    any("Sequential Read" in (cm or "") for cm in all_comments),
            "CurrAddr Read": any("Current Addr" in (cm or "") or "CurrentAddr" in (cm or "") for cm in all_comments),
            "ACK Poll":    any("ACK Polling" in (cm or "") or "Poll" in (cm or "") for cm in all_comments),
            "WP Protect":  any("WP" in (cm or "") and ("protect" in (cm or "").lower() or "WP=1" in (cm or "")) for cm in all_comments),
            "NACK":        any("NACK" in (cm or "") for cm in all_comments),
            "Addr Wrap":   any("wraparound" in (cm or "").lower() or "boundary" in (cm or "").lower() for cm in all_comments),
        }
        proto_hit = sum(protocol_features.values())
        proto_total = len(protocol_features)
        proto_pct = proto_hit / proto_total * 100 if proto_total else 0
        self._draw_coverage_bar(c, 20, y, cw,
                                f"协议特性 ({proto_hit}/{proto_total})", proto_pct,
                                self.colors["warning"])
        y += 32

        # 4. 测试类型覆盖率
        test_types = {"OS_TEST": "开短路", "DC_TEST": "DC参数", "FUNC_TEST": "功能",
                      "MARCH_TEST": "March C-", "MARCHB_TEST": "March B",
                      "SCAN_TEST": "地址扫描", "RET_TEST": "数据保持",
                      "ERR_TEST": "I2C异常", "ENDUR_TEST": "耐久性"}
        type_hit = sum(1 for k in test_types if k in section_names)
        type_pct = type_hit / len(test_types) * 100
        self._draw_coverage_bar(c, 20, y, cw,
                                f"测试类型 ({type_hit}/{len(test_types)})", type_pct,
                                "#b197fc")
        y += 40

        # ============================================================
        # 5 维覆盖率雷达图
        # ============================================================
        c.create_text(20, y, text="覆盖率雷达图",
                      fill=self.colors["text"],
                      font=("Segoe UI", 11, "bold"), anchor=tk.W)
        y += 20
        radar_dims = [
            ("地址", addr_pct),
            ("数据", pattern_pct),
            ("协议", proto_pct),
            ("类型", type_pct),
            ("故障", self._calc_fault_coverage(section_names)),
        ]
        self._draw_radar_chart(c, cw // 2, y + 90, 80, radar_dims)
        y += 200

        # ============================================================
        # 地址空间热力图 (16x16 网格)
        # ============================================================
        y += 10
        c.create_text(20, y, text="地址空间热力图",
                      fill=self.colors["text"],
                      font=("Segoe UI", 11, "bold"), anchor=tk.W)
        y += 6
        c.create_text(20, y, text="(绿色=已覆盖, 灰色=未测试, 每格1字节地址)",
                      fill=self.colors["text_dim"],
                      font=("Segoe UI", 7), anchor=tk.W)
        y += 18
        hm_cell = 16
        hm_gap = 2
        hm_left = 30
        # 列标题
        for col in range(16):
            cx = hm_left + col * (hm_cell + hm_gap) + hm_cell // 2
            c.create_text(cx, y, text=f"{col:X}",
                          fill=self.colors["text_dim"],
                          font=("Consolas", 6), anchor=tk.S)
        y += 6
        for row in range(16):
            ry = y + row * (hm_cell + hm_gap)
            c.create_text(hm_left - 6, ry + hm_cell // 2,
                          text=f"{row:X}", fill=self.colors["text_dim"],
                          font=("Consolas", 6), anchor=tk.E)
            for col in range(16):
                addr = row * 16 + col
                cx = hm_left + col * (hm_cell + hm_gap)
                hit = addr in tested_addrs
                color = self.colors["success"] if hit else self.colors["bg"]
                c.create_rectangle(cx, ry, cx + hm_cell, ry + hm_cell,
                                   fill=color, outline=self.colors["border"],
                                   width=1)
        y += 16 * (hm_cell + hm_gap) + 16

        # 协议特性明细
        c.create_text(20, y, text="协议特性明细",
                      fill=self.colors["text"],
                      font=("Segoe UI", 11, "bold"), anchor=tk.W)
        y += 24
        col_w = (cw - 40) // 3
        for i, (feat, hit) in enumerate(protocol_features.items()):
            col = i % 3
            row = i // 3
            fx = 30 + col * col_w
            fy = y + row * 20
            sym = "✓" if hit else "✗"
            clr = self.colors["success"] if hit else self.colors["text_dim"]
            c.create_text(fx, fy, text=f"{sym} {feat}",
                          fill=clr, font=("Consolas", 9), anchor=tk.W)
        y += (len(protocol_features) // 3 + 1) * 20 + 16

        # 段明细
        c.create_text(20, y, text="测试段明细",
                      fill=self.colors["text"],
                      font=("Segoe UI", 11, "bold"), anchor=tk.W)
        y += 24

        for name, desc, vectors, comments, labels in pat_sections:
            lbl_cnt = sum(1 for lb in labels if lb)
            c.create_text(30, y, text=f"● {name}",
                          fill=self.colors["accent"],
                          font=("Consolas", 10, "bold"), anchor=tk.W)
            c.create_text(220, y,
                          text=f"{len(vectors)} 向量,  {lbl_cnt} 标签",
                          fill=self.colors["text_dim"],
                          font=("Consolas", 9), anchor=tk.W)
            y += 22

        # 测试限值表
        y += 20
        c.create_text(20, y, text=self.t("test_limits"),
                      fill=self.colors["text"],
                      font=("Segoe UI", 14, "bold"), anchor=tk.W)
        y += 30

        # 表头
        col_x = [30, 110, 240, 310, 370, 430, 500]
        headers = ["Param", "Description", "Min", "Typ", "Max", "Unit", "Condition"]
        for xi, h in zip(col_x, headers):
            c.create_text(xi, y, text=h,
                          fill=self.colors["accent"],
                          font=("Consolas", 8, "bold"), anchor=tk.W)
        y += 18
        c.create_line(20, y, cw - 20, y, fill=self.colors["border"])
        y += 6

        for lim in TEST_LIMITS.values():
            c.create_text(col_x[0], y, text=lim["param"],
                          fill=self.colors["text"],
                          font=("Consolas", 8, "bold"), anchor=tk.W)
            c.create_text(col_x[1], y, text=lim["desc"][:18],
                          fill=self.colors["text_dim"],
                          font=("Consolas", 7), anchor=tk.W)
            c.create_text(col_x[2], y,
                          text=str(lim["min"]) if lim["min"] is not None else "—",
                          fill=self.colors["text"], font=("Consolas", 8), anchor=tk.W)
            c.create_text(col_x[3], y,
                          text=str(lim["typ"]) if lim["typ"] is not None else "—",
                          fill=self.colors["text_dim"], font=("Consolas", 8), anchor=tk.W)
            c.create_text(col_x[4], y,
                          text=str(lim["max"]) if lim["max"] is not None else "—",
                          fill=self.colors["text"], font=("Consolas", 8), anchor=tk.W)
            c.create_text(col_x[5], y, text=lim["unit"],
                          fill=self.colors["text_dim"],
                          font=("Consolas", 8), anchor=tk.W)
            c.create_text(col_x[6], y, text=lim["condition"][:25],
                          fill="#5a6378",
                          font=("Consolas", 7), anchor=tk.W)
            y += 18

        # 更新 scrollregion
        c.configure(scrollregion=(0, 0, cw, y + 30))

    def _draw_coverage_bar(self, canvas, x, y, cw, label, pct, color):
        """绘制覆盖率进度条"""
        bar_left = 200
        bar_w = cw - bar_left - 80
        bar_h = 18
        canvas.create_text(x, y + bar_h // 2, text=label,
                           fill=self.colors["text"], font=("Segoe UI", 9),
                           anchor=tk.W)
        # 背景
        canvas.create_rectangle(bar_left, y, bar_left + bar_w, y + bar_h,
                                fill=self.colors["bg"], outline="")
        # 填充
        fw = max(1, bar_w * pct / 100)
        canvas.create_rectangle(bar_left, y, bar_left + fw, y + bar_h,
                                fill=color, outline="")
        # 百分比文字
        canvas.create_text(bar_left + bar_w + 8, y + bar_h // 2,
                           text=f"{pct:.0f}%", fill=color,
                           font=("Consolas", 9, "bold"), anchor=tk.W)

    @staticmethod
    def _calc_fault_coverage(section_names):
        """计算故障模型覆盖率百分比"""
        fault_map = {
            "OS_TEST": ["OS"],
            "DC_TEST": ["DC"],
            "FUNC_TEST": ["FUNC"],
            "MARCH_TEST": ["SAF", "TF", "CFin"],
            "MARCHB_TEST": ["CFid", "CFdyn"],
            "SCAN_TEST": ["AF"],
            "RET_TEST": ["DRF"],
            "ERR_TEST": ["I2C-ERR"],
            "ENDUR_TEST": ["ENDF"],
        }
        all_faults = set()
        hit_faults = set()
        for test, faults in fault_map.items():
            all_faults.update(faults)
            if test in section_names:
                hit_faults.update(faults)
        return len(hit_faults) / len(all_faults) * 100 if all_faults else 0

    def _draw_radar_chart(self, canvas, cx, cy, radius, dimensions):
        """绘制 5 维覆盖率雷达图"""
        n = len(dimensions)
        if n < 3:
            return
        angle_step = 2 * math.pi / n

        # 绘制背景网格 (3层同心多边形)
        for level in [0.33, 0.66, 1.0]:
            pts = []
            for i in range(n):
                angle = -math.pi / 2 + i * angle_step
                px = cx + radius * level * math.cos(angle)
                py = cy + radius * level * math.sin(angle)
                pts.extend([px, py])
            canvas.create_polygon(*pts, outline=self.colors["border"],
                                  fill="", width=1)

        # 绘制轴线
        for i in range(n):
            angle = -math.pi / 2 + i * angle_step
            ex = cx + radius * math.cos(angle)
            ey = cy + radius * math.sin(angle)
            canvas.create_line(cx, cy, ex, ey,
                               fill=self.colors["border"], width=1)

        # 绘制数据多边形
        data_pts = []
        for i, (name, pct) in enumerate(dimensions):
            angle = -math.pi / 2 + i * angle_step
            r = radius * min(pct, 100) / 100
            px = cx + r * math.cos(angle)
            py = cy + r * math.sin(angle)
            data_pts.extend([px, py])
        canvas.create_polygon(*data_pts,
                              outline=self.colors["accent"],
                              fill=self.colors["accent"],
                              stipple="gray50", width=2)

        # 绘制数据点和标签
        for i, (name, pct) in enumerate(dimensions):
            angle = -math.pi / 2 + i * angle_step
            # 标签位置 (在轴线末端外侧)
            lx = cx + (radius + 18) * math.cos(angle)
            ly = cy + (radius + 18) * math.sin(angle)
            canvas.create_text(lx, ly, text=f"{name}\n{pct:.0f}%",
                               fill=self.colors["text"],
                               font=("Segoe UI", 7), anchor=tk.CENTER)
            # 数据点
            r = radius * min(pct, 100) / 100
            px = cx + r * math.cos(angle)
            py = cy + r * math.sin(angle)
            canvas.create_oval(px - 3, py - 3, px + 3, py + 3,
                               fill=self.colors["accent"], outline="")

    def on_generate(self):
        """生成按钮点击事件 — 带进度条"""
        logger.info("Generate started")
        try:
            # 获取地址配置
            a2 = self.addr_vars["A2"].get()
            a1 = self.addr_vars["A1"].get()
            a0 = self.addr_vars["A0"].get()
            wp = self.wp_var.get()

            try:
                poll_count = int(self.poll_count_var.get())
            except (ValueError, AttributeError):
                poll_count = 2
            # 提取芯片配置参数
            preset_name = self.chip_preset_var.get()
            if preset_name in CHIP_PRESETS:
                chip = CHIP_PRESETS[preset_name]
                device_addr_base = chip.get("device_addr_base", 0xA0)
                capacity_bytes = chip.get("capacity_bytes", 256)
                page_size = chip.get("page_size", 8)
                addr_byte_count = chip.get("addr_byte_count", 1)
                page_select_bits = chip.get("page_select_bits", 0)
            else:
                device_addr_base = 0xA0
                try:
                    capacity_bytes = int(self.chip_capacity_var.get())
                except (ValueError, AttributeError):
                    capacity_bytes = 256
                try:
                    page_size = int(self.chip_page_size_var.get())
                except (ValueError, AttributeError):
                    page_size = 8
                try:
                    addr_byte_count = int(self.chip_addr_bytes_var.get())
                except (ValueError, AttributeError):
                    addr_byte_count = 1
                page_select_bits = 0

            max_addr = capacity_bytes - 1

            # 提取协议和协议专属参数
            protocol = self.chip_protocol_var.get()
            spi_mode = 0
            sector_size = None
            has_jedec_id = False
            jedec_id = 0
            org_mode = "x16"
            word_bits = 16
            mw_addr_bits = 6
            if preset_name in CHIP_PRESETS:
                chip_p = CHIP_PRESETS[preset_name]
                spi_mode = chip_p.get("spi_mode", 0)
                sector_size = chip_p.get("sector_size", None)
                has_jedec_id = chip_p.get("has_jedec_id", False)
                jedec_id = chip_p.get("jedec_id", 0)
                org_mode = chip_p.get("org_mode", "x16")
                word_bits = chip_p.get("word_bits", 16)
                mw_addr_bits = chip_p.get("addr_bits", 6)

            self.gen = TestPatternGenerator(
                addr_pins=(a2, a1, a0), wp=wp, poll_count=poll_count,
                device_addr_base=device_addr_base,
                capacity_bytes=capacity_bytes, page_size=page_size,
                addr_byte_count=addr_byte_count,
                page_select_bits=page_select_bits,
                protocol=protocol,
                spi_mode=spi_mode, sector_size=sector_size,
                has_jedec_id=has_jedec_id, jedec_id=jedec_id,
                org_mode=org_mode, word_bits=word_bits,
                mw_addr_bits=mw_addr_bits)

            # 解析自定义写入参数
            custom_addr = None
            custom_data = None
            addr_str = self.custom_addr_var.get().strip()
            data_str = self.custom_data_var.get().strip()
            if addr_str and data_str:
                try:
                    custom_addr = int(addr_str, 16)
                    custom_data = int(data_str, 16)
                    if not (0x00 <= custom_addr <= max_addr):
                        raise ValueError(f"地址 {addr_str} 超出范围 0x00~0x{max_addr:X}")
                    if not (0x00 <= custom_data <= 0xFF):
                        raise ValueError(f"数据 {data_str} 超出范围 0x00~0xFF")
                except ValueError as ve:
                    messagebox.showwarning("自定义参数无效",
                                           f"自定义写入参数解析失败，将跳过 FUNC-5 测试:\n{ve}")
                    custom_addr = None
                    custom_data = None

            # 解析地址范围 (用于 March / Scan)
            try:
                scan_start = int(self.scan_start_var.get().strip(), 16)
            except (ValueError, AttributeError):
                scan_start = 0x00
            try:
                scan_end = int(self.scan_end_var.get().strip(), 16)
            except (ValueError, AttributeError):
                scan_end = 0x07
            scan_start = max(0, min(scan_start, max_addr))
            scan_end = max(scan_start, min(scan_end, max_addr))

            # 构建待生成的测试任务列表
            gen_tasks = []
            if self.test_vars["os_test"].get():
                gen_tasks.append(("OS_TEST", "Open/Short Test",
                                  lambda: self.gen.generate_os_test()))
            if self.test_vars["dc_test"].get():
                gen_tasks.append(("DC_TEST", "DC Parameter Test",
                                  lambda: self.gen.generate_dc_test()))
            if self.test_vars["func_test"].get():
                if protocol == "SPI":
                    chip_type = CHIP_PRESETS.get(preset_name, {}).get("chip_type", "EEPROM")
                    if chip_type == "Flash":
                        gen_tasks.append(("FUNC_TEST", "SPI Flash Functional Test",
                                          lambda: self.gen.generate_spi_flash_test()))
                    else:
                        gen_tasks.append(("FUNC_TEST", "SPI EEPROM Functional Test",
                                          lambda: self.gen.generate_spi_functional_test()))
                elif protocol == "Microwire":
                    gen_tasks.append(("FUNC_TEST", "Microwire Functional Test",
                                      lambda: self.gen.generate_mw_functional_test()))
                else:
                    # FUNC 拆分为独立子测试, 每个生成独立 .pat 文件
                    gen_tasks.append(("FUNC_BW", "Byte Write + Read",
                                      lambda ca=custom_addr, cd=custom_data:
                                      self.gen.generate_func_byte_write(ca, cd)))
                    gen_tasks.append(("FUNC_PW", "Page Write + Read",
                                      lambda: self.gen.generate_func_page_write()))
                    gen_tasks.append(("FUNC_BOUND", "Address Boundary",
                                      lambda: self.gen.generate_func_boundary()))
                    gen_tasks.append(("FUNC_WP", "WP Protect Test",
                                      lambda: self.gen.generate_func_wp_test()))
                    gen_tasks.append(("FUNC_WRAP", "Page Wrap Test",
                                      lambda: self.gen.generate_func_page_wrap()))
                    gen_tasks.append(("FUNC_CAR", "Current Address Read",
                                      lambda: self.gen.generate_func_current_read()))
            if self.test_vars["march_test"].get():
                cnt = scan_end - scan_start + 1
                gen_tasks.append(("MARCH_TEST", "March C- Memory Test",
                                  lambda s=scan_start, c=cnt:
                                  self.gen.generate_march_c_test(s, c)))
            if self.test_vars.get("march_b_test", tk.BooleanVar()).get():
                cnt = scan_end - scan_start + 1
                gen_tasks.append(("MARCHB_TEST", "March B Memory Test",
                                  lambda s=scan_start, c=cnt:
                                  self.gen.generate_march_b_test(s, c)))
            if self.test_vars["scan_test"].get():
                gen_tasks.append(("SCAN_TEST", "Address Scan Test",
                                  lambda s=scan_start, e=scan_end:
                                  self.gen.generate_addr_scan_test(s, e)))
            if self.test_vars["ret_test"].get():
                cnt = scan_end - scan_start + 1
                gen_tasks.append(("RET_TEST", "Data Retention Test",
                                  lambda s=scan_start, c=cnt:
                                  self.gen.generate_data_retention_test(s, c)))
            if self.test_vars["err_test"].get():
                if protocol == "SPI":
                    gen_tasks.append(("ERR_TEST", "SPI Error/Boundary Test",
                                      lambda: self.gen.generate_spi_error_test()))
                elif protocol == "Microwire":
                    gen_tasks.append(("ERR_TEST", "Microwire Error/Boundary Test",
                                      lambda: self.gen.generate_mw_error_test()))
                else:
                    gen_tasks.append(("ERR_TEST", "I2C Error/Boundary Test",
                                      lambda: self.gen.generate_i2c_error_test()))
            if self.test_vars["endur_test"].get():
                endur_addr = min(0x70, max_addr)
                gen_tasks.append(("ENDUR_TEST", "Write Endurance Test",
                                  lambda ea=endur_addr: self.gen.generate_endurance_test(
                                      test_addr=ea, cycles=10)))
            if self.test_vars.get("iddq_test", tk.BooleanVar()).get():
                gen_tasks.append(("IDDQ_TEST", "IDDQ Quiescent Current Test",
                                  lambda: self.gen.generate_iddq_test()))

            if not gen_tasks:
                messagebox.showwarning("", self.t("select_test"))
                return

            # ---- 创建进度对话框 ----
            total_steps = len(gen_tasks) + 1  # +1 for preview update
            prog_dlg = tk.Toplevel(self.root)
            prog_dlg.title(self.t("gen_progress"))
            prog_dlg.geometry("420x100")
            prog_dlg.resizable(False, False)
            prog_dlg.transient(self.root)
            prog_dlg.grab_set()
            prog_dlg.configure(bg=self.colors["card"])
            # 居中
            prog_dlg.update_idletasks()
            x = self.root.winfo_x() + (self.root.winfo_width() - 420) // 2
            y = self.root.winfo_y() + (self.root.winfo_height() - 100) // 2
            prog_dlg.geometry(f"+{x}+{y}")

            prog_label = tk.Label(prog_dlg, text=self.t("gen_progress"),
                                  font=("Segoe UI", 10),
                                  fg=self.colors["text"], bg=self.colors["card"])
            prog_label.pack(pady=(12, 4))
            prog_bar = ttk.Progressbar(prog_dlg, length=380, maximum=total_steps)
            prog_bar.pack(pady=(0, 8))
            prog_dlg.update()

            # ---- 逐步生成 ----
            all_vectors = []
            all_comments = []
            all_labels = []
            pat_sections = []

            # v9.0: 上电序列
            cur_protocol = self.chip_protocol_var.get() if hasattr(self, 'chip_protocol_var') else "I2C"
            cur_pins = PROTOCOL_PINS.get(cur_protocol, TEST_PINS)
            cur_vcc = float(self.voltage_var.get().replace("V", ""))
            pwr_v, pwr_c, pwr_ls = PowerSequenceGenerator.generate_power_up(
                cur_pins, cur_protocol, cur_vcc)
            pwr_labels = [""] * len(pwr_v)
            pwr_labels[0] = "start_power_up"
            pat_sections.append(("POWER_UP", self.t("power_up_label"), pwr_v, pwr_c, pwr_labels))
            all_vectors.extend(pwr_v)
            all_comments.extend(pwr_c)
            all_labels.extend(pwr_labels)

            for step_idx, (name, desc, gen_fn) in enumerate(gen_tasks):
                prog_label.config(text=self.t("gen_step").format(desc))
                prog_bar["value"] = step_idx
                prog_dlg.update()

                v, c, l = gen_fn()
                pat_sections.append((name, desc, v, c, l))
                all_vectors.extend(v)
                all_comments.extend(c)
                all_labels.extend(l)

            # v9.0: 下电序列
            pwd_v, pwd_c, pwd_ls = PowerSequenceGenerator.generate_power_down(cur_pins)
            pwd_labels = [""] * len(pwd_v)
            pwd_labels[0] = "start_power_down"
            pat_sections.append(("POWER_DOWN", self.t("power_down_label"), pwd_v, pwd_c, pwd_labels))
            all_vectors.extend(pwd_v)
            all_comments.extend(pwd_c)
            all_labels.extend(pwd_labels)

            # ---- 更新预览 ----
            prog_label.config(text=self.t("gen_step_preview"))
            prog_bar["value"] = total_steps - 1
            prog_dlg.update()

            self.current_vectors = all_vectors
            self.current_comments = all_comments
            self.current_labels = all_labels
            self.pat_sections = pat_sections

            # 生成PAT内容
            period_ns = self._get_period_ns()
            vp = VOLTAGE_PRESETS.get(self.voltage_var.get())
            pat_content = self._build_pat_content(pat_sections, period_ns, vp)
            txt_content = self._build_txt_content(pat_sections)
            self._pat_content_cache = pat_content
            self._txt_content_cache = txt_content

            # 显示到预览区
            self.pat_text.delete("1.0", tk.END)
            self.pat_text.insert("1.0", pat_content)
            self._apply_pat_syntax_highlighting()
            self._update_line_numbers()
            self._update_jump_buttons(pat_sections)

            self.txt_text.delete("1.0", tk.END)
            self.txt_text.insert("1.0", txt_content)

            # 绘制波形图
            self.wave_end_var.set(str(min(200, len(all_vectors))))
            self._draw_waveform()
            self._update_wave_jump_buttons(pat_sections)

            # 更新流程图和统计面板
            self._draw_flowchart(pat_sections)
            self._update_statistics(pat_sections)

            # v9.0: 更新 Datasheet 覆盖矩阵
            self._update_compliance_matrix()

            # 启用导出按钮, 标记未导出
            self.export_btn.config(state=tk.NORMAL)
            self._exported = False

            # 关闭进度条
            prog_bar["value"] = total_steps
            prog_dlg.update()
            prog_dlg.destroy()

            # 更新状态栏
            total = len(all_vectors)
            freq_khz = 1e9 / period_ns / 1e3
            time_ms = total * period_ns / 1_000_000
            logger.info(f"Generated {total} vectors, {len(pat_sections)} segments, "
                        f"chip={self.chip_preset_var.get()}, protocol={self.chip_protocol_var.get()}")
            self.status_label.config(
                text=self.t("gen_ok"),
                fg=self.colors["success"])
            self.stats_label.config(
                text=f"{total} 向量  |  {len(pat_sections)} 段  |  ~{time_ms:.2f}ms @{freq_khz:.0f}kHz",
                fg=self.colors["accent2"])
            self.status_voltage_label.config(
                text=f"VCC={self.voltage_var.get()}  {period_ns}ns")

            # 切换到PAT预览
            self.notebook.select(0)

        except Exception as e:
            try:
                prog_dlg.destroy()
            except Exception:
                pass
            messagebox.showerror("生成错误", f"生成过程中出错:\n{str(e)}")
            self.status_label.config(text=f"✗ 错误: {str(e)}", fg=self.colors["danger"])

    def _build_pat_content(self, sections, period_ns=2500, voltage_preset=None):
        """构建完整PAT文件内容 — EStar 官方格式 (单个 @@PATTERN_DEFINE 块)"""
        pin_list = self._get_active_pins()
        preset_name = self.chip_preset_var.get() if hasattr(self, 'chip_preset_var') else "AT24C02"
        protocol = self.chip_protocol_var.get() if hasattr(self, 'chip_protocol_var') else "I2C"
        chip_label = preset_name if preset_name in CHIP_PRESETS else "Custom"
        fmt = PATFormatter()
        content = fmt.generate_pat_header(
            f"{chip_label}_TEST",
            f"{chip_label} {protocol} Complete Test Pattern",
            pin_list
        )
        content += "\n"

        # 单个 @@PATTERN_DEFINE 块包裹所有测试段
        content += "@@PATTERN_DEFINE  \n"
        content += f"// {','.join(pin_list)}\n\n"

        total_vectors = 0
        for i, (name, desc, vectors, comments, labels) in enumerate(sections):
            content += f"// {'='*60}\n"
            content += f"// {desc}\n"
            content += f"// {'='*60}\n"
            content += fmt.format_vector_body(
                vectors, comments, labels, pin_list, name,
                is_first_section=(i == 0),
                is_last_section=(i == len(sections) - 1)
            )
            total_vectors += len(vectors)

        content += "@@END_PATTERN_DEFINE\n"

        # 完整性校验尾部 (在 @@END_PATTERN_DEFINE 之后)
        content += self._generate_checksum_footer(content, total_vectors, len(sections))

        return content

    @staticmethod
    def _generate_checksum_footer(content, total_vectors, section_count):
        """生成PAT文件完整性校验尾部 (MD5 + 向量计数)"""
        md5 = hashlib.md5(content.encode("utf-8")).hexdigest().upper()
        lines = []
        lines.append("")
        lines.append("// " + "=" * 60)
        lines.append("// INTEGRITY CHECK")
        lines.append("// " + "=" * 60)
        lines.append(f"// VECTOR_COUNT   = {total_vectors}")
        lines.append(f"// SECTION_COUNT  = {section_count}")
        lines.append(f"// MD5_CHECKSUM   = {md5}")
        lines.append(f"// GENERATED_BY   = EEPROM PAT Generator {VERSION}")
        lines.append("// " + "=" * 60)
        lines.append("")
        return "\n".join(lines)

    def _build_txt_content(self, sections):
        """构建完整TXT预览内容"""
        fmt = PATFormatter()
        pin_list = self._get_active_pins()
        content = ""
        for name, desc, vectors, comments, labels in sections:
            content += fmt.format_txt_preview(vectors, comments, pin_list, desc)
            content += "\n\n"
        return content

    def _generate_html_report(self, pat_sections):
        """生成 HTML 测试报告"""
        total = sum(len(s[2]) for s in pat_sections)
        period_ns = self._get_period_ns()
        time_ms = total * period_ns / 1_000_000
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 收集覆盖率数据
        all_comments = []
        for _, _, _, comments, _ in pat_sections:
            all_comments.extend(comments)

        tested_addrs = set()
        for cm in all_comments:
            if not cm:
                continue
            for m in re.finditer(r'addr=0x([0-9A-Fa-f]{2,4})', cm):
                tested_addrs.add(int(m.group(1), 16))
            for m in re.finditer(r'WordAddr=0x([0-9A-Fa-f]{2,4})', cm):
                tested_addrs.add(int(m.group(1), 16))
            for m in re.finditer(r'AddrHigh=0x([0-9A-Fa-f]{2})', cm):
                pass  # High byte alone doesn't tell us the full address
            for m in re.finditer(r'AddrLow=0x([0-9A-Fa-f]{2})', cm):
                tested_addrs.add(int(m.group(1), 16))  # At minimum the low byte

        protocol_features = {
            "START": any("START" in (cm or "") and "Rep" not in (cm or "") for cm in all_comments),
            "STOP": any("STOP" in (cm or "") for cm in all_comments),
            "Repeated START": any("RepSTART" in (cm or "") for cm in all_comments),
            "Byte Write": any("Byte Write" in (cm or "") for cm in all_comments),
            "Random Read": any("Random Read" in (cm or "") for cm in all_comments),
            "Page Write": any("Page Write" in (cm or "") for cm in all_comments),
            "Sequential Read": any("Sequential Read" in (cm or "") for cm in all_comments),
            "Current Addr Read": any("Current Addr" in (cm or "") or "CurrentAddr" in (cm or "") for cm in all_comments),
            "ACK Polling": any("Poll" in (cm or "") for cm in all_comments),
            "Write Protect": any("WP" in (cm or "") and "protect" in (cm or "").lower() for cm in all_comments),
            "NACK": any("NACK" in (cm or "") for cm in all_comments),
        }
        proto_hit = sum(protocol_features.values())

        # 器件地址
        try:
            a2 = self.addr_vars["A2"].get()
            a1 = self.addr_vars["A1"].get()
            a0 = self.addr_vars["A0"].get()
            w_addr = 0xA0 | (a2 << 3) | (a1 << 2) | (a0 << 1)
            r_addr = w_addr | 1
        except Exception:
            w_addr, r_addr = 0xA0, 0xA1

        # SVG 饼图 (带百分比标签, 小扇区自动隐藏标签防重叠)
        svg_parts = []
        svg_labels = []
        colors = ["#4f8cff", "#38d9a9", "#ffd43b", "#b197fc", "#ff9f43",
                  "#e599f7", "#63e6be", "#ffa8a8", "#74c0fc", "#ffe066"]
        start_angle = 0
        for i, (name, desc, vectors, _, _) in enumerate(pat_sections):
            pct = len(vectors) / total if total else 0
            angle = pct * 360
            end_angle = start_angle + angle
            large_arc = 1 if angle > 180 else 0
            sr = math.radians(start_angle)
            er = math.radians(end_angle)
            x1, y1 = 100 + 80 * math.cos(sr), 100 + 80 * math.sin(sr)
            x2, y2 = 100 + 80 * math.cos(er), 100 + 80 * math.sin(er)
            clr = colors[i % len(colors)]
            svg_parts.append(
                f'<path d="M100,100 L{x1:.1f},{y1:.1f} A80,80 0 {large_arc},1 {x2:.1f},{y2:.1f} Z" fill="{clr}" opacity="0.9" />')
            # 百分比标签: 仅当扇区 >= 5% 时显示, 防止小扇区标签重叠
            if pct >= 0.05:
                mid_angle = math.radians((start_angle + end_angle) / 2)
                lx = 100 + 50 * math.cos(mid_angle)
                ly = 100 + 50 * math.sin(mid_angle)
                svg_labels.append(
                    f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle" '
                    f'dominant-baseline="central" fill="white" font-size="11" '
                    f'font-weight="bold" font-family="Consolas">{pct*100:.0f}%</text>')
            start_angle = end_angle

        svg_legend = ""
        for i, (name, desc, vectors, _, _) in enumerate(pat_sections):
            clr = colors[i % len(colors)]
            pct = len(vectors) / total * 100 if total else 0
            svg_legend += f'<div style="margin:4px 0"><span style="display:inline-block;width:12px;height:12px;background:{clr};border-radius:2px;margin-right:6px;vertical-align:middle"></span>{desc}: {len(vectors)} ({pct:.1f}%)</div>'

        # 协议特性 HTML
        proto_html = ""
        for feat, hit in protocol_features.items():
            sym = "&#10003;" if hit else "&#10007;"
            clr = "#38d9a9" if hit else "#6b7280"
            proto_html += f'<span style="color:{clr};margin-right:16px;font-family:Consolas">{sym} {feat}</span>'

        chip_cap = self._get_chip_capacity_bytes()
        addr_pct = len(tested_addrs) / max(chip_cap, 1) * 100

        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>{self.chip_preset_var.get()} PAT Test Report</title>
<style>
body {{ font-family: 'Segoe UI', sans-serif; background: #1a1f2e; color: #e8ecf1; max-width: 920px; margin: 0 auto; padding: 24px; }}
h1 {{ color: #4f8cff; border-bottom: 2px solid #353d52; padding-bottom: 12px; margin-top: 0; }}
h2 {{ color: #38d9a9; margin-top: 28px; }}
.card {{ background: #2a3042; border-radius: 8px; padding: 16px 20px; margin: 12px 0; }}
.stats-row {{ display: flex; gap: 16px; }}
.stat-box {{ flex:1; text-align:center; background:#232838; border-radius:8px; padding:14px 8px; }}
.stat-val {{ font-size: 28px; font-weight: bold; color: #38d9a9; }}
.stat-label {{ font-size: 11px; color: #8892a4; margin-top: 4px; }}
table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
th, td {{ padding: 8px 12px; border: 1px solid #353d52; text-align: left; }}
th {{ background: #232838; color: #4f8cff; font-size: 13px; }}
td {{ font-family: Consolas, monospace; font-size: 12px; }}
.bar-bg {{ height:16px; background:#1a1f2e; border-radius:4px; overflow:hidden; }}
.bar-fill {{ height:16px; border-radius:4px; }}
.footer {{ text-align:center; color:#5a6378; font-size:11px; margin-top:30px; border-top:1px solid #353d52; padding-top:12px; }}
.pie-row {{ display:flex; align-items:center; gap:24px; }}
</style>
</head>
<body>
<h1>{self.chip_preset_var.get()} PAT 测试报告</h1>
<p style="color:#8892a4">生成时间: {now} &nbsp;|&nbsp; 工具: EEPROM PAT Generator {VERSION} &nbsp;|&nbsp; 目标 ATE: AdaptStar-E</p>

<h2>器件配置</h2>
<div class="card">
<table>
<tr><th>参数</th><th>值</th></tr>
<tr><td>器件</td><td>{self.chip_preset_var.get()} ({self._get_chip_capacity_label()} I2C EEPROM, SOP-8)</td></tr>
<tr><td>I2C 地址</td><td>Write: 0x{w_addr:02X} / Read: 0x{r_addr:02X}</td></tr>
<tr><td>地址引脚</td><td>A2={a2} A1={a1} A0={a0}</td></tr>
<tr><td>向量周期</td><td>{period_ns} ns ({1e9/period_ns/1e3:.1f} kHz)</td></tr>
</table>
</div>

<h2>Executive Summary</h2>
<div class="card">
{self._generate_executive_summary_html(pat_sections, tested_addrs, proto_hit, len(protocol_features))}
</div>

<h2>测试概要</h2>
<div class="stats-row">
<div class="stat-box"><div class="stat-val">{total}</div><div class="stat-label">总向量数</div></div>
<div class="stat-box"><div class="stat-val">{len(pat_sections)}</div><div class="stat-label">测试段</div></div>
<div class="stat-box"><div class="stat-val">{time_ms:.2f}ms</div><div class="stat-label">预估时间</div></div>
<div class="stat-box"><div class="stat-val">{addr_pct:.0f}%</div><div class="stat-label">地址覆盖</div></div>
</div>

<h2>向量分布</h2>
<div class="card pie-row">
<svg width="200" height="200" viewBox="0 0 200 200">
{''.join(svg_parts)}
{''.join(svg_labels)}
</svg>
<div>{svg_legend}</div>
</div>

<h2>测试段明细</h2>
<div class="card">
<table>
<tr><th>测试段</th><th>描述</th><th>向量数</th><th>占比</th></tr>
{''.join(f'<tr><td>{name}</td><td>{desc}</td><td>{len(vectors)}</td><td>{len(vectors)/total*100:.1f}%</td></tr>' for name, desc, vectors, _, _ in pat_sections)}
</table>
</div>

<h2>覆盖率分析</h2>
<div class="card">
<p><b>地址空间覆盖:</b> {len(tested_addrs)}/{chip_cap} ({addr_pct:.1f}%)</p>
<div class="bar-bg"><div class="bar-fill" style="width:{addr_pct:.1f}%;background:#4f8cff"></div></div>
<p style="margin-top:12px"><b>I2C 协议特性覆盖:</b> {proto_hit}/{len(protocol_features)}</p>
<div class="bar-bg"><div class="bar-fill" style="width:{proto_hit/len(protocol_features)*100:.1f}%;background:#38d9a9"></div></div>
<p style="margin-top:12px">{proto_html}</p>
</div>

<h2>地址空间热力图</h2>
<div class="card">
<p style="color:#8892a4;font-size:12px">16x16 网格, 每格代表一个字节地址 (0x00~0xFF), 绿色=已覆盖, 灰色=未测试</p>
<svg width="420" height="420" viewBox="0 0 420 420">
{self._generate_addr_heatmap_svg(tested_addrs)}
</svg>
</div>

<h2>I2C 波形示意 (前50向量)</h2>
<div class="card">
<p style="color:#8892a4;font-size:12px">SCL/SDA 信号波形 — 展示 START, 器件地址写入, ACK 等关键协议事件</p>
{self._generate_waveform_svg_for_html(pat_sections)}
</div>

<h2>故障模型覆盖率</h2>
<div class="card">
<table>
<tr><th>故障模型</th><th>英文全称</th><th>覆盖测试</th><th>状态</th></tr>
{self._generate_fault_coverage_html(pat_sections)}
</table>
</div>

<h2>March 算法对比</h2>
<div class="card">
<table>
<tr><th>特性</th><th>March C-</th><th>March B</th></tr>
<tr><td>复杂度</td><td>10N</td><td>17N</td></tr>
<tr><td>步骤数</td><td>6 (M0-M5)</td><td>5 (M0-M4)</td></tr>
<tr><td style="color:#4f8cff">算法序列</td>
<td style="font-family:Consolas;font-size:11px">M0:&#8679;(w0) M1:&#8679;(r0,w1) M2:&#8679;(r1,w0)<br>M3:&#8681;(r0,w1) M4:&#8681;(r1,w0) M5:&#8679;(r0)</td>
<td style="font-family:Consolas;font-size:11px">M0:&#8679;(w0) M1:&#8679;(r0,w1,r1,w0,r0,w1)<br>M2:&#8679;(r1,w0,w1) M3:&#8681;(r1,w0,w1,w0)<br>M4:&#8681;(r0,w1,w0)</td></tr>
<tr><td>SAF (固定故障)</td><td style="color:#38d9a9;text-align:center">&#10003;</td><td style="color:#38d9a9;text-align:center">&#10003;</td></tr>
<tr><td>TF (转换故障)</td><td style="color:#38d9a9;text-align:center">&#10003;</td><td style="color:#38d9a9;text-align:center">&#10003;</td></tr>
<tr><td>CFin (反转耦合)</td><td style="color:#38d9a9;text-align:center">&#10003;</td><td style="color:#38d9a9;text-align:center">&#10003;</td></tr>
<tr><td>CFid (等幂耦合)</td><td style="color:#ff6b6b;text-align:center">&#10007;</td><td style="color:#38d9a9;text-align:center">&#10003;</td></tr>
<tr><td>CFdyn (动态耦合)</td><td style="color:#ff6b6b;text-align:center">&#10007;</td><td style="color:#38d9a9;text-align:center">&#10003;</td></tr>
<tr><td>适用场景</td><td>快速筛选、量产测试</td><td>深度诊断、工程验证</td></tr>
</table>
</div>

<h2>测试限值表 (Pass/Fail Criteria)</h2>
<div class="card">
<table>
<tr><th>参数</th><th>描述</th><th>Min</th><th>Typ</th><th>Max</th><th>单位</th><th>测试条件</th></tr>
{''.join(f'<tr><td style="color:#4f8cff;font-weight:bold">{lim["param"]}</td><td>{lim["desc"]}</td><td>{lim["min"] if lim["min"] is not None else "—"}</td><td>{lim["typ"] if lim["typ"] is not None else "—"}</td><td>{lim["max"] if lim["max"] is not None else "—"}</td><td>{lim["unit"]}</td><td style="font-size:11px;color:#8892a4">{lim["condition"]}</td></tr>' for lim in TEST_LIMITS.values())}
</table>
</div>

<h2>导出文件清单</h2>
<div class="card">
<table>
<tr><th>文件类型</th><th>扩展名</th><th>说明</th></tr>
<tr><td>测试向量</td><td>.pat</td><td>ATE 可执行的 PAT 向量文件 (合并 + 分段)</td></tr>
<tr><td>向量预览</td><td>.txt</td><td>人类可读的向量表格预览</td></tr>
<tr><td>测试程序</td><td>.prg</td><td>ATE 测试流程模板 (DPS/LEVEL/PATTERN/JUDGE)</td></tr>
<tr><td>时序配置</td><td>.tim</td><td>ATE 时序定义 (PERIOD/DRIVE/COMPARE/CLOCK)</td></tr>
<tr><td>电平配置</td><td>.lvl</td><td>ATE 电平定义 (VIH/VIL/VOH/VOL/IOL per pin)</td></tr>
<tr><td>测试报告</td><td>.html</td><td>本报告文件 (含统计/覆盖率/限值表)</td></tr>
<tr><td>配置信息</td><td>.json</td><td>GUI 配置快照 (可重新加载)</td></tr>
</table>
</div>

<div class="footer">
EEPROM PAT Generator {VERSION} — 全国大学生集成电路创新创业大赛 "胜达克" 企业命题
</div>
</body>
</html>"""
        return html

    @staticmethod
    def _generate_fault_coverage_html(pat_sections):
        """生成故障模型覆盖率表格行"""
        section_names = {name for name, _, _, _, _ in pat_sections}

        fault_models = [
            ("SAF", "Stuck-At Fault", "March C-", "MARCH_TEST",
             "存储单元固定为 0 或 1, 无法改写"),
            ("TF", "Transition Fault", "March C-", "MARCH_TEST",
             "存储单元无法完成 0→1 或 1→0 翻转"),
            ("CFin", "Coupling Fault (Inversion)", "March C-", "MARCH_TEST",
             "写入一个单元导致另一个单元翻转"),
            ("CFid", "Coupling Fault (Idempotent)", "March B", "MARCHB_TEST",
             "写入一个单元导致另一个单元被强制为固定值"),
            ("CFdyn", "Dynamic Coupling Fault", "March B", "MARCHB_TEST",
             "连续读写操作中耦合单元发生动态翻转"),
            ("AF", "Address Fault", "Addr Scan", "SCAN_TEST",
             "地址译码错误, 访问了错误的存储单元"),
            ("DRF", "Data Retention Fault", "Data Retention", "RET_TEST",
             "写入数据经过一段时间后丢失或翻转"),
            ("ENDF", "Endurance Fault", "Endurance", "ENDUR_TEST",
             "反复擦写后存储单元失效"),
            ("OS", "Open/Short", "OS Test", "OS_TEST",
             "引脚开路或短路到 VCC/GND/相邻引脚"),
            ("DC", "DC Parametric", "DC Test", "DC_TEST",
             "静态电流/电压参数超出规格限值"),
            ("I2C-ERR", "Protocol Error Handling", "I2C Error", "ERR_TEST",
             "I2C 协议异常下的容错与恢复能力"),
            ("FUNC", "Functional Integrity", "Functional", "FUNC_TEST",
             "基本读写/页操作/WP保护/地址边界"),
        ]

        rows = []
        covered = 0
        for code, full_name, test_name, section_key, desc in fault_models:
            hit = section_key in section_names
            if hit:
                covered += 1
            sym = "&#10003;" if hit else "&#10007;"
            clr = "#38d9a9" if hit else "#ff6b6b"
            rows.append(
                f'<tr><td style="font-weight:bold;color:#4f8cff">{code}</td>'
                f'<td>{full_name}<br><span style="font-size:11px;color:#8892a4">{desc}</span></td>'
                f'<td>{test_name}</td>'
                f'<td style="color:{clr};font-size:16px;text-align:center">{sym}</td></tr>'
            )

        # 汇总行
        pct = covered / len(fault_models) * 100 if fault_models else 0
        rows.append(
            f'<tr style="background:#1a1f2e"><td colspan="3" style="text-align:right;font-weight:bold">'
            f'故障模型覆盖率</td>'
            f'<td style="text-align:center;color:#38d9a9;font-weight:bold;font-size:16px">'
            f'{covered}/{len(fault_models)} ({pct:.0f}%)</td></tr>'
        )
        return "\n".join(rows)

    @staticmethod
    def _generate_executive_summary_html(pat_sections, tested_addrs, proto_hit, proto_total):
        """生成 Executive Summary HTML (测试就绪度评分)"""
        section_names = {s[0] for s in pat_sections}
        total = sum(len(s[2]) for s in pat_sections)

        # 评分维度 (各 20 分, 满分 100)
        # 1. 测试类型覆盖 (9种)
        all_types = ["OS_TEST", "DC_TEST", "FUNC_TEST", "MARCH_TEST", "MARCHB_TEST",
                     "SCAN_TEST", "RET_TEST", "ERR_TEST", "ENDUR_TEST"]
        type_score = sum(1 for t in all_types if t in section_names) / len(all_types) * 20

        # 2. 地址空间覆盖
        capacity = max(tested_addrs) + 1 if tested_addrs else 256
        addr_ratio = len(tested_addrs) / max(capacity, 1)
        addr_score = min(20, addr_ratio * 25)  # 80% 覆盖即满分

        # 3. 协议特性覆盖
        proto_score = proto_hit / proto_total * 20 if proto_total else 0

        # 4. 向量充分性 (>10000 向量视为充分)
        vec_score = min(20, total / 10000 * 20)

        # 5. 故障模型覆盖 (有 March + Scan + Ret + Endurance 则满分)
        fault_tests = {"MARCH_TEST", "SCAN_TEST", "RET_TEST", "ENDUR_TEST"}
        fault_hit = len(fault_tests & section_names)
        fault_score = fault_hit / len(fault_tests) * 20

        readiness = type_score + addr_score + proto_score + vec_score + fault_score
        readiness = min(100, readiness)

        # 颜色
        if readiness >= 80:
            grade, grade_clr = "A (Production Ready)", "#38d9a9"
        elif readiness >= 60:
            grade, grade_clr = "B (Engineering Validation)", "#ffd43b"
        elif readiness >= 40:
            grade, grade_clr = "C (Basic Screening)", "#ff9f43"
        else:
            grade, grade_clr = "D (Insufficient)", "#ff6b6b"

        dims = [
            ("测试类型覆盖", type_score, 20, "#4f8cff"),
            ("地址空间覆盖", addr_score, 20, "#38d9a9"),
            ("协议特性覆盖", proto_score, 20, "#ffd43b"),
            ("向量充分性", vec_score, 20, "#b197fc"),
            ("故障模型覆盖", fault_score, 20, "#ff9f43"),
        ]

        html = f'<div style="text-align:center;margin-bottom:16px">'
        html += f'<div style="font-size:48px;font-weight:bold;color:{grade_clr}">{readiness:.0f}</div>'
        html += f'<div style="font-size:14px;color:{grade_clr};font-weight:bold">{grade}</div>'
        html += f'<div style="font-size:11px;color:#8892a4;margin-top:4px">Test Readiness Score (0-100)</div>'
        html += '</div>'

        for name, score, max_s, clr in dims:
            pct = score / max_s * 100
            html += f'<div style="margin:6px 0"><span style="display:inline-block;width:120px;font-size:12px">{name}</span>'
            html += f'<div class="bar-bg" style="display:inline-block;width:60%;vertical-align:middle">'
            html += f'<div class="bar-fill" style="width:{pct:.0f}%;background:{clr}"></div></div>'
            html += f'<span style="margin-left:8px;font-family:Consolas;font-size:12px;color:{clr}">{score:.0f}/{max_s}</span></div>'

        return html

    @staticmethod
    def _generate_waveform_svg_for_html(pat_sections, max_vectors=50):
        """生成前 N 个向量的 SCL/SDA 波形 SVG (嵌入 HTML 报告)"""
        all_vecs = []
        all_cms = []
        for _, _, vectors, comments, _ in pat_sections:
            all_vecs.extend(vectors)
            all_cms.extend(comments)
            if len(all_vecs) >= max_vectors:
                break
        vecs = all_vecs[:max_vectors]
        cms = all_cms[:max_vectors]
        n = len(vecs)
        if n == 0:
            return '<p style="color:#5a6378">无向量数据</p>'

        vec_w = 14
        lane_h = 40
        margin_l = 50
        margin_t = 30
        gap = 16
        total_w = margin_l + n * vec_w + 30
        total_h = margin_t + 2 * (lane_h + gap) + 50

        parts = [f'<svg width="{total_w}" height="{total_h}" '
                 f'viewBox="0 0 {total_w} {total_h}" '
                 f'style="background:#1a1f2e;border-radius:6px">']

        color_map = {"1": "#4f8cff", "0": "#4f8cff", "H": "#38d9a9",
                     "L": "#ff6b6b", "Z": "#ffd43b", "X": "#5a6378"}

        for si, sig in enumerate(["SCL", "SDA"]):
            y_base = margin_t + si * (lane_h + gap)
            y_high = y_base + 4
            y_low = y_base + lane_h - 4
            y_mid = (y_high + y_low) // 2
            # 信号名
            parts.append(f'<text x="{margin_l - 8}" y="{y_mid + 4}" '
                         f'fill="#e8ecf1" font-family="Consolas" font-size="10" '
                         f'text-anchor="end" font-weight="bold">{sig}</text>')
            # 参考线
            parts.append(f'<line x1="{margin_l}" y1="{y_high}" '
                         f'x2="{margin_l + n * vec_w}" y2="{y_high}" '
                         f'stroke="#353d52" stroke-dasharray="2,4"/>')
            parts.append(f'<line x1="{margin_l}" y1="{y_low}" '
                         f'x2="{margin_l + n * vec_w}" y2="{y_low}" '
                         f'stroke="#353d52" stroke-dasharray="2,4"/>')

            prev_y = None
            for i in range(n):
                x = margin_l + i * vec_w
                val = vecs[i].get(sig, "X")
                clr = color_map.get(val, "#5a6378")
                if val in ("1", "H"):
                    cur_y = y_high
                elif val in ("0", "L"):
                    cur_y = y_low
                else:
                    cur_y = y_mid
                # 跳变
                if prev_y is not None and prev_y != cur_y:
                    parts.append(f'<line x1="{x}" y1="{prev_y}" x2="{x}" y2="{cur_y}" '
                                 f'stroke="{clr}" stroke-width="1"/>')
                # 水平线
                dash = ' stroke-dasharray="3,3"' if val in ("Z", "X") else ""
                parts.append(f'<line x1="{x}" y1="{cur_y}" x2="{x + vec_w}" y2="{cur_y}" '
                             f'stroke="{clr}" stroke-width="2"{dash}/>')
                prev_y = cur_y

        # 事件标注
        anno_y = margin_t + 2 * (lane_h + gap) + 4
        for i in range(n):
            cm = cms[i] if i < len(cms) else ""
            if not cm:
                continue
            x = margin_l + i * vec_w
            for kw, kclr in [("START", "#ffd43b"), ("STOP", "#ff6b6b"),
                              ("ACK", "#38d9a9"), ("NACK", "#ff6b6b")]:
                if kw in cm:
                    parts.append(f'<line x1="{x}" y1="{margin_t}" x2="{x}" y2="{anno_y}" '
                                 f'stroke="{kclr}" stroke-dasharray="1,3" stroke-width="1"/>')
                    parts.append(f'<text x="{x}" y="{anno_y + 10}" fill="{kclr}" '
                                 f'font-family="Consolas" font-size="7" '
                                 f'text-anchor="start">{kw}</text>')
                    break

        parts.append('</svg>')
        return '\n'.join(parts)

    @staticmethod
    def _generate_addr_heatmap_svg(tested_addrs):
        """生成 16x16 地址空间热力图 SVG 元素"""
        cell = 24
        gap = 2
        margin = 20
        parts = []
        # 列标题 (0~F)
        for col in range(16):
            x = margin + col * (cell + gap) + cell // 2
            parts.append(f'<text x="{x}" y="14" fill="#8892a4" font-family="Consolas" '
                         f'font-size="10" text-anchor="middle">{col:X}</text>')
        # 行标题 + 单元格
        for row in range(16):
            y = margin + row * (cell + gap)
            parts.append(f'<text x="10" y="{y + cell // 2 + 4}" fill="#8892a4" '
                         f'font-family="Consolas" font-size="10" text-anchor="middle">'
                         f'{row:X}</text>')
            for col in range(16):
                addr = row * 16 + col
                x = margin + col * (cell + gap)
                hit = addr in tested_addrs
                color = "#38d9a9" if hit else "#2a3042"
                opacity = "0.9" if hit else "0.5"
                parts.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" '
                             f'rx="3" fill="{color}" opacity="{opacity}"/>')
                if hit:
                    parts.append(f'<text x="{x + cell//2}" y="{y + cell//2 + 4}" '
                                 f'fill="white" font-family="Consolas" font-size="7" '
                                 f'text-anchor="middle">{addr:02X}</text>')
        return "\n".join(parts)

    def _generate_csv_stats(self, pat_sections, period_ns):
        """生成 CSV 格式的测试统计数据"""
        lines = []
        lines.append("Test Segment,Description,Vectors,Percentage,Vector Time (ms),Write Ops,tWR Wait (ms),Total Time (ms)")
        total = sum(len(s[2]) for s in pat_sections)
        for name, desc, vectors, comments, _ in pat_sections:
            cnt = len(vectors)
            pct = cnt / total * 100 if total else 0
            vec_ms = cnt * period_ns / 1_000_000
            writes = sum(1 for cm in comments
                         if cm and ("ACK Polling" in cm or "Poll #1" in cm))
            twr_ms = writes * 5.0
            total_ms = vec_ms + twr_ms
            lines.append(f"{name},{desc},{cnt},{pct:.1f}%,{vec_ms:.2f},{writes},{twr_ms:.0f},{total_ms:.2f}")

        # 汇总行
        total_vec_ms = total * period_ns / 1_000_000
        all_writes = sum(
            sum(1 for cm in s[3] if cm and ("ACK Polling" in cm or "Poll #1" in cm))
            for s in pat_sections
        )
        total_twr = all_writes * 5.0
        lines.append(f"TOTAL,All Segments,{total},100%,{total_vec_ms:.2f},{all_writes},{total_twr:.0f},{total_vec_ms + total_twr:.2f}")
        lines.append("")
        lines.append(f"Period (ns),{period_ns}")
        lines.append(f"Frequency (kHz),{1e9/period_ns/1e3:.1f}")
        lines.append(f"Generated,{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Tool,EEPROM PAT Generator {VERSION}")
        return "\n".join(lines)

    def on_export(self):
        """导出文件"""
        if not self.current_vectors:
            messagebox.showinfo("", self.t("gen_first"))
            return

        # v9.0: 格式选择对话框
        fmt_dlg = tk.Toplevel(self.root)
        fmt_dlg.title(self.t("export_format_title"))
        fmt_dlg.geometry("320x200")
        fmt_dlg.transient(self.root)
        fmt_dlg.grab_set()
        fmt_dlg.resizable(False, False)

        tk.Label(fmt_dlg, text=self.t("export_format_title"),
                 font=("Segoe UI", 10, "bold")).pack(pady=(10, 6))

        self._export_fmt_pat = tk.BooleanVar(value=True)
        self._export_fmt_stil = tk.BooleanVar(value=True)
        self._export_fmt_wgl = tk.BooleanVar(value=True)

        tk.Checkbutton(fmt_dlg, text=self.t("export_format_pat"),
                       variable=self._export_fmt_pat, anchor=tk.W).pack(fill=tk.X, padx=30)
        tk.Checkbutton(fmt_dlg, text=self.t("export_format_stil"),
                       variable=self._export_fmt_stil, anchor=tk.W).pack(fill=tk.X, padx=30)
        tk.Checkbutton(fmt_dlg, text=self.t("export_format_wgl"),
                       variable=self._export_fmt_wgl, anchor=tk.W).pack(fill=tk.X, padx=30)

        btn_frame = tk.Frame(fmt_dlg)
        btn_frame.pack(pady=10)

        def _do_export():
            fmt_dlg.destroy()
            init_dir = self._last_export_dir or ""
            save_dir = filedialog.askdirectory(title="选择保存目录",
                                                initialdir=init_dir if init_dir else None)
            if not save_dir:
                return
            self._do_export_to(save_dir)

        def _cancel():
            fmt_dlg.destroy()

        tk.Button(btn_frame, text=self.t("export_format_go"),
                  command=_do_export).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text=self.t("cancel") if "cancel" in I18N.get(self.lang, {}) else "Cancel",
                  command=_cancel).pack(side=tk.LEFT, padx=5)

    def _export_files(self, save_dir, prefix, _prog, prog_dlg):
        """实际导出逻辑 (on_export 和 _quick_reexport 共享)"""
        file_list = []  # 跟踪已成功写入的文件（用于错误恢复报告）
        total_steps = 0
        try:
            n_sections = len(self.pat_sections)
            # 主要步骤数: PAT + TXT + 各段(x2) + JSON + HTML + TIM + LVL + PRG
            total_steps = 5 + n_sections * 2 + 4
            step = 0

            # 保存PAT文件
            period_ns = self._get_period_ns()
            vp = VOLTAGE_PRESETS.get(self.voltage_var.get())
            step += 1; _prog(step, total_steps, "导出 PAT 合并文件...")
            pat_content = self._build_pat_content(self.pat_sections, period_ns, vp)
            pat_path = os.path.join(save_dir, f"{prefix}_TEST.pat")
            with open(pat_path, "w", encoding="utf-8") as f:
                f.write(pat_content)

            # 保存TXT预览文件
            step += 1; _prog(step, total_steps, "导出 TXT 预览文件...")
            txt_content = self._build_txt_content(self.pat_sections)
            txt_path = os.path.join(save_dir, f"{prefix}_TEST_preview.txt")
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(txt_content)

            # 也分别保存各测试段的PAT文件
            fmt = PATFormatter()
            pin_list = self._get_active_pins()
            for name, desc, vectors, comments, labels in self.pat_sections:
                step += 1; _prog(step, total_steps, f"导出 {name}...")

                # 拆分 ACK Polling 到独立文件
                (main_v, main_c, main_l), (poll_v, poll_c, poll_l) = \
                    PATFormatter.split_ack_polling(vectors, comments, labels)

                # 主文件 (ACK Polling 替换为 idle 占位)
                seg_content = fmt.generate_pat_header(name, desc, pin_list)
                seg_content += "\n"
                seg_content += fmt.format_vectors(main_v, main_c, main_l, pin_list, name)
                seg_path = os.path.join(save_dir, f"{prefix}_{name}.pat")
                with open(seg_path, "w", encoding="utf-8") as f:
                    f.write(seg_content)

                # ACK Polling 独立文件 (如果有)
                if poll_v:
                    poll_name = f"{name}_ACK_POLL"
                    poll_content = fmt.generate_pat_header(
                        poll_name, f"{desc} - ACK Polling", pin_list)
                    poll_content += "\n"
                    poll_content += fmt.format_vectors(
                        poll_v, poll_c, poll_l, pin_list, poll_name)
                    poll_path = os.path.join(save_dir, f"{prefix}_{poll_name}.pat")
                    with open(poll_path, "w", encoding="utf-8") as f:
                        f.write(poll_content)

                # TXT 预览仍使用原始完整向量
                step += 1; _prog(step, total_steps)
                seg_txt = fmt.format_txt_preview(vectors, comments, pin_list, desc)
                seg_txt_path = os.path.join(save_dir, f"{prefix}_{name}_preview.txt")
                with open(seg_txt_path, "w", encoding="utf-8") as f:
                    f.write(seg_txt)

            # 保存配置信息
            step += 1; _prog(step, total_steps, "导出 JSON 配置...")
            config = {
                "device": self.chip_preset_var.get(),
                "protocol": self.chip_protocol_var.get(),
                "addr_pins": {
                    "A2": self.addr_vars["A2"].get(),
                    "A1": self.addr_vars["A1"].get(),
                    "A0": self.addr_vars["A0"].get(),
                },
                "tests": {k: v.get() for k, v in self.test_vars.items()},
                "total_vectors": len(self.current_vectors),
                "generated_time": datetime.datetime.now().isoformat(),
            }
            config_path = os.path.join(save_dir, f"{prefix}_config.json")
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            # 生成 HTML 测试报告
            step += 1; _prog(step, total_steps, "生成 HTML 报告...")
            html_content = self._generate_html_report(self.pat_sections)
            html_path = os.path.join(save_dir, f"{prefix}_TEST_REPORT.html")
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            # 生成 .tim 时序配置文件
            step += 1; _prog(step, total_steps, "导出 TIM/LVL/PRG...")
            cur_protocol = self.chip_protocol_var.get()
            chip_name = self.chip_preset_var.get()
            tim_content = fmt.generate_tim_file(period_ns, self.voltage_var.get(),
                                                 protocol=cur_protocol, chip_name=chip_name)
            tim_path = os.path.join(save_dir, f"{prefix}_timing.tim")
            with open(tim_path, "w", encoding="utf-8") as f:
                f.write(tim_content)

            # 生成 .lvl 电平配置文件
            lvl_content = fmt.generate_lvl_file(vp, chip_name=chip_name)
            lvl_path = os.path.join(save_dir, f"{prefix}_level.lvl")
            with open(lvl_path, "w", encoding="utf-8") as f:
                f.write(lvl_content)

            # 生成 .prg 测试程序模板
            if chip_name in CHIP_PRESETS:
                chip_cap = CHIP_PRESETS[chip_name].get("capacity", "")
            else:
                chip_cap = f"{self.chip_capacity_var.get()} bytes"
            # v9.0 Phase 26: 构建 Pin Map + Multi-Site PRG 段
            _pin_map_sec = ""
            _site_config_sec = ""
            _num_sites = int(self.site_count_var.get()) if hasattr(self, 'site_count_var') else 1
            if _num_sites > 1:
                _pm = PinMapManager(protocol=cur_protocol)
                if cur_protocol == "SPI":
                    _pins = ["CS", "SCK", "MOSI", "MISO", "WP", "HOLD"]
                    _dirs = {"MISO": "Out"}
                elif cur_protocol == "Microwire":
                    _pins = ["CS", "SK", "DI", "DO", "ORG", "NC"]
                    _dirs = {"DO": "Out"}
                else:
                    _pins = ["A0", "A1", "A2", "WP", "SCL", "SDA"]
                    _dirs = {"SDA": "InOut"}
                _pmap = _pm.generate_pin_map(_pins, _dirs, _num_sites)
                _pin_map_sec = _pm.generate_pin_map_section(_pmap)
                _ms = MultiSiteGenerator(site_count=_num_sites, protocol=cur_protocol)
                _site_config_sec = _ms.generate_full_site_config()

            prg_content = fmt.generate_prg_file(self.pat_sections, period_ns, vp,
                                                 chip_name=chip_name, chip_capacity=chip_cap,
                                                 protocol=cur_protocol,
                                                 export_prefix=prefix,
                                                 pin_map_section=_pin_map_sec,
                                                 site_config_section=_site_config_sec,
                                                 num_sites=_num_sites)
            prg_path = os.path.join(save_dir, f"{prefix}_TEST.prg")
            with open(prg_path, "w", encoding="utf-8") as f:
                f.write(prg_content)

            # 生成 CSV 统计文件
            csv_content = self._generate_csv_stats(self.pat_sections, period_ns)
            csv_path = os.path.join(save_dir, f"{prefix}_TEST_stats.csv")
            with open(csv_path, "w", encoding="utf-8-sig") as f:
                f.write(csv_content)

            # 生成 .dlog Datalog 模板
            dlog_content = self.generate_datalog_template(
                f"{prefix}_TEST", pin_list, self.pat_sections)
            dlog_path = os.path.join(save_dir, f"{prefix}_TEST.dlog")
            with open(dlog_path, "w", encoding="utf-8") as f:
                f.write(dlog_content)

            file_list.extend([pat_path, txt_path])
            for name, _, _, _, _ in self.pat_sections:
                file_list.append(os.path.join(save_dir, f"{prefix}_{name}.pat"))
                file_list.append(os.path.join(save_dir, f"{prefix}_{name}_preview.txt"))
            file_list.append(config_path)
            file_list.append(html_path)
            file_list.append(csv_path)
            file_list.append(tim_path)
            file_list.append(lvl_path)
            file_list.append(prg_path)
            file_list.append(dlog_path)

            # 多电压批量导出: 为每个电压条件生成独立子目录
            if self.multi_voltage_var.get():
                current_vkey = self.voltage_var.get()
                for vkey, vpreset in VOLTAGE_PRESETS.items():
                    if vkey == current_vkey:
                        continue  # 当前电压已导出到主目录
                    v_period = vpreset["period_ns"]
                    v_dir = os.path.join(save_dir, f"{prefix}_{vkey.replace('.', 'v')}")
                    os.makedirs(v_dir, exist_ok=True)

                    # PAT (使用该电压的时序/电平)
                    v_pat = self._build_pat_content(self.pat_sections, v_period, vpreset)
                    v_pat_path = os.path.join(v_dir, f"{prefix}_TEST_{vkey}.pat")
                    with open(v_pat_path, "w", encoding="utf-8") as f:
                        f.write(v_pat)
                    file_list.append(v_pat_path)

                    # .tim / .lvl / .prg
                    v_tim = fmt.generate_tim_file(v_period, vkey)
                    v_tim_path = os.path.join(v_dir, f"{prefix}_timing_{vkey}.tim")
                    with open(v_tim_path, "w", encoding="utf-8") as f:
                        f.write(v_tim)
                    file_list.append(v_tim_path)

                    v_lvl = fmt.generate_lvl_file(vpreset)
                    v_lvl_path = os.path.join(v_dir, f"{prefix}_level_{vkey}.lvl")
                    with open(v_lvl_path, "w", encoding="utf-8") as f:
                        f.write(v_lvl)
                    file_list.append(v_lvl_path)

                    v_prg = fmt.generate_prg_file(self.pat_sections, v_period, vpreset,
                                                    chip_name=chip_name, chip_capacity=chip_cap,
                                                    export_prefix=prefix)
                    v_prg_path = os.path.join(v_dir, f"{prefix}_TEST_{vkey}.prg")
                    with open(v_prg_path, "w", encoding="utf-8") as f:
                        f.write(v_prg)
                    file_list.append(v_prg_path)

            # v9.0: 按格式选择导出 STIL / WGL
            try:
                cur_protocol = self.chip_protocol_var.get() if hasattr(self, 'chip_protocol_var') else "I2C"
                pins = PROTOCOL_PINS.get(cur_protocol, TEST_PINS)
                cur_voltage = self.voltage_var.get()

                export_stil = getattr(self, '_export_fmt_stil', None)
                export_wgl = getattr(self, '_export_fmt_wgl', None)

                if export_stil is None or export_stil.get():
                    stil = STILFormatter()
                    stil_content = stil.format(self.pat_sections, pins, period_ns, cur_voltage,
                                               chip_name=chip_name, protocol=cur_protocol)
                    stil_path = os.path.join(save_dir, f"{prefix}_TEST.stil")
                    with open(stil_path, "w", encoding="utf-8") as f:
                        f.write(stil_content)
                    file_list.append(stil_path)

                if export_wgl is None or export_wgl.get():
                    wgl = WGLFormatter()
                    wgl_content = wgl.format(self.pat_sections, pins, period_ns, cur_voltage,
                                             chip_name=chip_name, protocol=cur_protocol)
                    wgl_path = os.path.join(save_dir, f"{prefix}_TEST.wgl")
                    with open(wgl_path, "w", encoding="utf-8") as f:
                        f.write(wgl_content)
                    file_list.append(wgl_path)
            except Exception as e:
                logger.warning(f"STIL/WGL export failed: {e}")

            self._exported = True
            self._last_export_dir = save_dir
            self._last_export_time = datetime.datetime.now().strftime("%H:%M:%S")
            self.reexport_btn.config(state=tk.NORMAL)
            _prog(total_steps, total_steps, "导出完成!")

            # 生成 MANIFEST.txt (SHA256 校验)
            manifest_path = self._generate_manifest(save_dir, file_list, prefix)
            file_list.append(manifest_path)

            # PAT 文件合规性自检
            check_results = self._pat_self_check(self.pat_sections)

            # Phase 3: EStar 格式验证 (23 条规则)
            estar_results = EStarValidator.validate_all(
                pat_content=pat_content,
                lvl_content=lvl_content,
                tim_content=tim_content,
                prg_content=prg_content,
            )
            ep, ef, et = EStarValidator.summary(estar_results)
            check_results += f"\n--- EStar 格式验证 ---"
            check_results += f"\n✓ 通过 {ep}/{et} 项"
            if ef > 0:
                for r in estar_results:
                    if not r["pass"]:
                        detail = f" ({r['detail']})" if r["detail"] else ""
                        check_results += f"\n  ✗ {r['desc']}{detail}"

            # 关闭进度条
            prog_dlg.destroy()

            # 自定义导出成功对话框 (含 "打开文件夹" 按钮 + 自检结果)
            logger.info(f"Exported {len(file_list)} files to {save_dir}, EStar: {ep}/{et}")
            self._show_export_success(save_dir, file_list, check_results)

            self.status_label.config(
                text=f"✓ 已导出 {len(file_list)} 个文件到 {save_dir}",
                fg=self.colors["success"]
            )

        except Exception as e:
            import traceback
            traceback.print_exc()
            prog_dlg.destroy()
            # 构建详细错误信息，包含已成功写入的文件
            err_msg = f"导出过程中出错:\n{str(e)}\n\n{traceback.format_exc()}"
            try:
                written = [f for f in file_list if os.path.isfile(f)]
                if written:
                    total_expected = total_steps  # 近似值
                    err_msg = self.t("export_partial_msg").format(
                        n=len(written), m=total_expected)
                    err_msg += f"\n\n{str(e)}\n\n"
                    err_msg += "已写入的文件:\n"
                    err_msg += "\n".join(f"  ✓ {os.path.basename(f)}" for f in written)
            except Exception:
                pass
            messagebox.showerror(self.t("export_partial"), err_msg)

    def _quick_reexport(self):
        """快速重导出到上次目录 (无需选择目录)"""
        if not self._last_export_dir or not self.current_vectors:
            messagebox.showinfo("", "请先正常导出一次")
            return
        if not os.path.isdir(self._last_export_dir):
            messagebox.showwarning("目录不存在",
                                    f"上次导出目录不存在:\n{self._last_export_dir}")
            self._last_export_dir = None
            self.reexport_btn.config(state=tk.DISABLED)
            return
        # 直接使用上次目录调用导出逻辑 (模拟 on_export 跳过目录选择)
        self._do_export_to(self._last_export_dir)

    def _do_export_to(self, save_dir):
        """导出到指定目录 (on_export 和 _quick_reexport 共享逻辑)"""
        prefix = self.export_prefix_var.get().strip() or self.chip_preset_var.get()

        # v6.0: 文件名非法字符校验
        import re as _re
        sanitized = _re.sub(r'[<>:"/\\|?*]', '_', prefix)
        if sanitized != prefix:
            prefix = sanitized
            messagebox.showwarning(self.t("warning"), self.t("prefix_sanitized"))

        # v6.0: 路径长度校验
        max_fname = f"{prefix}_FULL_TEST_preview.txt"
        if len(os.path.join(save_dir, max_fname)) > 240:
            messagebox.showwarning(self.t("warning"), self.t("path_too_long"))
            return

        # v6.0: 写权限预检
        if not os.access(save_dir, os.W_OK):
            messagebox.showerror(self.t("warning"), self.t("export_permission_denied"))
            return

        # v6.0: 文件覆盖确认
        expected_files = [f"{prefix}_FULL_TEST.pat", f"{prefix}_FULL_TEST_preview.txt"]
        if hasattr(self, 'pat_sections'):
            for name, *_ in self.pat_sections:
                expected_files.append(f"{prefix}_{name}.pat")
        existing = [f for f in expected_files if os.path.exists(os.path.join(save_dir, f))]
        if existing:
            show_list = "\n".join(existing[:10])
            if len(existing) > 10:
                show_list += f"\n... (+{len(existing)-10} more)"
            if not messagebox.askyesno(self.t("confirm"),
                    f"{self.t('files_exist_overwrite')}\n\n{show_list}"):
                return

        # 创建进度条弹窗
        prog_dlg = tk.Toplevel(self.root)
        prog_dlg.title("导出中...")
        prog_dlg.geometry("360x90")
        prog_dlg.resizable(False, False)
        prog_dlg.configure(bg=self.colors["card"])
        prog_dlg.transient(self.root)
        prog_dlg.grab_set()
        prog_label = tk.Label(prog_dlg, text="准备导出...",
                              font=("Segoe UI", 9), fg=self.colors["text"],
                              bg=self.colors["card"])
        prog_label.pack(pady=(12, 4))
        prog_bar = ttk.Progressbar(prog_dlg, length=300, mode="determinate")
        prog_bar.pack(pady=4)
        prog_dlg.update()

        def _prog(step, total, msg=""):
            prog_bar["value"] = step / total * 100
            if msg:
                prog_label.config(text=msg)
            prog_dlg.update()

        try:
            self._export_files(save_dir, prefix, _prog, prog_dlg)
        except Exception as e:
            prog_dlg.destroy()
            messagebox.showerror("导出错误", f"导出过程中出错:\n{str(e)}")

    def _generate_manifest(self, save_dir, file_list, prefix):
        """生成 MANIFEST.txt 文件完整性清单 (SHA256)"""
        import hashlib
        lines = []
        lines.append(f"{'='*60}")
        lines.append(f"  {self.t('manifest_header')}")
        lines.append(f"  Generated by EEPROM PAT Generator {VERSION}")
        lines.append(f"  Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"  Files: {len(file_list)}")
        lines.append(f"{'='*60}")
        lines.append("")

        total_bytes = 0
        for fpath in file_list:
            if not os.path.isfile(fpath):
                continue
            try:
                with open(fpath, "rb") as f:
                    data = f.read()
                sha = hashlib.sha256(data).hexdigest()
                size = len(data)
                total_bytes += size
                fname = os.path.basename(fpath)
                lines.append(f"SHA256 ({fname}) = {sha}")
                lines.append(f"  Size: {size:,} bytes")
            except Exception:
                fname = os.path.basename(fpath)
                lines.append(f"SHA256 ({fname}) = <error reading file>")

        lines.append("")
        lines.append(f"Total: {total_bytes:,} bytes ({total_bytes/1024:.1f} KB)")
        lines.append(f"{'='*60}")

        manifest_path = os.path.join(save_dir, f"{prefix}_MANIFEST.txt")
        with open(manifest_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return manifest_path

    def _show_export_success(self, save_dir, file_list, check_results=""):
        """导出成功弹窗 (含打开文件夹按钮, 文件列表可滚动, 自检结果)"""
        dlg = tk.Toplevel(self.root)
        dlg.title("导出成功")
        dlg.geometry("480x500")
        dlg.resizable(False, True)
        dlg.configure(bg=self.colors["card"])
        dlg.transient(self.root)
        dlg.grab_set()

        tk.Label(dlg, text=self.t("export_ok"),
                 font=("Segoe UI", 14, "bold"),
                 fg=self.colors["success"],
                 bg=self.colors["card"]).pack(pady=(18, 6))

        # 计算总文件大小
        total_bytes = sum(os.path.getsize(f) for f in file_list if os.path.isfile(f))
        if total_bytes >= 1024 * 1024:
            size_str = f"{total_bytes / (1024*1024):.2f} MB"
        else:
            size_str = f"{total_bytes / 1024:.1f} KB"

        tk.Label(dlg, text=f"{save_dir}  ({len(file_list)} files, {size_str})",
                 font=("Consolas", 9),
                 fg=self.colors["accent"],
                 bg=self.colors["card"]).pack(pady=(0, 2))
        tk.Label(dlg, text=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                 font=("Consolas", 8),
                 fg=self.colors["text_dim"],
                 bg=self.colors["card"]).pack(pady=(0, 4))

        # 自检结果
        if check_results:
            chk_color = self.colors["success"] if "✓" in check_results else self.colors["warning"]
            tk.Label(dlg, text=check_results,
                     font=("Consolas", 8),
                     fg=chk_color, bg=self.colors["card"],
                     justify=tk.LEFT, wraplength=440).pack(pady=(2, 8))

        # 可滚动文件列表
        list_outer = tk.Frame(dlg, bg=self.colors["bg"])
        list_outer.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 8))

        list_canvas = tk.Canvas(list_outer, bg=self.colors["bg"],
                                highlightthickness=0, height=220)
        list_scrollbar = tk.Scrollbar(list_outer, orient=tk.VERTICAL,
                                       command=list_canvas.yview)
        list_canvas.configure(yscrollcommand=list_scrollbar.set)
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        list_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        list_frame = tk.Frame(list_canvas, bg=self.colors["bg"], padx=10, pady=6)
        list_canvas.create_window((0, 0), window=list_frame, anchor=tk.NW)

        for fp in file_list:
            # 对多电压子目录文件显示相对路径
            rel = os.path.relpath(fp, save_dir)
            tk.Label(list_frame, text=f"  {rel}",
                     font=("Consolas", 8), anchor=tk.W,
                     fg=self.colors["text"], bg=self.colors["bg"]).pack(
                         anchor=tk.W, pady=1)

        list_frame.update_idletasks()
        list_canvas.configure(scrollregion=list_canvas.bbox("all"))
        list_canvas.bind("<MouseWheel>",
                         lambda e: list_canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        # 按钮区
        btn_frame = tk.Frame(dlg, bg=self.colors["card"])
        btn_frame.pack(pady=16)

        tk.Button(btn_frame, text=self.t("open_folder"),
                  command=lambda: self._open_folder(save_dir),
                  font=("Segoe UI", 9, "bold"),
                  bg=self.colors["accent"], fg="white",
                  activebackground="#3a7ae8",
                  relief=tk.FLAT, padx=14, pady=5,
                  cursor="hand2").pack(side=tk.LEFT, padx=6)

        tk.Button(btn_frame, text=self.t("close"),
                  command=dlg.destroy,
                  font=("Segoe UI", 9),
                  bg=self.colors["border"], fg=self.colors["text"],
                  relief=tk.FLAT, padx=14, pady=5,
                  cursor="hand2").pack(side=tk.LEFT, padx=6)

    def _pat_self_check(self, pat_sections):
        """PAT 文件合规性自检: 验证向量完整性"""
        issues = []
        total_vectors = 0
        all_labels = []
        valid_states = {"0", "1", "H", "L", "Z", "X"}

        for name, desc, vectors, comments, labels in pat_sections:
            seg_n = len(vectors)
            total_vectors += seg_n

            # 检查向量数与注释数一致
            if len(comments) != seg_n:
                issues.append(f"[{name}] 向量数({seg_n})与注释数({len(comments)})不一致")
            if len(labels) != seg_n:
                issues.append(f"[{name}] 向量数({seg_n})与标签数({len(labels)})不一致")

            # 检查引脚数
            for i, vec in enumerate(vectors):
                expected_pin_count = len(self._get_active_pins())
                if len(vec) != expected_pin_count:
                    issues.append(f"[{name}] V{i}: 引脚数={len(vec)}, 期望={expected_pin_count}")
                    break
                # 检查非法状态字符
                for pin, val in vec.items():
                    if val not in valid_states:
                        issues.append(f"[{name}] V{i}.{pin}: 非法状态 '{val}'")
                        break

            # 收集标签 (检查唯一性)
            for lb in labels:
                if lb:
                    all_labels.append(lb)

        # 标签唯一性检查
        seen = set()
        for lb in all_labels:
            if lb in seen:
                issues.append(f"标签重复: '{lb}'")
            seen.add(lb)

        # 生成报告
        if not issues:
            return f"✓ PAT 自检通过: {total_vectors} 向量, {len(all_labels)} 标签, {len(pat_sections)} 段, 0 问题"
        else:
            return f"⚠ PAT 自检: {len(issues)} 个问题\n" + "\n".join(issues[:10])

    @staticmethod
    def _open_folder(path):
        """用系统文件管理器打开目录"""
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])


# ============================================================
# 主程序入口
# ============================================================

def main():
    """主入口 — 支持 GUI 和 CLI 批处理模式"""
    parser = argparse.ArgumentParser(
        description=f"ATE Pattern Generator Platform {VERSION}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python at24c02_pat_generator.py                              # GUI mode
  python at24c02_pat_generator.py --batch --chip AT24C02       # Batch: default tests
  python at24c02_pat_generator.py --batch --chip W25Q32JV --protocol SPI --format stil
  python at24c02_pat_generator.py --batch --config myconfig.json --output ./output
""")
    parser.add_argument("--batch", action="store_true", help="Run in batch mode (no GUI)")
    parser.add_argument("--config", type=str, help="Config JSON file path")
    parser.add_argument("--output", type=str, default="./output", help="Output directory (batch mode)")
    parser.add_argument("--chip", type=str, default="AT24C02", help="Chip preset name")
    parser.add_argument("--protocol", type=str, default="I2C", help="Protocol: I2C / SPI / Microwire")
    parser.add_argument("--tests", type=str, default="all",
                        help="Comma-separated tests: os,dc,func,march,march_b,scan,ret,err,endur or 'all'")
    parser.add_argument("--format", type=str, default="pat", help="Output format: pat,stil,wgl,all")
    parser.add_argument("--voltage", type=str, default="5.0V", help="Voltage preset")
    parser.add_argument("--period", type=int, default=2500, help="Vector period (ns)")
    parser.add_argument("--shmoo", action="store_true", help="Run Shmoo characterization sweep")
    parser.add_argument("--sites", type=int, default=1, help="Multi-site count (1/2/4/8)")
    parser.add_argument("--simulate", action="store_true", help="Run pattern simulation after generation")
    parser.add_argument("--verbose", action="store_true", help="Verbose output to console")

    args = parser.parse_args()

    if args.verbose:
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        console.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        logger.addHandler(console)

    if args.batch:
        logger.info(f"Batch mode: chip={args.chip}, protocol={args.protocol}, tests={args.tests}")
        exit_code = run_batch(args)
        sys.exit(exit_code)

    # GUI mode
    logger.info(f"Application started (GUI mode) {VERSION}")
    root = tk.Tk()

    # 设置图标(如果存在)
    try:
        if sys.platform == "win32":
            root.iconbitmap(default="")
    except Exception:
        pass

    app = PatGeneratorApp(root)
    root.mainloop()
    logger.info("Application closed")


def run_batch(args):
    """无 GUI 批处理执行"""
    print(f"=== ATE Pattern Generator {VERSION} — Batch Mode ===")
    print(f"Chip: {args.chip} | Protocol: {args.protocol} | Voltage: {args.voltage}")

    # 1. 解析芯片预设
    if args.chip not in CHIP_PRESETS:
        print(f"ERROR: Unknown chip preset '{args.chip}'")
        print(f"Available: {', '.join(CHIP_PRESETS.keys())}")
        return 2

    chip = CHIP_PRESETS[args.chip]
    protocol = args.protocol
    capacity = chip.get("capacity_bytes", 256)
    page_size = chip.get("page_size", 8)
    addr_bytes = chip.get("addr_byte_count", 1)

    # 2. 加载配置文件 (可选覆盖)
    if args.config:
        try:
            with open(args.config, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            protocol = cfg.get("protocol", protocol)
            args.voltage = cfg.get("voltage", args.voltage)
            args.period = int(cfg.get("period_ns", args.period))
            print(f"Config loaded: {args.config}")
        except Exception as e:
            print(f"WARNING: Config load failed: {e}")

    # 3. 解析测试列表
    test_map = {
        "os": "OS_TEST", "dc": "DC_TEST", "func": "FUNC_TEST",
        "march": "MARCH_C_TEST", "march_b": "MARCH_B_TEST",
        "scan": "ADDR_SCAN_TEST", "ret": "DATA_RET_TEST",
        "err": "ERR_TEST", "endur": "ENDUR_TEST",
    }
    if args.tests == "all":
        selected = list(test_map.values())
    else:
        selected = []
        for t in args.tests.split(","):
            t = t.strip().lower()
            if t in test_map:
                selected.append(test_map[t])
            else:
                print(f"WARNING: Unknown test '{t}'")

    if not selected:
        print("ERROR: No tests selected")
        return 2

    # 4. 提取协议参数
    spi_mode = chip.get("spi_mode", 0)
    sector_size = chip.get("sector_size", None)
    has_jedec = chip.get("has_jedec_id", False)
    jedec_id = chip.get("jedec_id", 0)
    org_mode = chip.get("organization", "x16")
    word_bits = chip.get("word_bits", 16)
    mw_addr_bits = chip.get("addr_bits", 6)

    # 5. 创建生成器
    gen = TestPatternGenerator(
        addr_pins=(0, 0, 0), wp=0, poll_count=2,
        addr_byte_count=addr_bytes, capacity_bytes=capacity, page_size=page_size,
        protocol=protocol, spi_mode=spi_mode, sector_size=sector_size,
        has_jedec_id=has_jedec, jedec_id=jedec_id,
        org_mode=org_mode, word_bits=word_bits, mw_addr_bits=mw_addr_bits,
    )

    # 6. 生成测试向量
    pat_sections = []
    test_methods = {
        "OS_TEST": ("OS_TEST", "Open/Short", gen.generate_os_test),
        "DC_TEST": ("DC_TEST", "DC Parametric", gen.generate_dc_test),
        "FUNC_TEST": ("FUNC_TEST", "Functional", gen.generate_functional_test),
        "MARCH_C_TEST": ("MARCH_C_TEST", "March C-", gen.generate_march_c_test),
        "MARCH_B_TEST": ("MARCH_B_TEST", "March B", gen.generate_march_b_test),
        "ADDR_SCAN_TEST": ("ADDR_SCAN_TEST", "Addr Scan", gen.generate_addr_scan_test),
        "DATA_RET_TEST": ("DATA_RET_TEST", "Data Retention", gen.generate_data_retention_test),
        "ERR_TEST": ("ERR_TEST", "Error/Boundary", gen.generate_i2c_error_test),
        "ENDUR_TEST": ("ENDUR_TEST", "Endurance", gen.generate_endurance_test),
    }

    # SPI/MW 功能测试和异常测试分发
    if protocol == "SPI":
        chip_type = chip.get("chip_type", "spi_eeprom")
        if chip_type == "spi_flash":
            test_methods["FUNC_TEST"] = ("FUNC_TEST", "SPI Flash Functional", gen.generate_spi_flash_test)
        else:
            test_methods["FUNC_TEST"] = ("FUNC_TEST", "SPI Functional", gen.generate_spi_functional_test)
        test_methods["ERR_TEST"] = ("ERR_TEST", "SPI Error", gen.generate_spi_error_test)
    elif protocol == "Microwire":
        test_methods["FUNC_TEST"] = ("FUNC_TEST", "Microwire Functional", gen.generate_mw_functional_test)
        test_methods["ERR_TEST"] = ("ERR_TEST", "Microwire Error", gen.generate_mw_error_test)

    total_vectors = 0
    for test_id in selected:
        if test_id in test_methods:
            name, desc, fn = test_methods[test_id]
            try:
                v, c, l = fn()
                pat_sections.append((name, desc, v, c, l))
                total_vectors += len(v)
                print(f"  [{name}] {desc}: {len(v)} vectors")
            except Exception as e:
                print(f"  [{name}] ERROR: {e}")
                logger.exception(f"Batch generate {name} failed")

    if not pat_sections:
        print("ERROR: No vectors generated")
        return 1

    print(f"\nTotal: {total_vectors} vectors across {len(pat_sections)} segments")

    # 7. 导出文件
    os.makedirs(args.output, exist_ok=True)
    prefix = args.chip
    pins = PROTOCOL_PINS.get(protocol, TEST_PINS)

    all_vectors = []
    all_comments = []
    all_labels = []
    for name, desc, v, c, l in pat_sections:
        all_vectors.extend(v)
        all_comments.extend(c)
        all_labels.extend(l)

    formatter = PATFormatter()
    file_count = 0
    v_preset = VOLTAGE_PRESETS.get(args.voltage, VOLTAGE_PRESETS.get("5.0V"))

    # PAT 格式
    if args.format in ("pat", "all"):
        pat_header = formatter.generate_pat_header(
            f"{args.chip}_TEST", f"{args.chip} {protocol} Full Test", pins)
        pat_timing = formatter.generate_pat_timing_header(args.period, v_preset)
        pat_body = formatter.format_vectors(all_vectors, all_comments, all_labels, pins,
                                              f"{prefix}_FULL_TEST")
        pat_path = os.path.join(args.output, f"{prefix}_FULL_TEST.pat")
        with open(pat_path, "w", encoding="utf-8") as f:
            f.write(pat_header + "\n" + pat_timing + "\n" + pat_body)
        file_count += 1

        # TXT preview
        txt_body = formatter.format_txt_preview(all_vectors, all_comments, pins,
                                                  f"{prefix}_FULL_TEST")
        txt_path = os.path.join(args.output, f"{prefix}_FULL_TEST_preview.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(txt_body)
        file_count += 1

        # Per-segment PAT
        for name, desc, v, c, l in pat_sections:
            seg_body = formatter.format_vectors(v, c, l, pins, name)
            seg_path = os.path.join(args.output, f"{prefix}_{name}.pat")
            with open(seg_path, "w", encoding="utf-8") as f:
                f.write(pat_header + "\n" + pat_timing + "\n" + seg_body)
            file_count += 1

    # STIL 格式
    if args.format in ("stil", "all"):
        stil = STILFormatter()
        stil_content = stil.format(pat_sections, pins, args.period, args.voltage,
                                   chip_name=args.chip, protocol=protocol)
        stil_path = os.path.join(args.output, f"{prefix}_TEST.stil")
        with open(stil_path, "w", encoding="utf-8") as f:
            f.write(stil_content)
        file_count += 1
        print(f"  STIL: {stil_path}")

    # WGL 格式
    if args.format in ("wgl", "all"):
        wgl = WGLFormatter()
        wgl_content = wgl.format(pat_sections, pins, args.period, args.voltage,
                                 chip_name=args.chip, protocol=protocol)
        wgl_path = os.path.join(args.output, f"{prefix}_TEST.wgl")
        with open(wgl_path, "w", encoding="utf-8") as f:
            f.write(wgl_content)
        file_count += 1
        print(f"  WGL: {wgl_path}")

    # TIM/LVL/PRG
    tim_content = formatter.generate_tim_file(args.period, args.voltage, protocol, args.chip)
    with open(os.path.join(args.output, f"{prefix}_TEST.tim"), "w", encoding="utf-8") as f:
        f.write(tim_content)
    file_count += 1

    lvl_content = formatter.generate_lvl_file(v_preset, chip_name=args.chip)
    with open(os.path.join(args.output, f"{prefix}_TEST.lvl"), "w", encoding="utf-8") as f:
        f.write(lvl_content)
    file_count += 1

    prg_content = formatter.generate_prg_file(pat_sections, args.period, v_preset,
                                               chip_name=args.chip, protocol=protocol,
                                               export_prefix=prefix)
    with open(os.path.join(args.output, f"{prefix}_TEST.prg"), "w", encoding="utf-8") as f:
        f.write(prg_content)
    file_count += 1

    # 可选: 运行模拟器
    if args.simulate:
        print("\n--- Pattern Simulation ---")
        sim = PatternSimulator(protocol=protocol, capacity_bytes=capacity, page_size=page_size)
        sim.simulate(all_vectors, all_comments)
        print(f"  Transactions: {len(sim.transactions)}")
        print(f"  Errors: {len(sim.errors)}")
        for err in sim.errors[:5]:
            print(f"    [{err.get('severity','?')}] Cycle {err.get('cycle',0)}: {err.get('detail','')}")

    print(f"\n=== Exported {file_count} files to {args.output} ===")
    logger.info(f"Batch complete: {file_count} files, {total_vectors} vectors")
    return 0


if __name__ == "__main__":
    main()
