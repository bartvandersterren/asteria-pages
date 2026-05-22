# lander-google — Coordinator Plan

> **Doel van dit document:** Dit is het uitvoeringsplan voor de coördinatorsessie. Niet het implementatieplan zelf — dat staat in `docs/superpowers/plans/2026-05-22-lander-google.md`. Dit document beschrijft hoe de coördinator de taken orkestreert met minimale tussenkomst van de gebruiker.

---

## Aanpak: Pre-flight + 4 sequentiële agents

**Task 1 is al afgerond** (git: `a8d6c1c`). Open: Tasks 2–8.

**Batching:**

| Agent | Tasks | Type | Skills |
|-------|-------|------|--------|
| Agent 1 | Task 2 (Hero) | Copy + foto swap | `frontend-design` |
| Agent 2 | Tasks 3 + 4 (USP-blok + Sfeerblok) | Nieuw bouwen | `frontend-design` + `ui-ux-pro-max` |
| Agent 3 | Tasks 5 + 6 + 7 (Kamertypes, Popup, Footer) | Mechanisch (grep-replace) | Geen |
| Agent 4 | Task 8 (Polish + final check) | QA + copy-review | Geen |

---

## Stap 0: Pre-flight intake

Het design van de nieuwe blokken is vastgelegd in de spec. Er is nog één beslissing die de gebruiker moet maken:

```
Voordat ik begin, één vraag:

**Hero-foto (Task 2):**
De huidige wellness-hero wordt vervangen. In de repo heb ik:
- `fotos/hero-buitenkant.webp` — exterieur hotel, rode bakstenen gevel, blauwe lucht
- `fotos/intro-lobby.webp` — moderne lobby met receptie en raam op groen

Welke wil je als hero? Of een andere foto uit de fotobank?
```

**Coördinator wacht op antwoord. Daarna begint Agent 1.**

---

## Agent 1: Task 2 — Hero aanpassen

### Context package (volledig zelfstandig)

```
Je bent een sub-agent die één taak uitvoert in de Asteria Pages repository.

**Doel:** Pas de hero-sectie van `lander-google.html` aan van wellness-focus naar generiek hotel.

**Werkdirectory:** /Users/bartvandersterren/Projects/asteria-pages

**Verplichte skill:** Gebruik de `frontend-design` skill voor de copy en visuele aanpassingen.

**Te lezen vóór je begint (verplicht):**
- `brand.css` — kleurpalet, typografie tokens, spacing
- `design-dna.md` — visuele stijl, anti-patronen, wat NIET te doen
- `tone-of-voice.md` — schrijfstijl: altijd "u/uw", geen em dashes, geen superlatieven
- `hotel-content.md` — feiten voor trust badges en copy

**Pre-flight antwoord van de gebruiker:**
- Hero-foto: [ANTWOORD — hier bakt de coördinator het antwoord in]

**Wat je doet:**
Voer Task 2 uit zoals beschreven in `docs/superpowers/plans/2026-05-22-lander-google.md` sectie "Task 2: Hero aanpassen":
1. Vervang hero-foto + preload-link in <head>
2. Herschrijf headline (max 8 woorden) en subline (max 15 woorden) — concreet, "u/uw"
3. Vervang trust badges door generieke hotel USPs op basis van hotel-content.md
4. Pas sticky CTA aan: "Boek uw verblijf"

**Verificatie:**
```bash
git add lander-google.html
git commit -m "feat: lander-google — hero generiek gemaakt"
git push
```
Wacht 35 seconden. Playwright screenshot mobile 375×812:
```js
// browser_run_code_unsafe:
await page.setViewportSize({ width: 375, height: 812 });
await page.goto('https://visit.asteria.nl/lander-google');
```
Dan browser_take_screenshot.

**Output:** Headline + subline + trust badge teksten + screenshot-observaties.

**Niet doen:** Andere secties aanraken. Geen nieuwe bestanden.
```

### Review criteria (coördinator checkt)
- [ ] Hero-foto is niet-wellness
- [ ] Headline max 8 woorden, "u" niet "je"
- [ ] Trust badges generiek (geen "wellness arrangement")
- [ ] Sticky CTA = "Boek uw verblijf"
- [ ] Screenshot: headline niet afgekapt, badges wrappen correct

---

## Agent 2: Tasks 3 + 4 — USP-blok + Sfeerblok

### Context package

```
Je bent een sub-agent die twee nieuwe blokken bouwt in de Asteria Pages repository.

**Doel:** Voeg twee nieuwe secties toe aan `lander-google.html`:
1. USP-blok (direct na hero, voor kamertypes)
2. Sfeerblok (direct na USP-blok, voor kamertypes)

**Werkdirectory:** /Users/bartvandersterren/Projects/asteria-pages

**Verplichte skills:**
- Gebruik de `frontend-design` skill vóórdat je begint met bouwen
- Gebruik de `ui-ux-pro-max` skill voor visuele kwaliteitsbewaking

**Te lezen vóór je begint (verplicht):**
- `brand.css` — kleurpalet (#c23435, #f8f7f5, #1a1a1a etc.), typografie tokens (Electrolize, Montserrat 300/400/700)
- `design-dna.md` — visuele stijl, anti-patronen, wat NIET te doen
- `tone-of-voice.md` — schrijfstijl
- `hotel-content.md` — feiten voor USP-copy
- `docs/superpowers/specs/2026-05-22-usp-sfeer-blok-design.md` — VOLLEDIGE design spec voor beide blokken met exacte HTML-structuur, CSS-klassen en JS

**Wat je doet:**

TAAK A — USP-blok:
Bouw exact zoals beschreven in de design spec sectie "USP-blok":
- Desktop: 2-koloms split (headline links sticky, 3 USP-rijen rechts met rode border + thumbnail)
- Mobile: accordion (3 items, eerste open, toggle via data-open attribuut)
- Twee aparte DOM-structuren (desktop en mobile), gewisseld via CSS media query (>768px / ≤768px)
- Inhoud en foto's: zie spec sectie "Drie USPs"

TAAK B — Sfeerblok:
Bouw exact zoals beschreven in de design spec sectie "Sfeerblok":
- Horizontale draggable carousel (cursor: grab, mousedown/mousemove JS)
- 3 kaarten, alternerende layout via CSS nth-child(even) .sfeer-foto-wrap { order: 999 }
- Drag-to-scroll JS: zie spec sectie "Drag-to-scroll JS"
- Kaartinhoud: zie spec sectie "Kaartinhoud"
- Geen sectie-heading

**Volgorde:** Bouw USP-blok volledig eerst (HTML + CSS + JS), dan sfeerblok.

**Verificatie:**
```bash
git add lander-google.html
git commit -m "feat: lander-google — USP-blok + sfeerblok toegevoegd"
git push
```
Wacht 35 seconden. Playwright screenshots:
- Desktop 1280×800: beide blokken volledig zichtbaar
- Mobile 375×812: USP accordion + sfeer-slider met peek van volgende kaart

**Output:** Screenshots + observaties per blok + bevestiging accordion werkt op mobile.

**Niet doen:** Hero, kamertypes of andere bestaande secties aanraken.
```

### Review criteria (coördinator checkt)
- [ ] USP-blok desktop: 2-koloms split zichtbaar, rode borders, thumbnails rechts
- [ ] USP-blok mobile: accordion, eerste item open, chevron aanwezig
- [ ] Sfeerblok: 3 kaarten, kaart 2 heeft tekst boven/foto onder (even-stijl)
- [ ] Sfeerblok drag werkt (grab cursor zichtbaar)
- [ ] Mobile: volgende kaart peekt zichtbaar aan rand
- [ ] Volgorde pagina: hero → USP → sfeer → kamertypes

---

## Agent 3: Tasks 5 + 6 + 7 — Kamertypes, Popup, Footer

### Context package

```
Je bent een sub-agent die drie mechanische taken uitvoert in de Asteria Pages repository.
Puur copy-cleanup: wellness/arrangement-verwijzingen vervangen door generieke tekst.

**Doel:** Verwijder alle wellness-arrangement-specifieke taal uit kamertypes, booking popup en footer.

**Werkdirectory:** /Users/bartvandersterren/Projects/asteria-pages

**Referentie:** `docs/superpowers/plans/2026-05-22-lander-google.md` — secties Task 5, Task 6, Task 7

**TAAK A — Kamertypes (Task 5):**
Grep op "arrangement", "wellness", "WELLNESS" in het kamertypes-IIFE blok.
- CTA per kamer: "Selecteer kamer"
- Popup-CTA: "Boek deze kamer"
- Verwijder "Inclusief wellness" als aanwezig

**TAAK B — Booking popup (Task 6):**
Grep op "wellness", "arrangement" in het popup-IIFE.
- Stap 1 titel: "Wanneer wilt u verblijven?"
- Stap 2 titel: "Kies uw kamer"
- Stap 3 titel: "Kamerdetails"
- Primaire CTA: "Boek uw verblijf"

**TAAK C — Email capture + footer (Task 7):**
- Email capture offer (wellness voucher): NIET aanpassen — bewust wellness-gefocust gelaten
- Footer: grep op "wellness", "arrangement" — verwijder of generaliseer
- Controleer adres: "Maasheseweg 80a, 5804 AD Venray" (niet Leunseweg)

**Verificatie:**
Open pagina live → klik sticky CTA → kies datum → kies kamer → controleer Mews-URL.
URL mag GEEN mewsVoucherCode bevatten.

```bash
git add lander-google.html
git commit -m "feat: lander-google — kamertypes, popup, footer generiek"
git push
```

**Output:** Lijst per taak van gewijzigde teksten (voor/na). Mews-URL die getest is.

**Niet doen:** USP-blok, sfeerblok of hero aanraken. Geen structuurwijzigingen.
```

### Review criteria (coördinator checkt)
- [ ] Geen "arrangement" of "wellness" in kamertypes-CTA's
- [ ] Popup-titels generiek
- [ ] Adres correct in footer
- [ ] Mews-URL heeft geen mewsVoucherCode parameter

---

## Agent 4: Task 8 — Polish + final check

### Context package

```
Je bent een sub-agent die de eindcheck uitvoert op `lander-google.html`.

**Doel:** Copy-review, meta-tags bijwerken, volledige visuele QA via Playwright.

**Werkdirectory:** /Users/bartvandersterren/Projects/asteria-pages

**Te lezen:**
- `tone-of-voice.md` — ter referentie bij copy-review
- `brand.css` — ter referentie bij visuele check

**Referentie:** `docs/superpowers/plans/2026-05-22-lander-google.md` sectie Task 8

**TAAK A — Copy-review:**
Grep op:
- em dash of en dash (— of –) in zichtbare tekst → vervang door punt, komma of middot
- "je", "jij", "jou" (niet in JS-variabelenamen) → vervang door "u"/"uw"
- Superlatieven: "beste", "unieke", "perfecte", "geweldige" → neutraliseer
- Resterende arrangement-verwijzingen

**TAAK B — Meta + SEO:**
```html
<title>Hotel Asteria Venray — Officiële Website | Boek direct</title>
<meta name="description" content="Overnacht in Hotel Asteria in Venray. Moderne kamers, wellness op de Top Floor, restaurant en brasserie. Gratis parkeren. Boek direct voor de beste prijs.">
<link rel="canonical" href="https://visit.asteria.nl/lander-google">
<meta property="og:url" content="https://visit.asteria.nl/lander-google">
```
OG-image: vervang wellness-hero door de hero-foto gekozen in Task 2.

**TAAK C — Playwright QA:**
```bash
git add lander-google.html
git commit -m "feat: lander-google — polish, meta, copy-review"
git push
```
Wacht 35 seconden. Screenshots via browser_run_code_unsafe (375×812 mobile):
Scroll door: hero → USP-blok → sfeerblok → kamertypes → email capture → footer.
Dan één desktop screenshot 1280×800.

**Output:** Lijst copy-fixes + bevestiging meta-tags + screenshot-observaties.
```

### Review criteria (coördinator checkt)
- [ ] Geen em dashes in zichtbare tekst
- [ ] Geen je/jij/jou
- [ ] Meta title + description correct
- [ ] Canonical = lander-google
- [ ] Alle blokken visueel correct mobile + desktop

---

## Coördinator-flow samengevat

```
1. Pre-flight: 1 vraag (hero-foto) → wacht op antwoord
2. Spawn Agent 1 (Task 2) → review → go/stop
3. Spawn Agent 2 (Tasks 3+4) → review → go/stop
4. Spawn Agent 3 (Tasks 5+6+7) → review → go/stop
5. Spawn Agent 4 (Task 8) → final review
6. Klaar — pagina live op visit.asteria.nl/lander-google
```

Bij **stop**: coördinator communiceert probleem aan gebruiker, lost op of spawnt fix-agent, dan door.

---

## Gotchas voor alle agents

- **Mews distributor ID:** `6dc9094c-76e3-4fd8-83a7-af1d00ffc556` — nooit wijzigen
- **Mobile testen:** gebruik `browser_run_code_unsafe` met `page.setViewportSize({ width: 375, height: 812 })` — `browser_resize` werkt niet (type coercion bug)
- **Deploy tijd:** altijd 35 seconden wachten na `git push` vóór live-check
- **Adres:** Maasheseweg 80a, 5804 AD Venray (niet Leunseweg)
- **Schrijfstijl:** altijd "u/uw", geen em dashes (— of –), geen superlatieven
- **Email capture offer:** bewust wellness-gefocust laten — niet aanpassen
- **brand.css lezen:** verplicht voor alle agents die HTML/CSS schrijven of aanpassen
