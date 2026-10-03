// Offline installation check. No App Store request is made.
const assert = require('node:assert/strict');
const store = require('app-store-scraper');
const pkg = require('app-store-scraper/package.json');

assert.equal(typeof store.reviews, 'function');
assert.ok(store.sort.RECENT);
assert.ok(store.sort.HELPFUL);
console.log(JSON.stringify({
  'app-store-scraper': pkg.version,
  network_requests: 0,
  review_endpoint_checked: false,
}));
