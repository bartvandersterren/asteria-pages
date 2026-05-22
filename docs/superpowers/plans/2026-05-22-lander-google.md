# lander-google.html Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bouw `lander-google.html` — een algemene Google Ads landingspagina voor Hotel Asteria, gefocust op directe kamerboeking, gebaseerd op de bestaande `wellness-arr-c.html`.

**Architecture:** Fork van `wellness-arr-c.html`. Wellness-arrangement-specifieke secties worden verwijderd. Twee nieuwe blokken worden toegevoegd (USP, Sfeer). Alle bewezen JS-IIFEs (datepicker, booking popup, kamertypes, email capture) blijven intact.

**Tech Stack:** Vanilla HTML/CSS/JS, geen build tool, geen framework. Cloudflare Pages (auto-deploy op push naar `main`). Verificatie via Playwright screenshots + live URL.

---

## Referentie

- **Spec:** `docs/superpowers/specs/2026-05-22-lander-google-design.md`
- **Basis:** `wellness-arr-c.html` (live op `visit.asteria.nl/wellness-arr-c`)
- **Design tokens:** `brand.css`
- **Visuele stijl:** `design-dna.md` — lezen vóór elke bouwtaak
- **Foto's:** `foto-index.md` + `fotos/` in repo
- **Hotelfeiten:** `hotel-content.md`
- **Schrijfstijl:** `tone-of-voice.md` — altijd "u/uw", geen em dashes, geen superlatieven
- **Mews distributor ID:** `6dc9094c-76e3-4fd8-83a7-af1d00ffc556`

---

## Verificatieworkflow (elke sessie)

Na elke sessie:
```bash
cd /Users/bartvandersterren/Projects/asteria-pages
git add lander-google.html
git commit -m "..."
git push
# wacht ~35 seconden
# check: https://visit.asteria.nl/lander-google
```

Playwright screenshot (mobile 375×812):
```js
// in browser_run_code_unsafe:
await page.setViewportSize({ width: 375, height: 812 });
await page.goto('https://visit.asteria.nl/lander-google');
// dan browser_take_screenshot
```

---

## Task 1: Strippen

**Sessie:** 1
**Files:**
- Create: `lander-google.html` (kopie van `wellness-arr-c.html`)

### Wat eruit gaat

De volgende secties volledig verwijderen uit de HTML:

1. **Wellness-arrangement-blok** (`arr-c` sectie) — de grote kaart met foto-carousel, features, prijs en boek-CTA. Herkenbaar aan `class="arr-c"` of vergelijkbaar.
2. **Wellness plattegrond + hotspot-blok** — de sectie met `WP_ZONES`, hotspot-pins en de modal/drawer. Herkenbaar aan `id="wellness-plattegrond"` of `WP_ZONES`.
3. **Diner-blok** — de sectie over het restaurant/diner. Herkenbaar aan "diner" in class of id.
4. **A/B price split logica** — de code die `variant` bepaalt op basis van `Math.random()` en de voucher kiest tussen WELLNESSARRA en WELLNESS124. De `track()` IIFE zelf mag blijven.
5. **Voucher codes** — alle voorkomens van `WELLNESSARRA` en `WELLNESS124` in deeplink-opbouw verwijderen. Vervangen door deeplink zonder `mewsVoucherCode` param.

### Stappen

- [ ] **Stap 1: Kopieer het bestand**

```bash
cp /Users/bartvandersterren/Projects/asteria-pages/wellness-arr-c.html \
   /Users/bartvandersterren/Projects/asteria-pages/lander-google.html
```

- [ ] **Stap 2: Verwijder wellness-arrangement-blok**

Zoek in `lander-google.html` naar de sectie die begint met `arr-c` (arrangement-kaart). Verwijder de volledige HTML-sectie, inclusief de bijbehorende `<style>` regels in de `<head>` die exclusief voor dit blok zijn.

- [ ] **Stap 3: Verwijder wellness plattegrond + hotspot-blok**

Zoek naar `WP_ZONES` in het bestand. Verwijder de volledige sectie-HTML én het bijbehorende script-blok met de `WP_ZONES` array en hotspot-logica.

- [ ] **Stap 4: Verwijder diner-blok**

Zoek naar de diner-sectie. Verwijder de volledige HTML-sectie.

- [ ] **Stap 5: Verwijder A/B price split**

Zoek naar `WELLNESSARRA` en `WELLNESS124`. Verwijder de variant-logica. Pas `buildBookingUrl()` aan zodat deze geen `mewsVoucherCode` parameter meer toevoegt:

```js
function buildBookingUrl(checkin, checkout, roomKey) {
  const base = 'https://app.mews.com/distributor/6dc9094c-76e3-4fd8-83a7-af1d00ffc556';
  let url = base;
  if (checkin && checkout) {
    url += `?mewsStart=${checkin}&mewsEnd=${checkout}`;
    if (roomKey && ROOMS[roomKey]) {
      url += `&mewsRoute=rates&mewsRoom=${ROOMS[roomKey].categoryId}`;
    } else {
      url += `&mewsRoute=rooms`;
    }
  }
  return url;
}
```

- [ ] **Stap 6: Pas canonical URL aan**

Vervang `https://visit.asteria.nl/wellness-arr-c` door `https://visit.asteria.nl/lander-google` in de canonical tag en OG-tags.

- [ ] **Stap 7: Verificeer dat de pagina laadt zonder JS-fouten**

Open `lander-google.html` lokaal in browser (of push en check live). Controleer browser console op fouten.

- [ ] **Stap 8: Commit en push**

```bash
cd /Users/bartvandersterren/Projects/asteria-pages
git add lander-google.html
git commit -m "feat: lander-google — strip wellness-specifieke secties"
git push
```

- [ ] **Stap 9: Verificeer live**

Wacht 35 seconden. Check `https://visit.asteria.nl/lander-google`. Verwacht: pagina toont hero + kamertypes + booking popup + email capture + footer. Geen JS-fouten.

---

## Task 2: Hero aanpassen

**Sessie:** 2
**Files:**
- Modify: `lander-google.html` — hero-sectie + trust badges + sticky CTA

### Context

De huidige hero is wellness-gefocust: wellness-foto, wellness-tekst, "Boek het Wellness Arrangement" CTA. Dit wordt generiek hotel.

Raadpleeg `foto-index.md` voor een geschikte hero-foto (exterieur of sfeer, niet wellness-specifiek). De meest voor de hand liggende kandidaten zijn exterieur-foto's of lobby/interieur shots.

### Stappen

- [ ] **Stap 1: Lees design-dna.md en foto-index.md**

```bash
# lees beide bestanden vóór je begint
```

- [ ] **Stap 2: Kies hero-foto**

Selecteer een foto uit `fotos/` op basis van `foto-index.md`. Geschikte categorieën: Exterieur, Lobby, of algemene sfeer. Geen wellness-bad of sauna als hero.

- [ ] **Stap 3: Pas hero-foto aan**

Vervang de `src` van de hero-afbeelding én de preload-link in de `<head>`:

```html
<!-- in <head> -->
<link rel="preload" as="image" href="fotos/[GEKOZEN_FOTO].webp" type="image/webp">

<!-- in hero -->
<img src="fotos/[GEKOZEN_FOTO].webp" alt="Hotel Asteria Venray" ...>
```

- [ ] **Stap 4: Pas hero headline en subline aan**

Huidige wellness-copy vervangen door hotel-first copy. Raadpleeg `tone-of-voice.md` en `hotel-content.md`. Schrijfstijl: "u/uw", geen em dashes, geen superlatieven. Concreet en down-to-earth.

Richtlijn voor headline: max 8 woorden, hotel-naam of locatie centraal.
Richtlijn voor subline: max 15 woorden, één concrete belofte (comfort, ligging, faciliteiten).

- [ ] **Stap 5: Pas trust badges aan**

Huidige badges zijn wellness-specifiek ("Inclusief 2 uur wellness", etc.). Vervangen door generieke hotel USPs. Raadpleeg `hotel-content.md` voor feiten:
- Bijv. Google rating (4,2/5 · 2.219 reviews)
- Bijv. "Gratis parkeren"
- Bijv. "Wellness op de Top Floor"

- [ ] **Stap 6: Pas sticky CTA tekst aan**

"Boek het Wellness Arrangement" → "Boek uw verblijf"

- [ ] **Stap 7: Controleer mobile layout**

Playwright screenshot mobile (375×812). Controleer dat headline niet afkapt, trust badges netjes wrappen.

- [ ] **Stap 8: Commit en push**

```bash
git add lander-google.html
git commit -m "feat: lander-google — hero generiek gemaakt"
git push
```

---

## Task 3: USP-blok bouwen

**Sessie:** 3
**Files:**
- Modify: `lander-google.html` — nieuw blok invoegen direct ná hero

### Context

Dit blok beantwoordt de vraag "waarom Hotel Asteria?". Drie pijlers: locatie, faciliteiten, sfeer/service. Raadpleeg `design-dna.md` voor visuele stijl. Raadpleeg `hotel-content.md` voor feiten.

### Structuur

3-koloms grid op desktop, gestapeld op mobile. Per kolom: icoon (inline SVG) + titel + 2-3 regels tekst. Achtergrond: `#f8f7f5` (lichte tint, zoals het plattegrond-blok). Max-width 1200px, padding 80px desktop / 48px mobile.

### Stappen

- [ ] **Stap 1: Lees design-dna.md en hotel-content.md**

- [ ] **Stap 2: Schrijf de HTML voor het USP-blok**

Voeg in na de hero-sectie, vóór het kamertypes-blok:

```html
<section class="usp-blok">
  <div class="usp-inner">
    <div class="usp-grid">

      <div class="usp-item">
        <div class="usp-icon">
          <!-- inline SVG locatie/pin icoon -->
        </div>
        <h3 class="usp-titel">[TITEL LOCATIE]</h3>
        <p class="usp-tekst">[TEKST LOCATIE — max 2 zinnen, concreet]</p>
      </div>

      <div class="usp-item">
        <div class="usp-icon">
          <!-- inline SVG faciliteiten icoon -->
        </div>
        <h3 class="usp-titel">[TITEL FACILITEITEN]</h3>
        <p class="usp-tekst">[TEKST FACILITEITEN — max 2 zinnen]</p>
      </div>

      <div class="usp-item">
        <div class="usp-icon">
          <!-- inline SVG sfeer/ster icoon -->
        </div>
        <h3 class="usp-titel">[TITEL SFEER]</h3>
        <p class="usp-tekst">[TEKST SFEER — max 2 zinnen]</p>
      </div>

    </div>
  </div>
</section>
```

- [ ] **Stap 3: Schrijf de CSS voor het USP-blok**

Voeg toe in de `<style>` sectie:

```css
.usp-blok {
  background: #f8f7f5;
  padding: 80px 24px;
}
.usp-inner {
  max-width: 1200px;
  margin: 0 auto;
}
.usp-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 48px;
}
.usp-item {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 16px;
}
.usp-icon {
  width: 48px;
  height: 48px;
  color: #c23435;
}
.usp-icon svg {
  width: 100%;
  height: 100%;
}
.usp-titel {
  font-family: 'Electrolize', sans-serif;
  font-size: 1.1rem;
  color: #1a1a1a;
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.usp-tekst {
  font-family: 'Montserrat', sans-serif;
  font-size: 0.95rem;
  font-weight: 300;
  color: #4a4a4a;
  line-height: 1.7;
  margin: 0;
}
@media (max-width: 768px) {
  .usp-blok { padding: 48px 16px; }
  .usp-grid {
    grid-template-columns: 1fr;
    gap: 32px;
  }
}
```

- [ ] **Stap 4: Vul copy in**

Raadpleeg `hotel-content.md` en `tone-of-voice.md`. Schrijf de drie USPs concreet:
- Locatie: Maasheseweg 80a Venray, bosrijke omgeving Noord-Limburg
- Faciliteiten: wellness (sauna's, 300m²), restaurant/brasserie, parkeren
- Sfeer: hotelsfeer, reviews (4,2/5)

Gebruik "u/uw", geen em dashes.

- [ ] **Stap 5: Controleer desktop en mobile layout**

Playwright screenshots op 1280×800 en 375×812.

- [ ] **Stap 6: Commit en push**

```bash
git add lander-google.html
git commit -m "feat: lander-google — USP-blok toegevoegd"
git push
```

---

## Task 4: Sfeerblok bouwen

**Sessie:** 4
**Files:**
- Modify: `lander-google.html` — nieuw blok invoegen ná USP-blok, vóór kamertypes

### Context

Foto-gedreven blok met drie thema's: hotel/interieur, wellness (licht), omgeving + restaurant. Raadpleeg `foto-index.md` voor fotoselectie. Raadpleeg `design-dna.md` voor visuele stijl. Geen tekst-zwaar blok — foto's dragen het verhaal.

### Structuur

Drie kaarten naast elkaar op desktop (of 2+1 layout), gestapeld op mobile. Elke kaart: grote foto (aspect-ratio 3:4 of 4:5) + label onderaan. Achtergrond: wit.

### Stappen

- [ ] **Stap 1: Lees design-dna.md en foto-index.md**

- [ ] **Stap 2: Selecteer drie foto's**

Uit `fotos/`:
- Thema 1 (hotel/interieur): lobby, kamer, of sfeer-interieur
- Thema 2 (wellness): één wellness-foto (bad, sauna-sfeer — niet te wellness-heavy)
- Thema 3 (omgeving/restaurant): exterieur natuur, of brasserie-shot

- [ ] **Stap 3: Schrijf HTML voor het sfeerblok**

Voeg in na het USP-blok:

```html
<section class="sfeer-blok">
  <div class="sfeer-inner">
    <div class="sfeer-grid">

      <div class="sfeer-item">
        <div class="sfeer-foto-wrap">
          <img src="fotos/[FOTO_1].webp" alt="[ALT_1]" loading="lazy">
        </div>
        <p class="sfeer-label">[LABEL 1 — max 4 woorden]</p>
      </div>

      <div class="sfeer-item">
        <div class="sfeer-foto-wrap">
          <img src="fotos/[FOTO_2].webp" alt="[ALT_2]" loading="lazy">
        </div>
        <p class="sfeer-label">[LABEL 2]</p>
      </div>

      <div class="sfeer-item">
        <div class="sfeer-foto-wrap">
          <img src="fotos/[FOTO_3].webp" alt="[ALT_3]" loading="lazy">
        </div>
        <p class="sfeer-label">[LABEL 3]</p>
      </div>

    </div>
  </div>
</section>
```

- [ ] **Stap 4: Schrijf CSS voor het sfeerblok**

```css
.sfeer-blok {
  background: #fff;
  padding: 80px 24px;
}
.sfeer-inner {
  max-width: 1200px;
  margin: 0 auto;
}
.sfeer-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}
.sfeer-item {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.sfeer-foto-wrap {
  aspect-ratio: 3/4;
  overflow: hidden;
  border-radius: 12px;
}
.sfeer-foto-wrap img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.sfeer-label {
  font-family: 'Electrolize', sans-serif;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: #4a4a4a;
  margin: 0;
}
@media (max-width: 768px) {
  .sfeer-blok { padding: 48px 16px; }
  .sfeer-grid {
    grid-template-columns: 1fr;
    gap: 24px;
  }
  .sfeer-foto-wrap {
    aspect-ratio: 4/3;
  }
}
```

- [ ] **Stap 5: Controleer desktop en mobile layout**

Playwright screenshots 1280×800 en 375×812. Controleer dat foto's scherp laden en aspect-ratio klopt.

- [ ] **Stap 6: Commit en push**

```bash
git add lander-google.html
git commit -m "feat: lander-google — sfeerblok toegevoegd"
git push
```

---

## Task 5: Kamertypes aanpassen

**Sessie:** 5
**Files:**
- Modify: `lander-google.html` — kamertypes IIFE + popup copy

### Context

Het kamertypes-blok is al grotendeels generiek. Kleine aanpassingen nodig: CTA-tekst en eventuele arrangement-verwijzingen in de popup.

### Stappen

- [ ] **Stap 1: Zoek alle arrangement-verwijzingen in het kamertypes-blok**

Gebruik Grep op `lander-google.html` voor termen als "arrangement", "wellness", "WELLNESS".

- [ ] **Stap 2: Pas CTA-tekst aan in kamertypes-kaarten**

Zoek naar de CTA-knop per kamerkaart. Vervang arrangement-specifieke tekst door generiek:
- "Boek dit arrangement" → "Bekijk kamer" of "Selecteer kamer"
- "Inclusief wellness" → verwijderen indien aanwezig

- [ ] **Stap 3: Pas kamer-popup copy aan**

In de popup die opent bij het klikken op een kamer: verwijder verwijzingen naar het wellness arrangement. De popup toont kamernaam, foto, features en een boek-CTA. CTA-tekst: "Boek deze kamer".

- [ ] **Stap 4: Controleer dat de booking flow nog werkt**

Open pagina live → klik op een kamerkaart → kies datum → selecteer kamer → controleer dat de Mews-deeplink geen `mewsVoucherCode` bevat.

- [ ] **Stap 5: Commit en push**

```bash
git add lander-google.html
git commit -m "feat: lander-google — kamertypes copy generiek"
git push
```

---

## Task 6: Booking popup aanpassen

**Sessie:** 6
**Files:**
- Modify: `lander-google.html` — booking popup IIFE, stap-titels, deeplink-opbouw

### Context

De booking popup heeft nog wellness-taal in stap-titels en copy. Voucher is al verwijderd in Task 1. Deze sessie focust op copy-aanpassingen in de popup zelf.

### Stappen

- [ ] **Stap 1: Zoek alle wellness-verwijzingen in de booking popup IIFE**

Grep op "wellness", "arrangement", "WELLNESS" binnen het popup-script.

- [ ] **Stap 2: Pas stap-titels aan**

- Stap 1 titel: "Wanneer wilt u verblijven?" (of equivalent — neutraal)
- Stap 2 titel: "Kies uw kamer"
- Stap 3 titel: "Kamerdetails"

- [ ] **Stap 3: Pas overige popup-copy aan**

Controleer intro-tekst, sublines, en button-labels. Alles generiek maken. "Boek uw verblijf" als primaire CTA.

- [ ] **Stap 4: Verifieer de volledige boekflow**

Desktop én mobile doorlopen:
1. Klik sticky CTA → popup opent
2. Kies datum → ga naar stap 2
3. Kies kamer → ga naar stap 3 (of deeplink direct)
4. Controleer gegenereerde Mews-URL: geen `mewsVoucherCode` aanwezig

- [ ] **Stap 5: Commit en push**

```bash
git add lander-google.html
git commit -m "feat: lander-google — booking popup copy generiek"
git push
```

---

## Task 7: Email capture + footer aanpassen

**Sessie:** 7
**Files:**
- Modify: `lander-google.html` — email capture sectie, footer

### Context

**Email capture:** De offer blijft wellness-gefocust (intentioneel — werkt als upsell). Alleen technische of layout-aanpassingen indien nodig. Geen inhoudelijke copy-wijzigingen in de offer zelf.

**Footer:** Controleer op arrangement-specifieke verwijzingen. Adres is correct: Maasheseweg 80a, 5804 AD Venray.

### Stappen

- [ ] **Stap 1: Controleer email capture op arrangement-verwijzingen buiten de offer**

Bijv. in de sectie-heading boven het formulier. Als er staat "Boek het Wellness Arrangement + ontvang..." mag dat blijven (dat is de offer). Als er een aparte intro staat die arrangement-specifiek is en niet over de offer gaat, aanpassen.

- [ ] **Stap 2: Controleer footer op wellness-verwijzingen**

Grep op "wellness", "arrangement" in het footer-blok. Verwijder of generaliseer waar van toepassing.

- [ ] **Stap 3: Controleer adres in footer**

Adres moet zijn: `Maasheseweg 80a, 5804 AD Venray` (niet Leunseweg of andere variant).

- [ ] **Stap 4: Commit en push**

```bash
git add lander-google.html
git commit -m "feat: lander-google — footer opgeschoond"
git push
```

---

## Task 8: Polish

**Sessie:** 8
**Files:**
- Modify: `lander-google.html` — meta-tags, copy-review, tracking

### Stappen

- [ ] **Stap 1: Copy-review volledige pagina**

Grep op:
- `em dash` (`—` / `–`) in zichtbare tekst → vervangen door punt, komma of middot
- Superlatieven ("beste", "unieke", "perfecte") → verwijderen of vervangen
- "je/jij/jou" → vervangen door "u/uw"
- Arrangement-verwijzingen die eerder zijn gemist

- [ ] **Stap 2: SEO meta aanpassen**

```html
<title>Hotel Asteria Venray — Officiële Website | Boek direct</title>
<meta name="description" content="Overnacht in Hotel Asteria in Venray. [CONCREET: kamers, wellness, restaurant, ligging]. Boek direct en profiteer van de beste prijs.">
```

Canonical: `https://visit.asteria.nl/lander-google`

- [ ] **Stap 3: OG-afbeelding aanpassen**

Vervang de wellness-hero in de OG-tag door de algemene hero-foto die in Task 2 gekozen is:

```html
<meta property="og:image" content="https://visit.asteria.nl/fotos/[GEKOZEN_HERO_FOTO].webp">
```

- [ ] **Stap 4: Tracking controleren**

Controleer dat `track()` IIFE aanwezig is en werkt. Controleer dat er geen dubbele GA4- of pixel-snippets zijn binnengeslopen.

- [ ] **Stap 5: Volledige mobile check via Playwright**

Screenshot van elk blok op 375×812:
1. Hero (above the fold)
2. USP-blok
3. Sfeerblok
4. Kamertypes
5. Email capture
6. Footer

- [ ] **Stap 6: Volledige desktop check via Playwright**

Screenshots op 1280×800 van dezelfde blokken.

- [ ] **Stap 7: Eindcommit**

```bash
git add lander-google.html
git commit -m "feat: lander-google — polish, meta, copy-review afgerond"
git push
```
