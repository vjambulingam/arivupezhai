import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

test('Thirukkural summary page renders pure Tamil overview and section weightage', async () => {
  const [landing, summarize, summary] = await Promise.all([
    readFile('dist/book/thirukkural/index.html', 'utf8'),
    readFile('dist/book/thirukkural/summarize/index.html', 'utf8'),
    readFile('dist/book/thirukkural/summary/index.html', 'utf8'),
  ]);

  // Landing page links to summarize
  assert.ok(landing.includes('/book/thirukkural/summarize'));
  assert.ok(landing.includes('நூல் கண்ணோட்டம்'));

  // Both summarize and summary endpoints render content
  for (const html of [summarize, summary]) {
    assert.ok(html.includes('திருக்குறள் — நூல் கண்ணோட்டம்'));
    assert.ok(html.includes('1,330 குறள்கள் · 3 பால்கள் (9 இயல்கள் · 133 அதிகாரங்கள்)'));
    assert.ok(html.includes('பால்கள் வாரியான சுருக்கம்'));
    assert.ok(html.includes('இயல்கள் வாரியான பாடல் அளவு'));

    // 3 பால்கள்
    assert.ok(html.includes('அறத்துப்பால்'));
    assert.ok(html.includes('பொருட்பால்'));
    assert.ok(html.includes('காமத்துப்பால்'));

    // 9 இயல்கள்
    for (const iyal of ['பாயிரவியல்', 'இல்லறவியல்', 'துறவறவியல்', 'ஊழியல்', 'அரசியல்', 'அங்கவியல்', 'ஒழிபியல்', 'களவியல்', 'கற்பியல்']) {
      assert.ok(html.includes(iyal), `Missing iyal: ${iyal}`);
    }

    assert.ok(html.includes('அதிகாரப் பாடல் அளவு'));
    assert.ok(html.includes('1. கடவுள் வாழ்த்து'));
    assert.ok(html.includes('/book/thirukkural/read/1/'));

    // Pure Tamil: No English labels or transliterations in content
    assert.ok(!html.includes('SECTION WEIGHTAGE'));
    assert.ok(!html.includes('Book Overview'));
    assert.ok(!html.includes('Tirukkural'));
  }
});

test('Thiruvasagam summary page renders pure Tamil overview and section weightage', async () => {
  const [landing, summarize, summary] = await Promise.all([
    readFile('dist/book/thiruvasagam/index.html', 'utf8'),
    readFile('dist/book/thiruvasagam/summarize/index.html', 'utf8'),
    readFile('dist/book/thiruvasagam/summary/index.html', 'utf8'),
  ]);

  // Landing page links to summarize
  assert.ok(landing.includes('/book/thiruvasagam/summarize'));
  assert.ok(landing.includes('நூல் கண்ணோட்டம்'));

  // Both summarize and summary endpoints render content
  for (const html of [summarize, summary]) {
    assert.ok(html.includes('திருவாசகம் — நூல் கண்ணோட்டம்'));
    assert.ok(html.includes('661 பாடல்கள் · 5 பிரிவுகள் (51 பதிகங்கள்)'));
    assert.ok(html.includes('பதிகங்கள் 1–10'));
    assert.ok(html.includes('பதிகங்கள் 11–20'));
    assert.ok(html.includes('பதிகங்கள் 21–30'));
    assert.ok(html.includes('பதிகங்கள் 31–40'));
    assert.ok(html.includes('பதிகங்கள் 41–51'));
    assert.ok(html.includes('பதிகப் பாடல் அளவு'));
    assert.ok(html.includes('1. சிவபுராணம்'));
    assert.ok(html.includes('5. திருச்சதகம்'));
    assert.ok(html.includes('/book/thiruvasagam/read/sivapuranam/'));

    // Pure Tamil: No English labels or transliterations in content
    assert.ok(!html.includes('SECTION WEIGHTAGE'));
    assert.ok(!html.includes('Book Overview'));
    assert.ok(!html.includes('Thiruvasagam Summary'));
  }
});
