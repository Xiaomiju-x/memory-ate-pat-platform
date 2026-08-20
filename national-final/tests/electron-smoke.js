'use strict';

const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');
const { app, BrowserWindow, ipcMain, Menu, session } = require('electron');
const { LargePatStore } = require('../large-pat-store');
const { LARGE_PAT_CHANNELS, registerLargePatHandlers } = require('../main');

const projectRoot = path.resolve(__dirname, '..');
const entry = path.join(projectRoot, 'renderer', 'index.html');
const preload = path.join(projectRoot, 'preload.js');
const saveRequests = [];
const consoleErrors = [];
const remoteRequests = [];
const largePatRequests = {
  create: [],
  discard: []
};
let nextSaveResult = { ok: true, canceled: false, fileName: 'smoke.pat' };
let currentStage = '初始化';
let smokeLargePatStore = null;
let largePatReadDelayMs = 0;
let largePatReadStarted = 0;

function delay(milliseconds) {
  return new Promise(resolve => setTimeout(resolve, milliseconds));
}

function normalizeRenderedText(value) {
  return String(value).replace(/\r\n/g, '\n').replace(/\n\s*\n/g, '\n').trim();
}

async function waitFor(check, label, timeout = 10000) {
  const deadline = Date.now() + timeout;
  while (Date.now() < deadline) {
    if (await check()) return;
    await delay(25);
  }
  throw new Error(`等待超时：${label}`);
}

async function assertAndCloseGenerationSuccess(window, label) {
  await waitFor(
    () => window.webContents.executeJavaScript("document.querySelector('#pat-generation-success-dialog')?.open === true"),
    `${label}生成成功弹窗`,
    30000
  );
  const state = await window.webContents.executeJavaScript(`(() => {
    const root = document.querySelector('#pat-generator-prototype');
    const dialog = document.querySelector('#pat-generation-success-dialog');
    return {
      open: dialog.open,
      message: document.querySelector('#pat-generation-success-message').textContent,
      lineCount: Number(root.dataset.patLineCount),
      filename: document.querySelector('#pat-file-name').textContent,
      confirmDisabled: document.querySelector('#pat-generation-success-confirm').disabled
    };
  })()`);
  assert.equal(state.open, true, `${label}成功后应打开提示弹窗`);
  assert.match(state.message, /生成成功/, `${label}弹窗应明确提示生成成功`);
  assert.ok(
    state.message.includes(state.lineCount.toLocaleString('zh-CN')),
    `${label}弹窗应包含行数 ${state.lineCount.toLocaleString('zh-CN')}`
  );
  assert.ok(state.filename && state.message.includes(state.filename), `${label}弹窗应包含文件名`);
  assert.equal(state.confirmDisabled, false, `${label}成功弹窗确认按钮应可用`);
  await window.webContents.executeJavaScript("document.querySelector('#pat-generation-success-confirm').click()");
  await waitFor(
    () => window.webContents.executeJavaScript("document.querySelector('#pat-generation-success-dialog')?.open === false"),
    `${label}生成成功弹窗关闭`
  );
  return state;
}

async function assertGenerationSuccessClosed(window, label) {
  const open = await window.webContents.executeJavaScript("document.querySelector('#pat-generation-success-dialog')?.open === true");
  assert.equal(open, false, `${label}不得弹出生成成功提示`);
}

async function readPatSnapshot(window) {
  return window.webContents.executeJavaScript(`(() => {
    const root = document.querySelector('#pat-generator-prototype');
    return {
      text: document.querySelector('#pat-output').innerText,
      filename: document.querySelector('#pat-file-name').textContent,
      lineCount: Number(root.dataset.patLineCount),
      validation: root.dataset.validation,
      generatorState: root.dataset.generatorState,
      previewWindowed: root.dataset.previewWindowed,
      exportDisabled: document.querySelector('#pat-export').disabled,
      progressHidden: document.querySelector('#pat-generation-progress').hidden,
      successOpen: document.querySelector('#pat-generation-success-dialog').open
    };
  })()`);
}

function assertPatSnapshotUnchanged(actual, expected, label) {
  assert.deepEqual(actual, expected, `${label}不得重算、清空或替换上一份 PAT`);
  assert.equal(actual.progressHidden, true, `${label}不得启动生成进度`);
  assert.equal(actual.successOpen, false, `${label}不得弹出生成成功提示`);
}

function transactionBlocks(text) {
  const starts = [...text.matchAll(/^\/\/ ((?:QTX|STX|TX)\d+) BEGIN：([^\r\n]*)/gm)];
  return starts.map((match, index) => ({
    tag: match[1],
    title: match[2],
    index: match.index,
    body: text.slice(match.index, index + 1 < starts.length ? starts[index + 1].index : text.length)
  }));
}

function findTransactionByTag(text, tag, label) {
  const block = transactionBlocks(text).find(item => item.tag === tag);
  assert.ok(block, `${label}缺少 ${tag} 事务`);
  return block;
}

function vectorRows(text) {
  return text.split(/\r?\n/).map(line => {
    const match = line.match(/^\s*(?:start:\s+|end:\s+)?([01HLXZ]{6});/);
    return match ? match[1] : null;
  }).filter(Boolean);
}

function decodeSpiByte(vectors, label) {
  assert.equal(vectors.length, 32, `${label}必须包含 8 bit × 4 vectors`);
  const bits = [];
  for (let bit = 0; bit < 8; bit += 1) {
    const group = vectors.slice(bit * 4, bit * 4 + 4);
    assert.equal(group.map(vector => vector[4]).join(''), '0110', `${label} bit${7 - bit} 时钟必须是 0→1→1→0`);
    assert.ok(group.every(vector => /^[01]$/.test(vector[3])), `${label} bit${7 - bit} 必须由 SI/IO0 实际驱动`);
    assert.ok(group.every(vector => vector[3] === group[0][3]), `${label} bit${7 - bit} 在完整时钟内必须保持稳定`);
    bits.push(group[1][3]);
  }
  return parseInt(bits.join(''), 2);
}

function decodeTransactionCommand(block, label) {
  const marker = `[${block.tag}:CMD]`;
  const markerIndex = block.body.indexOf(marker);
  assert.notEqual(markerIndex, -1, `${label}缺少 ${marker} 命令向量标记`);
  return decodeSpiByte(vectorRows(block.body.slice(markerIndex)).slice(0, 32), `${label}命令`);
}

function decodeFirstTransactionDataByte(block, label) {
  const marker = `[${block.tag}:CMD]`;
  const markerIndex = block.body.indexOf(marker);
  assert.notEqual(markerIndex, -1, `${label}缺少 ${marker} 命令向量标记`);
  return decodeSpiByte(vectorRows(block.body.slice(markerIndex)).slice(32, 64), `${label}首个数据 Byte`);
}

function taggedSampleVectors(block, tag) {
  const marker = `[${tag}]`;
  return block.body.split(/\r?\n/).map(line => {
    if (!line.includes(marker)) return null;
    const match = line.match(/^\s*(?:start:\s+|end:\s+)?([01HLXZ]{6});/);
    return match ? match[1] : null;
  }).filter(Boolean);
}

function decodeTaggedDataBytes(block, tag, bus, compare, label) {
  const samples = taggedSampleVectors(block, tag);
  const clocksPerByte = bus === 'SPI' ? 8 : (bus === 'SDI' ? 4 : 2);
  assert.equal(samples.length % clocksPerByte, 0, `${label}采样数必须是每Byte时钟数的整数倍`);
  const bitValue = symbol => {
    if (symbol === '0' || symbol === 'L') return '0';
    if (symbol === '1' || symbol === 'H') return '1';
    assert.fail(`${label}出现不可解码的数据符号 ${symbol}`);
  };
  return Array.from({ length: samples.length / clocksPerByte }, (_, byteIndex) => {
    const byteSamples = samples.slice(byteIndex * clocksPerByte, (byteIndex + 1) * clocksPerByte);
    const bits = byteSamples.flatMap(vector => {
      assert.equal(vector[4], '1', `${label}必须在SCLK High采样`);
      if (bus === 'SPI') return [bitValue(compare ? vector[1] : vector[3])];
      if (bus === 'SDI') return [bitValue(vector[1]), bitValue(vector[3])];
      return [bitValue(vector[5]), bitValue(vector[2]), bitValue(vector[1]), bitValue(vector[3])];
    });
    return parseInt(bits.join(''), 2);
  });
}

function assertDriveSamples(samples, bus, count, label) {
  assert.equal(samples.length, count, `${label}实际时钟数必须为 ${count}`);
  for (const vector of samples) {
    assert.equal(vector[4], '1', `${label}检查点必须位于 SCLK High`);
    if (bus === 'SPI') {
      assert.equal(vector[1], 'X', `${label}单线输入时 SO/IO1 必须释放`);
      assert.match(vector[3], /^[01]$/, `${label}单线输入必须由 SI/IO0 驱动`);
    } else if (bus === 'SDI') {
      assert.match(vector[1], /^[01]$/, `${label}双线输入必须驱动 IO1`);
      assert.match(vector[3], /^[01]$/, `${label}双线输入必须驱动 IO0`);
    } else {
      for (const pin of [1, 2, 3, 5]) assert.match(vector[pin], /^[01]$/, `${label}四线输入必须驱动全部 IO`);
    }
  }
}

function assertCompareSamples(samples, bus, count, label) {
  assert.equal(samples.length, count, `${label}实际比较时钟数必须为 ${count}`);
  const pins = bus === 'SDI' ? [1, 3] : [1, 2, 3, 5];
  for (const vector of samples) {
    assert.equal(vector[4], '1', `${label}比较点必须位于 SCLK High`);
    for (const pin of pins) assert.match(vector[pin], /^[HL]$/, `${label}必须在实际输出 IO 上使用 H/L 比较`);
  }
}

function assertAddressVectors(block, bus, label) {
  const suffix = bus === 'SPI' ? 'ADDR' : `${bus}-ADDR`;
  const samples = taggedSampleVectors(block, `${block.tag}:${suffix}`);
  assertDriveSamples(samples, bus, bus === 'SPI' ? 24 : (bus === 'SDI' ? 12 : 6), `${label}地址阶段`);
}

function assertProgramTransaction(text, expected, label) {
  const blocks = transactionBlocks(text).filter(block => /^(?:Dual Page Program|Page Program|4 x I\/O Page Program|Quad Page Program)（/.test(block.title));
  assert.equal(blocks.length, 1, `${label}必须且只能有一个 Program 事务`);
  const block = blocks[0];
  assert.match(block.title, expected.title, `${label}Program 事务名称错误`);
  assert.equal(decodeTransactionCommand(block, label), expected.opcode, `${label}Program 实际命令向量错误`);
  assertAddressVectors(block, expected.addressBus, label);
  assertDriveSamples(
    taggedSampleVectors(block, `${block.tag}:DATA-IN`),
    expected.dataBus,
    (expected.dataBus === 'SPI' ? 8 : (expected.dataBus === 'SDI' ? 4 : 2)) * (expected.dataBytes || 1),
    `${label}Program Data`
  );
  return block;
}

function assertFuncRwPolling(text, expectedLoopCount, label) {
  const blocks = transactionBlocks(text);
  const cases = [
    { operation: /^Sector Erase（20h）/, reason: 'Sector Erase完成' },
    { operation: /^(?:Dual Page Program|Page Program|4 x I\/O Page Program|Quad Page Program)（/, reason: 'Page Program完成' }
  ];
  for (const item of cases) {
    const operationIndex = blocks.findIndex(block => item.operation.test(block.title));
    assert.notEqual(operationIndex, -1, `${label}缺少 ${item.reason} 前置事务`);
    const polling = blocks[operationIndex + 1];
    assert.ok(polling, `${label}${item.reason}后缺少状态轮询事务`);
    assert.match(polling.title, new RegExp(`^Read Status Register-1（05h），等待${item.reason}$`), `${label}${item.reason}后必须立即读取05h`);
    assert.match(polling.body, new RegExp(`LOOP MATCH ${expectedLoopCount};`), `${label}${item.reason}后必须使用LOOP MATCH ${expectedLoopCount}`);
    assert.match(polling.body, /LOOP END;/, `${label}${item.reason}轮询必须闭合LOOP END`);
    assert.equal((polling.body.match(/LOOP MATCH \d+;/g) || []).length, 1, `${label}${item.reason}轮询只能有一个LOOP MATCH`);
    assert.equal((polling.body.match(/LOOP END;/g) || []).length, 1, `${label}${item.reason}轮询只能有一个LOOP END`);
    const matchIndex = polling.body.indexOf(`LOOP MATCH ${expectedLoopCount};`);
    const endIndex = polling.body.indexOf('LOOP END;', matchIndex);
    const matchLineStart = polling.body.lastIndexOf('\n', matchIndex) + 1;
    const endLineEnd = polling.body.indexOf('\n', endIndex);
    const statusVectors = vectorRows(polling.body.slice(matchLineStart, endLineEnd === -1 ? polling.body.length : endLineEnd));
    assert.equal(statusVectors.length, 32, `${label}${item.reason}每次SR1轮询必须按8 bit × 4 vectors完整输出`);
    assert.equal(decodeTransactionCommand(polling, `${label}${item.reason}状态轮询`), 0x05, `${label}${item.reason}状态轮询必须实际发送05h`);
    for (let bit = 7; bit >= 0; bit -= 1) {
      const group = statusVectors.slice((7 - bit) * 4, (8 - bit) * 4);
      assert.equal(group.map(vector => vector[4]).join(''), '0110', `${label}${item.reason} S${bit}时钟必须为0→1→1→0`);
      assert.equal(group[1], group[2], `${label}${item.reason} S${bit}两个High保持向量必须一致`);
      assert.equal(group[1][1], bit === 0 ? 'L' : 'X', `${label}${item.reason}必须只在S0比较WIP=Low`);
      assert.equal((polling.body.match(new RegExp(`\\[${polling.tag}:STATUS\\] S${bit}=`, 'g')) || []).length, 1, `${label}${item.reason} S${bit}标记必须恰好一次`);
    }
    assert.match(polling.body.slice(0, matchIndex), new RegExp(`\\[${polling.tag}:CMD\\]`), `${label}${item.reason}LOOP MATCH必须位于05h命令之后`);
    assert.match(polling.body.slice(matchIndex, endIndex + 'LOOP END;'.length), new RegExp(`\\[${polling.tag}:STATUS\\] S0=0[\\s\\S]*LOOP END;`), `${label}${item.reason}LOOP END必须闭合在S0/WIP=0周期`);
    assert.doesNotMatch(polling.body, /单次读取|全部向量直接展开/, `${label}${item.reason}状态轮询不得退化为单次展开读取`);
  }

  const program = blocks.find(block => /^(?:Dual Page Program|Page Program|4 x I\/O Page Program|Quad Page Program)（/.test(block.title));
  assert.ok(program, `${label}缺少Program事务`);
  assert.doesNotMatch(program.body, /\bLOOP(?:\s+MATCH|\s+END|\s+\d+)\b/, `${label}写入数据必须逐Byte展开，不得使用普通LOOP或LOOP MATCH`);
  const mutationPolls = blocks.filter(block => /^Read Status Register-1（05h），等待(?:Sector Erase|Page Program)完成$/.test(block.title));
  assert.equal(mutationPolls.length, 2, `${label}必须且只能有擦除后、编程后两次目标WIP轮询`);
}

function assertFullPageFuncData(programBlock, readBlock, programBus, label) {
  const expected = Array.from({ length: 256 }, (_value, index) => index % 2 === 0 ? 0xAA : 0x55);
  assert.deepEqual(decodeTaggedDataBytes(programBlock, `${programBlock.tag}:DATA-IN`, programBus, false, `${label}写入数据`), expected, `${label}写入必须严格按AA/55交替展开256 Byte`);
  assert.deepEqual(decodeTaggedDataBytes(readBlock, `${readBlock.tag}:DATA-OUT`, 'SDI', true, `${label}读回数据`), expected, `${label}读回期望必须严格按AA/55交替展开256 Byte`);
  assert.equal((programBlock.body.match(new RegExp(`\\[${programBlock.tag}:WRITE BYTE\\[`, 'g')) || []).length, 256, `${label}必须包含256个WRITE BYTE标记`);
  assert.equal((readBlock.body.match(new RegExp(`\\[${readBlock.tag}:READ BYTE\\[`, 'g')) || []).length, 256, `${label}必须包含256个READ BYTE标记`);
  assert.match(programBlock.body, /WRITE BYTE\[001\] @0x000000/, `${label}写入首地址必须为0x000000`);
  assert.match(programBlock.body, /WRITE BYTE\[256\] @0x0000FF/, `${label}写入末地址必须为0x0000FF`);
  assert.match(readBlock.body, /READ BYTE\[001\] @0x000000/, `${label}读回首地址必须为0x000000`);
  assert.match(readBlock.body, /READ BYTE\[256\] @0x0000FF/, `${label}读回末地址必须为0x0000FF`);
}

function dummySampleVectors(block) {
  return block.body.split(/\r?\n/).map(line => {
    if (!/\/\/ Dummy Clock \d+\/\d+/.test(line)) return null;
    const match = line.match(/^\s*([01HLXZ]{6});/);
    return match ? match[1] : null;
  }).filter(Boolean);
}

function assertPerformanceIndicatorFf(block, label) {
  const marker = block.body.search(new RegExp(`\\[${block.tag}:(?:PERFORMANCE|P-IND)\\]`));
  assert.notEqual(marker, -1, `${label}缺少 Performance Indicator 段`);
  const dummyMarker = block.body.indexOf(`[${block.tag}:DUMMY]`, marker);
  assert.notEqual(dummyMarker, -1, `${label}Performance Indicator 后缺少 Dummy 段`);
  const section = block.body.slice(marker, dummyMarker);
  assert.match(section, /FFh/, `${label}Performance Indicator 必须明确为 FFh`);
  const vectors = vectorRows(section);
  assert.equal(vectors.length, 8, `${label}Performance Indicator 必须是 2 个 Quad clocks`);
  for (let cycle = 0; cycle < 2; cycle += 1) {
    const group = vectors.slice(cycle * 4, cycle * 4 + 4);
    assert.equal(group.map(vector => vector[4]).join(''), '0110', `${label}Performance cycle ${cycle + 1} 时钟错误`);
    for (const vector of group) {
      for (const pin of [1, 2, 3, 5]) assert.equal(vector[pin], '1', `${label}Performance Indicator 必须实际驱动 FFh`);
    }
  }
}

function assertReadTransaction(text, expected, label) {
  const blocks = transactionBlocks(text).filter(block => /^(?:Fast Read Dual Output|2READ|4 x I\/O Read)（/.test(block.title));
  assert.equal(blocks.length, 1, `${label}必须且只能有一个目标 Read 事务`);
  const block = blocks[0];
  assert.match(block.title, expected.title, `${label}Read 事务名称错误`);
  assert.equal(decodeTransactionCommand(block, label), expected.opcode, `${label}Read 实际命令向量错误`);
  assertAddressVectors(block, expected.addressBus, label);
  if (expected.performanceFf) assertPerformanceIndicatorFf(block, label);
  const dummy = dummySampleVectors(block);
  assert.equal(dummy.length, expected.dummy, `${label}Dummy 实际时钟数错误`);
  assert.ok(dummy.every(vector => vector[4] === '1'), `${label}Dummy 检查点必须位于 SCLK High`);
  assertCompareSamples(
    taggedSampleVectors(block, `${block.tag}:DATA-OUT`),
    expected.dataBus,
    (expected.dataBus === 'SDI' ? 4 : 2) * (expected.dataBytes || 1),
    `${label}Read Data`
  );
  return block;
}

function decodedCommands(text) {
  return transactionBlocks(text).filter(block => block.body.includes(`[${block.tag}:CMD]`)).map(block => ({
    tag: block.tag,
    title: block.title,
    opcode: decodeTransactionCommand(block, block.tag)
  }));
}

function decodeI2cTaggedBytes(text, tx, field, label) {
  const marker = `[${tx}:${field}]`;
  const bits = text.split(/\r?\n/).map(line => {
    if (!line.includes(marker)) return null;
    const match = line.match(/^\s*(?:start:\s+|end:\s+)?([01HLXZ]{3});/);
    if (!match) return null;
    assert.equal(match[1][1], '1', `${label}的标记采样点必须位于 SCL High`);
    assert.match(match[1][0], /^[01]$/, `${label}必须由主机实际驱动 SDA`);
    return match[1][0];
  }).filter(bit => bit !== null);
  assert.ok(bits.length > 0 && bits.length % 8 === 0, `${label}必须包含完整的 8-bit 字节`);
  const bytes = [];
  for (let offset = 0; offset < bits.length; offset += 8) {
    bytes.push(parseInt(bits.slice(offset, offset + 8).join(''), 2));
  }
  return bytes;
}

function assertMxNonvolatileQeClear(text, label, requireDescription = true) {
  if (requireDescription) {
    assert.match(text, /非易失(?:性)?[^\r\n]*清除[^\r\n]*QE|清除[^\r\n]*非易失[^\r\n]*QE/, `${label}必须说明以非易失方式清 QE`);
  }
  const blocks = transactionBlocks(text);
  const statusWrites = blocks.filter(block => /Write Status Register/.test(block.title) && decodeTransactionCommand(block, `${label} WRSR`) === 0x01);
  assert.equal(statusWrites.length, 1, `${label}必须且只能执行一次非易失 WRSR 清 QE`);
  const write = statusWrites[0];
  assert.equal(decodeFirstTransactionDataByte(write, `${label} WRSR`), 0x00, `${label}WRSR 必须实际写入 00h`);
  const writeIndex = blocks.indexOf(write);
  const before = blocks.slice(0, writeIndex).map(block => decodeTransactionCommand(block, `${label} ${block.tag}`));
  const after = blocks.slice(writeIndex + 1).map(block => decodeTransactionCommand(block, `${label} ${block.tag}`));
  assert.ok(before.includes(0x06), `${label}WRSR 之前必须有实际 06h WREN 向量`);
  assert.ok(after.filter(opcode => opcode === 0x05).length >= 2, `${label}WRSR 后必须以 05h 等待并确认 Status=00h`);
  assert.equal(decodedCommands(text).some(command => command.opcode === 0x50), false, `${label}不得出现实际 50h 命令向量`);
}

function assertMxNonvolatileQeSet(text, label) {
  assert.match(text, /QE=Status Register bit6[^\r\n]*NON-VOLATILE/i, `${label}文件头必须说明 QE bit6 为 NON-VOLATILE`);
  assert.match(text, /非易失性设置\s*QE=1/, `${label}必须说明非易失性设置 QE=1`);
  assert.match(text, /掉电后QE仍保持1/, `${label}必须说明掉电后 QE 仍保持 1`);
  const qtx1 = findTransactionByTag(text, 'QTX1', label);
  const qtx2 = findTransactionByTag(text, 'QTX2', label);
  const qtx3 = findTransactionByTag(text, 'QTX3', label);
  const qtx4 = findTransactionByTag(text, 'QTX4', label);
  assert.deepEqual(
    [qtx1, qtx2, qtx3, qtx4].map((block, index) => decodeTransactionCommand(block, `${label} QTX${index + 1}`)),
    [0x06, 0x01, 0x05, 0x05],
    `${label}QE 初始化实际命令必须为 06h→01h→05h→05h`
  );
  assert.equal(decodeFirstTransactionDataByte(qtx2, `${label} QTX2`), 0x40, `${label}WRSR 必须实际写入 40h`);
  assert.equal(decodedCommands(text).some(command => command.opcode === 0x50), false, `${label}不得出现实际 50h 命令向量`);
  assert.match(text, /PAT结束[^\r\n]*QE仍[^\r\n]*(?:非易失性)?\s*1|本PAT结束后QE仍保持1/, `${label}结束处必须明确 QE 仍为非易失性 1`);
}

async function generateFixedPat(window, { modelName, bus, kind, funcEndAddress = '000000', funcData = 'A5', captureExport = false }) {
  const label = `${modelName} ${bus} ${kind.toUpperCase()}`;
  currentStage = `生成并验收 ${label}`;
  const config = JSON.stringify({ modelName, bus, kind, funcEndAddress, funcData });
  const saveCountBefore = saveRequests.length;
  await window.webContents.executeJavaScript(`(() => {
    const config = ${config};
    const type = document.querySelector('#pat-device-type');
    const model = document.querySelector('#pat-device-model');
    type.value = 'SPI_FLASH';
    type.dispatchEvent(new Event('change', { bubbles: true }));
    model.value = config.modelName;
    model.dispatchEvent(new Event('change', { bubbles: true }));
    if (config.kind === 'memory') {
      document.querySelector('#pat-memory-view').click();
      document.querySelector('#pat-data-mode').value = 'mode1';
      document.querySelector('#pat-pattern').value = 'ALL 0';
      const bus = document.querySelector('#pat-memory-bus');
      bus.value = config.bus;
      bus.dispatchEvent(new Event('change', { bubbles: true }));
      document.querySelector('#pat-start').value = '000000';
      document.querySelector('#pat-end').value = '000000';
      document.querySelector('#pat-generate').click();
    } else {
      document.querySelector('#pat-func-view').click();
      document.querySelector('[data-func-panel="rw"]').click();
      const radio = document.querySelector('input[name="func-rw-bus"][value="' + config.bus + '"]');
      if (!radio || radio.disabled) throw new Error(config.modelName + ' 未开放 ' + config.bus + ' FUNC');
      radio.checked = true;
      radio.dispatchEvent(new Event('change', { bubbles: true }));
      document.querySelector('#func-rw-data').value = config.funcData;
      document.querySelector('#func-start-address').value = '000000';
      document.querySelector('#func-end-address').value = config.funcEndAddress;
      document.querySelector('#pat-func-generate').click();
    }
  })()`);
  const success = await assertAndCloseGenerationSuccess(window, label);
  const result = await window.webContents.executeJavaScript(`(() => ({
    text: document.querySelector('#pat-output').innerText,
    filename: document.querySelector('#pat-file-name').textContent
  }))()`);
  if (captureExport) {
    await window.webContents.executeJavaScript("document.querySelector('#pat-export').click()");
    await waitFor(() => saveRequests.length === saveCountBefore + 1, `${label}完整PAT导出IPC`);
    const request = saveRequests[saveCountBefore];
    assert.equal(request.kind, 'pat', `${label}必须通过PAT保存接口导出完整内容`);
    assert.equal(request.suggestedName, result.filename, `${label}导出文件名必须与预览一致`);
    assert.equal(request.content.includes('\r'), false, `${label}renderer到主进程的保存请求必须保持规范LF，由保存层统一转换CRLF`);
    assert.equal((request.content.match(/\n/g) || []).length, success.lineCount, `${label}完整导出逻辑行数必须与成功弹窗一致`);
    assert.equal(request.content.trimEnd().endsWith('@@END_PATTERN_DEFINE'), true, `${label}完整导出必须以@@END_PATTERN_DEFINE结束`);
    assert.equal((request.content.match(/^end:/gm) || []).length, 1, `${label}完整导出必须且只能有一个end标签`);
    result.text = request.content;
  }
  result.lineCount = success.lineCount;
  assert.equal(result.filename, success.filename, `${label}成功弹窗与当前文件名必须一致`);
  assert.match(result.filename, new RegExp('^' + modelName + '_' + bus + '_'), `${label}文件名必须标明芯片和总线`);
  return result;
}

async function sha256File(filePath) {
  const hash = crypto.createHash('sha256');
  await new Promise((resolve, reject) => {
    const stream = fs.createReadStream(filePath);
    stream.on('data', chunk => hash.update(chunk));
    stream.on('error', reject);
    stream.on('end', resolve);
  });
  return hash.digest('hex').toUpperCase();
}

async function generateFixedMemoryLargeCase(window, spec) {
  currentStage = `生成固定${spec.model}大PAT`;
  const createCountBefore = largePatRequests.create.length;
  const saveCountBefore = saveRequests.length;
  const serialized = JSON.stringify(spec);
  await window.webContents.executeJavaScript(`(() => {
    const spec = ${serialized};
    const dispatch = (element, type = 'change') => element.dispatchEvent(new Event(type, { bubbles: true }));
    document.querySelector('#pat-memory-view').click();
    const type = document.querySelector('#pat-device-type');
    const model = document.querySelector('#pat-device-model');
    type.value = spec.type;
    dispatch(type);
    const protocol = document.querySelector('#pat-eeprom-protocol');
    if (protocol && spec.protocol) {
      protocol.value = spec.protocol;
      dispatch(protocol);
    }
    model.value = spec.model;
    dispatch(model);
    const hex = document.querySelector('#pat-address-hex');
    if (hex.getAttribute('aria-pressed') !== 'true') hex.click();
    const mode = document.querySelector('#pat-data-mode');
    mode.value = spec.mode;
    dispatch(mode);
    const pattern = document.querySelector('#pat-pattern');
    pattern.value = spec.pattern;
    dispatch(pattern);
    const bus = document.querySelector('#pat-memory-bus');
    if (bus && spec.bus) {
      bus.value = spec.bus;
      dispatch(bus);
    }
    const operation = document.querySelector('#pat-eeprom-operation');
    if (operation && spec.operation) {
      operation.value = spec.operation;
      dispatch(operation);
    }
    document.querySelector('#pat-start').value = spec.start;
    document.querySelector('#pat-end').value = spec.end;
    window.__fixedMemoryHeartbeat = 0;
    window.__fixedMemoryWriteHeartbeat = 0;
    window.__fixedMemoryStartedAt = performance.now();
    window.__fixedMemoryHeartbeatTimer = setInterval(() => {
      window.__fixedMemoryHeartbeat += 1;
      if (document.querySelector('#pat-generation-status').textContent.includes('正在生成 SRAM 写入数据')) window.__fixedMemoryWriteHeartbeat += 1;
    }, 10);
    document.querySelector('#pat-generate').click();
  })()`);
  await waitFor(
    () => window.webContents.executeJavaScript("document.querySelector('#pat-generation-progress').hidden && document.querySelector('#pat-generation-success-dialog').open"),
    `${spec.model}大PAT生成`,
    spec.timeout
  );
  const success = await assertAndCloseGenerationSuccess(window, `${spec.model}大PAT`);
  await waitFor(
    () => window.webContents.executeJavaScript("!document.querySelector('#pat-output').textContent.startsWith('正在读取')"),
    `${spec.model}大PAT首段预览`,
    30000
  );
  const state = await window.webContents.executeJavaScript(`(() => {
    clearInterval(window.__fixedMemoryHeartbeatTimer);
    const root = document.querySelector('#pat-generator-prototype');
    const output = document.querySelector('#pat-output');
    return {
      filename: document.querySelector('#pat-file-name').textContent,
      lineCount: Number(root.dataset.patLineCount),
      windowed: root.dataset.previewWindowed,
      heartbeat: window.__fixedMemoryHeartbeat,
      writeHeartbeat: window.__fixedMemoryWriteHeartbeat,
      elapsed: performance.now() - window.__fixedMemoryStartedAt,
      renderedLines: output.textContent.split('\\n').length,
      renderedElementNodes: output.childElementCount,
      controlsVisible: !document.querySelector('#pat-large-preview-controls').hidden,
      readOnly: output.contentEditable === 'false',
      validation: root.dataset.validation,
      generatorState: root.dataset.generatorState
    };
  })()`);
  assert.equal(state.filename, success.filename, `${spec.model}成功弹窗文件名必须与当前PAT一致`);
  assert.equal(state.lineCount, success.lineCount, `${spec.model}成功弹窗行数必须与当前PAT一致`);
  if (spec.expectedLines != null) assert.equal(state.lineCount, spec.expectedLines, `${spec.model}全容量大PAT行数发生变化`);
  assert.equal(state.windowed, 'true', `${spec.model}大PAT必须使用分段预览`);
  assert.equal(state.controlsVisible, true, `${spec.model}大PAT必须显示分段预览控件`);
  assert.equal(state.readOnly, true, `${spec.model}大PAT的窗口预览必须只读`);
  assert.ok(state.renderedLines <= 5000, `${spec.model}大PAT同时渲染行数必须不超过5000`);
  assert.equal(state.renderedElementNodes, 0, `${spec.model}大PAT不得逐行创建DOM元素`);
  assert.ok(state.heartbeat >= spec.minimumHeartbeat, `${spec.model}生成期间事件循环必须持续响应，实际心跳${state.heartbeat}`);
  if (spec.verifyUncompressible) assert.ok(state.writeHeartbeat > 0, `${spec.model}不可压缩写模板展开期间必须有独立UI心跳`);
  assert.ok(state.elapsed < spec.maxElapsed, `${spec.model}大PAT生成耗时过长：${state.elapsed.toFixed(1)} ms`);

  const streamed = largePatRequests.create.length === createCountBefore + 1;
  console.log(`${spec.model} fixed-memory path diagnostic: ${state.lineCount.toLocaleString('en-US')} lines, create-count ${createCountBefore}→${largePatRequests.create.length}, expected ${spec.streamed ? 'streamed' : 'in-memory'}`);
  assert.equal(streamed, spec.streamed, `${spec.model}流式/内存生成路径与阈值契约不符`);
  let hash;
  if (streamed) {
    const request = largePatRequests.create.at(-1);
    const source = await smokeLargePatStore.getFinalizedSource({ token: request.token });
    assert.equal(source.lineCount, state.lineCount, `${spec.model}流式文件行数必须与UI一致`);
    assert.ok(source.sizeBytes > 0, `${spec.model}流式文件不得为空`);
    const expectedTail = Buffer.from('@@END_PATTERN_DEFINE\r\n', 'utf8');
    assert.ok(source.sizeBytes >= expectedTail.length, `${spec.model}流式文件长度异常`);
    const tail = Buffer.alloc(expectedTail.length);
    const handle = fs.openSync(source.filePath, 'r');
    try {
      fs.readSync(handle, tail, 0, tail.length, source.sizeBytes - tail.length);
    } finally {
      fs.closeSync(handle);
    }
    assert.deepEqual(tail, expectedTail, `${spec.model}真实流式文件必须以@@END_PATTERN_DEFINE + CRLF结束`);
    hash = await sha256File(source.filePath);
    if (spec.verifyUncompressible) {
      const content = fs.readFileSync(source.filePath, 'utf8');
      assert.match(content, /\/\/ 23LC1024 SPI CHECKERBOARD PAT/, '专项PAT必须是Checkerboard而不是可压缩ALL 0');
      assert.match(content, /LOOP 1; \/\/ LOOP 起点/, '奇数Byte Checkerboard必须使用整数LOOP 1完整展开模板');
      assert.doesNotMatch(content, /\bLOOP\s+\d+\.\d+\s*;/, 'SRAM PAT不得生成小数LOOP');
      assert.equal((content.match(/\[TX1:DATA-IN\]/g) || []).length, spec.byteCount * 8, 'SRAM不可压缩SPI写模板必须实际展开每Byte的8个bit标记');
      assert.equal((content.match(/\[TX2:READ BYTE\[/g) || []).length, spec.byteCount, 'SRAM读回必须逐Byte展开完整范围');
      assert.match(content, new RegExp(`\\[TX2:READ BYTE\\[${String(spec.byteCount).padStart(3, '0')}\\] @0x${spec.end.toUpperCase()}\\]`), 'SRAM读回末地址必须与用户范围一致');
    }
  } else {
    nextSaveResult = { ok: true, canceled: false, fileName: `${spec.model}-large.pat` };
    await window.webContents.executeJavaScript("document.querySelector('#pat-export').click()");
    await waitFor(() => saveRequests.length === saveCountBefore + 1, `${spec.model}大PAT完整导出`, 30000);
    const request = saveRequests[saveCountBefore];
    assert.equal(request.kind, 'pat');
    assert.equal(request.suggestedName, state.filename);
    assert.equal((request.content.match(/\n/g) || []).length, state.lineCount, `${spec.model}完整导出逻辑行数必须与UI一致`);
    assert.equal(request.content.trimEnd().endsWith('@@END_PATTERN_DEFINE'), true, `${spec.model}完整导出必须以END结束`);
    hash = crypto.createHash('sha256').update(request.content, 'utf8').digest('hex').toUpperCase();
  }
  if (spec.sha256) assert.equal(hash, spec.sha256, `${spec.model}全容量PAT内容哈希发生变化`);

  await window.webContents.executeJavaScript(`(() => {
    const root = document.querySelector('#pat-generator-prototype');
    document.querySelector('#pat-preview-jump').value = root.dataset.patLineCount;
    document.querySelector('#pat-preview-jump-button').click();
  })()`);
  await waitFor(
    () => window.webContents.executeJavaScript("document.querySelector('#pat-output').textContent.includes('@@END_PATTERN_DEFINE')"),
    `${spec.model}大PAT末尾预览`,
    30000
  );
  const retainedBeforeCancel = await readPatSnapshot(window);
  await window.webContents.executeJavaScript(`(() => {
    document.querySelector('#pat-generate').click();
    document.querySelector('#pat-generation-cancel').click();
  })()`);
  await waitFor(
    () => window.webContents.executeJavaScript("document.querySelector('#pat-generation-progress').hidden && document.querySelector('#pat-file-meta').textContent.includes('已取消生成')"),
    `${spec.model}大PAT取消`,
    30000
  );
  await assertGenerationSuccessClosed(window, `${spec.model}大PAT取消`);
  assertPatSnapshotUnchanged(await readPatSnapshot(window), retainedBeforeCancel, `${spec.model}取消新任务`);
  console.log(`${spec.model} fixed-memory large regression: ${state.lineCount.toLocaleString('en-US')} lines, ${state.elapsed.toFixed(1)} ms, ${state.heartbeat} heartbeats${spec.verifyUncompressible ? ` (${state.writeHeartbeat} during SRAM write expansion)` : ''}, ${streamed ? 'streamed' : 'in-memory'}, SHA-256 ${hash}`);
  return state;
}

async function run() {
  await app.whenReady();
  Menu.setApplicationMenu(null);
  session.defaultSession.webRequest.onBeforeRequest((details, callback) => {
    if (/^https?:/i.test(details.url)) remoteRequests.push(details.url);
    callback({ cancel: /^https?:/i.test(details.url) });
  });
  ipcMain.handle('file:save', async (_event, request) => {
    saveRequests.push(request);
    return nextSaveResult;
  });
  smokeLargePatStore = await LargePatStore.create();
  const createLargePatFile = smokeLargePatStore.createFile.bind(smokeLargePatStore);
  smokeLargePatStore.createFile = async request => {
    const result = await createLargePatFile(request);
    largePatRequests.create.push({ token: result.token, expectedLines: result.expectedLines });
    return result;
  };
  const discardLargePatFile = smokeLargePatStore.discard.bind(smokeLargePatStore);
  smokeLargePatStore.discard = async request => {
    const result = await discardLargePatFile(request);
    largePatRequests.discard.push({ token: request.token });
    return result;
  };
  const readLargePatChunk = smokeLargePatStore.readChunk.bind(smokeLargePatStore);
  smokeLargePatStore.readChunk = async request => {
    largePatReadStarted += 1;
    const delayMs = largePatReadDelayMs;
    if (delayMs > 0) await delay(delayMs);
    return readLargePatChunk(request);
  };
  registerLargePatHandlers(smokeLargePatStore);

  const window = new BrowserWindow({
    show: false,
    width: 1440,
    height: 900,
    minWidth: 1100,
    minHeight: 700,
    webPreferences: {
      preload,
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: true,
      webSecurity: true
    }
  });
  window.removeMenu();
  window.webContents.setWindowOpenHandler(() => ({ action: 'deny' }));
  window.webContents.on('console-message', details => {
    if (details && details.level === 'error') consoleErrors.push(details.message);
  });
  window.webContents.on('render-process-gone', (_event, details) => {
    consoleErrors.push(`renderer terminated: ${details.reason}`);
  });

  await window.loadFile(entry);
  await waitFor(
    () => window.webContents.executeJavaScript("Boolean(document.querySelector('#pat-generator-prototype'))"),
    '主界面加载'
  );
  await waitFor(
    () => window.webContents.executeJavaScript("document.querySelectorAll('svg.lucide').length > 0"),
    '本地图标加载'
  );

  currentStage = '检查初始界面';
  const initial = await window.webContents.executeJavaScript(`(() => ({
    title: document.title,
    memoryPressed: document.querySelector('#pat-memory-view').getAttribute('aria-pressed'),
    desktopApi: typeof window.desktopAPI?.saveFile,
    size: [window.innerWidth, window.innerHeight]
  }))()`);
  assert.equal(initial.title, 'PAT 生成工具');
  assert.equal(initial.memoryPressed, 'true');
  assert.equal(initial.desktopApi, 'function');

  currentStage = '切换 MEMORY/FUNC';
  const viewSwitch = await window.webContents.executeJavaScript(`(() => {
    document.querySelector('#pat-func-view').click();
    const funcVisible = !document.querySelector('#pat-func-config').hidden;
    document.querySelector('#pat-memory-view').click();
    return { funcVisible, memoryVisible: !document.querySelector('#pat-memory-config').hidden };
  })()`);
  assert.deepEqual(viewSwitch, { funcVisible: true, memoryVisible: true });

  currentStage = '检查器件类型与型号联动';
  const linkedModels = await window.webContents.executeJavaScript(`(() => {
    const type = document.querySelector('#pat-device-type');
    const model = document.querySelector('#pat-device-model');
    const visibleTypes = {};
    for (const value of ['SRAM', 'EEPROM', 'SPI_FLASH']) {
      type.value = value;
      type.dispatchEvent(new Event('change', { bubbles: true }));
      visibleTypes[value] = [...model.options]
        .filter(option => !option.hidden && !option.disabled)
        .map(option => option.dataset.deviceType);
    }
    return visibleTypes;
  })()`);
  for (const [type, models] of Object.entries(linkedModels)) {
    assert.ok(models.length > 0, `${type} 至少显示一个型号`);
    assert.ok(models.every(modelType => modelType === type), `${type} 不得显示其他类型型号`);
  }

  currentStage = '生成固定 23LC1024 SRAM PAT';
  await window.webContents.executeJavaScript(`(() => {
    const type = document.querySelector('#pat-device-type');
    const model = document.querySelector('#pat-device-model');
    type.value = 'SRAM';
    type.dispatchEvent(new Event('change', { bubbles: true }));
    model.value = '23LC1024';
    model.dispatchEvent(new Event('change', { bubbles: true }));
    document.querySelector('#pat-memory-view').click();
    document.querySelector('#pat-data-mode').value = 'mode1';
    document.querySelector('#pat-pattern').value = 'ALL 0';
    const bus = document.querySelector('#pat-memory-bus');
    bus.value = 'SPI';
    bus.dispatchEvent(new Event('change', { bubbles: true }));
    document.querySelector('#pat-start').value = '000000';
    document.querySelector('#pat-end').value = '000001';
    document.querySelector('#pat-generate').click();
  })()`);
  await waitFor(
    () => window.webContents.executeJavaScript("document.querySelector('#pat-file-name').textContent.startsWith('23LC1024_SPI_MEMORY_') && document.querySelector('#pat-generation-progress').hidden"),
    '固定 23LC1024 SRAM PAT',
    30000
  );
  await assertAndCloseGenerationSuccess(window, '固定 23LC1024 SRAM PAT');
  const fixedSram = await window.webContents.executeJavaScript(`(() => ({
    text: document.querySelector('#pat-output').innerText,
    filename: document.querySelector('#pat-file-name').textContent,
    structureHidden: document.querySelector('#pat-export-structure').hidden
  }))()`);
  assert.match(fixedSram.filename, /^23LC1024_SPI_MEMORY_/);
  assert.match(fixedSram.text, /\/\/ 23LC1024 SPI ALL 0 PAT/);
  assert.match(fixedSram.text, /HEAD\[PIN_NAME\]:\s*\nCS_N,\s*\nSO_IO1,\s*\nWP_IO2,\s*\nSI_IO0,\s*\nSCLK,\s*\nHOLD_IO3;/);
  assert.match(fixedSram.text, /无WREN、无擦除、无WIP或写等待/);
  assert.deepEqual(decodedCommands(fixedSram.text).map(command => command.opcode), [0x02, 0x03], '固定 SRAM SPI 必须且只能执行 WRITE 02h → READ 03h');
  const fixedSramReadSamples = taggedSampleVectors(findTransactionByTag(fixedSram.text, 'TX2', '固定 23LC1024 SRAM'), 'TX2:DATA-R');
  assert.equal(fixedSramReadSamples.length, 16, '固定 SRAM 必须逐 bit 比较两个读取字节');
  assert.ok(fixedSramReadSamples.every(vector => vector[4] === '1' && vector[1] === 'L' && vector[3] === 'X'), 'ALL 0 SRAM 读取必须在 SO/IO1 比较 L，并释放 SI/IO0');
  assert.equal(fixedSram.structureHidden, true, '固定 SRAM 不应冒充自定义结构说明');

  currentStage = '生成自定义 SRAM PAT 并验证 TX 快速定位';
  await window.webContents.executeJavaScript(`(() => {
    const model = document.querySelector('#pat-device-model');
    model.value = 'CUSTOM_SRAM';
    model.dispatchEvent(new Event('change', { bubbles: true }));
    document.querySelector('#pat-data-mode').value = 'mode1';
    document.querySelector('#pat-start').value = '000000';
    document.querySelector('#pat-end').value = '000000';
    document.querySelector('#pat-tx-count').value = '2';
    const command = document.querySelector('#pat-tx-command');
    command.value = 'WRITE';
    command.dispatchEvent(new Event('change', { bubbles: true }));
    const opcode = document.querySelector('#pat-opcode');
    opcode.value = '0A';
    opcode.dispatchEvent(new Event('input', { bubbles: true }));
    document.querySelector('#pat-generate').click();
  })()`);
  await waitFor(
    () => window.webContents.executeJavaScript("document.querySelector('#pat-file-name').textContent.startsWith('CUSTOM_SRAM_SPI_MEMORY_') && document.querySelector('#pat-generation-progress').hidden"),
    '自定义 SRAM PAT',
    30000
  );
  await assertAndCloseGenerationSuccess(window, '自定义 SRAM PAT');
  const customSram = await window.webContents.executeJavaScript(`(() => ({
    text: document.querySelector('#pat-output').innerText,
    structureVisible: !document.querySelector('#pat-export-structure').hidden,
    commandOptions: [...document.querySelector('#pat-tx-command').options].map(option => option.value)
  }))()`);
  assert.match(customSram.text, /\/\/ CUSTOM SRAM SPI ALL 0 PAT/);
  assert.deepEqual(customSram.commandOptions, ['WRITE', 'READ', 'EDIO', 'EQIO', 'RSTIO', 'WRMR', 'RDMR']);
  assert.deepEqual(decodedCommands(customSram.text).map(command => command.opcode), [0x0A, 0x03], '自定义 SRAM 必须采用用户修改后的 TX1 指令码并保留 TX2 READ');
  assert.equal(customSram.structureVisible, true, '自定义 SRAM 必须可导出结构说明');
  await window.webContents.executeJavaScript("document.querySelector('#pat-tx-locate').click()");
  await waitFor(
    () => window.webContents.executeJavaScript("document.querySelector('#pat-edit-state').textContent.includes('已定位到 TX1')"),
    '自定义 SRAM TX 快速定位'
  );
  const locatedTx = await window.webContents.executeJavaScript(`(() => {
    const hits = [...document.querySelectorAll('#pat-output .pat-tx-locate-hit')];
    return { count: hits.length, text: hits[0]?.textContent || '' };
  })()`);
  assert.equal(locatedTx.count, 1, '快速定位必须只高亮当前一条 TX');
  assert.match(locatedTx.text, /TX1 BEGIN：WRITE（0Ah）/);

  currentStage = '生成固定 24LC02B I2C EEPROM PAT';
  await window.webContents.executeJavaScript(`(() => {
    const type = document.querySelector('#pat-device-type');
    const model = document.querySelector('#pat-device-model');
    type.value = 'EEPROM';
    type.dispatchEvent(new Event('change', { bubbles: true }));
    model.value = '24LC02B';
    model.dispatchEvent(new Event('change', { bubbles: true }));
    document.querySelector('#pat-data-mode').value = 'mode1';
    document.querySelector('#pat-pattern').value = 'ALL 0';
    document.querySelector('#pat-eeprom-operation').value = 'page-write';
    document.querySelector('#pat-start').value = '00';
    document.querySelector('#pat-end').value = '07';
    document.querySelector('#pat-generate').click();
  })()`);
  await waitFor(
    () => window.webContents.executeJavaScript("document.querySelector('#pat-file-name').textContent.startsWith('24LC02B_I2C_MEMORY_') && document.querySelector('#pat-generation-progress').hidden"),
    '固定 24LC02B EEPROM PAT',
    30000
  );
  await assertAndCloseGenerationSuccess(window, '固定 24LC02B EEPROM PAT');
  const fixedEeprom = await window.webContents.executeJavaScript("document.querySelector('#pat-output').innerText");
  assert.match(fixedEeprom, /\/\/ 24LC02B PAGE_WRITE ALL 0 PAT/);
  assert.match(fixedEeprom, /HEAD\[PIN_NAME\]:\s*\nSDA,\s*\nSCL,\s*\nWP;/);
  assert.deepEqual(decodeI2cTaggedBytes(fixedEeprom, 'TX1', 'CONTROL', '24LC02B 写控制字节'), [0xA0]);
  assert.deepEqual(decodeI2cTaggedBytes(fixedEeprom, 'TX1', 'ADDR', '24LC02B 字地址'), [0x00]);
  assert.deepEqual(decodeI2cTaggedBytes(fixedEeprom, 'TX1', 'DATA-W', '24LC02B 页写模板'), [0x00]);
  assert.match(fixedEeprom, /^\s*000; LOOP 8;$/m, '8 个相同页写字节必须以无损 LOOP 8 表达');
  assert.match(fixedEeprom, /^\s*L10;.*\[TX1:ACK-DEV\]/m, '器件 ACK 必须由 ATE 在 SDA 比较 L');
  assert.match(fixedEeprom, /^\s*000; LOOP 6250;/m, '固定 EEPROM 写周期必须保留 LOOP 6250');

  currentStage = '生成自定义 EEPROM 页写与随机读 PAT';
  await window.webContents.executeJavaScript(`(() => {
    const model = document.querySelector('#pat-device-model');
    model.value = 'CUSTOM_EEPROM';
    model.dispatchEvent(new Event('change', { bubbles: true }));
    document.querySelector('#pat-address-width').value = '16';
    document.querySelector('#pat-page-size').value = '4';
    document.querySelector('#pat-eeprom-write-control').value = 'A4';
    document.querySelector('#pat-eeprom-read-control').value = 'A5';
    document.querySelector('#pat-eeprom-wait-loop').value = '123';
    document.querySelector('#pat-eeprom-operation').value = 'page-write';
    document.querySelector('#pat-start').value = '0010';
    document.querySelector('#pat-end').value = '0011';
    document.querySelector('#pat-generate').click();
  })()`);
  await waitFor(
    () => window.webContents.executeJavaScript("document.querySelector('#pat-file-name').textContent.startsWith('CUSTOM_EEPROM_I2C_MEMORY_') && document.querySelector('#pat-generation-progress').hidden"),
    '自定义 EEPROM 页写 PAT',
    30000
  );
  await assertAndCloseGenerationSuccess(window, '自定义 EEPROM 页写 PAT');
  const customEepromWrite = await window.webContents.executeJavaScript(`(() => ({
    text: document.querySelector('#pat-output').innerText,
    structureVisible: !document.querySelector('#pat-export-structure').hidden
  }))()`);
  assert.match(customEepromWrite.text, /\/\/ CUSTOM EEPROM PAGE_WRITE ALL 0 PAT/);
  assert.deepEqual(decodeI2cTaggedBytes(customEepromWrite.text, 'TX1', 'CONTROL', '自定义 EEPROM 写控制字节'), [0xA4]);
  assert.deepEqual(decodeI2cTaggedBytes(customEepromWrite.text, 'TX1', 'ADDR', '自定义 EEPROM 16-bit 字地址'), [0x00, 0x10]);
  assert.match(customEepromWrite.text, /^\s*000; LOOP 123;/m, '自定义 EEPROM 必须采用用户配置的写等待');
  assert.equal(customEepromWrite.structureVisible, true, '自定义 EEPROM 必须可导出结构说明');

  await window.webContents.executeJavaScript(`(() => {
    document.querySelector('#pat-eeprom-operation').value = 'random-read';
    document.querySelector('#pat-end').value = '0010';
    document.querySelector('#pat-generate').click();
  })()`);
  await waitFor(
    () => window.webContents.executeJavaScript("document.querySelector('#pat-file-name').textContent.includes('_RANDOM_READ_') && document.querySelector('#pat-generation-progress').hidden"),
    '自定义 EEPROM 随机读 PAT',
    30000
  );
  await assertAndCloseGenerationSuccess(window, '自定义 EEPROM 随机读 PAT');
  const customEepromRead = await window.webContents.executeJavaScript("document.querySelector('#pat-output').innerText");
  assert.deepEqual(decodeI2cTaggedBytes(customEepromRead, 'TX1', 'CONTROL', '自定义 EEPROM 随机读控制字节'), [0xA4, 0xA5]);
  assert.deepEqual(decodeI2cTaggedBytes(customEepromRead, 'TX1', 'ADDR', '自定义 EEPROM 随机读地址'), [0x00, 0x10]);
  assert.match(customEepromRead, /\[TX1:RESTART\] Repeated START/);
  assert.match(customEepromRead, /\[TX1:NACK-HOST\]/, '随机读末字节必须以主机 NACK 结束');
  assert.doesNotMatch(customEepromRead, /LOOP 123;/, '纯随机读不得错误插入写周期等待');

  currentStage = '拒绝会丢失地址位的串行存储器宽度';
  await window.webContents.executeJavaScript(`(() => {
    const type = document.querySelector('#pat-device-type');
    const model = document.querySelector('#pat-device-model');
    type.value = 'SRAM';
    type.dispatchEvent(new Event('change', { bubbles: true }));
    model.value = 'CUSTOM_SRAM';
    model.dispatchEvent(new Event('change', { bubbles: true }));
    document.querySelector('#pat-memory-bus').value = 'SDI';
    document.querySelector('#pat-address-width').value = '23';
    document.querySelector('#pat-start').value = '000000';
    document.querySelector('#pat-end').value = '000000';
    document.querySelector('#pat-generate').click();
  })()`);
  await waitFor(
    () => window.webContents.executeJavaScript("document.querySelector('#pat-generation-progress').hidden && document.querySelector('#pat-file-meta').textContent.includes('必须能被 2 整除')"),
    'SRAM SDI 非整除地址宽度拦截'
  );
  await assertGenerationSuccessClosed(window, 'SRAM SDI 非整除地址宽度');
  await window.webContents.executeJavaScript(`(() => {
    const bus = document.querySelector('#pat-memory-bus');
    bus.value = 'SPI';
    bus.dispatchEvent(new Event('change', { bubbles: true }));
    document.querySelector('#pat-address-width').value = '23';
    document.querySelector('#pat-tx-count').value = '2';
    document.querySelector('#pat-tx-count').dispatchEvent(new Event('input', { bubbles: true }));
    const command = document.querySelector('#pat-tx-command');
    command.value = 'EQIO';
    command.dispatchEvent(new Event('change', { bubbles: true }));
    document.querySelector('[data-tx-step="1"]').click();
    command.value = 'WRITE';
    command.dispatchEvent(new Event('change', { bubbles: true }));
    document.querySelector('#pat-generate').click();
  })()`);
  await waitFor(
    () => window.webContents.executeJavaScript("document.querySelector('#pat-generation-progress').hidden && document.querySelector('#pat-file-meta').textContent.includes('必须能被 4 整除')"),
    'SRAM TX 内切 SQI 非整除地址宽度拦截'
  );
  await assertGenerationSuccessClosed(window, 'SRAM TX 内切 SQI 非整除地址宽度');
  await window.webContents.executeJavaScript(`(() => {
    const type = document.querySelector('#pat-device-type');
    const model = document.querySelector('#pat-device-model');
    type.value = 'EEPROM';
    type.dispatchEvent(new Event('change', { bubbles: true }));
    model.value = 'CUSTOM_EEPROM';
    model.dispatchEvent(new Event('change', { bubbles: true }));
    document.querySelector('#pat-address-width').value = '12';
    document.querySelector('#pat-start').value = '000';
    document.querySelector('#pat-end').value = '000';
    document.querySelector('#pat-generate').click();
  })()`);
  await waitFor(
    () => window.webContents.executeJavaScript("document.querySelector('#pat-generation-progress').hidden && document.querySelector('#pat-file-meta').textContent.includes('必须是 8、16 或 24 bit')"),
    'EEPROM 非字节整数地址宽度拦截'
  );
  await assertGenerationSuccessClosed(window, 'EEPROM 非字节整数地址宽度');

  currentStage = '生成固定 SPI Flash MEMORY PAT';
  await window.webContents.executeJavaScript(`(() => {
    const type = document.querySelector('#pat-device-type');
    const model = document.querySelector('#pat-device-model');
    type.value = 'SPI_FLASH';
    type.dispatchEvent(new Event('change', { bubbles: true }));
    model.value = 'BY25Q40ALTIG';
    model.dispatchEvent(new Event('change', { bubbles: true }));
    const bus = document.querySelector('#pat-memory-bus');
    bus.value = 'SPI';
    bus.dispatchEvent(new Event('change', { bubbles: true }));
    document.querySelector('#pat-start').value = '000000';
    document.querySelector('#pat-end').value = '00000F';
    document.querySelector('#pat-generate').click();
  })()`);
  await waitFor(
    () => window.webContents.executeJavaScript("Boolean(document.querySelector('#pat-generator-prototype').dataset.patLineCount) && document.querySelector('#pat-generation-progress').hidden"),
    '固定 MEMORY PAT 异步生成',
    30000
  );
  await assertAndCloseGenerationSuccess(window, '固定 MEMORY PAT');
  const fixedMemory = await window.webContents.executeJavaScript(`(() => ({
      text: document.querySelector('#pat-output').innerText,
      filename: document.querySelector('#pat-file-name').textContent,
      exportDisabled: document.querySelector('#pat-export').disabled
    }))()`);
  assert.match(fixedMemory.text, /@@PATTERN_DEFINE/);
  assert.doesNotMatch(fixedMemory.text, /生成失败/);
  assert.match(fixedMemory.filename, /^BY25Q40ALTIG_.*\.pat$/);
  assert.equal(fixedMemory.exportDisabled, false);
  assert.equal(fixedMemory.text.length, 33462, '默认固定 SPI 小样本字符数必须保持公开回归稳定');
  assert.equal(
    crypto.createHash('sha256').update(fixedMemory.text, 'utf8').digest('hex').toUpperCase(),
    'DACF4E4AC1FCDFD94326CFA1FF4BAFEF844E31E70245204A22626B45943FD60A',
    '默认固定 SPI 小样本 PAT 必须保持公开回归稳定'
  );

  currentStage = '配置与视图变化不得自动替换 MEMORY PAT';
  const explicitMemorySnapshot = await readPatSnapshot(window);
  await window.webContents.executeJavaScript(`(() => {
    const setInput = (selector, value) => {
      const input = document.querySelector(selector);
      input.value = value;
      input.dispatchEvent(new Event('input', { bubbles: true }));
    };
    setInput('#pat-start', '000001');
    setInput('#pat-end', '000002');
    document.querySelector('#pat-address-bin').click();
    document.querySelector('#pat-address-hex').click();
    const memoryBus = document.querySelector('#pat-memory-bus');
    memoryBus.value = 'SDI';
    memoryBus.dispatchEvent(new Event('change', { bubbles: true }));
    const mode = document.querySelector('#pat-data-mode');
    mode.value = 'mode2';
    mode.dispatchEvent(new Event('change', { bubbles: true }));
    const model = document.querySelector('#pat-device-model');
    model.value = 'GD25Q40CTIG';
    model.dispatchEvent(new Event('change', { bubbles: true }));

    document.querySelector('#pat-func-view').click();
    document.querySelector('[data-func-panel="voh"]').click();
    setInput('#func-voh-address', '000001');
    const vohBus = document.querySelector('#func-voh-bus');
    vohBus.value = 'SDI';
    vohBus.dispatchEvent(new Event('change', { bubbles: true }));
    document.querySelector('[data-func-panel="vol"]').click();
    setInput('#func-vol-address', '000002');
    const volBus = document.querySelector('#func-vol-bus');
    volBus.value = 'SPI';
    volBus.dispatchEvent(new Event('change', { bubbles: true }));
    document.querySelector('[data-func-panel="icc"]').click();
    setInput('#func-icc-address', '000003');
    const iccMode = document.querySelector('input[name="func-icc-mode"][value="program"]');
    iccMode.checked = true;
    iccMode.dispatchEvent(new Event('change', { bubbles: true }));
    document.querySelector('[data-func-panel="rw"]').click();
    setInput('#func-rw-data', '5A');
    setInput('#func-start-address', '000000');
    setInput('#func-end-address', '000000');
    const rwBus = document.querySelector('input[name="func-rw-bus"][value="SPI"]');
    rwBus.checked = true;
    rwBus.dispatchEvent(new Event('change', { bubbles: true }));
    document.querySelector('#pat-memory-view').click();
    document.querySelector('#pat-func-view').click();
  })()`);
  await delay(850);
  assertPatSnapshotUnchanged(
    await readPatSnapshot(window),
    explicitMemorySnapshot,
    '地址、HEX/BIN、总线、模式、型号、MEMORY/FUNC视图及FUNC配置变化'
  );

  currentStage = '仅点击生成 FUNC PAT 才替换 MEMORY PAT';
  await window.webContents.executeJavaScript("document.querySelector('#pat-func-generate').click()");
  await waitFor(
    () => window.webContents.executeJavaScript("document.querySelector('#pat-file-name').textContent.startsWith('GD25Q40CTIG_SPI_FUNC_WRITE_READ_') && document.querySelector('#pat-generation-progress').hidden"),
    '显式 FUNC PAT 生成',
    30000
  );
  await assertAndCloseGenerationSuccess(window, '显式 FUNC PAT');
  const explicitFuncSnapshot = await readPatSnapshot(window);
  assert.notEqual(explicitFuncSnapshot.text, explicitMemorySnapshot.text, '点击 FUNC 生成按钮后才允许替换 PAT 文本');
  assert.notEqual(explicitFuncSnapshot.filename, explicitMemorySnapshot.filename, '点击 FUNC 生成按钮后才允许替换文件名');
  assert.match(explicitFuncSnapshot.filename, /^GD25Q40CTIG_SPI_FUNC_WRITE_READ_/);
  assert.match(explicitFuncSnapshot.validation, /FUNC PAT/);
  assert.match(explicitFuncSnapshot.validation, /RW/);

  currentStage = 'FUNC配置与返回MEMORY不得自动替换 FUNC PAT';
  await window.webContents.executeJavaScript(`(() => {
    const setInput = (selector, value) => {
      const input = document.querySelector(selector);
      input.value = value;
      input.dispatchEvent(new Event('input', { bubbles: true }));
    };
    setInput('#func-rw-data', 'A5');
    setInput('#func-end-address', '000001');
    const rwBus = document.querySelector('input[name="func-rw-bus"][value="SDI"]');
    rwBus.checked = true;
    rwBus.dispatchEvent(new Event('change', { bubbles: true }));
    document.querySelector('[data-func-panel="vol"]').click();
    setInput('#func-vol-address', '000004');
    const volBus = document.querySelector('#func-vol-bus');
    volBus.value = 'SDI';
    volBus.dispatchEvent(new Event('change', { bubbles: true }));
    document.querySelector('#pat-func-reset').click();
  })()`);
  await delay(850);
  assertPatSnapshotUnchanged(
    await readPatSnapshot(window),
    explicitFuncSnapshot,
    'FUNC数据、地址、总线、类别及FUNC重置变化'
  );

  await window.webContents.executeJavaScript(`(() => {
    document.querySelector('#pat-memory-view').click();
    const setInput = (selector, value) => {
      const input = document.querySelector(selector);
      input.value = value;
      input.dispatchEvent(new Event('input', { bubbles: true }));
    };
    const mode = document.querySelector('#pat-data-mode');
    mode.value = 'mode1';
    mode.dispatchEvent(new Event('change', { bubbles: true }));
    document.querySelector('#pat-pattern').value = 'ALL 1';
    const bus = document.querySelector('#pat-memory-bus');
    bus.value = 'SPI';
    bus.dispatchEvent(new Event('change', { bubbles: true }));
    setInput('#pat-start', '000001');
    setInput('#pat-end', '000001');
  })()`);
  await delay(850);
  assertPatSnapshotUnchanged(
    await readPatSnapshot(window),
    explicitFuncSnapshot,
    '返回MEMORY并修改MEMORY配置'
  );

  currentStage = '返回 MEMORY 后仅点击生成按钮才替换 FUNC PAT';
  await window.webContents.executeJavaScript("document.querySelector('#pat-generate').click()");
  await waitFor(
    () => window.webContents.executeJavaScript("document.querySelector('#pat-file-name').textContent.startsWith('GD25Q40CTIG_SPI_MEMORY_') && document.querySelector('#pat-generation-progress').hidden"),
    '返回 MEMORY 后显式生成',
    30000
  );
  await assertAndCloseGenerationSuccess(window, '返回 MEMORY 后显式生成');
  const regeneratedMemorySnapshot = await readPatSnapshot(window);
  assert.notEqual(regeneratedMemorySnapshot.text, explicitFuncSnapshot.text, '点击 MEMORY 生成按钮后才允许替换 FUNC PAT 文本');
  assert.notEqual(regeneratedMemorySnapshot.filename, explicitFuncSnapshot.filename, '点击 MEMORY 生成按钮后才允许替换 FUNC PAT 文件名');
  assert.match(regeneratedMemorySnapshot.filename, /^GD25Q40CTIG_SPI_MEMORY_ALL_1_/);
  assert.doesNotMatch(regeneratedMemorySnapshot.validation, /FUNC PAT/);

  currentStage = '生成自定义 SPI Flash MEMORY PAT';
  await window.webContents.executeJavaScript(`(() => {
    const model = document.querySelector('#pat-device-model');
    model.value = 'CUSTOM';
    model.dispatchEvent(new Event('change', { bubbles: true }));
    document.querySelector('#pat-start').value = '000000';
    document.querySelector('#pat-end').value = '00000F';
    document.querySelector('#pat-generate').click();
  })()`);
  await waitFor(
    () => window.webContents.executeJavaScript("document.querySelector('#pat-file-name').textContent.startsWith('CUSTOM_') && document.querySelector('#pat-generation-progress').hidden"),
    '自定义 MEMORY PAT 异步生成',
    30000
  );
  await assertAndCloseGenerationSuccess(window, '自定义 MEMORY PAT');
  const customMemory = await window.webContents.executeJavaScript(`(() => ({
      text: document.querySelector('#pat-output').innerText,
      structureVisible: !document.querySelector('#pat-export-structure').hidden,
      filename: document.querySelector('#pat-file-name').textContent
    }))()`);
  assert.match(customMemory.text, /@@PATTERN_DEFINE/);
  assert.doesNotMatch(customMemory.text, /生成失败/);
  assert.equal(customMemory.structureVisible, true);
  assert.match(customMemory.filename, /^CUSTOM_.*\.pat$/);

  currentStage = '执行 PAT 整列替换';
  await window.webContents.executeJavaScript(`(() => {
    document.querySelector('#pat-column-number').value = '1';
    document.querySelector('#pat-column-char').value = 'X';
    document.querySelector('#pat-column-apply').click();
  })()`);
  await waitFor(
    () => window.webContents.executeJavaScript("document.querySelector('#pat-column-status').textContent.startsWith('已将第') && document.querySelector('#pat-generation-progress').hidden"),
    'PAT 整列替换完成',
    30000
  );
  const columnReplacement = await window.webContents.executeJavaScript(`(() => {
    const text = document.querySelector('#pat-output').innerText;
    const vectors = text.match(/^\\s*(?:start:\\s+|end:\\s+)?[01HLXZ]{6};/gm) || [];
    return { count: vectors.length, allReplaced: vectors.every(line => /^(?:\\s*(?:start:\\s+|end:\\s+)?)X/.test(line)) };
  })()`);
  assert.ok(columnReplacement.count > 0);
  assert.equal(columnReplacement.allReplaced, true);

  currentStage = '验证同tick切换校验页不丢失手工编辑及保存内容';
  saveRequests.length = 0;
  nextSaveResult = { ok: true, canceled: false, fileName: '已编辑.pat' };
  const editTabRoundTrip = await window.webContents.executeJavaScript(`(() => {
    const output = document.querySelector('#pat-output');
    output.textContent = '// 用户当前编辑内容\\nX00000;';
    output.dispatchEvent(new InputEvent('input', { bubbles: true, inputType: 'insertText' }));
    document.querySelector('.pat-tab[data-tab="validation"]').click();
    const validationText = output.innerText;
    document.querySelector('.pat-tab[data-tab="preview"]').click();
    const previewText = output.innerText;
    document.querySelector('#pat-export').click();
    return { validationText, previewText };
  })()`);
  assert.match(editTabRoundTrip.validationText, /PAT/);
  assert.ok(editTabRoundTrip.previewText.includes('// 用户当前编辑内容'));
  assert.match(editTabRoundTrip.previewText, /X00000;/);
  await waitFor(() => saveRequests.length === 1, 'PAT 保存 IPC');
  assert.equal(saveRequests[0].kind, 'pat');
  assert.equal(saveRequests[0].extension, '.pat');
  assert.equal(saveRequests[0].content, '// 用户当前编辑内容\nX00000;\n');

  currentStage = '验证取消保存';
  nextSaveResult = { ok: false, canceled: true };
  await window.webContents.executeJavaScript("document.querySelector('#pat-export').click()");
  await waitFor(
    () => window.webContents.executeJavaScript("document.querySelector('#pat-file-meta').textContent === '已取消导出'"),
    '取消保存状态'
  );

  currentStage = '验证结构说明 TXT 保存';
  saveRequests.length = 0;
  nextSaveResult = { ok: true, canceled: false, fileName: '结构说明.txt' };
  await window.webContents.executeJavaScript(`(() => {
    document.querySelector('#pat-memory-view').click();
    document.querySelector('#pat-device-model').value = 'CUSTOM';
    document.querySelector('#pat-device-model').dispatchEvent(new Event('change', { bubbles: true }));
    document.querySelector('#pat-start').value = '000000';
    document.querySelector('#pat-end').value = '00000F';
    document.querySelector('#pat-generate').click();
  })()`);
  await waitFor(
    () => window.webContents.executeJavaScript("document.querySelector('#pat-file-name').textContent.startsWith('CUSTOM_') && document.querySelector('#pat-generation-progress').hidden"),
    'TXT 对应 PAT 生成',
    30000
  );
  await assertAndCloseGenerationSuccess(window, 'TXT 对应 PAT');
  const structureSnapshot = await window.webContents.executeJavaScript(`(() => {
    const before = {
      patFilename: document.querySelector('#pat-file-name').textContent,
      structureFilename: document.querySelector('#pat-structure-file-name').textContent
    };
    const model = document.querySelector('#pat-device-model');
    model.value = 'BY25Q40ALTIG';
    model.dispatchEvent(new Event('change', { bubbles: true }));
    const after = {
      patFilename: document.querySelector('#pat-file-name').textContent,
      structureFilename: document.querySelector('#pat-structure-file-name').textContent
    };
    document.querySelector('#pat-export-structure').click();
    return { before, after };
  })()`);
  assert.deepEqual(structureSnapshot.after, structureSnapshot.before, '切到固定型号不得改写上一份CUSTOM PAT及结构TXT文件名');
  assert.match(structureSnapshot.before.patFilename, /^CUSTOM_/);
  assert.match(structureSnapshot.before.structureFilename, /^CUSTOM_.*PAT结构说明\.txt$/);
  await waitFor(() => saveRequests.length === 1 && saveRequests[0].kind === 'txt', '切换固定型号后的TXT保存 IPC');
  const txtRequest = saveRequests[0];
  assert.equal(txtRequest.extension, '.txt');
  assert.equal(txtRequest.suggestedName, structureSnapshot.before.structureFilename);
  assert.match(txtRequest.content, /PAT结构说明/);
  assert.match(txtRequest.content, /^自定义器件 MEMORY PAT结构说明/m);
  assert.equal(/(^|[^\r])\n/.test(txtRequest.content), false);

  currentStage = '生成固定 SPI Flash FUNC PAT';
  await window.webContents.executeJavaScript(`(() => {
    const model = document.querySelector('#pat-device-model');
    model.value = 'BY25Q40ALTIG';
    model.dispatchEvent(new Event('change', { bubbles: true }));
    document.querySelector('#pat-func-view').click();
    document.querySelector('[data-func-panel="voh"]').click();
    document.querySelector('#pat-func-generate').click();
  })()`);
  await waitFor(
    () => window.webContents.executeJavaScript("document.querySelector('#pat-file-name').textContent.includes('_VOH_TEST.pat') && document.querySelector('#pat-generation-progress').hidden"),
    '固定 FUNC PAT 异步生成',
    30000
  );
  await assertAndCloseGenerationSuccess(window, '固定 FUNC PAT');
  const func = await window.webContents.executeJavaScript("document.querySelector('#pat-output').innerText");
  assert.match(func, /FUNC/);
  assert.match(func, /@@PATTERN_DEFINE/);
  assert.doesNotMatch(func, /生成失败/);

  const classADualModels = ['BY25Q40ALTIG', 'BY25Q16BL', 'BY25Q80AL'];
  const classBDualModels = ['BY25Q16ESOIG', 'BY25Q80ES', 'GD25LQ40E', 'GD25Q40CTIG', 'W25Q40CLSNIG', 'W25Q64JVSSIQ'];
  const funcWipLoops = {
    BY25Q40ALTIG: 25000,
    BY25Q16BL: 25000,
    BY25Q16ESOIG: 65535,
    BY25Q80AL: 25000,
    BY25Q80ES: 50000,
    GD25LQ40E: 50000,
    GD25Q40CTIG: 50000,
    MX25U4033EM: 50000,
    W25Q40CLSNIG: 50000,
    W25Q64JVSSIQ: 65535
  };
  for (const modelName of classADualModels) {
    for (const kind of ['memory', 'func']) {
      const fullPageFunc = kind === 'func' && modelName === 'BY25Q40ALTIG';
      const generated = await generateFixedPat(window, {
        modelName,
        bus: 'SDI',
        kind,
        funcEndAddress: fullPageFunc ? '0000FF' : '000000',
        funcData: fullPageFunc ? 'AA 55' : 'A5',
        captureExport: fullPageFunc
      });
      const label = `${modelName} SDI ${kind.toUpperCase()}`;
      const programBlock = assertProgramTransaction(generated.text, {
        opcode: 0xA2,
        title: /^Dual Page Program（A2h）/,
        addressBus: 'SPI',
        dataBus: 'SDI',
        dataBytes: fullPageFunc ? 256 : 1
      }, label);
      const readBlock = assertReadTransaction(generated.text, {
        opcode: 0x3B,
        title: /^Fast Read Dual Output（3Bh）/,
        addressBus: 'SPI',
        dataBus: 'SDI',
        dummy: 8,
        dataBytes: fullPageFunc ? 256 : 1
      }, label);
      if (kind === 'func') {
        assertFuncRwPolling(generated.text, funcWipLoops[modelName], label);
        assert.doesNotMatch(programBlock.body, /\bLOOP\b/, `${label}数据写入必须全部展开`);
        if (fullPageFunc) assertFullPageFuncData(programBlock, readBlock, 'SDI', label);
      }
    }
  }

  for (const modelName of classBDualModels) {
    for (const kind of ['memory', 'func']) {
      const fullPageFunc = kind === 'func' && modelName === 'GD25Q40CTIG';
      const generated = await generateFixedPat(window, {
        modelName,
        bus: 'SDI',
        kind,
        funcEndAddress: fullPageFunc ? '0000FF' : '000000',
        funcData: fullPageFunc ? 'AA 55' : 'A5',
        captureExport: fullPageFunc
      });
      const label = `${modelName} SDI ${kind.toUpperCase()}`;
      const programBlock = assertProgramTransaction(generated.text, {
        opcode: 0x02,
        title: /^Page Program（02h）/,
        addressBus: 'SPI',
        dataBus: 'SPI',
        dataBytes: fullPageFunc ? 256 : 1
      }, label);
      const readBlock = assertReadTransaction(generated.text, {
        opcode: 0x3B,
        title: /^Fast Read Dual Output（3Bh）/,
        addressBus: 'SPI',
        dataBus: 'SDI',
        dummy: 8,
        dataBytes: fullPageFunc ? 256 : 1
      }, label);
      if (kind === 'func') {
        assertFuncRwPolling(generated.text, funcWipLoops[modelName], label);
        assert.doesNotMatch(programBlock.body, /\bLOOP\b/, `${label}数据写入必须全部展开`);
        if (fullPageFunc) assertFullPageFuncData(programBlock, readBlock, 'SPI', label);
      }
    }
  }

  for (const kind of ['memory', 'func']) {
    const generated = await generateFixedPat(window, { modelName: 'MX25U4033EM', bus: 'SDI', kind });
    const label = `MX25U4033EM SDI ${kind.toUpperCase()}`;
    assertMxNonvolatileQeClear(generated.text, label);
    const programBlock = assertProgramTransaction(generated.text, {
      opcode: 0x02,
      title: /^Page Program（02h）/,
      addressBus: 'SPI',
      dataBus: 'SPI'
    }, label);
    assertReadTransaction(generated.text, {
      opcode: 0xBB,
      title: /^2READ（BBh）/,
      addressBus: 'SDI',
      dataBus: 'SDI',
      dummy: 4
    }, label);
    if (kind === 'func') {
      assertFuncRwPolling(generated.text, funcWipLoops.MX25U4033EM, label);
      assert.doesNotMatch(programBlock.body, /\bLOOP\b/, `${label}数据写入必须全部展开`);
    }
  }

  for (const kind of ['memory', 'func']) {
    const generated = await generateFixedPat(window, { modelName: 'MX25U4033EM', bus: 'SQI', kind });
    const label = `MX25U4033EM SQI ${kind.toUpperCase()}`;
    assertMxNonvolatileQeSet(generated.text, label);
    assertProgramTransaction(generated.text, {
      opcode: 0x38,
      title: /^4 x I\/O Page Program（38h）/,
      addressBus: 'SQI',
      dataBus: 'SQI'
    }, label);
    assertReadTransaction(generated.text, {
      opcode: 0xEB,
      title: /^4 x I\/O Read（EBh）/,
      addressBus: 'SQI',
      dataBus: 'SQI',
      dummy: 4,
      performanceFf: true
    }, label);
    const opcode38 = decodedCommands(generated.text).filter(command => command.opcode === 0x38);
    assert.equal(opcode38.length, 1, `${label}必须且只能发送一次实际 38h 命令`);
    assert.ok(opcode38.every(command => /4 x I\/O Page Program|4PP/.test(command.title)), `${label}不得把实际 38h 命令当成 Enter QPI`);
  }

  const volCases = [
    { modelName: 'W25Q40CLSNIG', opcode: 0x02, title: /^Page Program（02h）/, dataBus: 'SPI', readOpcode: 0x3B, readTitle: /^Fast Read Dual Output（3Bh）/, readAddressBus: 'SPI', readDummy: 8 },
    { modelName: 'GD25Q40CTIG', opcode: 0x02, title: /^Page Program（02h）/, dataBus: 'SPI', readOpcode: 0x3B, readTitle: /^Fast Read Dual Output（3Bh）/, readAddressBus: 'SPI', readDummy: 8 },
    { modelName: 'BY25Q16ESOIG', opcode: 0x02, title: /^Page Program（02h）/, dataBus: 'SPI', readOpcode: 0x3B, readTitle: /^Fast Read Dual Output（3Bh）/, readAddressBus: 'SPI', readDummy: 8 },
    { modelName: 'BY25Q80ES', opcode: 0x02, title: /^Page Program（02h）/, dataBus: 'SPI', readOpcode: 0x3B, readTitle: /^Fast Read Dual Output（3Bh）/, readAddressBus: 'SPI', readDummy: 8, exactSingleWireVol: true },
    { modelName: 'BY25Q40ALTIG', opcode: 0xA2, title: /^Dual Page Program（A2h）/, dataBus: 'SDI', readOpcode: 0x3B, readTitle: /^Fast Read Dual Output（3Bh）/, readAddressBus: 'SPI', readDummy: 8 },
    { modelName: 'GD25LQ40E', opcode: 0x02, title: /^Page Program（02h）/, dataBus: 'SPI', readOpcode: 0x3B, readTitle: /^Fast Read Dual Output（3Bh）/, readAddressBus: 'SPI', readDummy: 8, exactSingleWireVol: true },
    { modelName: 'MX25U4033EM', opcode: 0x02, title: /^Page Program（02h）/, dataBus: 'SPI', readOpcode: 0xBB, readTitle: /^2READ（BBh）/, readAddressBus: 'SDI', readDummy: 4, exactSingleWireVol: true, mxNonvolatileQeClear: true },
    { modelName: 'W25Q64JVSSIQ', opcode: 0x02, title: /^Page Program（02h）/, dataBus: 'SPI', readOpcode: 0x3B, readTitle: /^Fast Read Dual Output（3Bh）/, readAddressBus: 'SPI', readDummy: 8, exactSingleWireVol: true }
  ];
  currentStage = '验证既有 SDI VOL 流程不受固定 MEMORY/FUNC 分类修改影响';
  for (const { modelName, opcode, title, dataBus, readOpcode, readTitle, readAddressBus, readDummy, exactSingleWireVol, mxNonvolatileQeClear } of volCases) {
    await window.webContents.executeJavaScript(`(() => {
      const model = document.querySelector('#pat-device-model');
      model.value = '${modelName}';
      model.dispatchEvent(new Event('change', { bubbles: true }));
      document.querySelector('#pat-func-view').click();
      document.querySelector('[data-func-panel="vol"]').click();
      const bus = document.querySelector('#func-vol-bus');
      bus.value = 'SDI';
      bus.dispatchEvent(new Event('change', { bubbles: true }));
      document.querySelector('#func-vol-address').value = '000000';
      document.querySelector('#pat-func-generate').click();
    })()`);
    await waitFor(
      () => window.webContents.executeJavaScript(`document.querySelector('#pat-file-name').textContent === '${modelName}_SDI_VOL_TEST.pat' && document.querySelector('#pat-generation-progress').hidden`),
      `${modelName} SDI VOL PAT 生成`,
      30000
    );
    await assertAndCloseGenerationSuccess(window, `${modelName} SDI VOL PAT`);
    const dualVol = await window.webContents.executeJavaScript(`(() => {
      const text = document.querySelector('#pat-output').innerText;
      return {
        filename: document.querySelector('#pat-file-name').textContent,
        text
      };
    })()`);
    assert.equal(dualVol.filename, `${modelName}_SDI_VOL_TEST.pat`);
    if (mxNonvolatileQeClear) assertMxNonvolatileQeClear(dualVol.text, `${modelName} SDI VOL`, false);
    const programBlock = assertProgramTransaction(dualVol.text, {
      opcode,
      title,
      addressBus: 'SPI',
      dataBus
    }, `${modelName} SDI VOL`);
    const readBlock = assertReadTransaction(dualVol.text, {
      opcode: readOpcode,
      title: readTitle,
      addressBus: readAddressBus,
      dataBus: 'SDI',
      dummy: readDummy
    }, `${modelName} SDI VOL`);
    if (exactSingleWireVol) {
      assert.deepEqual(
        taggedSampleVectors(programBlock, `${programBlock.tag}:DATA-IN`),
        Array(8).fill('0X1011'),
        `${modelName} SDI VOL 的 00h 数据必须用 8 个 SPI 单线实际时钟发送`
      );
      assert.deepEqual(
        taggedSampleVectors(readBlock, `${readBlock.tag}:DATA-OUT`),
        Array(4).fill('0L1L11'),
        `${modelName} SDI VOL 的 00h 回读必须用 4 个 SDI 双线实际比较时钟`
      );
    }
    if (modelName === 'GD25LQ40E') {
      assert.match(dualVol.text, /随后3Bh命令和24-bit地址仍由SI\/IO0单线发送，仅数据阶段由IO1\/IO0双线输出。/);
    }
    if (modelName === 'MX25U4033EM') {
      assert.match(dualVol.text, /随后BBh命令仍由SI\/IO0单线发送，24-bit地址和数据阶段由IO1\/IO0双线传输。/);
    }
    assert.match(dualVol.text, /^end:\s+0L1L11;/m);
  }

  currentStage = '生成约 50 万行 PAT 并验证界面持续响应';
  await window.webContents.executeJavaScript(`(() => {
    document.querySelector('#pat-memory-view').click();
    const type = document.querySelector('#pat-device-type');
    const model = document.querySelector('#pat-device-model');
    type.value = 'SPI_FLASH';
    type.dispatchEvent(new Event('change', { bubbles: true }));
    model.value = 'BY25Q40ALTIG';
    model.dispatchEvent(new Event('change', { bubbles: true }));
    document.querySelector('#pat-data-mode').value = 'mode1';
    document.querySelector('#pat-pattern').value = 'ALL 0';
    document.querySelector('#pat-memory-bus').value = 'SPI';
    document.querySelector('#pat-start').value = '000000';
    document.querySelector('#pat-end').value = '002FFF';
    window.__patHeartbeat = 0;
    window.__patStartedAt = performance.now();
    window.__patHeartbeatTimer = setInterval(() => { window.__patHeartbeat += 1; }, 10);
    document.querySelector('#pat-generate').click();
  })()`);
  await waitFor(
    () => window.webContents.executeJavaScript("Number(document.querySelector('#pat-generator-prototype').dataset.patLineCount) > 500000 && document.querySelector('#pat-generation-progress').hidden"),
    '50 万行 PAT 完成且没有卡死',
    120000
  );
  await assertAndCloseGenerationSuccess(window, '50 万行 PAT');
  const largePat = await window.webContents.executeJavaScript(`(() => {
    clearInterval(window.__patHeartbeatTimer);
    const root = document.querySelector('#pat-generator-prototype');
    const output = document.querySelector('#pat-output');
    return {
      totalLines: Number(root.dataset.patLineCount),
      windowed: root.dataset.previewWindowed,
      heartbeat: window.__patHeartbeat,
      elapsed: performance.now() - window.__patStartedAt,
      renderedLines: output.textContent.split('\\n').length,
      renderedElementNodes: output.childElementCount,
      controlsVisible: !document.querySelector('#pat-large-preview-controls').hidden,
      readOnly: output.contentEditable === 'false'
    };
  })()`);
  assert.equal(largePat.totalLines, 521237, '50 万行公开回归配置的行数不得改变');
  assert.equal(largePat.windowed, 'true');
  assert.ok(largePat.heartbeat > 10, '生成期间事件循环必须持续响应');
  assert.ok(largePat.elapsed < 5000, `50 万行生成耗时应小于 5 秒，实际 ${largePat.elapsed.toFixed(1)} ms`);
  assert.ok(largePat.renderedLines <= 5000, 'DOM 同时显示的行数必须有硬上限');
  assert.equal(largePat.renderedElementNodes, 0, '大文件预览不得逐行创建元素节点');
  assert.equal(largePat.controlsVisible, true);
  assert.equal(largePat.readOnly, true);
  console.log(`Large PAT regression: ${largePat.totalLines.toLocaleString('en-US')} lines, ${largePat.heartbeat} UI heartbeats, ${largePat.renderedElementNodes} rendered line elements`);
  const lastWindowHasEnd = await window.webContents.executeJavaScript(`(() => {
    const lineCount = Number(document.querySelector('#pat-generator-prototype').dataset.patLineCount);
    document.querySelector('#pat-preview-jump').value = String(lineCount);
    document.querySelector('#pat-preview-jump-button').click();
    return document.querySelector('#pat-output').textContent.includes('@@END_PATTERN_DEFINE');
  })()`);
  assert.equal(lastWindowHasEnd, true, '应能跳到完整 PAT 最后一段');

  currentStage = '校验 50 万行完整 PAT 的字符数与 SHA-256';
  saveRequests.length = 0;
  nextSaveResult = { ok: true, canceled: false, fileName: 'large-regression.pat' };
  await window.webContents.executeJavaScript("document.querySelector('#pat-export').click()");
  await waitFor(() => saveRequests.length === 1, '50 万行 PAT 导出 IPC', 30000);
  const largePayload = saveRequests[0].content.endsWith('\n') ? saveRequests[0].content.slice(0, -1) : saveRequests[0].content;
  assert.equal(largePayload.length, 11954998);
  assert.equal(
    crypto.createHash('sha256').update(largePayload, 'utf8').digest('hex').toUpperCase(),
    '5FB44C2EDD147344C3C7247D45843F7D73A7C9D8A677A971E2D4186FE422E756'
  );

  currentStage = '完整生成超过 200 万行的流式 PAT';
  const streamedCreateCount = largePatRequests.create.length;
  await window.webContents.executeJavaScript(`(() => {
    document.querySelector('#pat-end').value = '00BFFF';
    window.__streamedPatHeartbeat = 0;
    window.__streamedPatStartedAt = performance.now();
    window.__streamedPatHeartbeatTimer = setInterval(() => { window.__streamedPatHeartbeat += 1; }, 10);
    document.querySelector('#pat-generate').click();
  })()`);
  await waitFor(
    () => window.webContents.executeJavaScript("Number(document.querySelector('#pat-generator-prototype').dataset.patLineCount) > 2000000 && document.querySelector('#pat-generation-progress').hidden && document.querySelector('#pat-generation-success-dialog').open"),
    '超过 200 万行流式 PAT 完整生成',
    180000
  );
  const streamedSuccess = await assertAndCloseGenerationSuccess(window, '超过 200 万行流式 PAT');
  await waitFor(
    () => window.webContents.executeJavaScript("document.querySelector('#pat-output').textContent.includes('@@PATTERN_DEFINE') && !document.querySelector('#pat-output').textContent.startsWith('正在读取')"),
    '流式 PAT 首段预览',
    30000
  );
  const streamedPat = await window.webContents.executeJavaScript(`(() => {
    clearInterval(window.__streamedPatHeartbeatTimer);
    const root = document.querySelector('#pat-generator-prototype');
    const output = document.querySelector('#pat-output');
    return {
      totalLines: Number(root.dataset.patLineCount),
      windowed: root.dataset.previewWindowed,
      heartbeat: window.__streamedPatHeartbeat,
      elapsed: performance.now() - window.__streamedPatStartedAt,
      renderedLines: output.textContent.split('\\n').length,
      renderedElementNodes: output.childElementCount,
      firstWindowHasPattern: output.textContent.includes('@@PATTERN_DEFINE'),
      controlsVisible: !document.querySelector('#pat-large-preview-controls').hidden,
      readOnly: output.contentEditable === 'false'
    };
  })()`);
  assert.ok(streamedPat.totalLines > 2000000, '完整流式 PAT 必须实际超过旧 200 万行上限');
  assert.equal(streamedPat.totalLines, 2084312, '流式公开回归配置必须稳定生成 2,084,312 行');
  assert.equal(streamedSuccess.lineCount, streamedPat.totalLines);
  assert.equal(streamedPat.windowed, 'true');
  assert.ok(streamedPat.heartbeat > 10, '超过 200 万行生成期间事件循环必须持续响应');
  assert.ok(streamedPat.elapsed < 45000, `超过 200 万行生成耗时应小于 45 秒，实际 ${streamedPat.elapsed.toFixed(1)} ms`);
  assert.ok(streamedPat.renderedLines <= 5000, '流式预览同时显示的行数必须有硬上限');
  assert.equal(streamedPat.renderedElementNodes, 0, '流式预览不得逐行创建元素节点');
  assert.equal(streamedPat.firstWindowHasPattern, true);
  assert.equal(streamedPat.controlsVisible, true);
  assert.equal(streamedPat.readOnly, true);
  assert.equal(largePatRequests.create.length, streamedCreateCount + 1, '超过 200 万行应切换到桌面流式临时文件');
  const completedStreamRequest = largePatRequests.create.at(-1);
  assert.ok(completedStreamRequest.expectedLines > 2000000, '流式配置的预计行数必须确实超过旧上限');
  const completedStreamSource = await smokeLargePatStore.getFinalizedSource({ token: completedStreamRequest.token });
  assert.equal(completedStreamSource.lineCount, streamedPat.totalLines, '真实临时文件行数必须与界面统计一致');
  assert.ok(completedStreamSource.sizeBytes > 0, '真实流式 PAT 临时文件不得为空');
  const streamHandle = fs.openSync(completedStreamSource.filePath, 'r');
  try {
    const firstBytes = Buffer.alloc(3);
    fs.readSync(streamHandle, firstBytes, 0, firstBytes.length, 0);
    assert.notDeepEqual([...firstBytes], [0xEF, 0xBB, 0xBF], '流式 PAT 不得写入 UTF-8 BOM');
    const finalBytes = Buffer.alloc(2);
    fs.readSync(streamHandle, finalBytes, 0, finalBytes.length, completedStreamSource.sizeBytes - finalBytes.length);
    assert.equal(finalBytes.toString('ascii'), '\r\n', '流式 PAT 必须以 Windows CRLF 结尾');
  } finally {
    fs.closeSync(streamHandle);
  }
  currentStage = '流式异步读取不得反向覆盖校验页';
  const readCountBeforeRace = largePatReadStarted;
  largePatReadDelayMs = 250;
  const validationDuringStreamRead = await window.webContents.executeJavaScript(`(() => {
    const root = document.querySelector('#pat-generator-prototype');
    const lineCount = Number(document.querySelector('#pat-generator-prototype').dataset.patLineCount);
    document.querySelector('#pat-preview-jump').value = String(lineCount);
    document.querySelector('#pat-preview-jump-button').click();
    document.querySelector('.pat-tab[data-tab="validation"]').click();
    return {
      expected: root.dataset.validation,
      shown: document.querySelector('#pat-output').innerText,
      validationSelected: document.querySelector('.pat-tab[data-tab="validation"]').getAttribute('aria-selected')
    };
  })()`);
  assert.equal(validationDuringStreamRead.validationSelected, 'true');
  assert.equal(normalizeRenderedText(validationDuringStreamRead.shown), normalizeRenderedText(validationDuringStreamRead.expected));
  await waitFor(() => largePatReadStarted > readCountBeforeRace, '延迟的流式预览读取启动');
  await delay(400);
  const validationAfterStreamRead = await window.webContents.executeJavaScript(`(() => ({
    shown: document.querySelector('#pat-output').innerText,
    expected: document.querySelector('#pat-generator-prototype').dataset.validation,
    validationSelected: document.querySelector('.pat-tab[data-tab="validation"]').getAttribute('aria-selected')
  }))()`);
  assert.equal(validationAfterStreamRead.validationSelected, 'true');
  assert.equal(normalizeRenderedText(validationAfterStreamRead.shown), normalizeRenderedText(validationAfterStreamRead.expected), '过期流式读取完成后不得覆盖校验页');
  assert.doesNotMatch(validationAfterStreamRead.shown, /@@END_PATTERN_DEFINE/);

  largePatReadDelayMs = 0;
  await window.webContents.executeJavaScript("document.querySelector('.pat-tab[data-tab=\"preview\"]').click()");
  await waitFor(
    () => window.webContents.executeJavaScript("document.querySelector('#pat-output').textContent.includes('@@END_PATTERN_DEFINE')"),
    '返回预览后的流式 PAT 最后一段 END',
    30000
  );
  console.log(`Streamed PAT regression: ${streamedPat.totalLines.toLocaleString('en-US')} lines, ${streamedPat.elapsed.toFixed(1)} ms, ${streamedPat.heartbeat} UI heartbeats`);

  currentStage = '对超过 200 万行流式 PAT 执行完整整列替换';
  const replacementCreateCount = largePatRequests.create.length;
  await window.webContents.executeJavaScript(`(() => {
    document.querySelector('#pat-column-number').value = '1';
    document.querySelector('#pat-column-char').value = 'X';
    document.querySelector('#pat-column-apply').click();
  })()`);
  await waitFor(
    () => window.webContents.executeJavaScript("document.querySelector('#pat-column-status').textContent.startsWith('已将第 1 列替换为 X') && document.querySelector('#pat-generation-progress').hidden"),
    '流式 PAT 整列替换',
    180000
  );
  assert.equal(largePatRequests.create.length, replacementCreateCount + 1, '流式整列替换应写入新的临时文件');
  const replacedStreamRequest = largePatRequests.create.at(-1);
  const replacedStreamSource = await smokeLargePatStore.getFinalizedSource({ token: replacedStreamRequest.token });
  assert.equal(replacedStreamSource.lineCount, streamedPat.totalLines, '整列替换不得改变流式 PAT 行数');
  const replacedFirstChunk = await smokeLargePatStore.readChunk({
    token: replacedStreamRequest.token,
    offset: 0,
    length: Math.min(4 * 1024 * 1024, replacedStreamSource.sizeBytes)
  });
  const replacedVectors = replacedFirstChunk.text.match(/^\s*(?:start:\s+|end:\s+)?[01HLXZ]{6};/gm) || [];
  assert.ok(replacedVectors.length > 0, '流式替换后的首段必须包含 PAT 向量');
  assert.ok(replacedVectors.every(line => /^(?:\s*(?:start:\s+|end:\s+)?)X/.test(line)), '流式替换必须作用于首段全部向量');
  assert.ok(largePatRequests.discard.some(request => request.token === completedStreamRequest.token), '流式替换成功后应清理旧临时文件');
  await assertGenerationSuccessClosed(window, '流式 PAT 整列替换');

  currentStage = '取消更大的流式 PAT 并保留超过 200 万行结果';
  const cancelCreateCount = largePatRequests.create.length;
  await window.webContents.executeJavaScript(`(() => {
    document.querySelector('#pat-end').value = '00FFFF';
    document.querySelector('#pat-generate').click();
  })()`);
  await waitFor(
    () => largePatRequests.create.length === cancelCreateCount + 1,
    '更大流式 PAT 临时文件创建',
    10000
  );
  await delay(100);
  const obsoleteLimitError = await window.webContents.executeJavaScript("document.querySelector('#pat-file-meta').textContent.includes('2,000,000 行安全上限')");
  assert.equal(obsoleteLimitError, false, '超过 200 万行不得再被旧安全上限拒绝');
  await window.webContents.executeJavaScript("document.querySelector('#pat-generation-cancel').click()");
  await waitFor(
    () => window.webContents.executeJavaScript("document.querySelector('#pat-generation-progress').hidden && document.querySelector('#pat-file-meta').textContent.includes('已取消生成')"),
    '取消更大的流式 PAT',
    30000
  );
  await assertGenerationSuccessClosed(window, '取消更大的流式 PAT');
  const retainedAfterRaisedLimitCancel = await window.webContents.executeJavaScript("Number(document.querySelector('#pat-generator-prototype').dataset.patLineCount)");
  assert.equal(retainedAfterRaisedLimitCancel, streamedPat.totalLines, '取消后必须保留上一份超过 200 万行的完整 PAT');
  assert.equal(largePatRequests.create.length, cancelCreateCount + 1);
  const canceledStreamRequest = largePatRequests.create.at(-1);
  assert.ok(canceledStreamRequest.expectedLines > completedStreamRequest.expectedLines, '取消任务必须比已完成的流式 PAT 更大');
  assert.ok(
    largePatRequests.discard.some(request => request.token === canceledStreamRequest.token),
    '取消生成后必须丢弃对应的大 PAT 临时文件'
  );
  assert.equal(
    largePatRequests.discard.some(request => request.token === replacedStreamRequest.token),
    false,
    '取消新任务时不得丢弃上一份已完成的流式 PAT'
  );

  currentStage = '运行中超过内存阈值时自动迁移到流式 PAT';
  const adaptiveCreateCount = largePatRequests.create.length;
  await window.webContents.executeJavaScript(`(() => {
    document.querySelector('#pat-reset').click();
    const model = document.querySelector('#pat-device-model');
    model.value = 'CUSTOM';
    model.dispatchEvent(new Event('change', { bubbles: true }));
    document.querySelector('#pat-data-mode').value = 'mode1';
    document.querySelector('#pat-pattern').value = 'ALL 0';
    document.querySelector('#pat-write-bus').value = 'SPI';
    document.querySelector('#pat-read-bus').value = 'SPI';
    document.querySelector('#pat-start').value = '000000';
    document.querySelector('#pat-end').value = '003FFF';
    document.querySelector('#pat-page-size').value = '16384';
    document.querySelector('#pat-sector-size').value = '1';
    document.querySelector('#pat-generate').click();
  })()`);
  await waitFor(
    () => largePatRequests.create.length === adaptiveCreateCount + 1,
    '运行中跨阈值后创建流式临时文件',
    120000
  );
  const adaptiveStreamRequest = largePatRequests.create.at(-1);
  assert.ok(adaptiveStreamRequest.expectedLines > 2000000, '运行时迁移必须发生在实际行数跨过内存阈值之后');
  await window.webContents.executeJavaScript("document.querySelector('#pat-generation-cancel').click()");
  await waitFor(
    () => window.webContents.executeJavaScript("document.querySelector('#pat-generation-progress').hidden && document.querySelector('#pat-file-meta').textContent.includes('已取消生成')"),
    '取消运行时迁移任务',
    30000
  );
  assert.ok(
    largePatRequests.discard.some(request => request.token === adaptiveStreamRequest.token),
    '取消运行时迁移后必须清理新建的流式临时文件'
  );
  await assertGenerationSuccessClosed(window, '运行时流式迁移取消');

  const fixedMemoryLargeCases = [
    {
      type: 'EEPROM', protocol: 'IIC', model: '24LC02B', bus: 'I2C', mode: 'mode2', pattern: 'ALL 0', operation: 'page-write',
      start: '00', end: 'FF', expectedLines: 172069, sha256: 'A475A1AC8A81F35D7CE33C2081D3062FF39B7CFF6D17C376D9EF4B1B3FEEAE7D', streamed: true, minimumHeartbeat: 1, maxElapsed: 60000, timeout: 120000
    },
    {
      type: 'EEPROM', protocol: 'SPI', model: '25LC256', bus: 'SPI', mode: 'mode1', pattern: 'ALL 0',
      start: '0000', end: '7FFF', expectedLines: 1497257, sha256: '8706CA66820DA3C4EF928F59815264C3F67BB8C87715365CF45E2601A170EE8E', streamed: true, minimumHeartbeat: 10, maxElapsed: 90000, timeout: 150000
    },
    {
      type: 'SRAM', model: '23LC1024', bus: 'SPI', mode: 'mode1', pattern: 'ALL 0',
      start: '000000', end: '01FFFF', expectedLines: 5636515, sha256: '9D8A74D6671B38D61B8891A059B4E8ACF46AF5E2A58E2A2BD21C61FD9EDE8BF9', streamed: true, minimumHeartbeat: 10, maxElapsed: 120000, timeout: 180000
    },
    {
      type: 'SRAM', model: '23LC1024', bus: 'SPI', mode: 'mode1', pattern: 'Checkerboard',
      start: '000000', end: '001A0A', byteCount: 6667, verifyUncompressible: true,
      expectedLines: 553740, sha256: 'FA970144C2795B18A4397F4C98B1E7ED76EF288D57AF89D7798EA1B8C1EEACEB', streamed: true, minimumHeartbeat: 5, maxElapsed: 60000, timeout: 120000
    }
  ];
  for (const spec of fixedMemoryLargeCases) await generateFixedMemoryLargeCase(window, spec);

  currentStage = '拒绝超过 JavaScript 安全整数的自定义地址';
  await window.webContents.executeJavaScript(`(() => {
    const model = document.querySelector('#pat-device-model');
    model.value = 'CUSTOM';
    model.dispatchEvent(new Event('change', { bubbles: true }));
    document.querySelector('#pat-address-width').value = '64';
    document.querySelector('#pat-start').value = '20000000000000';
    document.querySelector('#pat-end').value = '20000000000000';
    document.querySelector('#pat-generate').click();
  })()`);
  await waitFor(
    () => window.webContents.executeJavaScript("document.querySelector('#pat-generation-progress').hidden && document.querySelector('#pat-file-meta').textContent.includes('超出安全整数范围')"),
    '不安全整数地址拦截',
    5000
  );
  await assertGenerationSuccessClosed(window, '不安全整数地址');

  assert.deepEqual(remoteRequests, []);
  assert.deepEqual(consoleErrors, []);
  assert.equal(window.webContents.isDevToolsOpened(), false);
  await smokeLargePatStore.cleanupAll();
  smokeLargePatStore = null;
  ipcMain.removeHandler('file:save');
  Object.values(LARGE_PAT_CHANNELS).forEach(channel => ipcMain.removeHandler(channel));
  window.destroy();
  console.log('Electron smoke: 31/31 checks passed');
}

run()
  .then(() => app.exit(0))
  .catch(error => {
    console.error(`Smoke 阶段失败：${currentStage}`);
    console.error(error);
    if (consoleErrors.length) console.error('Renderer console errors:', consoleErrors);
    if (smokeLargePatStore) smokeLargePatStore.cleanupAllSync();
    app.exit(1);
  });
