'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');

const projectRoot = path.resolve(__dirname, '..');
const repositoryRoot = path.resolve(projectRoot, '..');

function read(...parts) {
  return fs.readFileSync(path.join(...parts), 'utf8');
}

function publicTextFiles(directory, relative = '') {
  const excludedDirectories = new Set(['dist', 'licenses', 'node_modules', 'source', 'vendor', 'work']);
  const files = [];
  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    if (entry.isDirectory() && excludedDirectories.has(entry.name)) continue;
    const childRelative = path.join(relative, entry.name);
    const childPath = path.join(directory, entry.name);
    if (entry.isDirectory()) files.push(...publicTextFiles(childPath, childRelative));
    if (!entry.isFile()) continue;
    if (entry.name === 'package-lock.json' || entry.name === 'publication-boundary.test.js') continue;
    if (/\.(?:bat|html|js|json|md|nvmrc|ya?ml)$/i.test(entry.name) || entry.name === '.nvmrc') files.push(childRelative);
  }
  return files;
}

test('public finals source excludes internal provenance identifiers', () => {
  const forbidden = /AI\s*训练|学习依据|训练(?:文件|版)|黄金\s*PAT|按之前要求|@TRAIN|_[A-Z0-9]+[\\/](?:SRAM|EEPROM)/i;
  const hits = publicTextFiles(projectRoot).filter(relative => forbidden.test(read(projectRoot, relative)));
  assert.deepEqual(hits, []);

  const ignore = read(repositoryRoot, '.gitignore');
  assert.match(ignore, /^\/national-final\/source\/$/m, '私有历史兼容快照必须被 Git 排除');
  assert.match(ignore, /^\/national-final\/tests\/compatibility-contract\.js$/m);
  assert.match(ignore, /^\/national-final\/tests\/incremental-compatibility\.test\.js$/m);
  assert.match(ignore, /^\/national-final\/tests\/incremental-compatibility-smoke\.js$/m);
});

test('Apache and vendored dependency licenses are part of the portable build inputs', () => {
  const packageJson = JSON.parse(read(projectRoot, 'package.json'));
  assert.equal(packageJson.license, 'Apache-2.0');
  assert.equal(packageJson.packageManager, 'npm@10.9.0');
  assert.equal(packageJson.engines.node, '>=22.12.0');

  const builder = read(projectRoot, 'electron-builder.yml');
  assert.match(builder, /- THIRD_PARTY_NOTICES\.md/);
  assert.match(builder, /- licenses\/\*\*\/\*/);
  assert.match(builder, /from: \.\.\/LICENSE/);

  assert.match(read(projectRoot, 'licenses', 'FLOATING_UI_LICENSE.txt'), /^MIT License/m);
  assert.match(read(projectRoot, 'licenses', 'LUCIDE_LICENSE.txt'), /^ISC License/m);
});
