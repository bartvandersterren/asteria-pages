# Asteria Pages — Claude Instructies

Dit is de repository voor landingspagina's op visit.asteria.nl.

Elke pagina wordt gebouwd via een **verplicht 7-stappen proces**. Geen stap overslaan. Geen stap samenvoegen. Elke stap afronden met de gebruiker voor je verdergaat.

Maak bij aanvang taken aan met TaskCreate voor elke stap.

---

## STAP 1 — BRIEF

Stel de volgende vragen. Wacht op antwoord. Ga niet verder zonder antwoord op minimaal 1, 2 en 3.

1. **Doel** — Wat is het doel van deze pagina?
2. **CTA** — Wat is de primaire actie die de bezoeker moet nemen?
3. **Doelgroep** — Wie is de bezoeker?
4. **Verkeersbron** — Waar komt het verkeer vandaan?
5. **URL** — Wat wordt de slug? (bv. `moederdag` → visit.asteria.nl/moederdag)
6. **Deadline** — Wanneer moet de pagina live?

Vat de brief samen in 3 zinnen en vraag bevestiging.

---

## STAP 2 — STRUCTUUR

Stel op basis van de brief een blokkenstructuur voor. Gebruik alleen deze bewezen bloktypen:

- **Hero** — grote kop, subkop, CTA-knop, achtergrondafbeelding
- **USP balk** — 3 korte voordelen met icoon of vinkje
- **Intro tekst** — korte beschrijving / context
- **Cards grid** — 2 of 3 kaarten (arrangementen, kamers, etc.)
- **Afbeelding blok** — breed beeld met tekst overlay of naast tekst
- **Review / testimonial** — 1 citaat + sterren
- **Nieuwsbrief / lead capture** — e-mail input + CTA
- **Footer CTA** — laatste kans, prominente knop
- **Sticky header** — altijd aanwezig

Schrijf de volgorde als genummerde lijst. Vraag bevestiging.

---

## STAP 3 — COPY

Schrijf per blok de exacte copy:
- Koptekst (H1 of H2)
- Subkop of bodytekst (max 2-3 zinnen)
- CTA-knoptekst

Stijlregels (zie `tone-of-voice.md` voor volledig overzicht):
- Altijd "u" — nooit "je" of "jij"
- Warm en gastvrij, nuchter Limburgs — geen superlatieven, geen marketingjargon
- Concreet: noem prijzen, tijden, locatie (Venray, Noord-Limburg, Maasduinen)
- Korte actieve zinnen
- Kopteksten in uppercase (Electrolize font)
- CTA's actiegericht: "Boek nu", "Bekijk arrangementen" — niet "Klik hier"

Vraag bevestiging op de copy voor je verdergaat.

---

## STAP 4 — GRAFISCH

De basis staat vast in `brand.css`. Stel per pagina alleen vast wat afwijkt:

- Eigen accentkleur of campagnekleur? (standaard rood `#c23435`)
- Specifieke afbeeldingen beschikbaar?
- Hero-afbeelding beschikbaar?
- Afwijkende H1-grootte? (standaard 30px)

Leg de grafische keuzes vast als commentaar bovenaan het HTML-bestand.

---

## STAP 5 — BOUWEN

Technische vereisten — geen uitzonderingen:

- [ ] Één `.html` bestand — bestandsnaam = slug (bv. `moederdag.html`)
- [ ] `brand.css` geladen vóór eigen styles
- [ ] Google Fonts embed aanwezig (Electrolize + Montserrat)
- [ ] Logo geladen van `https://www.asteria.nl/images/logo-hotel-asteria.png`
- [ ] Sticky header met navigatie en "Boek nu" knop
- [ ] Alle blokken uit de goedgekeurde structuur aanwezig
- [ ] Alle copy verwerkt — geen placeholder teksten
- [ ] Alle afbeeldingen hebben `alt`-tekst
- [ ] `<meta charset>`, `<meta viewport>` en `<title>` aanwezig

Bouw blok voor blok. Na elk blok bevestigen voor je verdergaat.

---

## STAP 6 — QA

Open de pagina en loop elk punt af:

**Visueel**
- [ ] Heading font is Electrolize, staat in uppercase
- [ ] Body font is Montserrat
- [ ] Rode CTA-knop heeft kleur `#c23435`
- [ ] Logo niet afgerond (geen border-radius op logo img)
- [ ] Kaarten hebben border-radius 8px
- [ ] Content afbeeldingen hebben border-radius 20px (`.img--rounded`)

**Responsief (375px)**
- [ ] Teksten leesbaar op mobile
- [ ] Knoppen minstens 44px hoog
- [ ] Hero-afbeelding schaalt correct

**Functioneel**
- [ ] Geen dode links (`href="#"`) in finale versie
- [ ] CTA-knop zichtbaar op elke scroll-positie
- [ ] Formulieren hebben een `action` of zijn verbonden

**Performance**
- [ ] Geen blokkerende externe scripts
- [ ] Afbeeldingen hebben `loading="lazy"` (behalve hero)

Fix gevonden problemen. Herhaal check na fixes.

---

## STAP 7 — DEPLOY

- [ ] Bestand opgeslagen als `[slug].html` in de root van deze repo
- [ ] Commit met duidelijke message (bv. `add moederdag landing page`)
- [ ] Gepusht naar `main` branch
- [ ] Cloudflare Pages deploy gecontroleerd
- [ ] Pagina live getest op `visit.asteria.nl/[slug]`

Na deploy: URL doorgeven.

---

## Overzicht

| # | Stap | Output | Wacht op bevestiging? |
|---|------|--------|----------------------|
| 1 | Brief | Samenvatting in 3 zinnen | Ja |
| 2 | Structuur | Genummerde blokkenlijst | Ja |
| 3 | Copy | Tekst per blok | Ja |
| 4 | Grafisch | Afwijkingen t.o.v. brand.css | Ja |
| 5 | Bouwen | HTML bestand | Per blok |
| 6 | QA | Afgevinkte checklist | Nee |
| 7 | Deploy | Live URL | Nee |

---

## Technische context

- **Repo:** github.com/bartvandersterren/asteria-pages
- **Lokale clone:** ~/Projects/asteria-pages/ — dit is de enige werkdirectory
- **Hosting:** Cloudflare Pages → auto-deploy op push naar `main`
- **Subdomain:** visit.asteria.nl (CNAME → asteria-pages.pages.dev)
- **Brand:** `brand.css` in root van deze repo
- **Logo:** https://www.asteria.nl/images/logo-hotel-asteria.png (90×104px)
- **Primaire kleur:** `#c23435`
- **Fonts:** Electrolize (headings) + Montserrat 300/400/700 (body)

## Git workflow

- GitHub token (bartvandersterren): zie ~/.claude/projects/.../memory/reference_github_token.md
- Push naar main → Cloudflare deployt automatisch (geen extra stap)
- git config: user.email = bart@vandersterrenhotels.nl, user.name = Bart van der Sterren

## Booking engine

- Bestanden: boeken.html, boeken-stap1-3.html
- Backend: functions/mews/[[path]].js (Mews proxy) + functions/api/session.js (KV session)
- KV binding: ASTERIA_KV (gekoppeld aan Cloudflare Pages, namespace_id: 0b06387ff7724995b0e287df3f0c5cb0)
- Session injecteren: POST https://visit.asteria.nl/api/session met {"session":"<token>","client":"Mews Distributor 5656.0.0"}
- Mews IDs: configId 9fc01bd9-bc04-49f2-83cf-b44400835224 | enterpriseId 65a522c9-4828-413d-9ad8-af1d00ffb83f

## Foto's

- fotos/ in repo = geselecteerde foto's (semantisch benoemd, ~17 stuks)
- ~/Documents/Asteria Fotobank/ = volledig archief (318MB, 800 foto's) — niet in git
