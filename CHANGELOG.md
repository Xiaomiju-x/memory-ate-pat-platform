# Changelog

本文件记录 Memory ATE PAT Platform 面向公开使用者的重要变更。版本号遵循
[Semantic Versioning](https://semver.org/)，条目结构参考
[Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)。

## [Unreleased]

### Changed

- 公开全国总决赛一等奖证书的隐私处理版本，遮蔽二维码与证书编号并移除隐藏元数据。
- 更新全国总决赛一等奖（全国一等奖）结果，并公开三张已获人物授权、已移除隐藏元数据的参赛纪念照片。

### Fixed

- 统一更正奖项表述为“西南赛区一等奖”，删除此前不准确的名次性表述及其英文对应内容。

## [national-final-v1.0.9] - 2026-08-20

全国总决赛软件组件独立版本；不改变根 Python 平台的 `8.0.0` 版本号。

### Added

- 完整开源 `national-final/` Electron 离线桌面工程、锁定依赖、构建脚本与公开测试。
- 固定/自定义 SPI Flash、23LC1024 SRAM、24LC02B I²C EEPROM、25LC256 SPI EEPROM 的 MEMORY/FUNC PAT 生成路径。
- SPI / SDI / SQI、多种数据模式、地址范围、自定义事务、普通 PAT 编辑与六列批量替换。
- 超大 PAT 的协作式生成、取消、磁盘流式存储、5,000 行窗口预览、流式校验与原生保存。
- Electron sandbox、context isolation、最小 preload API、IPC sender/字段校验、离线 CSP 和网络阻断。
- Windows + Node.js 22.12 CI，19 项 Node 单元/完整性测试及 31 项 Electron 交互/生成回归。
- Apache-2.0 项目许可、Floating UI/Lucide 完整第三方许可文本与便携包分发配置。
- GitHub Release 中的 Windows 10/11 x64 portable EXE 与 `SHA256SUMS.txt`。

### Security

- EXE 不要求管理员权限，不创建服务或安装项；renderer 无 Node.js/文件系统/进程执行权限。
- 公开源码、构建和测试不附带内部参考 PAT、厂商资料、密钥、本机路径或其文件名/哈希。

### Known limitations

- Windows EXE 尚未使用商业代码签名证书，SmartScreen 可能显示“未知发布者”。
- 仍需在第二台干净 Windows 电脑和目标 ATE/真实 DUT 环境完成独立验证。
- 生成成功与公开测试通过不构成主办方、芯片厂商或 ATE 厂商认证。

## [8.0.0] - 2026-08-13

首次公开源码基线。

### Added

- AT24C02 初赛 / 通用平台：GUI、无界面批处理、I2C 测试向量生成、ATE 工程文件导出、
  波形与流程展示、仿真和测试数据分析能力。
- BY25Q40AL 复赛公开版：Standard、Dual、Quad SPI，六类 Memory 数据模式、GUI / CLI、
  PAT 校验与团队自生成的公开回归测试。
- Windows 可复现构建脚本、固定 PyInstaller 构建依赖，以及 Python 3.10 / 3.12、
  Windows / Linux 的 GitHub Actions 测试矩阵。
- 中英文首页、架构、格式、快速开始、竞赛历程、知识产权边界、路线图和 FAQ 文档。
- Apache-2.0 许可证、贡献指南、行为准则、安全策略、支持说明、Issue / PR 模板、
  Dependabot 和 Gitleaks 扫描。

### Changed

- 可选 DeepSeek 接口凭据仅从 `DEEPSEEK_API_KEY` 环境变量读取；公开源码和示例配置不含真实密钥。
- 复赛公开版不读取、不复制、不对比，也不附带赛方或企业提供的黄金 PAT、FUNC 模板、
  私有规范、培训材料或其他受限资产。
- HTML 统计报告统一引用主程序的 `VERSION` 常量，避免报告与应用显示不同版本。
- PRG 中文日期不再把非 ASCII 字符交给 Windows C locale 的 `strftime`，兼容 Python 3.10 英文区域设置。

### Known limitations

- AdaptStar-E / EStar 私有语法需要使用者依据其合法获得的目标设备文档和真机环境复核；
  仓库测试不等同于厂商认证或量产验证。
- 主平台源码、PyInstaller spec 和公开构建的 EXE 文件名统一为 `v8.0.0`；
  早期生成物中的版本标识仅作为历史工程快照保留。
- 仓库中的历史生成样例用于展示演进，不应被误认为全部由当前版本产生的正式 Release 资产。

> 说明：公开 Git 历史从此基线开始。仓库内早期样例中出现的 v1 / v6 标识是工程快照，
> 不是本公开仓库的独立发行版本。
