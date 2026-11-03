// Unit-test arr-vanaf-kern.js (gemockte kalenderdelen, geen Mews). Gebruik: node --test scripts/test_arr_vanaf.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { delen, vanafVoorCode } from '../arr-vanaf-kern.js';

const KAMER = '98900f3b-e5e2-49c9-9776-af1d00ffc315';
const dag = (datum, cent, extra = {}) => Object.assign({ datum, beschikbaar: cent != null, aankomst_mag: true,
  prijzen: cent != null ? { [KAMER]: { prijs_cent: cent, berekend: false } } : undefined }, extra);

test('delen: 56 dagen vanaf 3 nov raken nov deel 1-4 en dec deel 1-4', () => {
  const { tot, delen: d } = delen('2026-11-03', 56);
  assert.equal(tot, '2026-12-28');
  assert.deepEqual(d.map((x) => x.maand + '/' + x.deel), ['2026-11/1', '2026-11/2', '2026-11/3', '2026-11/4', '2026-12/1', '2026-12/2', '2026-12/3', '2026-12/4']);
});

test('laagste echte prijs van de standaardkamer, ceil(cent/100/2), zondagkorting en buiten venster tellen niet', async () => {
  const kal = {
    '2026-11/1': [dag('2026-11-02', 10000), dag('2026-11-04', 25700), dag('2026-11-05', null)],     // 2 nov = voor vandaag
    '2026-11/2': [dag('2026-11-09', 24900), dag('2026-11-08', 20000, { prijzen: { [KAMER]: { prijs_cent: 20000, berekend: true } } })],
    '2026-11/3': [dag('2026-11-20', 30000, { aankomst_mag: false })],
    '2026-12/4': [dag('2026-12-29', 1000)],                                                           // na het venster
  };
  const haal = async (code, maand, deel) => ({ ok: true, dagen: kal[maand + '/' + deel] || [] });
  const r = await vanafVoorCode('WELLNESS2026', { standaardkamer: KAMER.toUpperCase(), nachten: 1 }, '2026-11-03', haal, 56);
  assert.equal(r.prijs_cent, 24900);
  assert.equal(r.euro, 125);           // 249 / 2 = 124,50 -> 125
  assert.equal(r.eenheid, 'pp_nacht');
  assert.equal(r.datum, '2026-11-09');
  assert.equal(r.volledig, true);
});

test('vaste nachten: p.p. voor het hele verblijf', async () => {
  const haal = async () => ({ ok: true, dagen: [dag('2026-11-06', 33200)] });
  const r = await vanafVoorCode('WEEKEND', { standaardkamer: KAMER, nachten: 2 }, '2026-11-03', haal, 56);
  assert.equal(r.euro, 166); assert.equal(r.eenheid, 'pp_verblijf'); assert.equal(r.nachten, 2);
});

test('Mews-/kalenderfout: alles faalt -> null; deels faalt -> prijs, volledig false', async () => {
  const fout = async () => { throw new Error('mews_http_500'); };
  assert.equal(await vanafVoorCode('GOLF', { standaardkamer: KAMER }, '2026-11-03', fout, 56), null);
  let n = 0;
  const half = async () => { if (n++ % 2) throw new Error('x'); return { ok: true, dagen: [dag('2026-11-10', 37100)] }; };
  const r = await vanafVoorCode('GOLF', { standaardkamer: KAMER }, '2026-11-03', half, 56);
  assert.equal(r.euro, 186); assert.equal(r.volledig, false);
  const leeg = async () => ({ ok: true, dagen: [] });
  assert.equal(await vanafVoorCode('GOLF', { standaardkamer: KAMER }, '2026-11-03', leeg, 56), null);
});
