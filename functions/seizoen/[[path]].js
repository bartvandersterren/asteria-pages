/**
 * Cloudflare Pages Function: seizoensfoto's en -links voor de flowmails
 *
 *   GET /seizoen/ (of /seizoen)  -> overzichtspagina (HTML, noindex): bron, periodes, foto's en link-doelen
 *   GET /seizoen/<slot>.jpg       -> de foto van de huidige periode (de bytes zelf, geen redirect)
 *   GET /seizoen/lander[/]        -> 302 naar de seizoenslander van nu (/herfst, /winter, /lente, /zomer)
 *   GET /seizoen/arrangement[/]   -> 302 naar het seizoensarrangement van nu
 *   ?datum=YYYY-MM-DD             -> doet alsof het die dag is (testen); ?vers=1 haalt actief.json opnieuw op
 *   GET en HEAD (HEAD: zelfde headers, lege body; mailproxy's en linkcheckers doen eerst HEAD), rest 405.
 *
 * Bron: seizoen/asteria/actief.json op R2 (OS > Mediabank > Seizoensfoto's), 5 min in de Cache API; valt die
 * weg, dan seizoen-kalender.json (repo-root) met de foto's in mail/seizoen/. Logica in seizoen-kern.js
 * (gelijk aan ~/projects/parkhotel-site/src/seizoen-kern.js; zelfde URL-vorm en JSON-schema als de
 * Parkhotel-Worker src/seizoen.js). Periode wordt bepaald op de datum in Europe/Amsterdam.
 * Env-variabele SEIZOEN_BASIS (optioneel) overschrijft de R2-basis, voor lokaal testen.
 */

import BUNDEL from '../../seizoen-kalender.json';
import {
  basisVan, fotoVoor, laadKalenderVan, linkVoor, middenVan, periodeVan, seizoenVoor, volgendeWissels,
} from '../../seizoen-kern.js';

const DATUM_RE = /^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$/;
const FOTO_RE = /^([a-z0-9-]+)\.jpg$/;

/** Actieve kalender: R2 (actief.json) of de meegebundelde. { kalender, bron, reden?, bundel } */
function laadKalender(request, env, ctx) {
  return laadKalenderVan(request, env, ctx, BUNDEL);
}

function vandaag(tijdzone) {
  // en-CA geeft YYYY-MM-DD
  return new Intl.DateTimeFormat('en-CA', {
    timeZone: tijdzone, year: 'numeric', month: '2-digit', day: '2-digit',
  }).format(new Date());
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

// Haalt de jpg-bytes: R2 bij een `key`, anders het bestand in de repo (`pad`). null = mislukt.
async function haalFoto(foto, env, origin) {
  try {
    if (foto.key) {
      const r = await fetch(`${basisVan(env)}/${String(foto.key).replace(/^\/+/, '')}`, {
        cf: { cacheTtl: 3600, cacheEverything: true },
      });
      return r.ok ? r : null;
    }
    const r = await env.ASSETS.fetch(new URL(foto.pad, origin));
    return r.ok ? r : null;
  } catch (e) {
    console.log('[seizoen] foto ophalen mislukt: ' + e);
    return null;
  }
}

const MAANDEN = ['jan', 'feb', 'mrt', 'apr', 'mei', 'jun', 'jul', 'aug', 'sep', 'okt', 'nov', 'dec'];
const SLOTUITLEG = { hero: 'Hero-achtergrond bovenaan de mail', sfeer: 'Sfeerfoto in de mail' };

function esc(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function kortMd(md) {
  const [m, d] = md.split('-').map(Number);
  if (m === 2 && d >= 28) return 'eind feb';
  return `${d} ${MAANDEN[m - 1]}`;
}

function langeDatum(datum) {
  const [j, m, d] = datum.split('-').map(Number);
  return new Intl.DateTimeFormat('nl-NL', { timeZone: 'UTC', day: 'numeric', month: 'long', year: 'numeric' })
    .format(new Date(Date.UTC(j, m - 1, d)));
}

function tijdTekst(waarde, tijdzone) {
  const d = new Date(waarde);
  if (Number.isNaN(d.getTime())) return String(waarde);
  return new Intl.DateTimeFormat('nl-NL', {
    timeZone: tijdzone, day: 'numeric', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit',
  }).format(d);
}

function periodeTekst(kalender, id) {
  const p = periodeVan(kalender, id);
  return p ? `${kortMd(p.van)} t/m ${kortMd(p.tot)}` : '';
}

const naamVan = (kalender, id) => (periodeVan(kalender, id) || {}).naam || id;
const maatTekst = (maat) => (Array.isArray(maat) ? maat.join('x') : maat || '');

function doelLink(doel) {
  return doel ? `<a href="${esc(doel)}">${esc(doel)}</a>` : '<em>geen eigen doel</em>';
}

function overzichtHtml(datum, gesimuleerd, actief) {
  const { kalender, bundel, bron } = actief;
  const seizoen = seizoenVoor(kalender, datum.slice(5));
  const dq = gesimuleerd ? `?datum=${datum}` : '';
  const links = kalender.links || {};
  const nuLabel = (id) => (id === seizoen ? ' <span class="label">Nu</span>' : '');
  const tr = (id) => `<tr${id === seizoen ? ' class="nu"' : ''}>`;

  const bronRegel = bron === 'r2'
    ? `<span class="bron-r2">Bron: R2</span> <code>seizoen/${esc(kalender.hotel || bundel.hotel)}/actief.json</code>`
      + (kalender.bijgewerkt_op ? ` · bijgewerkt op ${esc(tijdTekst(kalender.bijgewerkt_op, kalender.tijdzone))}` : '')
      + (kalender.bijgewerkt_door ? ` door ${esc(kalender.bijgewerkt_door)}` : '')
    : `<span class="bron-repo">Bron: repo</span> meegebundelde kalender <code>seizoen-kalender.json</code>`
      + ` (R2: ${esc(actief.reden || 'geen actief.json')})`;

  const kalenderRijen = kalender.periodes.map((p) =>
    `${tr(p.id)}<td>${esc(p.naam || p.id)}${nuLabel(p.id)}</td>`
    + `<td>${kortMd(p.van)}</td><td>${kortMd(p.tot)}</td><td>${esc(p.prioriteit || 0)}</td>`
    + `<td>${doelLink((links.lander || {})[p.id])}</td><td>${doelLink((links.arrangement || {})[p.id])}</td></tr>`).join('\n');

  const slotNamen = Object.keys(kalender.slots);
  for (const s of Object.keys(bundel.slots)) if (!slotNamen.includes(s)) slotNamen.push(s);

  const slotBlokken = slotNamen.map((naam) => {
    const slot = kalender.slots[naam] || bundel.slots[naam];
    const fotos = kalender.periodes.map((p) => {
      const nu = p.id === seizoen;
      const midden = middenVan(p);
      const src = `/seizoen/${naam}.jpg?datum=${datum.slice(0, 4)}-${midden}`;
      const keuze = fotoVoor(kalender, naam, midden, bundel);
      const f = keuze ? keuze.foto : {};
      const bestand = String(f.key || f.pad || '').split('/').pop();
      const herkomst = f.key ? 'R2' : 'repo';
      const ander = keuze && keuze.periode !== p.id
        ? `<p class="let">Geen eigen foto: toont ${esc(naamVan(keuze.uitBundel ? bundel : kalender, keuze.periode))}${keuze.uitBundel && bron === 'r2' ? ' (repo)' : ''}</p>` : '';
      const lander = f.landerfoto && (!keuze || keuze.periode === p.id)
        ? `<p class="let">Nog geen echt ${esc((p.naam || p.id).toLowerCase())}beeld: foto van de seizoenslander</p>` : '';
      return `<figure class="foto${nu ? ' nu' : ''}">`
        + (nu ? '<span class="label">Nu</span>' : '')
        + `<img src="${esc(src)}" alt="${esc(naam)} ${esc(p.naam || p.id)}" loading="lazy">`
        + `<figcaption><strong>${esc(p.naam || p.id)}</strong> · ${periodeTekst(kalender, p.id)}<br>`
        + `<code>${esc(bestand)}</code><br><span class="zacht">${herkomst} · bron: ${esc(f.bron || 'onbekend')}${f.door ? ` · door ${esc(f.door)}` : ''}</span>${ander}${lander}</figcaption></figure>`;
    }).join('\n');
    const mails = (slot.mails || []).map((m) => `<li>${esc(m)}</li>`).join('');
    return `<section class="blok"><h2>${esc(naam)} <span class="zacht">· ${esc(maatTekst(slot.maat))}</span></h2>`
      + `<p class="zacht">${esc(SLOTUITLEG[naam] || '')} · <code>/seizoen/${esc(naam)}.jpg</code></p>`
      + `<p>Staat in: </p><ul class="mails">${mails}</ul>`
      + `<div class="fotos">${fotos}</div></section>`;
  }).join('\n');

  const linkBlok = ['lander', 'arrangement'].map((soort) => {
    const rijen = kalender.periodes.map((p) => {
      const doel = (links[soort] || {})[p.id];
      const geen = soort === 'arrangement' && /^https:\/\/www\.asteria\.nl\/arrangementen/.test(doel || '')
        ? ' <span class="zacht">(nog geen seizoensarrangement)</span>' : '';
      return `${tr(p.id)}<td>${esc(p.naam || p.id)}${nuLabel(p.id)}</td><td>${doelLink(doel)}${geen}</td></tr>`;
    }).join('\n');
    return `<h3><a href="/seizoen/${soort}/${dq}">/seizoen/${soort}/</a></h3>`
      + `<div class="tabel"><table><thead><tr><th>Periode</th><th>Doel</th></tr></thead><tbody>${rijen}</tbody></table></div>`;
  }).join('\n');

  const wissels = volgendeWissels(kalender, datum, 2).map((w) =>
    `<li><a href="/seizoen/?datum=${w.datum}">/seizoen/?datum=${w.datum}</a> (${langeDatum(w.datum)}, begin ${esc(naamVan(kalender, w.periode).toLowerCase())})</li>`).join('');

  const naamNu = esc(naamVan(kalender, seizoen).toLowerCase());
  const datumRegel = (gesimuleerd
    ? `Gesimuleerde datum ${langeDatum(datum)} · periode ${naamNu} · <a href="/seizoen/">terug naar vandaag</a>`
    : `Vandaag ${langeDatum(datum)} · periode ${naamNu}`) + `<br>${bronRegel}`;

  return `<!doctype html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Seizoensfoto's flowmails · Hotel Asteria</title>
<style>
  :root { --zand: #F7E7D1; --ivoor: #FFFAF1; --kastanje: #442A06; --terracotta: #C76E4E; --tekst: #3a2a17; --lijn: #e6d3b8; }
  * { box-sizing: border-box; }
  body { margin: 0; background: var(--ivoor); color: var(--tekst); font: 16px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
  main { max-width: 1100px; margin: 0 auto; padding: 32px 16px 64px; }
  h1, h2, h3 { color: var(--kastanje); line-height: 1.25; }
  h1 { font-size: 28px; margin: 0 0 6px; }
  h2 { font-size: 22px; margin: 0 0 4px; text-transform: capitalize; }
  h2 .zacht { text-transform: none; }
  h3 { font-size: 18px; margin: 24px 0 8px; }
  a { color: var(--kastanje); }
  code { font-size: 13px; background: var(--zand); padding: 1px 5px; border-radius: 3px; word-break: break-all; }
  .zacht { color: #7a6650; font-weight: normal; }
  .datum { margin: 0 0 20px; font-size: 17px; }
  .blok { background: #fff; border: 1px solid var(--lijn); border-radius: 6px; padding: 20px; margin: 28px 0; }
  .blok > p { margin: 4px 0; }
  table { border-collapse: collapse; width: 100%; background: #fff; }
  th, td { text-align: left; padding: 8px 10px; border-bottom: 1px solid var(--lijn); vertical-align: top; overflow-wrap: anywhere; }
  th { color: var(--kastanje); font-size: 14px; background: var(--zand); }
  tr.nu td { background: #fbefe9; font-weight: 600; }
  td:first-child, th:first-child { width: 150px; }
  .tabel { overflow-x: auto; }
  .label { display: inline-block; background: var(--terracotta); color: #fff; font-size: 12px; font-weight: 700; letter-spacing: .04em; text-transform: uppercase; padding: 2px 8px; border-radius: 3px; }
  .mails { display: flex; flex-wrap: wrap; gap: 6px; list-style: none; padding: 0; margin: 4px 0 16px; }
  .mails li { background: var(--zand); border-radius: 3px; padding: 2px 8px; font-size: 14px; }
  .fotos { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }
  .foto { position: relative; margin: 0; border: 3px solid transparent; border-radius: 5px; padding: 6px; }
  .foto.nu { border-color: var(--terracotta); }
  .foto .label { position: absolute; top: 14px; left: 14px; }
  .foto img { display: block; width: 100%; height: auto; border-radius: 2px; background: var(--zand); }
  figcaption { font-size: 14px; margin-top: 8px; }
  .let { margin: 6px 0 0; font-size: 13px; color: #8a4a2f; }
  ol, ul.stap { padding-left: 20px; }
  .bron-r2, .bron-repo { display: inline-block; font-size: 13px; font-weight: 700; padding: 1px 8px; border-radius: 3px; color: #fff; }
  .bron-r2 { background: var(--kastanje); } .bron-repo { background: #8a6d3b; }
  @media (max-width: 760px) {
    th, td { padding: 6px; font-size: 14px; }
    .fotos { grid-template-columns: 1fr; }
    h1 { font-size: 23px; }
  }
</style>
</head>
<body>
<main>
<h1>Seizoensfoto's in de flowmails · Hotel Asteria</h1>
<p class="datum">${datumRegel}</p>
<div class="tabel"><table>
<thead><tr><th>Periode</th><th>Van</th><th>Tot en met</th><th>Prioriteit</th><th>Lander-doel</th><th>Arrangement-doel</th></tr></thead>
<tbody>
${kalenderRijen}
</tbody></table></div>

${slotBlokken}

<section class="blok"><h2>Links</h2>
<p class="zacht">Vaste links in de mails; de server stuurt door naar het doel van de huidige periode.</p>
${linkBlok}
</section>

<section class="blok"><h2>Zo ruil je een foto</h2>
<ol>
<li>Open het OS: <strong>Mediabank › Seizoensfoto's</strong> (os.asteria.nl). Kies bij het slot en de periode "Wisselen", kies of upload een foto, zet de uitsnede en sla op.</li>
<li>Het OS zet de foto op R2 en werkt <code>seizoen/asteria/actief.json</code> bij; de site neemt dat binnen 5 minuten over. Mailclients cachen de foto tot 1 uur. Geen mail aanraken, geen commit nodig.</li>
<li>Periodes (ook een extra periode zoals feestdagen) en linkdoelen pas je daar ook aan.</li>
<li>De repo is de terugval: zonder (geldige) <code>actief.json</code> gelden <code>seizoen-kalender.json</code> en de foto's in <code>mail/seizoen/</code>.</li>
</ol>
</section>

<section class="blok"><h2>Zo kijk je vooruit</h2>
<p>Zet <code>?datum=JJJJ-MM-DD</code> achter de URL, bv. <a href="/seizoen/?datum=2026-12-15"><code>/seizoen/?datum=2026-12-15</code></a>. Dat werkt ook op de foto's en links.</p>
<p>De eerstvolgende wissels:</p>
<ul class="stap">${wissels}</ul>
</section>
</main>
</body>
</html>
`;
}

async function behandel(context) {
  const url = new URL(context.request.url);
  const actief = await laadKalender(context.request, context.env, context);
  const { kalender, bundel } = actief;
  const opgegeven = url.searchParams.get('datum');
  const gesimuleerd = Boolean(opgegeven && DATUM_RE.test(opgegeven));
  const datum = gesimuleerd ? opgegeven : vandaag(kalender.tijdzone || 'Europe/Amsterdam');
  const mmdd = datum.slice(5);
  const seizoen = seizoenVoor(kalender, mmdd);

  const pad = url.pathname.replace(/^\/seizoen\/?/, '').replace(/\/+$/, '');

  if (pad === '') {
    return new Response(overzichtHtml(datum, gesimuleerd, actief), {
      status: 200,
      headers: {
        'Content-Type': 'text/html; charset=utf-8',
        'Cache-Control': 'no-store',
        'X-Robots-Tag': 'noindex',
        'X-Seizoen': seizoen,
        'X-Bron': actief.bron,
      },
    });
  }

  if (pad === 'lander' || pad === 'arrangement') {
    const l = linkVoor(kalender, pad, mmdd, bundel);
    if (!l) return nietGevonden();
    return doorsturen(l.doel, url.origin, seizoen);
  }

  const m = FOTO_RE.exec(pad);
  if (!m) return nietGevonden();
  const keuze = fotoVoor(kalender, m[1], mmdd, bundel);
  if (!keuze) return nietGevonden();

  let bestand = await haalFoto(keuze.foto, context.env, url.origin);
  let bron = keuze.foto.key ? 'r2' : 'repo';
  let periode = keuze.periode;
  if (!bestand && !keuze.uitBundel) {
    // R2-foto niet bereikbaar: de repo-foto van de meegebundelde kalender.
    const terug = fotoVoor(bundel, m[1], mmdd, bundel);
    if (terug) {
      bestand = await haalFoto(terug.foto, context.env, url.origin);
      bron = 'repo';
      periode = terug.periode;
    }
  }
  if (!bestand) return nietGevonden();

  return new Response(bestand.body, {
    status: 200,
    headers: {
      'Content-Type': 'image/jpeg',
      'Cache-Control': 'public, max-age=3600',
      'X-Seizoen': seizoen,
      'X-Periode': periode,
      'X-Bron': bron,
    },
  });
}

export async function onRequest(context) {
  const methode = context.request.method;
  if (methode !== 'GET' && methode !== 'HEAD') {
    return new Response('Methode niet toegestaan', {
      status: 405,
      headers: { Allow: 'GET, HEAD', 'Content-Type': 'text/plain; charset=utf-8', 'Cache-Control': 'no-store' },
    });
  }
  const antwoord = await behandel(context);
  if (methode === 'HEAD') return new Response(null, { status: antwoord.status, headers: antwoord.headers });
  return antwoord;
}
