/**
 * Cloudflare Pages Function — Mews Booking webhook ontvanger
 * Route: POST /api/mews-webhook
 *
 * Authenticatie: Authorization: Bearer <MEWS_WEBHOOK_SECRET>
 * Binding vereist: ASTERIA_D1
 */

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

export async function onRequestPost({ env, request }) {
  const auth = request.headers.get('Authorization');
  if (!auth || auth !== `Bearer ${env.MEWS_WEBHOOK_SECRET}`) {
    return json({ error: 'Unauthorized' }, 401);
  }

  if (!env.ASTERIA_D1) {
    return json({ error: 'D1 not configured' }, 503);
  }

  let body;
  try {
    body = await request.json();
  } catch {
    return json({ error: 'Invalid JSON' }, 400);
  }

  const { reservation_id, created_at } = body;
  if (!reservation_id || !created_at) {
    return json({ error: 'Missing required fields: reservation_id, created_at' }, 400);
  }

  const createdAt = new Date(created_at);
  if (isNaN(createdAt.getTime())) {
    return json({ error: 'Invalid created_at date' }, 400);
  }

  try {
    await env.ASTERIA_D1.prepare(
      `INSERT OR IGNORE INTO mews_bookings
        (reservation_id, created_at, checkin, checkout, nights, room_category, total_price, currency, adults, channel)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`
    ).bind(
      String(reservation_id),
      createdAt.toISOString(),
      body.checkin || null,
      body.checkout || null,
      body.nights ? parseInt(body.nights) : null,
      body.room_category || null,
      body.total_price ? parseFloat(body.total_price) : null,
      body.currency || 'EUR',
      body.adults ? parseInt(body.adults) : null,
      body.channel || 'Mews Booking Engine'
    ).run();

    return json({ ok: true, reservation_id });
  } catch (e) {
    return json({ error: e.message }, 500);
  }
}

export async function onRequestOptions() {
  return new Response(null, {
    status: 204,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  });
}
