'use strict';

const { contextBridge, ipcRenderer } = require('electron');

function requestObject(value) {
  return value && typeof value === 'object' && !Array.isArray(value) ? value : Object.create(null);
}

contextBridge.exposeInMainWorld('desktopAPI', Object.freeze({
  saveFile(request) {
    const safeRequest = {
      suggestedName: String(request && request.suggestedName || ''),
      content: String(request && request.content || ''),
      extension: String(request && request.extension || ''),
      kind: String(request && request.kind || '')
    };
    return ipcRenderer.invoke('file:save', safeRequest);
  },
  createLargePat(request) {
    const source = requestObject(request);
    return ipcRenderer.invoke('large-pat:create', { expectedLines: source.expectedLines });
  },
  appendLargePat(request) {
    const source = requestObject(request);
    return ipcRenderer.invoke('large-pat:append', {
      token: source.token,
      chunk: String(source.content == null ? '' : source.content)
    });
  },
  finalizeLargePat(request) {
    const source = requestObject(request);
    return ipcRenderer.invoke('large-pat:finalize', { token: source.token });
  },
  readLargePatChunk(request) {
    const source = requestObject(request);
    return ipcRenderer.invoke('large-pat:read', { token: source.token, offset: source.offset, length: source.length });
  },
  saveLargePat(request) {
    const source = requestObject(request);
    const safeRequest = { token: source.token, suggestedName: source.suggestedName };
    return ipcRenderer.invoke('large-pat:save', safeRequest);
  },
  discardLargePat(request) {
    const source = requestObject(request);
    return ipcRenderer.invoke('large-pat:discard', { token: source.token });
  }
}));
