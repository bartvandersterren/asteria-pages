# Admin Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bouw een intern dashboard op `visit.asteria.nl/admin/dashboard` dat Google Ads campagne-data, D1-funnel, A/B-testresultaten en GA4-sessies combineert zonder enige impact op de landingspagina's.

**Architecture:** Een nieuwe Cloudflare Pages Function (`functions/api/dashboard.js`) haalt via `Promise.allSettled` parallel data op uit D1, de Maton Google Ads API en de Maton GA4 API, en retourneert één gecombineerde JSON. Een statische HTML-pagina (`admin/dashboard.html`) toont dit in vijf secties. Alle externe API-aanroepen verlopen volledig server-side — de `MATON_API_KEY` staat nooit in de browser.

**Tech Stack:** Cloudflare Pages Functions (ES modules), Cloudflare D1 (SQLite), Maton Google Ads API v23, Maton GA4 Data API v1beta, vanilla HTML/CSS/JS.

---

## File Map

| Bestand | Actie | Verantwoordelijkheid |
|---|---|---|
| `functions/api/dashboard.js` | Aanmaken | Data aggregator: D1 + Maton Ads + Maton GA4 → JSON |
| `admin/dashboard.html` | Aanmaken | Dashboard UI: fetch + render 5 secties |

---

## Task 1: Maak `functions/api/dashboard.js`

**Files:**
- Create: `functions/api/dashboard.js`

### Context

- Route: `GET /api/dashboard?period=yesterday|7d|30d`
- Bindings: `ASTERIA_D1` (al geconfigureerd), `MATON_API_KEY` (nog als secret toevoegen, zie Task 3)
- Maton Google Ads: `POST https://gateway.maton.ai/google-ads/v23/customers/1847810067/googleAds:search`
  - Header: `Authorization: Bearer <MATON_API_KEY>`
  - GAQL-gotcha: gebruik ALTIJD expliciete datum-strings (`BETWEEN 'YYYY-MM-DD' AND 'YYYY-MM-DD'`), nooit `DURING LAST_X_DAYS`
- Maton GA4: `POST https://gateway.maton.ai/google-analytics-data/v1beta/properties/262565995:runReport`
  - Headers: `Authorization: Bearer <MATON_API_KEY>`, `x-connection-id: 5b8b245f-cf32-4529-b032-9f9a3c39b8e0`
- D1 `ts`-veld is ISO-string (bijv. `"2026-05-24T10:30:00.000Z"`) — filter met `ts >= ?`
- Als een bron faalt: `Promise.allSettled` vangt dit op, het betreffende veld wordt `null`

- [ ] **Stap 1: Maak het bestand aan met de volledige implementatie**

Schrijf `functions/api/dashboard.js`:

```javascript
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
```

- [ ] **Stap 2: Commit**

```bash
git add functions/api/dashboard.js
git commit -m "feat: add /api/dashboard aggregator function (D1 + Maton Ads + GA4)"
```

---

## Task 2: Voeg `MATON_API_KEY` toe als secret in Cloudflare Pages

**Files:** geen (Cloudflare dashboard)

- [ ] **Stap 1: Open Cloudflare Pages dashboard**

Ga naar: Cloudflare Dashboard → Pages → `asteria-pages` → Settings → Environment variables

- [ ] **Stap 2: Voeg de secret toe**

Klik "Add variable":
- Variable name: `MATON_API_KEY`
- Value: de waarde uit `/Users/bartvandersterren/Projects/asteria-google-ads/.env` (regel `MATON_API_KEY=v2.j9y27boo...`)
- Zet op "Encrypt" (secret)
- Sla op voor zowel Production als Preview

**Let op:** De secret is pas beschikbaar na de volgende deploy.

---

## Task 3: Smoke-test de Function

**Files:** geen

- [ ] **Stap 1: Push naar main en wacht op deploy**

```bash
git push
```

Wacht ~35 seconden.

- [ ] **Stap 2: Test de Function via curl**

```bash
curl -s "https://visit.asteria.nl/api/dashboard?period=yesterday" | python3 -m json.tool | head -60
```

Verwacht resultaat: JSON met de keys `period`, `funnel`, `ab`, `cta`, `ads`, `ga4`.

Als `MATON_API_KEY` nog niet geconfigureerd is (Task 2 niet gedaan), zullen `ads` en `ga4` `null` zijn — dat is correct gedrag.

Als `ads` of `ga4` `null` zijn terwijl de key wél is ingesteld: check de Cloudflare Pages Function logs:
- Cloudflare Dashboard → Pages → asteria-pages → Deployments → (laatste deploy) → Functions

- [ ] **Stap 3: Test met 7-dagenperiode**

```bash
curl -s "https://visit.asteria.nl/api/dashboard?period=7d" | python3 -m json.tool | grep -E '"period"|"page_view"|"spend"'
```

Verwacht: `"period": "7d"` en hogere getallen dan gisteren.

---

## Task 4: Maak `admin/dashboard.html`

**Files:**
- Create: `admin/dashboard.html`

- [ ] **Stap 1: Maak het bestand aan**

Schrijf `admin/dashboard.html`:

```html
<!DOCTYPE html>
<html lang="nl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Asteria Dashboard</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: system-ui, -apple-system, sans-serif; background: #f0efed; color: #1a1a1a; min-height: 100vh; }

    .top-bar { background: #c23435; color: #fff; padding: 14px 24px; display: flex; align-items: center; justify-content: space-between; position: sticky; top: 0; z-index: 10; }
    .top-bar h1 { font-size: 16px; font-weight: 700; letter-spacing: .02em; }
    .period-toggle { display: flex; gap: 4px; }
    .period-btn { padding: 5px 14px; border-radius: 20px; font-size: 12px; font-weight: 600; border: none; cursor: pointer; background: rgba(255,255,255,.2); color: #fff; transition: background .15s; }
    .period-btn.active { background: #fff; color: #c23435; }
    .period-btn:hover:not(.active) { background: rgba(255,255,255,.3); }

    .content { max-width: 960px; margin: 0 auto; padding: 24px 20px; display: flex; flex-direction: column; gap: 28px; }

    .section-label { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: .07em; color: #9ca3af; margin-bottom: 10px; }

    /* KPI kaarten */
    .kpi-row { display: grid; gap: 10px; }
    .kpi-row-3 { grid-template-columns: repeat(3, 1fr); }
    .kpi-row-4 { grid-template-columns: repeat(4, 1fr); }
    .kpi { background: #fff; border-radius: 10px; padding: 14px 18px; box-shadow: 0 1px 4px rgba(0,0,0,.08); }
    .kpi__label { font-size: 10px; color: #9ca3af; font-weight: 700; text-transform: uppercase; letter-spacing: .05em; margin-bottom: 4px; }
    .kpi__value { font-size: 26px; font-weight: 700; line-height: 1.1; }
    .kpi__value.sm { font-size: 22px; }
    .kpi__sub { font-size: 11px; color: #9ca3af; margin-top: 4px; }

    /* Campagne tabel */
    .table-card { background: #fff; border-radius: 10px; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,.08); margin-top: 10px; }
    table { width: 100%; border-collapse: collapse; font-size: 13px; }
    thead th { background: #f9fafb; padding: 9px 14px; font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: .05em; color: #6b7280; text-align: left; }
    tbody td { padding: 10px 14px; border-top: 1px solid #f3f4f6; }
    tbody tr:hover td { background: #fafafa; }
    .badge { display: inline-block; font-size: 10px; font-weight: 700; padding: 2px 7px; border-radius: 4px; background: #dcfce7; color: #16a34a; }

    /* Funnel */
    .funnel-card { background: #fff; border-radius: 10px; padding: 18px 20px; box-shadow: 0 1px 4px rgba(0,0,0,.08); }
    .funnel-row { display: flex; align-items: center; gap: 12px; padding: 8px 0; border-bottom: 1px solid #f3f4f6; }
    .funnel-row:last-child { border-bottom: none; }
    .funnel-label { width: 150px; font-size: 12px; color: #374151; flex-shrink: 0; }
    .funnel-bar-bg { flex: 1; background: #f3f4f6; border-radius: 4px; height: 8px; overflow: hidden; }
    .funnel-bar { height: 8px; border-radius: 4px; background: #c23435; transition: width .4s; }
    .funnel-num { width: 44px; font-size: 13px; font-weight: 700; text-align: right; }
    .funnel-pct { width: 48px; font-size: 11px; font-weight: 700; color: #22c55e; text-align: right; }

    /* A/B test kaarten */
    .ab-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
    .ab-card { background: #fff; border-radius: 10px; padding: 16px 18px; box-shadow: 0 1px 4px rgba(0,0,0,.08); position: relative; overflow: hidden; }
    .ab-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; }
    .ab-card.var-a::before { background: #2563eb; }
    .ab-card.var-b::before { background: #c23435; }
    .ab-card.var-other::before { background: #9ca3af; }
    .ab-name { font-size: 12px; font-weight: 700; margin-bottom: 12px; display: flex; align-items: center; gap: 8px; }
    .ab-tag { font-size: 10px; font-weight: 700; padding: 2px 7px; border-radius: 4px; }
    .ab-tag-a { background: #dbeafe; color: #1d4ed8; }
    .ab-tag-b { background: #fee2e2; color: #c23435; }
    .ab-tag-other { background: #f3f4f6; color: #6b7280; }
    .ab-metrics { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; }
    .ab-metric__label { font-size: 9px; color: #9ca3af; text-transform: uppercase; letter-spacing: .05em; margin-bottom: 2px; }
    .ab-metric__value { font-size: 18px; font-weight: 700; }
    .ab-winner { font-size: 10px; color: #22c55e; font-weight: 700; }

    /* Interacties */
    .two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
    .action-card { background: #fff; border-radius: 10px; padding: 16px 18px; box-shadow: 0 1px 4px rgba(0,0,0,.08); }
    .action-card__title { font-size: 12px; font-weight: 700; color: #374151; margin-bottom: 10px; }
    .action-row { display: flex; justify-content: space-between; font-size: 13px; color: #6b7280; padding: 6px 0; border-bottom: 1px solid #f9fafb; }
    .action-row:last-child { border-bottom: none; }
    .action-row span:last-child { font-weight: 700; color: #1a1a1a; }

    /* Status */
    .loading { color: #9ca3af; font-size: 13px; padding: 20px 0; }
    .unavailable { color: #9ca3af; font-style: italic; font-size: 12px; }
    .footer-note { font-size: 11px; color: #9ca3af; text-align: center; padding: 8px; }
  </style>
</head>
<body>

<div class="top-bar">
  <h1>Asteria Dashboard</h1>
  <div class="period-toggle">
    <button class="period-btn active" data-period="yesterday">Gisteren</button>
    <button class="period-btn" data-period="7d">7 dagen</button>
    <button class="period-btn" data-period="30d">30 dagen</button>
  </div>
</div>

<div class="content">
  <div id="ads-section">
    <div class="section-label">Google Ads</div>
    <p class="loading">Laden…</p>
  </div>

  <div id="funnel-section">
    <div class="section-label">Funnel landingspagina</div>
    <p class="loading">Laden…</p>
  </div>

  <div id="ab-section">
    <div class="section-label">A/B tests</div>
    <p class="loading">Laden…</p>
  </div>

  <div id="cta-section">
    <div class="section-label">Interacties</div>
    <p class="loading">Laden…</p>
  </div>

  <div id="ga4-section">
    <div class="section-label">GA4 sessies</div>
    <p class="loading">Laden…</p>
  </div>

  <p class="footer-note">Data wordt vers opgehaald bij laden · API-aanroepen verlopen server-side</p>
</div>

<script>
(function () {
  var currentPeriod = 'yesterday';

  // --- Render helpers ---

  function fmt(n) {
    if (n === null || n === undefined) return '—';
    return n.toLocaleString('nl-NL');
  }

  function fmtEuro(n) {
    if (n === null || n === undefined) return '—';
    return '€\u202f' + n.toFixed(2).replace('.', ',');
  }

  function pct(part, total) {
    if (!total || total === 0) return '—';
    return Math.round((part / total) * 1000) / 10 + '%';
  }

  function fmtDuration(seconds) {
    if (!seconds) return '—';
    var m = Math.floor(seconds / 60);
    var s = Math.round(seconds % 60);
    return m + ':' + (s < 10 ? '0' : '') + s;
  }

  // --- Section renderers ---

  function renderAds(ads) {
    var el = document.getElementById('ads-section');
    if (!ads) {
      el.innerHTML = '<div class="section-label">Google Ads</div><p class="unavailable">Niet beschikbaar (controleer MATON_API_KEY)</p>';
      return;
    }
    var t = ads.totals;
    var rows = ads.campaigns.map(function (c) {
      return '<tr>' +
        '<td>' + c.name + '</td>' +
        '<td>' + fmtEuro(c.spend) + '</td>' +
        '<td>' + fmt(c.clicks) + '</td>' +
        '<td>' + fmt(c.impressions) + '</td>' +
        '<td>' + fmt(c.conversions) + '</td>' +
        '<td>' + fmtEuro(c.cpa) + '</td>' +
        '<td>' + (c.impression_share !== null ? '<span class="badge">' + c.impression_share + '%</span>' : '—') + '</td>' +
        '</tr>';
    }).join('');

    el.innerHTML = '<div class="section-label">Google Ads</div>' +
      '<div class="kpi-row kpi-row-3">' +
        mkKpi('Spend', fmtEuro(t.spend), '') +
        mkKpi('Kliks', fmt(t.clicks), '') +
        mkKpi('CPA', fmtEuro(t.cpa), t.conversions + ' conv.') +
      '</div>' +
      '<div class="table-card"><table>' +
        '<thead><tr><th>Campagne</th><th>Spend</th><th>Kliks</th><th>Impr.</th><th>Conv.</th><th>CPA</th><th>Imp. share</th></tr></thead>' +
        '<tbody>' + rows + '</tbody>' +
      '</table></div>';
  }

  function renderFunnel(funnel) {
    var el = document.getElementById('funnel-section');
    if (!funnel) {
      el.innerHTML = '<div class="section-label">Funnel landingspagina</div><p class="unavailable">Niet beschikbaar</p>';
      return;
    }
    var pv = funnel.page_view;
    var steps = [
      { label: 'Bezoekers', n: pv, base: pv, color: '#6b7280' },
      { label: 'Popup geopend', n: funnel.popup_open, base: pv, color: '#c23435' },
      { label: 'Stap 2 bereikt', n: funnel.step2_reached, base: pv, color: '#c23435' },
      { label: 'Naar Mews', n: funnel.mews_click, base: pv, color: '#c23435' },
      { label: 'Email signup', n: funnel.email_success, base: pv, color: '#10b981' },
    ];
    var rows = steps.map(function (s, i) {
      var w = pv > 0 ? Math.round((s.n / pv) * 100) : 0;
      var pctStr = i === 0 ? '—' : pct(s.n, pv);
      var pctColor = i === 0 ? '#9ca3af' : (s.color === '#10b981' ? s.color : '#22c55e');
      return '<div class="funnel-row">' +
        '<div class="funnel-label">' + s.label + '</div>' +
        '<div class="funnel-bar-bg"><div class="funnel-bar" style="width:' + w + '%;background:' + s.color + '"></div></div>' +
        '<div class="funnel-num">' + fmt(s.n) + '</div>' +
        '<div class="funnel-pct" style="color:' + pctColor + '">' + pctStr + '</div>' +
        '</div>';
    }).join('');

    el.innerHTML = '<div class="section-label">Funnel landingspagina</div>' +
      '<div class="funnel-card">' + rows + '</div>';
  }

  function renderAB(ab) {
    var el = document.getElementById('ab-section');
    if (!ab || ab.length === 0) {
      el.innerHTML = '<div class="section-label">A/B tests</div><p class="unavailable">Geen variant-data in deze periode</p>';
      return;
    }

    // Sorteer op CVR descending om winnaar te bepalen
    var sorted = ab.slice().sort(function (a, b) { return b.cvr - a.cvr; });
    var winnerVariant = sorted[0].variant;

    var cards = ab.map(function (v) {
      var cls = v.variant === 'A' ? 'var-a' : (v.variant === 'B' ? 'var-b' : 'var-other');
      var tagCls = v.variant === 'A' ? 'ab-tag-a' : (v.variant === 'B' ? 'ab-tag-b' : 'ab-tag-other');
      var isWinner = v.variant === winnerVariant && ab.length > 1;
      return '<div class="ab-card ' + cls + '">' +
        '<div class="ab-name"><span class="ab-tag ' + tagCls + '">' + v.variant + '</span></div>' +
        '<div class="ab-metrics">' +
          '<div><div class="ab-metric__label">Bezoekers</div><div class="ab-metric__value">' + fmt(v.page_views) + '</div></div>' +
          '<div><div class="ab-metric__label">Naar Mews</div><div class="ab-metric__value">' + fmt(v.mews_clicks) + '</div></div>' +
          '<div><div class="ab-metric__label">Conv.</div><div class="ab-metric__value">' + v.cvr + '%</div>' +
            (isWinner ? '<div class="ab-winner">↑ hoogste</div>' : '') +
          '</div>' +
        '</div>' +
      '</div>';
    }).join('');

    el.innerHTML = '<div class="section-label">A/B tests (variant_price)</div>' +
      '<div class="ab-grid">' + cards + '</div>' +
      '<p style="font-size:11px;color:#9ca3af;margin-top:8px">Conversieratio = mews_clicks / page_views per variant · "hoogste" is informatief, geen statistische significantie</p>';
  }

  function renderCTA(cta, funnel) {
    var el = document.getElementById('cta-section');
    if (!cta && !funnel) {
      el.innerHTML = '<div class="section-label">Interacties</div><p class="unavailable">Niet beschikbaar</p>';
      return;
    }
    var submitN = funnel ? funnel.email_submit : 0;
    var successN = funnel ? funnel.email_success : 0;
    var emailRatio = submitN > 0 ? Math.round((successN / submitN) * 100) + '%' : '—';

    el.innerHTML = '<div class="section-label">Interacties</div>' +
      '<div class="two-col">' +
        '<div class="action-card">' +
          '<div class="action-card__title">CTA kliks</div>' +
          '<div class="action-row"><span>Totaal cta_click events</span><span>' + fmt(cta ? cta.cta_click : 0) + '</span></div>' +
        '</div>' +
        '<div class="action-card">' +
          '<div class="action-card__title">Email signups</div>' +
          '<div class="action-row"><span>Verstuurd (submit)</span><span>' + fmt(submitN) + '</span></div>' +
          '<div class="action-row"><span>Bevestigd (success)</span><span>' + fmt(successN) + '</span></div>' +
          '<div class="action-row"><span>Conversieratio</span><span style="color:#22c55e">' + emailRatio + '</span></div>' +
        '</div>' +
      '</div>';
  }

  function renderGA4(ga4) {
    var el = document.getElementById('ga4-section');
    if (!ga4) {
      el.innerHTML = '<div class="section-label">GA4 sessies</div><p class="unavailable">Niet beschikbaar (controleer MATON_API_KEY)</p>';
      return;
    }
    el.innerHTML = '<div class="section-label">GA4 sessies</div>' +
      '<div class="kpi-row kpi-row-4">' +
        mkKpi('Sessies', fmt(ga4.sessions), '', 'sm') +
        mkKpi('Gebruikers', fmt(ga4.users), '', 'sm') +
        mkKpi('Bounce rate', Math.round(ga4.bounce_rate * 100) + '%', '', 'sm') +
        mkKpi('Gem. duur', fmtDuration(ga4.avg_session_duration), '', 'sm') +
      '</div>';
  }

  function mkKpi(label, value, sub, size) {
    return '<div class="kpi">' +
      '<div class="kpi__label">' + label + '</div>' +
      '<div class="kpi__value' + (size ? ' ' + size : '') + '">' + value + '</div>' +
      (sub ? '<div class="kpi__sub">' + sub + '</div>' : '') +
      '</div>';
  }

  // --- Data fetch ---

  function load(period) {
    // Reset alle secties naar "Laden..."
    ['ads-section','funnel-section','ab-section','cta-section','ga4-section'].forEach(function (id) {
      var label = document.querySelector('#' + id + ' .section-label');
      var labelHTML = label ? label.outerHTML : '';
      document.getElementById(id).innerHTML = labelHTML + '<p class="loading">Laden\u2026</p>';
    });

    fetch('/api/dashboard?period=' + period)
      .then(function (r) { return r.json(); })
      .then(function (data) {
        renderAds(data.ads);
        renderFunnel(data.funnel);
        renderAB(data.ab);
        renderCTA(data.cta, data.funnel);
        renderGA4(data.ga4);
      })
      .catch(function (err) {
        ['ads-section','funnel-section','ab-section','cta-section','ga4-section'].forEach(function (id) {
          document.getElementById(id).innerHTML += '<p style="color:#c23435;font-size:12px">Fout: ' + err.message + '</p>';
        });
      });
  }

  // --- Period toggle ---

  document.querySelectorAll('.period-btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      document.querySelectorAll('.period-btn').forEach(function (b) { b.classList.remove('active'); });
      btn.classList.add('active');
      currentPeriod = btn.dataset.period;
      load(currentPeriod);
    });
  });

  // --- Init ---
  load(currentPeriod);
})();
</script>

</body>
</html>
```

- [ ] **Stap 2: Commit**

```bash
git add admin/dashboard.html
git commit -m "feat: add admin dashboard UI"
```

---

## Task 5: Deploy en end-to-end test

**Files:** geen

- [ ] **Stap 1: Push naar main**

```bash
git push
```

Wacht ~35 seconden op Cloudflare deploy.

- [ ] **Stap 2: Open het dashboard in de browser**

Navigeer naar: `https://visit.asteria.nl/admin/dashboard`

Controleer per sectie:
- **Google Ads:** spend, kliks, CPA en campagnetabel gevuld (niet "Niet beschikbaar")
- **Funnel:** balkjes zichtbaar, percentages naast de stappen
- **A/B tests:** variant-kaarten getoond, of "Geen variant-data" als er geen data is voor gisteren
- **Interacties:** CTA kliks en email-aantallen
- **GA4:** sessies, gebruikers, bounce, duur gevuld (niet "Niet beschikbaar")

Als Google Ads of GA4 "Niet beschikbaar" toont: controleer of `MATON_API_KEY` correct is ingesteld in Cloudflare Pages (Task 2) en of de laatste deploy erna is aangemaakt.

- [ ] **Stap 3: Test period-toggle**

Klik op "7 dagen" en "30 dagen". Alle secties herladen; getallen worden groter dan "Gisteren".

- [ ] **Stap 4: Controleer landingspagina-performance**

Open `https://visit.asteria.nl/hotel-venray` in een nieuw tabblad. Controleer via DevTools → Network dat er geen aanroepen naar Maton of externe ad-APIs plaatsvinden vanaf de landingspagina.

---
