# BB-Price Fix — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** De logies & ontbijt prijs op hotel-venray.html (en lander-google.html) tonen een echte prijs i.p.v. de fallback €120 per nacht.

**Architecture:** De Mews Booking Engine (`api/bookingEngine/v1`) vereist een sessie-token die via een Cloudflare challenge beschermd is — geen publiek endpoint. Een Playwright script captured de sessie door de booking pagina te laden, extraheert het token uit het netwerk verkeer, en inject het via POST `/api/session` in Cloudflare KV. Een GitHub Actions cron draait dit dagelijks. `bb-price.js` wordt bijgewerkt naar de nieuwe `bookingEngine/v1/services/getPricing` API die expliciete prijsdata geeft.

**Tech Stack:** Playwright (Node.js), GitHub Actions, Cloudflare Pages Functions, Cloudflare KV

---

## Vaste IDs (hardcoded in alle bestanden)

```
configId     = 6dc9094c-76e3-4fd8-83a7-af1d00ffc556
enterpriseId = 65a522c9-4828-413d-9ad8-af1d00ffb83f
serviceId    = 755424cc-3077-4320-b069-af1d00ffbe47
comfortId    = 98900f3b-e5e2-49c9-9776-af1d00ffc315
adultCatId   = af8df461-b6ba-4d46-8253-af1d00ffbed6
childCatId   = 3a6ba692-297a-4818-8eb3-af1d00ffbed7
```

## Response structuur `getPricing`

```json
{
  "CategoryPrices": [{
    "CategoryId": "98900f3b-...",
    "OccupancyPrices": [{
      "Occupancies": [{"AgeCategoryId": "af8df461-...", "PersonCount": 2}],
      "RateGroupPrices": [{
        "MinPrice": {
          "TotalAmount": { "GrossValue": 151.85 }
        }
      }]
    }]
  }]
}
```

GrossValue = kamerprijs voor 2 personen. Deel door 2 voor p.p. prijs.

---

## File Map

| Bestand | Actie | Verantwoordelijkheid |
|---------|-------|---------------------|
| `functions/api/bb-price.js` | Modify | Server-side prijsophaalmechanism via nieuwe Mews API |
| `scripts/refresh-mews-session.js` | Create | Playwright script: session capturen + injecteren |
| `.github/workflows/refresh-mews-session.yml` | Create | Dagelijkse cron die het script uitvoert |
| `package.json` | Create | playwright dependency voor het script |

---

## Task 1: Update `bb-price.js` naar nieuwe Mews API

**Files:**
- Modify: `functions/api/bb-price.js`

- [ ] **Step 1: Vervang de inhoud van `functions/api/bb-price.js`**

```javascript
/**
 * Cloudflare Pages Function — Logies & Ontbijt laagste prijs
 * GET /api/bb-price → { price: 75.93 } of { error: "..." }
 *
 * Leest de Mews sessie uit KV, haalt de laagste prijs op via
 * bookingEngine/v1/services/getPricing voor de Comfort kamer (2 personen),
 * en stuurt de laagste p.p.-prijs terug (afgerond op €0,50).
 *
 * Sessie refreshen: node scripts/refresh-mews-session.js
 */

const CORS = {
  'Content-Type': 'application/json',
  'Access-Control-Allow-Origin': '*',
};

const BOOKING_ENGINE_ID = '6dc9094c-76e3-4fd8-83a7-af1d00ffc556';
const ENTERPRISE_ID     = '65a522c9-4828-413d-9ad8-af1d00ffb83f';
const SERVICE_ID        = '755424cc-3077-4320-b069-af1d00ffbe47';
const COMFORT_ID        = '98900f3b-e5e2-49c9-9776-af1d00ffc315';
const ADULT_CAT_ID      = 'af8df461-b6ba-4d46-8253-af1d00ffbed6';
const CHILD_CAT_ID      = '3a6ba692-297a-4818-8eb3-af1d00ffbed7';
const CLIENT            = 'Mews Distributor 5670.0.0';
const CACHE_SECONDS     = 3600;

function toMewsDate(d) {
  // Mews gebruikt 22:00 UTC als daggrens (= middernacht Amsterdam-tijd)
  const dt = new Date(d);
  dt.setUTCHours(22, 0, 0, 0);
  return dt.toISOString().replace('.000Z', '.000Z');
}

function ceilHalf(price) {
  return Math.ceil(price * 2) / 2;
}

function json(data, status = 200) {
  return new Response(JSON.stringify(data), { status, headers: CORS });
}

export async function onRequestGet(context) {
  const { env } = context;
  const kv = env.ASTERIA_KV;

  if (!kv) return json({ error: 'KV not configured' }, 500);

  const session = await kv.get('mews_session');
  const client  = await kv.get('mews_client') || CLIENT;

  if (!session) return json({ error: 'no session' });

  // Volgende week als representatieve priesdatum
  const now      = new Date();
  const checkin  = new Date(now);
  checkin.setDate(now.getDate() + 7);
  const checkout = new Date(checkin);
  checkout.setDate(checkin.getDate() + 1);

  let data;
  try {
    const res = await fetch('https://api.mews.com/api/bookingEngine/v1/services/getPricing', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Origin':      'https://apps.mews.com',
        'Referer':     'https://apps.mews.com/',
        'User-Agent':  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
      },
      body: JSON.stringify({
        availabilityBlockId: null,
        categoryIds:         [COMFORT_ID],
        currencyCode:        'EUR',
        startUtc:            toMewsDate(checkin),
        endUtc:              toMewsDate(checkout),
        enterpriseId:        ENTERPRISE_ID,
        fullAmounts:         false,
        languageCode:        'nl-NL',
        occupancyData: [
          { ageCategoryId: ADULT_CAT_ID, personCount: 2 },
          { ageCategoryId: CHILD_CAT_ID, personCount: 0 },
        ],
        productIds:      [],
        serviceId:       SERVICE_ID,
        bookingEngineId: BOOKING_ENGINE_ID,
        client:          client,
        session:         session,
      }),
    });
    data = await res.json();
  } catch (e) {
    return json({ error: 'mews fetch failed' });
  }

  if (data.Message) return json({ error: data.Message });

  const catPrices = data.CategoryPrices || [];
  const comfort   = catPrices.find(c => c.CategoryId === COMFORT_ID);
  if (!comfort) return json({ error: 'no category data' });

  // Zoek de 2-persoons occupancy
  const twoPersonOcc = comfort.OccupancyPrices?.find(o =>
    o.Occupancies?.some(a => a.AgeCategoryId === ADULT_CAT_ID && a.PersonCount === 2)
  ) || comfort.OccupancyPrices?.[0];

  if (!twoPersonOcc) return json({ error: 'no occupancy data' });

  const rateGroupPrices = twoPersonOcc.RateGroupPrices || [];
  if (!rateGroupPrices.length) return json({ error: 'no rate group prices' });

  // Laagste prijs over alle rate groups
  let lowestRoom = null;
  for (const rgp of rateGroupPrices) {
    const v = rgp.MinPrice?.TotalAmount?.GrossValue;
    if (v != null && (lowestRoom === null || v < lowestRoom)) lowestRoom = v;
  }

  if (lowestRoom === null) return json({ error: 'no gross value' });

  // Kamerprijs / 2 personen, afgerond op €0,50
  const ppPrice = ceilHalf(lowestRoom / 2);

  return new Response(JSON.stringify({ price: ppPrice }), {
    status: 200,
    headers: {
      ...CORS,
      'Cache-Control': `public, max-age=${CACHE_SECONDS}`,
    },
  });
}

export async function onRequestOptions() {
  return new Response(null, {
    status: 204,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    },
  });
}
```

- [ ] **Step 2: Commit**

```bash
git add functions/api/bb-price.js
git commit -m "feat: bb-price via bookingEngine/v1 getPricing API"
git push
```

---

## Task 2: Playwright script voor sessie-refresh

**Files:**
- Create: `scripts/refresh-mews-session.js`
- Create: `package.json`

- [ ] **Step 1: Check of package.json al bestaat**

```bash
cat package.json 2>/dev/null || echo "niet aanwezig"
```

- [ ] **Step 2: Maak `package.json` aan (of voeg playwright toe als het al bestaat)**

```json
{
  "name": "asteria-pages-scripts",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "refresh-session": "node scripts/refresh-mews-session.js"
  },
  "dependencies": {
    "playwright": "^1.44.0"
  }
}
```

- [ ] **Step 3: Maak `scripts/` map en het script aan**

```bash
mkdir -p scripts
```

Inhoud van `scripts/refresh-mews-session.js`:

```javascript
#!/usr/bin/env node
/**
 * refresh-mews-session.js
 *
 * Opent de Mews Distributor pagina headless, onderschept het
 * configurations/get request, extraheert de sessie + client string,
 * en POST die naar https://visit.asteria.nl/api/session.
 *
 * Gebruik:
 *   node scripts/refresh-mews-session.js
 *   SESSION_TARGET=https://visit.asteria.nl node scripts/refresh-mews-session.js
 */

const { chromium } = require('playwright');

const MEWS_URL      = 'https://api.mews.com/distributor/6dc9094c-76e3-4fd8-83a7-af1d00ffc556';
const SESSION_TARGET = process.env.SESSION_TARGET || 'https://visit.asteria.nl';
const TIMEOUT_MS    = 30_000;

async function run() {
  console.log('Start sessie-refresh...');
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page    = await context.newPage();

  let capturedSession = null;
  let capturedClient  = null;

  // Onderschep configurations/get — die bevat de sessie
  page.on('request', request => {
    if (request.url().includes('/api/bookingEngine/v1/configurations/get')) {
      try {
        const body = JSON.parse(request.postData() || '{}');
        if (body.session) {
          capturedSession = body.session;
          capturedClient  = body.client || 'Mews Distributor 5670.0.0';
          console.log('Sessie gecaptured:', capturedSession.slice(0, 30) + '...');
        }
      } catch (_) {}
    }
  });

  console.log('Navigeer naar Mews Distributor...');
  await page.goto(MEWS_URL, { waitUntil: 'networkidle', timeout: TIMEOUT_MS });

  if (!capturedSession) {
    // Extra wachten als networkidle te vroeg was
    await page.waitForTimeout(5_000);
  }

  await browser.close();

  if (!capturedSession) {
    console.error('FOUT: geen sessie gecaptured.');
    process.exit(1);
  }

  // Injecteer in KV
  const targetUrl = `${SESSION_TARGET}/api/session`;
  console.log(`POST naar ${targetUrl}...`);

  const resp = await fetch(targetUrl, {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify({ session: capturedSession, client: capturedClient }),
  });

  if (!resp.ok) {
    console.error('FOUT bij injecteren:', resp.status, await resp.text());
    process.exit(1);
  }

  const result = await resp.json();
  console.log('Geïnjecteerd:', result);

  // Verificatie
  const priceResp = await fetch(`${SESSION_TARGET}/api/bb-price`);
  const priceData = await priceResp.json();
  console.log('bb-price:', priceData);

  if (!priceData.price) {
    console.error('Verificatie mislukt:', priceData);
    process.exit(1);
  }

  console.log(`Klaar. Prijs: EUR ${priceData.price} p.p.`);
}

run().catch(err => {
  console.error(err);
  process.exit(1);
});
```

- [ ] **Step 4: Installeer dependencies**

```bash
npm install
npx playwright install chromium
```

- [ ] **Step 5: Test het script**

```bash
node scripts/refresh-mews-session.js
```

Verwachte output (verkorte versie):
```
Start sessie-refresh...
Navigeer naar Mews Distributor...
Sessie gecaptured: 054052101048...
POST naar https://visit.asteria.nl/api/session...
Geïnjecteerd: { ok: true, capturedAt: "2026-05-23T..." }
bb-price: { price: 75.93 }
Klaar. Prijs: EUR 75.93 p.p.
```

Als de test slaagt: ga naar Task 3. Als het mislukt: controleer of de Mews pagina bereikbaar is en of `/api/session` antwoordt.

- [ ] **Step 6: Voeg node_modules toe aan .gitignore**

```bash
grep -q "node_modules" .gitignore 2>/dev/null || echo "node_modules" >> .gitignore
```

- [ ] **Step 7: Commit**

```bash
git add scripts/refresh-mews-session.js package.json package-lock.json .gitignore
git commit -m "feat: Playwright script voor dagelijkse Mews sessie-refresh"
git push
```

---

## Task 3: GitHub Actions cron

**Files:**
- Create: `.github/workflows/refresh-mews-session.yml`

- [ ] **Step 1: Maak de map aan**

```bash
mkdir -p .github/workflows
```

- [ ] **Step 2: Maak het workflow bestand**

Inhoud van `.github/workflows/refresh-mews-session.yml`:

```yaml
name: Refresh Mews Session

on:
  schedule:
    # Elke dag om 04:00 UTC (06:00 Amsterdam-tijd)
    - cron: '0 4 * * *'
  workflow_dispatch:  # Handmatig uitvoerbaar via GitHub UI

jobs:
  refresh:
    runs-on: ubuntu-latest
    timeout-minutes: 10

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Install Playwright browsers
        run: npx playwright install chromium --with-deps

      - name: Refresh Mews session
        env:
          SESSION_TARGET: https://visit.asteria.nl
        run: node scripts/refresh-mews-session.js
```

- [ ] **Step 3: Commit en push**

```bash
git add .github/workflows/refresh-mews-session.yml
git commit -m "feat: GitHub Actions cron voor dagelijkse Mews sessie-refresh"
git push
```

- [ ] **Step 4: Trigger handmatig via GitHub UI**

Ga naar: `github.com/bartvandersterren/asteria-pages/actions`
Klik op "Refresh Mews Session" → "Run workflow" → "Run workflow"

Wacht op de run en controleer de logs.

---

## Task 4: Live verificatie

- [ ] **Step 1: Controleer /api/bb-price na GitHub Actions run**

```bash
curl -s https://visit.asteria.nl/api/bb-price
# Verwacht: {"price": <getal>}
```

- [ ] **Step 2: Controleer visueel op hotel-venray.html**

```bash
open https://visit.asteria.nl/hotel-venray
```

Het L&O arrangement kaartje moet een prijs tonen (niet "Laden…").

- [ ] **Step 3: Zelfde voor lander-google**

```bash
open https://visit.asteria.nl/lander-google
```

---

## Bekende risico's

- Mews kan de sessie-bescherming aanpassen. Monitor GitHub Actions logs wekelijks.
- Als de cron faalt, valt de pagina terug op €120 fallback — acceptabel.
- `package.json` in de root: Cloudflare Pages negeert Node bestanden bij HTML-only deploys.
