# 路线图 / Roadmap

路线图区分“已经在仓库中实现”“正在做”“希望做”。它不是交付日期承诺，也不会用规划项抬高当前功能口径。

## 状态定义

- **已完成**：源码和公开入口存在，并有相应样例或测试依据；
- **持续改进**：基本能力存在，但测试、模块化、设备验证或文档仍可增强；
- **候选**：欢迎讨论，尚未承诺实现。

## 竞赛阶段

| 方向 | 状态 | 可检查依据 |
|---|---|---|
| AT24C02 初赛完整测试平台 | 已完成 / 持续改进 | 根主程序、CLI、示例输出、格式化与分析类 |
| BY25Q40AL 复赛竞赛优化平台 | 已完成 | 独立入口、参数化生成器、验证器、公开测试与说明 |
| 西南赛区奖项材料 | 已公开 | 已获授权；展示图遮蔽二维码与证书编号 |
| 全国总决赛一等奖与纪念材料 | 已公开 | 全国总决赛一等奖证书、颁奖现场与团队参赛照片；证书敏感标识已遮蔽，人物形象已获同意公开，隐藏元数据已移除 |
| 全国总决赛 PAT 软件 | **已公开 / 持续验证** | [`national-final/`](../national-final/README.md) v1.0.9 源码、测试、构建工程与 Windows Release |

## 全国总决赛平台状态

`v1.0.9` 已达到公开软件基线：源码、锁定依赖、单元/完整性测试、Electron 交互测试、公开协议回归、Windows 构建脚本、第三方许可和 SHA-256 发布信息均已进入公开交付链。全国总决赛已完赛，参赛团队获得全国总决赛一等奖；软件发布与赛事奖项仍是两个独立事实。

仍需持续完成或增强：

- [x] 固定/自定义 SPI Flash、SRAM、I²C EEPROM、SPI EEPROM 的生成入口与参数约束；
- [x] MEMORY / FUNC、SPI / SDI / SQI 和关键数据模式的公开协议回归；
- [x] 普通与超大 PAT 的生成、取消、预览、替换、校验和保存链路；
- [x] Electron 最小权限、离线资源与网络阻断；
- [x] Windows x64 portable 构建、版本元数据、Release 和 SHA-256；
- [x] 密钥、隐私、本机路径、第三方许可与公开资产边界审计；
- [ ] 使用商业代码签名证书签名 Windows EXE；
- [ ] 在第二台干净 Windows 电脑复核便携版首次启动；
- [ ] 在合法授权环境完成目标 ATE 离线导入、Pin Map、电平、时序与 LOOP 语法签核；
- [ ] 在受控硬件条件下记录真实 DUT/负载板验证证据；
- [x] 依据团队获奖材料更新全国总决赛一等奖状态与现场纪念照片。

## 开源工程改进

### 近期：建立可信基线

- [x] 重写公开 README，区分初赛、复赛和决赛状态；
- [x] 建立架构、快速开始、竞赛、格式、路线图和 FAQ 文档；
- [x] 将复赛第三方资产与公开代码隔离，公开版保留团队语义回归；
- [x] 在 CI 中执行根平台导入 / 生成冒烟测试和复赛回归；
- [x] 为发布包生成可审计清单、版本说明与哈希；
- [x] 从 Git 候选集排除历史构建物、重复压缩包和本机缓存；
- [x] 为所有公开第三方材料记录来源、许可证或移除原因。

### 中期：降低单文件耦合

目标模块边界：

```text
src/
├─ domain/       vectors, pins, segments, device profiles
├─ protocols/    I2C, SPI, Microwire emitters
├─ testspec/     functional, March, retention, error, endurance
├─ formats/      PAT, STIL, WGL, PRG, TIM, LVL
├─ validators/   syntax, timing, protocol, cross-file
├─ analysis/     simulation, ATPG, yield, STDF
├─ cli/          stable headless interface
└─ gui/          presentation and interaction only
```

拆分原则：

- 先用快照 / 语义测试固定现有输出；
- 一次迁移一条数据流，不同时重写协议与界面；
- 领域对象不依赖 Tk 变量；
- formatter 不读取 GUI 状态；
- 器件参数逐步迁移到带来源信息的 profile；
- 保持旧 CLI / 配置兼容，破坏性修改走主版本升级。

### 中期：增强可验证性

- 为 START/STOP、ACK/NACK、读写 bit 和地址边界增加单元测试；
- 为 PAT/TIM/LVL/PRG 增加跨文件引用测试；
- 建立小型、可审查、由团队代码自生成的语义快照，避免依赖超大输出做全部断言；
- 区分语法验证、协议验证、设备导入验证和硅验证结果；
- 为 STIL / WGL / STDF 声明当前支持子集并增加 round-trip 测试；
- 给随机模拟统一 seed、分布和单位元数据。

### 候选：生态与研究

- 新器件 profile 贡献规范和校验 schema；
- 面向公开格式的插件式 formatter / validator；
- 生成器核心的 Python package 与稳定 API；
- 可重复的 ATE 离线导入报告模板；
- 测试算法覆盖证明与器件故障模型数据集；
- 文档英文版和可检索 API 参考。

## 不在默认承诺中的事项

- 对所有 AdaptStar-E 版本零修改导入；
- 对任何真实 DUT 的无风险执行保证；
- 用模拟数据替代量产相关性或硅验证；
- 未经授权公开赛方资料、厂商私有格式或第三方文档；
- 在没有测试和来源依据时快速堆叠器件型号。

如果你希望推动路线图中的一项，请先阅读 [CONTRIBUTING.md](../CONTRIBUTING.md)，在 Issue 中说明使用场景、最小输入、期望输出和可执行验收标准。
