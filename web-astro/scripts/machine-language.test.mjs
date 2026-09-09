import test from 'node:test';
import assert from 'node:assert/strict';
import { machineLanguage } from '../src/lib/machine-language.ts';
import config from '../src/lib/machine-translation.json' with { type: 'json' };

test('Machine translation accepts only configured fallbacks on English source pages', () => {
  assert.equal(config.languages.length, 21);
  for (const language of config.languages) {
    for (const path of ['/en/', '/book-en/chapter1/']) {
      assert.equal(
        machineLanguage(
          new URL(`https://book.test${path}?translate=${language.locale}`),
        )?.name,
        language.name,
      );
    }
  }
  for (const path of [
    '/?translate=fr',
    '/book/chapter1/?translate=fr',
    '/en/?translate=unknown',
    '/en/',
  ]) {
    assert.equal(
      machineLanguage(new URL(`https://book.test${path}`)),
      undefined,
    );
  }
});
