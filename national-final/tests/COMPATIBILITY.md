# 公开兼容性测试

公开测试直接验证当前 `renderer/index.html`、Electron 主进程和文件保存/流式后端，不依赖或分发内部历史 PAT、厂商资料、原文件名、路径或哈希。

## 公开回归层级

- `project-integrity.test.js`：固定器件 profile、底层 PAT 原语、显式生成按钮、协议分类、超大文件策略、离线资源和 Electron 安全配置；
- `large-pat-store.test.js`：随机 token、字段白名单、UTF-8/CRLF、窗口读取、替换、取消与临时文件生命周期；
- `save-file.test.js`：原生保存、后缀、路径清理、取消和中文路径；
- `publication-boundary.test.js`：Apache-2.0/第三方许可构建输入，以及内部资料标识不得回流公开 renderer；
- `electron-smoke.js`：真实 Electron renderer 中的器件/总线/模式切换、PAT 生成、校验、保存、超大流式输出和取消回滚。

## 兼容性原则

1. 公开协议契约、器件 profile、命令/地址/数据宽度和状态轮询必须由可读断言保护；
2. 团队自生成的固定配置可以使用行数、字符数和 SHA-256 作为回归值，但不得把它们描述为赛方或企业黄金文件；
3. 公开测试输入必须由仓库代码生成或由团队独立构造；
4. 任何内部参考资料只可在合法授权的离线环境中核验，不属于公开安装、CI、构建或复现步骤；
5. 修改器件语义时，应同时更新公开测试、变更记录和设备验证边界，不能只覆盖断言以让测试通过。

运行：

```powershell
npm ci
npm test
```
