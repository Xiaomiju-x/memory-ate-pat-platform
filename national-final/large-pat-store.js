'use strict';

const crypto = require('node:crypto');
const fs = require('node:fs');
const fsp = require('node:fs/promises');
const os = require('node:os');
const path = require('node:path');
const { Transform } = require('node:stream');
const { pipeline } = require('node:stream/promises');
const { StringDecoder } = require('node:string_decoder');
const { TextDecoder } = require('node:util');

const MAX_ACTIVE_FILES = 8;
const MAX_APPEND_CHARS = 4 * 1024 * 1024;
const MAX_READ_BYTES = 16 * 1024 * 1024;
const MIN_READ_BYTES = 4;
const TOKEN_PATTERN = /^[A-Za-z0-9_-]{43}$/;
const SESSION_PREFIX = 'pat-generator-large-';

class LargePatStoreError extends Error {
  constructor(code, message) {
    super(message);
    this.name = 'LargePatStoreError';
    this.code = code;
  }
}

function fail(code, message) {
  throw new LargePatStoreError(code, message);
}

function assertExactObject(value, allowedKeys, requiredKeys = allowedKeys) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    fail('INVALID_REQUEST', '大 PAT 请求格式无效。');
  }
  const keys = Object.keys(value);
  if (keys.some(key => !allowedKeys.includes(key)) || requiredKeys.some(key => !keys.includes(key))) {
    fail('INVALID_REQUEST', '大 PAT 请求包含无效字段。');
  }
  return value;
}

function assertSafeInteger(label, value, minimum, maximum = Number.MAX_SAFE_INTEGER) {
  if (!Number.isSafeInteger(value) || value < minimum || value > maximum) {
    fail('INVALID_REQUEST', label + '超出允许范围。');
  }
  return value;
}

function assertToken(token) {
  if (typeof token !== 'string' || !TOKEN_PATTERN.test(token)) {
    fail('INVALID_TOKEN', '大 PAT token 无效。');
  }
  return token;
}

function assertWellFormedUnicode(value) {
  for (let index = 0; index < value.length; index += 1) {
    const code = value.charCodeAt(index);
    if (code >= 0xD800 && code <= 0xDBFF) {
      const next = value.charCodeAt(index + 1);
      if (!(next >= 0xDC00 && next <= 0xDFFF)) return false;
      index += 1;
    } else if (code >= 0xDC00 && code <= 0xDFFF) {
      return false;
    }
  }
  return true;
}

function assertLfChunk(chunk) {
  if (typeof chunk !== 'string') fail('INVALID_REQUEST', '大 PAT 数据块必须是文本。');
  if (chunk.length === 0 || chunk.length > MAX_APPEND_CHARS) {
    fail('INVALID_REQUEST', '大 PAT 数据块大小超出允许范围。');
  }
  if (chunk.includes('\r')) fail('INVALID_REQUEST', '大 PAT 数据块只能使用 LF 换行。');
  if (/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F\uFEFF]/.test(chunk) || !assertWellFormedUnicode(chunk)) {
    fail('INVALID_REQUEST', '大 PAT 数据块包含无效字符。');
  }
  return chunk;
}

function countLf(value) {
  let count = 0;
  for (let index = 0; index < value.length; index += 1) {
    if (value.charCodeAt(index) === 10) count += 1;
  }
  return count;
}

function isContainedPath(parent, candidate) {
  const relative = path.relative(path.resolve(parent), path.resolve(candidate));
  return relative !== '' && relative !== '..' && !relative.startsWith('..' + path.sep) && !path.isAbsolute(relative);
}

function decodeCompleteUtf8(buffer) {
  const decoder = new TextDecoder('utf-8', { fatal: true });
  for (let trim = 0; trim <= Math.min(3, buffer.length); trim += 1) {
    const length = buffer.length - trim;
    if (length === 0) break;
    try {
      return { byteLength: length, text: decoder.decode(buffer.subarray(0, length)) };
    } catch (_error) {
      // A UTF-8 code point may straddle the requested byte window. Trim at most 3 bytes.
    }
  }
  fail('INVALID_OFFSET', '读取位置不是有效的 UTF-8 文本边界。');
}

function replaceVectorColumn(line, columnIndex, target, counters) {
  return line.replace(/^(\s*(?:(?:start|end):\s*)?)([01HLXZ]{6})(\s*;)/i, (_all, prefix, vector, suffix) => {
    const characters = vector.toUpperCase().split('');
    characters[columnIndex] = target;
    counters.changed += 1;
    return prefix + characters.join('') + suffix;
  });
}

function createColumnReplacementTransform(columnIndex, target, counters) {
  const decoder = new StringDecoder('utf8');
  let pending = '';
  const emitCompleteLines = stream => {
    let newline;
    while ((newline = pending.indexOf('\r\n')) !== -1) {
      const line = pending.slice(0, newline);
      pending = pending.slice(newline + 2);
      counters.lineCount += 1;
      stream.push(replaceVectorColumn(line, columnIndex, target, counters) + '\r\n');
    }
  };
  return new Transform({
    transform(chunk, _encoding, callback) {
      try {
        pending += decoder.write(chunk);
        emitCompleteLines(this);
        callback();
      } catch (error) {
        callback(error);
      }
    },
    flush(callback) {
      try {
        pending += decoder.end();
        emitCompleteLines(this);
        if (pending) {
          counters.lineCount += 1;
          this.push(replaceVectorColumn(pending, columnIndex, target, counters));
        }
        callback();
      } catch (error) {
        callback(error);
      }
    }
  });
}

class LargePatStore {
  constructor({ temporaryRoot, sessionDirectory }) {
    this.temporaryRoot = path.resolve(temporaryRoot);
    this.sessionDirectory = path.resolve(sessionDirectory);
    this.entries = new Map();
    this.closed = false;
  }

  static async create({ temporaryRoot = os.tmpdir() } = {}) {
    const resolvedRoot = path.resolve(temporaryRoot);
    const sessionDirectory = await fsp.mkdtemp(path.join(resolvedRoot, SESSION_PREFIX));
    if (!isContainedPath(resolvedRoot, sessionDirectory)) {
      await fsp.rm(sessionDirectory, { recursive: true, force: true });
      fail('IO_ERROR', '无法建立安全的大 PAT 临时目录。');
    }
    return new LargePatStore({ temporaryRoot: resolvedRoot, sessionDirectory });
  }

  _assertOpen() {
    if (this.closed) fail('INVALID_STATE', '大 PAT 临时存储已关闭。');
  }

  _entry(token) {
    this._assertOpen();
    const normalizedToken = assertToken(token);
    const entry = this.entries.get(normalizedToken);
    if (!entry || entry.state === 'discarded') fail('NOT_FOUND', '大 PAT token 不存在或已失效。');
    return entry;
  }

  _enqueue(entry, operation) {
    const pending = entry.queue.then(operation);
    entry.queue = pending.catch(() => undefined);
    return pending;
  }

  async createFile(request) {
    this._assertOpen();
    assertExactObject(request, ['expectedLines']);
    const expectedLines = assertSafeInteger('预计行数', request.expectedLines, 1);
    if (this.entries.size >= MAX_ACTIVE_FILES) {
      fail('LIMIT_EXCEEDED', '同时存在的大 PAT 临时文件过多，请先保存或丢弃旧文件。');
    }

    const token = crypto.randomBytes(32).toString('base64url');
    const fileName = crypto.randomBytes(24).toString('hex') + '.pat.tmp';
    const filePath = path.join(this.sessionDirectory, fileName);
    if (!isContainedPath(this.sessionDirectory, filePath)) fail('IO_ERROR', '大 PAT 临时文件路径无效。');
    await fsp.writeFile(filePath, Buffer.alloc(0), { flag: 'wx', mode: 0o600 });
    this.entries.set(token, {
      token,
      filePath,
      expectedLines,
      state: 'open',
      queue: Promise.resolve(),
      sizeBytes: 0,
      newlineCount: 0,
      hasText: false,
      endsWithLf: false,
      lineCount: 0
    });
    return Object.freeze({ token, expectedLines });
  }

  async append(request) {
    assertExactObject(request, ['token', 'chunk']);
    const entry = this._entry(request.token);
    const chunk = assertLfChunk(request.chunk);
    return this._enqueue(entry, async () => {
      if (entry.state !== 'open') fail('INVALID_STATE', '大 PAT 已完成，不能继续追加。');
      const crlfChunk = chunk.replace(/\n/g, '\r\n');
      const bytesWritten = Buffer.byteLength(crlfChunk, 'utf8');
      const offset = entry.sizeBytes;
      await fsp.appendFile(entry.filePath, crlfChunk, { encoding: 'utf8', flag: 'a' });
      entry.sizeBytes += bytesWritten;
      entry.newlineCount += countLf(chunk);
      entry.hasText = true;
      entry.endsWithLf = chunk.endsWith('\n');
      return Object.freeze({ offset, length: bytesWritten, bytesWritten, totalBytes: entry.sizeBytes });
    });
  }

  async finalize(request) {
    assertExactObject(request, ['token']);
    const entry = this._entry(request.token);
    return this._enqueue(entry, async () => {
      if (entry.state !== 'open') fail('INVALID_STATE', '大 PAT 已经完成。');
      const stat = await fsp.stat(entry.filePath);
      if (!stat.isFile() || stat.size !== entry.sizeBytes) fail('IO_ERROR', '大 PAT 临时文件校验失败。');
      entry.lineCount = entry.hasText ? entry.newlineCount + (entry.endsWithLf ? 0 : 1) : 0;
      entry.state = 'finalized';
      return Object.freeze({
        expectedLines: entry.expectedLines,
        lineCount: entry.lineCount,
        size: entry.sizeBytes,
        sizeBytes: entry.sizeBytes
      });
    });
  }

  async readChunk(request) {
    assertExactObject(request, ['token', 'offset', 'length']);
    const entry = this._entry(request.token);
    const offset = assertSafeInteger('读取偏移', request.offset, 0);
    const length = assertSafeInteger('读取长度', request.length, MIN_READ_BYTES, MAX_READ_BYTES);
    return this._enqueue(entry, async () => {
      if (entry.state !== 'finalized') fail('INVALID_STATE', '大 PAT 完成后才能读取。');
      if (offset > entry.sizeBytes) fail('INVALID_OFFSET', '读取偏移超出大 PAT 文件范围。');
      if (offset === entry.sizeBytes) {
        return Object.freeze({ offset, nextOffset: offset, eof: true, content: '', text: '' });
      }

      const bytesToRead = Math.min(length, entry.sizeBytes - offset);
      const buffer = Buffer.allocUnsafe(bytesToRead);
      const handle = await fsp.open(entry.filePath, 'r');
      let bytesRead;
      try {
        ({ bytesRead } = await handle.read(buffer, 0, bytesToRead, offset));
      } finally {
        await handle.close();
      }
      const decoded = decodeCompleteUtf8(buffer.subarray(0, bytesRead));
      let usableBytes = decoded.byteLength;
      let text = decoded.text;

      // Keep CRLF together so every returned text block can be normalized to LF losslessly.
      if (offset + usableBytes < entry.sizeBytes && text.endsWith('\r')) {
        usableBytes -= 1;
        text = text.slice(0, -1);
      }
      if (usableBytes <= 0) fail('INVALID_OFFSET', '读取窗口无法形成完整文本，请增加读取长度。');
      const nextOffset = offset + usableBytes;
      const normalizedText = text.replace(/\r\n/g, '\n');
      return Object.freeze({
        offset,
        nextOffset,
        eof: nextOffset >= entry.sizeBytes,
        content: normalizedText,
        text: normalizedText
      });
    });
  }

  async getFinalizedSource(request) {
    assertExactObject(request, ['token']);
    const entry = this._entry(request.token);
    return this._enqueue(entry, async () => {
      if (entry.state !== 'finalized') fail('INVALID_STATE', '大 PAT 完成后才能保存。');
      const stat = await fsp.stat(entry.filePath);
      if (!stat.isFile() || stat.size !== entry.sizeBytes) fail('IO_ERROR', '大 PAT 临时文件校验失败。');
      return Object.freeze({ filePath: entry.filePath, sizeBytes: entry.sizeBytes, lineCount: entry.lineCount });
    });
  }

  async withFinalizedSource(request, operation) {
    assertExactObject(request, ['token']);
    if (typeof operation !== 'function') fail('INVALID_REQUEST', '大 PAT 保存操作无效。');
    const entry = this._entry(request.token);
    return this._enqueue(entry, async () => {
      if (entry.state !== 'finalized') fail('INVALID_STATE', '大 PAT 完成后才能保存。');
      const stat = await fsp.stat(entry.filePath);
      if (!stat.isFile() || stat.size !== entry.sizeBytes) fail('IO_ERROR', '大 PAT 临时文件校验失败。');
      return operation(Object.freeze({ filePath: entry.filePath, sizeBytes: entry.sizeBytes, lineCount: entry.lineCount }));
    });
  }

  async replaceColumn(request) {
    assertExactObject(request, ['token', 'column', 'target']);
    const entry = this._entry(request.token);
    const column = assertSafeInteger('PAT 列号', request.column, 1, 6);
    if (typeof request.target !== 'string' || !/^[01HLXZ]$/.test(request.target)) {
      fail('INVALID_REQUEST', '目标字符只能是 0、1、H、L、X 或 Z。');
    }
    const target = request.target;
    return this._enqueue(entry, async () => {
      if (entry.state !== 'finalized') fail('INVALID_STATE', '大 PAT 完成后才能执行整列替换。');
      const replacementToken = crypto.randomBytes(32).toString('base64url');
      const replacementName = crypto.randomBytes(24).toString('hex') + '.pat.tmp';
      const replacementPath = path.join(this.sessionDirectory, replacementName);
      if (!isContainedPath(this.sessionDirectory, replacementPath)) fail('IO_ERROR', '大 PAT 替换文件路径无效。');
      const counters = { changed: 0, lineCount: 0 };
      try {
        await pipeline(
          fs.createReadStream(entry.filePath),
          createColumnReplacementTransform(column - 1, target, counters),
          fs.createWriteStream(replacementPath, { flags: 'wx', mode: 0o600 })
        );
        const stat = await fsp.stat(replacementPath);
        if (!stat.isFile() || counters.lineCount !== entry.lineCount) {
          fail('IO_ERROR', '大 PAT 整列替换后的文件校验失败。');
        }

        // Only retire the source after the complete replacement has been written and verified.
        await fsp.unlink(entry.filePath);
        entry.state = 'discarded';
        this.entries.delete(entry.token);
        this.entries.set(replacementToken, {
          token: replacementToken,
          filePath: replacementPath,
          expectedLines: entry.expectedLines,
          state: 'finalized',
          queue: Promise.resolve(),
          sizeBytes: stat.size,
          newlineCount: entry.newlineCount,
          hasText: entry.hasText,
          endsWithLf: entry.endsWithLf,
          lineCount: entry.lineCount
        });
        return Object.freeze({
          token: replacementToken,
          expectedLines: entry.expectedLines,
          lineCount: entry.lineCount,
          sizeBytes: stat.size,
          changed: counters.changed
        });
      } catch (error) {
        try {
          await fsp.unlink(replacementPath);
        } catch (cleanupError) {
          if (!cleanupError || cleanupError.code !== 'ENOENT') console.error('清理大 PAT 替换临时文件失败：', cleanupError);
        }
        throw error;
      }
    });
  }

  async discard(request) {
    assertExactObject(request, ['token']);
    const entry = this._entry(request.token);
    return this._enqueue(entry, async () => {
      entry.state = 'discarded';
      this.entries.delete(entry.token);
      try {
        await fsp.unlink(entry.filePath);
      } catch (error) {
        if (!error || error.code !== 'ENOENT') throw error;
      }
      return Object.freeze({ discarded: true });
    });
  }

  async cleanupAll() {
    if (this.closed) return;
    this.closed = true;
    const pending = Array.from(this.entries.values(), entry => entry.queue.catch(() => undefined));
    await Promise.all(pending);
    this.entries.clear();
    if (!isContainedPath(this.temporaryRoot, this.sessionDirectory)) {
      fail('IO_ERROR', '拒绝清理不安全的大 PAT 临时目录。');
    }
    await fsp.rm(this.sessionDirectory, { recursive: true, force: true, maxRetries: 2 });
  }

  cleanupAllSync() {
    if (this.closed) return;
    this.closed = true;
    this.entries.clear();
    if (!isContainedPath(this.temporaryRoot, this.sessionDirectory)) return;
    fs.rmSync(this.sessionDirectory, { recursive: true, force: true, maxRetries: 2 });
  }
}

module.exports = {
  LargePatStore,
  LargePatStoreError,
  MAX_ACTIVE_FILES,
  MAX_APPEND_CHARS,
  MAX_READ_BYTES,
  MIN_READ_BYTES,
  assertExactObject
};
