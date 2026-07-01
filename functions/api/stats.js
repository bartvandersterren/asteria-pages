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
      const [eventCounts, variantCounts, popupAb, bookingStats] = await Promise.all([
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
        // A/B nieuwsbrief-popup: shows / submits / conversies per variant
        env.ASTERIA_D1.prepare(
          `SELECT variant_email as variant,
                  SUM(CASE WHEN event='email_popup_open' THEN 1 ELSE 0 END) as shows,
                  SUM(CASE WHEN event='email_submit'     THEN 1 ELSE 0 END) as submits,
                  SUM(CASE WHEN event='email_success'    THEN 1 ELSE 0 END) as conversions
           FROM events
           WHERE variant_email IN ('A_whitecard','B_scratchcard')
           GROUP BY variant_email
           ORDER BY variant_email`
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

      // Conversieratio per variant erbij rekenen
      const popup_ab = (popupAb.results || []).map((r) => ({
        ...r,
        conversion_rate: r.shows ? +(100 * r.conversions / r.shows).toFixed(1) : 0,
      }));

      return new Response(
        JSON.stringify({
          events: eventCounts.results,
          variants: variantCounts.results,
          popup_ab,
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
