'use strict';

const fs = require('node:fs');
const path = require('node:path');
const { spawnSync } = require('node:child_process');

const projectRoot = path.resolve(__dirname, '..');
const distDirectory = path.join(projectRoot, 'dist');
const artifactName = 'PAT生成工具.exe';
const artifactPath = path.join(distDirectory, artifactName);

if (path.dirname(distDirectory) !== projectRoot || path.basename(distDirectory) !== 'dist') {
  throw new Error('拒绝清理非项目 dist 目录');
}

fs.rmSync(distDirectory, { recursive: true, force: true });

const builderCli = require.resolve('electron-builder/cli.js');
const result = spawnSync(process.execPath, [builderCli, '--config', 'electron-builder.yml'], {
  cwd: projectRoot,
  env: process.env,
  stdio: 'inherit',
  windowsHide: true
});
if (result.error) throw result.error;
if (result.status !== 0) process.exit(result.status || 1);
if (!fs.existsSync(artifactPath) || !fs.statSync(artifactPath).isFile()) {
  throw new Error(`未找到便携版产物：${artifactPath}`);
}

for (const entry of fs.readdirSync(distDirectory, { withFileTypes: true })) {
  if (entry.name === artifactName && entry.isFile()) continue;
  fs.rmSync(path.join(distDirectory, entry.name), { recursive: true, force: true });
}

const remaining = fs.readdirSync(distDirectory);
if (remaining.length !== 1 || remaining[0] !== artifactName) {
  throw new Error('dist 目录必须只保留一个便携版 EXE');
}
console.log(`便携版构建完成：${artifactPath}`);
