/* Private browser-to-browser transfer of Rural Scan review drafts. */
const ReviewBackup = (() => {
  const format = 'ruralscan-browser-review';
  const textKeys = new Set(['vfReviewer', 'review:reviewer', 'review:theme',
    'nbs_dashboard_feedback_on', 'nbs_dashboard_feedback_reviewer',
    'nbs_v2_review_on', 'nbs_v2_review_reviewer']);
  const listKeys = new Set(['nbs_dashboard_feedback', 'nbs_dashboard_feedback_clear_backup', 'nbs_v2_review']);
  const objectKeys = new Set(['vfDecisions', 'vfReasons', 'vfNotes',
    't4-input-decisions-2026-10-20-v1', 't4-feedback:agroforestry-t4-bounded-2026-10-21']);

  function kind(key, batches) {
    if (textKeys.has(key)) return 'text';
    if (listKeys.has(key)) return 'list';
    if (objectKeys.has(key)) return 'object';
    // Batch IDs come from this notebook's index. Reviewer handles may contain colons.
    if (key.startsWith('review:')) {
      const end = key.indexOf(':', 7);
      if (end > 7 && end + 1 < key.length && batches.has(key.slice(7, end))) return 'object';
    }
    return null;
  }

  function capture(storage, batches, origin) {
    const entries = [];
    for (let i = 0; i < storage.length; i++) {
      const key = storage.key(i);
      if (key !== null && kind(key, batches)) entries.push([key, storage.getItem(key)]);
    }
    return {format, version: 1, origin, entries};
  }

  function plan(storage, batches, backup) {
    if (backup?.format !== format || backup.version !== 1 || !Array.isArray(backup.entries))
      throw Error('Choose a Rural Scan browser review backup.');
    const seen = new Set(), missing = [], conflicts = [];
    for (const entry of backup.entries) {
      if (!Array.isArray(entry) || entry.length !== 2 || !entry.every(v => typeof v === 'string'))
        throw Error('Invalid backup entry.');
      const [key, value] = entry;
      const type = kind(key, batches);
      if (!type || seen.has(key)) throw Error('Unknown or repeated review key: ' + key);
      seen.add(key);
      if (type !== 'text') {
        const parsed = JSON.parse(value);
        if (type === 'list' ? !Array.isArray(parsed) : (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)))
          throw Error('Invalid review data for ' + key);
      }
      const existing = storage.getItem(key);
      if (existing === null) missing.push(entry);
      else if (existing !== value) conflicts.push(key);
    }
    return {missing, conflicts};
  }

  function restore(storage, batches, backup) {
    const {missing, conflicts} = plan(storage, batches, backup);
    if (conflicts.length) throw Error('Different drafts already exist for ' + conflicts.join(', ') +
      '. Use a fresh browser profile or reconcile both exports before restoring.');
    const installed = [];
    try {
      for (const [key, value] of missing) {
        if (storage.getItem(key) !== null) throw Error('Browser storage changed for ' + key);
        storage.setItem(key, value);
        installed.push([key, value]);
      }
    } catch (error) {
      const unresolved = [];
      for (const [key, value] of installed.reverse()) {
        try {
          if (storage.getItem(key) === value) storage.removeItem(key);
          else unresolved.push(key);
        } catch { unresolved.push(key); }
      }
      if (unresolved.length) throw Error('Restore interrupted. Check these browser keys before retrying: ' + unresolved.join(', '));
      throw error;
    }
    return missing.length;
  }
  return {capture, restore};
})();
if (typeof module !== 'undefined') module.exports = ReviewBackup;
