'use strict';

const fsSync = require('node:fs');
const fs = require('node:fs/promises');
const path = require('node:path');
const { pipeline } = require('node:stream/promises');

const SAVE_TYPES = Object.freeze({
  pat: Object.freeze({
    extension: '.pat',
    title: '保存 PAT 向量文件',
    buttonLabel: '保存 PAT',
    filterName: 'PAT 文件 (*.pat)',
    fallbackName: 'PAT向量.pat'
  }),
  txt: Object.freeze({
    extension: '.txt',
    title: '保存 PAT 结构说明',
    buttonLabel: '保存 TXT',
    filterName: '文本文件 (*.txt)',
    fallbackName: 'PAT结构说明.txt'
  })
});

const WINDOWS_RESERVED_NAME = /^(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?$/i;

function normalizeCrlf(value) {
  return String(value).replace(/\r\n|\r|\n/g, '\r\n');
}

function sanitizeSuggestedName(value, type) {
  const spec = SAVE_TYPES[type];
  if (!spec) throw new TypeError('不支持的保存文件类型');

  let name = path.win32.basename(String(value || ''))
    .replace(/[<>:"/\\|?*\u0000-\u001F]/g, '_')
    .replace(/[. ]+$/g, '')
    .trim();

  if (!name) name = spec.fallbackName;
  if (!name.toLowerCase().endsWith(spec.extension)) {
    const currentExtension = path.win32.extname(name);
    const stem = currentExtension ? name.slice(0, -currentExtension.length) : name;
    name = (stem || path.win32.basename(spec.fallbackName, spec.extension)) + spec.extension;
  }
  if (WINDOWS_RESERVED_NAME.test(name)) name = '_' + name;

  const maxStemLength = 240 - spec.extension.length;
  const stem = name.slice(0, -spec.extension.length).slice(0, maxStemLength);
  return (stem || path.win32.basename(spec.fallbackName, spec.extension)) + spec.extension;
}

function normalizeSaveRequest(request) {
  if (!request || typeof request !== 'object' || Array.isArray(request)) {
    throw new TypeError('保存请求格式无效');
  }
  const type = String(request.kind || '').toLowerCase();
  const spec = SAVE_TYPES[type];
  if (!spec) throw new TypeError('不支持的保存文件类型');
  if (typeof request.content !== 'string') throw new TypeError('保存内容必须是文本');
  if (request.extension != null && String(request.extension).toLowerCase() !== spec.extension) {
    throw new TypeError('文件扩展名与保存类型不匹配');
  }

  return Object.freeze({
    kind: type,
    suggestedName: sanitizeSuggestedName(request.suggestedName, type),
    content: normalizeCrlf(request.content),
    spec
  });
}

function ensureRequiredExtension(filePath, extension) {
  const selectedPath = String(filePath || '');
  if (selectedPath.toLowerCase().endsWith(extension)) return selectedPath;
  return selectedPath + extension;
}

async function saveFileWithDialog({
  dialog,
  parentWindow,
  request,
  defaultDirectory,
  writeFile = fs.writeFile
}) {
  if (!dialog || typeof dialog.showSaveDialog !== 'function') {
    throw new TypeError('原生保存对话框不可用');
  }

  const normalized = normalizeSaveRequest(request);
  const defaultPath = path.join(String(defaultDirectory || ''), normalized.suggestedName);
  const result = await dialog.showSaveDialog(parentWindow || undefined, {
    title: normalized.spec.title,
    buttonLabel: normalized.spec.buttonLabel,
    defaultPath,
    filters: [{
      name: normalized.spec.filterName,
      extensions: [normalized.spec.extension.slice(1)]
    }],
    properties: ['createDirectory', 'showOverwriteConfirmation']
  });

  if (!result || result.canceled || !result.filePath) {
    return Object.freeze({ ok: false, canceled: true });
  }

  const targetPath = ensureRequiredExtension(result.filePath, normalized.spec.extension);
  await writeFile(targetPath, normalized.content, { encoding: 'utf8', flag: 'w' });
  return Object.freeze({
    ok: true,
    canceled: false,
    fileName: path.basename(targetPath)
  });
}

async function savePatStreamWithDialog({
  dialog,
  parentWindow,
  sourcePath,
  suggestedName,
  defaultDirectory,
  stat = fs.stat,
  createReadStream = fsSync.createReadStream,
  createWriteStream = fsSync.createWriteStream,
  streamPipeline = pipeline
}) {
  if (!dialog || typeof dialog.showSaveDialog !== 'function') {
    throw new TypeError('原生保存对话框不可用');
  }
  if (typeof sourcePath !== 'string' || !path.isAbsolute(sourcePath)) {
    throw new TypeError('大 PAT 临时文件路径无效');
  }
  if (typeof suggestedName !== 'string' || suggestedName.length > 1024) {
    throw new TypeError('大 PAT 文件名无效');
  }

  const sourceStat = await stat(sourcePath);
  if (!sourceStat || typeof sourceStat.isFile !== 'function' || !sourceStat.isFile()) {
    throw new TypeError('大 PAT 临时文件无效');
  }
  const safeName = sanitizeSuggestedName(suggestedName, 'pat');
  const defaultPath = path.join(String(defaultDirectory || ''), safeName);
  const result = await dialog.showSaveDialog(parentWindow || undefined, {
    title: SAVE_TYPES.pat.title,
    buttonLabel: SAVE_TYPES.pat.buttonLabel,
    defaultPath,
    filters: [{
      name: SAVE_TYPES.pat.filterName,
      extensions: [SAVE_TYPES.pat.extension.slice(1)]
    }],
    properties: ['createDirectory', 'showOverwriteConfirmation']
  });

  // The target is not opened until the user confirms the native dialog.
  if (!result || result.canceled || !result.filePath) {
    return Object.freeze({ ok: false, canceled: true });
  }

  const targetPath = ensureRequiredExtension(result.filePath, SAVE_TYPES.pat.extension);
  if (path.resolve(targetPath) === path.resolve(sourcePath)) {
    throw new TypeError('保存目标不能是大 PAT 临时文件');
  }
  await streamPipeline(
    createReadStream(sourcePath),
    createWriteStream(targetPath, { flags: 'w', mode: 0o600 })
  );
  return Object.freeze({
    ok: true,
    canceled: false,
    fileName: path.basename(targetPath),
    sizeBytes: sourceStat.size
  });
}

module.exports = {
  SAVE_TYPES,
  ensureRequiredExtension,
  normalizeCrlf,
  normalizeSaveRequest,
  sanitizeSuggestedName,
  savePatStreamWithDialog,
  saveFileWithDialog
};
