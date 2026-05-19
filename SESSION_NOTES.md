# Session Notes — 2026-05-19

## Wat gedaan

### Eerdere sessie
- Comfort kamer klikbaar gemaakt in het kamerblok (wellness-arr-c.html)

### Deze sessie
Volledige brainstorm + design spec voor de **booking popup** op wellness-arr-c.html.

**Spec:** `docs/superpowers/specs/2026-05-19-booking-popup-design.md` (gecommit 5c3afd4)

### Kern van het design
- Alle 4 "Boek"-knoppen openen een 2-staps popup
- **Stap 1**: Inline Flatpickr range-picker (kalender direct zichtbaar), bevestigingsbalk (aankomst/vertrek/nachten read-only), CTA naar stap 2 of direct boeken
- **Stap 2** (conditioneel, skip als kamer al gekozen op pagina): 6 kamer-cards met vaste upgrade-delta's, accordion voor meer info
- **Deeplink naar Mews**: `mewsVoucherCode=WELLNESS&mewsStart=&mewsEnd=&mewsCategories[0]=<id>`
- **Fase 2**: switch naar boeken.html via één `buildBookingUrl()` functie

### Technische bevindingen (Playwright onderzoek)
- `mewsStart` / `mewsEnd` (YYYY-MM-DD) werken ✓
- `mewsVoucherCode` werkt ✓
- `mewsCategories[0]=<id>` — in URL verwerkt door Mews
- Mews booking engine ID: `bee2f902-f30f-4977-b9f7-af5d00e4ab76`
- Mews serviceId: `755424cc-3077-4320-b069-af1d00ffbe47`

### Kamer → Mews categoryId mapping
| Kamer | Delta | Mews ID |
|---|---|---|
| Comfort | basis | `98900f3b-e5e2-49c9-9776-af1d00ffc315` |
| Royale | +€10 p.p. | `a8fd7310-0d61-422f-89e6-af1d00ffc315` |
| Deluxe | +€20 p.p. | `c737de50-e41e-4c8d-a818-af1d00ffc315` |
| Junior suite | +€30 p.p. | `27ea8deb-ded5-4856-8fdd-af1d00ffc315` |
| Suite | +€40 p.p. | `4a642b66-68e6-444c-beeb-af1d00ffc315` |
| Bruidssuite | +€60 p.p. | `a9f18d18-561b-47a9-8ba7-b2a800cfd0e2` |

## Wat open staat

**Volgende stap: implementatieplan schrijven**
1. `/clear` doen
2. Skill `superpowers:writing-plans` aanroepen
3. Spec: `docs/superpowers/specs/2026-05-19-booking-popup-design.md`

## Gotchas voor implementatie
- Flatpickr via CDN (geen build stap nodig)
- Popup z-index hoger dan sticky nav (z-index: 1000) en bestaande kamerpopup
- Mobile: popup scrollbaar als kalender + stap 2 viewport overschrijdt
- Bestaande kamerpopup JS nakijken voor `selectedRoomId` pattern
- `.superpowers/` toevoegen aan `.gitignore`
