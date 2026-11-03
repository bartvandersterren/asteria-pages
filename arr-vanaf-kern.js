/**
 * Kern van /api/arr-vanaf (functions/api/arr-vanaf.js): laagste "vanaf"-prijs per arrangementcode in de komende
 * 56 dagen, met dezelfde rekenregel en instellingen als de prijskalender (/api/arr-kalender, content/arr-kalender.json).
 *
 * Werkwijze: de kalender is per code/maand/deel (8 dagen) al uitgerekend en 6 uur gecachet door /api/arr-kalender.
 * Deze kern vraagt die delen op via `haalDeel(code, maand, deel)` (in productie een fetch naar de eigen
 * /api/arr-kalender, zodat de Mews-logica, privé-tarieven, vaste nachten, aankomstdagen en de cache van de kalender
 * één bron houden) en neemt het minimum:
 *   - alleen dagen binnen [vandaag, vandaag + 55], beschikbaar en aankomst_mag;
 *   - alleen de standaardkamer van de code (cfg.standaardkamer = eerste 'inbegrepen' kamer uit _kamers);
 *   - alleen echte Mews-prijzen (berekend:false). De berekende zondagkorting (berekend:true) telt niet mee: die
 *     staat apart in het zondagblok, en de vanaf-prijs moet de gewone prijs blijven.
 *   - euro = ceil(prijs_cent / 100 / 2) (zelfde als de kalendercel): p.p. per nacht, of bij vaste nachten
 *     (cfg.nachten > 1) p.p. voor het hele verblijf.
 * Uitkomst per code: {euro, prijs_cent, datum, nachten, eenheid: 'pp_nacht' | 'pp_verblijf'} of null (geen prijs of
 * een Mews-/kalenderfout zonder enige bruikbare dag).
 * Puur (geen Cloudflare-API's), zodat node --test hem kan draaien: scripts/test_arr_vanaf.mjs.
 */

export const VENSTER_DAGEN = 56;
export const DEEL_DAGEN = 8;

function plusDagen(iso, n) { return new Date(Date.parse(iso + 'T00:00:00Z') + n * 86400000).toISOString().slice(0, 10); }

/** Alle (maand, deel)-paren van /api/arr-kalender die [van, van + dagen - 1] raken. */
export function delen(van, dagen) {
  const tot = plusDagen(van, (dagen || VENSTER_DAGEN) - 1);
  const uit = [];
  const gezien = {};
  for (let d = van; d <= tot; d = plusDagen(d, 1)) {
    const maand = d.slice(0, 7);
    const dag = Number(d.slice(8, 10));
    const deel = Math.min(4, Math.floor((dag - 1) / DEEL_DAGEN) + 1);
    const k = maand + '/' + deel;
    if (!gezien[k]) { gezien[k] = 1; uit.push({ maand, deel }); }
  }
  return { tot, delen: uit };
}

/** Laagste prijs voor één code. haalDeel(code, maand, deel) -> kalenderantwoord ({ok, dagen}) of gooit. */
export async function vanafVoorCode(code, cfg, van, haalDeel, dagen) {
  const { tot, delen: lijst } = delen(van, dagen);
  const kamer = String(cfg.standaardkamer || '').toLowerCase();
  const nachten = cfg.nachten || 1;
  let best = null, fouten = 0, gelukt = 0, storing = false;
  // Na elkaar, niet tegelijk: elk deel is een eigen /api/arr-kalender-invocatie met 2 Mews-calls tegelijk; alles
  // parallel (8 delen x 2) gaf bij een lege cache direct 429 van Mews (getest 3 nov 2026).
  const antwoorden = [];
  for (const x of lijst) {
    try { const r = await haalDeel(code, x.maand, x.deel); antwoorden.push(r && r.ok ? r : null); }
    catch (e) { antwoorden.push(null); }
  }
  for (const r of antwoorden) {
    if (!r) { fouten++; continue; }
    gelukt++;
    for (const dag of r.dagen || []) {
      if (dag.datum < van || dag.datum > tot) continue;
      if (dag.storing) storing = true;
      if (!dag.beschikbaar || dag.aankomst_mag === false) continue;
      const p = dag.prijzen && dag.prijzen[kamer];
      if (!p || p.berekend || typeof p.prijs_cent !== 'number') continue;
      if (!best || p.prijs_cent < best.prijs_cent) best = { prijs_cent: p.prijs_cent, datum: dag.datum };
    }
  }
  if (!best) return null;   // geen tarief, of alles faalde
  return {
    euro: Math.ceil(best.prijs_cent / 100 / 2 - 1e-9),
    prijs_cent: best.prijs_cent,
    datum: best.datum,
    nachten,
    eenheid: nachten > 1 ? 'pp_verblijf' : 'pp_nacht',
    volledig: fouten === 0 && !storing && gelukt === lijst.length,
  };
}
