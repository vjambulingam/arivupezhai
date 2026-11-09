import test from 'node:test';
import assert from 'node:assert/strict';
import { readingTimeMinutes } from '../src/utils/reading-time.js';

const section = (...texts) => ({ passages: texts.map((text) => ({ text })) });

test('reading time counts words across passages and rounds up at 150 words per minute', () => {
  assert.equal(readingTimeMinutes([section('அறம் செய விரும்பு.')]), 1);
  assert.equal(readingTimeMinutes([section('தமிழ் '.repeat(150))]), 1);
  assert.equal(readingTimeMinutes([section('தமிழ் '.repeat(150)), section('நூல்')]), 2);
  assert.equal(readingTimeMinutes([section('தமிழ் '.repeat(300))]), 2);
  assert.equal(readingTimeMinutes([section('தமிழ் '.repeat(301))]), 3);
  assert.equal(readingTimeMinutes([section('...')]), 1);
});
