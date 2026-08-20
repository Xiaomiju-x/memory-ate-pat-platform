# 公开源码完整性与演进记录

本文件说明全国总决赛 PAT 平台 `1.0.9` 的公开源码边界、性能改造和可复现验证方式。当前可维护业务源码是 [`renderer/index.html`](renderer/index.html)，Electron 桌面与文件后端位于 `main.js`、`preload.js`、`save-file.js` 和 `large-pat-store.js`。

## 公开与私有基线的边界

- 仓库公开完整的当前实现、构建配置、锁定依赖、团队测试和第三方许可；
- 团队开发过程中使用过的历史 HTML 快照和内部兼容性资料继续保留在本地授权环境，不进入 Git、CI、构建或 Release；
- 赛方/企业参考 PAT、厂商资料及其原文件名、路径和哈希不属于公开复现输入；
- 公开测试直接断言器件 profile、命令、地址、总线宽度、状态轮询、行数、取消、保存和安全边界；
- 团队自生成的公开回归输出可以使用 SHA-256 保护，但不会被描述为第三方“黄金文件”。

这一区分不会影响完整开源：运行和修改 `1.0.9` 所需的全部当前源码都在 `national-final/`；被排除的是私有历史验收输入，不是应用实现。

## 版本演进

- `1.0.1`：加入协作式生成、进度、取消和分段预览；
- `1.0.2`：取消固定 2,000,000 行拒绝上限，加入磁盘流式生成、读取、替换和保存；
- `1.0.3–1.0.4`：修正固定 SPI Flash 的 SDI VOL、Dual MEMORY/FUNC 和 MX Quad/SQI 协议分类；
- `1.0.5`：接入固定/自定义 SRAM 与 I²C EEPROM，并复用异步和流式框架；
- `1.0.6`：PAT 只由两个显式生成按钮更新，配置/视图切换保留上一份成功结果；
- `1.0.7`：补齐固定器件 SDI VOL 与 FUNC 擦除/编程后的 WIP 状态轮询；
- `1.0.8`：接入固定 25LC256 和自定义 SPI EEPROM，按物理页拆分 WRITE；
- `1.0.9`：为固定 23LC1024、24LC02B、25LC256 增加 100,000 行专用流式切换点，并让不可压缩写模板持续让出 UI。

## 受控性能改造

相对于早期同步页面实现，当前 renderer 和 Electron 后端包含以下公开、可审查的变化：

1. CSP 删除远程域、`unsafe-eval` 与 `wasm-unsafe-eval`，所有浏览器依赖改为本地锁定资源；
2. 逐 Byte、Page、Phase 和校验循环采用串行 `async/await` 检查点，保持 PAT 行顺序；
3. 超过 12,000 行时只显示 5,000 行窗口，完整内容仍可保存；
4. Flash/自定义路径预计超过 2,000,000 行、固定串行存储器预计超过 100,000 行时，从首行进入主进程临时文件；
5. 实际行数超过预估时，内存结果在检查点无损迁移到流式路径；
6. 流式结果使用随机 token、字段白名单、块大小和读写范围限制；
7. 整列替换处理完整 PAT，失败时保留旧结果；
8. 取消、替换失败、主动丢弃和应用退出都会清理临时文件；
9. 成功弹窗只在用户主动生成并完整成功后显示；
10. MEMORY/FUNC、器件、总线、模式和地址变化不会在后台替换上一份 PAT。

## 公开协议契约

公开测试覆盖：

- 固定 SPI Flash 的 A 类 `A2h+3Bh`、B 类 `02h+3Bh`、MX 类 `02h+BBh` Dual 行为；
- MX25U4033E/MX25U4033EM 的 QE、`38h` 4PP 与 `EBh` 4READ；
- 七款固定器件 SDI VOL 的单线 Page Program 与双线回读；
- FUNC Sector Erase/Page Program 后的 `05h`、`LOOP MATCH`、WIP=0；
- 23LC1024 的 SPI/SDI/SQI、模式 1/2 和受限 GALPAT；
- 24LC02B 的页写、当前地址读、随机读、顺序读和 ACK/NACK；
- 25LC256 的 `06h → 02h → 05h → 03h`、16-bit 线上地址、物理页拆分和无 NOR Flash `20h`；
- 自定义器件的地址宽度、页边界、事务配置和结构说明；
- 普通/超大 PAT 的预览、校验、替换、保存、取消和回滚。

## 安全与许可证完整性

- `nodeIntegration: false`、`contextIsolation: true`、`sandbox: true`、`devTools: false`；
- session 层拒绝外部网络、权限、下载、新窗口、WebView 和外部导航；
- preload 只暴露保存与大 PAT 流式 API；
- `package.json` 和便携包元数据使用 `Apache-2.0`；
- Floating UI 与 Lucide 的完整许可文本位于 [`licenses/`](licenses/) 并随便携包分发；
- 根项目 Apache-2.0 文本作为构建资源随便携包分发；
- `.gitignore` 排除内部历史快照、`node_modules/`、`work/`、`dist/` 和旧压缩包。

## 验证命令

```powershell
npm ci
npm test
npm run portable
```

测试失败时不得继续发布。`npm test` 验证当前公开源码，不需要任何私有资料。

## 设备级边界

公开测试覆盖软件结构、协议契约和生成/保存链路，不等价于 AdaptStar-E 或其他目标 ATE 的认证。在连接真实设备前，仍需在合法授权环境复核 HEAD、Pin Map、状态符号、时序、电平、LOOP、写等待、负载板和限流/断电安全序列。
