# 快速开始 / Quickstart

本页给出从源码运行、批量生成、回归测试和 Windows 打包的最短路径。命令默认在仓库根目录执行，并使用 PowerShell 语法。

## 1. 准备环境

推荐环境：

- Windows 10 / 11；
- Python 3.10+；
- 可用的 `tkinter`（python.org 的 Windows 安装包通常包含）；
- Git。

克隆并创建隔离环境：

```powershell
git clone https://github.com/Xiaomiju-x/memory-ate-pat-platform.git
cd memory-ate-pat-platform

py -3.10 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

如果 PowerShell 策略不允许激活虚拟环境，可以不修改系统策略，直接使用：

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe at24c02_pat_generator.py --help
```

确认两个入口都能解析参数：

```powershell
python at24c02_pat_generator.py --help
python "regional-final\by25q40al\by25q40al_pat_generator.py" --help
```

### 可选 DeepSeek 诊断

主平台包含可选 AI 诊断面板。不开启该功能时无需 API Key，也不会因为普通 PAT 生成而调用模型接口。需要使用时，只在当前进程设置 DeepSeek 专用凭据：

```powershell
$env:DEEPSEEK_API_KEY = "在本机输入，不要写入源码或提交到 Git"
python at24c02_pat_generator.py
```

该面板将对话上下文发送到 `https://api.deepseek.com`。不要输入赛方私有 PAT、企业资料、账号、个人信息或其他无权发送给第三方的内容；使用后可运行 `Remove-Item Env:DEEPSEEK_API_KEY` 清除当前会话变量。

## 2. 运行初赛 / 通用平台

### GUI

```powershell
python at24c02_pat_generator.py
```

建议第一次使用按以下顺序操作：

1. 选择器件预设与协议；AT24C02 对应 I2C；
2. 确认地址引脚、WP、电压、向量周期和 Site 数；
3. 选择测试项并设置地址范围；
4. 生成后先查看 PAT、TXT、波形、统计和检查结果；
5. 通过导出对话框选择 PAT / STIL / WGL，并指定一个新的输出目录；
6. 在真实机台导入前，再检查 `.prg/.tim/.lvl` 与目标工程的语法和通道映射。

GUI 支持 `Ctrl+G` 生成、`Ctrl+E` 导出、`Ctrl+F` 搜索。

### CLI 批处理

生成 AT24C02 全部 CLI 测试段，并导出 PAT、STIL、WGL 及配套工程文件：

```powershell
python at24c02_pat_generator.py `
  --batch `
  --chip AT24C02 `
  --protocol I2C `
  --tests all `
  --voltage 5.0V `
  --period 2500 `
  --sites 1 `
  --format all `
  --output output_cli
```

常用参数：

| 参数 | 取值 / 示例 | 说明 |
|---|---|---|
| `--chip` | `AT24C02`, `W25Q32JV`, `93C46` | 必须是源码中的器件预设名 |
| `--protocol` | `I2C`, `SPI`, `Microwire` | 应与器件预设匹配 |
| `--tests` | `all` 或逗号分隔 | `os,dc,func,march,march_b,scan,ret,err,endur` |
| `--format` | `pat`, `stil`, `wgl`, `all` | PAT 模式同时生成 TXT、TIM、LVL、PRG |
| `--voltage` | `1.8V`, `2.5V`, `3.3V`, `5.0V` | 电平与时序预设 |
| `--period` | `2500` | 向量周期，单位 ns |
| `--simulate` | 开关 | 生成后运行软件模拟器 |
| `--config` | JSON 路径 | 当前批处理入口读取协议、电压和周期覆盖项 |

I2C 每 bit 使用 4 条向量，所以 `--period` 指定的是向量周期 `Tvec`，实际
`fSCL = 1 / (4 × Tvec)`。上例的 `2500ns` 对应 `100kHz` I2C 时钟。

示例：只生成 AT24C02 功能、March C- 和地址扫描，并运行模拟器：

```powershell
python at24c02_pat_generator.py `
  --batch --chip AT24C02 --protocol I2C `
  --tests func,march,scan --format pat --simulate `
  --output output_smoke
```

> 当前 CLI 的 `all` 对应 9 个主测试标识，不包含独立 IDDQ 标识。IDDQ 生成逻辑存在于主平台中；不同 GUI 模式和测试阶段可能将它作为 DC 子项或独立段。以实际导出的段名为准，不要只依赖宣传性计数。

### 生成仓库示例

```powershell
python generate_samples.py
```

脚本会更新 `output/` 下的 AT24C02 示例包。它目前固定生成 9 类主测试，其中功能测试拆为多个子段；它不是 GUI 全部分析功能的无头镜像。

## 3. 运行复赛 BY25Q40AL 专用平台

该入口只依赖 Python 标准库和 `tkinter`，定位是复赛 PAT 生成，不替代根目录的通用平台。

启动 GUI：

```powershell
python "regional-final\by25q40al\by25q40al_pat_generator.py"
```

生成 Standard SPI Checkerboard，比较范围为 `000000h~0001FFh`：

```powershell
python "regional-final\by25q40al\by25q40al_pat_generator.py" `
  --batch --mode mode_2 --bus SPI `
  --start 000000h --end 0001FFh `
  --output semifinal_output
```

模式参数：

| 参数 | 含义 |
|---|---|
| `mode_1` | 全 0 |
| `mode_2` | Checkerboard |
| `mode_3` | Walking One |
| `mode_4` | Walking 0 |
| `mode_5` | Sliding Diagonal |
| `mode_6` | GALPAT 乒乓 |

总线参数为 `SPI`、`DUAL` 或 `QUAD`。芯片合法地址范围是 `0x000000~0x07FFFF`；程序会把页写范围向外对齐到 256 Byte 页，而读比较范围保持用户输入。

校验已有 PAT：

```powershell
python "regional-final\by25q40al\by25q40al_pat_generator.py" `
  --validate "semifinal_output\STANDARD_MEMORY_PROGRAM_READ.pat"
```

更多竞赛专用规则见[复赛软件使用说明](../regional-final/by25q40al/README.md)。

## 4. 运行测试

根平台测试：

```powershell
python -m unittest discover -s tests -v
```

根测试覆盖 I2C START/STOP、四向量写 bit、ACK 释放与比较、协议违规检测、PAT/TIM/LVL/PRG 结构、推荐时序、CLI 子进程和临时目录示例生成。测试不会改写仓库的 `output/`。

复赛公开回归需要从专用目录执行，以便模块导入路径与打包脚本一致：

```powershell
Push-Location "regional-final\by25q40al"
python -m unittest discover -s tests -v
Pop-Location
```

回归失败时不要继续构建或发布 EXE。公开测试检查团队生成器、事务结构、地址边界、总线映射和打包配置，不附带或读取赛方原始黄金 PAT、FUNC 参考模板等第三方资产。

### 第三方资料不属于公开复现输入

公开生成器、测试与构建不需要赛方黄金 PAT、FUNC 模板或其他第三方赛事资料。合法持有相关资料者只能在授权范围内自行离线核验；本项目不接收、不定位、不自动读取或提供相关资产，也不提供其哈希、复制或对比工具。私有核验不属于公开复现步骤。不要向维护者提交资产正文、路径、哈希或可用于还原资产的信息。

## 5. Windows 打包

先安装构建依赖：

```powershell
python -m pip install -r requirements.txt -r requirements-dev.txt
```

构建工具版本由 `requirements-dev.txt` 锁定。主平台推荐直接运行构建脚本；它会先安装锁定依赖、执行回归测试，再使用已包含 CustomTkinter 收集规则的 spec：

```powershell
.\build_exe.bat
```

当前 spec、EXE 文件名与源码版本统一为 `v8.0.0`。

复赛工具使用带回归前置检查的脚本：

```powershell
Push-Location "regional-final\by25q40al"
.\build_exe.bat
Pop-Location
```

构建产物位于对应目录的 `dist/`。可执行文件是派生物；发布时应同时提供源码版本、测试状态和 SHA-256，而不是只提交 EXE。

## 6. 复现与输出检查

每次准备交付时至少记录：

- Git commit；
- Python 版本与依赖版本；
- 器件、协议、电压、周期、Site、地址范围、测试选择；
- 导出格式和输出清单；
- 回归测试结果；
- PAT/TIM/LVL/PRG 的校验结果；
- 待真机确认项。

主平台文件可能包含生成时间，因此同一配置的整个文件未必逐字节相同；应同时比较配置、段数、向量数和事务语义。复赛公开版的固定范围与自定义范围都走团队参数化生成器；内部获授权语料对比不是公开复现要求。

## 7. 常见启动问题

| 现象 | 检查项 |
|---|---|
| `No module named customtkinter` | 执行 `python -m pip install -r requirements.txt`，并确认运行的是同一个 Python |
| `No module named tkinter` | 安装带 Tcl/Tk 的 Python；Linux 需安装发行版对应的 Tk 包，但 GUI 主要在 Windows 验证 |
| PowerShell 无法激活虚拟环境 | 直接调用 `.venv\Scripts\python.exe`，无需放宽全局策略 |
| GUI 可启动但字体/缩放异常 | 检查 Windows DPI 和系统字体；先用默认缩放复现 |
| PAT 被目标 ATE 拒绝 | 先看[格式说明](formats.md)，再按目标设备的授权格式文档校准 |
| EXE 被安全软件提示 | 从源码自行构建并核对 SHA-256；不要把“误报”当作默认结论 |

仍未解决时，请按 [CONTRIBUTING.md](../CONTRIBUTING.md) 的 Issue 模板提供最小复现信息。
