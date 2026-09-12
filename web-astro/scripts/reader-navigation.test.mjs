import test from 'node:test';
import assert from 'node:assert/strict';
import {
  createRevealFollower,
  revealScrollTop,
} from '../src/scripts/reader-navigation.ts';

const geometry = {
  scrollTop: 100,
  maxScrollTop: 500,
  viewportTop: 80,
  viewportBottom: 480,
  padding: 16,
};

test('sidebar reveal uses the nearest edge and does not move visible entries', () => {
  assert.equal(
    revealScrollTop({ ...geometry, itemTop: 200, itemBottom: 240 }),
    null,
  );
  assert.equal(
    revealScrollTop({ ...geometry, itemTop: 70, itemBottom: 110 }),
    74,
  );
  assert.equal(
    revealScrollTop({ ...geometry, itemTop: 470, itemBottom: 510 }),
    146,
  );
  assert.equal(
    revealScrollTop({
      ...geometry,
      scrollTop: 490,
      itemTop: 470,
      itemBottom: 510,
    }),
    500,
  );
});

test('outline follow waits for scrolling to settle and pauses for manual browsing', () => {
  const calls = [];
  const timers = new Map();
  let nextTimer = 1;
  const follower = createRevealFollower(
    (item, behavior) => calls.push([item, behavior]),
    {
      behavior: () => 'smooth',
      setTimer(callback) {
        const id = nextTimer++;
        timers.set(id, callback);
        return id;
      },
      clearTimer(id) {
        timers.delete(id);
      },
    },
  );
  const flush = () => {
    const pending = [...timers.values()];
    timers.clear();
    pending.forEach((callback) => callback());
  };

  follower.setItem('first', true);
  assert.deepEqual(calls, [['first', 'auto']]);

  follower.setPointerInside(true);
  follower.setItem('second');
  flush();
  assert.equal(calls.length, 1);

  follower.setPointerInside(false);
  follower.setFocusInside(true);
  flush();
  assert.equal(calls.length, 1);

  follower.setFocusInside(false);
  assert.equal(calls.length, 1);
  flush();
  assert.deepEqual(calls.at(-1), ['second', 'smooth']);
});
