# 贡献指南 / Contributing Guide

感谢你帮助完善存储芯片 ATE PAT 测试工具。我们欢迎协议实现、测试算法、格式兼容、可复现样例、文档、翻译和缺陷修复。

## 开始之前

- 先搜索现有 Issue 和 Pull Request；较大功能请先提出设计 Issue。
- 安全漏洞、凭据泄漏和未授权资料请按 [SECURITY.md](SECURITY.md) 私密报告。
- 只提交你有权以 Apache-2.0 许可证公开的内容。提交贡献即表示该贡献适用仓库的 Apache-2.0 许可证（除非双方另有书面约定）。
- 不接受未经授权的赛方/企业资料、题目附件、培训材料、厂商模板、ATE 私有文档、芯片手册或从中直接复制的 PAT。可引用公开来源，或提交有清晰来源记录的 clean-room 实现。
- 不要提交真实 API Key、账户、个人信息、证书原图、内部路径、构建缓存、EXE 或交付 ZIP。

## 本地开发

要求 Python 3.10+；根平台 GUI 依赖 `customtkinter`，复赛公开版只使用标准库与 `tkinter`。

```powershell
git clone <your-fork-url>
cd <repository>
python -m pip install -r requirements.txt
python -m compileall -q at24c02_pat_generator.py generate_samples.py waveform_html.py flowchart_template.py
python -m unittest discover -s tests -v
Push-Location regional-final\by25q40al
python -m unittest discover -s tests -v
Pop-Location
```

如果启用可选 DeepSeek 功能，请在当前 shell 设置 `DEEPSEEK_API_KEY`；不要把真实值写入源码或 `.env.example`，也不要复用其他服务商签发的密钥。

复赛公开版的专用约束和测试命令见其[独立说明](regional-final/by25q40al/README.md)。提交前请运行所有与你的改动相关的测试；不能运行真实 ATE 验证时，请在 PR 中明确说明验证边界。

## 代码约定

- 使用 UTF-8；Python、Markdown 和配置文件使用 LF，Windows 批处理及 ATE 交换文件使用 CRLF。
- 保持 `TEST_PINS = ["A0", "A1", "A2", "WP", "SCL", "SDA"]` 的既定顺序，除非变更同时包含迁移说明和测试。
- I18N 可见文本通过翻译字典接入，不在控件中新增只支持单一语言的硬编码文本。
- tkinter 的布局参数（例如 tuple 形式的 `pady`）放在 `.pack()` / `.grid()` 调用中。
- 优先小而聚焦的改动；不要在功能修复中顺带格式化整个大型主文件。
- 新协议、算法或导出格式应包含最小可复现样例、边界条件和失败行为说明。

## PAT 变更检查表

修改向量生成或格式化逻辑时，至少核对：

- `HEAD[PIN_NAME]`、`@@PATTERN_DEFINE`、`start:`、`end:` 和 `@@END_PATTERN_DEFINE` 完整配对；
- 首向量带 `AC_SET 1;`，PRG 引用的文件名与标签存在；
- I2C 位序为 MSB first，每 bit 的四相位 setup/sample/hold/end 未被破坏；
- 从机 ACK 在采样相位期望 `L`，读数据非采样相位使用 `X`；
- START/Repeated START/STOP、WP、地址脚和多 Site 行为有覆盖；
- 新生成文件可重复生成，且没有时间戳等无意义差异（确需时间戳时说明原因）；
- 大体积输出只保留一个有评审价值的 canonical 样例，其余由脚本生成。

## 提交与 Pull Request

提交信息建议采用清晰的祈使句；可使用 `fix:`、`feat:`、`docs:`、`test:`、`refactor:` 等前缀。一个 PR 尽量只解决一个主题。

PR 描述应包括：

- 问题、方案和明确的不做事项；
- 受影响的协议、测试段、芯片、输出格式和平台；
- 实际执行的测试命令与结果；
- PAT/预览输出的摘要差异，避免粘贴数万行；
- GUI 改动的截图（先清除个人信息和本地路径）；
- ATE 实机验证状态和已知限制；
- 新增素材、算法或样例的来源与再分发依据。

维护者可能要求拆分过大的 PR、补充测试、重新生成样例或移除来源不清的文件。合并前所有评审意见和 CI 检查应解决。

## 报告缺陷

优先使用仓库 Issue 表单。请提供版本/提交、系统与 Python 版本、芯片和协议、最小配置、预期与实际行为、最小复现，以及经过脱敏的错误信息。不要上传完整的保密 ATE 工程、STDF 生产数据或真实凭据。

## 许可证与署名

除非文件另有明确说明，原创贡献按 [Apache-2.0](LICENSE) 授权。第三方商标、标准、数据手册、竞赛资料和厂商内容不因被提及而获得再许可；详见 [NOTICE](NOTICE)。
