/**
 * Hotel Asteria · /extras (pre-arrival upsell), Cloudflare Pages Function.
 * Port van src/extras.js uit parkhotel-site (v2-lander, 13 okt 2026), zonder het legacy-pad: alles is client extras-v2
 * (een ontbrekende `client` telt ook als v2).
 *
 * De gast opent /extras?r=<Mews-reserverings-GUID>&n=<nummer>&a=<aankomst>&d=<vertrek>&p=<personen>&v=<voornaam>
 * (+ optioneel &e=<e-mail>&k=<aanbevolen product-key>&t=<kamertype>) uit de pre-arrival-mail. Alleen `r` is verplicht;
 * de GUID is zelf de sleutel.
 *
 *   GET  /api/extras/sessie  · producten (live uit de Mews Distributor-configuratie) met prijs voor dit verblijf
 *   POST /api/extras/bestel  · bestelling: per productregel één POST naar de Zapier Catch Hook
 *                              (Zap "Extras-bestelling → Mews (Asteria)": Add Reservation Product + Create Task),
 *                              daarna receptiemail (MAIL_INFO) en bevestigingsmail aan de gast.
 *
 * Typen: eenmalig · personen (count = personen of fietsen) · perdag (diner, wellness: aantal × gekozen dagen; het veld
 * heet `avonden`) · pernacht (ontbijt: personen × alle nachten). Mews vermenigvuldigt het meegestuurde Count zelf
 * (PerPerson = × personen, PerPersonPerTimeUnit = × personen × nachten; bewezen bij Parkhotel 13 okt 2026). Asteria heeft
 * nog geen aparte Once-bestelproducten (`bestel_id`), dus wijkt wat Mews boekt soms af van wat de gast koos; dan krijgt
 * de receptietaak een blok "!! CORRIGEER IN MEWS" en staat die regel vooraan.
 *
 * Env (Pages-project): ZAPIER_EXTRAS_HOOK (Catch Hook-URL; zonder = fallback naar de receptiemail met [HANDMATIG]),
 *   EXTRAS_SHARED_SECRET (gaat mee in de payload, Filter-stap in de Zap), RESEND_API_KEY (optioneel; zonder gaat de
 *   receptiemail via FormSubmit en is er geen gastmail), MAIL_FROM, MAIL_INFO (standaard info@asteria.nl).
 * Alleen voor tests (.dev.vars of preview): EXTRAS_DRY_RUN=1 (hook overslaan, payload loggen), MAIL_DRY_RUN=1 (geen
 *   echte mail), MAIL_OVERRIDE_TO, MAIL_SUBJECT_PREFIX. Optionele ratelimit-binding FORM_LIMIT (zonder = alles door).
 */

const MEWS_DISTRIBUTOR = "https://api.mews.com/api/distributor/v1";
const MEWS_CLIENT = "Asteria Booking 1.0.0";
const CONFIGURATION_ID = "6dc9094c-76e3-4fd8-83a7-af1d00ffc556";
const SERVICE_ID = "755424cc-3077-4320-b069-af1d00ffbe47"; // logies-service Hotel Asteria (Mews)
const CATALOGUS_TTL_MS = 10 * 60 * 1000;
const TELEFOON = "0478 511 466";
const MAIL_STANDAARD = "info@asteria.nl";
const PLAFOND_CENTS = 250000; // € 2.500 per bestelling
const TAAKNAAM_MAX = 120;
const CLIENT_V2 = "extras-v2";
const RESEND_ENDPOINT = "https://api.resend.com/emails";
const FORMSUBMIT = "https://formsubmit.co/ajax/";
const MIN_SECONDS = 3; // sneller ingevuld dan dit = bot

/** Welke Mews-producten we aanbieden, in deze volgorde (= volgorde in de Mews-configuratie), met eigen korte teksten.
 *  Prijs, foto en chargingmode komen live uit Mews (op `id`); de Mews-naam gaat wél mee naar de receptietaak.
 *  key     : korte naam (maillink `k=`, payload `recommended_key`)
 *  type    : eenmalig · personen (count = personen of fietsen) · perdag (count = personen, plus dagen uit nights_list)
 *            · pernacht (count = personen, alle nachten)
 *  dagLabel: alleen perdag, "avond" of "dag"
 *  eenheid : "persoon" of "fiets" (wat count telt); leeg bij eenmalig
 *  groep   : aankomst · verblijf · vertrek
 *  max     : hoogste count die de pagina mag sturen
 *  foto    : eigen kaartfoto (gaat vóór de Mews-foto)
 *  tijd    : tijdstip wordt met de gast afgestemd (noot op de kaart)
 *  Geen bestel_id: de Once-bestelproducten bestaan bij Asteria nog niet. */
const AANBOD = [
  { id: "75fce6f2-6339-41c2-9e48-b3b60095d412", key: "diner", type: "perdag", dagLabel: "avond", eenheid: "persoon", max: 8, foto: "/fotos/extras-diner.webp", naam: "Driegangendiner in ons restaurant", tekst: "Een driegangendiner in ons restaurant, per persoon per avond. Wij reserveren een tafel voor je.", groep: "verblijf" },
  { id: "a80b1abc-7079-44f7-be63-af2e00bb4d9f", key: "ontbijt", type: "pernacht", eenheid: "persoon", max: 8, foto: "/fotos/extras-ontbijt.webp", naam: "Ontbijtbuffet", tekst: "Elke ochtend van je verblijf het uitgebreide ontbijtbuffet in ons restaurant. Alleen nodig als je kamer zonder ontbijt is geboekt.", groep: "verblijf" },
  { id: "bd06307a-e86f-434c-a799-b43400d93806", key: "wellness", type: "perdag", dagLabel: "dag", eenheid: "persoon", max: 8, tijd: true, foto: "/fotos/extras-wellness.webp", naam: "Toegang tot de Top Floor wellness", tekst: "Een dag sauna's, stoomcabine, belevenisdouches en relaxruimte, per persoon per dag. De receptie reserveert je plek.", groep: "verblijf" },
  { id: "a3a062b9-3854-449c-b74f-b05300c1a15e", key: "fiets", type: "personen", eenheid: "fiets", max: 8, foto: "/fotos/extras-fiets.webp", naam: "Fietshuur", tekst: "Een stadsfiets, klaar bij de receptie. Laat in de opmerking weten op welke dag je wilt fietsen.", groep: "verblijf" },
  { id: "527b5916-5451-4db7-9839-b0b2008e6dd3", key: "ebike", type: "personen", eenheid: "fiets", max: 8, foto: "/fotos/extras-ebike.webp", naam: "Elektrische fietshuur", tekst: "Een elektrische fiets, opgeladen en klaar bij de receptie. Laat in de opmerking weten op welke dag.", groep: "verblijf" },
  { id: "a2871461-233c-4aac-a2b9-b43400854b25", key: "kruidenolie", type: "eenmalig", max: 3, foto: "/fotos/extras-kruidenolie.webp", naam: "Kruidenolie voor in bad", tekst: "Een flesje kruidenolie om je wellnessmoment in bad compleet te maken.", groep: "verblijf" },
  { id: "8a5468e9-1aa8-4a2f-818a-af810098ec66", key: "badjas", type: "personen", eenheid: "persoon", max: 8, foto: "/fotos/extras-badjas.webp", naam: "Badjas en slippers op je kamer", tekst: "Een zachte badjas met slippers, voor ieder een eigen set. Je loopt zo naar de Top Floor.", groep: "aankomst" },
  { id: "c558563b-c217-4b66-ac99-b43300d08641", key: "handdoek", type: "personen", eenheid: "persoon", max: 8, foto: "/fotos/extras-handdoek.webp", naam: "Handdoekpakket voor de wellness", tekst: "Een grote en een kleine handdoek voor in de wellness, per persoon, bij aankomst op je kamer.", groep: "aankomst" },
  { id: "325c73ef-09f9-4596-81d9-b0970067bd55", key: "early", type: "eenmalig", max: 1, foto: "/fotos/extras-early.webp", naam: "Early check-in", tekst: "Je kamer is al vanaf 12.00 uur beschikbaar in plaats van 15.00 uur (op basis van beschikbaarheid).", groep: "aankomst" },
  { id: "196e6fe4-f15a-4384-a7e0-b097006801ee", key: "late", type: "eenmalig", max: 1, foto: "/fotos/extras-late.webp", naam: "Late check-out", tekst: "Uitchecken tot 14.00 uur in plaats van 11.00 uur, zodat je de ochtend rustig kunt beginnen.", groep: "vertrek" },
];

/** key → AANBOD-item */
const KEYS = {};
for (const a of AANBOD) KEYS[a.key] = a;

const GUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/;
const MAX_REGELS = 12;
const TALEN = ["nl", "en", "de"];

let catalogus = { t: 0, perId: null };

/* ────────────────────────────────────────────── entree (Pages Function) */

export async function onRequest(context) {
  const { request, env, params } = context;
  const pad = Array.isArray(params && params.path) ? params.path.join("/") : String((params && params.path) || "");
  const route = "/api/extras/" + pad.replace(/\/+$/, "");
  if (route !== "/api/extras/sessie" && route !== "/api/extras/bestel") {
    return H.json({ ok: false, message: "Onbekend eindpunt." }, 404);
  }
  const toegestaan = route === "/api/extras/sessie" ? "GET, OPTIONS" : "POST, OPTIONS";
  if (request.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: { Allow: toegestaan, "Cache-Control": "no-store" } });
  }
  if (route === "/api/extras/sessie") {
    if (request.method !== "GET") return H.json({ ok: false, message: "Alleen GET." }, 405, { Allow: toegestaan });
    return handleSessie(request, env || {}, H);
  }
  if (request.method !== "POST") return H.json({ ok: false, message: "Alleen POST." }, 405, { Allow: toegestaan });
  return handleBestel(request, env || {}, H);
}

/* ────────────────────────────────────────────── helpers (inline, gelijk aan parkhotel-site src/index.js) */

function json(body, status, extra) {
  const headers = {
    "Content-Type": "application/json; charset=utf-8",
    "Cache-Control": "no-store",
  };
  if (extra) for (const k in extra) headers[k] = extra[k];
  return new Response(JSON.stringify(body), { status: status || 200, headers });
}

/** Optionele Cloudflare Rate Limiting binding FORM_LIMIT; zonder binding gaat alles door. */
async function rateOk(env, request, route) {
  if (!env || !env.FORM_LIMIT || typeof env.FORM_LIMIT.limit !== "function") return true;
  const ip = request.headers.get("cf-connecting-ip") || "0.0.0.0";
  try {
    const { success } = await env.FORM_LIMIT.limit({ key: ip + "|" + route });
    return success !== false;
  } catch (e) {
    console.log("[api] rate-limit binding faalde, door laten gaan: " + e);
    return true;
  }
}

/** Trimmen, controltekens weg, afkappen. */
function clean(v, max) {
  if (v === null || v === undefined) return "";
  let s = String(v).replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/g, "");
  s = s.replace(/\r\n?/g, "\n").trim();
  if (typeof max === "number" && s.length > max) s = s.slice(0, max);
  return s;
}

/** Eén regel: nieuwe regels eruit (voor kopvelden en onderwerpen). */
function line(v, max) {
  return clean(v, max).replace(/\s*\n\s*/g, " ");
}

function isEmail(v) {
  return /^[^\s@,;:<>"]+@[^\s@,;:<>"]+\.[A-Za-z]{2,}$/.test(v);
}

/** Honeypot + tijdcheck. true = als spam behandelen (stil laten mislukken). */
function isSpam(honeypot, started) {
  if (clean(honeypot) !== "") return true;
  const ms = parseInt(started, 10);
  if (!ms || isNaN(ms) || ms <= 0) return false;
  const elapsed = (Date.now() - ms) / 1000;
  return elapsed >= 0 && elapsed < MIN_SECONDS;
}

function mailDry(env) {
  return env.MAIL_DRY_RUN === "1" || env.MAIL_DRY_RUN === "true";
}

/** Mail via Resend (platte tekst). false zonder RESEND_API_KEY of bij een fout. */
async function sendMail(env, opts) {
  if (!env.RESEND_API_KEY) {
    console.log("[api] geen RESEND_API_KEY, mail niet verstuurd: " + opts.subject);
    return false;
  }
  const to = env.MAIL_OVERRIDE_TO ? [env.MAIL_OVERRIDE_TO] : [].concat(opts.to);
  if (mailDry(env)) {
    console.log("[api] MAIL_DRY_RUN (resend), niet verstuurd. to=" + to.join(",") + " subject=" + opts.subject);
    return true;
  }
  const body = {
    from: env.MAIL_FROM || "Hotel Asteria <" + MAIL_STANDAARD + ">",
    to: to,
    subject: (env.MAIL_SUBJECT_PREFIX || "") + opts.subject,
    text: opts.text,
  };
  if (opts.replyTo) body.reply_to = opts.replyTo;
  try {
    const res = await fetch(RESEND_ENDPOINT, {
      method: "POST",
      headers: { Authorization: "Bearer " + env.RESEND_API_KEY, "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) {
      const txt = await res.text();
      console.log("[api] Resend HTTP " + res.status + ": " + txt.slice(0, 500));
      return false;
    }
    return true;
  } catch (e) {
    console.log("[api] Resend onbereikbaar: " + e);
    return false;
  }
}

/** Receptiemail zonder Resend: via FormSubmit (zoals functions/api/feedback.js), zodat de bestelling altijd binnenkomt. */
async function sendFormSubmit(env, opts) {
  const to = env.MAIL_OVERRIDE_TO || [].concat(opts.to)[0] || MAIL_STANDAARD;
  if (mailDry(env)) {
    console.log("[api] MAIL_DRY_RUN (formsubmit), niet verstuurd. to=" + to + " subject=" + opts.subject);
    return true;
  }
  const body = {
    _subject: (env.MAIL_SUBJECT_PREFIX || "") + opts.subject,
    bericht: opts.text,
    _template: "box",
    _captcha: "false",
  };
  if (opts.replyTo) body._replyto = opts.replyTo;
  try {
    const res = await fetch(FORMSUBMIT + encodeURIComponent(to), {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(8000),
    });
    const txt = await res.text();
    let ok = res.ok;
    try {
      const j = JSON.parse(txt);
      if (j && (j.success === false || j.success === "false")) ok = false;
    } catch (e) { /* geen JSON: status telt */ }
    if (!ok) console.log("[api] FormSubmit HTTP " + res.status + ": " + txt.slice(0, 300));
    return ok;
  } catch (e) {
    console.log("[api] FormSubmit onbereikbaar: " + e);
    return false;
  }
}

/** Receptiemail: Resend als die er is, anders FormSubmit. */
async function mailReceptie(env, opts) {
  if (env.RESEND_API_KEY) return sendMail(env, opts);
  return sendFormSubmit(env, opts);
}

const H = { json, rateOk, clean, line, isEmail, isSpam, sendMail };

/* ────────────────────────────────────────────── catalogus (Mews Distributor) */

/** Alle Mews-producten met een EUR-prijs uit de Distributor-configuratie, per (kleine letters) id. Gecachet. */
async function haalMews() {
  if (catalogus.perId && Date.now() - catalogus.t < CATALOGUS_TTL_MS) return catalogus.perId;
  const res = await fetch(MEWS_DISTRIBUTOR + "/configuration/get", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ Client: MEWS_CLIENT, Ids: [CONFIGURATION_ID] }),
    signal: AbortSignal.timeout(8000),
  });
  if (!res.ok) throw new Error("mews_configuration_http_" + res.status);
  const data = await res.json();
  const prods = (data && data.Configurations && data.Configurations[0] && data.Configurations[0].Enterprise &&
    data.Configurations[0].Enterprise.Products) || [];
  const perId = {};
  for (const p of prods) {
    if (!p || !p.Id) continue;
    const eur = p.Prices && typeof p.Prices.EUR === "number" ? p.Prices.EUR : null;
    if (eur === null) continue;
    perId[String(p.Id).toLowerCase()] = {
      name: tekst(p.Name),
      description: tekst(p.Description),
      price_cents: Math.round(eur * 100),
      mews_charging: String(p.ChargingMode || "Once"),
      image_url: p.ImageId ? "https://www.mews.li/Media/Image/" + p.ImageId + "?Mode=Fit&Width=640" : "",
    };
  }
  if (!Object.keys(perId).length) throw new Error("mews_configuration_leeg");
  catalogus = { t: Date.now(), perId };
  return perId;
}

function isDry(env) {
  return !!env && (env.EXTRAS_DRY_RUN === "1" || env.EXTRAS_DRY_RUN === "true");
}

/** Productlijst: AANBOD in volgorde, met Mews-gegevens. Een item zonder Mews-product met EUR-prijs valt weg. */
async function haalCatalogus() {
  const mews = await haalMews();
  const items = [];
  for (const a of AANBOD) {
    const m = mews[a.id];
    if (!m) continue;
    items.push(catalogusItem(a, m));
  }
  if (!items.length) throw new Error("mews_configuration_leeg");
  return items;
}

/** Eén catalogus-item uit een AANBOD-regel en de Mews-gegevens (ook gebruikt door de unit-test). */
function catalogusItem(a, m) {
  return {
    id: a.id,
    name: a.naam || m.name,
    description: a.tekst !== undefined ? a.tekst : m.description,
    price_cents: m.price_cents,
    mews_charging: m.mews_charging,
    mews_name: m.name,
    image_url: a.foto ? a.foto : m.image_url, // eigen foto (pad op deze site, werkt ook op previews) gaat vóór Mews
    key: a.key,
    type: a.type,
    dagLabel: a.type === "perdag" ? a.dagLabel || "avond" : "",
    eenheid: a.eenheid || "",
    groep: a.groep,
    max: a.max,
    tijd_overleg: !!a.tijd,
    bestel_id: "",
    bestel_charging: m.mews_charging,
  };
}

function tekst(v) {
  if (!v) return "";
  if (typeof v === "string") return v;
  return v["nl-NL"] || v["en-US"] || v["en-GB"] || v["de-DE"] || Object.values(v)[0] || "";
}

/** Wat Mews boekt bij Add Reservation Product met `count`: Once = count · PerPerson = count × personen ·
 *  PerTimeUnit = count × nachten · PerPersonPerTimeUnit = count × personen × nachten. */
function mewsCents(prijsCents, mewsCharging, count, nachten, adults) {
  const perPers = mewsCharging === "PerPerson" || mewsCharging === "PerPersonPerTimeUnit";
  return prijsCents * count * (perPers ? adults : 1) * (perNacht(mewsCharging) ? nachten : 1);
}

/** Count dat Mews zo dicht mogelijk bij `units` (wat de gast betaalt, in stuks van de prijs) laat uitkomen. */
function countVoorMews(mewsCharging, units, nachten, adults) {
  if (mewsCharging === "PerPerson") return Math.max(1, Math.ceil(units / adults));
  if (mewsCharging === "PerPersonPerTimeUnit") return Math.max(1, Math.round(units / (adults * nachten)));
  if (mewsCharging === "PerTimeUnit") return Math.max(1, Math.round(units / nachten));
  return units;
}

function perNacht(mewsCharging) {
  return mewsCharging === "PerTimeUnit" || mewsCharging === "PerPersonPerTimeUnit";
}

/* ────────────────────────────────────────────── datums (vaste tabellen, UTC; geen Intl) */

const DAGEN = {
  nl: ["zo", "ma", "di", "wo", "do", "vr", "za"],
  en: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
  de: ["So", "Mo", "Di", "Mi", "Do", "Fr", "Sa"],
};
const MAANDEN = {
  nl: ["jan", "feb", "mrt", "apr", "mei", "jun", "jul", "aug", "sep", "okt", "nov", "dec"],
  en: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
  de: ["Jan.", "Feb.", "März", "Apr.", "Mai", "Juni", "Juli", "Aug.", "Sep.", "Okt.", "Nov.", "Dez."],
};

function utcDatum(iso) {
  if (typeof iso !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(iso)) return null;
  const [j, m, d] = iso.split("-").map(Number);
  const dt = new Date(Date.UTC(j, m - 1, d));
  if (dt.getUTCFullYear() !== j || dt.getUTCMonth() !== m - 1 || dt.getUTCDate() !== d) return null;
  return dt;
}

function isoPlus(iso, dagen) {
  const dt = utcDatum(iso);
  if (!dt) return "";
  return new Date(dt.getTime() + dagen * 86400000).toISOString().slice(0, 10);
}

/** "di 20 okt 2026" / kort "di 20 okt" (nl); "Tue 20 Oct 2026" (en); "Di 20. Okt. 2026" (de). */
function datumLabel(iso, taal, kort) {
  const dt = utcDatum(iso);
  if (!dt) return "";
  const t = TALEN.indexOf(taal) >= 0 ? taal : "nl";
  const dag = DAGEN[t][dt.getUTCDay()];
  const maand = MAANDEN[t][dt.getUTCMonth()];
  const nr = dt.getUTCDate();
  const jaar = kort ? "" : " " + dt.getUTCFullYear();
  if (t === "de") return dag + " " + nr + ". " + maand + jaar;
  return dag + " " + nr + " " + maand + jaar;
}

/* ────────────────────────────────────────────── verblijf uit de link */

function leesVerblijf(bron, h) {
  const r = h.clean(bron.r, 40).toLowerCase();
  if (!GUID_RE.test(r)) return null;
  const lang = TALEN.indexOf(h.clean(bron.taal, 2).toLowerCase()) >= 0 ? h.clean(bron.taal, 2).toLowerCase() : "nl";
  const a = h.clean(bron.a, 10), d = h.clean(bron.d, 10);
  let aankomst = utcDatum(a) ? a : "";
  let vertrek = utcDatum(d) ? d : "";
  let personen = parseInt(bron.p, 10);
  if (!personen || isNaN(personen) || personen < 1) personen = 2;
  if (personen > 8) personen = 8;
  let nachten = 1;
  if (aankomst && vertrek) {
    const n = Math.round((utcDatum(vertrek) - utcDatum(aankomst)) / 86400000);
    if (n >= 1 && n <= 30) nachten = n;
    else { aankomst = ""; vertrek = ""; } // vertrek ≤ aankomst (of onzinnig lang): datums niet gebruiken
  }
  const nightsList = [];
  if (aankomst && vertrek) {
    for (let i = 0; i < nachten; i++) {
      const iso = isoPlus(aankomst, i);
      nightsList.push({ date: iso, label: datumLabel(iso, lang, false), short: datumLabel(iso, lang, true) });
    }
  }
  const k = h.clean(bron.k, 20).toLowerCase();
  return {
    id: r,
    number: h.line(bron.n, 20).replace(/[^0-9A-Za-z-]/g, ""),
    arrival: aankomst,
    departure: vertrek,
    adults: personen,
    nights: nachten,
    first_name: h.line(bron.v, 60),
    lang: lang,
    arrival_label: datumLabel(aankomst, lang, false),
    departure_label: datumLabel(vertrek, lang, false),
    nights_list: nightsList,
    recommended: KEYS[k] ? k : "",
  };
}

function euro(c) {
  return "€ " + (c / 100).toFixed(2).replace(".", ",");
}

/** "a", "a en b", "a, b en c" */
function opsomming(lijst, en) {
  if (lijst.length <= 1) return lijst.join("");
  return lijst.slice(0, -1).join(", ") + " " + (en || "en") + " " + lijst[lijst.length - 1];
}

/* ────────────────────────────────────────────── GET /api/extras/sessie */

async function handleSessie(request, env, h) {
  const q = new URL(request.url).searchParams;
  const bron = {};
  for (const k of ["r", "n", "a", "d", "p", "v", "k", "taal"]) bron[k] = q.get(k);
  const verblijf = leesVerblijf(bron, h);
  if (!verblijf) return h.json({ ok: false, message: "Deze link is niet geldig." }, 400);
  let items;
  try {
    items = await haalCatalogus();
  } catch (e) {
    console.log("[api] extras: catalogus mislukt: " + e);
    return h.json({ ok: false, message: "De extra's konden nu niet worden opgehaald." }, 503);
  }
  const products = items.map((p) => Object.assign({}, p, {
    default_count: standaardCount(p, verblijf),
    adults: verblijf.adults,
    nights: verblijf.nights,
  }));
  return h.json({ ok: true, reservation: verblijf, recommended: verblijf.recommended, products: products }, 200,
    { "Cache-Control": "private, max-age=60" });
}

/** Beginstand van de stepper: eenmalig 1, anders het aantal personen (begrensd op max). */
function standaardCount(item, verblijf) {
  if (item.type === "eenmalig") return 1;
  return Math.min(verblijf.adults, item.max);
}

/* ────────────────────────────────────────────── regels: lezen en berekenen */

/** Valideert één binnenkomende regel tegen het product en het verblijf.
 *  Geeft {count, avonden, tijd} of {fout: {ok:false, message, fields, product_id}}. */
function leesRegel(rg, item, verblijf) {
  const fout = (message, veld) => ({ fout: { ok: false, message: message, fields: [veld], product_id: item.id } });

  let count;
  const ruw = rg ? rg.count : undefined;
  if (ruw === undefined || ruw === null || ruw === "") {
    count = standaardCount(item, verblijf);
  } else {
    const n = Number(ruw);
    if (!Number.isInteger(n) || n < 1 || n > item.max) {
      return fout("Kies voor " + item.name + " een aantal van 1 tot en met " + item.max + ".", "count");
    }
    count = n;
  }

  let avonden = [];
  const ruwAvonden = rg ? rg.avonden : undefined;
  if (ruwAvonden !== undefined && ruwAvonden !== null && !(Array.isArray(ruwAvonden) && ruwAvonden.length === 0)) {
    const woord = item.dagLabel === "dag" ? "dagen" : "avonden";
    if (item.type !== "perdag") return fout("Dagen of avonden kun je alleen kiezen bij een extra per dag.", "avonden");
    if (!Array.isArray(ruwAvonden)) return fout("Kies de " + woord + " opnieuw.", "avonden");
    const geldig = {};
    for (const n of verblijf.nights_list) geldig[n.date] = true;
    const gezien = {};
    for (const a of ruwAvonden) {
      const iso = typeof a === "string" ? a.trim() : "";
      if (!geldig[iso]) return fout("Een van de gekozen " + woord + " valt buiten je verblijf.", "avonden");
      gezien[iso] = true;
    }
    avonden = Object.keys(gezien).sort();
  }
  if (item.type === "perdag" && !avonden.length) avonden = verblijf.nights_list.map((n) => n.date);

  // Voorkeurstijd bestaat alleen bij het diner; bij andere producten wordt hij genegeerd.
  let tijd = "";
  const ruwTijd = rg && rg.tijd !== undefined && rg.tijd !== null ? String(rg.tijd).trim() : "";
  if (ruwTijd && item.key === "diner") {
    const m = /^(\d{1,2})[.:](\d{2})$/.exec(ruwTijd);
    if (!m || Number(m[1]) > 23 || Number(m[2]) > 59) return fout("Kies een geldige voorkeurstijd.", "tijd");
    tijd = String(Number(m[1])).padStart(2, "0") + ":" + m[2];
  }
  return { count: count, avonden: avonden, tijd: tijd };
}

/** Rekent één regel uit: wat de gast betaalt (total_cents), wat er naar Mews gaat (count, mews_cents),
 *  en of die twee afwijken (afwijking ≠ "").
 *  billing: "exact" (Once, eenmalig/personen) · "A" (perdag/pernacht op een Once-product) · "B" (Mews vermenigvuldigt
 *  zelf × personen en/of × nachten; count = dichtstbijzijnde). */
function berekenRegel(item, keuze, verblijf) {
  const prijs = item.price_cents;
  const nachten = verblijf.nights;
  const labelVan = {};
  for (const n of verblijf.nights_list) labelVan[n.date] = n;
  const uit = {
    product: item,
    key: item.key,
    type: item.type,
    keuze_count: keuze.count,
    count: 0,
    personen: null,
    units: 0,
    avonden: [],
    avond_labels: [],
    avond_kort: [],
    tijd: (keuze && keuze.tijd) || "",
    nachten: nachten,
    billing: "exact",
    total_cents: 0,
    mews_cents: 0,
    afwijking: "",
  };

  const mc = mcVan(item);
  const adults = verblijf.adults;
  const once = mc === "Once";
  if (item.type === "eenmalig") {
    uit.units = keuze.count;
  } else if (item.type === "personen") {
    uit.personen = keuze.count;
    uit.units = keuze.count;
  } else if (item.type === "pernacht") {
    // ontbijt: geldt voor alle nachten
    uit.personen = keuze.count;
    uit.units = keuze.count * nachten;
    if (once) uit.billing = "A";
  } else {
    // perdag (diner, wellness): aantal × gekozen dagen
    const avonden = keuze.avonden || [];
    uit.personen = keuze.count;
    uit.avonden = avonden.slice();
    uit.units = keuze.count * (avonden.length || nachten);
    if (once) uit.billing = "A";
  }
  uit.total_cents = prijs * uit.units;
  // Once: count = stuks, exact. Anders vermenigvuldigt Mews zelf; kies het Count dat er het dichtst bij komt.
  uit.count = once ? uit.units : countVoorMews(mc, uit.units, nachten, adults);
  if (!once) uit.billing = "B";
  uit.mews_cents = mewsCents(prijs, mc, uit.count, nachten, adults);

  uit.avond_labels = uit.avonden.map((d) => (labelVan[d] ? labelVan[d].label : d));
  uit.avond_kort = uit.avonden.map((d) => (labelVan[d] ? labelVan[d].short : d));

  if (uit.mews_cents !== uit.total_cents) {
    let mewsDeel = uit.count + "× " + euro(prijs);
    if (mc === "PerPerson" || mc === "PerPersonPerTimeUnit") mewsDeel += " × " + adults + " pers.";
    if (perNacht(mc)) mewsDeel += " × " + nachten + (nachten === 1 ? " nacht" : " nachten");
    let gastDeel;
    if (item.type === "perdag") {
      gastDeel = aantalTekst(uit.personen, item.eenheid, true) + " op " +
        (uit.avond_labels.length ? opsomming(uit.avond_labels) : nachten + (item.dagLabel === "dag" ? " dag(en)" : " avond(en)"));
    } else if (item.type === "pernacht") {
      gastDeel = uit.personen + " pers. × " + nachten + (nachten === 1 ? " nacht" : " nachten");
    } else if (item.type === "personen") {
      gastDeel = aantalTekst(uit.personen, item.eenheid, true) + ", eenmalig";
    } else {
      gastDeel = uit.keuze_count + "×";
    }
    uit.afwijking = item.name + ": Mews boekt " + mewsDeel + " = " + euro(uit.mews_cents) +
      "; de gast koos " + gastDeel + " = " + euro(uit.total_cents) +
      ". Zet het product in Mews op " + euro(uit.total_cents) + ".";
  }
  return uit;
}

/** Effectieve chargingmode bij het bestellen: Once bij een bestel_id, anders die van het catalogusproduct. */
function mcVan(item) {
  return item.bestel_charging || item.mews_charging || "Once";
}

/* ────────────────────────────────────────────── receptietaak en gastmail */

/** "2 fietsen", "1 fiets", "2 personen" of kort "2 pers." */
function aantalTekst(n, eenheid, kort) {
  if (eenheid === "fiets") return n + (n === 1 ? " fiets" : " fietsen");
  if (kort) return n + " pers.";
  return n + (n === 1 ? " persoon" : " personen");
}

/** Eén regel voor taak en receptiemail.
 *  perdag  : "Toegang tot de Top Floor wellness · 2 personen, di 20 okt en wo 21 okt · € 50,00"
 *  pernacht: "Ontbijtbuffet · 2 personen, 2 nachten · € 70,00"
 *  personen: "Fietshuur · 2 fietsen · € 19,00" / "Badjas en slippers op je kamer · 2 pers. · € 14,00" */
function regelSamenvatting(r) {
  if (r.type === "perdag" || r.type === "pernacht") {
    const aantal = r.personen !== null ? r.personen : r.keuze_count;
    const det = [aantalTekst(aantal, r.product.eenheid)];
    if (r.type === "perdag" && r.avond_kort.length) det.push(opsomming(r.avond_kort));
    if (r.type === "pernacht") det.push(r.nachten + (r.nachten === 1 ? " nacht" : " nachten"));
    if (r.tijd) det.push("voorkeurstijd " + r.tijd);
    return r.product.name + " · " + det.join(", ") + " · " + euro(r.total_cents);
  }
  const perPers = r.type !== "eenmalig" && r.personen !== null;
  const delen = [perPers ? r.product.name : r.keuze_count + "× " + r.product.name];
  if (perPers) delen.push(aantalTekst(r.personen, r.product.eenheid, true));
  if (r.tijd) delen.push("voorkeurstijd " + r.tijd);
  delen.push(euro(r.total_cents));
  return delen.join(" · ");
}

/** Taaknaam + omschrijving voor Mews (en de receptiemail).
 *  o = {verblijf, email, regels, totaalCents, opmerking, recommended} */
function bouwTaak(o) {
  const v = o.verblijf;
  const corrigeer = o.regels.filter((r) => r.afwijking);
  const naam = v.first_name;
  const regels = [];
  if (corrigeer.length) {
    regels.push("!! CORRIGEER IN MEWS");
    for (const r of corrigeer) regels.push("- " + r.afwijking);
    regels.push("");
  }
  const verblijfTekst = (v.arrival_label || v.arrival || "?") + " t/m " + (v.departure_label || v.departure || "?") +
    ", " + v.adults + " pers.";
  regels.push(
    "Besteld via visit.asteria.nl/extras (pre-arrival mail).",
    "Reservering: " + (v.number || v.id),
    "Gast: " + (naam || "-") + " " + (o.email ? "<" + o.email + ">" : "(e-mail onbekend)"),
    "Verblijf: " + verblijfTekst,
    "",
    "Bestelling:"
  );
  for (const r of o.regels) regels.push("- " + regelSamenvatting(r));
  if (o.regels.some((r) => r.key === "ontbijt")) {
    regels.push("Controleer of het tarief al ontbijt bevat; zo ja, verwijder de productregel.");
  }
  regels.push(
    "Totaal gast: " + euro(o.totaalCents) + " (op de kamerrekening)",
    "",
    "Opmerking gast: " + (o.opmerking || "-"),
    "Aanbevolen in de mail: " + (o.recommended && KEYS[o.recommended] ? KEYS[o.recommended].naam : "-"),
    ""
  );

  const todo = [];
  const diner = o.regels.find((r) => r.key === "diner");
  if (diner) {
    todo.push("tafel in ons restaurant reserveren voor " + (diner.personen || v.adults) + " pers." +
      (diner.avond_labels.length ? " op " + opsomming(diner.avond_labels) : "") +
      (diner.tijd ? " rond " + diner.tijd : ""));
  }
  const wellness = o.regels.find((r) => r.key === "wellness");
  if (wellness) {
    todo.push("wellness reserveren voor " + (wellness.personen || v.adults) + " pers." +
      (wellness.avond_labels.length ? " op " + opsomming(wellness.avond_labels) : "") + " en het tijdstip bevestigen");
  }
  for (const f of o.regels.filter((r) => r.product.eenheid === "fiets")) {
    todo.push("fietsen klaarzetten bij de receptie: " + aantalTekst(f.personen !== null ? f.personen : f.keuze_count, "fiets") +
      " (" + f.product.name.toLowerCase() + "), dag volgens de opmerking");
  }
  const opKamer = [];
  if (o.regels.some((r) => r.key === "badjas")) opKamer.push("badjassen en slippers");
  if (o.regels.some((r) => r.key === "handdoek")) opKamer.push("handdoekpakketten");
  if (o.regels.some((r) => r.key === "kruidenolie")) opKamer.push("kruidenolie");
  if (opKamer.length) todo.push(opsomming(opKamer) + " op de kamer klaarleggen");
  if (o.regels.some((r) => r.key === "early" || r.key === "late")) todo.push("early check-in/late check-out noteren");
  regels.push((corrigeer.length ? "Te doen: eerst de correctie hierboven in Mews; daarna " : "Te doen: de producten staan automatisch op de reservering; ") +
    (todo.length ? todo.join("; ") : "controleren") + ".");

  let taakNaam = "Extra's via website: " + o.regels.map((r) => r.keuze_count + "× " + r.product.name).join(", ");
  const achter = corrigeer.length ? " (CORRIGEER)" : "";
  if (taakNaam.length + achter.length > TAAKNAAM_MAX) taakNaam = taakNaam.slice(0, TAAKNAAM_MAX - achter.length - 1).trimEnd() + "…";
  taakNaam += achter;

  return { name: taakNaam, description: regels.join("\n"), corrigeer: corrigeer.length > 0 };
}

/** Gastteksten (je-vorm); en/de vallen terug op nl zolang ze leeg zijn. */
const T = {
  nl: {
    onderwerp: "Je extra's voor Hotel Asteria staan genoteerd",
    aanhef: (naam) => "Beste " + (naam || "gast") + ",",
    intro: (datum) => "Wij hebben de volgende extra's aan je verblijf" + (datum ? " op " + datum : "") + " toegevoegd:",
    persoon: (n) => n + (n === 1 ? " persoon" : " personen"),
    fiets: (n) => n + (n === 1 ? " fiets" : " fietsen"),
    dagen: (n) => n + (n === 1 ? " dag" : " dagen"),
    nachten: (n) => n + (n === 1 ? " nacht" : " nachten"),
    voor: "voor",
    op: "op",
    en: "en",
    avonden: (n) => n + (n === 1 ? " avond" : " avonden"),
    voorkeurstijd: (t) => "voorkeurstijd " + t + ", wij bevestigen het tijdstip",
    overleg: "de receptie reserveert je plek en bevestigt het tijdstip",
    totaal: (b) => "Totaal: " + b + ". Dit bedrag komt op je kamerrekening; je rekent het bij vertrek af aan de receptie.",
    opmerking: (o) => "Je opmerking: " + o,
    wijzigen: "Wil je nog iets wijzigen? Bel ons via " + TELEFOON + " of beantwoord deze e-mail.",
    slot: "Wij verheugen ons op je komst.",
  },
  en: {},
  de: {},
};

function teksten(taal) {
  return Object.assign({}, T.nl, T[taal] || {});
}

function gastZin(r, t) {
  const perPers = r.type !== "eenmalig" && r.personen !== null;
  let zin = "  " + (perPers ? r.product.name : r.keuze_count + "× " + r.product.name);
  const wie = []; // "voor 2 personen op wo 21 okt 2026", "voor 2 fietsen"
  if (perPers) wie.push(t.voor + " " + (r.product.eenheid === "fiets" ? t.fiets(r.personen) : t.persoon(r.personen)));
  if (r.type === "perdag" && r.avond_labels.length) wie.push(t.op + " " + opsomming(r.avond_labels, t.en));
  else if (r.type === "perdag" && r.personen) {
    const n = Math.round(r.units / r.personen);
    wie.push(r.product.dagLabel === "dag" ? t.dagen(n) : t.avonden(n));
  }
  const delen = wie.length ? [wie.join(" ")] : [];
  if (r.type === "pernacht") delen.push(t.nachten(r.nachten)); // "voor 2 personen, 2 nachten"
  if (r.tijd) delen.push(t.voorkeurstijd(r.tijd));
  else if (r.product.tijd_overleg) delen.push(t.overleg);
  if (delen.length) zin += " " + delen.join(", ");
  return zin + ": " + euro(r.total_cents);
}

function bevestigingGast(naam, verblijf, regels, totaalCents, opmerking, taal) {
  const t = teksten(taal || (verblijf && verblijf.lang) || "nl");
  const datum = verblijf.arrival_label || (verblijf.arrival ? verblijf.arrival.split("-").reverse().join("-") : "");
  return [
    t.aanhef(naam),
    "",
    t.intro(datum),
    "",
    regels.map((r) => gastZin(r, t)).join("\n"),
    "",
    t.totaal(euro(totaalCents)),
    opmerking ? "\n" + t.opmerking(opmerking) : "",
    "",
    t.wijzigen,
    "",
    t.slot,
    "",
    "Hotel Asteria",
    "Maasheseweg 80a, 5804 AD Venray",
    TELEFOON + " · " + MAIL_STANDAARD,
  ].join("\n");
}

/* ────────────────────────────────────────────── POST /api/extras/bestel */

async function handleBestel(request, env, h) {
  if (!(await h.rateOk(env, request, "/api/extras/bestel"))) {
    return h.json({ ok: false, message: "Te veel aanvragen vanaf dit adres. Probeer het over een minuut opnieuw of bel " + TELEFOON + "." }, 429);
  }
  let body;
  try {
    body = await request.json();
  } catch (e) {
    return h.json({ ok: false, message: "Ongeldige aanvraag." }, 400);
  }
  if (!body || typeof body !== "object") return h.json({ ok: false, message: "Ongeldige aanvraag." }, 400);

  // Honeypot + tijdcheck: stil "gelukt" teruggeven, niets doorsturen.
  if (h.isSpam(body.website, body.t0)) return h.json({ ok: true }, 200);

  const verblijf = leesVerblijf(body, h);
  if (!verblijf) return h.json({ ok: false, message: "Deze link is niet geldig." }, 400);
  const email = h.line(body.e, 200);
  if (email && !h.isEmail(email)) return h.json({ ok: false, message: "Vul een geldig e-mailadres in.", fields: ["e"] }, 400);
  const opmerking = h.clean(body.opmerking, 600);
  const taal = verblijf.lang;
  const mailInfo = env.MAIL_INFO || MAIL_STANDAARD;

  let items;
  try {
    items = await haalCatalogus();
  } catch (e) {
    console.log("[api] extras: catalogus mislukt bij bestellen: " + e);
    return h.json({ ok: false, message: "De extra's konden nu niet worden verwerkt. Bel " + TELEFOON + " of mail " + MAIL_STANDAARD + "." }, 503);
  }
  const perId = {};
  for (const p of items) perId[p.id] = p;

  const regelsIn = Array.isArray(body.regels) ? body.regels.slice(0, MAX_REGELS) : [];
  let regels = [];
  const gezien = {};
  for (const rg of regelsIn) {
    const id = h.clean(rg && rg.product_id, 40).toLowerCase();
    const p = perId[id];
    if (!p) {
      if (id) return h.json({ ok: false, message: "Een van de gekozen extra's is niet meer beschikbaar. Vernieuw de pagina.", fields: ["product_id"], product_id: id }, 400);
      continue;
    }
    if (gezien[id]) continue;
    gezien[id] = true;
    const keuze = leesRegel(rg, p, verblijf);
    if (keuze.fout) return h.json(keuze.fout, 400);
    regels.push(berekenRegel(p, keuze, verblijf));
  }
  if (!regels.length) return h.json({ ok: false, message: "Kies eerst een of meer extra's." }, 400);

  // Regels met afwijking vooraan: de receptietaak hangt aan regel 1.
  regels = regels.filter((r) => r.afwijking).concat(regels.filter((r) => !r.afwijking));

  const naam = verblijf.first_name;
  const totaalCents = regels.reduce((s, r) => s + r.total_cents, 0);
  if (totaalCents > PLAFOND_CENTS) {
    return h.json({ ok: false, message: "Deze bestelling is groter dan wij online kunnen verwerken. Bel ons via " + TELEFOON + ", dan regelen wij het graag.", fields: ["regels"] }, 400);
  }
  const samenvatting = regels.map(regelSamenvatting).join("\n");
  const taak = bouwTaak({ verblijf, email, regels, totaalCents, opmerking, recommended: verblijf.recommended });

  const basis = {
    secret: env.EXTRAS_SHARED_SECRET || "",
    reservation_id: verblijf.id,
    reservation_number: verblijf.number,
    service_id: SERVICE_ID,
    guest_name: naam,
    guest_email: email,
    arrival: verblijf.arrival,
    departure: verblijf.departure,
    adults: verblijf.adults,
    nights: verblijf.nights,
    remark: opmerking,
    order_summary: samenvatting,
    order_total: euro(totaalCents),
    lang: taal,
  };

  // ── per productregel één call naar de Zap; alleen de eerste regel maakt de receptietaak ──
  const dry = isDry(env);
  const fouten = [];
  for (let i = 0; i < regels.length; i++) {
    const r = regels[i];
    const payload = Object.assign({}, basis, {
      product_id: r.product.bestel_id || r.product.id,
      product_name: r.product.name,
      count: r.count,
      charging: r.product.bestel_charging,
      unit_price: euro(r.product.price_cents),
      line_total: euro(r.total_cents),
      task: i === 0 ? "ja" : "nee",
      task_name: i === 0 ? taak.name : "",
      task_description: i === 0 ? taak.description : "",
      task_deadline: (verblijf.arrival || new Date().toISOString().slice(0, 10)) + "T12:00:00",
      // informatief (de Zap leest ze niet), allemaal strings
      persons: r.personen === null ? "" : String(r.personen),
      units: String(r.units),
      evenings: r.avonden.join(","),
      evening_labels: r.avond_labels.join(", "),
      preferred_time: r.tijd,
      billing: r.billing,
      mews_total: euro(r.mews_cents),
      deviation: r.afwijking,
      recommended_key: verblijf.recommended,
      client: CLIENT_V2,
      catalog_product_id: String(r.product.id),
    });
    if (dry) {
      console.log("[api] extras: EXTRAS_DRY_RUN · niet naar Zapier. payload=" + JSON.stringify(payload));
      continue;
    }
    if (!env.ZAPIER_EXTRAS_HOOK) {
      fouten.push("geen ZAPIER_EXTRAS_HOOK ingesteld");
      break;
    }
    try {
      const res = await fetch(env.ZAPIER_EXTRAS_HOOK, {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify(payload),
        signal: AbortSignal.timeout(8000),
      });
      if (res.status < 200 || res.status > 299) {
        const txt = await res.text();
        fouten.push("HTTP " + res.status + " bij " + r.product.name + ": " + txt.slice(0, 200));
      }
    } catch (e) {
      fouten.push("transportfout bij " + r.product.name + ": " + e);
    }
  }

  const fallback = fouten.length > 0;
  if (fallback) console.log("[api] extras: Zapier-hook faalde: " + fouten.join(" | "));

  // ── mails: kopie/fallback naar de receptie + bevestiging aan de gast ──
  const kop = fallback
    ? "LET OP: de automatische koppeling naar Mews gaf een fout, deze bestelling moet HANDMATIG op de reservering worden gezet.\nReden: " + fouten.join(" | ") + "\n\n"
    : "De producten staan automatisch op de reservering in Mews; er is ook een taak aangemaakt.\n\n";
  const receptieMail = {
    to: mailInfo,
    subject: (fallback ? "[HANDMATIG] " : "") + (taak.corrigeer ? "[CORRIGEER] " : "") + "Extra's besteld · reservering " +
      (verblijf.number || verblijf.id.slice(0, 8)) + (naam ? " (" + naam + ")" : ""),
    text: kop + taak.description,
  };
  if (email) receptieMail.replyTo = email;
  const receptieOk = await mailReceptie(env, receptieMail);
  if (fallback && !receptieOk) {
    return h.json({ ok: false, message: "De bestelling kon nu niet verwerkt worden. Bel " + TELEFOON + " of mail " + MAIL_STANDAARD + "." }, 503);
  }

  // Gastmail alleen via Resend; zonder Resend-key slaan we hem over.
  let mailSent = false;
  if (email && env.RESEND_API_KEY) {
    mailSent = await h.sendMail(env, {
      to: email,
      replyTo: mailInfo,
      subject: teksten(taal).onderwerp,
      text: bevestigingGast(naam, verblijf, regels, totaalCents, opmerking, taal),
    });
  }

  return h.json({
    ok: true,
    fallback: fallback,
    total_cents: totaalCents,
    mail_sent: !!mailSent,
    regels: regels.map((r) => ({
      product_id: r.product.id,
      key: r.key,
      count: r.keuze_count,
      personen: r.personen,
      avonden: r.avonden,
      avond_labels: r.avond_labels,
      tijd: r.tijd,
      total_cents: r.total_cents,
    })),
  }, 200);
}

export { AANBOD, KEYS, catalogusItem, leesVerblijf, leesRegel, berekenRegel, mewsCents, datumLabel, bouwTaak, bevestigingGast, regelSamenvatting };
