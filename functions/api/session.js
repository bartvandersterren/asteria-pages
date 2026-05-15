/**
 * Cloudflare Pages Function — Mews session opslag
 * Routes:
 *   GET  /api/session → geeft opgeslagen session terug (uit KV)
 *   POST /api/session → slaat nieuwe session op in KV
 *
 * KV binding vereist: ASTERIA_KV (instellen in Cloudflare Pages dashboard)
 * Settings → Functions → KV namespace bindings → variabelenaam: ASTERIA_KV
 *
 * Vervangt de GET/POST /api/session routes uit server.js.
 */

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

export async function onRequestOptions() {
  return new Response(null, { status: 204, headers: CORS });
}

export async function onRequestGet(context) {
  const { env } = context;
  const kv = env.ASTERIA_KV;

  if (!kv) {
    return new Response(JSON.stringify({ error: 'KV not configured' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json', ...CORS },
    });
  }

  const session = await kv.get('mews_session');
  const client = await kv.get('mews_client') || 'Mews Distributor 5656.0.0';
  const capturedAt = await kv.get('mews_session_at');

  return new Response(JSON.stringify({ session, client, capturedAt }), {
    headers: { 'Content-Type': 'application/json', ...CORS },
  });
}

export async function onRequestPost(context) {
  const { request, env } = context;
  const kv = env.ASTERIA_KV;

  if (!kv) {
    return new Response(JSON.stringify({ error: 'KV not configured' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json', ...CORS },
    });
  }

  let data;
  try {
    data = await request.json();
  } catch {
    return new Response(JSON.stringify({ error: 'invalid JSON' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json', ...CORS },
    });
  }

  if (!data.session) {
    return new Response(JSON.stringify({ error: 'session field required' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json', ...CORS },
    });
  }

  const capturedAt = new Date().toISOString();
  await kv.put('mews_session', data.session);
  await kv.put('mews_client', data.client || 'Mews Distributor 5656.0.0');
  await kv.put('mews_session_at', capturedAt);

  return new Response(JSON.stringify({ ok: true, capturedAt }), {
    headers: { 'Content-Type': 'application/json', ...CORS },
  });
}
