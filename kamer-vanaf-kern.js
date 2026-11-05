/**
 * Kern van /api/kamer-vanaf (functions/api/kamer-vanaf.js): laagste prijs per nacht per kamertype (hele kamer) in de
 * komende 56 dagen, voor de kamerprijzen op de spiegel van de staging (/kamers, /kamers/comfort-kamer, ...).
 *
 * Rekenregel (zelfde tariefkeuze als scripts/seizoen_prijzen.py):
 * - Mews Distributor hotels/getAvailability per aankomstdag voor één nacht, ZONDER AdultCount en zonder vouchercode:
 *   Mews geeft dan per categorie alle bezettingen terug, zodat één call per dag alle kamertypes dekt (Comfort 3-persoons
 *   op 3 volwassenen, de rest op 2). Altijd CurrencyCode 'EUR': zonder geeft Mews alle valuta en is het antwoord zonder
 *   AdultCount ~22 MB (Worker-fout 1102, geheugen); met EUR ~340 kB (gemeten 3 nov 2026).
 * - Per kamertype de laagste Price.Total.EUR over de publieke tarieven (Rates[].IsPrivate false) waarvan de naam geen
 *   "OTA" bevat (die zijn voor de boekingssites), bij de bezetting AdultCount = personen, ChildCount 0, en alleen als
 *   AvailableRoomCount > 0.
 * - Over het venster de laagste dag; euro = ceil(prijs_cent / 100) (hele kamer per nacht, naar boven op hele euro's).
 * Het venster wordt in delen van 8 dagen opgehaald (eigen invocatie per deel, Free-plan 50 subrequests).
 * Puur (fetch wordt meegegeven), zodat node --test hem kan draaien: scripts/test_kamer_vanaf.mjs.
 * Mews-aanroep, Client-header, pogingen bij 429 en tijdzone zoals functions/api/arr-kalender.js.
 */

export const VENSTER_DAGEN = 56;
export const DEEL_DAGEN = 8;
export const AANTAL_DELEN = Math.ceil(VENSTER_DAGEN / DEEL_DAGEN);   // 7

export const API = 'https://api.mews.com/api/distributor/v1/hotels/getAvailability';
export const CLIENT = 'Asteria Booking 1.0.0';
export const CONFIGURATIE = '6dc9094c-76e3-4fd8-83a7-af1d00ffc556';
export const HOTEL = '65a522c9-4828-413d-9ad8-af1d00ffb83f';
const TIJDZONE = 'Europe/Amsterdam';

/* sleutel = build.py KAMER_MEWS / build_kamers.py CATEGORY; personen = bezetting waarvoor de prijs geldt */
export const KAMERS = {
  'comfort': { id: '98900f3b-e5e2-49c9-9776-af1d00ffc315', personen: 2 },
  'comfort-3': { id: '85ca19d7-eea5-41c8-8b93-af1d00ffc315', personen: 3 },
  'mindervalide': { id: 'fa5b6540-7234-49ce-beb1-af1d00ffc315', personen: 2 },
  'royale': { id: 'a8fd7310-0d61-422f-89e6-af1d00ffc315', personen: 2 },
  'deluxe': { id: 'c737de50-e41e-4c8d-a818-af1d00ffc315', personen: 2 },
  'junior-suite': { id: '27ea8deb-ded5-4856-8fdd-af1d00ffc315', personen: 2 },
  'suite': { id: '4a642b66-68e6-444c-beeb-af1d00ffc315', personen: 2 },
  'bruidssuite': { id: 'a9f18d18-561b-47a9-8ba7-b2a800cfd0e2', personen: 2 },
};

const POGINGEN = 3;
const CALL_TIMEOUT = 12000;
const MAX_WACHT = 8000;

/* ── datums (hoteltijd), zoals arr-kalender.js ── */
export function plusDagen(iso, n) { return new Date(Date.parse(iso + 'T00:00:00Z') + n * 86400000).toISOString().slice(0, 10); }
export function weekdag(iso) { return new Date(Date.parse(iso + 'T00:00:00Z')).getUTCDay(); }
export function vandaag(nu) {
  return new Intl.DateTimeFormat('en-CA', { timeZone: TIJDZONE, year: 'numeric', month: '2-digit', day: '2-digit' }).format(nu || new Date());
}
function zoneVerschuiving(moment) {
  const dtf = new Intl.DateTimeFormat('en-US', { timeZone: TIJDZONE, hour12: false,
    year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit' });
  const d = {};
  for (const p of dtf.formatToParts(moment)) d[p.type] = p.value;
  return Date.UTC(+d.year, +d.month - 1, +d.day, +d.hour % 24, +d.minute, +d.second) - moment.getTime();
}
/** Middernacht hoteltijd op deze datum als UTC-tekst. */
export function utc(datumIso) {
  const doel = Date.parse(datumIso + 'T00:00:00Z');
  let gok = doel;
  for (let i = 0; i < 3; i++) gok = doel - zoneVerschuiving(new Date(gok));
  return new Date(gok).toISOString().replace(/\.\d{3}Z$/, 'Z');
}

/** Dagen van deel n (1..7) van het venster vanaf `van`. */
export function dagenVanDeel(van, deel) {
  const uit = [];
  for (let i = (deel - 1) * DEEL_DAGEN; i < Math.min(deel * DEEL_DAGEN, VENSTER_DAGEN); i++) uit.push(plusDagen(van, i));
  return uit;
}

/** {sleutel: laagste totaal in centen} voor één getAvailability-antwoord (één nacht); ontbrekende kamer = geen sleutel. */
export function dagPrijzen(av) {
  const publiek = {};
  for (const r of (av && av.Rates) || []) {
    if (!r || r.IsPrivate) continue;
    const namen = r.Name ? Object.values(r.Name).join(' ') : '';
    if (/\bOTA\b/i.test(namen)) continue;
    publiek[String(r.Id).toLowerCase()] = 1;
  }
  const perId = {};
  for (const k in KAMERS) perId[KAMERS[k].id] = k;
  const uit = {};
  for (const rc of (av && av.RoomCategoryAvailabilities) || []) {
    const sleutel = perId[String(rc.RoomCategoryId || '').toLowerCase()];
    if (!sleutel || (rc.AvailableRoomCount || 0) <= 0) continue;
    const personen = KAMERS[sleutel].personen;
    for (const occ of rc.RoomOccupancyAvailabilities || []) {
      if (occ.AdultCount !== personen || occ.ChildCount) continue;
      for (const pr of occ.Pricing || []) {
        if (!publiek[String(pr.RateId || '').toLowerCase()]) continue;
        const eur = pr.Price && pr.Price.Total ? pr.Price.Total.EUR : null;
        if (typeof eur !== 'number') continue;
        const cent = Math.round(eur * 100);
        if (uit[sleutel] === undefined || cent < uit[sleutel]) uit[sleutel] = cent;
      }
    }
  }
  return uit;
}

function slaap(ms) { return new Promise((r) => setTimeout(r, ms)); }
function wachttijd(header) {
  const s = Number(header);
  if (header && !isNaN(s)) return Math.max(1000, Math.min(MAX_WACHT, s * 1000));
  return 2500;
}

/** Eén getAvailability voor één nacht, met pogingen bij 429/5xx; gooit bij mislukken. */
export async function vraagNacht(datum, doeFetch, deadline) {
  const payload = JSON.stringify({ Client: CLIENT, ConfigurationId: CONFIGURATIE, HotelId: HOTEL,
    StartUtc: utc(datum), EndUtc: utc(plusDagen(datum, 1)), CurrencyCode: 'EUR' });
  let laatste = null;
  for (let poging = 0; poging < POGINGEN; poging++) {
    const over = deadline - Date.now();
    if (over <= 0) throw laatste || new Error('mews_tijd_op');
    const stop = typeof AbortController !== 'undefined' ? new AbortController() : null;
    const timer = stop ? setTimeout(() => stop.abort(), Math.min(CALL_TIMEOUT, over)) : null;
    let res;
    try {
      res = await doeFetch(API, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: payload, signal: stop ? stop.signal : undefined });
    } catch (e) {
      laatste = e;
      if (timer) clearTimeout(timer);
      if (poging < POGINGEN - 1) { await slaap(1000); continue; }
      throw e;
    }
    if (timer) clearTimeout(timer);
    if (res.status === 429 && poging < POGINGEN - 1) {
      const w = wachttijd(res.headers && res.headers.get ? res.headers.get('Retry-After') : null);
      if (Date.now() + w >= deadline) throw new Error('mews_429_geen_tijd');
      await slaap(w);
      laatste = new Error('mews_429');
      continue;
    }
    if (!res.ok) {
      laatste = new Error('mews_http_' + res.status);
      if (res.status >= 500 && poging < POGINGEN - 1) { await slaap(1000); continue; }
      throw laatste;
    }
    return res.json();
  }
  throw laatste || new Error('mews_mislukt');
}

/** Deel ophalen: na elkaar (Mews geeft 429 bij parallelle reeksen). -> {dagen: [{datum, prijzen} | {datum, storing}]} */
export async function haalDeel(van, deel, doeFetch, budgetMs) {
  const deadline = Date.now() + (budgetMs || 25000);
  const dagen = [];
  for (const datum of dagenVanDeel(van, deel)) {
    try {
      dagen.push({ datum, prijzen: dagPrijzen(await vraagNacht(datum, doeFetch, deadline)) });
    } catch (e) {
      dagen.push({ datum, storing: true, fout: String(e && e.message || e) });
    }
  }
  return { dagen };
}

/** Delen samenvoegen tot {prijzen: {sleutel: {euro, prijs_cent, datum, zondag} | null}, volledig}. */
export function combineer(deelAntwoorden) {
  const best = {};
  let volledig = deelAntwoorden.length === AANTAL_DELEN;
  for (const d of deelAntwoorden) {
    if (!d || !Array.isArray(d.dagen)) { volledig = false; continue; }
    for (const dag of d.dagen) {
      if (dag.storing) { volledig = false; continue; }
      for (const k in dag.prijzen || {}) {
        const cent = dag.prijzen[k];
        if (typeof cent !== 'number') continue;
        if (!best[k] || cent < best[k].prijs_cent) best[k] = { prijs_cent: cent, datum: dag.datum };
      }
    }
  }
  const prijzen = {};
  for (const k in KAMERS) {
    const b = best[k];
    prijzen[k] = b ? { euro: Math.ceil(b.prijs_cent / 100 - 1e-9), prijs_cent: b.prijs_cent, datum: b.datum, zondag: weekdag(b.datum) === 0 } : null;
  }
  return { prijzen, volledig };
}
