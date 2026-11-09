import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile, writeFile, unlink } from 'node:fs/promises';
import { spawnSync } from 'node:child_process';
import { randomUUID } from 'node:crypto';

const readJson = async (path) => JSON.parse(await readFile(path, 'utf8'));

test('build includes searchable metadata and every static chapter and verse', async () => {
  const [book, catalog, index] = await Promise.all([
    readJson('src/data/books/thirukkural.json'),
    readJson('src/data/library.json'),
    readJson('dist/search-index.json'),
  ]);
  assert.equal(index.filter((item) => item.type === 'book').length, catalog.length);
  assert.equal(index.filter((item) => item.type === 'chapter').length, book.athikarams.length);
  assert.equal(index.filter((item) => item.type === 'verse').length, 1330);
  for (const entry of catalog) {
    const item = index.find((result) => result.type === 'book' && result.title === entry.title_ta);
    assert.ok(item);
    assert.ok(item.searchable.includes(entry.author_en));
    assert.ok(item.searchable.includes(entry.genre_en));
    assert.equal(Boolean(item.url), entry.is_available);
  }
  for (const chapter of book.athikarams) {
    const html = await readFile(`dist/book/thirukkural/read/${chapter.number}/index.html`, 'utf8');
    if (chapter.number > 1) assert.ok(html.includes(`href="/book/thirukkural/read/${chapter.number - 1}/"`));
    if (chapter.number < book.athikarams.length) assert.ok(html.includes(`href="/book/thirukkural/read/${chapter.number + 1}/"`));
    for (const verse of chapter.kurals) {
      assert.ok(html.includes(`id="kural-${verse.number}"`));
      assert.ok(html.includes(verse.line1));
      const item = index.find((result) => result.url === `/book/thirukkural/read/${chapter.number}/#kural-${verse.number}`);
      const normalize = (text) => text.replace(/\s+/g, ' ');
      assert.ok(item?.searchable.some((text) => normalize(text).includes(normalize(verse.line1))));
      assert.ok(item?.searchable.some((text) => normalize(text).includes(normalize(verse.line2))));
    }
  }
});

test('new Markdown and text books are discovered automatically', async () => {
  const suffix = randomUUID().slice(0, 8);
  const ids = [`test-markdown-${suffix}`, `test-text-${suffix}`];
  const paths = ids.map((id, i) => `src/content/books/${id}.${i ? 'txt' : 'md'}`);
  const makeBook = (id) => `---
id: ${id}
title: சோதனை நூல்
author: சோதனை ஆசிரியர்
genre: சோதனை வகை
description: மாதிரி விளக்கம்
acknowledgement: மாதிரி நன்றியுரை
pdf: /downloads/sample.pdf
epub: https://example.com/book.epub
aliases: [Sample Test Alias]
---

# முதல் தொகுப்பு

## முதல் பகுதி {#first}

### முதல் பாடல் {#verse-1}

**சிறப்பான** மாதிரி வரி
இரண்டாம் வரி

## அடுத்த பகுதி {#second}

இரண்டாம் பகுதியின் உரை
`;
  const created = [];
  function build() {
    const result = spawnSync('npm', ['run', 'build'], { encoding: 'utf8' });
    assert.equal(result.status, 0, result.stderr || result.stdout);
  }
  try {
    for (let i = 0; i < paths.length; i++) {
      await writeFile(paths[i], makeBook(ids[i]), { flag: 'wx' });
      created.push(paths[i]);
    }
    build();
    const index = await readJson('dist/search-index.json');
    const home = await readFile('dist/index.html', 'utf8');
    for (const id of ids) {
      assert.ok(home.includes(`/book/${id}`));
      const landing = await readFile(`dist/book/${id}/index.html`, 'utf8');
      assert.ok(landing.includes('மாதிரி நன்றியுரை'));
      assert.ok(landing.includes('/downloads/sample.pdf'));
      assert.ok(landing.includes('https://example.com/book.epub'));
      const reader = await readFile(`dist/book/${id}/read/first/index.html`, 'utf8');
      assert.ok(reader.includes('<strong>சிறப்பான</strong>'));
      assert.ok(reader.includes('id="verse-1"'));
      assert.ok(reader.includes(`/book/${id}/read/second/`));
      assert.ok(index.some((item) => item.searchable.includes('Sample Test Alias') && item.url === `/book/${id}`));
      assert.ok(index.some((item) => item.searchable.some((value) => value.includes('மாதிரி வரி')) && item.url === `/book/${id}/read/first/#verse-1`));
    }
    await writeFile(paths[1], makeBook(ids[0]));
    const invalid = spawnSync('npm', ['run', 'build'], { encoding: 'utf8' });
    assert.notEqual(invalid.status, 0);
    assert.match(invalid.stdout + invalid.stderr, /Duplicate book id/);
  } finally {
    for (const path of created) await unlink(path);
    build();
  }
});

test('legacy reader exposes chapter links without JavaScript', async () => {
  const html = await readFile('dist/book/thirukkural/read/index.html', 'utf8');
  assert.ok(html.includes('href="/book/thirukkural/read/1/"'));
  assert.ok(html.includes('href="/book/thirukkural/read/133/"'));
});

test('production output uses the custom domain and root-relative assets', async () => {
  const [html, manifest] = await Promise.all([
    readFile('dist/index.html', 'utf8'),
    readJson('dist/manifest.json'),
  ]);
  assert.ok(html.includes('content="https://arivupezhai.com/icon-512.png"'));
  assert.ok(html.includes('href="/manifest.json"'));
  assert.ok(!html.includes('/arivupezhai/'));
  assert.equal(manifest.start_url, '/');
  assert.equal(manifest.scope, '/');
  assert.deepEqual(manifest.icons.map((icon) => icon.src), ['/icon-192.png', '/icon-512.png']);
});
