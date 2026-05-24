/**
 * Cloudflare Pages Function — Admin dashboard data aggregator
 * Route: GET /api/dashboard?period=yesterday|7d|30d
 *
 * Bindings:
 *   ASTERIA_D1     — D1 database (al geconfigureerd)
 *   MATON_API_KEY  — Maton API key (toevoegen als secret in CF Pages)
 */

const MATON_BASE = 'https://gateway.maton.ai';
const CUSTOMER_ID = '1847810067';
const GA4_PROPERTY = '262565995';
const GA4_CONNECTION_ID = '5b8b245f-cf32-4529-b032-9f9a3c39b8e0';

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

/**
 * Berekent datumbereiken voor alle drie bronnen op basis van period.
 * - d1Start/d1End: ISO strings voor D1 WHERE ts >= ? AND ts < ?
 * - adsStart/adsEnd: YYYY-MM-DD strings voor Google Ads BETWEEN
 * - ga4Start/ga4End: GA4 relatieve strings ('yesterday', '7daysAgo', etc.)
 */
function getDateRange(period) {
  const now = new Date();
  const today = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate()));

  let startDay;
  if (period === '7d') {
    startDay = new Date(today);
    startDay.setUTCDate(startDay.getUTCDate() - 7);
  } else if (period === '30d') {
    startDay = new Date(today);
    startDay.setUTCDate(startDay.getUTCDate() - 30);
  } else {
    // yesterday (default)
    startDay = new Date(today);
    startDay.setUTCDate(startDay.getUTCDate() - 1);
  }

  const endDay = today; // exclusive upper bound voor D1

  const fmt = d => d.toISOString().slice(0, 10);
  const yesterday = new Date(today);
  yesterday.setUTCDate(yesterday.getUTCDate() - 1);

  const ga4Map = { yesterday: 'yesterday', '7d': '7daysAgo', '30d': '30daysAgo' };

  return {
    d1Start: startDay.toISOString(),
    d1End: endDay.toISOString(),
    adsStart: fmt(startDay),
    adsEnd: fmt(yesterday), // Google Ads BETWEEN is inclusief, dus t/m gisteren
    ga4Start: ga4Map[period] || 'yesterday',
    ga4End: 'yesterday',
  };
}

async function fetchD1(db, d1Start, d1End) {
  const [funnelResult, abResult] = await Promise.all([
    db.prepare(
      `SELECT event, COUNT(*) as count FROM events WHERE ts >= ? AND ts < ? GROUP BY event`
    ).bind(d1Start, d1End).all(),
    db.prepare(
      `SELECT variant_price,
         SUM(CASE WHEN event='page_view' THEN 1 ELSE 0 END) as page_views,
         SUM(CASE WHEN event='mews_click' THEN 1 ELSE 0 END) as mews_clicks
       FROM events
       WHERE ts >= ? AND ts < ? AND variant_price IS NOT NULL
       GROUP BY variant_price`
    ).bind(d1Start, d1End).all(),
  ]);

  const funnelMap = {};
  for (const row of funnelResult.results) {
    funnelMap[row.event] = row.count;
  }

  const ab = abResult.results.map(row => ({
    variant: row.variant_price,
    page_views: row.page_views,
    mews_clicks: row.mews_clicks,
    cvr: row.page_views > 0 ? Math.round((row.mews_clicks / row.page_views) * 1000) / 10 : 0,
  }));

  return {
    funnel: {
      page_view: funnelMap['page_view'] || 0,
      popup_open: funnelMap['popup_open'] || 0,
      step2_reached: funnelMap['step2_reached'] || 0,
      mews_click: funnelMap['mews_click'] || 0,
      email_submit: funnelMap['email_submit'] || 0,
      email_success: funnelMap['email_success'] || 0,
    },
    ab,
    cta: { cta_click: funnelMap['cta_click'] || 0 },
  };
}

async function fetchAds(apiKey, adsStart, adsEnd) {
  if (!apiKey) return null;

  const query = `
    SELECT
      campaign.name,
      metrics.impressions,
      metrics.clicks,
      metrics.cost_micros,
      metrics.conversions,
      metrics.search_impression_share
    FROM campaign
    WHERE segments.date BETWEEN '${adsStart}' AND '${adsEnd}'
      AND campaign.status = 'ENABLED'
    ORDER BY metrics.cost_micros DESC
  `;

  const res = await fetch(
    `${MATON_BASE}/google-ads/v23/customers/${CUSTOMER_ID}/googleAds:search`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query }),
    }
  );

  if (!res.ok) throw new Error(`Maton Ads ${res.status}: ${await res.text()}`);

  const data = await res.json();
  const campaigns = (data.results || []).map(r => {
    const m = r.metrics || {};
    const c = r.campaign || {};
    const spend = parseInt(m.costMicros || 0) / 1_000_000;
    const conversions = parseFloat(m.conversions || 0);
    const impShare = m.searchImpressionShare;
    return {
      name: c.name || '?',
      spend: Math.round(spend * 100) / 100,
      clicks: parseInt(m.clicks || 0),
      impressions: parseInt(m.impressions || 0),
      conversions: Math.round(conversions * 10) / 10,
      cpa: conversions > 0 ? Math.round((spend / conversions) * 100) / 100 : null,
      impression_share: typeof impShare === 'number' ? Math.round(impShare * 1000) / 10 : null,
    };
  });

  const totals = campaigns.reduce(
    (acc, c) => ({
      spend: acc.spend + c.spend,
      clicks: acc.clicks + c.clicks,
      impressions: acc.impressions + c.impressions,
      conversions: acc.conversions + c.conversions,
    }),
    { spend: 0, clicks: 0, impressions: 0, conversions: 0 }
  );
  totals.spend = Math.round(totals.spend * 100) / 100;
  totals.conversions = Math.round(totals.conversions * 10) / 10;
  totals.cpa = totals.conversions > 0
    ? Math.round((totals.spend / totals.conversions) * 100) / 100
    : null;

  return { totals, campaigns };
}

async function fetchGA4(apiKey, ga4Start, ga4End) {
  if (!apiKey) return null;

  const res = await fetch(
    `${MATON_BASE}/google-analytics-data/v1beta/properties/${GA4_PROPERTY}:runReport`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
        'x-connection-id': GA4_CONNECTION_ID,
      },
      body: JSON.stringify({
        dateRanges: [{ startDate: ga4Start, endDate: ga4End }],
        metrics: [
          { name: 'sessions' },
          { name: 'totalUsers' },
          { name: 'bounceRate' },
          { name: 'averageSessionDuration' },
        ],
      }),
    }
  );

  if (!res.ok) throw new Error(`Maton GA4 ${res.status}: ${await res.text()}`);

  const data = await res.json();
  const vals = (data.rows?.[0]?.metricValues) || [];
  return {
    sessions: parseInt(vals[0]?.value || 0),
    users: parseInt(vals[1]?.value || 0),
    bounce_rate: parseFloat(vals[2]?.value || 0),
    avg_session_duration: Math.round(parseFloat(vals[3]?.value || 0)),
  };
}

export async function onRequestGet({ env, request }) {
  if (!env.ASTERIA_D1) {
    return json({ error: 'D1 not configured' }, 503);
  }

  const url = new URL(request.url);
  const period = url.searchParams.get('period') || 'yesterday';
  const { d1Start, d1End, adsStart, adsEnd, ga4Start, ga4End } = getDateRange(period);

  const [d1Result, adsResult, ga4Result] = await Promise.allSettled([
    fetchD1(env.ASTERIA_D1, d1Start, d1End),
    fetchAds(env.MATON_API_KEY, adsStart, adsEnd),
    fetchGA4(env.MATON_API_KEY, ga4Start, ga4End),
  ]);

  const d1 = d1Result.status === 'fulfilled' ? d1Result.value : null;
  const ads = adsResult.status === 'fulfilled' ? adsResult.value : null;
  const ga4 = ga4Result.status === 'fulfilled' ? ga4Result.value : null;

  return json({
    period,
    funnel: d1?.funnel ?? null,
    ab: d1?.ab ?? null,
    cta: d1?.cta ?? null,
    ads,
    ga4,
  });
}
