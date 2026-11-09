import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { stringify } from 'yaml';

const book = JSON.parse(await readFile('src/data/books/thirukkural.json', 'utf8'));
const catalog = JSON.parse(await readFile('src/data/library.json', 'utf8'));
const info = catalog.find((item) => item.id === book.id);
if (!info) throw new Error('Missing catalog metadata for Thirukkural');

const metadata = {
  id: book.id,
  title: book.title_ta,
  title_en: book.title_en,
  author: book.author_ta,
  author_en: book.author_en,
  genre: book.genre_ta,
  genre_en: book.genre_en,
  category: book.category_ta,
  period: book.period_ta,
  description: book.description_ta,
  featured_quote: info.featured_quote,
  acknowledgement: 'திருக்குறள் உரை: Project Madurai மின்னூல் தொகுப்பு.',
  pdf: null,
  epub: null,
  aliases: [],
};
let previousGroup = '';
const chapters = book.athikarams.map((chapter) => {
  const group = `${chapter.paal.name_ta} / ${chapter.iyal}`;
  const heading = group === previousGroup ? '' : `# ${group}\n\n`;
  previousGroup = group;
  const verses = chapter.kurals.map((verse) =>
    `### குறள் ${verse.number} {#kural-${verse.number}}\n\n${verse.line1}\n${verse.line2}\n`
  ).join('\n');
  return `${heading}## ${chapter.number}. ${chapter.name_ta} {#${chapter.number}}\n\n${verses}`;
}).join('\n');
await mkdir('src/content/books', { recursive: true });
await writeFile('src/content/books/thirukkural.md', `---\n${stringify(metadata)}---\n\n${chapters}`, 'utf8');
