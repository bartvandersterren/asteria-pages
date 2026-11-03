// Unit-test (zonder echte inschrijving): /api/nieuwsbrief met bron scratchcard en taal nl
// moet naar Klaviyo-lijst Nieuwsbrief NL (WfwqBR) gaan. fetch is gemockt.
// Gebruik: node --test scripts/test_nieuwsbrief_lijst.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { onRequestPost } from '../functions/api/nieuwsbrief.js';

test('scratchcard nl -> lijst WfwqBR, consent SUBSCRIBED', async () => {
  const calls = [];
  globalThis.fetch = async (url, init) => { calls.push({ url, body: JSON.parse(init.body) }); return new Response('{}', { status: 202 }); };
  const req = new Request('https://visit.asteria.nl/api/nieuwsbrief', {
    method: 'POST', headers: { 'Content-Type': 'application/json', Origin: 'https://visit.asteria.nl' },
    body: JSON.stringify({ email: 'test@example.com', taal: 'nl', bron: 'scratchcard', website: '', ts: Date.now() - 60000 }),
  });
  const res = await onRequestPost({ request: req, env: { KLAVIYO_API_KEY_ASTERIA: 'test' } });
  assert.equal(res.status, 200);
  assert.deepEqual(await res.json(), { ok: true });
  assert.equal(calls.length, 1);
  assert.match(calls[0].url, /profile-subscription-bulk-create-jobs/);
  const d = calls[0].body.data;
  assert.equal(d.relationships.list.data.id, 'WfwqBR');
  assert.equal(d.attributes.profiles.data[0].attributes.email, 'test@example.com');
  assert.equal(d.attributes.profiles.data[0].attributes.subscriptions.email.marketing.consent, 'SUBSCRIBED');
  console.log('custom_source:', d.attributes.custom_source);
});
