import { marked } from 'marked';
import { parse as parseYaml } from 'yaml';
import placeholders from '../data/library.json';

const sources = import.meta.glob('/src/content/books/*.{md,txt}', {
  eager: true,
  query: '?raw',
  import: 'default',
});

export interface Passage {
  id: string;
  title: string;
  markdown: string;
  text: string;
  copyText: string;
  html: string;
}

export interface Section {
  id: string;
  title: string;
  group: string;
  passages: Passage[];
}

export interface Book {
  id: string;
  title_ta: string;
  title_en: string;
  author_ta: string;
  author_en: string;
  genre_ta: string;
  genre_en: string;
  category_ta: string;
  period_ta: string;
  description_ta: string;
  featured_quote: string;
  acknowledgement: string;
  pdf: string | null;
  epub: string | null;
  aliases: string[];
  sections: Section[];
}

const slugPattern = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;
const headingId = /^(.*?)\s+\{#([a-z0-9]+(?:-[a-z0-9]+)*)\}$/;

function requiredString(data: Record<string, unknown>, key: string, file: string): string {
  const value = data[key];
  if (typeof value !== 'string' || !value.trim()) throw new Error(`${file}: "${key}" must be a non-empty string`);
  return value.trim();
}

function optionalString(data: Record<string, unknown>, key: string, file: string): string {
  const value = data[key];
  if (value == null) return '';
  if (typeof value !== 'string') throw new Error(`${file}: "${key}" must be a string`);
  return value.trim();
}

function downloadUrl(data: Record<string, unknown>, key: string, file: string): string | null {
  const value = optionalString(data, key, file);
  if (!value) return null;
  if (!/^https?:\/\//i.test(value) && !(value.startsWith('/') && !value.startsWith('//'))) {
    throw new Error(`${file}: "${key}" must be an HTTP(S) URL or an absolute site path`);
  }
  return value;
}

function parseBook(source: string, file: string): Book {
  const match = source.replace(/\r\n/g, '\n').match(/^---\n([\s\S]*?)\n---\n?([\s\S]*)$/);
  if (!match) throw new Error(`${file}: expected YAML frontmatter between --- lines`);
  const data = parseYaml(match[1]);
  if (!data || typeof data !== 'object' || Array.isArray(data)) throw new Error(`${file}: invalid frontmatter`);
  const id = requiredString(data, 'id', file);
  if (!slugPattern.test(id)) throw new Error(`${file}: book id must use lowercase letters, digits and hyphens`);
  const aliases = data.aliases ?? [];
  if (!Array.isArray(aliases) || aliases.some((alias) => typeof alias !== 'string')) throw new Error(`${file}: aliases must be a list of strings`);
  const sections: Section[] = [];
  let section: Section | undefined;
  let passage: { id: string; title: string; markdown: string } | undefined;
  let group = '';

  function finishPassage() {
    if (!section || !passage) return;
    const markdown = passage.markdown.trim();
    if (!markdown) throw new Error(`${file}: "${passage.title || section.title}" has no content`);
    const html = marked.parse(markdown, { breaks: true, async: false });
    const copyText = markdown.replace(/[*_`#\[\]()]/g, '').trim();
    const text = copyText.replace(/\s+/g, ' ');
    section.passages.push({ ...passage, markdown, text, copyText, html });
    passage = undefined;
  }

  const sectionIds = new Set<string>();
  const passageIds = new Set<string>();
  for (const token of marked.lexer(match[2])) {
    if (token.type === 'heading' && token.depth === 1) {
      finishPassage();
      group = token.text.trim();
      section = undefined;
    } else if (token.type === 'heading' && token.depth === 2) {
      finishPassage();
      const heading = token.text.match(headingId);
      if (!heading) throw new Error(`${file}: level 2 headings require a stable id, e.g. ## Title {#1}`);
      if (sectionIds.has(heading[2])) throw new Error(`${file}: duplicate section id "${heading[2]}"`);
      sectionIds.add(heading[2]);
      section = { id: heading[2], title: heading[1].trim(), group, passages: [] };
      sections.push(section);
    } else if (token.type === 'heading' && token.depth === 3 && token.text.match(headingId)) {
      if (!section) throw new Error(`${file}: passage appears before a section`);
      finishPassage();
      const heading = token.text.match(headingId)!;
      if (passageIds.has(heading[2])) throw new Error(`${file}: duplicate passage id "${heading[2]}"`);
      passageIds.add(heading[2]);
      passage = { id: heading[2], title: heading[1].trim(), markdown: '' };
    } else {
      if (!section && token.raw.trim()) throw new Error(`${file}: content must begin with a level 2 section heading`);
      if (section && (passage || token.raw.trim())) {
        passage ??= { id: '', title: '', markdown: '' };
        passage.markdown += token.raw;
      }
    }
  }
  finishPassage();
  if (!sections.length || sections.some((item) => !item.passages.length)) throw new Error(`${file}: every book must have at least one non-empty section`);

  return {
    id,
    title_ta: requiredString(data, 'title', file),
    title_en: optionalString(data, 'title_en', file),
    author_ta: requiredString(data, 'author', file),
    author_en: optionalString(data, 'author_en', file),
    genre_ta: requiredString(data, 'genre', file),
    genre_en: optionalString(data, 'genre_en', file),
    category_ta: optionalString(data, 'category', file),
    period_ta: optionalString(data, 'period', file),
    description_ta: requiredString(data, 'description', file),
    featured_quote: optionalString(data, 'featured_quote', file),
    acknowledgement: requiredString(data, 'acknowledgement', file),
    pdf: downloadUrl(data, 'pdf', file),
    epub: downloadUrl(data, 'epub', file),
    aliases,
    sections,
  };
}

export const books: Book[] = Object.entries(sources).map(([file, source]) => parseBook(source as string, file));
const ids = new Set<string>();
for (const book of books) {
  if (ids.has(book.id)) throw new Error(`Duplicate book id "${book.id}"`);
  ids.add(book.id);
}

export const catalog = [
  ...books.map((book) => ({
    ...book,
    is_available: true,
    subsections_label: `${book.sections.length} பகுதிகள்`,
    stats: { subsections: book.sections.length, verses: book.sections.reduce((sum, section) => sum + section.passages.length, 0) },
  })),
  ...placeholders.filter((book) => !ids.has(book.id)).map((book) => ({ ...book, is_available: false })),
];
