# Admin Dashboard — Design Spec
_2026-05-24_

## Doel

Een lightweight intern dashboard op `visit.asteria.nl/admin/dashboard` dat Google Ads performance, landingspagina-funnel, A/B testresultaten en email-interacties combineert in één overzicht. Geïnspireerd op Triple Whale × Analytics × Google Ads, maar volledig zelfgebouwd en zonder impact op de performance van de landingspagina's.

---

## Nieuwe bestanden

| Bestand | Omschrijving |
|---|---|
| `functions/api/dashboard.js` | Cloudflare Function — haalt alle data op en retourneert gecombineerde JSON |
| `admin/dashboard.html` | Dashboard UI — statische HTML, fetcht van de Function |

Bestaande `admin/stats.html` blijft ongewijzigd.

---

## Architectuur

```
Browser (admin/dashboard.html)
  │
  └─ GET /api/dashboard?period=yesterday|7d|30d
       │
       └─ functions/api/dashboard.js (Cloudflare Worker)
            │
            ├─ D1: ASTERIA_D1.prepare(...)  ← funnel, A/B, interacties
            ├─ fetch Maton Google Ads API   ← campagne performance
            └─ fetch Maton GA4 API          ← sessies, bounce, duur
```

Alle externe API-aanroepen verlopen **server-side** in de Function. De `MATON_API_KEY` staat als Cloudflare Pages environment variable (secret), nooit in de browser of git.

---

## API: `GET /api/dashboard`

**Query param:** `?period=yesterday` (default) | `7d` | `30d`

**Response (JSON):**
```json
{
  "period": "yesterday",
  "ads": {
    "totals": { "spend": 47.20, "clicks": 84, "impressions": 5102, "conversions": 2, "cpa": 23.60 },
    "campaigns": [
      { "name": "Branded (Search)", "spend": 31.10, "clicks": 61, "impressions": 892, "conversions": 2, "cpa": 15.55, "impression_share": 0.78 },
      { "name": "Performance Max", "spend": 16.10, "clicks": 23, "impressions": 4210, "conversions": 0, "cpa": null, "impression_share": null }
    ]
  },
  "funnel": {
    "page_view": 312,
    "popup_open": 94,
    "step2_reached": 57,
    "mews_click": 41,
    "email_submit": 22,
    "email_success": 18
  },
  "ab": [
    { "variant": "A", "page_views": 158, "mews_clicks": 24, "cvr": 15.2 },
    { "variant": "B", "page_views": 154, "mews_clicks": 17, "cvr": 11.0 }
  ],
  "cta": {
    "cta_click": 69,
    "email_submit": 22,
    "email_success": 18
  },
  "ga4": {
    "sessions": 289,
    "users": 251,
    "bounce_rate": 0.61,
    "avg_session_duration": 102
  }
}
```

**Foutafhandeling:** Als een bron faalt (bijv. Maton timeout), wordt het betreffende veld `null` en toont de UI "—" zonder de rest te blokkeren. Elke bron wordt onafhankelijk gecatcht.

---

## Datumbereiken

Period-parameter vertaalt naar expliciete datums (GAQL-gotcha: `DURING LAST_X_DAYS` werkt niet):

| Period | Google Ads | D1 | GA4 |
|---|---|---|---|
| `yesterday` | `BETWEEN 'YYYY-MM-DD' AND 'YYYY-MM-DD'` (gisteren) | `WHERE ts >= '...' AND ts < '...'` | `startDate: yesterday, endDate: yesterday` |
| `7d` | afgelopen 7 dagen | idem | `startDate: 7daysAgo` |
| `30d` | afgelopen 30 dagen | idem | `startDate: 30daysAgo` |

---

## Cloudflare Function — `dashboard.js`

- Route: `GET /api/dashboard`
- Bindings: `ASTERIA_D1` (al geconfigureerd), `MATON_API_KEY` (nieuw secret)
- Parallel fetch met `Promise.allSettled()` zodat één falende bron de rest niet blokkeert
- CORS: niet nodig (zelfde domein)
- Caching: geen — data wordt elke keer vers opgehaald

**Maton Google Ads:**
- Endpoint: `POST https://gateway.maton.ai/google-ads/v23/customers/1847810067/googleAds:search`
- Header: `Authorization: Bearer <MATON_API_KEY>`
- Query: campagne-niveau metrics (name, cost_micros, clicks, impressions, conversions, search_impression_share)
- Datumfilter via `WHERE segments.date BETWEEN '...' AND '...'`

**Maton GA4:**
- Endpoint: `POST https://gateway.maton.ai/google-analytics-data/v1beta/properties/262565995:runReport`
- Headers: `Authorization: Bearer <MATON_API_KEY>`, `x-connection-id: 5b8b245f-cf32-4529-b032-9f9a3c39b8e0`
- Metrics: sessions, totalUsers, bounceRate, averageSessionDuration

**D1 queries (parallel):**
1. Funnel counts: `SELECT event, COUNT(*) FROM events WHERE ts >= ? GROUP BY event`
2. A/B split: `SELECT variant_price, SUM(CASE WHEN event='page_view' THEN 1 ELSE 0 END) as page_views, SUM(CASE WHEN event='mews_click' THEN 1 ELSE 0 END) as mews_clicks FROM events WHERE ts >= ? AND variant_price IS NOT NULL GROUP BY variant_price`

---

## Dashboard UI — `admin/dashboard.html`

Volledig statische HTML, geen externe dependencies, geen CDN.

**Structuur (van boven naar beneden):**
1. Top bar — titel + period-toggle (Gisteren / 7 dagen / 30 dagen)
2. **Google Ads sectie** — 3 KPI-kaarten (spend, kliks, CPA) + campagne-tabel
3. **Funnel sectie** — horizontale balk + %-conversie per stap (page_view → email_success)
4. **A/B tests sectie** — variant A vs B kaarten (bezoekers, Mews-kliks, conversieratio)
5. **Interacties sectie** — totaal cta_click count + email signup (submit vs. success + ratio). Geen uitsplitsing per CTA-locatie (niet in D1-schema).
6. **GA4 sectie** — 4 KPI-kaarten (sessies, gebruikers, bounce rate, gem. duur)

**Laadgedrag:**
- Bij pageload: `fetch('/api/dashboard?period=yesterday')`
- Period-toggle: nieuwe fetch, UI toont "Laden…" tijdens ophalen
- Bij fout per sectie: "Niet beschikbaar" inline, rest blijft zichtbaar

**Styling:** zelfde design tokens als `admin/stats.html` — `#f8f7f5` achtergrond, `#c23435` primair, system-ui font, kaartjes met `box-shadow: 0 1px 4px rgba(0,0,0,.08)`.

**Beveiliging:** via Cloudflare Access op `/admin/*` (al geconfigureerd voor stats.html).

---

## Secrets instellen

Na implementatie, vóór eerste gebruik:

```
Cloudflare Pages → asteria-pages → Settings → Environment variables
→ Add variable: MATON_API_KEY (secret) = v2.j9y27boo...
```

(Waarde staat in `/Users/bartvandersterren/Projects/asteria-google-ads/.env`)

---

## Buiten scope

- Historische grafieken / time-series charts
- Keyword-level of asset group detail
- Alerting / notificaties
- Exporteren naar CSV
