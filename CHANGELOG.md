# Changelog

本文件记录 Memory ATE PAT Platform 面向公开使用者的重要变更。版本号遵循
[Semantic Versioning](https://semver.org/)，条目结构参考
[Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)。

## [Unreleased]

### Planned

- 全国总决赛 PAT 向量生成与测试软件仍在开发和验证；当前只保留
  [`national-final/`](national-final/) 入口，不把计划功能描述为已经完成。

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
