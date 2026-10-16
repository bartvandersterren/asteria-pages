/**
 * Seizoenskern: kalenderlogica voor /seizoen/ (gedeeld met parkhotel-site/src/seizoen-kern.js;
 * beide bestanden zijn gelijk op deze verwijzing na).
 *
 * Bron van waarheid is seizoen/<hotel>/actief.json op R2 (geschreven door OS > Mediabank >
 * Seizoensfoto's). Ontbreekt die of is hij ongeldig, dan geldt de meegebundelde kalender uit
 * de repo. Vorm van beide (versie 1):
 *   { versie: 1, hotel, tijdzone, bijgewerkt_op?, bijgewerkt_door?,
 *     periodes: [{ id, naam, van: "MM-DD", tot: "MM-DD", prioriteit }],
 *     links: { lander: { <periode>: doel }, arrangement: { <periode>: doel } },
 *     slots: { <slot>: { maat: [b, h], label_nu, mails: [...],
 *                        fotos: { <periode>: { key | pad, bron?, door?, op? } } } } }
 * `key` = R2-sleutel (foto staat op R2), `pad` = asset-pad in de site zelf (repo-foto).
 *
 * Periodekeuze: van de periodes die de dag bevatten wint de hoogste prioriteit (gelijk: eerste in
 * de lijst). Heeft een slot voor die periode geen foto (of een link geen doel), dan de volgende
 * periode die de dag ook bevat (feest > winter); daarna de meegebundelde kalender.
 */

export const R2_BASIS = "https://pub-c740ef36abd24be1aa637f4ee69d7a03.r2.dev";
export const KALENDER_TTL = 300; // seconden dat actief.json in de Cache API blijft
export const VERS_SLOT_TTL = 60; // `?vers=1` haalt hoogstens eens per minuut opnieuw op

const MMDD_RE = /^(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$/;

export function basisVan(env) {
  const b = env && env.SEIZOEN_BASIS ? String(env.SEIZOEN_BASIS) : R2_BASIS;
  return b.replace(/\/+$/, "");
}

/** Is dit een bruikbare kalender (versie 1, periodes en slots)? */
export function geldigeKalender(k) {
  if (!k || typeof k !== "object" || k.versie !== 1) return false;
  if (!Array.isArray(k.periodes) || k.periodes.length === 0) return false;
  if (!k.slots || typeof k.slots !== "object" || Array.isArray(k.slots)) return false;
  return k.periodes.every((p) => p && typeof p.id === "string" && p.id
    && MMDD_RE.test(p.van) && MMDD_RE.test(p.tot));
}

/** Valt mmdd in periode p? `tot` is inclusief; van > tot = over de jaarwisseling. */
export function bevat(p, mmdd) {
  return p.van <= p.tot ? mmdd >= p.van && mmdd <= p.tot : mmdd >= p.van || mmdd <= p.tot;
}

/** Periodes die mmdd bevatten, hoogste prioriteit eerst (gelijk: volgorde in de lijst). */
export function periodesOp(kalender, mmdd) {
  return kalender.periodes
    .map((p, i) => ({ p, i }))
    .filter(({ p }) => bevat(p, mmdd))
    .sort((a, b) => (Number(b.p.prioriteit) || 0) - (Number(a.p.prioriteit) || 0) || a.i - b.i)
    .map(({ p }) => p);
}

/** Id van de periode die op mmdd geldt; valt niets erin, dan de eerste periode. */
export function seizoenVoor(kalender, mmdd) {
  const op = periodesOp(kalender, mmdd);
  return (op[0] || kalender.periodes[0]).id;
}

export function periodeVan(kalender, id) {
  return kalender.periodes.find((p) => p.id === id) || null;
}

function fotoIn(kalender, slot, mmdd) {
  const s = kalender.slots && kalender.slots[slot];
  if (!s || !s.fotos) return null;
  for (const p of periodesOp(kalender, mmdd)) {
    const f = s.fotos[p.id];
    if (f && (f.key || f.pad)) return { foto: f, periode: p.id };
  }
  return null;
}

/**
 * Foto voor slot op mmdd: { foto, periode, uitBundel } of null (onbekend slot).
 * Eerst de actieve kalender, dan de meegebundelde (repo-foto).
 */
export function fotoVoor(kalender, slot, mmdd, bundel) {
  const r = fotoIn(kalender, slot, mmdd);
  if (r) return { ...r, uitBundel: kalender === bundel };
  if (bundel && bundel !== kalender) {
    const b = fotoIn(bundel, slot, mmdd);
    if (b) return { ...b, uitBundel: true };
  }
  return null;
}

/** Linkdoel (soort lander|arrangement) op mmdd: { doel, periode } of null. */
export function linkVoor(kalender, soort, mmdd, bundel) {
  for (const k of [kalender, bundel]) {
    if (!k) continue;
    const doelen = (k.links && k.links[soort]) || {};
    for (const p of periodesOp(k, mmdd)) {
      if (doelen[p.id]) return { doel: doelen[p.id], periode: p.id };
    }
  }
  return null;
}

/* ---------- datums ---------- */

function plusDagen(iso, n) {
  const [j, m, d] = iso.split("-").map(Number);
  return new Date(Date.UTC(j, m - 1, d + n)).toISOString().slice(0, 10);
}

/** De eerstvolgende n wissels na iso (YYYY-MM-DD): [{ datum, periode }]. */
export function volgendeWissels(kalender, iso, n) {
  const uit = [];
  let vorige = seizoenVoor(kalender, iso.slice(5));
  for (let i = 1; i <= 800 && uit.length < n; i++) {
    const dag = plusDagen(iso, i);
    const nu = seizoenVoor(kalender, dag.slice(5));
    if (nu !== vorige) uit.push({ datum: dag, periode: nu });
    vorige = nu;
  }
  return uit;
}

/** Een MM-DD halverwege periode p (voor de voorbeeldfoto's op het overzicht). */
export function middenVan(p) {
  const dagNr = (mmdd) => {
    const [m, d] = mmdd.split("-").map(Number);
    return Math.round((Date.UTC(2001, m - 1, Math.min(d, m === 2 ? 28 : d)) - Date.UTC(2001, 0, 1)) / 864e5);
  };
  const a = dagNr(p.van);
  let b = dagNr(p.tot);
  if (b < a) b += 365;
  const midden = (a + Math.floor((b - a) / 2)) % 365;
  return new Date(Date.UTC(2001, 0, 1 + midden)).toISOString().slice(5, 10);
}

/* ---------- laden van R2 ---------- */

function inDeAchtergrond(ctx, belofte) {
  if (!ctx || !ctx.waitUntil) return;
  try {
    ctx.waitUntil(Promise.resolve(belofte).catch((e) => {
      console.log("[seizoen] achtergrondtaak mislukt: " + e);
    }));
  } catch (e) {
    console.log("[seizoen] achtergrondtaak kon niet starten: " + e);
  }
}

async function haalActief(bron) {
  try {
    const r = await fetch(bron, {
      headers: { Accept: "application/json" },
      signal: typeof AbortSignal !== "undefined" && AbortSignal.timeout ? AbortSignal.timeout(4000) : undefined,
    });
    if (!r.ok) return { status: "geen", reden: "HTTP " + r.status };
    let k;
    try {
      k = JSON.parse(await r.text());
    } catch (e) {
      return { status: "geen", reden: "geen geldige JSON" };
    }
    if (!geldigeKalender(k)) return { status: "geen", reden: "JSON voldoet niet aan versie 1" };
    return { status: "ok", kalender: k };
  } catch (e) {
    return { status: "geen", reden: "netwerkfout: " + e };
  }
}

/**
 * Kalender laden: actief.json van R2 (Cache API, KALENDER_TTL), anders de bundel.
 * Geeft { kalender, bron: "r2" | "repo", reden?, bundel }.
 * `?vers=1` op het verzoek haalt opnieuw op (hoogstens eens per VERS_SLOT_TTL).
 */
export async function laadKalenderVan(request, env, ctx, bundel) {
  const url = new URL(request.url);
  const hotel = bundel.hotel;
  const bron = `${basisVan(env)}/seizoen/${hotel}/actief.json`;
  const repo = (reden) => ({ kalender: bundel, bron: "repo", reden, bundel });

  const cache = typeof caches !== "undefined" && caches.default ? caches.default : null;
  const sleutelUrl = new URL(`${url.origin}/__seizoen-cache/${hotel}/actief.json`);
  sleutelUrl.searchParams.set("bron", bron);
  const sleutel = new Request(sleutelUrl.toString(), { method: "GET" });

  let uitCache = null;
  if (cache) {
    try {
      const c = await cache.match(sleutel);
      if (c) uitCache = JSON.parse(await c.text());
    } catch (e) {
      console.log("[seizoen] cache lezen mislukt: " + e);
    }
  }

  let verversen = !uitCache;
  if (uitCache && cache && url.searchParams.get("vers") === "1") {
    const slotUrl = new URL(sleutelUrl.toString());
    slotUrl.searchParams.set("vers-slot", "1");
    const slotSleutel = new Request(slotUrl.toString(), { method: "GET" });
    let slot = null;
    try {
      slot = await cache.match(slotSleutel);
    } catch (e) {
      console.log("[seizoen] slot lezen mislukt: " + e);
    }
    if (!slot) {
      verversen = true;
      inDeAchtergrond(ctx, cache.put(slotSleutel, new Response("1", {
        headers: { "Content-Type": "text/plain; charset=utf-8", "Cache-Control": "public, max-age=" + VERS_SLOT_TTL },
      })));
    }
  }

  let uit = uitCache;
  if (verversen) {
    uit = await haalActief(bron);
    if (cache) {
      inDeAchtergrond(ctx, cache.put(sleutel, new Response(JSON.stringify(uit), {
        headers: { "Content-Type": "application/json", "Cache-Control": "public, max-age=" + KALENDER_TTL },
      })));
    }
  }

  if (uit && uit.status === "ok" && geldigeKalender(uit.kalender)) {
    return { kalender: uit.kalender, bron: "r2", bundel };
  }
  return repo((uit && uit.reden) || "onbekend");
}
