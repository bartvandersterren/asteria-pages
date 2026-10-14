/**
 * Cloudflare Pages Function: prijskalender "Kies je nachten" voor de arrangementpagina's (lander-w1, blok arrangement)
 *
 *   GET /api/arr-kalender?code=NAJAAR2D&maand=2026-11&deel=1..4[&vers=1]
 *
 * Port van de Parkhotel-Worker (~/projects/parkhotel-site/src/kalender.js) naar Asteria:
 * - Whitelist en instellingen per code in content/arr-kalender.json (gegenereerd door build.py uit de
 *   arrangement-JSON's): {CODE: {slug, nachten, aankomstdagen: [5,6] | null, zondag, standaardkamer}}.
 *   Onbekende code = 400.
 * - Per dag van het DEEL van de maand (1 = 1 t/m 8, 2 = 9 t/m 16, 3 = 17 t/m 24, 4 = 25 t/m het eind) één
 *   Mews Distributor hotels/getAvailability: StartUtc = aankomst, EndUtc = aankomst + nachten, 2 volwassenen,
 *   VoucherCode = code. Per kamercategorie de laagste Price.Total over de PRIVÉ-tarieven in het antwoord
 *   (Rates[].IsPrivate: alleen boekbaar met de code; de publieke kamertarieven die Mews er ook bij geeft tellen
 *   niet mee). Een toekomstig zondagtarief achter dezelfde code wint zo vanzelf.
 *   Dagen die geen aankomstdag mogen zijn (Weekend: alleen vr/za) worden niet bij Mews opgevraagd.
 * - Zondag (alleen als de code zondag:true heeft): per categorie vergelijken met de zaterdag of maandag. Is de
 *   zondagprijs niet lager, dan is de korting nog niet in Mews: prijs_cent = gewoon - 2000 (EUR 20 per kamer,
 *   EUR 10 p.p.), berekend:true. Is hij wel lager, dan de echte prijs, berekend:false. Zat de vergelijkingsdag
 *   niet in het deel (of had die geen prijs voor de categorie), dan één extra call voor de andere buurdag. Geen
 *   vergelijking mogelijk: de Mews-prijs zonder korting (berekend:false).
 * - Antwoord {ok, code, maand, deel, nachten, personen, dagen: [{datum, beschikbaar, zondag, aankomst_mag,
 *   prijzen: {categorie-id: {prijs_cent, berekend}}}]}; een dag die niet opgehaald kon worden: storing:true;
 *   buiten vandaag t/m +18 maanden: buiten_bereik:true.
 * - Cache API (caches.default) 6 uur per code/maand/deel, 5 minuten als er storingsdagen in zitten. `&vers=1`
 *   haalt opnieuw op (hoogstens eens per 2 minuten per sleutel). Geen KV (schrijflimieten).
 * - Mews niet overbelasten: 2 tegelijk, 3 pogingen met wachttijd, harde subrequestteller (onder 45 van de 50
 *   op het Free-plan), tijdbudget per aanvraag. Liever een paar storingsdagen dan een hangende aanvraag.
 * Mews-config 6dc9094c (CLAUDE.md); de oude config wordt hier nooit gebruikt.
 */

import CONFIG from '../../content/arr-kalender.json';

const API = 'https://api.mews.com/api/distributor/v1/hotels/getAvailability';
const CLIENT = 'Asteria Booking 1.0.0';
const CONFIGURATIE = '6dc9094c-76e3-4fd8-83a7-af1d00ffc556';
const HOTEL = '65a522c9-4828-413d-9ad8-af1d00ffb83f';
const TIJDZONE = 'Europe/Amsterdam';
const PERSONEN = 2;
const ZONDAG_KORTING_CENT = 2000;   // EUR 20 per kamer = EUR 10 p.p. (zolang Mews geen zondagtarief heeft)

const GELIJKTIJDIG = 2;
const POGINGEN = 3;
const MAANDEN_VOORUIT = 18;
const CALL_TIMEOUT = 12000;   // één Mews-call
const MAX_WACHT = 8000;       // wachten op Retry-After, per poging
const DAG_BUDGET = 18000;     // alle pogingen samen voor één dag
const RONDE_BUDGET = 25000;   // de hele deelaanvraag
const SUBREQUEST_MAX = 44;    // Free-plan: 50 per invocatie; Mews-calls + cache-bewerkingen tellen mee

const KALENDER_TTL = 6 * 60 * 60;
const ONTBREEKT_TTL = 5 * 60;
const VERS_SLOT_TTL = 120;

const MAAND_RE = /^\d{4}-(0[1-9]|1[0-2])$/;
const DEEL_RE = /^[1-4]$/;
const DEEL_DAGEN = 8;

function antwoord(body, status, extra) {
  const headers = { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store' };
  for (const k in (extra || {})) headers[k] = extra[k];
  return new Response(typeof body === 'string' ? body : JSON.stringify(body), { status: status || 200, headers });
}

function nieuweTeller() {
  return { n: 0, tel() { this.n++; }, ruimte(a) { return this.n + (a || 1) <= SUBREQUEST_MAX; } };
}

export async function onRequestGet(context) {
  const begonnen = Date.now();
  const teller = nieuweTeller();
  try {
    return await route(context, teller, begonnen);
  } catch (err) {
    console.log('[arr-kalender] afgevangen: ' + (err && err.stack ? err.stack : err));
    return antwoord({ ok: false, message: 'De prijzen konden nu niet worden opgehaald.',
      meta: { subrequests: teller.n, duur_ms: Date.now() - begonnen } }, 500);
  }
}

async function route(context, teller, begonnen) {
  const { request } = context;
  const url = new URL(request.url);
  const verversenGevraagd = url.searchParams.get('vers') === '1';

  const code = String(url.searchParams.get('code') || '').trim().toUpperCase();
  if (!code || !Object.prototype.hasOwnProperty.call(CONFIG, code)) {
    return antwoord({ ok: false, message: 'Onbekende code.' }, 400);
  }
  const maand = String(url.searchParams.get('maand') || '');
  if (!MAAND_RE.test(maand)) return antwoord({ ok: false, message: 'Geef een maand als YYYY-MM.' }, 400);
  const deelTekst = String(url.searchParams.get('deel') || '');
  if (!DEEL_RE.test(deelTekst)) return antwoord({ ok: false, message: 'Geef een deel van de maand: deel=1 t/m 4.' }, 400);

  // Sleutel zonder vers en in vaste vorm, zodat elke variant van dezelfde vraag dezelfde cache raakt
  const sleutelUrl = new URL(url.origin + '/api/arr-kalender');
  sleutelUrl.searchParams.set('code', code);
  sleutelUrl.searchParams.set('maand', maand);
  sleutelUrl.searchParams.set('deel', deelTekst);
  const sleutel = new Request(sleutelUrl.toString(), { method: 'GET' });
  const cache = (typeof caches !== 'undefined' && caches.default) ? caches.default : null;

  let uitCache = null;
  if (cache) {
    try { teller.tel(); uitCache = await cache.match(sleutel); } catch (e) { console.log('[arr-kalender] cache lezen: ' + e); }
  }

  let verversen = false;
  if (verversenGevraagd && cache) {
    const slotUrl = new URL(sleutelUrl.toString());
    slotUrl.searchParams.set('vers-slot', '1');
    const slotSleutel = new Request(slotUrl.toString(), { method: 'GET' });
    let slot = null;
    try { teller.tel(); slot = await cache.match(slotSleutel); } catch (e) { /* geen slot */ }
    if (!(slot && uitCache)) {
      verversen = true;
      try {
        teller.tel();
        await cache.put(slotSleutel, new Response('1', { headers: { 'Content-Type': 'text/plain', 'Cache-Control': 'public, max-age=' + VERS_SLOT_TTL } }));
      } catch (e) { /* niets aan te doen */ }
    }
  }

  if (!verversen && uitCache) {
    const h = new Headers(uitCache.headers);
    h.set('x-arr-kalender', 'cache');
    h.set('Cache-Control', 'no-store');
    return new Response(uitCache.body, { status: uitCache.status, headers: h });
  }

  const cfg = CONFIG[code];
  const uit = await kalender(code, cfg, maand, Number(deelTekst), teller);
  if (cache) teller.tel(); // de cache-schrijfactie telt ook mee
  uit.body.meta = { subrequests: teller.n, duur_ms: Date.now() - begonnen };
  const tekst = JSON.stringify(uit.body);

  if (cache) {
    const bewaar = new Response(tekst, { status: 200, headers: {
      'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'public, max-age=' + uit.ttl } });
    const p = cache.put(sleutel, bewaar).catch((e) => console.log('[arr-kalender] cache schrijven: ' + e));
    try { if (context.waitUntil) context.waitUntil(p); } catch (e) { /* niets */ }
  }
  return antwoord(tekst, 200, { 'x-arr-kalender': 'mews' });
}

/* ── datums (hoteltijd) ── */

/** Middernacht hoteltijd op deze datum als UTC-tekst (zelfde als utc() in de Parkhotel-Worker). */
function utc(datumIso) {
  const doel = Date.parse(datumIso + 'T00:00:00Z');
  let gok = doel;
  for (let i = 0; i < 3; i++) gok = doel - zoneVerschuiving(new Date(gok));
  return new Date(gok).toISOString().replace(/\.\d{3}Z$/, 'Z');
}
function zoneVerschuiving(moment) {
  const dtf = new Intl.DateTimeFormat('en-US', { timeZone: TIJDZONE, hour12: false,
    year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit' });
  const d = {};
  for (const p of dtf.formatToParts(moment)) d[p.type] = p.value;
  return Date.UTC(+d.year, +d.month - 1, +d.day, +d.hour % 24, +d.minute, +d.second) - moment.getTime();
}
function vandaag() {
  return new Intl.DateTimeFormat('en-CA', { timeZone: TIJDZONE, year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date());
}
function plusDagen(iso, n) { return new Date(Date.parse(iso + 'T00:00:00Z') + n * 86400000).toISOString().slice(0, 10); }
function plusMaanden(iso, n) {
  const [j, m, d] = iso.split('-').map(Number);
  return new Date(Date.UTC(j, m - 1 + n, d)).toISOString().slice(0, 10);
}
function weekdag(iso) { return new Date(Date.parse(iso + 'T00:00:00Z')).getUTCDay(); } // 0 = zondag

/* ── Mews ── */

function slaap(ms) { return new Promise((r) => setTimeout(r, ms)); }
function wachttijd(header) {
  const s = Number(header);
  if (header && !isNaN(s)) return Math.max(1000, Math.min(MAX_WACHT, s * 1000));
  return 2500;
}

/** Eén getAvailability met harde einddatum en subrequestbudget; gooit bij mislukken (dag wordt storingsdag). */
async function vraag(body, deadline, teller) {
  const payload = JSON.stringify(body);
  let laatste = null;
  for (let poging = 0; poging < POGINGEN; poging++) {
    const over = deadline - Date.now();
    if (over <= 0) { laatste = laatste || new Error('mews_tijd_op'); break; }
    if (!teller.ruimte(2)) { laatste = new Error('mews_subrequests_op'); break; } // één over voor de cache
    const stop = new AbortController();
    const timer = setTimeout(() => stop.abort(), Math.min(CALL_TIMEOUT, over));
    let res = null, data = null, fout = null;
    teller.tel();
    try {
      res = await fetch(API, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: payload, signal: stop.signal });
      if (res.ok) {
        try { data = await res.json(); } catch (e) { fout = new Error('mews_onleesbaar'); }
      } else {
        try { if (res.body) await res.body.cancel(); } catch (e) { /* los */ }
      }
    } catch (e) {
      fout = e;
    } finally {
      clearTimeout(timer);
    }
    if (!res) {
      laatste = fout || new Error('mews_geen_antwoord');
      if (poging < POGINGEN - 1 && Date.now() + 1000 < deadline) { await slaap(1000); continue; }
      throw laatste;
    }
    if (res.status === 429 && poging < POGINGEN - 1) {
      const w = wachttijd(res.headers.get('Retry-After'));
      if (Date.now() + w >= deadline) { laatste = new Error('mews_429_geen_tijd'); break; }
      await slaap(w);
      continue;
    }
    if (!res.ok) {
      laatste = new Error('mews_http_' + res.status);
      if (res.status >= 500 && poging < POGINGEN - 1 && Date.now() + 1000 < deadline) { await slaap(1000); continue; }
      throw laatste;
    }
    if (fout) throw fout;
    return data;
  }
  throw laatste || new Error('mews_mislukt');
}

/** {categorie-id (kleine letters): laagste totaal in centen} over de privé-tarieven (achter de code), of null. */
function privePrijzen(av) {
  const prive = {};
  for (const r of av.Rates || []) if (r && r.IsPrivate) prive[String(r.Id).toLowerCase()] = 1;
  const uit = {};
  for (const rc of av.RoomCategoryAvailabilities || []) {
    const cat = String(rc.RoomCategoryId || '').toLowerCase();
    if (!cat || (rc.AvailableRoomCount || 0) <= 0) continue;
    for (const occ of rc.RoomOccupancyAvailabilities || []) {
      if (occ.AdultCount !== PERSONEN || occ.ChildCount) continue;
      for (const pr of occ.Pricing || []) {
        if (!prive[String(pr.RateId || '').toLowerCase()]) continue;
        const eur = pr.Price && pr.Price.Total ? pr.Price.Total.EUR : null;
        if (eur === null || eur === undefined) continue;
        const cent = Math.round(eur * 100);
        if (uit[cat] === undefined || cent < uit[cat]) uit[cat] = cent;
      }
    }
  }
  return Object.keys(uit).length ? uit : null;
}

async function peil(code, nachten, datum, tot, teller) {
  const deadline = Math.min(Date.now() + DAG_BUDGET, tot);
  return privePrijzen(await vraag({
    Client: CLIENT, ConfigurationId: CONFIGURATIE, HotelId: HOTEL,
    StartUtc: utc(datum), EndUtc: utc(plusDagen(datum, nachten)),
    AdultCount: PERSONEN, ChildCount: 0, VoucherCode: code,
  }, deadline, teller));
}

async function inRijen(lijst, taak) {
  const uit = new Array(lijst.length);
  let volgende = 0;
  const werkers = [];
  for (let w = 0; w < Math.min(GELIJKTIJDIG, lijst.length); w++) {
    werkers.push((async () => {
      for (;;) {
        const i = volgende++;
        if (i >= lijst.length) return;
        uit[i] = await taak(lijst[i], i);
      }
    })());
  }
  await Promise.all(werkers);
  return uit;
}

async function kalender(code, cfg, maand, deel, teller) {
  const nachten = cfg.nachten || 1;
  const aankomstdagen = Array.isArray(cfg.aankomstdagen) && cfg.aankomstdagen.length ? cfg.aankomstdagen : null;
  const nu = vandaag();
  const grens = plusMaanden(nu, MAANDEN_VOORUIT);
  const [jaar, mnd] = maand.split('-').map(Number);
  const aantalDagen = new Date(Date.UTC(jaar, mnd, 0)).getUTCDate();
  const vanDag = (deel - 1) * DEEL_DAGEN + 1;
  const totDag = deel === 4 ? aantalDagen : Math.min(deel * DEEL_DAGEN, aantalDagen);

  const dagen = [];
  for (let d = vanDag; d <= totDag; d++) {
    const iso = maand + '-' + (d < 10 ? '0' : '') + d;
    const wd = weekdag(iso);
    dagen.push({ datum: iso, wd, bereik: iso >= nu && iso <= grens, mag: !aankomstdagen || aankomstdagen.indexOf(wd) > -1 });
  }

  const tot = Date.now() + RONDE_BUDGET;
  const perDatum = {};   // datum -> prijzen | null (geen tarief) | undefined (storing)
  async function haal(datum) {
    if (Object.prototype.hasOwnProperty.call(perDatum, datum)) return perDatum[datum];
    if (Date.now() >= tot || !teller.ruimte(2)) return undefined;
    try {
      perDatum[datum] = await peil(code, nachten, datum, tot, teller);
    } catch (e) {
      console.log('[arr-kalender] ' + code + ' ' + datum + ': ' + e);
      perDatum[datum] = undefined;
    }
    return perDatum[datum];
  }
  const op = dagen.filter((x) => x.bereik && x.mag);
  await inRijen(op, (x) => haal(x.datum));

  // Zondag: buurdag (za of ma) als vergelijking; ontbreekt die in het deel, dan één extra call
  if (cfg.zondag) {
    const extra = [];
    for (const x of op) {
      if (x.wd !== 0 || !perDatum[x.datum]) continue;
      const za = plusDagen(x.datum, -1), ma = plusDagen(x.datum, 1);
      const heeft = (d) => Object.prototype.hasOwnProperty.call(perDatum, d);
      if (!heeft(za) && !heeft(ma)) extra.push(za >= nu ? za : ma);
      else if (heeft(za) && !perDatum[za] && !heeft(ma) && ma <= grens) extra.push(ma);
      else if (heeft(ma) && !perDatum[ma] && !heeft(za) && za >= nu) extra.push(za);
    }
    await inRijen(extra, (d) => haal(d));
  }

  let ontbreekt = false;
  const uit = dagen.map((x) => {
    const basis = { datum: x.datum, zondag: x.wd === 0, aankomst_mag: x.mag };
    if (!x.bereik) return Object.assign(basis, { beschikbaar: false, buiten_bereik: true });
    if (!x.mag) return Object.assign(basis, { beschikbaar: false });
    const r = perDatum[x.datum];
    if (r === undefined) { ontbreekt = true; return Object.assign(basis, { beschikbaar: false, storing: true }); }
    if (r === null) return Object.assign(basis, { beschikbaar: false });
    const prijzen = {};
    for (const cat in r) {
      let cent = r[cat], berekend = false;
      if (cfg.zondag && x.wd === 0) {
        const refs = [perDatum[plusDagen(x.datum, -1)], perDatum[plusDagen(x.datum, 1)]]
          .filter((p) => p && p[cat] !== undefined).map((p) => p[cat]);
        if (refs.length) {
          const gewoon = Math.min.apply(null, refs);
          if (cent >= gewoon) { cent = gewoon - ZONDAG_KORTING_CENT; berekend = true; }
        }
      }
      prijzen[cat] = { prijs_cent: cent, berekend };
    }
    return Object.assign(basis, { beschikbaar: true, prijzen });
  });

  return {
    ttl: ontbreekt ? ONTBREEKT_TTL : KALENDER_TTL,
    body: { ok: true, code, maand, deel, nachten, personen: PERSONEN, dagen: uit },
  };
}
