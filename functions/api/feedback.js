/**
 * Cloudflare Pages Function — Feedback submission
 * Route: POST /api/feedback
 *
 * D1 binding: ASTERIA_D1
 * Tabel: feedback (rating, message, name, email, lang, page_referrer, created_at)
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
  let body;
  try {
    body = await request.json();
  } catch {
    return json({ success: false, error: 'Invalid JSON' }, 400);
  }

  const { rating, message, name, email, lang, page_referrer, _hp } = body || {};

  // Honeypot — als dit veld ingevuld is, is het spam
  if (_hp) {
    return json({ success: true });
  }

  // Validatie
  if (!rating || rating < 1 || rating > 5 || !Number.isInteger(rating)) {
    return json({ success: false, error: 'Rating must be 1-5' }, 400);
  }

  if (rating <= 3 && (!message || !message.trim())) {
    return json({ success: false, error: 'Message required for low ratings' }, 400);
  }

  // Sanitize
  const clean = {
    rating,
    message: (message || '').trim().slice(0, 2000),
    name: (name || '').trim().slice(0, 100),
    email: (email || '').trim().slice(0, 200),
    lang: ['nl', 'en', 'de'].includes(lang) ? lang : 'nl',
    page_referrer: (page_referrer || '').slice(0, 500),
  };

  // D1 insert
  if (env.ASTERIA_D1) {
    try {
      await env.ASTERIA_D1.prepare(
        `INSERT INTO feedback (rating, message, name, email, lang, page_referrer)
         VALUES (?, ?, ?, ?, ?, ?)`
      )
        .bind(
          clean.rating,
          clean.message || null,
          clean.name || null,
          clean.email || null,
          clean.lang,
          clean.page_referrer || null,
        )
        .run();
    } catch (e) {
      console.error('D1 feedback insert failed:', e.message);
    }
  }

  // Email notificatie via FormSubmit.co
  try {
    const stars = '★'.repeat(clean.rating) + '☆'.repeat(5 - clean.rating);
    await fetch('https://formsubmit.co/ajax/info@asteria.nl', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({
        _subject: `Feedback ${stars} (${clean.rating}/5) — visit.asteria.nl`,
        Rating: `${stars} (${clean.rating}/5)`,
        Bericht: clean.message || '(geen bericht)',
        Naam: clean.name || '(niet ingevuld)',
        Email: clean.email || '(niet ingevuld)',
        Taal: clean.lang.toUpperCase(),
        _template: 'table',
      }),
    });
  } catch (e) {
    console.error('FormSubmit email failed:', e.message);
  }

  return json({ success: true });
}

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*',
    },
  });
}
