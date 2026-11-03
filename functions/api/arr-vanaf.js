/**
 * Cloudflare Pages Function: live "vanaf"-prijs voor de arrangementpagina's (lander-w1, blok arrangement)
 *
 *   GET /api/arr-vanaf?codes=WELLNESS2026,NAJAAR2D[&vers=1]
 *   -> {ok, van, tot, prijzen: {CODE: {euro, prijs_cent, datum, nachten, eenheid, volledig} | null}}
 *
 * - Codes uit content/arr-kalender.json (dezelfde whitelist en instellingen als /api/arr-kalender); onbekende
 *   codes worden overgeslagen (staan niet in `prijzen`). Een code waarvoor niets bruikbaars terugkwam (Mews-fout,
 *   geen tarief) = null; de pagina houdt dan de vaste prijs uit de JSON.
 * - Rekenregel en venster in arr-vanaf-kern.js: laagste echte prijs (geen berekende zondagkorting) van de
 *   standaardkamer in de komende 56 dagen, EUR ceil(cent/100/2), p.p. per nacht of p.p. voor het hele verblijf bij
 *   vaste nachten. De dagprijzen komen van de eigen /api/arr-kalender (per maand/deel van 8 dagen, daar 6 uur
 *   gecachet), zodat de Mews-logica op één plek staat en de Mews-calls over aparte invocaties verdeeld worden
 *   (Free-plan: 50 subrequests per invocatie; één code = hoogstens 9 delen).
 * - Edge-cache 3 uur (Cache API + Cache-Control), 5 minuten als een code niet volledig was. `&vers=1` slaat de
 *   eigen cache over. CORS zoals /api/bb-price.
 */

import CONFIG from '../../content/arr-kalender.json';
import { vanafVoorCode, VENSTER_DAGEN, delen } from '../../arr-vanaf-kern.js';

const TTL = 3 * 60 * 60;
const TTL_ONVOLLEDIG = 5 * 60;
const SUBREQUEST_MAX = 44;
const TIJDZONE = 'Europe/Amsterdam';

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

function vandaag() {
  return new Intl.DateTimeFormat('en-CA', { timeZone: TIJDZONE, year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date());
}

export async function onRequestOptions() {
  return new Response(null, { status: 204, headers: CORS });
}

export async function onRequestGet(context) {
  try {
    return await route(context);
  } catch (err) {
    console.log('[arr-vanaf] afgevangen: ' + (err && err.stack ? err.stack : err));
    return antwoord({ ok: false, message: 'De prijzen konden nu niet worden opgehaald.' }, 500, 0);
  }
}

async function route(context) {
  const { request } = context;
  const url = new URL(request.url);
  const codes = [...new Set(String(url.searchParams.get('codes') || '').split(',')
    .map((c) => c.trim().toUpperCase()).filter((c) => c && Object.prototype.hasOwnProperty.call(CONFIG, c)))].sort();
  const van = vandaag();
  const { tot } = delen(van, VENSTER_DAGEN);
  if (!codes.length) return antwoord({ ok: true, van, tot, prijzen: {} }, 200, TTL);

  const sleutelUrl = new URL(url.origin + '/api/arr-vanaf');
  sleutelUrl.searchParams.set('codes', codes.join(','));
  sleutelUrl.searchParams.set('van', van);
  const sleutel = new Request(sleutelUrl.toString(), { method: 'GET' });
  const cache = (typeof caches !== 'undefined' && caches.default) ? caches.default : null;
  let teller = 0;
  if (cache && url.searchParams.get('vers') !== '1') {
    try {
      teller++;
      const hit = await cache.match(sleutel);
      if (hit) {
        const h = new Headers(hit.headers);
        h.set('x-arr-vanaf', 'cache');
        return new Response(hit.body, { status: hit.status, headers: h });
      }
    } catch (e) { console.log('[arr-vanaf] cache lezen: ' + e); }
  }

  // Dagprijzen via de eigen kalender-API (eigen invocatie per deel, eigen Mews-budget en 6 uur cache)
  const haalDeel = async (code, maand, deel) => {
    if (teller + 2 > SUBREQUEST_MAX) throw new Error('subrequests_op');
    teller++;
    const u = new URL(url.origin + '/api/arr-kalender');
    u.searchParams.set('code', code); u.searchParams.set('maand', maand); u.searchParams.set('deel', String(deel));
    const res = await fetch(u.toString(), { headers: { Accept: 'application/json' } });
    if (!res.ok) throw new Error('kalender_http_' + res.status);
    return res.json();
  };

  const prijzen = {};
  let onvolledig = false;
  for (const code of codes) {
    try {
      const r = await vanafVoorCode(code, CONFIG[code], van, haalDeel, VENSTER_DAGEN);
      prijzen[code] = r;
      if (!r || !r.volledig) onvolledig = true;
    } catch (e) {
      console.log('[arr-vanaf] ' + code + ': ' + e);
      prijzen[code] = null; onvolledig = true;
    }
  }

  const ttl = onvolledig ? TTL_ONVOLLEDIG : TTL;
  const tekst = JSON.stringify({ ok: true, van, tot, prijzen });
  if (cache) {
    const p = cache.put(sleutel, new Response(tekst, { status: 200, headers: Object.assign({
      'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'public, max-age=' + ttl }, CORS) }))
      .catch((e) => console.log('[arr-vanaf] cache schrijven: ' + e));
    try { if (context.waitUntil) context.waitUntil(p); } catch (e) { /* niets */ }
  }
  return antwoord(tekst, 200, ttl, { 'x-arr-vanaf': 'kalender' });
}
