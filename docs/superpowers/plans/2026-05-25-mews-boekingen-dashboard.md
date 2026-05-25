# Mews Boekingen Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Toon vandaag gemaakte Mews Booking Engine-reserveringen als KPI-sectie in het admin dashboard.

**Architecture:** Zapier luistert op nieuwe Mews-reserveringen (filter: channel = Mews Booking Engine) en POST de data via webhook naar een nieuwe Cloudflare Function, die het opslaat in een nieuwe D1-tabel. `dashboard.js` leest die tabel op basis van de geselecteerde periode. `dashboard.html` toont een nieuwe "Mews Boekingen" sectie.

**Tech Stack:** Cloudflare Pages Functions, D1 (SQLite), Zapier Webhooks

---

## Bestandsstructuur

| Bestand | Actie | Verantwoordelijkheid |
|---|---|---|
| `functions/api/mews-webhook.js` | Aanmaken | Webhook-ontvanger: authenticatie, validatie, INSERT in D1 |
| `functions/api/dashboard.js` | Wijzigen | Voeg `fetchMews()` toe, include in response |
| `admin/dashboard.html` | Wijzigen | Voeg "Mews Boekingen" sectie toe (KPI-grid + lijstje) |

---

## Task 1: D1-tabel aanmaken

**Files:** geen bestanden — alleen wrangler CLI

- [ ] **Stap 1: Maak de tabel aan**

```bash
wrangler d1 execute asteria-analytics --remote --command "CREATE TABLE IF NOT EXISTS mews_bookings (id INTEGER PRIMARY KEY AUTOINCREMENT, reservation_id TEXT UNIQUE NOT NULL, created_at TEXT NOT NULL, checkin TEXT, checkout TEXT, nights INTEGER, room_category TEXT, total_price REAL, currency TEXT DEFAULT 'EUR', adults INTEGER, channel TEXT DEFAULT 'Mews Booking Engine')"
```

Verwacht: `Executed 1 command in ...ms`

- [ ] **Stap 2: Controleer**

```bash
wrangler d1 execute asteria-analytics --remote --command "SELECT name FROM sqlite_master WHERE name='mews_bookings'"
```

Verwacht: `{ "name": "mews_bookings" }`

- [ ] **Stap 3: Commit**

```bash
git add -A && git commit -m "feat: create mews_bookings D1 table"
```

---

## Task 2: Webhook endpoint

**Files:**
- Aanmaken: `functions/api/mews-webhook.js`

- [ ] **Stap 1: Maak het bestand aan**

```javascript
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
```

- [ ] **Stap 2: Commit**

```bash
git add functions/api/mews-webhook.js
git commit -m "feat: add mews-webhook endpoint"
```

---

## Task 3: Dashboard backend uitbreiden

**Files:**
- Wijzigen: `functions/api/dashboard.js`

- [ ] **Stap 1: Voeg `fetchMews()` toe**

Voeg de volgende functie toe direct vóór `export async function onRequestGet`:

```javascript
async function fetchMews(db, d1Start, d1End) {
  const result = await db.prepare(
    `SELECT
       room_category,
       COUNT(*) as count,
       COALESCE(SUM(total_price), 0) as revenue,
       COALESCE(SUM(nights), 0) as nights_total
     FROM mews_bookings
     WHERE created_at >= ? AND created_at < ?
     GROUP BY room_category
     ORDER BY count DESC`
  ).bind(d1Start, d1End).all();

  const rows = result.results || [];
  const totals = rows.reduce(
    (acc, r) => ({
      count: acc.count + r.count,
      revenue: acc.revenue + (r.revenue || 0),
      nights: acc.nights + (r.nights_total || 0),
    }),
    { count: 0, revenue: 0, nights: 0 }
  );
  totals.revenue = Math.round(totals.revenue * 100) / 100;
  totals.avg_value = totals.count > 0
    ? Math.round((totals.revenue / totals.count) * 100) / 100
    : null;

  return {
    totals,
    by_category: rows.map(r => ({
      category: r.room_category || 'Onbekend',
      count: r.count,
      revenue: Math.round((r.revenue || 0) * 100) / 100,
    })),
  };
}
```

- [ ] **Stap 2: Voeg Mews toe aan Promise.allSettled**

Vervang de huidige `Promise.allSettled`-aanroep door:

```javascript
  const [d1Result, adsResult, ga4Result, mewsResult] = await Promise.allSettled([
    fetchD1(env.ASTERIA_D1, d1Start, d1End),
    fetchAds(env.MATON_API_KEY, adsStart, adsEnd),
    fetchGA4(env.MATON_API_KEY, ga4Start, ga4End),
    fetchMews(env.ASTERIA_D1, d1Start, d1End),
  ]);

  const d1 = d1Result.status === 'fulfilled' ? d1Result.value : null;
  const ads = adsResult.status === 'fulfilled' ? adsResult.value : null;
  const ga4 = ga4Result.status === 'fulfilled' ? ga4Result.value : null;
  const mews = mewsResult.status === 'fulfilled' ? mewsResult.value : null;

  const errors = {};
  if (d1Result.status === 'rejected') errors.d1 = d1Result.reason?.message || 'unknown';
  if (adsResult.status === 'rejected') errors.ads = adsResult.reason?.message || 'unknown';
  if (ga4Result.status === 'rejected') errors.ga4 = ga4Result.reason?.message || 'unknown';
  if (mewsResult.status === 'rejected') errors.mews = mewsResult.reason?.message || 'unknown';
```

- [ ] **Stap 3: Voeg `mews` toe aan de return**

Zoek `return json({` en voeg `mews,` toe:

```javascript
  return json({
    period,
    funnel: d1?.funnel ?? null,
    ab: d1?.ab ?? null,
    cta: d1?.cta ?? null,
    ads,
    ga4,
    mews,
    ...(Object.keys(errors).length ? { errors } : {}),
  });
```

- [ ] **Stap 4: Commit**

```bash
git add functions/api/dashboard.js
git commit -m "feat: add fetchMews to dashboard API"
```

---

## Task 4: Dashboard UI

**Files:**
- Wijzigen: `admin/dashboard.html`

- [ ] **Stap 1: Voeg CSS toe**

Voeg toe in de `<style>`-tag na de `.footer-note`-regel:

```css
    /* Mews sectie */
    .kpi.kpi-mews::before { background: #10b981; }
    .mews-breakdown { background: #fff; border-radius: 12px; padding: 16px 20px; box-shadow: 0 1px 3px rgba(0,0,0,.08); margin-top: 12px; }
    .mews-breakdown__title { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: .07em; color: #94a3b8; margin-bottom: 10px; }
    .mews-row { display: flex; justify-content: space-between; align-items: center; padding: 7px 0; border-bottom: 1px solid #f1f5f9; font-size: 13px; }
    .mews-row:last-child { border-bottom: none; }
    .mews-row__cat { color: #374151; font-weight: 500; }
    .mews-row__meta { display: flex; gap: 16px; color: #64748b; }
    .mews-row__meta span:last-child { font-weight: 700; color: #111827; font-variant-numeric: tabular-nums; }
```

- [ ] **Stap 2: Voeg de Mews-sectie HTML toe**

Zoek `<div id="funnel-section">` en voeg direct daarvóór in:

```html
  <div id="mews-section">
    <div class="section-header"><span class="section-label">Mews Boekingen</span><div class="section-rule"></div></div>
    <div class="skeleton-wrap"><div class="skeleton-kpi-row"><div class="skeleton skeleton-kpi"></div><div class="skeleton skeleton-kpi"></div><div class="skeleton skeleton-kpi"></div><div class="skeleton skeleton-kpi"></div></div></div>
  </div>
```

- [ ] **Stap 3: Voeg `renderMews()` toe in de script-tag**

Zoek `function renderGA4(ga4)` en voeg direct erna toe:

```javascript
  function renderMews(mews) {
    var el = document.getElementById('mews-section');
    if (!mews) {
      el.innerHTML =
        '<div class="section-header"><span class="section-label">Mews Boekingen</span><div class="section-rule"></div></div>' +
        '<p class="unavailable">Geen Mews-data beschikbaar</p>';
      return;
    }
    var t = mews.totals;
    var kpis =
      '<div class="kpi-row kpi-row-4">' +
        mkKpi('Boekingen', fmt(t.count), null, 'kpi-mews') +
        mkKpi('Omzet', fmtEuro(t.revenue), null, 'kpi-mews') +
        mkKpi('Gem. waarde', fmtEuro(t.avg_value), null, 'kpi-mews') +
        mkKpi('Kameravonden', fmt(t.nights), null, 'kpi-mews') +
      '</div>';
    var rows = (mews.by_category || []).map(function(r) {
      return '<div class="mews-row">' +
        '<span class="mews-row__cat">' + r.category + '</span>' +
        '<div class="mews-row__meta">' +
          '<span>' + r.count + ' boeking' + (r.count !== 1 ? 'en' : '') + '</span>' +
          '<span>' + fmtEuro(r.revenue) + '</span>' +
        '</div>' +
      '</div>';
    }).join('');
    var breakdown = rows
      ? '<div class="mews-breakdown"><div class="mews-breakdown__title">Per kamertype</div>' + rows + '</div>'
      : '';
    el.innerHTML =
      '<div class="section-header"><span class="section-label">Mews Boekingen</span><div class="section-rule"></div></div>' +
      kpis + breakdown;
  }
```

- [ ] **Stap 4: Roep `renderMews()` aan in `render(data)`**

Zoek `renderGA4(data.ga4);` en voeg direct erna toe:

```javascript
      renderMews(data.mews);
```

- [ ] **Stap 5: Commit**

```bash
git add admin/dashboard.html
git commit -m "feat: add Mews bookings section to dashboard UI"
```

---

## Task 5: Cloudflare secret instellen

- [ ] **Stap 1: Genereer secret**

```bash
openssl rand -hex 32
```

Kopieer de output.

- [ ] **Stap 2: Stel in als env var**

Cloudflare Dashboard → Pages → asteria-pages → Settings → Environment variables → Add variable:
- Name: `MEWS_WEBHOOK_SECRET`
- Value: `<gegenereerde hex>`
- Environment: Production + Preview

Noteer de waarde — nodig voor Zapier.

- [ ] **Stap 3: Push en wacht op deploy**

```bash
git push
```

Wacht ~35 seconden.

---

## Task 6: Zapier configureren

Stappen in de Zapier-interface:

- [ ] **Stap 1: Trigger — Mews New Reservation**

App: Mews | Event: New Reservation  
Verbind Mews-account. Test de trigger en noteer welke velden beschikbaar zijn.

- [ ] **Stap 2: Filter — alleen Booking Engine**

App: Filter by Zapier  
Conditie: `[Channel]` **Contains** `Mews Booking Engine`  
(Zoek naar veld dat "channel", "source" of "origin" heet in de Mews trigger-output.)

- [ ] **Stap 3: Action — Webhook POST**

App: Webhooks by Zapier | Action: POST

URL: `https://visit.asteria.nl/api/mews-webhook`  
Payload type: JSON

Data-mapping (map Mews-velden):

| Key | Mews-veld |
|---|---|
| `reservation_id` | Reservation ID / Identifier |
| `created_at` | Created UTC / Created At |
| `checkin` | Start UTC / Arrival Date |
| `checkout` | End UTC / Departure Date |
| `nights` | Nights / Duration |
| `room_category` | Space Category Name / Room Type |
| `total_price` | Total Price / Total Cost |
| `currency` | Currency (of hardcode `EUR`) |
| `adults` | Adults / Guest Count |
| `channel` | Channel (of hardcode `Mews Booking Engine`) |

Headers:
- `Authorization`: `Bearer <MEWS_WEBHOOK_SECRET>`
- `Content-Type`: `application/json`

- [ ] **Stap 4: Test**

Klik "Test step". Verwacht: HTTP 200 `{ "ok": true }`.

- [ ] **Stap 5: Activeer Zap**

---

## Task 7: End-to-end verificatie

- [ ] **Stap 1: Test webhook direct met curl**

```bash
curl -X POST https://visit.asteria.nl/api/mews-webhook \
  -H "Authorization: Bearer <MEWS_WEBHOOK_SECRET>" \
  -H "Content-Type: application/json" \
  -d '{"reservation_id":"test-001","created_at":"2026-05-25T10:00:00Z","checkin":"2026-05-30","checkout":"2026-06-01","nights":2,"room_category":"Comfort","total_price":278.00,"currency":"EUR","adults":2,"channel":"Mews Booking Engine"}'
```

Verwacht: `{"ok":true,"reservation_id":"test-001"}`

- [ ] **Stap 2: Controleer D1**

```bash
wrangler d1 execute asteria-analytics --remote --command "SELECT * FROM mews_bookings"
```

Verwacht: 1 rij met reservation_id = "test-001".

- [ ] **Stap 3: Controleer dashboard**

Open `https://visit.asteria.nl/admin/dashboard` → selecteer "Vandaag".  
Sectie "Mews Boekingen" toont: Boekingen 1, Omzet € 278,00, Gem. waarde € 278,00, Kameravonden 2.

- [ ] **Stap 4: Verwijder testdata**

```bash
wrangler d1 execute asteria-analytics --remote --command "DELETE FROM mews_bookings WHERE reservation_id = 'test-001'"
```

- [ ] **Stap 5: Final commit**

```bash
git add -A && git commit -m "chore: verified mews webhook e2e" && git push
```
