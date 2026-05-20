/**
 * Cloudflare Pages Function — Analytics event tracking
 * Route: POST /api/track
 *
 * D1 binding vereist: ASTERIA_D1
 * Setup: Cloudflare Dashboard → Pages → asteria-pages → Settings → Functions → D1 database bindings
 *   Variable name: ASTERIA_D1  |  D1 database: asteria-analytics
 *
 * D1 schema (eenmalig uitvoeren in D1 console):
 *   CREATE TABLE IF NOT EXISTS events (
 *     id INTEGER PRIMARY KEY AUTOINCREMENT,
 *     ts TEXT NOT NULL,
 *     session_id TEXT,
 *     event TEXT,
 *     variant_price TEXT,
 *     variant_email TEXT,
 *     page TEXT,
 *     referrer TEXT
 *   );
 */

export async function onRequestOptions() {
  return new Response(null, {
    status: 204,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    },
  });
}

export async function onRequestPost({ request, env }) {
  // Silent noop als D1 niet geconfigureerd is
  if (!env.ASTERIA_D1) {
    return new Response('OK', { status: 200 });
  }

  let body;
  try {
    body = await request.json();
  } catch {
    return new Response('bad request', { status: 400 });
  }

  const { session_id, event, variant_price, variant_email, page, referrer } = body || {};

  try {
    await env.ASTERIA_D1.prepare(
      `INSERT INTO events (ts, session_id, event, variant_price, variant_email, page, referrer)
       VALUES (?, ?, ?, ?, ?, ?, ?)`
    )
      .bind(
        new Date().toISOString(),
        session_id || null,
        event || null,
        variant_price || null,
        variant_email || null,
        page || null,
        referrer || null,
      )
      .run();
  } catch (e) {
    // Nooit user request laten mislukken door analytics fout
    console.error('D1 insert failed:', e.message);
  }

  return new Response('OK', { status: 200 });
}
