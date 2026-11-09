import { getUrl } from './url.js';

export function chapterUrl(bookId, chapter) {
  return getUrl(`book/${bookId}/read/${chapter}/`);
}
