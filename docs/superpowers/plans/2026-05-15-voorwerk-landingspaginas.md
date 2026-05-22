# Voorwerk Asteria Landingspagina's — Implementatieplan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Kennisbank en workflow gereedmaken zodat elke volgende pagina-sessie start met volledige hotelkennis, foto-overzicht en een gedegen design brief.

**Architecture:** Twee sporen parallel. Spoor 1 maakt statische kennisdocumenten aan (`hotel-content.md`, `foto-index.md`) op basis van asteria.nl en de lokale fotobank. Spoor 2 herschrijft de `asteria-lander` skill met een verplichte design-stap vooraf en ontdubbelt CLAUDE.md.

**Tech Stack:** Playwright (scrapen asteria.nl), Markdown, Bash (fotocatalogus lezen)

---

## Bestanden

| Actie | Pad |
|-------|-----|
| Aanmaken | `hotel-content.md` (repo root) |
| Aanmaken | `foto-index.md` (repo root) |
| Wijzigen | `/Users/bartvandersterren/.claude/skills/asteria-lander/SKILL.md` |
| Wijzigen | `CLAUDE.md` (repo root) |

---

## Task 1: hotel-content.md scrapen van asteria.nl

**Files:**
- Aanmaken: `hotel-content.md`

- [ ] **Stap 1: Open asteria.nl kamerpagina met Playwright**

Navigeer naar `https://www.asteria.nl/kamers` en maak een snapshot. Noteer per kamertype:
- Naam
- Kenmerken (oppervlakte, bed, max personen, faciliteiten)
- Prijs per nacht (of "vanaf"-prijs)

- [ ] **Stap 2: Scrape arrangementen**

Navigeer naar `https://www.asteria.nl/arrangementen`. Noteer per arrangement:
- Naam
- Wat is inbegrepen
- Prijs per persoon of per kamer
- Eventuele boekingslink of Mews deeplink

- [ ] **Stap 3: Scrape homepage voor USPs en reviews**

Navigeer naar `https://www.asteria.nl`. Noteer:
- De USP-balk (3-5 kernvoordelen, exacte tekst)
- Google-reviewscore en aantal reviews (als zichtbaar)
- 3-5 review-quotes met naam en score

- [ ] **Stap 4: Scrape contactpagina**

Navigeer naar `https://www.asteria.nl/contact`. Noteer:
- Adres
- Telefoonnummer
- E-mailadres
- Openingstijden brasserie, restaurant, wellness (als apart vermeld)

- [ ] **Stap 5: Schrijf hotel-content.md**

Structuur van het bestand:

```markdown
# Hotel Asteria — Hotelinhoud

_Gescrapet van asteria.nl op [datum]. Controleer bij twijfel de actuele website._

## Kamertypes

### [Kamertype naam]
- **Kenmerken:** [oppervlakte, bed, etc.]
- **Faciliteiten:** [wifi, airco, etc.]
- **Prijs:** vanaf €[X] per nacht

## Arrangementen

### [Arrangement naam]
- **Inbegrepen:** [ontbijt, diner, wellness, etc.]
- **Prijs:** €[X] per persoon / per kamer
- **Boekingslink:** [URL of "via Mews booking engine"]

## Vaste USPs

- [USP 1 — exacte tekst van de site]
- [USP 2]
- [USP 3]

## Reviews

**Google-score:** [X,X] / 5 ([Y] reviews)

> "[Quote]" — [Naam], [Sterren]★

## Contact & Praktisch

- **Adres:** [adres]
- **Telefoon:** [tel]
- **E-mail:** [email]
- **Openingstijden brasserie:** [tijden]
- **Openingstijden restaurant:** [tijden]
- **Openingstijden wellness:** [tijden]

## Mews booking

- **Config ID:** 9fc01bd9-bc04-49f2-83cf-b44400835224
- **Enterprise ID:** 65a522c9-4828-413d-9ad8-af1d00ffb83f
- **Booking URL:** https://visit.asteria.nl/boeken
```

- [ ] **Stap 6: Commit**

```bash
git add hotel-content.md
git commit -m "docs: add hotel-content.md (scraped from asteria.nl)"
```

---

## Task 2: foto-index.md samenstellen

**Files:**
- Aanmaken: `foto-index.md`
- Bron: `~/Documents/Asteria Fotobank/catalogus.md`

- [ ] **Stap 1: Lees de catalogus per categorie**

Lees `~/Documents/Asteria Fotobank/catalogus.md`. De catalogus heeft 7 categorieën:
Brasserie (47), Buitenkant (54), Kamer (225), Lobby (70), Restaurant (51), Wellness (56), Zaal (194).

- [ ] **Stap 2: Selecteer per use case de beste 3-5 foto's**

Selectiecriteria (uit cro-guidelines.md):
- Voorkeur voor foto's met gasten (👤) boven lege ruimtes
- Hero: breed, licht, emotioneel — geen drone-shot
- Sfeer: mensen in actie (diner, ontbijt, lounge)
- Kamers: opgemaakt bed met warm licht, shot vanuit deur
- Tags `homepage hero` en `homepage` zijn prioriteit

Use cases om te dekken:
1. **Hero** — buitenkant of lobby, breed landschap, gasten
2. **Sfeer brasserie** — gasten aan tafel, avondlicht
3. **Sfeer restaurant** — diner, gasten
4. **Kamer comfort** — opgemaakt bed
5. **Kamer superior** — opgemaakt bed
6. **Kamer suite** — opgemaakt bed of badkamer
7. **Wellness** — sauna of spa met sfeer
8. **Natuur/omgeving** — buitenkant of omgeving
9. **Lobby/entree** — breed overzicht

- [ ] **Stap 3: Schrijf foto-index.md**

Structuur van het bestand:

```markdown
# Foto-index — Asteria Fotobank

_Selectie uit 697 foto's in `~/Documents/Asteria Fotobank/`. Volledige catalogus: `~/Documents/Asteria Fotobank/catalogus.md`._
_De 17 geoptimaliseerde foto's in `fotos/` zijn de standaard voor live pagina's. Gebruik deze index als je een andere foto nodig hebt._

## Hero

| Bestand | Omschrijving |
|---------|-------------|
| `~/Documents/Asteria Fotobank/[bestand].jpg` | [omschrijving] |

## Sfeer — Brasserie

| Bestand | Omschrijving |
|---------|-------------|
| ... | ... |

## Sfeer — Restaurant

...

## Kamers

### Comfort
...

### Superior
...

### Suite
...

## Wellness

...

## Natuur & Omgeving

...

## Lobby & Entree

...
```

- [ ] **Stap 4: Commit**

```bash
git add foto-index.md
git commit -m "docs: add foto-index.md (curated selection from fotobank)"
```

---

## Task 3: asteria-lander skill herschrijven

**Files:**
- Wijzigen: `/Users/bartvandersterren/.claude/skills/asteria-lander/SKILL.md`

- [ ] **Stap 1: Lees de huidige skill**

Lees `/Users/bartvandersterren/.claude/skills/asteria-lander/SKILL.md` volledig.

- [ ] **Stap 2: Schrijf de nieuwe skill**

De skill krijgt een verplichte **Stap 0** vóór de bestaande stappen. Verder worden de actieve referenties aan de kennisdocumenten toegevoegd.

Structuur van de nieuwe skill:

```markdown
# Asteria Landing Page — Verplicht Bouwproces

[bestaande intro]

---

## STAP 0 — DESIGN BRIEF (NIEUW — VERPLICHT)

**Doel:** Visueel en strategisch plan vastleggen voordat er ook maar één regel code wordt geschreven.

**Voer uit in deze volgorde:**

1. **Brainstorm** via superpowers:brainstorming skill:
   - Pagina-doel, doelgroep, verkeersbron (basis voor structuur en tone)
   - Welke blokken passen bij dit doel (volgorde conform cro-guidelines.md)

2. **Design brief** via ui-ux-pro-max skill:
   - Stijlkeuze en moodboard (passend bij Asteria brand)
   - Layout-variant per blok (niet altijd hetzelfde grid)
   - Typografische hiërarchie (H1-grootte, witruimte, contrast)
   - Foto-strategie: welke foto per blok, uit `foto-index.md`

3. **Output:** Goedgekeurd plan op papier met:
   - Blokkenlijst in volgorde (inclusief CRO-motivatie)
   - Stijlkeuze + foto-keuze per blok
   - Verwijzing naar relevante content uit `hotel-content.md`

Ga niet verder naar Stap 1 zonder goedgekeurd plan.

---

## STAP 1 — BRIEF

[bestaande tekst ongewijzigd]

**Referenties:**
- Tone of voice: zie `tone-of-voice.md`
- CRO-principes: zie `cro-guidelines.md`
- Hotelinhoud: zie `hotel-content.md`

---

## STAP 2 — STRUCTUUR

[bestaande tekst ongewijzigd]

**Referentie:** Paginavolgorde conform `cro-guidelines.md` sectie "Paginastructuur volgorde".

---

## STAP 3 — COPY

[bestaande tekst ongewijzigd]

**Referentie:** Schrijf conform `tone-of-voice.md`. Gebruik feitelijke inhoud uit `hotel-content.md` (prijzen, namen, locatie).

---

## STAP 4 — GRAFISCH

**Doel:** Visuele keuzes per blok vastleggen op basis van het Stap 0 plan.

Leg per blok vast:
- Welke foto (bestandspad uit `foto-index.md` of `fotos/`)
- Welke layout-variant
- Afwijkingen t.o.v. brand.css

---

## STAP 5 — BOUWEN

[bestaande tekst ongewijzigd]

---

## STAP 6 — QA

[bestaande tekst ongewijzigd]

**Referentie technische performance:** Controleer PageSpeed Insights score (streef naar 70+ mobile, 85+ desktop). Voer uit via https://pagespeed.web.dev/.

---

## STAP 7 — DEPLOY

[bestaande tekst ongewijzigd]
```

- [ ] **Stap 3: Sla de nieuwe skill op**

Overschrijf `/Users/bartvandersterren/.claude/skills/asteria-lander/SKILL.md` met de nieuwe inhoud.

- [ ] **Stap 4: Verificeer**

Lees het bestand terug en controleer:
- Stap 0 aanwezig en verplicht
- Alle referenties naar kennisdocumenten aanwezig
- Geen stappen verwijderd die er al in zaten

---

## Task 4: CLAUDE.md opschonen

**Files:**
- Wijzigen: `CLAUDE.md` (repo root)

- [ ] **Stap 1: Lees de huidige CLAUDE.md**

Lees `/Users/bartvandersterren/Projects/asteria-pages/CLAUDE.md` volledig.

- [ ] **Stap 2: Verwijder de stappenlijst**

Verwijder de volledige blokken STAP 1 t/m STAP 7 inclusief de tabel "Overzicht" onderaan. Dit is nu de verantwoordelijkheid van de `asteria-lander` skill.

- [ ] **Stap 3: Voeg pointer toe**

Voeg toe direct na de openingsregel (vóór de technische context):

```markdown
## Pagina's bouwen

Gebruik altijd de `asteria-lander` skill bij het bouwen van een nieuwe landingspagina. Die skill bevat het volledige 7-stappen proces inclusief design brief.

Beschikbare kennisdocumenten (altijd raadplegen bij pagina-sessie):
- `hotel-content.md` — kamers, arrangementen, prijzen, reviews, contact
- `foto-index.md` — fotoselectie per use case
- `tone-of-voice.md` — stemgeluid en schrijfstijl
- `cro-guidelines.md` — conversie-optimalisatie richtlijnen
- `brand.css` — design tokens
```

- [ ] **Stap 4: Controleer lengte**

CLAUDE.md mag niet meer dan 200 regels hebben (wordt anders afgekapt). Tel de regels:

```bash
wc -l CLAUDE.md
```

Trim indien nodig — technische context (Booking engine, Git workflow, Foto's) blijft, alles wat nu in de skill staat gaat eruit.

- [ ] **Stap 5: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: slim down CLAUDE.md, delegate build process to asteria-lander skill"
```

---

## Task 5: Eindverificatie

- [ ] **Stap 1: Check alle bestanden aanwezig**

```bash
ls hotel-content.md foto-index.md CLAUDE.md
```

- [ ] **Stap 2: Check CLAUDE.md lengte**

```bash
wc -l CLAUDE.md
```

Verwacht: onder 200 regels.

- [ ] **Stap 3: Check skill geladen**

Open een nieuw gesprek en typ: "bouw een Asteria landingspagina". Verificeer dat de `asteria-lander` skill automatisch triggert en Stap 0 als eerste stap toont.

- [ ] **Stap 4: Push naar main**

```bash
git push origin main
```
