/**
 * Cloudflare Pages Function: seizoensfoto's en -links voor de flowmails
 *
 *   GET /seizoen/<slot>.jpg       -> de foto van het huidige seizoen (de bytes zelf, geen redirect)
 *   GET /seizoen/lander[/]        -> 302 naar de seizoenslander van nu (/herfst, /winter, /lente, /zomer)
 *   GET /seizoen/arrangement[/]   -> 302 naar het seizoensarrangement van nu
 *   ?datum=YYYY-MM-DD             -> doet alsof het die dag is (testen)
 *
 * Seizoen en doelen staan in seizoen-kalender.json (repo-root). Seizoen wordt bepaald op de datum in
 * Europe/Amsterdam. Foto ruilen = het jpg in mail/seizoen/ vervangen (zelfde maat); geen mail aanraken.
 * Zelfde gedrag en URL-vorm als de Parkhotel-Worker (~/projects/parkhotel-site/src/seizoen.js).
 */

import KALENDER from '../../seizoen-kalender.json';

const DATUM_RE = /^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$/;
const FOTO_RE = /^([a-z0-9-]+)\.jpg$/;

function vandaag(tijdzone) {
  // en-CA geeft YYYY-MM-DD
  return new Intl.DateTimeFormat('en-CA', {
    timeZone: tijdzone, year: 'numeric', month: '2-digit', day: '2-digit',
  }).format(new Date());
}

function seizoenVoor(datum) {
  const md = datum.slice(5);   // MM-DD
  for (const p of KALENDER.periodes) {
    if (p.van <= p.tot) {
      if (md >= p.van && md <= p.tot) return p.seizoen;
    } else if (md >= p.van || md <= p.tot) {   // over de jaargrens (winter)
      return p.seizoen;
    }
  }
  return KALENDER.periodes[0].seizoen;
}

function nietGevonden() {
  return new Response('Niet gevonden', {
    status: 404,
    headers: { 'Content-Type': 'text/plain; charset=utf-8', 'Cache-Control': 'no-store' },
  });
}

function doorsturen(doel, origin, seizoen) {
  return new Response(null, {
    status: 302,
    headers: {
      Location: new URL(doel, origin).toString(),
      'Cache-Control': 'no-store',
      'X-Seizoen': seizoen,
    },
  });
}

export async function onRequestGet(context) {
  const url = new URL(context.request.url);
  const opgegeven = url.searchParams.get('datum');
  const datum = opgegeven && DATUM_RE.test(opgegeven) ? opgegeven : vandaag(KALENDER.tijdzone);
  const seizoen = seizoenVoor(datum);

  const pad = url.pathname.replace(/^\/seizoen\/?/, '').replace(/\/+$/, '');

  if (pad === 'lander' || pad === 'arrangement') {
    const doel = KALENDER[pad][seizoen];
    if (!doel) return nietGevonden();
    return doorsturen(doel, url.origin, seizoen);
  }

  const m = FOTO_RE.exec(pad);
  if (!m) return nietGevonden();
  const slot = KALENDER.slots[m[1]];
  if (!slot || !slot[seizoen]) return nietGevonden();

  const bestand = await context.env.ASSETS.fetch(new URL(slot[seizoen], url.origin));
  if (!bestand.ok) return nietGevonden();

  return new Response(bestand.body, {
    status: 200,
    headers: {
      'Content-Type': 'image/jpeg',
      'Cache-Control': 'public, max-age=3600',
      'X-Seizoen': seizoen,
    },
  });
}
