// node --test scripts/test_seizoen_kern.mjs  — periodekeuze en terugval uit seizoen-kern.js (geen netwerk)
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import {
  seizoenVoor, fotoVoor, linkVoor, geldigeKalender, volgendeWissels, middenVan, laadKalenderVan,
} from "../seizoen-kern.js";

const BUNDEL = JSON.parse(readFileSync(new URL("../seizoen-kalender.json", import.meta.url)));

// R2-kalender met een feestperiode (prioriteit 10) over de jaarwisseling, en alleen voor hero een feestfoto.
const R2 = structuredClone(BUNDEL);
R2.periodes.push({ id: "feest", naam: "Feestdagen", van: "12-15", tot: "01-01", prioriteit: 10 });
R2.links.lander.feest = "/kerst";
R2.slots.hero.fotos.feest = { key: "seizoen/asteria/hero-feest-001.jpg" };
R2.slots.hero.fotos.winter = { key: "seizoen/asteria/hero-winter-001.jpg" };
delete R2.slots.sfeer.fotos.winter; // sfeer winter ontbreekt op R2 -> repo

test("gebundelde kalender is geldig (versie 1)", () => {
  assert.equal(geldigeKalender(BUNDEL), true);
  assert.equal(geldigeKalender({ versie: 2, periodes: [], slots: {} }), false);
  assert.equal(geldigeKalender({ versie: 1, periodes: [{ id: "x", van: "13-01", tot: "01-01" }], slots: {} }), false);
  assert.equal(geldigeKalender(null), false);
});

test("seizoenVoor: gewone seizoenen en de jaarwisseling", () => {
  assert.equal(seizoenVoor(BUNDEL, "10-16"), "herfst");
  assert.equal(seizoenVoor(BUNDEL, "12-01"), "winter");
  assert.equal(seizoenVoor(BUNDEL, "01-15"), "winter");
  assert.equal(seizoenVoor(BUNDEL, "02-29"), "winter");
  assert.equal(seizoenVoor(BUNDEL, "03-01"), "lente");
  assert.equal(seizoenVoor(BUNDEL, "08-31"), "zomer");
});

test("seizoenVoor: hoogste prioriteit wint, ook over de jaarwisseling", () => {
  assert.equal(seizoenVoor(R2, "12-14"), "winter");
  assert.equal(seizoenVoor(R2, "12-15"), "feest");
  assert.equal(seizoenVoor(R2, "12-31"), "feest");
  assert.equal(seizoenVoor(R2, "01-01"), "feest");
  assert.equal(seizoenVoor(R2, "01-02"), "winter");
});

test("fotoVoor: feest > winter > repo", () => {
  let hero = fotoVoor(R2, "hero", "12-20", BUNDEL);
  assert.equal(hero.periode, "feest");
  assert.equal(hero.foto.key, "seizoen/asteria/hero-feest-001.jpg");
  const sfeer = fotoVoor(R2, "sfeer", "12-20", BUNDEL); // geen feest- en winterfoto in R2 -> bundel
  assert.equal(sfeer.uitBundel, true);
  assert.equal(sfeer.periode, "winter");
  assert.match(sfeer.foto.pad, /sfeer-winter\.jpg$/);
  hero = fotoVoor(R2, "hero", "12-05", BUNDEL); // winter zelf uit R2
  assert.equal(hero.foto.key, "seizoen/asteria/hero-winter-001.jpg");
  assert.equal(fotoVoor(R2, "bestaatniet", "12-20", BUNDEL), null);
});

test("linkVoor: feest heeft eigen lander, arrangement valt terug op winter", () => {
  assert.equal(linkVoor(R2, "lander", "12-20", BUNDEL).doel, "/kerst");
  assert.equal(linkVoor(R2, "arrangement", "12-20", BUNDEL).doel, "https://www.asteria.nl/arrangementen");
});

test("volgendeWissels en middenVan", () => {
  assert.deepEqual(volgendeWissels(R2, "2026-10-16", 3).map((w) => w.datum + " " + w.periode),
    ["2026-12-01 winter", "2026-12-15 feest", "2027-01-02 winter"]);
  assert.equal(middenVan({ van: "09-01", tot: "11-30" }), "10-16");
  assert.equal(middenVan({ van: "12-01", tot: "02-29" }), "01-14");
});

test("laadKalenderVan: gefaalde fetch, 404 en ongeldige JSON -> bundel; geldige JSON -> r2", async () => {
  globalThis.caches = undefined; // geen Cache API in node
  const req = new Request("https://visit.asteria.nl/seizoen/hero.jpg");
  const met = async (impl) => { globalThis.fetch = impl; return laadKalenderVan(req, {}, null, BUNDEL); };
  let r = await met(async () => { throw new Error("netwerk weg"); });
  assert.equal(r.bron, "repo"); assert.equal(r.kalender, BUNDEL);
  r = await met(async () => new Response("nee", { status: 404 }));
  assert.equal(r.bron, "repo");
  r = await met(async () => new Response("{kapot", { status: 200 }));
  assert.equal(r.bron, "repo");
  r = await met(async () => new Response(JSON.stringify({ versie: 1 }), { status: 200 }));
  assert.equal(r.bron, "repo");
  let gevraagd = "";
  r = await met(async (u) => { gevraagd = String(u); return new Response(JSON.stringify(R2), { status: 200 }); });
  assert.equal(r.bron, "r2");
  assert.equal(r.kalender.periodes.length, 5);
  assert.equal(gevraagd, "https://pub-6f4ac4e7df2b4c258d5fffc06c518bcc.r2.dev/seizoen/asteria/actief.json");
});
