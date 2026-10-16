/**
 * Cloudflare Pages Function: seizoensfoto's en -links voor de flowmails
 *
 *   GET /seizoen/ (of /seizoen)  -> overzichtspagina (HTML, noindex): welke foto nu en per seizoen, waar de links heen gaan
 *   GET /seizoen/<slot>.jpg       -> de foto van het huidige seizoen (de bytes zelf, geen redirect)
 *   GET /seizoen/lander[/]        -> 302 naar de seizoenslander van nu (/herfst, /winter, /lente, /zomer)
 *   GET /seizoen/arrangement[/]   -> 302 naar het seizoensarrangement van nu
 *   ?datum=YYYY-MM-DD             -> doet alsof het die dag is (testen)
 *   GET en HEAD (HEAD: zelfde headers, lege body; mailproxy's en linkcheckers doen eerst HEAD), rest 405.
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

const SEIZOENEN = ['herfst', 'winter', 'lente', 'zomer'];
const MIDDEN = { herfst: '10-15', winter: '01-15', lente: '04-15', zomer: '07-15' };
const MAANDEN = ['jan', 'feb', 'mrt', 'apr', 'mei', 'jun', 'jul', 'aug', 'sep', 'okt', 'nov', 'dec'];
const SLOTUITLEG = { hero: 'Hero-achtergrond bovenaan de mail', sfeer: 'Sfeerfoto in de mail' };

function esc(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function hoofdletter(s) { return s.charAt(0).toUpperCase() + s.slice(1); }

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

function periode(seizoen) {
  return KALENDER.periodes.find((p) => p.seizoen === seizoen);
}

function periodeTekst(seizoen) {
  const p = periode(seizoen);
  return `${kortMd(p.van)} t/m ${kortMd(p.tot)}`;
}

function eerstvolgendeWissels(datum, aantal) {
  const jaar = Number(datum.slice(0, 4));
  const kandidaten = [];
  for (const j of [jaar, jaar + 1]) {
    for (const p of KALENDER.periodes) kandidaten.push({ datum: `${j}-${p.van}`, seizoen: p.seizoen });
  }
  return kandidaten.filter((k) => k.datum > datum).sort((a, b) => (a.datum < b.datum ? -1 : 1)).slice(0, aantal);
}

function doelLink(doel) {
  return `<a href="${esc(doel)}">${esc(doel)}</a>`;
}

function overzichtHtml(datum, seizoen, gesimuleerd) {
  const dq = gesimuleerd ? `?datum=${datum}` : '';
  const kalenderRijen = SEIZOENEN.map((s) => {
    const p = periode(s);
    return `<tr${s === seizoen ? ' class="nu"' : ''}><td>${hoofdletter(s)}${s === seizoen ? ' <span class="label">Nu</span>' : ''}</td>`
      + `<td>${kortMd(p.van)}</td><td>${kortMd(p.tot)}</td>`
      + `<td>${doelLink(KALENDER.lander[s])}</td><td>${doelLink(KALENDER.arrangement[s])}</td></tr>`;
  }).join('\n');

  const slotBlokken = Object.entries(KALENDER.slots).map(([naam, slot]) => {
    const fotos = SEIZOENEN.map((s) => {
      const nu = s === seizoen;
      const jaar = datum.slice(0, 4);
      const src = `/seizoen/${naam}.jpg?datum=${jaar}-${MIDDEN[s]}`;
      const bestand = (slot[s] || '').split('/').pop();
      const bron = slot.bron && slot.bron[s] ? slot.bron[s] : 'onbekend';
      const lander = slot.landerfoto && slot.landerfoto[s]
        ? `<p class="let">Nog geen echt ${s}beeld: foto van de seizoenslander</p>` : '';
      return `<figure class="foto${nu ? ' nu' : ''}">`
        + (nu ? '<span class="label">Nu</span>' : '')
        + `<img src="${esc(src)}" alt="${esc(naam)} ${s}" loading="lazy">`
        + `<figcaption><strong>${hoofdletter(s)}</strong> · ${periodeTekst(s)}<br>`
        + `<code>${esc(bestand)}</code><br><span class="zacht">bron: ${esc(bron)}</span>${lander}</figcaption></figure>`;
    }).join('\n');
    const mails = (slot.mails || []).map((m) => `<li>${esc(m)}</li>`).join('');
    return `<section class="blok"><h2>${esc(naam)} <span class="zacht">· ${esc(slot.maat || '')}</span></h2>`
      + `<p class="zacht">${esc(SLOTUITLEG[naam] || '')} · <code>/seizoen/${esc(naam)}.jpg</code></p>`
      + `<p>Staat in: </p><ul class="mails">${mails}</ul>`
      + `<div class="fotos">${fotos}</div></section>`;
  }).join('\n');

  const linkBlok = ['lander', 'arrangement'].map((soort) => {
    const rijen = SEIZOENEN.map((s) => {
      const geen = soort === 'arrangement' && (s === 'winter' || s === 'lente')
        ? ' <span class="zacht">(nog geen seizoensarrangement)</span>' : '';
      return `<tr${s === seizoen ? ' class="nu"' : ''}><td>${hoofdletter(s)}${s === seizoen ? ' <span class="label">Nu</span>' : ''}</td>`
        + `<td>${doelLink(KALENDER[soort][s])}${geen}</td></tr>`;
    }).join('\n');
    return `<h3><a href="/seizoen/${soort}/${dq}">/seizoen/${soort}/</a></h3>`
      + `<div class="tabel"><table><thead><tr><th>Seizoen</th><th>Doel</th></tr></thead><tbody>${rijen}</tbody></table></div>`;
  }).join('\n');

  const wissels = eerstvolgendeWissels(datum, 2).map((w) =>
    `<li><a href="/seizoen/?datum=${w.datum}">/seizoen/?datum=${w.datum}</a> (${langeDatum(w.datum)}, begin ${w.seizoen})</li>`).join('');

  const datumRegel = gesimuleerd
    ? `Gesimuleerde datum ${langeDatum(datum)} · seizoen ${seizoen} · <a href="/seizoen/">terug naar vandaag</a>`
    : `Vandaag ${langeDatum(datum)} · seizoen ${seizoen}`;

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
<thead><tr><th>Seizoen</th><th>Van</th><th>Tot en met</th><th>Lander-doel</th><th>Arrangement-doel</th></tr></thead>
<tbody>
${kalenderRijen}
</tbody></table></div>

${slotBlokken}

<section class="blok"><h2>Links</h2>
<p class="zacht">Vaste links in de mails; de server stuurt door naar het doel van het huidige seizoen.</p>
${linkBlok}
</section>

<section class="blok"><h2>Zo ruil je een foto</h2>
<ol>
<li>Maak een nieuw jpg in exact dezelfde maat (hero 1200x520, sfeer 496x380; center-crop, kwaliteit 82, geen EXIF).</li>
<li>Vervang het bestand in <code>mail/seizoen/</code> van de repo asteria-pages, bv. <code>mail/seizoen/hero-winter.jpg</code>.</li>
<li>Commit en push naar <code>main</code>; Cloudflare Pages deployt zelf. Mailclients cachen de foto tot 1 uur. Geen mail aanraken.</li>
</ol>
</section>

<section class="blok"><h2>Zo kijk je vooruit</h2>
<p>Zet <code>?datum=JJJJ-MM-DD</code> achter de URL, bv. <a href="/seizoen/?datum=2026-12-15"><code>/seizoen/?datum=2026-12-15</code></a>. Dat werkt ook op de foto's en links.</p>
<p>De eerstvolgende seizoenswissels:</p>
<ul class="stap">${wissels}</ul>
</section>
</main>
</body>
</html>
`;
}

async function behandel(context) {
  const url = new URL(context.request.url);
  const opgegeven = url.searchParams.get('datum');
  const datum = opgegeven && DATUM_RE.test(opgegeven) ? opgegeven : vandaag(KALENDER.tijdzone);
  const seizoen = seizoenVoor(datum);

  const pad = url.pathname.replace(/^\/seizoen\/?/, '').replace(/\/+$/, '');

  if (pad === '') {
    const gesimuleerd = Boolean(opgegeven && DATUM_RE.test(opgegeven));
    return new Response(overzichtHtml(datum, seizoen, gesimuleerd), {
      status: 200,
      headers: {
        'Content-Type': 'text/html; charset=utf-8',
        'Cache-Control': 'no-store',
        'X-Robots-Tag': 'noindex',
        'X-Seizoen': seizoen,
      },
    });
  }

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
