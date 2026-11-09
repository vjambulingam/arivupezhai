import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

test('Project Madurai catalog has unique IDs and complete source fields', async () => {
  const books = JSON.parse(await readFile('src/data/project-madurai-catalog.json', 'utf8'));
  assert.ok(books.length >= 1290);
  const ids = new Set(books.map((book) => book.id));
  assert.equal(ids.size, books.length);
  for (let index = 1; index <= 1290; index++) {
    assert.ok(ids.has(`AP${String(index).padStart(3, '0')}`));
  }
  for (const book of books) {
    assert.match(book.id, /^AP\d{3,}$/);
    assert.ok(['pending', 'done'].includes(book.status));
    for (const field of ['project_madurai_work_number', 'title_ta', 'genre_ta', 'status']) {
      assert.equal(typeof book[field], 'string');
      assert.ok(book[field].trim());
    }
    assert.ok(book.author_ta === null || (typeof book.author_ta === 'string' && book.author_ta.trim()));
    for (const field of ['pdf_links', 'unicode_html_links']) {
      assert.ok(Array.isArray(book[field]));
      for (const link of book[field]) {
        const url = new URL(link);
        assert.ok(['http:', 'https:'].includes(url.protocol));
      }
    }
  }
  for (const id of ['AP001', 'AP002', 'AP003', 'AP004', 'AP005', 'AP006', 'AP007', 'AP008', 'AP036', 'AP037', 'AP038']) {
    assert.equal(books.find((book) => book.id === id)?.status, 'done');
  }
  assert.equal(books.find((book) => book.id === 'AP035')?.status, 'pending');
  assert.deepEqual(books.find((book) => book.id === 'AP001'), {
    id: 'AP001',
    project_madurai_work_number: '1',
    title_ta: 'திருக்குறள்',
    author_ta: 'திருவள்ளுவர்',
    genre_ta: 'நீதிநெறி – பதினெண்கீழ்க்கணக்கு',
    pdf_links: [
      'https://projectmadurai.org/pm_etexts/pdf/pm0001.pdf',
      'https://projectmadurai.org/pm_etexts/pdf/pm0001_01.pdf',
    ],
    unicode_html_links: ['https://projectmadurai.org/pm_etexts/utf8/pmuni0001.html'],
    status: 'done',
  });
  assert.ok(books.filter((book) => book.project_madurai_work_number === '2').length > 1);
});
