/**
 * Cloudflare Pages Function — Nieuwsbrief-aanmelding naar Klaviyo
 * Route: POST /api/nieuwsbrief
 *
 * Body (JSON): { email, taal: "nl"|"en"|"de", bron: "popup"|"scratchcard"|"pagina",
 *                website: "" (honeypot, moet leeg blijven), ts: <ms sinds epoch, moment dat het formulier openging> }
 * Antwoord (JSON): { ok: true } of { ok: false, message, fields? }
 *
 * Wordt alleen aangeroepen als NIEUWSBRIEF_BACKEND in /nieuwsbrief.js op "klaviyo" staat.
 *
 * Secret (Cloudflare Pages > Settings > Variables and Secrets, NIET in de repo):
 *   KLAVIYO_API_KEY_ASTERIA  private API-key van het Klaviyo-account van Asteria
 *                            (scope: subscriptions:write, lists:write, profiles:write)
 *
 * Werking: een profile-subscription-bulk-create-job met één profiel, consent email
 * marketing SUBSCRIBED, op de lijst Nieuwsbrief van de taal. De lijsten staan op enkele
 * opt-in, dus er gaat geen bevestigingsmail uit; "Added to List" start de welkomstflow.
 *
 * Alleen lokaal (.dev.vars, nooit in Cloudflare zetten): NIEUWSBRIEF_DRY_RUN=1 logt de
 * Klaviyo-payload in plaats van te posten; NIEUWSBRIEF_DRY_RUN=fail doet alsof Klaviyo faalt en
 * logt de meldmail in plaats van hem te versturen.
 *
 * Lukt Klaviyo niet (key ontbreekt, storing), dan gaat er een mail naar info@asteria.nl
 * (via FormSubmit, zelfde route als /api/feedback) zodat de receptie het adres met de hand
 * kan toevoegen. Een inschrijving mag niet verdampen.
 */

const KLAVIYO_ENDPOINT = 'https://a.klaviyo.com/api/profile-subscription-bulk-create-jobs';
const KLAVIYO_REVISION = '2026-07-15';
const LIJST = { nl: 'WfwqBR', en: 'WaTagt', de: 'RjZi2f' };
const BRON = {
  popup: 'Website pop-up',
  scratchcard: 'Website pop-up (kras & win)',
  pagina: 'Website nieuwsbriefpagina',
};
const MELDING_MAIL = 'https://formsubmit.co/ajax/info@asteria.nl';
const MIN_SECONDS = 2; // sneller dan dit na openen = bot

/* ── CORS: alleen visit.asteria.nl, localhost en de eigen origin (Pages-previews) ── */
function toegestaneOrigin(request) {
  const origin = request.headers.get('Origin');
  if (!origin) return null;
  if (origin === 'https://visit.asteria.nl') return origin;
  if (/^https?:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/.test(origin)) return origin;
  try {
    if (origin === new URL(request.url).origin) return origin;
  } catch (e) { /* negeren */ }
  return null;
}

function corsHeaders(request) {
  const origin = toegestaneOrigin(request);
  if (!origin) return {};
  return {
    'Access-Control-Allow-Origin': origin,
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    Vary: 'Origin',
  };
}

function json(request, body, status) {
  return new Response(JSON.stringify(body), {
    status: status || 200,
    headers: {
      'Content-Type': 'application/json; charset=utf-8',
      'Cache-Control': 'no-store',
      ...corsHeaders(request),
    },
  });
}

/* ── Helpers (zelfde regels als de Parkhotel-Worker) ── */
function clean(v, max) {
  if (v === null || v === undefined) return '';
  let s = String(v).replace(/[\u0000-\u001F\u007F]/g, ' ').trim();
  if (typeof max === 'number' && s.length > max) s = s.slice(0, max);
  return s;
}

function isEmail(v) {
  return /^[^\s@,;:<>"]+@[^\s@,;:<>"]+\.[A-Za-z]{2,}$/.test(v);
}

/** Honeypot + tijdcheck. true = als spam behandelen (stil laten mislukken). */
function isSpam(honeypot, started) {
  if (clean(honeypot) !== '') return true;
  const ms = parseInt(started, 10);
  if (!ms || isNaN(ms) || ms <= 0) return false;
  const elapsed = (Date.now() - ms) / 1000;
  return elapsed >= 0 && elapsed < MIN_SECONDS;
}

async function stuurNaarKlaviyo(env, taal, bron, email) {
  if (!env.KLAVIYO_API_KEY_ASTERIA && !env.NIEUWSBRIEF_DRY_RUN) throw new Error('KLAVIYO_API_KEY_ASTERIA ontbreekt');
  const body = {
    data: {
      type: 'profile-subscription-bulk-create-job',
      attributes: {
        custom_source: BRON[bron],
        profiles: {
          data: [
            {
              type: 'profile',
              attributes: {
                email: email,
                subscriptions: { email: { marketing: { consent: 'SUBSCRIBED' } } },
              },
            },
          ],
        },
        historical_import: false,
      },
      relationships: { list: { data: { type: 'list', id: LIJST[taal] } } },
    },
  };
  if (env.NIEUWSBRIEF_DRY_RUN === '1') {
    console.log('[nieuwsbrief] DRY RUN, payload: ' + JSON.stringify(body));
    return;
  }
  if (env.NIEUWSBRIEF_DRY_RUN === 'fail') throw new Error('DRY RUN: gesimuleerde Klaviyo-fout');
  const res = await fetch(KLAVIYO_ENDPOINT, {
    method: 'POST',
    headers: {
      Authorization: 'Klaviyo-API-Key ' + env.KLAVIYO_API_KEY_ASTERIA,
      revision: KLAVIYO_REVISION,
      Accept: 'application/vnd.api+json',
      'Content-Type': 'application/vnd.api+json',
    },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const tekst = await res.text().catch(() => '');
    throw new Error('Klaviyo gaf ' + res.status + ': ' + tekst.slice(0, 200));
  }
}

async function meldHandmatig(env, taal, bron, email) {
  if (env.NIEUWSBRIEF_DRY_RUN) {
    console.log('[nieuwsbrief] DRY RUN, meldmail naar info@asteria.nl: ' + email + ' (' + taal + ', ' + bron + ')');
    return true;
  }
  try {
    const res = await fetch(MELDING_MAIL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({
        _subject: 'Nieuwsbrief-aanmelding visit.asteria.nl (handmatig toevoegen)',
        _template: 'box',
        _captcha: 'false',
        Melding: 'De aanmelding kon niet naar Klaviyo worden doorgezet. Voeg dit adres met de hand toe aan de lijst Nieuwsbrief ' + taal.toUpperCase() + '.',
        Email: email,
        Taal: taal,
        Bron: BRON[bron],
      }),
    });
    return res.ok;
  } catch (e) {
    console.error('[nieuwsbrief] meldmail faalde: ' + e);
    return false;
  }
}

export async function onRequestOptions({ request }) {
  return new Response(null, { status: 204, headers: corsHeaders(request) });
}

export async function onRequestPost({ request, env }) {
  // Vreemde origin (andere site die hierheen post) weigeren; zonder Origin-header laten we door
  if (request.headers.get('Origin') && !toegestaneOrigin(request)) {
    return json(request, { ok: false, message: 'Origin niet toegestaan.' }, 403);
  }

  let body = {};
  try {
    body = (await request.json()) || {};
  } catch (e) {
    body = {};
  }
  if (typeof body !== 'object' || body === null) body = {};

  if (isSpam(body.website, body.ts)) {
    console.log('[nieuwsbrief] spam geweigerd van ' + (request.headers.get('cf-connecting-ip') || '?'));
    return json(request, { ok: true }, 200);
  }

  const email = clean(body.email, 200);
  if (email === '' || !isEmail(email)) {
    return json(request, { ok: false, message: 'Ongeldig e-mailadres.', fields: ['email'] }, 400);
  }

  const taalIn = clean(body.taal, 2).toLowerCase();
  const taal = Object.prototype.hasOwnProperty.call(LIJST, taalIn) ? taalIn : 'nl';

  const bron = clean(body.bron, 20).toLowerCase();
  if (!Object.prototype.hasOwnProperty.call(BRON, bron)) {
    return json(request, { ok: false, message: 'Onbekende bron.', fields: ['bron'] }, 400);
  }

  try {
    await stuurNaarKlaviyo(env, taal, bron, email);
    return json(request, { ok: true }, 200);
  } catch (err) {
    console.error('[nieuwsbrief] Klaviyo faalde (' + taal + ', ' + bron + '): ' + err);
  }

  if (await meldHandmatig(env, taal, bron, email)) {
    return json(request, { ok: true }, 200);
  }
  return json(request, { ok: false, message: 'Het inschrijven lukte even niet. Probeer het zo nog eens.' }, 502);
}

export async function onRequestGet({ request }) {
  return json(request, { ok: false, message: 'Alleen POST.' }, 405);
}
