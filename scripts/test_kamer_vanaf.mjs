// Unit-test voor kamer-vanaf-kern.js (gemockte Mews): node --test scripts/test_kamer_vanaf.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { dagPrijzen, combineer, haalDeel, dagenVanDeel, KAMERS, AANTAL_DELEN, utc } from '../kamer-vanaf-kern.js';

const RATES = [
  { Id: 'R-OTA', IsPrivate: false, Name: { 'nl-NL': 'Non refundable OTA logies' } },
  { Id: 'R-NR', IsPrivate: false, Name: { 'nl-NL': 'Kamer zonder ontbijt (terugbetaling niet mogelijk)' } },
  { Id: 'R-ONTB', IsPrivate: false, Name: { 'nl-NL': 'Kamer met ontbijt' } },
  { Id: 'R-PRIVE', IsPrivate: true, Name: { 'nl-NL': 'Wellness' } },
];
const prijs = (rate, eur) => ({ RateId: rate, Price: { Total: { EUR: eur } } });
function antwoord(basis, opties = {}) {
  return {
    Rates: RATES,
    RoomCategoryAvailabilities: Object.entries(KAMERS).map(([k, v]) => ({
      RoomCategoryId: v.id,
      AvailableRoomCount: opties.vol === k ? 0 : 3,
      RoomOccupancyAvailabilities: [1, 2, 3].map((a) => ({
        AdultCount: a, ChildCount: 0,
        Pricing: [prijs('R-OTA', basis - 50), prijs('R-PRIVE', basis - 40), prijs('R-NR', basis + (a === v.personen ? 0 : -30)), prijs('R-ONTB', basis + 30)],
      })).concat([{ AdultCount: 2, ChildCount: 1, Pricing: [prijs('R-NR', basis - 60)] }]),
    })),
  };
}

test('dagPrijzen: laagste publieke niet-OTA-prijs bij de juiste bezetting, geen privé, geen kinderen', () => {
  const p = dagPrijzen(antwoord(132.3));
  assert.equal(p.comfort, 13230);
  assert.equal(p['comfort-3'], 13230);      // bezetting 3 (bij 2 zou het 102,30 zijn)
  assert.equal(Object.keys(p).length, 8);
});

test('dagPrijzen: kamer zonder beschikbaarheid valt weg', () => {
  const p = dagPrijzen(antwoord(150, { vol: 'suite' }));
  assert.equal(p.suite, undefined);
  assert.equal(p.deluxe, 15000);
});

test('combineer: laagste dag, euro naar boven, zondagvlag, null zonder prijs, volledig', () => {
  const delen = [];
  for (let d = 1; d <= AANTAL_DELEN; d++) delen.push({ dagen: dagenVanDeel('2026-11-03', d).map((datum) => ({ datum, prijzen: { comfort: datum === '2026-11-08' ? 13230 : 14000 } })) });
  const r = combineer(delen);
  assert.deepEqual(r.prijzen.comfort, { euro: 133, prijs_cent: 13230, datum: '2026-11-08', zondag: true });
  assert.equal(r.prijzen.suite, null);
  assert.equal(r.volledig, true);
  delen[3] = null;
  assert.equal(combineer(delen).volledig, false);
  assert.equal(combineer([{ dagen: [{ datum: '2026-11-03', storing: true }] }]).prijzen.comfort, null);
});

test('combineer: hele euro blijft heel (geen afrondingsfout)', () => {
  assert.equal(combineer([{ dagen: [{ datum: '2026-11-04', prijzen: { royale: 14100 } }] }]).prijzen.royale.euro, 141);
});

test('haalDeel: 8 nachten na elkaar, Client-header, geen AdultCount; 429 opnieuw; fout = storing', async () => {
  const calls = [];
  let n = 0;
  const nep = async (url, init) => {
    const b = JSON.parse(init.body);
    calls.push(b);
    n++;
    if (n === 2) return { ok: false, status: 429, headers: { get: () => '1' } };
    if (b.StartUtc === utc('2026-11-07')) return { ok: false, status: 400, headers: { get: () => null } };
    return { ok: true, status: 200, json: async () => antwoord(140) };
  };
  const r = await haalDeel('2026-11-03', 1, nep, 60000);
  assert.equal(r.dagen.length, 8);
  assert.equal(calls[0].Client, 'Asteria Booking 1.0.0');
  assert.equal(calls[0].ConfigurationId, '6dc9094c-76e3-4fd8-83a7-af1d00ffc556');
  assert.equal(calls[0].AdultCount, undefined);
  assert.equal(calls[0].VoucherCode, undefined);
  assert.equal(calls[0].StartUtc, '2026-11-02T23:00:00Z');
  assert.equal(r.dagen[1].prijzen.comfort, 14000);   // na de 429 opnieuw gelukt
  assert.equal(r.dagen[4].storing, true);            // 7 nov gaf 400
  assert.equal(dagenVanDeel('2026-11-03', 7).length, 8);
});
