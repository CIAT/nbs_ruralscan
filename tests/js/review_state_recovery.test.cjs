const assert = require('node:assert/strict');
const fs = require('node:fs');
const test = require('node:test');
const vm = require('node:vm');

const html = fs.readFileSync('docs/dashboard.html', 'utf8');
function section(first, next) {
  const start = html.indexOf(first), end = html.indexOf(next, start + first.length);
  assert(start >= 0 && end > start);
  return html.slice(start, end);
}
const code = [
  section('async function vfFetchDecisions(', 'function updateVfMode('),
  section('async function applyVfDecisions(', 'function downloadVfDecisions('),
  section('async function resetVfDecisions(', 'function renderQaqcStats('),
  section('async function vfRefreshReview(', 'async function reopenVf('),
].join('\n');

const response = (data, status=200) => ({ok: status===200, status, json: async () => data});

function browser(fetch) {
  const window = {
    _reviewApi: true, _vfReviewer: 'alice', _vfVerPoll: 1,
    _vfAllReviews: {
      draft: {alice: {decision: 'query'}, bob: {decision: 'ok'}},
      kept: {alice: {decision: 'ok', applied: true}},
    },
    _vfDecisions: {draft: 'query', kept: 'ok'},
    _vfReasons: {draft: 'unclear'}, _vfNotes: {draft: 'See appendix'},
  };
  const storage = new Map();
  for (const key of ['vfDecisions','vfReasons','vfNotes']) {
    storage.set(key, JSON.stringify(window['_'+key]));
  }
  const notices = [], button = {}, calls = [];
  const noop = () => {};
  const page = vm.createContext({
    window, updateVfMode: noop, _vfToggleBanner: noop, vfLoadClarifications: noop,
    checkVersion: noop, checkReadiness: noop, renderVfWorklist: noop,
    localStorage: {setItem: (k,v) => storage.set(k,v), getItem: k => storage.get(k)},
    document: {getElementById: () => button}, confirm: () => true,
    vfNotice: (message,error) => notices.push({message,error}),
    fetch: async (url,options) => {
      calls.push(url);
      return fetch(url,options);
    },
  });
  vm.runInContext(code, page);
  function drafts() {
    return JSON.stringify([window._vfAllReviews,window._vfDecisions,window._vfReasons,
      window._vfNotes,Array.from(storage)]);
  }
  return {page, window, storage, notices, button, calls, drafts};
}

const failedReads = {
  'server failure': () => response({error:'Decision store unreadable'},500),
  'missing decisions': () => response({}),
  'invalid reviewer record': () => response({decisions:{draft:{alice:null}}}),
  'network error': () => {throw Error('Connection lost');},
  'invalid JSON': () => ({ok:true, json:async () => {throw SyntaxError('Invalid JSON');}}),
};
for (const [name, failure] of Object.entries(failedReads)) {
  test('Initial load keeps drafts after '+name, async () => {
    const b = browser(url => url==='/api/health'?response({ok:true}):failure());
    const before = b.drafts();
    await b.page.probeReviewApi();
    assert.equal(b.drafts(), before);
    assert.equal(b.notices.at(-1).error, true);
    assert.match(b.notices.at(-1).message, /reload/i);
  });
  test('Apply keeps drafts and submits after '+name, async () => {
    const b = browser(url => {
      if (url==='/api/apply') return response({ok:1,conflicts:[]});
      if (url==='/api/submit') return response({ok:true,pr_url:'https://example.org/pr/1'});
      if (url==='/api/state') return failure();
      throw Error('Unexpected request '+url);
    });
    const before = b.drafts();
    await b.page.applyVfDecisions();
    assert.equal(b.drafts(), before);
    assert.deepEqual(b.calls, ['/api/apply','/api/state','/api/submit']);
    assert.equal(b.button.disabled, false);
    assert.match(b.notices.at(-1).message, /reload[\s\S]+example\.org/);
  });
}

test('A valid empty decision store clears the prior view', async () => {
  const b = browser(url => url==='/api/health'?response({ok:true}):response({decisions:{}}));
  await b.page.probeReviewApi();
  assert.equal(b.storage.get('vfDecisions'), '{}');
  assert.equal(Object.keys(b.window._vfAllReviews).length, 0);
  assert.equal(b.notices.length, 0);
});

test('Refresh after a card action leaves drafts intact on malformed state', async () => {
  const b = browser(url => url==='/api/state'?response({decisions:[]}):response({}));
  const before = b.drafts();
  await assert.rejects(b.page.vfRefreshReview(), /invalid decision store/i);
  assert.equal(b.drafts(), before);
});

test('Clear requires confirmation for the selected reviewer', async () => {
  for (const failure of [
    () => response({error:'Disk full'},500), () => response({}),
    () => response({ok:true,cleared_for:'bob'}), () => {throw Error('Connection lost');},
  ]) {
    const b = browser(failure), before = b.drafts();
    await b.page.resetVfDecisions();
    assert.equal(b.drafts(), before);
    assert.match(b.notices.at(-1).message, /reload/i);
  }
});

test('Confirmed clear retains applied entries and other reviewers', async () => {
  const b = browser((url,options) => {
    assert.equal(url, '/api/clear');
    assert.deepEqual(JSON.parse(options.body), {reviewer:'alice'});
    return response({ok:true,cleared_for:'alice',cleared:1});
  });
  await b.page.resetVfDecisions();
  assert.deepEqual(b.window._vfAllReviews.draft, {bob:{decision:'ok'}});
  assert.deepEqual(JSON.parse(b.storage.get('vfDecisions')), {kept:'ok'});
  assert.equal(b.storage.get('vfReasons'), '{}');
  assert.equal(b.storage.get('vfNotes'), '{}');
  assert.equal(b.notices.length, 0);
});
