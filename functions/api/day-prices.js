/**
 * Cloudflare Pages Function — Dagprijzen-kalender (OTA-stijl datepicker)
 * GET /api/day-prices?from=YYYY-MM-DD&to=YYYY-MM-DD
 *   → { "prices": { "2026-08-01": 114, "2026-08-02": null, ... }, "currency": "EUR" }
 *
 * Per dag de laagste beschikbare kamerprijs (2 volwassenen, 1 nacht, afgerond
 * op hele euro's), zodat de kalender exact matcht met direct boeken via de
 * Mews Booking Engine. `null` = geen kamer beschikbaar om die nacht te starten.
 *
 * Werking (zie asteria-pages CLAUDE.md — Mews Distributor API, 2026-07-09 spike):
 *  - `hotels/getAvailability` geeft géén per-nacht prijzen terug: `Price.Total`
 *    is het VERBLIJFStotaal en `AvailableRoomCount` is het range-MINIMUM. Daarom
 *    doen we per dag een losse 1-nacht-call (StartUtc = dag, EndUtc = dag+1).
 *  - Alleen beschikbare categorieën komen terug; ontbreekt een categorie of is
 *    AvailableRoomCount < 1, dan telt die niet mee. Geen enkele → prijs = null.
 *  - Occupancy zoeken op AdultCount === 2 (NIET op index — de volgorde varieert).
 *  - Client "Asteria Booking 1.0.0" is bij Mews geregistreerd → geen sessie/key.
 *
 * Caching: per kalendermaand in KV (ASTERIA_KV) onder `dayprices:v1:{YYYY-MM}`.
 * Vers < 60 min → direct serveren. Ouder → stale serveren + achtergrond-refresh
 * (ctx.waitUntil). Niets in cache → synchroon bouwen (~5 s voor een maand).
 * Bij een Mews-fout degradeert alles netjes: de kalender werkt zonder prijzen.
 */

const CLIENT      = 'Asteria Booking 1.0.0';
const CONFIG_ID   = '6dc9094c-76e3-4fd8-83a7-af1d00ffc556';
const HOTEL_ID    = '65a522c9-4828-413d-9ad8-af1d00ffb83f';
const CATEGORY_IDS = [
  '98900f3b-e5e2-49c9-9776-af1d00ffc315', // comfort
  '85ca19d7-eea5-41c8-8b93-af1d00ffc315', // comfort-3
  'fa5b6540-7234-49ce-beb1-af1d00ffc315', // mindervalide
  'a8fd7310-0d61-422f-89e6-af1d00ffc315', // royale
  'c737de50-e41e-4c8d-a818-af1d00ffc315', // deluxe
  '27ea8deb-ded5-4856-8fdd-af1d00ffc315', // junior-suite
  '4a642b66-68e6-444c-beeb-af1d00ffc315', // suite
  'a9f18d18-561b-47a9-8ba7-b2a800cfd0e2', // bruidssuite
];

const AVAIL_URL   = 'https://api.mews.com/api/distributor/v1/hotels/getAvailability';
const KV_PREFIX   = 'dayprices:v1:';
const FRESH_MS    = 60 * 60 * 1000;   // < 1 uur = vers
const KV_TTL_S    = 26 * 60 * 60;     // 26 uur in KV bewaren
const BATCH       = 8;                 // gelijktijdige Mews-calls
const MAX_MONTHS  = 3;                 // max kalendermaanden per request
const HORIZON_MO  = 18;                // max vooruit boeken

const CORS = {
  'Content-Type': 'application/json',
  'Access-Control-Allow-Origin': '*',
};

function json(data, status = 200, extraHeaders = {}) {
  return new Response(JSON.stringify(data), { status, headers: { ...CORS, ...extraHeaders } });
}

// UTC-veilige datumhelpers (kalendermaand-berekeningen, geen tijdzone-drift).
function pad(n) { return n < 10 ? '0' + n : '' + n; }
function ymd(y, m, d) { return y + '-' + pad(m) + '-' + pad(d); }
function parseYMD(s) {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(s || '');
  if (!m) return null;
  const y = +m[1], mo = +m[2], d = +m[3];
  if (mo < 1 || mo > 12 || d < 1 || d > 31) return null;
  return { y, m: mo, d };
}
function daysInMonth(y, m) { return new Date(Date.UTC(y, m, 0)).getUTCDate(); }
function todayUTC() {
  const n = new Date();
  return { y: n.getUTCFullYear(), m: n.getUTCMonth() + 1, d: n.getUTCDate() };
}
// Vergelijk twee {y,m,d} → -1/0/1
function cmp(a, b) {
  if (a.y !== b.y) return a.y < b.y ? -1 : 1;
  if (a.m !== b.m) return a.m < b.m ? -1 : 1;
  if (a.d !== b.d) return a.d < b.d ? -1 : 1;
  return 0;
}

// Eén 1-nacht Mews-call → laagste EUR-prijs voor 2 volwassenen, of null.
async function nightPrice(y, m, d) {
  const start = ymd(y, m, d) + 'T12:00:00Z';
  const nd = new Date(Date.UTC(y, m - 1, d + 1)); // dag + 1 (rolt netjes over)
  const end = ymd(nd.getUTCFullYear(), nd.getUTCMonth() + 1, nd.getUTCDate()) + 'T12:00:00Z';

  const res = await fetch(AVAIL_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      Client: CLIENT, ConfigurationId: CONFIG_ID, HotelId: HOTEL_ID,
      StartUtc: start, EndUtc: end, CategoryIds: CATEGORY_IDS,
    }),
  });
  if (!res.ok) throw new Error('mews ' + res.status);
  const data = await res.json();

  let lowest = null;
  for (const cat of (data.RoomCategoryAvailabilities || [])) {
    if ((cat.AvailableRoomCount || 0) < 1) continue;
    for (const occ of (cat.RoomOccupancyAvailabilities || [])) {
      if (occ.AdultCount !== 2 || (occ.ChildCount || 0) !== 0) continue;
      for (const p of (occ.Pricing || [])) {
        const v = p.Price && p.Price.Total && p.Price.Total.EUR;
        if (v != null && (lowest === null || v < lowest)) lowest = v;
      }
    }
  }
  return lowest === null ? null : Math.round(lowest);
}

// Bouw een volledige kalendermaand. Verleden dagen krijgen geen call (null
// wordt niet opgenomen; de widget toont ze sowieso als disabled).
async function buildMonth(ym) {
  const [y, m] = ym.split('-').map(Number);
  const today = todayUTC();
  const last = daysInMonth(y, m);

  const days = [];
  for (let d = 1; d <= last; d++) {
    if (cmp({ y, m, d }, today) < 0) continue; // verleden overslaan
    days.push(d);
  }

  const prices = {};
  for (let i = 0; i < days.length; i += BATCH) {
    const chunk = days.slice(i, i + BATCH);
    const settled = await Promise.allSettled(chunk.map(d => nightPrice(y, m, d)));
    settled.forEach((r, idx) => {
      const d = chunk[idx];
      // Bij een call-fout laten we de dag weg (undefined) i.p.v. null, zodat de
      // widget "nog niet geladen" toont i.p.v. "onbeschikbaar". null = écht vol.
      if (r.status === 'fulfilled') prices[ymd(y, m, d)] = r.value;
    });
  }
  return prices;
}

// Haal een maand uit KV of bouw 'm. Retourneert { prices, refresh } waarbij
// refresh (optioneel) een Promise is die de achtergrond-verversing afmaakt.
async function getMonth(kv, ym) {
  let cached = null;
  try { cached = await kv.get(KV_PREFIX + ym, { type: 'json' }); } catch (_) { /* KV mis */ }

  const now = Date.now();
  if (cached && cached.prices) {
    const age = now - (cached.builtAt || 0);
    if (age < FRESH_MS) return { prices: cached.prices };
    // Stale: serveer meteen, ververs op de achtergrond.
    return {
      prices: cached.prices,
      refresh: (async () => {
        try {
          const fresh = await buildMonth(ym);
          await kv.put(KV_PREFIX + ym, JSON.stringify({ prices: fresh, builtAt: Date.now() }),
            { expirationTtl: KV_TTL_S });
        } catch (_) { /* stil: stale blijft geldig */ }
      })(),
    };
  }

  // Cold miss: synchroon bouwen.
  const prices = await buildMonth(ym);
  try {
    await kv.put(KV_PREFIX + ym, JSON.stringify({ prices, builtAt: Date.now() }),
      { expirationTtl: KV_TTL_S });
  } catch (_) { /* KV-put mislukt: prijzen deze request nog wel serveren */ }
  return { prices };
}

export async function onRequestGet(context) {
  const { env, request, waitUntil } = context;
  const kv = env.ASTERIA_KV;
  const url = new URL(request.url);
  const from = parseYMD(url.searchParams.get('from'));
  const to   = parseYMD(url.searchParams.get('to'));

  if (!from || !to) return json({ error: 'from/to vereist (YYYY-MM-DD)' }, 400);
  if (cmp(from, to) > 0) return json({ error: 'from > to' }, 400);
  if (!kv) return json({ prices: {}, currency: 'EUR', note: 'kv-off' }); // degradeer stil

  // Bereik-validatie: niet in het verleden, binnen horizon.
  const today = todayUTC();
  const maxDate = new Date(Date.UTC(today.y, today.m - 1 + HORIZON_MO, today.d));
  const maxYMD = { y: maxDate.getUTCFullYear(), m: maxDate.getUTCMonth() + 1, d: maxDate.getUTCDate() };
  if (cmp(to, maxYMD) > 0) return json({ error: 'buiten horizon (max +' + HORIZON_MO + ' mnd)' }, 400);

  // Welke kalendermaanden raakt [from, to]?
  const months = [];
  let cy = from.y, cm = from.m;
  while (cy < to.y || (cy === to.y && cm <= to.m)) {
    months.push(ymd(cy, cm, 1).slice(0, 7));
    cm++; if (cm > 12) { cm = 1; cy++; }
    if (months.length > MAX_MONTHS) return json({ error: 'max ' + MAX_MONTHS + ' maanden per request' }, 400);
  }

  const allPrices = {};
  try {
    for (const ym of months) {
      const { prices, refresh } = await getMonth(kv, ym);
      Object.assign(allPrices, prices);
      if (refresh && waitUntil) waitUntil(refresh);
    }
  } catch (_) {
    // Volledige Mews-uitval → lege prijzen; kalender blijft werken.
    return json({ prices: allPrices, currency: 'EUR', note: 'partial' },
      200, { 'Cache-Control': 'public, max-age=60' });
  }

  // Enkel dagen binnen [from, to] teruggeven.
  const out = {};
  for (const [k, v] of Object.entries(allPrices)) {
    const p = parseYMD(k);
    if (p && cmp(p, from) >= 0 && cmp(p, to) <= 0) out[k] = v;
  }

  return json({ prices: out, currency: 'EUR' }, 200, {
    'Cache-Control': 'public, max-age=900, stale-while-revalidate=3600',
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
