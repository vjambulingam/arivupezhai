import test from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { parse } from 'yaml';

test('Thirumandiram edition retains its source text and publishes all sections and verse anchors', async () => {
  const [catalog, index, source] = await Promise.all([
    readFile('src/data/project-madurai-catalog.json', 'utf8').then(JSON.parse),
    readFile('dist/search-index.json', 'utf8').then(JSON.parse),
    readFile('src/content/books/thirumanthiram.md', 'utf8'),
  ]);
  const match = source.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
  assert.ok(match);
  const metadata = parse(match[1]);
  const body = match[2];

  assert.equal(metadata.id, 'thirumanthiram');
  assert.equal(metadata.slug, 'thirumanthiram');
  assert.equal(metadata.catalog_id, 'AP008');
  assert.equal(metadata.title, 'திருமந்திரம்');
  assert.ok(metadata.pdf);
  assert.ok(metadata.acknowledgement.includes('You are welcome to freely distribute this file, provided this header page is kept intact.'));

  const tantrams = [...body.matchAll(/^# ([^\n]+)$/gm)];
  assert.equal(tantrams.length, 10);

  const sections = [...body.matchAll(/^## .+ \{#([^}]+)\}\s*$/gm)];
  assert.ok(sections.length >= 220);

  const verses = [...body.matchAll(/^### .+ \{#verse-[^}]+\}$/gm)];
  assert.equal(verses.length, 3045);

  const landing = await readFile('dist/book/thirumanthiram/index.html', 'utf8');
  assert.ok(landing.includes(metadata.title));
  assert.ok(landing.includes('திருமூலர்'));
  assert.ok(index.some((item) => item.type === 'book' && item.url === '/book/thirumanthiram'));

  // Test sample readers across different tantrams
  for (const sampleId of ['paayiram-1', 'tantram-1-1', 'tantram-2-1', 'tantram-3-1', 'tantram-4-1', 'tantram-9-1']) {
    const reader = await readFile(`dist/book/thirumanthiram/read/${sampleId}/index.html`, 'utf8');
    assert.ok(reader.includes('திருமந்திரம்'));
  }
});

test('Thirumandiram reader retains source line breaks, PDF passages and repeated labels', async () => {
  const [first, fourth, index] = await Promise.all([
    readFile('dist/book/thirumanthiram/read/paayiram-1/index.html', 'utf8'),
    readFile('dist/book/thirumanthiram/read/tantram-4-2/index.html', 'utf8'),
    readFile('dist/search-index.json', 'utf8').then(JSON.parse),
  ]);

  assert.ok(first.includes('ஐந்து கரத்தனை யானை முகத்தனை<br>இந்தின் இளம்பிறை போலும் எயிற்றனை'));
  assert.ok(fourth.includes('id="verse-997"'));
  assert.ok(fourth.includes('997. தம்பனம்'));

  // All 264 PDF verses from 1155 to 1418 are published
  for (let number = 1155; number <= 1418; number++) {
    assert.ok(index.some((item) => item.type === 'verse' && item.url?.includes(`#verse-${number}`)), `Missing PDF verse ${number}`);
  }

  // Duplicate verse labels from source are properly anchored
  const allReaders = await Promise.all([
    readFile('dist/book/thirumanthiram/read/tantram-7-29/index.html', 'utf8'),
    readFile('dist/book/thirumanthiram/read/tantram-7-38/index.html', 'utf8'),
    readFile('dist/book/thirumanthiram/read/tantram-9-2/index.html', 'utf8'),
    readFile('dist/book/thirumanthiram/read/tantram-9-4/index.html', 'utf8'),
    readFile('dist/book/thirumanthiram/read/tantram-9-28/index.html', 'utf8'),
  ]);

  const [t7_21, t7_37, t9_2, t9_4, t9_28] = allReaders;
  assert.ok(t7_21.includes('id="verse-2014"'));
  assert.ok(t7_37.includes('id="verse-2014-2"'));
  assert.ok(t9_2.includes('id="verse-2667"'));
  assert.ok(t9_4.includes('id="verse-2667-2"'));
  assert.ok(t9_28.includes('id="verse-3047"'));
  assert.ok(t9_28.includes('வாழ்கவே வாழ்கஎன் நந்தி திருவடி'));

  const landing = await readFile('dist/book/thirumanthiram/index.html', 'utf8');
  assert.ok(landing.includes('1155–1418'));
  assert.ok(landing.includes('/book/thirumanthiram/summarize'));

  const summarize = await readFile('dist/book/thirumanthiram/summarize/index.html', 'utf8');
  assert.ok(summarize.includes('திருமந்திரம் — நூல் கண்ணோட்டம்'));
  assert.ok(summarize.includes('3,047 பாடல்கள் · 10 பிரிவுகள் (பாயிரம் + 9 தந்திரங்கள்)'));
  assert.ok(summarize.includes('அதிகாரப் பாடல் அளவு'));
  assert.ok(summarize.includes('1. உபதேசம்'));
  assert.ok(summarize.includes('/book/thirumanthiram/read/tantram-1-1/'));
  assert.ok(!summarize.includes('SECTION WEIGHTAGE'));
  assert.ok(!summarize.includes('Book Overview'));
  assert.ok(!summarize.includes('First Tantra'));
});
