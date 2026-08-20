'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');

const projectRoot = path.resolve(__dirname, '..');
const rendererPath = path.join(projectRoot, 'renderer', 'index.html');

function read(relativePath) {
  return fs.readFileSync(path.join(projectRoot, relativePath), 'utf8');
}

function functionSource(source, name) {
  const marker = `function ${name}(`;
  const start = source.indexOf(marker);
  assert.notEqual(start, -1, `缺少函数：${name}`);
  const bodyStart = source.indexOf('{', start);
  let depth = 0;
  for (let index = bodyStart; index < source.length; index += 1) {
    if (source[index] === '{') depth += 1;
    if (source[index] === '}') depth -= 1;
    if (depth === 0) return source.slice(start, index + 1).replace(/\r\n/g, '\n');
  }
  throw new Error(`函数未闭合：${name}`);
}

function profileSource(source, name) {
  const escaped = name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const match = new RegExp(`^\\s*(?:['"]${escaped}['"]|${escaped}):\\s*\\{`, 'm').exec(source);
  const start = match ? match.index : -1;
  assert.notEqual(start, -1, `缺少固定芯片 Profile：${name}`);
  const bodyStart = source.indexOf('{', start);
  let depth = 0;
  for (let index = bodyStart; index < source.length; index += 1) {
    if (source[index] === '{') depth += 1;
    if (source[index] === '}') depth -= 1;
    if (depth === 0) return source.slice(start, index + 1);
  }
  throw new Error(`固定芯片 Profile 未闭合：${name}`);
}

test('public renderer contains the low-level PAT primitives and serial-memory profiles', () => {
  const renderer = fs.readFileSync(rendererPath, 'utf8');

  for (const name of ['patHex', 'patBits', 'patVector', 'patDataGroups', 'patDataVector', 'patDataTemplate']) {
    assert.doesNotThrow(() => functionSource(renderer, name), `渲染器必须包含 ${name}`);
  }

  const sram = profileSource(renderer, '23LC1024');
  assert.match(sram, /\bkind:\s*['"]sram['"]/);
  assert.match(sram, /\bwidth:\s*24\b/);
  assert.match(sram, /\beffectiveWidth:\s*17\b/);
  assert.match(sram, /\bcapacityBytes:\s*0x20000\b/i);
  assert.match(sram, /\breadOpcode:\s*0x03\b/i);
  assert.match(sram, /\bwriteOpcode:\s*0x02\b/i);
  assert.match(sram, /\bsdiOpcode:\s*0x3B\b/i);
  assert.match(sram, /\bsqiOpcode:\s*0x38\b/i);
  assert.match(sram, /\bexitOpcode:\s*0xFF\b/i);
  assert.match(sram, /\bdummyBytes:\s*1\b/);

  const eeprom = profileSource(renderer, '24LC02B');
  assert.match(eeprom, /\bkind:\s*['"]eeprom['"]/);
  assert.match(eeprom, /\bwidth:\s*8\b/);
  assert.match(eeprom, /\bpage:\s*8\b/);
  assert.match(eeprom, /\bcapacityBytes:\s*0x100\b/i);
  assert.match(eeprom, /\bwriteControl:\s*0xA0\b/i);
  assert.match(eeprom, /\breadControl:\s*0xA1\b/i);
  assert.match(eeprom, /\bwriteWaitLoop:\s*6250\b/);

  for (const name of [
    'configureTxEditorFamily',
    'defaultSramTxConfig',
    'findTxBeginLineIndex',
    'locateCurrentTxInPreview',
    'patBuildCustomSramTx',
    'patBuildSram',
    'patBuildEeprom'
  ]) {
    assert.doesNotThrow(() => functionSource(renderer, name), `渲染器必须集成 ${name}`);
  }
  for (const id of [
    'pat-eeprom-operation',
    'pat-eeprom-write-control',
    'pat-eeprom-read-control',
    'pat-eeprom-wait-loop',
    'pat-sram-custom-fields',
    'pat-eeprom-custom-fields',
    'pat-tx-locate',
    'pat-mode2-tx-locate'
  ]) {
    assert.match(renderer, new RegExp(`id=["']${id}["']`), `${id} 必须存在`);
  }

  assert.match(renderer, /const PAT_GENERATOR_VERSION = ['"]DEVICE_CLASSIFIED_ICC_9CHIPS_R16['"];/, 'SPI Flash PAT 版本标识必须保持稳定');
  assert.match(renderer, /async function patBuildMemory\(job\)/, '器件必须接入异步生成框架');
  assert.match(renderer, /deviceModel\.value === ['"]CUSTOM_SRAM['"]/);
  assert.match(renderer, /deviceModel\.value === ['"]CUSTOM_EEPROM['"]/);
});

test('PAT preview generation is exclusively bound to the two explicit generation buttons', () => {
  const renderer = fs.readFileSync(rendererPath, 'utf8');
  const memoryCalls = renderer.match(/\bgeneratePreview\s*\(/g) || [];
  const funcCalls = renderer.match(/\bgenerateFuncPreview\s*\(/g) || [];

  assert.equal(memoryCalls.length, 2, 'generatePreview 只能出现于函数定义和 MEMORY 生成按钮绑定');
  assert.equal(funcCalls.length, 2, 'generateFuncPreview 只能出现于函数定义和 FUNC 生成按钮绑定');
  assert.match(renderer, /root\.querySelector\('#pat-generate'\)\.addEventListener\('click', \(\) => generatePreview\(true\)\);/);
  assert.match(renderer, /root\.querySelector\('#pat-func-generate'\)\.addEventListener\('click', \(\) => generateFuncPreview\(true\)\);/);
  assert.doesNotMatch(renderer, /\bscheduleAddressPreview\b/, '不得保留地址变化自动生成入口');
  assert.doesNotMatch(renderer, /\bscheduleFuncPreview\b/, '不得保留 FUNC 配置自动生成入口');
  assert.doesNotMatch(renderer, /\bgeneratePreview\s*\(\s*\)/, '不得静默生成 MEMORY PAT');
  assert.doesNotMatch(renderer, /\bgenerateFuncPreview\s*\(\s*\)/, '不得静默生成 FUNC PAT');

  const switchView = functionSource(renderer, 'switchView');
  assert.doesNotMatch(switchView, /lastPreview\s*=/, '切换 MEMORY/FUNC 视图不得清空上一份 PAT');
  assert.doesNotMatch(switchView, /lastPreviewStream\s*=/, '切换 MEMORY/FUNC 视图不得丢弃上一份流式 PAT');
  assert.doesNotMatch(switchView, /discardLargePatToken/, '切换视图不得删除上一份流式 PAT');

  const switchFuncPanel = functionSource(renderer, 'switchFuncPanel');
  assert.doesNotMatch(switchFuncPanel, /generate(?:Func)?Preview/, '切换 FUNC 类别只能更新界面，不得生成 PAT');
  assert.match(switchFuncPanel, /updateFuncReadWriteSummary\(\)/, 'FUNC 类别切换仍须保留纯 UI 摘要更新');
  assert.match(renderer, /eepromOperation\.addEventListener\('change', updateAddress\);/, 'EEPROM 操作变化只能更新地址摘要');
  assert.match(renderer, /addEventListener\('input', updateFuncReadWriteSummary\)/, 'FUNC 输入仍须保留纯 UI 摘要更新');
  assert.match(renderer, /\[start, end, pageSize, sectorSize, addressWidth\][\s\S]*?updateAddress\(\);[\s\S]*?\}\);/, 'MEMORY 地址配置仍须保留纯 UI 地址更新');

  const flushPendingPreviewEdit = functionSource(renderer, 'flushPendingPreviewEdit');
  assert.match(flushPendingPreviewEdit, /clearTimeout\(previewEditTimer\)/, '切换标签前必须取消待执行的编辑防抖');
  assert.match(flushPendingPreviewEdit, /lastPreview\s*=\s*getPreviewText\(\)/, '切换标签前必须同步保存小文件手工编辑');
  assert.match(renderer, /\.pat-tab[\s\S]*?flushPendingPreviewEdit\(\);\s*activeTab\s*=\s*tab\.dataset\.tab;\s*renderTab\(\)/, '标签切换必须先落盘当前预览编辑');

  const renderPreviewWindow = functionSource(renderer, 'renderPreviewWindow');
  assert.match(renderPreviewWindow, /const renderedIndex = previewLineIndex/, '流式预览必须捕获本次索引快照');
  assert.match(renderPreviewWindow, /const streamToken = renderedIndex\.streamToken/, '流式预览必须捕获本次token');
  assert.match(renderPreviewWindow, /renderId !== previewRenderSerial \|\| activeTab !== 'preview' \|\| previewLineIndex !== renderedIndex/, '异步读取返回时必须校验渲染代次、标签和索引');
  assert.match(renderPreviewWindow, /streamToken !== \(lastPreviewStream && lastPreviewStream\.token\)/, '异步读取返回时必须校验流式token仍有效');
  assert.match(functionSource(renderer, 'setPreviewText'), /previewRenderSerial \+= 1/, '非窗口渲染必须使旧异步读取失效');
  assert.match(renderer, /#pat-reset[\s\S]*?previewRenderSerial \+= 1/, '重置必须使旧异步读取失效');

  const exportStructureText = functionSource(renderer, 'exportStructureText');
  assert.match(exportStructureText, /if \(!lastStructureText\) return;/, '结构TXT是否可导出只能依据已生成结构快照');
  assert.match(exportStructureText, /patExportText\(lastStructureText\)/, '结构TXT必须导出已生成快照');
  assert.doesNotMatch(exportStructureText, /deviceModel\.value|currentProfile\(\)/, '切换型号后不得按当前控件状态阻止旧结构TXT导出');
});

test('fixed SPI Flash profiles retain the authorized Dual and QE classification contract', () => {
  const renderer = fs.readFileSync(rendererPath, 'utf8');
  const classA = ['BY25Q40ALTIG', 'BY25Q16BL', 'BY25Q80AL'];
  const classB = ['BY25Q16ESOIG', 'BY25Q80ES', 'GD25LQ40E', 'GD25Q40CTIG', 'W25Q40CLSNIG', 'W25Q64JVSSIQ'];

  for (const name of classA) {
    const profile = profileSource(renderer, name);
    assert.match(profile, /\bdualProgram:\s*0xA2\b/, `${name} 必须保留 A2h Dual Page Program`);
    assert.match(profile, /\bdualRead:\s*0x3B\b/, `${name} Dual Read 必须是 3Bh`);
    assert.match(profile, /\bvolatileQeWrite:\s*true\b/, `${name} 必须允许 50h 易失 QE 写入`);
  }

  for (const name of classB) {
    const profile = profileSource(renderer, name);
    assert.doesNotMatch(profile, /\bdualProgram\s*:/, `${name} 无 A2h，Profile 不得用 02h 冒充 dualProgram`);
    assert.match(profile, /\bdualRead:\s*0x3B\b/, `${name} Dual Read 必须是 3Bh`);
    assert.match(profile, /\bvolatileQeWrite:\s*true\b/, `${name} 必须允许 50h 易失 QE 写入`);
  }

  const mx = profileSource(renderer, 'MX25U4033EM');
  assert.doesNotMatch(mx, /\bdualProgram\s*:/, 'MX25U4033E 无 A2h，Profile 不得用 02h 冒充 dualProgram');
  assert.match(mx, /\bdualRead:\s*0xBB\b/, 'MX25U4033E Dual Read 必须是 BBh 2READ');
  assert.match(mx, /\bquadProgram:\s*0x38\b/, 'MX25U4033E Quad Program 必须是 38h 4PP');
  assert.match(mx, /\bquadRead:\s*0xEB\b/, 'MX25U4033E Quad Read 必须是 EBh 4READ');
  assert.match(mx, /\bvolatileQeWrite:\s*false\b/, 'MX25U4033E 禁止 50h 易失 QE 写入');
  assert.match(mx, /\bqeInit:\s*['"]mx-nonvolatile['"]/, 'MX25U4033E QE 初始化必须走非易失路径');

  const volSetMatch = renderer.match(/const SDI_VOL_SINGLE_WIRE_PROGRAM_DEVICES = new Set\(\[([\s\S]*?)\]\);/);
  assert.ok(volSetMatch, '缺少 SDI VOL 单线写入型号集合');
  const singleWireVolModels = [...volSetMatch[1].matchAll(/['"]([^'"]+)['"]/g)].map(match => match[1]).sort();
  assert.deepEqual(singleWireVolModels, [
    'BY25Q16ESOIG',
    'BY25Q80ES',
    'GD25LQ40E',
    'GD25Q40CTIG',
    'MX25U4033EM',
    'W25Q40CLSNIG',
    'W25Q64JVSSIQ'
  ], '七款 02h 器件的 SDI VOL 必须全部使用 SPI 单线写数据，且不得扩大到三款 A2h 器件');

  const funcBuilder = functionSource(renderer, 'patBuildFunc');
  assert.match(functionSource(renderer, 'patFuncPageProgram'), /await patFuncDataExpanded\(/, 'FUNC写入数据必须继续逐Byte展开');
  assert.doesNotMatch(funcBuilder, /patWip\([^\n]*(?:Sector Erase完成|Page Program完成)[^\n]*0x05,\s*1,\s*true\s*\)/, 'FUNC擦除和编程后的WIP检查不得展开为单次读取');
  assert.match(funcBuilder, /patWip\([^\n]*Sector Erase完成[^\n]*0x05,\s*1,\s*false,\s*true\s*\)/, 'FUNC擦除后必须保留完整四向量时钟的LOOP MATCH轮询');
  assert.match(funcBuilder, /patWip\([^\n]*Page Program完成[^\n]*0x05,\s*1,\s*false,\s*true\s*\)/, 'FUNC编程后必须保留完整四向量时钟的LOOP MATCH轮询');
});

test('large PAT generation is cooperative, cancellable and uses a bounded preview window', () => {
  const renderer = fs.readFileSync(rendererPath, 'utf8');
  assert.match(renderer, /const PREVIEW_WINDOW_LINES = 5000;/);
  assert.match(renderer, /const MAX_PAT_LINES = Number\.MAX_SAFE_INTEGER;/);
  assert.match(renderer, /const IN_MEMORY_PAT_LINE_THRESHOLD = 2000000;/);
  assert.match(renderer, /const FIXED_SERIAL_MEMORY_STREAM_THRESHOLD = 100000;/, '固定SRAM/EEPROM应在10万行估算时提前切换流式生成');
  assert.match(renderer, /async ensureStreaming\(job = ownerJob\)/);
  assert.match(renderer, /PAT 已超过内存阈值，正在无损切换到磁盘流式生成/);
  assert.match(renderer, /appendLargePat\(\{ token, content: '\\n' \}\)/);
  assert.match(renderer, /async function patBuildMemory\(job\)/);
  assert.match(renderer, /async function patReadCompare\(/);
  assert.match(renderer, /await new Promise\(resolve => setTimeout\(resolve, 0\)\)/);
  assert.match(renderer, /generationCancelButton\.addEventListener\('click'/);
  assert.match(renderer, /output\.textContent = lastPreview\.slice\(startOffset, endOffset\)/);
  assert.match(renderer, /output\.contentEditable = 'false'/);
  const sramTemplate = functionSource(renderer, 'patSramDataTemplate');
  assert.match(renderer, /async function patSramDataTemplate\(/, 'SRAM超长模板生成必须是异步分片helper');
  assert.match(sramTemplate, /\(byteIndex \+ 1\) % 64 === 0[\s\S]*await generationCheckpoint\(job/, 'SRAM写模板每64 Byte必须给UI让出事件循环');
  assert.match(functionSource(renderer, 'patSramWrite'), /await patSramDataTemplate\(/, '固定SRAM写入必须调用可取消的异步模板helper');
  for (const builder of ['patBuildSram', 'patBuildEeprom', 'patBuildSpiEeprom']) {
    assert.match(functionSource(renderer, builder), /createPatLineTarget\([\s\S]*FIXED_SERIAL_MEMORY_STREAM_THRESHOLD/, `${builder}必须使用固定串行存储器的10万行流式阈值`);
  }
  for (const id of [
    'pat-generation-success-dialog',
    'pat-generation-success-message',
    'pat-generation-success-confirm'
  ]) {
    assert.match(renderer, new RegExp(`id=["']${id}["']`), `${id} 必须存在`);
  }
});

test('renderer is a direct local page with offline resources and no eval permission', () => {
  const renderer = fs.readFileSync(rendererPath, 'utf8');
  assert.equal(/<iframe\b/i.test(renderer), false);
  assert.equal(/\bsrcdoc\s*=/i.test(renderer), false);
  assert.equal(/<script[^>]+src=["']https?:/i.test(renderer), false);
  assert.equal(/unsafe-eval|wasm-unsafe-eval/i.test(renderer), false);
  assert.equal(/\beval\s*\(/.test(renderer), false);
  assert.match(renderer, /connect-src 'none'/);
  assert.match(renderer, /window\.desktopAPI\.saveFile/);
  assert.match(renderer, /'showSaveFilePicker' in window/);
  assert.match(renderer, /link\.download = suggestedName/);
});

test('all renderer script dependencies are declared and locally present', () => {
  const packageJson = JSON.parse(read('package.json'));
  assert.equal(packageJson.dependencies['@floating-ui/core'], '1.7.3');
  assert.equal(packageJson.dependencies['@floating-ui/dom'], '1.7.4');
  assert.equal(packageJson.dependencies.lucide, '1.17.0');
  const vendoredAssets = [
    ['node_modules/@floating-ui/core/dist/floating-ui.core.umd.min.js', 'renderer/vendor/floating-ui.core.umd.min.js'],
    ['node_modules/@floating-ui/dom/dist/floating-ui.dom.umd.min.js', 'renderer/vendor/floating-ui.dom.umd.min.js'],
    ['node_modules/lucide/dist/umd/lucide.js', 'renderer/vendor/lucide.js']
  ];
  for (const [packageAsset, vendoredAsset] of vendoredAssets) {
    const packageBytes = fs.readFileSync(path.join(projectRoot, packageAsset));
    const vendoredBytes = fs.readFileSync(path.join(projectRoot, vendoredAsset));
    assert.deepEqual(vendoredBytes, packageBytes, `${vendoredAsset} 必须与锁定依赖中的资源逐字节一致`);
  }
  const renderer = fs.readFileSync(rendererPath, 'utf8');
  assert.match(renderer, /src=["']\.\/vendor\/floating-ui\.core\.umd\.min\.js["']/);
  assert.match(renderer, /src=["']\.\/vendor\/floating-ui\.dom\.umd\.min\.js["']/);
  assert.match(renderer, /src=["']\.\/vendor\/lucide\.js["']/);
});

test('Electron window and build configuration retain the required security contract', () => {
  const main = read('main.js');
  const preload = read('preload.js');
  const saveFile = read('save-file.js');
  const builder = read('electron-builder.yml');
  const packageJson = JSON.parse(read('package.json'));

  assert.match(main, /nodeIntegration:\s*false/);
  assert.match(main, /contextIsolation:\s*true/);
  assert.match(main, /sandbox:\s*true/);
  assert.match(main, /devTools:\s*false/);
  assert.match(main, /setWindowOpenHandler\(\(\) => \(\{ action: 'deny' \}\)\)/);
  assert.match(main, /setPermissionRequestHandler/);
  assert.match(main, /disable-background-networking/);
  assert.match(main, /saveFileWithDialog/);
  assert.match(main, /LargePatStore\.create\(\)/);
  assert.match(main, /registerLargePatHandlers\(largePatStore\)/);
  assert.match(saveFile, /dialog\.showSaveDialog/);
  assert.match(preload, /contextBridge\.exposeInMainWorld\('desktopAPI'/);
  for (const method of [
    'createLargePat',
    'appendLargePat',
    'finalizeLargePat',
    'readLargePatChunk',
    'saveLargePat',
    'discardLargePat'
  ]) {
    assert.match(preload, new RegExp('\\b' + method + '\\('), `preload 必须暴露 ${method}`);
  }
  assert.equal(/require\(['"](?:node:)?(?:fs|child_process)/.test(preload), false);
  assert.match(builder, /appId:\s*com\.pat\.generator\.tool/);
  assert.match(builder, /productName:\s*PAT生成工具/);
  assert.match(builder, /^\s*-\s+large-pat-store\.js\s*$/m);
  assert.match(builder, /target:\s*portable/);
  assert.match(builder, /npmRebuild:\s*true/);
  assert.match(builder, /beforeBuild:\s*scripts\/skip-dependency-rebuild\.js/);
  assert.doesNotMatch(builder, /^\s*-\s+node_modules\//m);
  assert.match(read('scripts/skip-dependency-rebuild.js'), /module\.exports\s*=\s*async\s*\(\)\s*=>\s*false/);
  assert.equal(/nsis|msi|appx/i.test(builder), false);
  assert.equal(packageJson.scripts.start, 'electron .');
  assert.equal(packageJson.scripts.portable, 'node scripts/build-portable.js');
  assert.match(read('scripts/build-portable.js'), /electron-builder\/cli\.js/);
});
