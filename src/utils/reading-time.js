export const READING_WORDS_PER_MINUTE = 150;

/** @param {ReadonlyArray<{ passages: ReadonlyArray<{ text: string }> }>} sections */
export function readingTimeMinutes(sections) {
  const wordCount = sections.reduce((total, section) =>
    total + section.passages.reduce((count, passage) =>
      count + (passage.text.match(/[\p{L}\p{M}\p{N}]+/gu)?.length ?? 0), 0), 0);
  return Math.max(1, Math.ceil(wordCount / READING_WORDS_PER_MINUTE));
}
