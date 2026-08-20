'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const os = require('node:os');
const path = require('node:path');
const test = require('node:test');
const { LargePatStore } = require('../large-pat-store');
const { savePatStreamWithDialog } = require('../save-file');

async function temporaryStore(t) {
  const temporaryRoot = await fs.mkdtemp(path.join(os.tmpdir(), 'PAT大文件测试-'));
  const store = await LargePatStore.create({ temporaryRoot });
  t.after(async () => {
    await store.cleanupAll().catch(() => undefined);
    await fs.rm(temporaryRoot, { recursive: true, force: true });
  });
  return { store, temporaryRoot };
}

async function readAll(store, token, length = 7) {
  let offset = 0;
  let text = '';
  while (true) {
    const chunk = await store.readChunk({ token, offset, length });
    assert.equal(chunk.offset, offset);
    assert.ok(chunk.nextOffset > offset || chunk.eof);
    assert.equal(chunk.content, chunk.text);
    text += chunk.text;
    offset = chunk.nextOffset;
    if (chunk.eof) return text;
  }
}

test('large PAT store streams LF chunks to private UTF-8 CRLF files and reads Chinese safely', async t => {
  const { store } = await temporaryStore(t);
  const source = '// 中文 PAT\n        01HLXZ;\nend:    ZXLH10;';
  const created = await store.createFile({ expectedLines: 3 });

  assert.match(created.token, /^[A-Za-z0-9_-]{43}$/);
  assert.deepEqual(Object.keys(created).sort(), ['expectedLines', 'token']);
  const first = await store.append({ token: created.token, chunk: '// 中文 PAT' });
  const second = await store.append({ token: created.token, chunk: '\n        01HLXZ;\nend:    ZXLH10;' });
  assert.deepEqual([first.offset, second.offset], [0, first.length]);
  assert.equal(first.length, first.bytesWritten);
  assert.equal(second.totalBytes, first.length + second.length);

  const finalized = await store.finalize({ token: created.token });
  assert.equal(finalized.lineCount, 3);
  assert.equal(finalized.size, finalized.sizeBytes);
  await assert.rejects(
    store.append({ token: created.token, chunk: '\n不能追加' }),
    /不能继续追加/
  );

  const [temporaryName] = await fs.readdir(store.sessionDirectory);
  const bytes = await fs.readFile(path.join(store.sessionDirectory, temporaryName));
  assert.equal(bytes.subarray(0, 3).equals(Buffer.from([0xEF, 0xBB, 0xBF])), false);
  assert.equal(/(^|[^\r])\n/.test(bytes.toString('utf8')), false);
  assert.equal(bytes.toString('utf8'), source.replace(/\n/g, '\r\n'));
  assert.equal(await readAll(store, created.token, 7), source);
});

test('large PAT store rejects non-whitelisted fields, CR chunks and invalid read parameters', async t => {
  const { store } = await temporaryStore(t);
  await assert.rejects(store.createFile({ expectedLines: 1, filePath: '泄露路径' }), /无效字段/);
  const created = await store.createFile({ expectedLines: 1 });
  await assert.rejects(store.append({ token: created.token, chunk: 'A\r\n' }), /只能使用 LF/);
  await assert.rejects(store.append({ token: created.token, chunk: '' }), /大小超出/);
  await store.append({ token: created.token, chunk: '中文' });
  await store.finalize({ token: created.token });
  await assert.rejects(store.readChunk({ token: created.token, offset: 0, length: 3 }), /读取长度/);
  await assert.rejects(store.readChunk({ token: 'not-a-token', offset: 0, length: 4 }), /token 无效/);
});

test('column replacement creates a verified new token and retires the source only on success', async t => {
  const { store } = await temporaryStore(t);
  const source = 'HEAD\n        01HLXZ;\nstart:  ZXLH10; AC_SET 1;\n';
  const created = await store.createFile({ expectedLines: 3 });
  await store.append({ token: created.token, chunk: source });
  await store.finalize({ token: created.token });

  await assert.rejects(
    store.replaceColumn({ token: created.token, column: 2, target: '?' }),
    /目标字符/
  );
  assert.equal(await readAll(store, created.token), source, '参数错误不得改变原文件');

  const replaced = await store.replaceColumn({ token: created.token, column: 2, target: '0' });
  assert.notEqual(replaced.token, created.token);
  assert.equal(replaced.changed, 2);
  assert.equal(replaced.lineCount, 3);
  await assert.rejects(store.readChunk({ token: created.token, offset: 0, length: 8 }), /不存在|失效/);
  assert.equal(
    await readAll(store, replaced.token),
    'HEAD\n        00HLXZ;\nstart:  Z0LH10; AC_SET 1;\n'
  );

  await store.discard({ token: replaced.token });
  await assert.rejects(store.readChunk({ token: replaced.token, offset: 0, length: 8 }), /不存在|失效/);
  assert.deepEqual(await fs.readdir(store.sessionDirectory), []);
});

test('streamed PAT save forces .pat and cancellation never creates the selected target', async t => {
  const { store, temporaryRoot } = await temporaryStore(t);
  const created = await store.createFile({ expectedLines: 2 });
  await store.append({ token: created.token, chunk: '第一行\n第二行\n' });
  await store.finalize({ token: created.token });

  const canceledPath = path.join(temporaryRoot, '不应创建.pat');
  const canceled = await store.withFinalizedSource({ token: created.token }, source => savePatStreamWithDialog({
    dialog: { showSaveDialog: async () => ({ canceled: true, filePath: canceledPath }) },
    sourcePath: source.filePath,
    suggestedName: '取消.pat',
    defaultDirectory: temporaryRoot
  }));
  assert.deepEqual(canceled, { ok: false, canceled: true });
  await assert.rejects(fs.stat(canceledPath), error => error.code === 'ENOENT');

  const selectedPath = path.join(temporaryRoot, '决赛 输出.txt');
  const saved = await store.withFinalizedSource({ token: created.token }, source => savePatStreamWithDialog({
    dialog: { showSaveDialog: async () => ({ canceled: false, filePath: selectedPath }) },
    sourcePath: source.filePath,
    suggestedName: '../决赛 输出.txt',
    defaultDirectory: temporaryRoot
  }));
  assert.equal(saved.fileName, '决赛 输出.txt.pat');
  assert.equal(await fs.readFile(selectedPath + '.pat', 'utf8'), '第一行\r\n第二行\r\n');
});
