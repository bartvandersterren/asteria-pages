# Booking Popup — Design Spec
_Datum: 2026-05-19_

## Doel

Wanneer een bezoeker op een "Boek"-knop klikt op `wellness-arr-c.html`, opent een popup waar hij datums kiest en optioneel een kamertype selecteert. Daarna wordt hij zo diep mogelijk in Mews Distributor gedropt.

Later (fase 2), als de eigen boeken.html koppeling live is, wisselt alleen de CTA-bestemming van Mews-URL naar boeken.html — de popup zelf blijft identiek.

---

## Triggers

Alle vier "Boek"-knoppen op de pagina openen de popup:

1. Sticky FAB — "Boek direct"
2. Sticky card — "Boek direct →"
3. Arrangement-blok CTA — "Boek het arrangement"
4. Diner-blok CTA — "Boek het arrangement"

Aanvullend: als een gast al een kamer heeft geopend via de kamerpopup, en daar op "Boek" klikt, opent de booking popup met die kamer al voorgeselecteerd (stap 2 wordt overgeslagen).

---

## Popup — Stap 1: Datum kiezen

### Layout
- Lichte achtergrond (geen donkere header — kleur in build te bepalen)
- Sluit-knop (×) rechtsboven
- Stap-indicator: twee dots (stap 1 actief)

### Kalender
- Inline, direct zichtbaar bij openen — geen extra klik nodig
- Flatpickr library (range mode, ~4KB gzip)
- Range picker: gast klikt aankomst, kalender blijft open, gast klikt vertrek
- Geselecteerde range gehighlight (start rood, range licht rood)
- Verleden datums disabled

### Bevestigingsbalk (puur informatief, read-only)
Drie velden die live updaten bij klikken in de kalender:
- **Aankomst** — bijv. "za 4 juli"
- **Vertrek** — bijv. "zo 5 juli"
- **Nachten** — bijv. "1 nacht"

### CTA-rij
- Primair: `Volgende: kies kamer →` → opent stap 2
- Secundair (klein): `Of boek direct zonder kamerkeuze` → slaat stap 2 over, opent Mews direct

---

## Popup — Stap 2: Kamer kiezen

### Conditioneel
Stap 2 wordt **overgeslagen** als de gast al een kamer heeft geselecteerd op de pagina (via de kamerpopup). In dat geval gaat "Volgende" direct naar de Mews deeplink.

### Layout
- Terugknop (← stap 1)
- Stap-indicator: twee dots (stap 2 actief)
- Koptekst: "Kies je kamer"

### Kamer-cards (6 stuks)
Radio-stijl — één selectie tegelijk. Elke card bevat:
- Kamernaam
- Upgrade delta (of "basis" voor Comfort)
- Klikbaar voor meer info: accordion-toggle binnen de card (tekst klapt open onder de kamernaam)

| Kamer | Upgrade | Mews categoryId |
|---|---|---|
| Comfort kamer | basis | `98900f3b-e5e2-49c9-9776-af1d00ffc315` |
| Royale kamer | +€10 p.p. | `a8fd7310-0d61-422f-89e6-af1d00ffc315` |
| Deluxe kamer | +€20 p.p. | `c737de50-e41e-4c8d-a818-af1d00ffc315` |
| Junior suite | +€30 p.p. | `27ea8deb-ded5-4856-8fdd-af1d00ffc315` |
| Suite | +€40 p.p. | `4a642b66-68e6-444c-beeb-af1d00ffc315` |
| Bruidssuite | +€60 p.p. | `a9f18d18-561b-47a9-8ba7-b2a800cfd0e2` |

Niet tonen: Comfort 3-persoons (`85ca19d7`) en Intern (`d527d41d`).

### Meer info per kamer (expandable)
Kort: oppervlakte + 2-3 kenmerken. Bijv. voor Deluxe: "25m² · privé infraroodsauna · kingsize bed".

### CTA
- Primair: `Bekijk beschikbaarheid →` → opent Mews deeplink in nieuw tabblad

---

## Mews Deeplink (fase 1)

```
https://app.mews.com/distributor/bee2f902-f30f-4977-b9f7-af5d00e4ab76
  ?mewsVoucherCode=WELLNESS
  &mewsStart=YYYY-MM-DD
  &mewsEnd=YYYY-MM-DD
  &mewsCategories[0]=<categoryId>   ← alleen als kamer gekozen
```

Bevestigde werkende parameters (getest via Playwright):
- `mewsVoucherCode` ✓
- `mewsStart` / `mewsEnd` (formaat: `YYYY-MM-DD`) ✓
- `mewsAdultCount` ✓ (niet gebruikt in popup — personen weggelaten)
- `mewsCategories[0]` — parameter herkend door Mews, deeplink naar specifieke categorie

Mews opent in nieuw tabblad (`target="_blank"`).

---

## Fase 2 — Switch naar boeken.html

Wanneer de eigen booking engine live is, wisselt alleen de URL-constructie:

```
/boeken.html?checkin=YYYY-MM-DD&checkout=YYYY-MM-DD&room=<slug>
```

De popup-code heeft één functie `buildBookingUrl(checkin, checkout, roomId)` — alleen die functie hoeft aangepast te worden.

---

## State management

- Geselecteerde kamer op de pagina: bijgehouden via `data-selected-room` op een globaal element, of als JS variabele `window.selectedRoomId`
- Popup leest deze waarde bij openen om te beslissen of stap 2 getoond wordt
- Geen localStorage, geen cookies — puur in-memory per sessie

---

## Technische keuzes

| Keuze | Beslissing |
|---|---|
| Date picker library | Flatpickr (range mode) — 4KB gzip, geen afhankelijkheden |
| Popup animatie | Bestaande modal-stijl van kamerpopup als referentie |
| Personen-selector | Niet geïmplementeerd — Mews gebruikt voucher voor arrangement |
| Upgrade kosten | Hardcoded vaste delta's (zie tabel) — geen API call nodig |
| Kamer deeplink | `mewsCategories[0]=<id>` — IDs hardcoded in JS object |

---

## Niet in scope

- Personen-selector (weggelaten, YAGNI)
- Availability check vanuit popup (Mews toont beschikbaarheid)
- Taalwisseling in popup (volgt pagina)
- Analytics events (kunnen later toegevoegd worden)
