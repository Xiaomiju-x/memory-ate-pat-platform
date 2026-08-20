'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const os = require('node:os');
const path = require('node:path');
const test = require('node:test');
const {
  ensureRequiredExtension,
  normalizeCrlf,
  normalizeSaveRequest,
  sanitizeSuggestedName,
  saveFileWithDialog
} = require('../save-file');

test('normalizeCrlf converts mixed line endings exactly once', () => {
  assert.equal(normalizeCrlf('甲\n乙\r丙\r\n丁\r\n'), '甲\r\n乙\r\n丙\r\n丁\r\n');
});

test('suggested names are sanitized and forced to the selected kind', () => {
  assert.equal(sanitizeSuggestedName('../坏:名字.txt', 'pat'), '坏_名字.pat');
  assert.equal(sanitizeSuggestedName('报告', 'txt'), '报告.txt');
  assert.equal(sanitizeSuggestedName('CON.pat', 'pat'), '_CON.pat');
  assert.equal(ensureRequiredExtension('D:\\输出\\向量.txt', '.pat'), 'D:\\输出\\向量.txt.pat');
});

test('save requests reject untrusted kinds, content and extensions', () => {
  assert.throws(() => normalizeSaveRequest(null), /格式无效/);
  assert.throws(() => normalizeSaveRequest({ kind: 'exe', content: '' }), /不支持/);
  assert.throws(() => normalizeSaveRequest({ kind: 'pat', content: Buffer.from('x') }), /必须是文本/);
  assert.throws(() => normalizeSaveRequest({ kind: 'pat', content: 'x', extension: '.txt' }), /不匹配/);
});

test('canceling the native dialog never writes a file', async () => {
  let writeCount = 0;
  const result = await saveFileWithDialog({
    dialog: { showSaveDialog: async () => ({ canceled: true }) },
    request: { kind: 'pat', extension: '.pat', suggestedName: '测试.pat', content: 'A\n' },
    defaultDirectory: 'D:\\输出',
    writeFile: async () => { writeCount += 1; }
  });
  assert.deepEqual(result, { ok: false, canceled: true });
  assert.equal(writeCount, 0);
});

test('PAT save uses a single PAT filter, UTF-8, CRLF and a forced .pat suffix', async () => {
  let options;
  let write;
  const result = await saveFileWithDialog({
    dialog: {
      showSaveDialog: async (_parent, receivedOptions) => {
        options = receivedOptions;
        return { canceled: false, filePath: 'D:\\中文 路径\\edited.txt' };
      }
    },
    request: {
      kind: 'pat',
      extension: '.pat',
      suggestedName: 'edited.pat',
      content: '// 用户编辑\n000000;\r\n'
    },
    defaultDirectory: 'D:\\默认目录',
    writeFile: async (targetPath, content, encoding) => { write = { targetPath, content, encoding }; }
  });

  assert.equal(options.filters.length, 1);
  assert.deepEqual(options.filters[0].extensions, ['pat']);
  assert.match(options.defaultPath, /edited\.pat$/);
  assert.equal(write.targetPath, 'D:\\中文 路径\\edited.txt.pat');
  assert.equal(write.content, '// 用户编辑\r\n000000;\r\n');
  assert.deepEqual(write.encoding, { encoding: 'utf8', flag: 'w' });
  assert.deepEqual(result, { ok: true, canceled: false, fileName: 'edited.txt.pat' });
});

test('TXT saves successfully to a real path containing Chinese and spaces', async t => {
  const temporaryRoot = await fs.mkdtemp(path.join(os.tmpdir(), 'PAT 决赛 测试-'));
  t.after(() => fs.rm(temporaryRoot, { recursive: true, force: true }));
  const targetPath = path.join(temporaryRoot, '结构 说明.txt');
  const result = await saveFileWithDialog({
    dialog: { showSaveDialog: async () => ({ canceled: false, filePath: targetPath }) },
    request: {
      kind: 'txt',
      extension: '.txt',
      suggestedName: '结构 说明.txt',
      content: '第一行\n第二行\n'
    },
    defaultDirectory: temporaryRoot
  });

  const bytes = await fs.readFile(targetPath);
  assert.deepEqual(result, { ok: true, canceled: false, fileName: '结构 说明.txt' });
  assert.equal(bytes.subarray(0, 3).equals(Buffer.from([0xEF, 0xBB, 0xBF])), false);
  assert.equal(bytes.toString('utf8'), '第一行\r\n第二行\r\n');
  assert.equal(/(^|[^\r])\n/.test(bytes.toString('utf8')), false);
});
