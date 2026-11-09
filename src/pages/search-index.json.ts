import type { APIRoute } from 'astro';
import { books, catalog } from '../utils/books';
import { getUrl } from '../utils/url.js';
import { chapterUrl } from '../utils/reader.js';

export const GET: APIRoute = () => {
  const entries = catalog.map((book) => ({
    type: 'book',
    title: book.title_ta,
    author: book.author_ta,
    snippet: book.description_ta,
    searchable: [book.title_ta, book.title_en, book.author_ta, book.author_en, book.genre_ta, book.genre_en, book.category_ta, ...('aliases' in book ? book.aliases : [])].filter(Boolean),
    url: book.is_available && 'slug' in book ? getUrl(`book/${book.slug}`) : null,
  }));
  const chapters = books.flatMap((book) => book.sections.map((section) => ({
    type: 'chapter',
    title: section.title,
    author: book.author_ta,
    snippet: book.title_ta,
    searchable: [section.title, ...section.ancestors, section.ancestors.join(' / ')],
    url: chapterUrl(book.slug, section.id),
  })));
  const passages = books.flatMap((book) => book.sections.flatMap((section) =>
    section.passages.map((passage) => ({
      type: 'verse',
      title: passage.title ? `${book.title_ta} • ${passage.title}` : `${book.title_ta} • ${section.title}`,
      author: '',
      snippet: passage.text,
      searchable: [passage.title, passage.text],
      url: `${chapterUrl(book.slug, section.id)}${passage.id ? `#${passage.id}` : ''}`,
    }))
  ));
  return new Response(JSON.stringify([...entries, ...chapters, ...passages]), {
    headers: { 'Content-Type': 'application/json; charset=utf-8' },
  });
};
