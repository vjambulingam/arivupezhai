import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile, writeFile, unlink, readdir } from 'node:fs/promises';
import { spawnSync } from 'node:child_process';
import { createHash, randomUUID } from 'node:crypto';

const readJson = async (path) => JSON.parse(await readFile(path, 'utf8'));

test('build includes searchable metadata and every static chapter and verse', async () => {
  const [book, catalog, index] = await Promise.all([
    readJson('src/data/books/thirukkural.json'),
    readJson('src/data/library.json'),
    readJson('dist/search-index.json'),
  ]);
  assert.ok(index.filter((item) => item.type === 'book').length >= catalog.length);
  assert.equal(index.filter((item) => item.type === 'chapter' && item.url?.startsWith('/book/thirukkural/')).length, book.athikarams.length);
  assert.equal(index.filter((item) => item.type === 'verse' && item.url?.startsWith('/book/thirukkural/')).length, 1330);
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

test('AP002 publishes all sections and verses with attribution and search', async () => {
  const [source, landing, home, index] = await Promise.all([
    readFile('src/content/books/AP002-aathichudi.md', 'utf8'),
    readFile('dist/book/aathichudi/index.html', 'utf8'),
    readFile('dist/index.html', 'utf8'),
    readJson('dist/search-index.json'),
  ]);
  assert.ok(home.includes('/book/aathichudi'));
  assert.ok(landing.includes('ஒளவையார்'));
  assert.ok(landing.includes('Credits to Project Madurai team @ www.projectmadurai.org'));
  assert.ok(index.some((item) => item.type === 'book' && item.url === '/book/aathichudi' && item.searchable.includes('ஆத்திச்சூடி')));
  const sections = [...source.matchAll(/^## .+ \{#([^}]+)\}$/gm)].map((match) => match[1]);
  assert.equal(sections.length, 10);
  let number = 0;
  for (const section of sections) {
    const html = await readFile(`dist/book/aathichudi/read/${section}/index.html`, 'utf8');
    const sectionIndex = index.filter((item) => item.type === 'verse' && item.url?.startsWith(`/book/aathichudi/read/${section}/`));
    const text = source.split(`{#${section}}`)[1].split(/^## /m)[0];
    for (const match of text.matchAll(/^### (\d+) \{#verse-(\d+)\}\n\n(.+)$/gm)) {
      number++;
      assert.equal(Number(match[1]), number);
      assert.equal(Number(match[2]), number);
      assert.ok(html.includes(`id="verse-${number}"`));
      assert.ok(html.includes(match[3]));
      assert.ok(sectionIndex.some((item) => item.url.endsWith(`#verse-${number}`) && item.searchable.includes(match[3])));
    }
  }
  assert.equal(number, 109);
  assert.ok(source.includes('அறம் செய விரும்பு.'));
  assert.ok(source.includes('ஓரம் சொல்லேல்.'));
  assert.ok(!source.includes('அன்னையும் பிதாவும் முன்னறி தெய்வம்.'));
});

test('AP003 to AP005 publish the source sections and searchable verses', async () => {
  const [home, index] = await Promise.all([
    readFile('dist/index.html', 'utf8'),
    readJson('dist/search-index.json'),
  ]);
  const cases = [
    { id: 'AP003', slug: 'kondrai-vendhan', file: 'AP003-kondrai-vendhan.md', title: 'கொன்றை வேந்தன்', sections: 9, verses: 91, first: 'அன்னையும் பிதாவும் முன்னறி தெய்வம்.', last: 'ஓதாதார்க்கு இல்லை உணர்வொடும் ஒழுக்கம்.' },
    { id: 'AP004', slug: 'nalvazhi', file: 'AP004-nalvazhi.md', title: 'நல்வழி', sections: 2, verses: 40, first: 'புண்ணியம்ஆம் பாவம்போல் போனநாள் செய்தஅவை', last: 'ஒருவா சகமென் றுணர்.' },
    { id: 'AP005', slug: 'moodhurai', file: 'AP005-moodhurai.md', title: 'மூதுரை', sections: 2, verses: 30, first: 'நன்றி ஒருவர்க்குச் செய்தக்கால் அந்நன்றி', last: 'மறைக்குமாம் கண்டீர் மரம்.' },
  ];
  for (const book of cases) {
    const [source, landing] = await Promise.all([
      readFile(`src/content/books/${book.file}`, 'utf8'),
      readFile(`dist/book/${book.slug}/index.html`, 'utf8'),
    ]);
    assert.ok(home.includes(`/book/${book.slug}`));
    assert.ok(landing.includes(book.title));
    assert.ok(landing.includes('ஒளவையார்'));
    assert.ok(landing.includes('Credits to Project Madurai team @ www.projectmadurai.org'));
    assert.ok(index.some((item) => item.type === 'book' && item.url === `/book/${book.slug}` && item.searchable.includes(book.title)));
    assert.ok(source.includes(book.first));
    assert.ok(source.includes(book.last));
    const sections = [...source.matchAll(/^## .+ \{#([^}]+)\}$/gm)].map((match) => match[1]);
    assert.equal(sections.length, book.sections);
    let number = 0;
    for (const section of sections) {
      const html = await readFile(`dist/book/${book.slug}/read/${section}/index.html`, 'utf8');
      const text = source.split(`{#${section}}`)[1].split(/^## /m)[0];
      for (const match of text.matchAll(/^### \d+ \{#verse-(\d+)\}\n\n([\s\S]*?)(?=\n### |\n## |(?![\s\S]))/gm)) {
        number++;
        assert.equal(Number(match[1]), number);
        assert.ok(html.includes(`id="verse-${number}"`));
        const searchable = match[2].replace(/[*_`#\[\]()]/g, '').trim().replace(/\s+/g, ' ');
        assert.ok(index.some((item) => item.url === `/book/${book.slug}/read/${section}/#verse-${number}` && item.searchable.includes(searchable)));
      }
    }
    assert.equal(number, book.verses);
    if (book.id === 'AP004') {
      assert.match(source, /### 11 \{#verse-10\}/);
      assert.match(source, /### 11 \{#verse-11\}/);
    }
  }
});

test('book list includes available books with bilingual metadata and stable catalog IDs', async () => {
  const [html, home, index] = await Promise.all([
    readFile('dist/catalog/index.html', 'utf8'),
    readFile('dist/index.html', 'utf8'),
    readJson('dist/search-index.json'),
  ]);
  const header = home.split('<header')[1].split('</header>')[0];
  assert.equal((header.match(/href="\/catalog"/g) || []).length, 2);
  assert.ok(!header.includes('href="/book/thirukkural"'));
  assert.ok(html.includes('<table'));
  assert.ok(html.includes('scope="col"'));
  assert.ok(html.includes('scope="row"'));
  const rows = [...html.matchAll(/<tr class="border-t[^"]*">([\s\S]*?)<\/tr>/g)].map((match) => match[1]);
  assert.equal(rows.length, index.filter((item) => item.type === 'book' && item.url).length);
  for (const [id, route, title, titleEn, author, authorEn, genre, genreEn] of [
    ['AP001', 'thirukkural', 'திருக்குறள்', 'Thirukkural', 'திருவள்ளுவர்', 'Thiruvalluvar', 'நீதிநெறி நூல்கள்', 'Ethical Literature'],
    ['AP002', 'aathichudi', 'ஆத்திசூடி', 'Aathichudi', 'ஒளவையார்', 'Avvaiyar', 'நீதிநெறி நூல்கள்', 'Ethical Literature'],
    ['AP003', 'kondrai-vendhan', 'கொன்றை வேந்தன்', 'Kondrai Vendhan', 'ஒளவையார்', 'Avvaiyar', 'நீதிநெறி நூல்கள்', 'Ethical Literature'],
    ['AP004', 'nalvazhi', 'நல்வழி', 'Nalvazhi', 'ஒளவையார்', 'Avvaiyar', 'நீதிநெறி நூல்கள்', 'Ethical Literature'],
    ['AP005', 'moodhurai', 'மூதுரை', 'Moodhurai', 'ஒளவையார்', 'Avvaiyar', 'நீதிநெறி நூல்கள்', 'Ethical Literature'],
    ['AP006', 'thiruvaasagam', 'திருவாசகம்', 'Thiruvaasagam', 'மாணிக்க வாசகர்', 'Maanikkavasakar', 'சமயம் - சைவம்', 'Saiva Literature'],
  ]) {
    const row = rows.find((value) => value.includes(`>${id}</td>`));
    assert.ok(row, `Missing ${id}`);
    for (const value of [`href="/book/${route}"`, title, titleEn, author, authorEn, genre, genreEn]) assert.ok(row.includes(value), `${id}: ${value}`);
  }
});

test('only valid books exist in dist/book and redirect books are not generated', async () => {
  const entries = await readdir('dist/book');
  const validSlugs = new Set(['thirukkural', 'aathichudi', 'kondrai-vendhan', 'nalvazhi', 'moodhurai', 'thiruvaasagam', 'thirumanthiram']);
  assert.deepEqual(new Set(entries), validSlugs);
});

test('new Markdown and text books are discovered automatically', async () => {
  const suffix = randomUUID().slice(0, 8);
  const ids = [`AP${BigInt(`0x${suffix}`).toString().padStart(3, '0')}`, `test-text-${suffix}`];
  const slugs = [`test-markdown-${suffix}`, ids[1]];
  const paths = ids.map((id, i) => `src/content/books/${id}.${i ? 'txt' : 'md'}`);
  const makeBook = (id, hierarchical = false, slug = id === ids[0] ? slugs[0] : slugs[1]) => `---
id: ${id}
slug: ${slug}
title: சோதனை நூல்
author: சோதனை ஆசிரியர்
genre: சோதனை வகை
description: மாதிரி விளக்கம்
period: சோதனைக் காலம்
acknowledgement: மாதிரி நன்றியுரை
pdf: /downloads/sample.pdf
epub: https://example.com/book.epub
aliases: [Sample Test Alias]
---

${hierarchical ? '# முதல் தொகுப்பு / உட்பிரிவு / ஆழ்நிலை' : ''}

## முதல் பகுதி {#first}

### முதல் பாடல் {#verse-1}

**சிறப்பான** மாதிரி வரி
இரண்டாம் வரி

அடுத்த பத்தியின் வரி

${hierarchical ? '# வேறு தொகுப்பு' : ''}

## அடுத்த பகுதி {#second}

இரண்டாம் பகுதியின் உரை
${'தமிழ் '.repeat(150)}
`;
  const created = [];
  function build() {
    const result = spawnSync('npm', ['run', 'build'], { encoding: 'utf8' });
    assert.equal(result.status, 0, result.stderr || result.stdout);
  }
  try {
    for (let i = 0; i < paths.length; i++) {
      await writeFile(paths[i], makeBook(ids[i], i === 0), { flag: 'wx' });
      created.push(paths[i]);
    }
    build();
    const index = await readJson('dist/search-index.json');
    const home = await readFile('dist/index.html', 'utf8');
    const catalogPage = await readFile('dist/catalog/index.html', 'utf8');
    assert.ok(!home.includes('முழுப் பதிப்பு'));
    for (const [i, id] of ids.entries()) {
      const slug = slugs[i];
      assert.ok(home.includes(`/book/${slug}`));
      assert.ok(catalogPage.includes(`>${id}</td>`));
      assert.ok(catalogPage.includes(`href="/book/${slug}"`));
      const card = home.split(`<a href="/book/${slug}"`)[0].split('<!-- Top Metadata Badges -->').at(-1);
      assert.match(card, /<span class="[^"]*rounded-full[^"]*">\s*சுமார் 2 நிமிட வாசிப்பு\s*<\/span>/);
      assert.ok(!card.includes('சோதனைக் காலம்'));
      const landing = await readFile(`dist/book/${slug}/index.html`, 'utf8');
      assert.ok(landing.includes('மாதிரி நன்றியுரை'));
      assert.ok(landing.includes('சோதனைக் காலம்'));
      assert.ok(landing.includes('/downloads/sample.pdf'));
      assert.ok(landing.includes('https://example.com/book.epub'));
      const reader = await readFile(`dist/book/${slug}/read/first/index.html`, 'utf8');
      assert.ok(reader.includes('<strong>சிறப்பான</strong>'));
      assert.match(reader, /<p><strong>சிறப்பான<\/strong> மாதிரி வரி<br>இரண்டாம் வரி<\/p>\s*<p>அடுத்த பத்தியின் வரி<\/p>/);
      assert.ok(reader.includes('id="verse-1"'));
      assert.ok(reader.includes(`/book/${slug}/read/second/`));
      assert.ok(index.some((item) => item.searchable.includes('Sample Test Alias') && item.url === `/book/${slug}`));
      assert.ok(index.some((item) => item.searchable.some((value) => value.includes('மாதிரி வரி')) && item.url === `/book/${slug}/read/first/#verse-1`));
    }
    const hierarchicalLanding = await readFile(`dist/book/${slugs[0]}/index.html`, 'utf8');
    const hierarchicalReader = await readFile(`dist/book/${slugs[0]}/read/first/index.html`, 'utf8');
    const flatLanding = await readFile(`dist/book/${slugs[1]}/index.html`, 'utf8');
    assert.ok(hierarchicalLanding.includes('data-group="முதல் தொகுப்பு / உட்பிரிவு / ஆழ்நிலை"'));
    assert.ok(hierarchicalLanding.includes('data-group="முதல் தொகுப்பு / உட்பிரிவு"'));
    assert.ok(hierarchicalLanding.includes('data-group="வேறு தொகுப்பு"'));
    assert.ok(hierarchicalReader.includes('முதல் தொகுப்பு / உட்பிரிவு / ஆழ்நிலை'));
    assert.ok(hierarchicalReader.includes('முதல் தொகுப்பு / உட்பிரிவு / ஆழ்நிலை / முதல் பகுதி'));
    assert.ok(!flatLanding.includes('data-group="முதல் தொகுப்பு"'));
    assert.ok(index.some((item) => item.url === `/book/${slugs[0]}/read/first/` && item.searchable.includes('ஆழ்நிலை')));
    await writeFile(paths[1], makeBook(ids[0]));
    const invalid = spawnSync('npm', ['run', 'build'], { encoding: 'utf8' });
    assert.notEqual(invalid.status, 0);
    assert.match(invalid.stdout + invalid.stderr, /Duplicate book id/);
    await writeFile(paths[1], makeBook(ids[1]).replace(`id: ${ids[1]}`, `id: ${ids[1]}\ncatalog_id: ${ids[0]}`));
    const duplicateCatalog = spawnSync('npm', ['run', 'build'], { encoding: 'utf8' });
    assert.notEqual(duplicateCatalog.status, 0);
    assert.match(duplicateCatalog.stdout + duplicateCatalog.stderr, /Duplicate catalog id/);
    await writeFile(paths[1], makeBook(ids[1], false, slugs[0]));
    const duplicateRoute = spawnSync('npm', ['run', 'build'], { encoding: 'utf8' });
    assert.notEqual(duplicateRoute.status, 0);
    assert.match(duplicateRoute.stdout + duplicateRoute.stderr, /Duplicate book route/);
    await writeFile(paths[1], makeBook(ids[1], false, ids[0].toLowerCase()));
    const legacyCollision = spawnSync('npm', ['run', 'build'], { encoding: 'utf8' });
    assert.notEqual(legacyCollision.status, 0);
    assert.match(legacyCollision.stdout + legacyCollision.stderr, /Duplicate book route/);
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
