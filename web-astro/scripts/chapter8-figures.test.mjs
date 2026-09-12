import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import editions from '../src/lib/editions.json' with { type: 'json' };
import { layoutGrpoRollouts } from './grpo-rollouts-figure.mjs';
import { styleFigure } from './figure-style.mjs';

const requiredLabels = [
  'title',
  'example',
  'taskHeading',
  'taskBug',
  'taskConstraint',
  'policyHeading',
  'policyDetail',
  'rolloutsHeading',
  'rolloutsDetail',
  'summary',
  'rewardHeading',
  'rewardDetail',
  'rewardPass',
  'rewardFail',
  'advantageHeading',
  'advantageMean',
  'advantagePass',
  'advantageFail',
  'updateHeading',
  'updateDetail',
  'increase',
  'decrease',
  'nextStep',
  'stepSummary',
];

const normalize = (value) =>
  value
    .replace(/<[^>]+>/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/\s+/g, ' ')
    .trim();

test('Figure 8-13 renders the 16-rollout hypothetical in every locale and theme', () => {
  const titles = new Set();
  for (const locale of Object.keys(editions)) {
    const layout = layoutGrpoRollouts(locale);
    titles.add(layout.match(/<title id="grpo-title">([^<]+)<\/title>/)?.[1]);

    assert.equal(
      (layout.match(/<g data-rollout="\d+"/g) || []).length,
      16,
      `${locale} rollout count`,
    );
    assert.equal(
      (layout.match(/data-outcome="pass"/g) || []).length,
      4,
      `${locale} passing rollout count`,
    );
    assert.equal(
      (layout.match(/data-outcome="fail"/g) || []).length,
      12,
      `${locale} failed rollout count`,
    );
    assert.match(layout, /4\/16 = (?:0\.25|0,25)/, `${locale} group mean`);

    for (const theme of ['light', 'dark']) {
      const rendered = styleFigure(layout, theme);
      assert.doesNotMatch(rendered, />\s*(?:undefined|null)\s*</);
      for (const key of requiredLabels) {
        const match = rendered.match(
          new RegExp(
            `<foreignObject data-i18n="${key}"[^>]*>([\\s\\S]*?)<\\/foreignObject>`,
          ),
        );
        assert.ok(match, `${locale} ${theme} missing ${key}`);
        assert.ok(normalize(match[1]), `${locale} ${theme} empty ${key}`);
      }
      assert.match(rendered, /<div dir="auto"/);
    }
  }
  assert.equal(titles.size, Object.keys(editions).length);
});

test('Figure 8-13 stays guarded against changes to the source example', () => {
  const sourceSvg = readFileSync(
    new URL('../../book/images/fig8-13.svg', import.meta.url),
    'utf8',
  );
  const sourceRollouts = [
    ...sourceSvg.matchAll(/>#(\d{2}) ([×✓]) ([^<]+)<\/text>/g),
  ];
  assert.equal(sourceRollouts.length, 16);
  const sourcePasses = sourceRollouts
    .filter((match) => match[2] === '✓')
    .map((match) => Number(match[1]));
  assert.deepEqual(sourcePasses, [2, 7, 11, 16]);
  assert.equal(sourceRollouts.filter((match) => match[2] === '×').length, 12);
  assert.match(sourceSvg, />4 条通过，12 条失败<\/text>/);

  const webPasses = [
    ...layoutGrpoRollouts('zh-CN').matchAll(
      /<g data-rollout="(\d+)" data-outcome="pass">/g,
    ),
  ].map((match) => Number(match[1]));
  assert.deepEqual(webPasses, sourcePasses);

  const sourceChapter = readFileSync(
    new URL('../../book/chapter8.md', import.meta.url),
    'utf8',
  );
  assert.match(
    sourceChapter,
    /假设 16 次尝试中有 4 次通过全部测试且没有修改测试文件，另外 12 次失败/,
  );
  assert.match(sourceChapter, /前 4 条得到奖励 1，后 12 条得到奖励 0/);
  assert.match(sourceChapter, /平均成功率是 4\/16/);
});

test('Figure 8-13 rejects locales that have no reviewed translation', () => {
  assert.throws(
    () => layoutGrpoRollouts('not-a-locale'),
    /no localization for locale/,
  );
});
