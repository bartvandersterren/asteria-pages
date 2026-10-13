// node --test scripts/test_extras_unit.mjs  — bestelmodel uit functions/api/extras/[[path]].js
// (port van parkhotel-site test/extras.test.mjs; geen netwerk, geen Cloudflare-runtime nodig)
import { test } from "node:test";
import assert from "node:assert/strict";
import { AANBOD, KEYS, catalogusItem, leesVerblijf, leesRegel, berekenRegel, mewsCents, datumLabel, bouwTaak, bevestigingGast } from "../functions/api/extras/[[path]].js";

/* Stub van de helpers: kopieën van clean/line/isEmail. */
function clean(v, max) {
  if (v === null || v === undefined) return "";
  let s = String(v).replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/g, "");
  s = s.replace(/\r\n?/g, "\n").trim();
  if (typeof max === "number" && s.length > max) s = s.slice(0, max);
  return s;
}
function line(v, max) {
  return clean(v, max).replace(/\s*\n\s*/g, " ");
}
function isEmail(v) {
  return /^[^\s@,;:<>"]+@[^\s@,;:<>"]+\.[A-Za-z]{2,}$/.test(v);
}
const H = { clean, line, isEmail };

const GUID = "0c90a9f6-2e2e-4214-88c8-b4b900b4f047";
/* Prijzen en chargingmodes zoals Mews-Asteria ze levert (configuration/get, 13 okt 2026). */
const MEWS = {
  diner: [3750, "PerPersonPerTimeUnit"], ontbijt: [1750, "PerPersonPerTimeUnit"], wellness: [1250, "PerPerson"],
  fiets: [950, "PerPerson"], ebike: [2500, "PerPerson"], kruidenolie: [495, "Once"], badjas: [700, "PerPerson"],
  handdoek: [450, "PerPerson"], early: [2500, "Once"], late: [2500, "Once"],
};

/** Catalogus-item zoals haalCatalogus() het levert, zonder Mews. mc overschrijft de chargingmode. */
function item(key, mc) {
  const a = KEYS[key];
  const [prijs, charging] = MEWS[key];
  return catalogusItem(a, { name: a.naam, description: "", price_cents: prijs, mews_charging: mc || charging, image_url: "" });
}
function verblijf(extra) {
  return leesVerblijf(Object.assign({ r: GUID, n: "123456", a: "2026-10-20", d: "2026-10-22", p: "2", v: "Stijn" }, extra || {}), H);
}
function reken(key, keuze, v, mc) {
  const it = item(key, mc);
  const k = leesRegel(keuze, it, v);
  assert.ok(!k.fout, JSON.stringify(k.fout));
  return berekenRegel(it, k, v);
}

/* ── AANBOD ── */

test("AANBOD: tien producten in Mews-volgorde met de Mews-ids van Asteria", () => {
  assert.deepEqual(AANBOD.map((a) => a.key), ["diner", "ontbijt", "wellness", "fiets", "ebike", "kruidenolie", "badjas", "handdoek", "early", "late"]);
  assert.equal(KEYS.diner.id, "75fce6f2-6339-41c2-9e48-b3b60095d412");
  assert.equal(KEYS.wellness.id, "bd06307a-e86f-434c-a799-b43400d93806");
  assert.equal(KEYS.late.id, "196e6fe4-f15a-4384-a7e0-b097006801ee");
  for (const a of AANBOD) {
    assert.match(a.id, /^[0-9a-f-]{36}$/, a.key);
    assert.match(a.foto, /^\/fotos\/extras-[a-z]+\.webp$/, a.key);
    assert.equal(a.bestel_id, undefined, a.key); // nog geen Once-bestelproducten bij Asteria
  }
});
test("AANBOD: groep, typen, dagLabel en eenheid", () => {
  const g = {};
  for (const a of AANBOD) g[a.key] = [a.groep, a.type, a.dagLabel || "", a.eenheid || "", a.max];
  assert.deepEqual(g, {
    diner: ["verblijf", "perdag", "avond", "persoon", 8], ontbijt: ["verblijf", "pernacht", "", "persoon", 8],
    wellness: ["verblijf", "perdag", "dag", "persoon", 8], fiets: ["verblijf", "personen", "", "fiets", 8],
    ebike: ["verblijf", "personen", "", "fiets", 8], kruidenolie: ["verblijf", "eenmalig", "", "", 3],
    badjas: ["aankomst", "personen", "", "persoon", 8], handdoek: ["aankomst", "personen", "", "persoon", 8],
    early: ["aankomst", "eenmalig", "", "", 1], late: ["vertrek", "eenmalig", "", "", 1],
  });
  assert.equal(KEYS.wellness.tijd, true);
});
test("AANBOD: teksten in je-vorm, zonder em-dash, Asteria-feiten", () => {
  for (const a of AANBOD) {
    assert.doesNotMatch(a.tekst + a.naam, /—|\buw\b|\bu\b/, a.key);
  }
  assert.match(KEYS.early.tekst, /12\.00 uur/);
  assert.match(KEYS.late.tekst, /14\.00 uur/);
});
test("catalogusItem: eigen foto als pad op deze site, dagLabel alleen bij perdag", () => {
  const it = item("diner");
  assert.equal(it.image_url, "/fotos/extras-diner.webp");
  assert.equal(it.dagLabel, "avond");
  assert.equal(item("fiets").dagLabel, "");
  assert.equal(item("wellness").tijd_overleg, true);
  assert.equal(it.bestel_id, "");
  assert.equal(it.bestel_charging, "PerPersonPerTimeUnit");
});

/* ── datumLabel en leesVerblijf ── */

test("datumLabel nl lang en kort, ongeldig", () => {
  assert.equal(datumLabel("2026-10-20", "nl", false), "di 20 okt 2026");
  assert.equal(datumLabel("2026-10-20", "nl", true), "di 20 okt");
  assert.equal(datumLabel("2027-01-01", "nl", false), "vr 1 jan 2027");
  assert.equal(datumLabel("2026-13-45", "nl", false), "");
  assert.equal(datumLabel("2026-10-22", "de", false), "Do 22. Okt. 2026");
});
test("leesVerblijf: labels, nachtenlijst, aanbevolen", () => {
  const v = verblijf({ k: "wellness" });
  assert.equal(v.nights, 2);
  assert.equal(v.arrival_label, "di 20 okt 2026");
  assert.deepEqual(v.nights_list.map((n) => n.short), ["di 20 okt", "wo 21 okt"]);
  assert.equal(v.recommended, "wellness");
  assert.equal(verblijf({ k: "prosecco" }).recommended, "");
});
test("leesVerblijf: vertrek ≤ aankomst → datums leeg; ongeldige GUID; personen begrensd", () => {
  const v = verblijf({ d: "2026-10-19" });
  assert.equal(v.arrival, "");
  assert.equal(v.nights, 1);
  assert.deepEqual(v.nights_list, []);
  assert.equal(leesVerblijf({ r: "nope" }, H), null);
  assert.equal(verblijf({ p: "12" }).adults, 8);
  assert.equal(verblijf({ p: "0" }).adults, 2);
});

/* ── leesRegel ── */

test("leesRegel: standaard-count = personen, eenmalig 1", () => {
  const v = verblijf({ p: "3" });
  assert.equal(leesRegel({}, item("kruidenolie"), v).count, 1);
  assert.equal(leesRegel({}, item("badjas"), v).count, 3);
  assert.equal(leesRegel({}, item("wellness"), v).count, 3);
  assert.equal(leesRegel({}, item("fiets"), v).count, 3);
  assert.equal(leesRegel({}, item("badjas"), verblijf({ p: "9" })).count, 8);
});
test("leesRegel: count buiten 1..max → fout", () => {
  const v = verblijf();
  for (const c of [0, 4, -1, 2.5, "abc"]) {
    const r = leesRegel({ count: c }, item("kruidenolie"), v);
    assert.deepEqual(r.fout.fields, ["count"], String(c));
    assert.equal(r.fout.product_id, KEYS.kruidenolie.id);
  }
  assert.ok(leesRegel({ count: 2 }, item("late"), v).fout);
});
test("leesRegel: dagen alleen bij perdag en binnen het verblijf; fiets kent geen dagen", () => {
  const v = verblijf();
  assert.deepEqual(leesRegel({ avonden: ["2026-10-20"] }, item("fiets"), v).fout.fields, ["avonden"]);
  assert.deepEqual(leesRegel({ avonden: ["2026-10-22"] }, item("diner"), v).fout.fields, ["avonden"]);
  const f = leesRegel({ avonden: ["2026-10-22"] }, item("wellness"), v).fout;
  assert.match(f.message, /dagen/);
  assert.match(f.message, /je verblijf/);
  assert.deepEqual(leesRegel({ avonden: ["2026-10-21", "2026-10-20", "2026-10-21"] }, item("wellness"), v).avonden, ["2026-10-20", "2026-10-21"]);
  assert.deepEqual(leesRegel({}, item("diner"), v).avonden, ["2026-10-20", "2026-10-21"]);
});
test("leesRegel: tijd alleen bij diner, genormaliseerd", () => {
  const v = verblijf();
  assert.equal(leesRegel({ tijd: "19.00" }, item("diner"), v).tijd, "19:00");
  assert.equal(leesRegel({ tijd: "17.30" }, item("diner"), v).tijd, "17:30");
  assert.deepEqual(leesRegel({ tijd: "25:00" }, item("diner"), v).fout.fields, ["tijd"]);
  assert.equal(leesRegel({ tijd: "onzin" }, item("wellness"), v).tijd, "");
});

/* ── berekenRegel (geen bestel_id: model B waar Mews vermenigvuldigt) ── */

test("mewsCents: Once, PerPerson, PerPersonPerTimeUnit", () => {
  assert.equal(mewsCents(495, "Once", 2, 2, 2), 990);
  assert.equal(mewsCents(700, "PerPerson", 1, 2, 2), 1400);
  assert.equal(mewsCents(3750, "PerPersonPerTimeUnit", 1, 2, 2), 15000);
});
test("eenmalig kruidenolie 2: count 2, exact", () => {
  const r = reken("kruidenolie", { count: 2 }, verblijf());
  assert.deepEqual([r.count, r.total_cents, r.mews_cents, r.billing, r.afwijking], [2, 990, 990, "exact", ""]);
});
test("early en late: eenmalig € 25,00, exact", () => {
  for (const k of ["early", "late"]) {
    const r = reken(k, { count: 1 }, verblijf());
    assert.deepEqual([r.count, r.total_cents, r.afwijking], [1, 2500, ""]);
  }
});
test("badjas 2 pers. bij 2 gasten (PerPerson): count 1, Mews € 14,00, exact", () => {
  const r = reken("badjas", { count: 2 }, verblijf());
  assert.deepEqual([r.count, r.personen, r.total_cents, r.mews_cents, r.billing, r.afwijking], [1, 2, 1400, 1400, "B", ""]);
});
test("badjas 1 pers. bij 2 gasten: count 1, Mews € 14,00 ≠ € 7,00 → afwijking", () => {
  const r = reken("badjas", { count: 1 }, verblijf());
  assert.equal(r.mews_cents, 1400);
  assert.equal(r.total_cents, 700);
  assert.match(r.afwijking, /Mews boekt 1× € 7,00 × 2 pers\. = € 14,00; de gast koos 1 pers\., eenmalig = € 7,00/);
});
test("fiets 1 fiets bij 2 gasten: afwijking spreekt van fietsen", () => {
  const r = reken("fiets", { count: 1 }, verblijf());
  assert.equal(r.total_cents, 950);
  assert.equal(r.mews_cents, 1900);
  assert.match(r.afwijking, /de gast koos 1 fiets, eenmalig = € 9,50/);
  const twee = reken("fiets", { count: 2 }, verblijf());
  assert.deepEqual([twee.count, twee.mews_cents, twee.afwijking], [1, 1900, ""]);
});
test("wellness 2 pers. × 2 dagen (PerPerson): count 2, € 50,00 exact", () => {
  const r = reken("wellness", { count: 2 }, verblijf());
  assert.deepEqual([r.count, r.units, r.total_cents, r.mews_cents, r.afwijking], [2, 4, 5000, 5000, ""]);
  assert.deepEqual(r.avond_labels, ["di 20 okt 2026", "wo 21 okt 2026"]);
});
test("wellness 1 pers. op 1 dag bij 2 gasten: afwijking", () => {
  const r = reken("wellness", { count: 1, avonden: ["2026-10-21"] }, verblijf());
  assert.equal(r.total_cents, 1250);
  assert.equal(r.mews_cents, 2500);
  assert.match(r.afwijking, /de gast koos 1 pers\. op wo 21 okt 2026 = € 12,50/);
});
test("diner 2 pers. alle avonden: count 1, € 150,00 exact; op 1 avond → afwijking", () => {
  const alle = reken("diner", { count: 2 }, verblijf());
  assert.deepEqual([alle.count, alle.total_cents, alle.mews_cents, alle.afwijking], [1, 15000, 15000, ""]);
  const een = reken("diner", { count: 2, avonden: ["2026-10-21"], tijd: "19.00" }, verblijf());
  assert.equal(een.total_cents, 7500);
  assert.equal(een.mews_cents, 15000);
  assert.match(een.afwijking, /Mews boekt 1× € 37,50 × 2 pers\. × 2 nachten = € 150,00/);
});
test("ontbijt 2 pers. / 2 nachten: count 1, € 70,00 exact", () => {
  const r = reken("ontbijt", { count: 2 }, verblijf());
  assert.deepEqual([r.count, r.units, r.total_cents, r.mews_cents, r.afwijking], [1, 4, 7000, 7000, ""]);
});
test("perdag op een Once-product (later bestel_id): count = personen × dagen, billing A", () => {
  const r = reken("diner", { count: 2, avonden: ["2026-10-21"] }, verblijf(), "Once");
  assert.deepEqual([r.count, r.billing, r.total_cents, r.mews_cents, r.afwijking], [2, "A", 7500, 7500, ""]);
});

/* ── bouwTaak ── */

test("bouwTaak zonder afwijking: bron, gast, verblijf, taken", () => {
  const v = verblijf({ k: "wellness" });
  const regels = [reken("wellness", { count: 2 }, v), reken("badjas", { count: 2 }, v), reken("handdoek", { count: 2 }, v), reken("kruidenolie", { count: 1 }, v)];
  const tot = regels.reduce((s, r) => s + r.total_cents, 0);
  const t = bouwTaak({ verblijf: v, email: "gast@example.com", regels, totaalCents: tot, opmerking: "", recommended: "wellness" });
  assert.equal(t.corrigeer, false);
  assert.match(t.description, /^Besteld via visit\.asteria\.nl\/extras \(pre-arrival mail\)\./);
  assert.match(t.description, /Gast: Stijn <gast@example.com>/);
  assert.match(t.description, /Toegang tot de Top Floor wellness · 2 personen, di 20 okt en wo 21 okt · € 50,00/);
  assert.match(t.description, /Badjas en slippers op je kamer · 2 pers\. · € 14,00/);
  assert.match(t.description, /wellness reserveren voor 2 pers\. op di 20 okt 2026 en wo 21 okt 2026/);
  assert.match(t.description, /badjassen en slippers, handdoekpakketten en kruidenolie op de kamer klaarleggen/);
  assert.match(t.description, /Aanbevolen in de mail: Toegang tot de Top Floor wellness/);
  assert.doesNotMatch(t.description, /BØFF|prosecco|vlaai|massage|—/i);
});
test("bouwTaak met afwijking: CORRIGEER-blok, (CORRIGEER), diner en fietsen", () => {
  const v = verblijf();
  const regels = [reken("diner", { count: 2, avonden: ["2026-10-21"], tijd: "19.30" }, v), reken("fiets", { count: 2 }, v), reken("ontbijt", { count: 2 }, v)];
  const t = bouwTaak({ verblijf: v, email: "", regels, totaalCents: 1, opmerking: "Glutenvrij", recommended: "" });
  assert.equal(t.corrigeer, true);
  assert.ok(t.description.startsWith("!! CORRIGEER IN MEWS\n- Driegangendiner in ons restaurant: Mews boekt"));
  assert.ok(t.name.endsWith(" (CORRIGEER)"));
  assert.match(t.description, /e-mail onbekend/);
  assert.match(t.description, /tafel in ons restaurant reserveren voor 2 pers\. op wo 21 okt 2026 rond 19:30/);
  assert.match(t.description, /Fietshuur · 2 fietsen · € 19,00/);
  assert.match(t.description, /fietsen klaarzetten bij de receptie: 2 fietsen \(fietshuur\)/);
  assert.match(t.description, /Controleer of het tarief al ontbijt bevat; zo ja, verwijder de productregel\./);
  assert.match(t.description, /Opmerking gast: Glutenvrij/);
});
test("bouwTaak: taaknaam ≤ 120 tekens", () => {
  const v = verblijf({ p: "3" });
  const regels = AANBOD.map((a) => reken(a.key, a.key === "badjas" ? { count: 1 } : {}, v)); // badjas 1 van 3 → afwijking
  const t = bouwTaak({ verblijf: v, email: "", regels, totaalCents: 1, opmerking: "", recommended: "" });
  assert.ok(t.name.length <= 120, t.name.length);
  assert.ok(t.name.endsWith("… (CORRIGEER)"));
});

/* ── gastmail ── */

test("bevestigingGast: je-vorm, Asteria-afsluiting, geen em-dash", () => {
  const v = verblijf();
  const regels = [reken("diner", { count: 2, avonden: ["2026-10-21"], tijd: "19.00" }, v), reken("wellness", { count: 2 }, v), reken("fiets", { count: 2 }, v), reken("ontbijt", { count: 2 }, v)];
  const txt = bevestigingGast("Stijn", v, regels, 21400, "Graag een rustige tafel", "nl");
  assert.match(txt, /^Beste Stijn,/);
  assert.match(txt, /Wij hebben de volgende extra's aan je verblijf op di 20 okt 2026 toegevoegd:/);
  assert.match(txt, /Driegangendiner in ons restaurant voor 2 personen op wo 21 okt 2026, voorkeurstijd 19:00, wij bevestigen het tijdstip: € 75,00/);
  assert.match(txt, /Toegang tot de Top Floor wellness voor 2 personen op di 20 okt 2026 en wo 21 okt 2026, de receptie reserveert je plek en bevestigt het tijdstip: € 50,00/);
  assert.match(txt, /Fietshuur voor 2 fietsen: € 19,00/);
  assert.match(txt, /Ontbijtbuffet voor 2 personen, 2 nachten: € 70,00/);
  assert.match(txt, /Dit bedrag komt op je kamerrekening/);
  assert.match(txt, /Je opmerking: Graag een rustige tafel/);
  assert.match(txt, /Maasheseweg 80a, 5804 AD Venray/);
  assert.match(txt, /0478 511 466 · info@asteria\.nl/);
  assert.doesNotMatch(txt, /—|\buw\b|\bu\b/);
});
