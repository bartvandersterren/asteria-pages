/**
 * Cloudflare Pages Function: live "vanaf"-prijs per kamertype voor de spiegel van de staging (/kamers, kamerdetails, /home-nieuw)
 *
 *   GET /api/kamer-vanaf[?vers=1]
 *   -> {ok, van, tot, prijzen: {comfort|comfort-3|mindervalide|royale|deluxe|junior-suite|suite|bruidssuite:
 *        {euro, prijs_cent, datum, zondag} | null}, volledig}
 *   GET /api/kamer-vanaf?deel=1..7   (intern: 8 dagen van het venster, eigen invocatie en eigen Mews-budget)
 *
 * - Rekenregel in kamer-vanaf-kern.js: laagste prijs per nacht voor de hele kamer (2 volwassenen, Comfort 3-persoons 3)
 *   over de publieke niet-OTA-tarieven zonder vouchercode, komende 56 dagen, naar boven op hele euro's. null = geen prijs
 *   (geen beschikbaarheid of Mews-fout); de pagina verbergt dan de prijsregel.
 * - Zoals /api/arr-vanaf: het venster wordt per deel opgehaald via de eigen URL (?deel=), na elkaar (parallel gaf 429 van
 *   Mews); elk deel doet zijn 8 Mews-calls na elkaar. Edge-cache (Cache API) 3 uur, 5 minuten als iets ontbrak; `&vers=1`
 *   slaat de cache over. CORS zoals /api/arr-vanaf.
 */

import { AANTAL_DELEN, VENSTER_DAGEN, combineer, haalDeel, plusDagen, vandaag } from '../../kamer-vanaf-kern.js';

const TTL = 3 * 60 * 60;
const TTL_ONVOLLEDIG = 5 * 60;

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

function antwoord(body, status, ttl, extra) {
  const headers = Object.assign({ 'Content-Type': 'application/json; charset=utf-8',
    'Cache-Control': ttl ? 'public, max-age=' + ttl : 'no-store' }, CORS, extra || {});
  return new Response(typeof body === 'string' ? body : JSON.stringify(body), { status: status || 200, headers });
}

export async function onRequestOptions() {
  return new Response(null, { status: 204, headers: CORS });
}

export async function onRequestGet(context) {
  try {
    return await route(context);
  } catch (err) {
    console.log('[kamer-vanaf] afgevangen: ' + (err && err.stack ? err.stack : err));
    return antwoord({ ok: false, message: 'De prijzen konden nu niet worden opgehaald.' }, 500, 0);
  }
}

async function uitCache(cache, sleutel, label) {
  if (!cache) return null;
  try {
    const hit = await cache.match(sleutel);
    if (!hit) return null;
    const h = new Headers(hit.headers);
    h.set('x-kamer-vanaf', 'cache' + (label ? '-' + label : ''));
    return new Response(hit.body, { status: hit.status, headers: h });
  } catch (e) { console.log('[kamer-vanaf] cache lezen: ' + e); return null; }
}

function bewaar(context, cache, sleutel, tekst, ttl) {
  if (!cache) return;
  const p = cache.put(sleutel, new Response(tekst, { status: 200, headers: Object.assign({
    'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'public, max-age=' + ttl }, CORS) }))
    .catch((e) => console.log('[kamer-vanaf] cache schrijven: ' + e));
  try { if (context.waitUntil) context.waitUntil(p); } catch (e) { /* niets */ }
}

async function route(context) {
  const url = new URL(context.request.url);
  const vers = url.searchParams.get('vers') === '1';
  const van = vandaag();
  const tot = plusDagen(van, VENSTER_DAGEN - 1);
  const cache = (typeof caches !== 'undefined' && caches.default) ? caches.default : null;
  const deelTekst = url.searchParams.get('deel');

  if (deelTekst !== null) {
    const deel = Number(deelTekst);
    if (!(deel >= 1 && deel <= AANTAL_DELEN && Number.isInteger(deel))) {
      return antwoord({ ok: false, message: 'deel = 1 t/m ' + AANTAL_DELEN }, 400, 0);
    }
    const sleutel = new Request(url.origin + '/api/kamer-vanaf?deel=' + deel + '&van=' + van, { method: 'GET' });
    if (!vers) { const hit = await uitCache(cache, sleutel, 'deel'); if (hit) return hit; }
    const r = await haalDeel(van, deel, fetch, 25000);
    const onvolledig = r.dagen.some((d) => d.storing);
    const tekst = JSON.stringify({ ok: true, van, deel, dagen: r.dagen });
    bewaar(context, cache, sleutel, tekst, onvolledig ? TTL_ONVOLLEDIG : TTL);
    return antwoord(tekst, 200, onvolledig ? TTL_ONVOLLEDIG : TTL, { 'x-kamer-vanaf': 'mews' });
  }

  const sleutel = new Request(url.origin + '/api/kamer-vanaf?van=' + van, { method: 'GET' });
  if (!vers) { const hit = await uitCache(cache, sleutel); if (hit) return hit; }

  // delen na elkaar via de eigen URL (eigen invocatie, eigen subrequestbudget en eigen cache per deel)
  const delen = [];
  for (let deel = 1; deel <= AANTAL_DELEN; deel++) {
    try {
      const u = new URL(url.origin + '/api/kamer-vanaf');
      u.searchParams.set('deel', String(deel));
      if (vers) u.searchParams.set('vers', '1');
      const res = await fetch(u.toString(), { headers: { Accept: 'application/json' } });
      delen.push(res.ok ? await res.json() : null);
    } catch (e) {
      console.log('[kamer-vanaf] deel ' + deel + ': ' + e);
      delen.push(null);
    }
  }
  const { prijzen, volledig } = combineer(delen);
  const ttl = volledig ? TTL : TTL_ONVOLLEDIG;
  const tekst = JSON.stringify({ ok: true, van, tot, prijzen, volledig });
  bewaar(context, cache, sleutel, tekst, ttl);
  return antwoord(tekst, 200, ttl, { 'x-kamer-vanaf': 'mews' });
}
