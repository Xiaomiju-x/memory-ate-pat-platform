# CLAUDE.md — AT24C02 PAT测试向量生成工具

## 项目概览

这是一个为 **全国大学生集成电路创新创业大赛"胜达克"企业命题** 开发的工具。

目标：为 AT24C02 I2C EEPROM 芯片自动生成 ATE（自动测试设备）测试用的完整测试文件包，配合 AdaptStar-E (EStar) 测试系统使用。

核心功能：根据 AT24C02 的 I2C 协议和电气规格，生成 9 组主测试流程及独立 IDDQ 逻辑（OS/DC/功能/March/地址扫描/数据保持/I2C异常/耐久性/IDDQ），导出完整 ATE 工程文件包（.pat/.txt/.prg/.tim/.lvl/.html/.json），支持多Site并行、温度角分析、测试阶段管理、自适应测试流、Guard Band优化、参数相关性分析、PAT反向解析、STDF导入、AEC-Q100/JEDEC标准合规、版本对比。

## 项目结构

```
AT24C02_PAT_TOOL/
├── at24c02_pat_generator.py   # 主程序（GUI + 全部核心逻辑，单文件架构，约3.4万行, 49类, 16 Tab）
├── generate_samples.py        # 无GUI批量生成示例文件的脚本（全14段测试输出到output/）
├── waveform_html.py           # 交互式 HTML 波形查看器（独立模块，~770行）
├── flowchart_template.py      # HTML 流程图模板生成器（~190行）
├── patch_proto.py             # 协议矩阵补丁脚本
├── build_exe.bat              # Windows PyInstaller 打包脚本
├── README.md                  # 用户文档
├── CLAUDE.md                  # 本文件
├── CLAUDE_CODE_PROMPTS.md     # Claude Code 迁移指令手册
├── MIGRATION_PLAN.md          # tkinter → CustomTkinter 迁移任务规划
├── AT24C02_PAT_Generator_v8.0.0.spec  # 当前 PyInstaller 配置文件
├── legacy/tkinter/at24c02_pat_generator.py # tkinter-only 历史快照（非当前入口）
├── examples/legacy/            # 根目录旧样例与早期批量输出归档
├── output/                    # generate_samples.py 生成的完整输出
│   ├── AT24C02_FULL_TEST.pat / _preview.txt / .prg / _stats.csv
│   ├── AT24C02_OS_TEST.pat / _preview.txt
│   ├── AT24C02_DC_TEST.pat / _preview.txt / _ACK_POLL.pat
│   ├── AT24C02_FUNC_TEST.pat / _preview.txt (合并功能段)
│   ├── AT24C02_FUNC_BW.pat / _preview.txt / _ACK_POLL.pat (字节写读)
│   ├── AT24C02_FUNC_PW.pat / _preview.txt / _ACK_POLL.pat (页写读)
│   ├── AT24C02_FUNC_BOUND.pat / _preview.txt / _ACK_POLL.pat (边界)
│   ├── AT24C02_FUNC_WP.pat / _preview.txt / _ACK_POLL.pat (WP保护)
│   ├── AT24C02_FUNC_WRAP.pat / _preview.txt / _ACK_POLL.pat (翻转)
│   ├── AT24C02_FUNC_CAR.pat / _preview.txt / _ACK_POLL.pat (进位)
│   ├── AT24C02_MARCH_TEST.pat / _preview.txt / _ACK_POLL.pat
│   ├── AT24C02_MARCHB_TEST.pat / _preview.txt / _ACK_POLL.pat
│   ├── AT24C02_SCAN_TEST.pat / _preview.txt / _ACK_POLL.pat
│   ├── AT24C02_RET_TEST.pat / _preview.txt / _ACK_POLL.pat
│   ├── AT24C02_ERR_TEST.pat / _preview.txt / _ACK_POLL.pat
│   ├── AT24C02_ENDUR_TEST.pat / _preview.txt / _ACK_POLL.pat
│   ├── AT24C02_level.lvl
│   ├── AT24C02_timing.tim
│   ├── flowchart.html         # 交互式流程图 HTML
│   └── waveform.html          # 交互式波形查看 HTML
├── examples/legacy/batch-v1/ # 旧版批量测试输出（含 .prg/.tim/.lvl）
├── examples/legacy/batch-v6/ # v6批量测试输出（含 .stil/.wgl 格式导出）
├── dist/                      # PyInstaller 打包输出（AT24C02_PAT_Generator_v8.0.0.exe）
├── build/                     # PyInstaller 构建中间文件（可忽略）
└── __pycache__/               # Python 缓存（可忽略）
```

## 导出文件包 (GUI导出时完整输出)

| 扩展名 | 说明 |
|--------|------|
| `.pat` | ATE 可执行的 PAT 向量文件（合并 + 按测试段分拆） |
| `.txt` | 人类可读的向量表格预览 |
| `.prg` | ATE 测试程序 — EStar 格式（@@SCHEDULE / @@EOT / @@PLAN 块结构） |
| `.tim` | ATE 时序定义 — EStar 格式（@@TIMING_DEFINE / @@AC_SET_1 / DRV_LE/DRV_TE/STB） |
| `.lvl` | ATE 电平定义 — EStar 格式（@@LEVEL_SET_DEFINE: DC_0V_PWR / DC_VCC_LVL / DC_IDD / PWR_OFF） |
| `.html` | 测试报告（统计/覆盖率/限值表/饼图/文件清单）+ 交互式波形/流程图 |
| `.json` | GUI 配置快照（可重新加载） |
| `.svg` | I2C 波形矢量图 / Shmoo Plot / Wafer Map / 迁移报告（通过各页导出按钮生成） |
| `.stdf` | STDF V4 标准测试数据格式（二进制，兼容行业分析工具） |
| `.csv` | Datalog / Bin Summary CSV 导出 |
| `_compressed.pat` | 向量压缩 PAT（REPEAT/LOOP/SUBROUTINE 指令） |

## 技术栈

- **语言**: Python 3.10+
- **GUI**: CustomTkinter + tkinter/ttk 原生控件
- **打包**: PyInstaller（生成 Windows .exe）
- **目标平台**: Windows 10/11（exe运行环境）
- **运行依赖**: `customtkinter`（见 `requirements.txt`）；其余核心逻辑以标准库为主

## 主程序架构 (at24c02_pat_generator.py)

主文件约3.4万行，含49个类；另有3个辅助模块：

```
常量定义
├── AT24C02_PINS / TEST_PINS     # 引脚定义
├── I2C_TIMING                    # I2C时序参数
├── VOLTAGE_PRESETS               # 多电压等级预设 (1.8V/2.5V/3.3V/5.0V)
├── TEST_LIMITS                   # 测试限值表 (12项 Pass/Fail 判定标准)
├── I2C_TIMING_CONSTRAINTS        # 各电压的I2C时序约束 (tLOW/tHIGH/tSU等)
├── I18N                          # 国际化翻译字典 (zh/en, 140+ key)
└── THEMES                        # 深色/浅色主题配色

I2CVectorGenerator               # I2C协议层：生成逐周期的SCL/SDA信号向量
├── add_start_condition()        # I2C START: SCL高时SDA下降沿
├── add_stop_condition()         # I2C STOP: SCL高时SDA上升沿
├── add_repeated_start()         # Repeated START
├── add_write_byte()             # 写8bit (MSB first, 每bit=4个向量周期, EStar 格式)
├── add_read_byte()              # 读8bit (SDA设为X/H/L比较状态, 4向量/bit)
├── add_ack_from_slave()         # 从机ACK检查 (期望SDA=L)
├── add_nack_from_master()       # 主机NACK
├── add_ack_from_master()        # 主机ACK (顺序读)
├── gen_byte_write()             # 完整字节写事务 + ACK Polling
├── gen_random_read()            # 完整随机读事务 (写地址+RepSTART+读)
├── gen_page_write()             # 页写 (最多8字节/页) + ACK Polling
├── gen_sequential_read()        # 顺序读 (连续读多字节)
└── gen_ack_polling()            # 应答查询 (写周期完成等待)

SPIVectorGenerator               # SPI协议层：生成逐周期的SCLK/MOSI/MISO/CS信号向量
MicrowireVectorGenerator         # Microwire协议层：生成逐周期的SK/DI/DO/CS信号向量

TestPatternGenerator             # 测试方案层：组合I2C操作为完整测试流程
├── generate_os_test()           # 1. 开短路: Walking-1/Walking-0
├── generate_dc_test()           # 2. DC: ISB/ICC/VOL/VOH/VIL/VIH
├── generate_functional_test()   # 3. 功能: 字节写读/页写读/边界/WP/自定义
├── generate_march_c_test()      # 4. March C-: 6步经典存储器测试(SAF/TF/CF)
├── generate_addr_scan_test()    # 5. 地址扫描: 可配置范围写入+读回
├── generate_data_retention_test()  # 6. 数据保持: 棋盘格/全0/全1 写-等-验
├── generate_i2c_error_test()    # 7. I2C异常: 错误地址/不完整事务/总线恢复/多START
└── generate_endurance_test()    # 8. 耐久性: 同地址反复擦写+读回

PATFormatter                     # 输出格式化层 (EStar 官方格式)
├── generate_pat_header()        # PAT文件头 (HEAD[PIN_NAME]/END_HEAD)
├── format_vectors()             # 向量格式化 (@@PATTERN_DEFINE/start:/end:)
├── format_txt_preview()         # 人类可读表格 (.txt)
├── generate_tim_file()          # 时序配置 (@@TIMING_DEFINE/@@AC_SET_1)
├── generate_lvl_file()          # 电平配置 (@@LEVEL_SET_DEFINE: 5组)
└── generate_prg_file()          # 测试程序 (@@SCHEDULE/@@EOT/@@PLAN)

STILFormatter                    # STIL 格式导出器
WGLFormatter                     # WGL 格式导出器

I2CTimingChecker                 # I2C 时序合规性检查器
└── check(period, voltage)       # 8项时序参数校验 (fSCL/tLOW/tHIGH/tSU/tHD/tBUF)
SPITimingChecker                 # SPI 时序合规性检查器
MicrowireTimingChecker           # Microwire 时序合规性检查器

VectorProtocolValidator          # I2C 向量协议合规性验证器
└── validate(vectors, comments)  # SDA变化规则/总线状态/START-STOP配对检查
SPIProtocolValidator             # SPI 协议合规性验证器
MicrowireProtocolValidator       # Microwire 协议合规性验证器

PatternSimulator                 # 向量模拟器 (Fail Bit Map)
ShmooEngine                      # Shmoo V×F 参数表征 (3色: PASS/MARGINAL/FAIL + 规格框)
TestFlowEngine                   # 测试流程引擎 (可视化编排/执行/仿真)
MultiSiteGenerator               # 多Site并行向量生成器
DatalogAnalyzer                  # Datalog 数据分析器
ProjectManager                   # 项目/会话管理器
ToolTip                          # GUI 工具提示组件
BinningEngine                    # 9-Bin 分类系统 (Good Die + 8 Fail Bins)
DatalogGenerator                 # Monte Carlo Datalog 模拟 (单颗/批量)
STDFWriter                       # STDF V4 标准测试数据格式导出 (FAR/MIR/SDR/PMR/PTR/FTR/PRR/MRR)
VectorCompressor                 # 向量压缩引擎 (3层: REPEAT/LOOP/SUBROUTINE)
WaferMapGenerator                # 晶圆图 (200mm, 空间缺陷模型, Bin Map/良率热力图)
VectorDebugger                   # 向量同步调试器 (单步/事务步/段步/断点)
FaultCoverageSimulator           # ATPG 故障覆盖率仿真
YieldPredictor                   # 良率预测 + Monte Carlo
TestEconomicsEngine              # 测试经济学分析
MemoryATPG                       # March C- 覆盖率证明
ChipMigrationEngine              # 芯片迁移分析引擎 (跨型号向量映射/差异对比)
EStarValidator                   # EStar PAT 文件校验器 (PAT/LVL/TIM/PRG + STIL + WGL)
DatasheetComplianceMatrix        # Datasheet 参数覆盖矩阵 (34项参数, 5类, 含IDDQ)
PowerSequenceGenerator           # 上电/下电/热切换序列生成器
TemperatureCornerSimulator       # 三温参数漂移仿真 (8参数×商业级/工业级温度角)
PinMapManager                    # ATE Pin Electronics 通道分配 (PE/DPS/PMU)
TestPhaseManager                 # 测试阶段管理 (Wafer Sort/Final/QA/Incoming/Characterization)
AdaptiveTestEngine               # 自适应测试流引擎 (6规则: OS FastBin/DC Marginal/ISB/March/AllPass/IDDQ)
GuardBandEngine                  # Guard Band 限值优化 (高斯CDF + DPPM 目标收紧)
CorrelationAnalyzer              # DC 参数相关性分析 (Pearson 矩阵 + 异常值检测)
PATReverseParser                 # PAT 文件反向解析 (I2C/SPI/MW 事务解码)
STDFReader                       # STDF V4 二进制导入分析器 (STDFWriter 逆操作)
StandardsComplianceMapper        # AEC-Q100/JEDEC 标准合规映射
TestProgramVersionManager        # 测试程序版本管理与对比

辅助模块 (独立 .py 文件)
├── waveform_html.py             # 交互式 HTML 波形查看器 (~770行, 生成 waveform.html)
├── flowchart_template.py        # HTML 流程图模板 (~190行, 生成 flowchart.html)
└── patch_proto.py               # 协议矩阵热补丁脚本

PatGeneratorApp                  # GUI层 (CustomTkinter + tkinter, 16 Tab)
├── build_toolbar()              # 顶部: A2/A1/A0/WP/VCC/Sites/地址/生成/导出/阶段/主题/语言
├── build_config_panel()         # 左侧: 芯片图/10测试选择/自定义参数/地址范围/周期/前缀/Pin Map/检查按钮
├── build_preview_panel()        # 右侧: 16标签页预览面板
├── on_generate()                # 生成: 按选择调用测试方案 → 预览/波形/流程图/统计
├── on_export()                  # 导出: .pat/.txt/.prg/.tim/.lvl/.html/.json 完整文件包
├── _run_timing_check()          # 时序合规性检查 (弹窗显示8项结果)
├── _run_protocol_check()        # 协议合规性检查 (弹窗显示issue列表)
├── _draw_waveform()             # Canvas I2C波形图 (SCL/SDA信号+事件标注)
├── _export_waveform_svg()       # 波形导出为SVG矢量图
├── _draw_flowchart()            # Canvas测试流程图 (START→各段→END)
├── _update_statistics()         # 统计面板 (条形图/覆盖率/协议特性/测试限值表)
├── _generate_html_report()      # HTML报告 (饼图/覆盖率/限值表/文件清单)
├── _toggle_theme()              # 深色/浅色主题切换 (重建UI)
├── _toggle_language()           # 中文/英文国际化切换 (重建UI)
└── _save_config/_load_config()  # JSON配置保存/加载
```

## 测试向量分类（9 组主流程，含独立 IDDQ）

| # | 测试类型 | 检测目标 |
|---|----------|----------|
| 1 | OS (开短路) | PPMU Walking-1/0 逐引脚连通性 |
| 2 | DC (参数) | ISB/ICC/VOL/VOH/VIL/VIH |
| 3 | FUNC (功能) | 字节写读/页写读/边界/WP保护/自定义 |
| 4 | March C- | SAF/TF/CF 故障模型 (6步算法) |
| 5 | Addr Scan | 地址空间完整性 (写入addr^0x55+读回) |
| 6 | Data Ret | 棋盘格/全0/全1 写入-等待-验证 |
| 7 | I2C Error | 错误地址NACK/不完整事务/总线恢复/多START |
| 8 | Endurance | 同地址10轮擦写循环+读回验证 |
| 9 | IDDQ | 8点静态漏电流测量 (PMU, 操作间/多地址/WP切换) |

注: I2C 每 bit 使用 4 个向量周期 (setup→sample→hold→end)，与 EStar 真机格式一致。
实际导出会进一步拆分功能子段；向量数量随配置、地址范围和所选测试变化。

## 向量状态符号约定

PAT文件中每个引脚每个周期的状态：

| 符号 | 含义 | ATE行为 |
|------|------|---------|
| `0` | Drive Low | ATE驱动引脚输出低电平 |
| `1` | Drive High | ATE驱动引脚输出高电平 |
| `L` | Expect Low | ATE比较器检查DUT输出是否为低（不匹配=FAIL） |
| `H` | Expect High | ATE比较器检查DUT输出是否为高（不匹配=FAIL） |
| `Z` | Hi-Z | ATE释放引脚（三态，让DUT驱动） |
| `X` | Don't Care | ATE不比较，忽略该周期 |

## EStar PAT 文件格式 (基于真机文件校准)

PAT 文件结构:
```
HEAD[PIN_NAME]:
 A0, A1, A2, WP, SCL, SDA;
END_HEAD;
@@PATTERN_DEFINE
start:              000011;AC_SET 1;
                    ...
end:                000011;
@@END_PATTERN_DEFINE
```

I2C 每 bit 时序 (4 向量/bit):
```
000001;  // SCL=0, SDA=data (setup)
000011;  // SCL=1, SDA=data (sample - 器件在此采样)
000011;  // SCL=1, SDA=data (hold)
000001;  // SCL=0, SDA=data (end)
```

ACK 时序 (4 向量):
```
00000X;  // SCL=0, SDA=X (释放SDA)
00001L;  // SCL=1, SDA=L (检查ACK=LOW)
00001L;  // SCL=1, SDA=L (hold)
00000X;  // SCL=0, SDA=X (结束)
```

关键格式细节:
- 首向量必须有 `start:` 标签 + `AC_SET 1;` 后缀
- 末向量必须有 `end:` 标签
- PRG 通过 `RUN_PATTERN(filename:start, filename:end, 1, ...)` 引用
- 读 bit 的 SDA 非采样相位使用 `X`（Don't Care），不使用 `Z`

## AT24C02 关键参数

- I2C器件地址: `1010_A2_A1_A0_R/W` (默认A2=A1=A0=0 → Write=0xA0, Read=0xA1)
- 容量: 256×8bit = 2Kbit
- 页大小: 8字节
- 写周期: ≤5ms (tWR)
- I2C速率: 最高1MHz@5V, 400kHz@1.8V
- VCC: 1.8V~5.5V
- 擦写寿命: 100万次 (25°C)
- 数据保持: 100年 (25°C)
- 引脚 (SOP-8): 1=A0, 2=A1, 3=A2, 4=GND, 5=SDA, 6=SCL, 7=WP, 8=VCC

## 测试限值表 (Pass/Fail 判定标准)

| 参数 | 描述 | Min | Max | 单位 | 条件 |
|------|------|-----|-----|------|------|
| ISB | 待机电流 | — | 1.0 | μA | VCC=5.5V |
| ICC(R) | 读电流 | — | 1.0 | mA | fSCL=400kHz |
| ICC(W) | 写电流 | — | 3.0 | mA | fSCL=400kHz |
| VOL | 输出低电平 | — | 0.4 | V | IOL=3mA |
| VIL(5V) | 输入低 | -0.5 | 1.5 | V | VCC=5V |
| VIH(5V) | 输入高 | 3.5 | 5.5 | V | VCC=5V |
| tWR | 写周期 | — | 5.0 | ms | Page/Byte |
| Endurance | 擦写寿命 | 1M | — | cycles | 25°C |
| Retention | 数据保持 | 100 | — | years | 25°C |

## 多电压支持

| 电压 | VIH | VIL | VOH | VOL | IOL | fSCL max | 默认周期 |
|------|-----|-----|-----|-----|-----|----------|----------|
| 5.0V | 3.5V | 1.5V | 2.4V | 0.4V | 3mA | 1MHz | 2500ns |
| 3.3V | 2.31V | 0.99V | 2.4V | 0.4V | 3mA | 400kHz | 2500ns |
| 2.5V | 1.75V | 0.75V | 2.0V | 0.4V | 1mA | 400kHz | 2500ns |
| 1.8V | 1.17V | 0.63V | 1.35V | 0.45V | 1mA | 100kHz | 10000ns |

## 常用命令

```bash
# 运行GUI工具
python at24c02_pat_generator.py

# 无GUI批量生成示例文件到 output/（全14段测试 + ACK Polling + 子功能段）
python generate_samples.py

# 打包为Windows .exe（在Windows cmd中执行）
python -m PyInstaller --clean --noconfirm AT24C02_PAT_Generator_v8.0.0.spec

# 打包产物在 dist/AT24C02_PAT_Generator_v8.0.0.exe
```

## GUI功能速览

- **顶部工具栏**: A2/A1/A0地址引脚 | WP写保护 | VCC电压选择 | 多Site并行(1/2/4/8) | 器件地址显示 | 生成/导出按钮 | 测试阶段选择(Wafer Sort/Final/QA等) | 导入PAT/STDF | 版本管理(Ⓥ) | 主题切换(☀/☾) | 语言切换(EN/中文)
- **左侧配置面板**: AT24C02芯片引脚图 | 10种测试类型复选 | 自定义写入参数 | 测试地址范围 | 向量周期 | 导出前缀 | Pin Map配置 | 配置保存/加载 | 时序检查/协议检查按钮
- **右侧预览面板 (16个标签页)**:
  1. PAT向量: 语法高亮 + 行号 + 段跳转 + 搜索(Ctrl+F)
  2. TXT预览: 人类可读表格
  3. 波形图: SCL/SDA时序波形 + 事件标注 + SVG导出 + HTML交互式波形
  4. 测试说明: 10种测试项原理描述 + AEC-Q100/JEDEC标准合规矩阵
  5. 流程图: START→上电→各测试段(含PASS/FAIL分支)→END + HTML交互式流程图
  6. 统计: 向量分布条形图 + 覆盖率分析 + 协议特性矩阵 + 测试限值表 + Datasheet覆盖矩阵
  7. 模拟器: 向量模拟执行 + Fail Bit Map
  8. Shmoo: V×F参数表征散点图 + 规格框 + SVG导出
  9. 流程编排: 可视化测试流编辑 + 自适应测试流仿真
  10. 良率: Monte Carlo + Guard Band限值优化 + DPPM分析
  11. ATPG覆盖率: ATPG仿真 + SAF/TF/CF/AF故障模型 + March覆盖证明
  12. 测试经济学: 测试成本/时间分析 + COT优化
  13. 芯片迁移: 跨型号向量映射 + 差异对比 + 迁移报告
  14. Datalog: 单颗/批量Monte Carlo模拟 + STDF导出/导入 + 参数相关性分析
  15. Wafer Map: 200mm晶圆图 + 空间缺陷模型 + Bin着色
  16. 温度角: 三温(-40°C/25°C/125°C)参数漂移仿真 + 商业级/工业级

## 键盘快捷键

| 快捷键 | 功能 |
|--------|------|
| Ctrl+G | 生成PAT |
| Ctrl+E | 导出文件 |
| Ctrl+F | 搜索 |

## 编码规范

- 核心逻辑集中在 `at24c02_pat_generator.py` 中，辅助模块仅用于 HTML 交互式输出（waveform_html.py / flowchart_template.py）
- 中文注释为主，代码变量名和类名用英文
- 向量数据结构：每个向量是 `dict`，key为引脚名 ("A0","A1","A2","SDA","SCL","WP")，value为状态字符串
- 引脚顺序固定：`TEST_PINS = ["A0", "A1", "A2", "WP", "SCL", "SDA"]`
- tkinter的 `pady` 等接受tuple的参数必须放在 `.pack()/.grid()` 里，不能放在 Widget 构造函数里（否则运行报错 `bad screen distance`）
- I18N: 所有UI文本通过 `self.t(key)` 获取，支持 zh/en 切换
- 文件编码统一 UTF-8

## 已知问题

- PAT格式基于通用ATE向量格式设计，未完全适配AdaptStar-E私有格式（赛方未公开完整格式规范）
- .prg/.tim/.lvl 为模板文件，实际ATE语法可能需要根据AdaptStar-E文档微调

## 已修复问题

- ~~`build_exe.bat` 在中文Windows上有编码乱码~~ → 已改用 `chcp 65001` + 英文提示
- ~~"自定义写入数据"输入框未实际使用~~ → 已接入 FUNC-5 自定义写入测试
- ~~WP引脚状态未传入向量生成~~ → 已支持WP配置并新增 FUNC-4 WP写保护测试
- ~~写操作后使用固定idle等待~~ → 已替换为 ACK Polling 机制
- ~~器件地址标签不随A2/A1/A0变化更新~~ → 已添加实时刷新
- ~~DC测试在WP=1时写操作会失败~~ → 已在DC测试开头强制WP=0
- ~~模式5数据预览"左移N次："列标题与数据列累积偏移~~ → `SimplePATFormatter._generate_mode5_preview` 改用非均匀列宽 `HEADER_CELL_WIDTHS = [26,25,26,26,25,26,26,26]`（dw），经验模型：用户查看器（微软雅黑等比例字体）中 1 个 ASCII 尾空格视觉宽 ≈ 0.333 格，目标平均尾空格 16.71/列，5×26dw+2×25dw 方案使 7 列累积漂移 ≤ ±0.2 格

## 竞赛背景

- 赛事：全国大学生集成电路创新创业大赛 - "胜达克"企业命题
- 赛题：存储类芯片自动化测试系统设计与开发（A组）
- DUT：AT24C02 I2C EEPROM
- 测试设备：AdaptStar-E (EStar) ATE测试系统
- 初赛提交物：PPT文档 + PAT生成工具(.exe) + .pat文件 + .txt预览文件 + ATE工程文件包
