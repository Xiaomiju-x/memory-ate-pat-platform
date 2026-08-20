'use strict';

const path = require('node:path');
const { fileURLToPath } = require('node:url');
const { app, BrowserWindow, dialog, ipcMain, Menu, session } = require('electron');
const { LargePatStore, LargePatStoreError, assertExactObject } = require('./large-pat-store');
const { saveFileWithDialog, savePatStreamWithDialog } = require('./save-file');

const RENDERER_DIRECTORY = path.join(__dirname, 'renderer');
const RENDERER_ENTRY = path.join(RENDERER_DIRECTORY, 'index.html');
const SAVE_CHANNEL = 'file:save';
const LARGE_PAT_CHANNELS = Object.freeze({
  create: 'large-pat:create',
  append: 'large-pat:append',
  finalize: 'large-pat:finalize',
  read: 'large-pat:read',
  save: 'large-pat:save',
  discard: 'large-pat:discard'
});

let mainWindow = null;
let largePatStore = null;
let largePatCleanupStarted = false;

app.commandLine.appendSwitch('disable-background-networking');
app.commandLine.appendSwitch('disable-component-update');
app.commandLine.appendSwitch('disable-sync');
app.commandLine.appendSwitch('no-pings');

function isTrustedRendererUrl(rawUrl) {
  try {
    const url = new URL(rawUrl);
    if (url.protocol !== 'file:') return false;
    const candidate = path.resolve(fileURLToPath(url));
    const relative = path.relative(path.resolve(RENDERER_DIRECTORY), candidate);
    return relative === '' || (!relative.startsWith('..' + path.sep) && relative !== '..' && !path.isAbsolute(relative));
  } catch (error) {
    return false;
  }
}

function installSessionGuards(activeSession) {
  activeSession.setPermissionCheckHandler(() => false);
  activeSession.setPermissionRequestHandler((_webContents, _permission, callback) => callback(false));
  activeSession.webRequest.onBeforeRequest((details, callback) => {
    try {
      const protocol = new URL(details.url).protocol;
      callback({ cancel: !['file:', 'data:', 'blob:', 'about:'].includes(protocol) });
    } catch (error) {
      callback({ cancel: true });
    }
  });
  activeSession.on('will-download', event => event.preventDefault());
}

function hardenWebContents(webContents) {
  webContents.setWindowOpenHandler(() => ({ action: 'deny' }));
  webContents.on('will-navigate', (event, targetUrl) => {
    if (!isTrustedRendererUrl(targetUrl)) event.preventDefault();
  });
  webContents.on('will-attach-webview', event => event.preventDefault());
  webContents.on('before-input-event', (event, input) => {
    const key = String(input.key || '').toLowerCase();
    const blocked = key === 'f12' || (input.control && input.shift && ['i', 'j', 'c'].includes(key));
    if (blocked) event.preventDefault();
  });
  webContents.on('devtools-opened', () => webContents.closeDevTools());
}

function registerSaveHandler() {
  ipcMain.removeHandler(SAVE_CHANNEL);
  ipcMain.handle(SAVE_CHANNEL, async (event, request) => {
    if (!event.senderFrame || !isTrustedRendererUrl(event.senderFrame.url)) {
      return { ok: false, canceled: false };
    }

    try {
      return await saveFileWithDialog({
        dialog,
        parentWindow: BrowserWindow.fromWebContents(event.sender),
        request,
        defaultDirectory: app.getPath('documents')
      });
    } catch (error) {
      console.error('保存文件失败：', error);
      return { ok: false, canceled: false };
    }
  });
}

function largePatFailure(error) {
  if (error instanceof LargePatStoreError) {
    return Object.freeze({ ok: false, canceled: false, code: error.code, message: error.message });
  }
  console.error('大 PAT 后端操作失败：', error);
  return Object.freeze({ ok: false, canceled: false, code: 'IO_ERROR', message: '大 PAT 后端操作失败，请检查磁盘空间和目标路径权限。' });
}

function isTrustedIpcEvent(event) {
  return Boolean(event && event.senderFrame && isTrustedRendererUrl(event.senderFrame.url));
}

function registerLargePatHandlers(store) {
  if (!store || typeof store.createFile !== 'function') throw new TypeError('大 PAT 临时存储不可用');
  Object.values(LARGE_PAT_CHANNELS).forEach(channel => ipcMain.removeHandler(channel));

  const handle = (channel, operation) => {
    ipcMain.handle(channel, async (event, request) => {
      if (!isTrustedIpcEvent(event)) {
        return Object.freeze({ ok: false, canceled: false, code: 'UNTRUSTED_SENDER', message: '请求来源无效。' });
      }
      try {
        const result = await operation(event, request);
        return Object.freeze({ ok: true, ...result });
      } catch (error) {
        return largePatFailure(error);
      }
    });
  };

  handle(LARGE_PAT_CHANNELS.create, (_event, request) => store.createFile(request));
  handle(LARGE_PAT_CHANNELS.append, (_event, request) => store.append(request));
  handle(LARGE_PAT_CHANNELS.finalize, (_event, request) => store.finalize(request));
  handle(LARGE_PAT_CHANNELS.read, (_event, request) => store.readChunk(request));
  handle(LARGE_PAT_CHANNELS.discard, (_event, request) => store.discard(request));
  handle(LARGE_PAT_CHANNELS.save, async (event, request) => {
    assertExactObject(request, ['token', 'suggestedName']);
    if (typeof request.suggestedName !== 'string' || request.suggestedName.length > 1024) {
      throw new LargePatStoreError('INVALID_REQUEST', '大 PAT 文件名无效。');
    }
    return store.withFinalizedSource({ token: request.token }, source => savePatStreamWithDialog({
      dialog,
      parentWindow: BrowserWindow.fromWebContents(event.sender),
      sourcePath: source.filePath,
      suggestedName: request.suggestedName,
      defaultDirectory: app.getPath('documents')
    }));
  });
}

async function createMainWindow({ show = true } = {}) {
  const window = new BrowserWindow({
    title: 'PAT生成工具',
    width: 1440,
    height: 900,
    minWidth: 1100,
    minHeight: 700,
    show: false,
    autoHideMenuBar: true,
    backgroundColor: '#181818',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: true,
      webSecurity: true,
      allowRunningInsecureContent: false,
      devTools: false,
      spellcheck: false,
      navigateOnDragDrop: false,
      safeDialogs: true
    }
  });

  window.removeMenu();
  hardenWebContents(window.webContents);
  await window.loadFile(RENDERER_ENTRY);
  if (show) window.show();
  return window;
}

async function bootstrap() {
  const hasLock = app.requestSingleInstanceLock();
  if (!hasLock) {
    app.quit();
    return;
  }

  app.setAppUserModelId('com.pat.generator.tool');
  app.on('second-instance', () => {
    if (!mainWindow || mainWindow.isDestroyed()) return;
    if (mainWindow.isMinimized()) mainWindow.restore();
    mainWindow.show();
    mainWindow.focus();
  });

  await app.whenReady();
  Menu.setApplicationMenu(null);
  installSessionGuards(session.defaultSession);
  registerSaveHandler();
  largePatStore = await LargePatStore.create();
  registerLargePatHandlers(largePatStore);
  mainWindow = await createMainWindow();

  app.on('activate', async () => {
    if (BrowserWindow.getAllWindows().length === 0) mainWindow = await createMainWindow();
  });
}

if (require.main === module) {
  bootstrap().catch(error => {
    console.error('PAT生成工具启动失败：', error);
    app.quit();
  });
}

app.on('window-all-closed', () => app.quit());
app.on('before-quit', event => {
  if (!largePatStore || largePatCleanupStarted) return;
  event.preventDefault();
  largePatCleanupStarted = true;
  const store = largePatStore;
  store.cleanupAll()
    .catch(error => console.error('清理大 PAT 临时文件失败：', error))
    .finally(() => {
      largePatStore = null;
      app.quit();
    });
});
app.on('will-quit', () => {
  if (!largePatStore) return;
  try {
    largePatStore.cleanupAllSync();
  } catch (error) {
    console.error('同步清理大 PAT 临时文件失败：', error);
  }
  largePatStore = null;
});

module.exports = {
  LARGE_PAT_CHANNELS,
  RENDERER_DIRECTORY,
  RENDERER_ENTRY,
  SAVE_CHANNEL,
  createMainWindow,
  hardenWebContents,
  installSessionGuards,
  isTrustedRendererUrl,
  isTrustedIpcEvent,
  largePatFailure,
  registerLargePatHandlers,
  registerSaveHandler
};
