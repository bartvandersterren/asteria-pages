/**
 * Cloudflare Pages Function — Analytics stats (admin)
 * Route: GET /api/stats
 *
 * Query params:
 *   ?event=page_view       filter op event type
 *   ?limit=500             max rows (default 500)
 *   ?summary=1             geef samenvatting terug (counts per event + variant)
 *
 * Bescherming via Cloudflare Access (instellen op /admin/* en /api/stats*)
 * D1 binding vereist: ASTERIA_D1
 */

export async function onRequestGet({ env, request }) {
  if (!env.ASTERIA_D1) {
    return new Response(JSON.stringify({ error: 'D1 not configured' }), {
      status: 503,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  const url = new URL(request.url);
  const limit = Math.min(parseInt(url.searchParams.get('limit') || '500'), 2000);
  const eventFilter = url.searchParams.get('event');
  const summary = url.searchParams.get('summary') === '1';

  try {
    if (summary) {
      // Samenvatting: counts per event + per variant
      const [eventCounts, variantCounts, bookingStats] = await Promise.all([
        env.ASTERIA_D1.prepare(
          `SELECT event, COUNT(*) as count FROM events GROUP BY event ORDER BY count DESC`
        ).all(),
        env.ASTERIA_D1.prepare(
          `SELECT event, variant_price, COUNT(*) as count
           FROM events
           WHERE event IN ('page_view','mews_click','popup_open')
           GROUP BY event, variant_price
           ORDER BY event, variant_price`
        ).all(),
        env.ASTERIA_D1.prepare(
          `SELECT
             COUNT(*) as total_bookings,
             SUM(total_price) as total_revenue,
             AVG(total_price) as avg_value,
             MAX(created_at) as last_booking
           FROM mews_bookings`
        ).all(),
      ]);

      return new Response(
        JSON.stringify({
          events: eventCounts.results,
          variants: variantCounts.results,
          bookings: bookingStats.results[0] || { total_bookings: 0, total_revenue: 0 },
        }),
        { headers: { 'Content-Type': 'application/json' } }
      );
    }

    // Ruwe events
    let stmt;
    if (eventFilter) {
      stmt = env.ASTERIA_D1.prepare(
        `SELECT * FROM events WHERE event = ? ORDER BY ts DESC LIMIT ?`
      ).bind(eventFilter, limit);
    } else {
      stmt = env.ASTERIA_D1.prepare(
        `SELECT * FROM events ORDER BY ts DESC LIMIT ?`
      ).bind(limit);
    }

    const { results } = await stmt.all();
    return new Response(JSON.stringify(results), {
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (e) {
    return new Response(JSON.stringify({ error: e.message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }
}
