const assert = require('node:assert/strict');
const {capture, restore} = require('../../docs/review/browser-backup.js');

class Storage extends Map {
  get length() {return this.size;}
  key(i) {return [...this.keys()][i];}
  getItem(k) {return this.get(k) ?? null;}
  setItem(k, v) {this.set(k, v);}
  removeItem(k) {this.delete(k);}
}
const batches = new Set(['audit']);
const original = new Storage([
  ['vfReviewer', 'A'], ['vfNotes', '{"ev":"café"}'], ['review:audit:A:B', '{}'],
  ['nbs_dashboard_feedback_clear_backup', '[{"id":"old"}]'],
  ['nbs_v2_review', '[]'], ['t4-input-decisions-2026-10-20-v1','{}'],
  ['review:another-app:A','{}'], ['unrelated','private value'],
]);
const archive = capture(original, batches, 'http://localhost:8300');
assert.equal(archive.entries.length, 6);
assert.ok(!JSON.stringify(archive).includes('private value'));
const target = new Storage([['existing', 'keep']]);
assert.equal(restore(target, batches, archive), 6);
assert.equal(restore(target, batches, archive), 0);
assert.equal(target.getItem('nbs_dashboard_feedback_clear_backup'), '[{"id":"old"}]');
assert.equal(target.getItem('review:audit:A:B'), '{}');
assert.equal(target.getItem('existing'), 'keep');

for (const extra of [[['vfNotes', '[]']], [['vfNotes', 'malformed']], [['foreign','x']], [['vfReviewer','A'],['vfReviewer','B']]]) {
  const dest = new Storage();
  assert.throws(() => restore(dest, batches, {...archive, entries: [['vfReasons','{}'], ...extra]}));
  assert.equal(dest.size, 0);
}
const conflicts = new Storage([['vfNotes', '{"ev":"newer"}']]);
assert.throws(() => restore(conflicts, batches, archive), /Different drafts/);
assert.deepEqual([...conflicts], [['vfNotes', '{"ev":"newer"}']]);
const full = new Storage();
full.setItem = function(k, v) {
  if (k === 'nbs_v2_review') throw Error('quota');
  this.set(k,v);
};
assert.throws(() => restore(full, batches, archive), /quota/);
assert.equal(full.size, 0);
