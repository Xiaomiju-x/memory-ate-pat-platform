# 文件与向量格式 / Formats

本项目同时处理通用 AT24C02 / 多器件平台格式，以及复赛 BY25Q40AL 专用格式。两者都使用 `.pat` 扩展名，但引脚、状态约束和时钟方言不同，不能仅凭扩展名互换。

## 1. 向量状态

| 符号 | 含义 | ATE 侧意图 |
|---|---|---|
| `0` | Drive Low | 驱动引脚为低电平 |
| `1` | Drive High | 驱动引脚为高电平 |
| `L` | Expect Low | 比较 DUT 输出，期望低 |
| `H` | Expect High | 比较 DUT 输出，期望高 |
| `Z` | Hi-Z | 释放驱动，进入高阻态 |
| `X` | Don't Care / released phase | 不比较；在本项目读与 ACK 非采样相位也用于释放语义 |

状态字符的实际电气行为由目标 ATE 的 pin electronics、时序集和电平集共同决定。不要在未核对设备文档时，假设所有平台对 `X`、`Z` 或比较状态的解释完全相同。

## 2. AT24C02 EStar 风格 PAT

### 引脚顺序

当前根平台的 I2C PAT 固定为：

```text
A0, A1, A2, WP, SCL, SDA
```

因此一条 `000011` 表示 `A0=0, A1=0, A2=0, WP=0, SCL=1, SDA=1`。

典型文件结构：

```text
HEAD[PIN_NAME]:
 A0,
 A1,
 A2,
 WP,
 SCL,
 SDA;
END_HEAD;
@@PATTERN_DEFINE
// A0,A1,A2,WP,SCL,SDA

start:              000011;AC_SET 1;
                    ...
end:                000011;
@@END_PATTERN_DEFINE
```

`start:` 首向量携带 `AC_SET 1;`，`end:` 是 PRG 调用的结束标签。具体空白、注释和附加时序头以生成器版本为准。

### I2C 每 bit 四向量

写 bit 使用 `setup → sample → hold → end` 四个周期。以写入 `1`、且地址/WP 引脚均为 0 为例：

```text
000001;  // SCL=0, SDA=1: setup
000011;  // SCL=1, SDA=1: sample
000011;  // SCL=1, SDA=1: hold
000001;  // SCL=0, SDA=1: end
```

从机 ACK 检查：

```text
00000X;  // SCL=0, SDA released / don't care
00001L;  // SCL=1, expect ACK low
00001L;  // SCL=1, hold compare
00000X;  // SCL=0, end
```

读 bit 的非采样相位使用 `X`，SCL 高电平比较相位使用 `H` 或 `L`。这种选择是当前 EStar 风格实现契约，不应机械替换为 `Z`。

`TIM` 中的 `PERIOD` 是每一条 PAT 向量的周期，不是完整 I2C bit 的周期。连续 bit 的
SCL 序列为 `0,1,1,0 | 0,1,1,0`，因此高、低电平各占两个向量周期：

```text
tHIGH = 2 × PERIOD
tLOW  = 2 × PERIOD
fSCL  = 1 / (4 × PERIOD)
```

例如 `PERIOD=2500ns` 时，向量率为 `400k vectors/s`，而实际 I2C `fSCL=100kHz`。

### I2C 地址

AT24C02 器件地址字节：

```text
bit7                                            bit0
 1      0      1      0      A2     A1     A0     R/W
```

默认 `A2=A1=A0=0` 时，写地址是 `0xA0`，读地址是 `0xA1`。大容量 AT24C 器件可能使用页选择位或两字节字地址，应由器件预设提供，不能照搬 AT24C02 地址规则。

## 3. BY25Q40AL 复赛公开版 Memory PAT

以下是团队公开生成器当前输出的方言说明，不是赛方原始规范或参考 PAT 的转载。公开版的 HEAD 顺序为：

```text
HEAD[PIN_NAME]:
CS_N,
SO_IO1,
WP_IO2,
SI_IO0,
SCLK,
HOLD_IO3;
END_HEAD;
```

约束包括：

- 每条向量恰好 6 个状态；
- 正式 Memory 输出只使用 `0/1/H/L/X`，不使用大写 `Z`；
- 每个 SCLK 使用四条向量：低、低、高、高；
- DUT 输出比较位放在第二个低相位；
- Standard、Dual、Quad 的页写命令分别为 `02h/A2h/32h`；
- Standard、Dual、Quad 的读命令分别为 `03h/3Bh/6Bh`；
- Dual / Quad 读取包含 8 个 dummy clock；
- 首向量、RPT、LOOP、标签和输出文件名由公开生成器与团队测试约束。

Standard SPI 读回一个低 bit 的四个物理向量示意：

```text
0X1X01;
0L1X01;
0X1X11;
0X1X11;
```

赛方提供的 FUNC 参考模板、黄金 PAT 和相关私有规范不随公开仓库分发，本页也不复刻其内容。合法持有者只能在授权范围自行离线核验；本项目不接收、不定位、不自动读取或提供相关资产，也不提供其哈希、复制或对比工具。私有核验不属于公开复现步骤。详见[知识产权与公开边界](legal-and-ip.md)。

## 4. 工程文件职责

### `.pat`

包含引脚顺序、逐周期状态、标签、注释和可能的 RPT / LOOP 等微指令。根平台可生成合并 PAT、按测试段拆分 PAT，以及独立 ACK Polling 段。

### `.txt`

把向量、周期号、引脚状态和注释排成适合人工查看的表格。TXT 是审阅视图，不是执行文件；不要反向假设它保留 PAT 的全部微指令语义。

### `.prg`

描述测试调度和 PLAN，例如测试前序列、OS/DC、`RUN_PATTERN`、条件分 Bin 和 EOT。根平台使用 `@@SCHEDULE`、`@@PLAN`、`@@EOT` 风格模板。

### `.tim`

定义周期、驱动沿和比较沿。根平台的 EStar 风格模板包含 `@@TIMING_DEFINE`、`@@AC_SET_1`、`PERIOD`、`DRV_LE`、`DRV_TE`、`STB` 等字段。

### `.lvl`

定义电源和数字电平集合，如断电、工作电压、输入漏电、IDD 和 PPMU 工况。生成值来自所选电压预设，但仍需按 DUT 数据手册、负载板和 ATE 量程复核。

### `.stil` / `.wgl`

由根平台的独立 formatter 导出，用于交换或迁移。生成成功只代表通过本项目格式化路径，不代表任意第三方工具都能无修改导入。

### `.json`

保存 GUI 配置或项目状态。配置快照可能包含本机路径或操作者输入；公开前应检查隐私和秘密信息。

### `.html` / `.svg`

用于报告、交互式波形、流程图、Shmoo、Wafer Map 和覆盖率展示。HTML 中的统计和模拟结论应与真实测量结果明确区分。

### `.csv` / `.dlog` / `.stdf`

用于统计、Datalog 和标准测试数据交换。项目能够生成模拟记录并读写部分 STDF V4 记录；这不表示覆盖 STDF 的全部记录类型或厂商扩展。

### `MANIFEST.txt`

GUI 完整导出后生成 SHA-256 清单，用于发现文件丢失或意外修改。哈希证明“字节未变化”，不证明向量在真实硬件上正确或安全。

## 5. 跨文件一致性

交付前至少检查以下映射：

| 来源 | 消费方 | 必须一致 |
|---|---|---|
| PAT `HEAD` | Pin Map / ATE 通道 | 名称、顺序、方向 |
| PAT `AC_SET` | TIM | 时序集合编号 |
| PRG `RUN_PATTERN` | PAT | 文件名、start/end 标签 |
| LVL / TIM | 器件与电压配置 | VCC、VIH/VIL、VOH/VOL、周期、比较沿 |
| 测试段 | Bin / Datalog | 测试名、限值、单位、Fail 分类 |
| 配置 JSON | 导出清单 | 器件、协议、地址、测试选择和版本 |

## 6. 验证清单

在真实 ATE 前，建议按顺序验证：

1. UTF-8、行尾和文件名是否满足导入工具要求；
2. HEAD 引脚数量、顺序和状态字符是否合法；
3. PATTERN 块、标签、RPT / LOOP 是否闭合；
4. PRG、TIM、LVL 对 PAT 的引用是否存在；
5. I2C / SPI / Microwire 事务能否由协议解析器复原；
6. 时序和电平是否满足目标器件具体版本的数据手册；
7. ATE 离线编译 / 导入是否通过；
8. 使用安全的限流、低风险向量和已知样片完成小范围真机验证；
9. 再逐步扩大地址范围、并行 Site 和压力测试。

本项目已知限制和责任边界见[常见问题](faq.md)。
