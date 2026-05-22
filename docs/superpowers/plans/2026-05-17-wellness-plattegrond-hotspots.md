# Wellness Plattegrond Hotspots — Implementatieplan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Voeg een fullscreen interactieve wellness-plattegrond toe aan `wellness-arr-c.html`, waarbij gasten op hotspot-pins tikken voor een popup met foto, naam, specs en omschrijving per ruimte.

**Architecture:** Eén `<section>` in `wellness-arr-c.html` met een achtergrondafbeelding (plattegrond illustratie) en absoluut gepositioneerde hotspot-pins. Op mobile: bottom drawer. Op desktop (≥900px): side panel rechts. Alle zone-data staat in één JS-array in de pagina, die zowel de pins als de popup-content aantuurt.

**Tech Stack:** Vanilla HTML/CSS/JS. Geen externe dependencies. Foto's als lokale WebP-bestanden. Playwright voor mobile QA.

---

## Bestandsoverzicht

| Actie | Bestand | Verantwoordelijkheid |
|-------|---------|----------------------|
| Modify | `wellness-arr-c.html` | Nieuwe sectie, CSS en JS toevoegen |
| Add | `fotos/wellness-plattegrond-illustratie.webp` | AI-illustratie (placeholder: `wellness-plattegrond.png`) |
| Add | `fotos/wellness-sauna-fins.webp` | Foto Finse sauna (uit fotobank) |
| Add | `fotos/wellness-sauna-bio.webp` | Foto bio sauna |
| Add | `fotos/wellness-sauna-zoutsteen.webp` | Foto zoutsteen sauna |
| Add | `fotos/wellness-sauna-infrarood.webp` | Foto infrarood sauna |
| Add | `fotos/wellness-infrarood.webp` | Foto aparte infrarood sauna |
| Add | `fotos/wellness-ijsbad.webp` | Foto ijz-/dompelbad |
| Add | `fotos/wellness-kruidenbad.webp` | Foto kruidenbad |
| Add | `fotos/wellness-voetenbad.webp` | Foto voetenbaden |
| Add | `fotos/wellness-stoomdouche.webp` | Foto stoomdouche |
| Add | `fotos/wellness-belevingsdouche.webp` | Foto belevingsdouche |
| Add | `fotos/wellness-gym.webp` | Foto gym/fitness |
| Add | `fotos/wellness-lounge.webp` | Foto lounge/ruimte |

> **Foto-noot:** Voor zones zonder eigen foto tijdelijk `fotos/wellness-spa.webp` of `fotos/wellness-sauna.webp` als fallback gebruiken. Task 7 vervangt ze.

> **Illustratie-noot:** Gebruik `wellness-plattegrond.png` (technische tekening) als placeholder tijdens bouw. Task 9 vervangt dit met de AI-illustratie en verfijnt pin-posities.

---

## Task 1: Zone-data array definiëren

**Files:**
- Modify: `wellness-arr-c.html` — zones array toevoegen in `<script>` blok onderaan

- [ ] **Stap 1.1: Voeg de zones-array toe in het `<script>` blok**

Zoek in `wellness-arr-c.html` het bestaande `<script>` blok (rond regel 1467). Voeg de array vóór de bestaande JS toe:

```js
// ══ WELLNESS PLATTEGROND — ZONE DATA ══════════════════════════
const WP_ZONES = [
  {
    id: 'sauna-fins',
    naam: 'Finse Sauna',
    label: 'Sauna 1',
    foto: 'fotos/wellness-sauna.webp',
    omschrijving: 'De klassieke Finse sauna verwarmt het lichaam met droge hitte. Ideaal voor een diepe spier­ontspanning en om de bloedsomloop te stimuleren.',
    specs: [
      { icon: 'temp', tekst: '80–85°C' },
      { icon: 'type', tekst: 'Droge hitte' },
    ],
    pin: { left: 68, top: 42 }
  },
  {
    id: 'sauna-bio',
    naam: 'Bio Sauna',
    label: 'Sauna 2',
    foto: 'fotos/wellness-sauna2.webp',
    omschrijving: 'De bio sauna combineert lagere temperaturen met hoge luchtvochtigheid. Zachter voor de luchtwegen, ideaal als instap­sauna of voor wie het wat milder wil.',
    specs: [
      { icon: 'temp', tekst: '50–60°C' },
      { icon: 'type', tekst: 'Vochtige hitte' },
    ],
    pin: { left: 50, top: 22 }
  },
  {
    id: 'sauna-zoutsteen',
    naam: 'Zoutsteen Sauna',
    label: 'Sauna 3',
    foto: 'fotos/wellness-sauna.webp',
    omschrijving: 'Verlicht met zoutsteenlampen die een warm roze licht verspreiden. Het zout in de lucht heeft een positief effect op de luchtwegen en huid.',
    specs: [
      { icon: 'temp', tekst: '65–70°C' },
      { icon: 'type', tekst: 'Zoutsteen' },
    ],
    pin: { left: 66, top: 22 }
  },
  {
    id: 'sauna-infrarood-groot',
    naam: 'Infrarood Sauna',
    label: 'Sauna 4',
    foto: 'fotos/wellness-sauna2.webp',
    omschrijving: 'Infraroodstraling verwarmt het lichaam van binnenuit zonder de lucht te verhitten. Lager verbruik, hogere penetratie — perfect voor spier­herstel.',
    specs: [
      { icon: 'temp', tekst: '40–50°C' },
      { icon: 'type', tekst: 'Infrarood' },
    ],
    pin: { left: 78, top: 37 }
  },
  {
    id: 'infrarood-sauna',
    naam: 'Infrarood Sauna',
    label: 'Infrarood',
    foto: 'fotos/wellness-spa.webp',
    omschrijving: 'Een compacte infrarood­cabine voor een intensieve opwarming. De zachte stralingswarmte dringt diep door in spieren en gewrichten.',
    specs: [
      { icon: 'temp', tekst: '35–45°C' },
      { icon: 'type', tekst: 'Infrarood' },
    ],
    pin: { left: 35, top: 28 }
  },
  {
    id: 'ijsbad',
    naam: 'IJz-/Dompelbad',
    label: 'Contrast',
    foto: 'fotos/wellness-spa.webp',
    omschrijving: 'Het koude dompelbad na de sauna is het geheim van het contrastbaden. De plotselinge kou stimuleert de bloedsomloop en geeft een energieboost.',
    specs: [
      { icon: 'temp', tekst: '±10°C' },
      { icon: 'type', tekst: 'Koud bad' },
    ],
    pin: { left: 40, top: 38 }
  },
  {
    id: 'kruidenbad',
    naam: 'Kruidenbad',
    label: 'Kruidenbad',
    foto: 'fotos/wellness-spa.webp',
    omschrijving: 'Een warm sfeervol bad met verse kruiden. De geuren en warmte zorgen voor diepe ontspanning van lichaam en geest.',
    specs: [
      { icon: 'temp', tekst: '±38°C' },
      { icon: 'type', tekst: 'Warm bad' },
    ],
    pin: { left: 52, top: 43 }
  },
  {
    id: 'voetenbaden',
    naam: 'Voetenbaden',
    label: '4 bassins',
    foto: 'fotos/wellness-spa.webp',
    omschrijving: 'Vier voetenbaden wisselen warm en koud af. Verwen je voeten na een wandeling of sauna­sessie — reflexpunten worden gestimuleerd, benen voelen lichter.',
    specs: [
      { icon: 'aantal', tekst: '4 bassins' },
      { icon: 'type', tekst: 'Warm & koud' },
    ],
    pin: { left: 48, top: 28 }
  },
  {
    id: 'stoomdouche',
    naam: 'Stoomdouche',
    label: 'Stoom',
    foto: 'fotos/wellness-hero.webp',
    omschrijving: 'Een stoomcabine vol vochtige warmte. De stoom opent poriën, reinigt de huid en ontspant de bovenste luchtwegen. Ideaal na de sauna.',
    specs: [
      { icon: 'temp', tekst: '40–45°C' },
      { icon: 'type', tekst: 'Stoom' },
    ],
    pin: { left: 27, top: 50 }
  },
  {
    id: 'belevingsdouche',
    naam: 'Belevingsdouche',
    label: 'Ervaring',
    foto: 'fotos/wellness-hero.webp',
    omschrijving: 'Kies je eigen beleving: tropische regen, Scandinavische mist of een verfrissende koude straal. Elke douche is een nieuwe sensatie.',
    specs: [
      { icon: 'type', tekst: 'Regen / Mist / Koud' },
    ],
    pin: { left: 33, top: 50 }
  },
  {
    id: 'gym',
    naam: 'Gym & Fitness',
    label: 'Fitness',
    foto: 'fotos/wellness-hero.webp',
    omschrijving: 'Een moderne fitnessruimte met cardio- en krachtapparatuur. Vrij toegankelijk voor alle hotelgasten — voor een actieve start of afsluiting van de dag.',
    specs: [
      { icon: 'type', tekst: 'Cardio & Kracht' },
    ],
    pin: { left: 18, top: 72 }
  },
  {
    id: 'lounge',
    naam: 'Relaxruimte',
    label: 'Lounge',
    foto: 'fotos/wellness-spa.webp',
    omschrijving: 'De relaxruimte met comfortabele ligbedden biedt uitzicht over de omgeving. Neem de tijd na de sauna — rust is onderdeel van het ritueel.',
    specs: [
      { icon: 'type', tekst: 'Ligbedden' },
    ],
    pin: { left: 64, top: 78 }
  },
];
```

- [ ] **Stap 1.2: Verifieer de array in browser-console**

Open `wellness-arr-c.html` lokaal. Open DevTools console en typ:
```js
WP_ZONES.length
```
Verwacht: `12`

- [ ] **Stap 1.3: Commit**

```bash
git add wellness-arr-c.html
git commit -m "feat: wellness plattegrond — zones data array (12 zones)"
```

---

## Task 2: Sectie HTML + basis CSS

**Files:**
- Modify: `wellness-arr-c.html` — sectie HTML invoegen na reviews-sectie (na regel ~1318), CSS toevoegen in `<style>` blok

- [ ] **Stap 2.1: Voeg de CSS toe in het bestaande `<style>` blok**

Zoek de laatste CSS-sectie vóór `</style>`. Voeg toe:

```css
/* ══════════════════════════════════════════════════════════
   WELLNESS PLATTEGROND
══════════════════════════════════════════════════════════ */
.wp-section {
  position: relative;
  width: 100vw;
  height: 100svh;
  overflow: hidden;
  background: #2a2018;
  margin-left: calc(-50vw + 50%);
}

.wp-section__img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center center;
  display: block;
}

.wp-section__gradient {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    to bottom,
    transparent 40%,
    rgba(20, 12, 6, 0.55) 100%
  );
  pointer-events: none;
  z-index: 1;
}
```

- [ ] **Stap 2.2: Voeg de sectie HTML in na de reviews-sectie**

Zoek in het HTML-gedeelte van `wellness-arr-c.html`:
```html
<!-- ══ FOOTER ════════════════════════════════════════════════ -->
```
Voeg dáarvóór in:

```html
<!-- ══ WELLNESS PLATTEGROND ═══════════════════════════════════ -->
<section class="wp-section" id="wellness-plattegrond" aria-label="Wellness faciliteiten — interactieve plattegrond">
  <img
    class="wp-section__img"
    src="wellness-plattegrond.png"
    alt="Plattegrond van de wellness op de Top Floor van Hotel Asteria"
    loading="lazy"
  >
  <div class="wp-section__gradient"></div>
  <!-- Pins en drawer worden door JS ingevuld (Task 3 & 4) -->
  <div class="wp-pins" id="wp-pins"></div>
</section>
```

- [ ] **Stap 2.3: Visueel verifiëren**

Open `wellness-arr-c.html` in browser. Scroll naar de wellness-sectie. Controleer:
- Sectie vult het volledige viewport (100vw × 100svh)
- Plattegrond afbeelding is zichtbaar
- Gradient is zichtbaar onderaan

- [ ] **Stap 2.4: Commit**

```bash
git add wellness-arr-c.html
git commit -m "feat: wellness plattegrond — sectie HTML + CSS"
```

---

## Task 3: Hotspot-pins

**Files:**
- Modify: `wellness-arr-c.html` — CSS voor pins + JS om pins te renderen

- [ ] **Stap 3.1: Voeg pin CSS toe**

Voeg toe in het `<style>` blok direct na de `.wp-section__gradient` CSS:

```css
/* Pins */
.wp-pins {
  position: absolute;
  inset: 0;
  z-index: 2;
  pointer-events: none;
}

.wp-pin {
  position: absolute;
  pointer-events: auto;
  transform: translate(-50%, -50%);
  cursor: pointer;
  /* Vergroot taptarget naar 44×44px zonder de visuele pin te vergroten */
  padding: 15px;
  margin: -15px;
  background: none;
  border: none;
  border-radius: 50%;
  -webkit-tap-highlight-color: transparent;
}

.wp-pin__dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: #c23435;
  position: relative;
  box-shadow: 0 2px 8px rgba(0,0,0,0.4);
}

.wp-pin__dot::after {
  content: '';
  position: absolute;
  inset: -5px;
  border-radius: 50%;
  background: rgba(194, 52, 53, 0.35);
  animation: wp-pulse 2s ease-in-out infinite;
}

@keyframes wp-pulse {
  0%, 100% { transform: scale(1); opacity: 0.7; }
  50%       { transform: scale(1.5); opacity: 0; }
}

.wp-pin:focus-visible .wp-pin__dot {
  outline: 2px solid #fff;
  outline-offset: 4px;
}
```

- [ ] **Stap 3.2: Voeg pin-render JS toe**

In het `<script>` blok, na de zones-array (Task 1), voeg toe:

```js
function wpRenderPins() {
  const container = document.getElementById('wp-pins');
  if (!container) return;

  WP_ZONES.forEach(function(zone) {
    const btn = document.createElement('button');
    btn.className = 'wp-pin';
    btn.setAttribute('aria-label', zone.naam + ' — tik voor meer info');
    btn.setAttribute('data-zone-id', zone.id);
    btn.style.left = zone.pin.left + '%';
    btn.style.top  = zone.pin.top  + '%';

    btn.innerHTML = '<div class="wp-pin__dot"></div>';
    btn.addEventListener('click', function() { wpOpenPanel(zone.id); });
    container.appendChild(btn);
  });
}

document.addEventListener('DOMContentLoaded', wpRenderPins);
```

- [ ] **Stap 3.3: Visueel verifiëren**

Herlaad de pagina. Controleer:
- 12 rode stippen zichtbaar op de plattegrond
- Stippen pulseren zachtjes
- In DevTools mobile emulatie (375px): stippen zijn tappable

- [ ] **Stap 3.4: Commit**

```bash
git add wellness-arr-c.html
git commit -m "feat: wellness plattegrond — hotspot pins met pulse animatie"
```

---

## Task 4: Mobile drawer

**Files:**
- Modify: `wellness-arr-c.html` — drawer HTML, CSS en JS

- [ ] **Stap 4.1: Voeg drawer HTML toe**

Direct binnen de `<section class="wp-section">`, na `<div class="wp-pins">`:

```html
  <!-- Backdrop -->
  <div class="wp-backdrop" id="wp-backdrop" aria-hidden="true"></div>

  <!-- Drawer (mobile) / Side panel (desktop via CSS) -->
  <div class="wp-panel" id="wp-panel" role="dialog" aria-modal="true" aria-label="Wellness ruimte details" hidden>
    <div class="wp-panel__handle" aria-hidden="true"></div>
    <button class="wp-panel__close" id="wp-panel-close" aria-label="Sluiten">
      <svg width="18" height="18" viewBox="0 0 18 18" fill="none" aria-hidden="true">
        <line x1="2" y1="2" x2="16" y2="16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        <line x1="16" y1="2" x2="2" y2="16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      </svg>
    </button>
    <div class="wp-panel__photo-wrap">
      <img class="wp-panel__photo" id="wp-panel-photo" src="" alt="">
    </div>
    <div class="wp-panel__body">
      <div class="wp-panel__label">Wellness &middot; Top Floor</div>
      <h3 class="wp-panel__title" id="wp-panel-title"></h3>
      <div class="wp-panel__specs" id="wp-panel-specs"></div>
      <p class="wp-panel__desc" id="wp-panel-desc"></p>
    </div>
  </div>
```

- [ ] **Stap 4.2: Voeg drawer CSS toe**

In het `<style>` blok, na de pin CSS:

```css
/* Backdrop */
.wp-backdrop {
  position: absolute;
  inset: 0;
  background: rgba(0,0,0,0);
  z-index: 3;
  transition: background 0.3s;
  pointer-events: none;
}
.wp-backdrop.is-open {
  background: rgba(0,0,0,0.45);
  pointer-events: auto;
}

/* Panel — mobile: drawer vanuit onderkant */
.wp-panel {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: #fff;
  border-radius: 20px 20px 0 0;
  z-index: 4;
  transform: translateY(100%);
  transition: transform 0.35s cubic-bezier(0.32, 0.72, 0, 1);
  max-height: 72svh;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
}
.wp-panel[hidden] { display: none; }
.wp-panel.is-open {
  transform: translateY(0);
  display: block;
}

.wp-panel__handle {
  width: 40px;
  height: 4px;
  background: #ddd;
  border-radius: 2px;
  margin: 12px auto 0;
  flex-shrink: 0;
}

.wp-panel__close {
  position: absolute;
  top: 14px;
  right: 16px;
  background: none;
  border: none;
  cursor: pointer;
  color: #888;
  padding: 4px;
  line-height: 0;
}

.wp-panel__photo-wrap {
  width: 100%;
  height: 200px;
  overflow: hidden;
  margin-top: 8px;
  flex-shrink: 0;
}
.wp-panel__photo {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.wp-panel__body {
  padding: 16px 20px 28px;
}

.wp-panel__label {
  font-family: 'Montserrat', sans-serif;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #c23435;
}

.wp-panel__title {
  font-family: 'Electrolize', sans-serif;
  font-size: 22px;
  color: #1a1a1a;
  margin: 4px 0 12px;
  font-weight: normal;
}

.wp-panel__specs {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 12px;
}

.wp-spec-badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: #f5f0ea;
  color: #444;
  font-family: 'Montserrat', sans-serif;
  font-size: 12px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 20px;
}

.wp-spec-badge svg {
  flex-shrink: 0;
}

.wp-panel__desc {
  font-family: 'Montserrat', sans-serif;
  font-size: 14px;
  font-weight: 300;
  color: #555;
  line-height: 1.65;
  margin: 0;
}
```

- [ ] **Stap 4.3: Voeg SVG icon helper en panel JS toe**

In het `<script>` blok, na `wpRenderPins`:

```js
// SVG iconen voor specs-badges (geen emoji)
var WP_ICONS = {
  temp: '<svg width="13" height="13" viewBox="0 0 13 13" fill="none" aria-hidden="true"><rect x="5.5" y="1" width="2" height="7" rx="1" fill="currentColor"/><circle cx="6.5" cy="10" r="2.5" fill="currentColor"/></svg>',
  type: '<svg width="13" height="13" viewBox="0 0 13 13" fill="none" aria-hidden="true"><circle cx="6.5" cy="6.5" r="5.5" stroke="currentColor" stroke-width="1.5"/><circle cx="6.5" cy="6.5" r="2" fill="currentColor"/></svg>',
  aantal: '<svg width="13" height="13" viewBox="0 0 13 13" fill="none" aria-hidden="true"><circle cx="4" cy="4" r="2" fill="currentColor"/><circle cx="9" cy="4" r="2" fill="currentColor"/><path d="M1 11c0-2.2 1.3-4 3-4h4c1.7 0 3 1.8 3 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>',
};

function wpBuildSpecBadge(spec) {
  var icon = WP_ICONS[spec.icon] || WP_ICONS['type'];
  return '<span class="wp-spec-badge">' + icon + spec.tekst + '</span>';
}

function wpOpenPanel(zoneId) {
  var zone = WP_ZONES.find(function(z) { return z.id === zoneId; });
  if (!zone) return;

  var panel   = document.getElementById('wp-panel');
  var backdrop = document.getElementById('wp-backdrop');
  var photo   = document.getElementById('wp-panel-photo');
  var title   = document.getElementById('wp-panel-title');
  var specs   = document.getElementById('wp-panel-specs');
  var desc    = document.getElementById('wp-panel-desc');

  photo.src = zone.foto;
  photo.alt = zone.naam;
  title.textContent = zone.naam;
  specs.innerHTML = zone.specs.map(wpBuildSpecBadge).join('');
  desc.textContent = zone.omschrijving;

  panel.removeAttribute('hidden');
  // Één frame wachten zodat display:block is verwerkt vóór CSS transition start
  requestAnimationFrame(function() {
    panel.classList.add('is-open');
    backdrop.classList.add('is-open');
    panel.focus();
  });
}

function wpClosePanel() {
  var panel    = document.getElementById('wp-panel');
  var backdrop = document.getElementById('wp-backdrop');
  panel.classList.remove('is-open');
  backdrop.classList.remove('is-open');
  panel.addEventListener('transitionend', function handler() {
    panel.setAttribute('hidden', '');
    panel.removeEventListener('transitionend', handler);
  });
}

document.addEventListener('DOMContentLoaded', function() {
  document.getElementById('wp-panel-close').addEventListener('click', wpClosePanel);
  document.getElementById('wp-backdrop').addEventListener('click', wpClosePanel);

  // Escape toets sluit panel
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') wpClosePanel();
  });
});
```

- [ ] **Stap 4.4: Visueel verifiëren in mobile emulatie**

Open in browser, zet DevTools op 375px breed. Klik een hotspot-pin. Controleer:
- Drawer schuift soepel omhoog
- Foto, label (rood, uppercase), titel (Electrolize), specs-badges en omschrijving zichtbaar
- Kruisje sluit de drawer
- Tap op de backdrop sluit de drawer
- Escape sluit de drawer

- [ ] **Stap 4.5: Commit**

```bash
git add wellness-arr-c.html
git commit -m "feat: wellness plattegrond — mobile drawer met zone-content"
```

---

## Task 5: Desktop zijpaneel (≥900px)

**Files:**
- Modify: `wellness-arr-c.html` — media query CSS + kleine JS aanpassing

- [ ] **Stap 5.1: Voeg desktop CSS toe**

In het `<style>` blok, na de `.wp-panel__desc` CSS:

```css
/* ── Desktop: side panel ── */
@media (min-width: 900px) {
  /* Sectie wordt flex-rij zodat panel naast de kaart past */
  .wp-section {
    display: flex;
  }

  /* Backdrop verdwijnt op desktop — panel staat naast de kaart */
  .wp-backdrop { display: none !important; }

  /* Panel: vaste breedte rechts, hoogte = 100% sectie */
  .wp-panel {
    position: absolute;
    top: 0;
    right: 0;
    bottom: 0;
    left: auto;
    width: 320px;
    max-height: none;
    border-radius: 0;
    transform: translateX(100%);
    transition: transform 0.35s cubic-bezier(0.32, 0.72, 0, 1);
    overflow-y: auto;
    box-shadow: -4px 0 24px rgba(0,0,0,0.25);
  }

  .wp-panel.is-open {
    transform: translateX(0);
  }

  .wp-panel__handle { display: none; }

  .wp-panel__close {
    top: 16px;
    right: 16px;
  }

  .wp-panel__photo-wrap {
    height: 240px;
    margin-top: 0;
  }

  .wp-panel__body {
    padding: 20px 24px 40px;
  }

  .wp-panel__title {
    font-size: 26px;
  }
}
```

- [ ] **Stap 5.2: Visueel verifiëren op desktop breedte**

Zet DevTools op 1200px breed. Klik een hotspot-pin. Controleer:
- Panel schuift in vanuit rechts
- Plattegrond blijft volledig zichtbaar links
- Geen backdrop zichtbaar
- Wisselen van pin vervangt paneel-inhoud (vorig paneel sluit niet — pin-click roept `wpOpenPanel` aan die content overschrijft en panel open houdt)
- Kruisje werkt

- [ ] **Stap 5.3: Commit**

```bash
git add wellness-arr-c.html
git commit -m "feat: wellness plattegrond — desktop side panel (≥900px)"
```

---

## Task 6: Swipe-to-close op mobile

**Files:**
- Modify: `wellness-arr-c.html` — swipe gesture JS toevoegen

- [ ] **Stap 6.1: Voeg swipe-detect toe in `DOMContentLoaded`**

Voeg toe in de bestaande `DOMContentLoaded` listener, na de `keydown` handler:

```js
  // Swipe-down om drawer te sluiten (mobile only)
  var wpPanel = document.getElementById('wp-panel');
  var wpTouchStartY = 0;

  wpPanel.addEventListener('touchstart', function(e) {
    wpTouchStartY = e.touches[0].clientY;
  }, { passive: true });

  wpPanel.addEventListener('touchend', function(e) {
    var deltaY = e.changedTouches[0].clientY - wpTouchStartY;
    if (deltaY > 60) wpClosePanel(); // swipe naar beneden van >60px sluit drawer
  }, { passive: true });
```

- [ ] **Stap 6.2: Verifiëren**

Test op echte iPhone of DevTools touch mode: swipe de drawer naar beneden. Drawer sluit.

- [ ] **Stap 6.3: Commit**

```bash
git add wellness-arr-c.html
git commit -m "feat: wellness plattegrond — swipe-to-close drawer"
```

---

## Task 7: Foto's voorbereiden uit fotobank

**Files:**
- Add: `fotos/wellness-*.webp` — één foto per zone

- [ ] **Stap 7.1: Selecteer foto's per zone uit de fotobank**

Open `~/Documents/Asteria Fotobank/` en zoek foto's voor:
- Finse sauna (warme houten cabin, mensen zittend)
- Bio sauna
- Zoutsteen sauna (roze licht)
- Infrarood sauna
- IJsbad / koud bad
- Kruidenbad
- Voetenbaden
- Stoomdouche / stoomcabine
- Belevingsdouche
- Gym / fitnessruimte
- Lounge / ligbedden

Gebruik `foto-index.md` als selectiehulp. Als er geen specifieke foto voor een zone is, gebruik de beste beschikbare wellnessfoto als fallback.

- [ ] **Stap 7.2: Converteer geselecteerde JPEG's naar WebP**

Per foto (vervang `BRON.jpg` en `wellness-NAAM.webp` met werkelijke namen):

```bash
python3 -c "
from PIL import Image
import os

input_path = os.path.expanduser('~/Documents/Asteria Fotobank/BRON.jpg')
output_path = 'fotos/wellness-NAAM.webp'
img = Image.open(input_path)
# Max 2000px breed
if img.width > 2000:
    ratio = 2000 / img.width
    img = img.resize((2000, int(img.height * ratio)), Image.LANCZOS)
img.save(output_path, 'WEBP', quality=72, method=6)
print(f'Saved: {output_path} ({img.width}x{img.height})')
"
```

- [ ] **Stap 7.3: Update zones-array met correcte fotopaden**

In de `WP_ZONES` array (Task 1): vervang alle tijdelijke `fotos/wellness-spa.webp` fallbacks met de echte bestandsnamen.

- [ ] **Stap 7.4: Visueel verifiëren**

Klik alle 12 hotspots. Elke drawer/panel toont de juiste eigen foto.

- [ ] **Stap 7.5: Commit**

```bash
git add fotos/wellness-*.webp wellness-arr-c.html
git commit -m "feat: wellness plattegrond — zone foto's per ruimte"
```

---

## Task 8: Mobile QA met Playwright

**Files:**
- Geen nieuwe bestanden — alleen verificatie

- [ ] **Stap 8.1: Playwright test op 375px**

```js
// In een tijdelijk testscript of via MCP Playwright:
await page.setViewportSize({ width: 375, height: 812 });
await page.goto('http://localhost:PORT/wellness-arr-c.html'); // of live URL
// Scroll naar wellness sectie
await page.evaluate(() => {
  document.getElementById('wellness-plattegrond').scrollIntoView();
});
await page.screenshot({ path: 'qa-wp-375-overview.png', fullPage: false });
```

Controleer op screenshot:
- Sectie vult exact 100svh
- Plattegrond zichtbaar
- Minimaal 4 hotspot-pins zichtbaar

- [ ] **Stap 8.2: Test drawer openen op 375px**

```js
await page.setViewportSize({ width: 375, height: 812 });
// Klik de Gym pin (linksonder, relatief goed zichtbaar)
const gymPin = page.locator('[data-zone-id="gym"]');
await gymPin.tap();
await page.waitForTimeout(400); // wacht op animatie
await page.screenshot({ path: 'qa-wp-375-drawer.png', fullPage: false });
```

Controleer: drawer zichtbaar, foto laadt, titel en specs zichtbaar.

- [ ] **Stap 8.3: Test op 430px (iPhone Pro Max)**

Herhaal stap 8.1–8.2 met `width: 430`.

- [ ] **Stap 8.4: Test desktop side panel op 1200px**

```js
await page.setViewportSize({ width: 1200, height: 800 });
await page.evaluate(() => {
  document.getElementById('wellness-plattegrond').scrollIntoView();
});
const sauna1Pin = page.locator('[data-zone-id="sauna-fins"]');
await sauna1Pin.click();
await page.waitForTimeout(400);
await page.screenshot({ path: 'qa-wp-desktop-panel.png', fullPage: false });
```

Controleer: side panel zichtbaar rechts, plattegrond links volledig zichtbaar.

---

## Task 9: AI-illustratie swappen (wanneer beschikbaar)

> **Voer deze task uit nadat de AI-illustratie is gegenereerd in de subsessie.**

**Files:**
- Add: `fotos/wellness-plattegrond-illustratie.webp`
- Modify: `wellness-arr-c.html` — img src + pin posities

- [ ] **Stap 9.1: Converteer AI-illustratie naar WebP**

```bash
python3 -c "
from PIL import Image
img = Image.open('PAD_NAAR_AI_ILLUSTRATIE.png')
# Max 2000px breed
if img.width > 2000:
    ratio = 2000 / img.width
    img = img.resize((2000, int(img.height * ratio)), Image.LANCZOS)
img.save('fotos/wellness-plattegrond-illustratie.webp', 'WEBP', quality=72, method=6)
print(f'Saved: {img.width}x{img.height}')
"
```

- [ ] **Stap 9.2: Wissel src in HTML**

Zoek:
```html
src="wellness-plattegrond.png"
```
Vervang door:
```html
src="fotos/wellness-plattegrond-illustratie.webp"
```

- [ ] **Stap 9.3: Verfijn pin-posities op de echte illustratie**

Open de pagina in browser. Open DevTools console en gebruik dit hulpscript om precieze posities te bepalen (klik op de illustratie, console logt left%/top%):

```js
document.querySelector('.wp-section__img').addEventListener('click', function(e) {
  var rect = this.getBoundingClientRect();
  var left = ((e.clientX - rect.left) / rect.width * 100).toFixed(1);
  var top  = ((e.clientY - rect.top)  / rect.height * 100).toFixed(1);
  console.log('left: ' + left + '%, top: ' + top + '%');
});
```

Klik op elke zone in de illustratie en noteer de percentages. Update de `pin: { left, top }` waarden in de `WP_ZONES` array.

- [ ] **Stap 9.4: Visueel verifiëren en commit**

Controleer alle 12 pins op de illustratie. Dan:

```bash
git add fotos/wellness-plattegrond-illustratie.webp wellness-arr-c.html
git commit -m "feat: wellness plattegrond — AI-illustratie + verfijnde pin-posities"
```

---

## Openstaande noten

- **Sauna-types/temperaturen:** De website vermeldt "4 unieke sauna's (o.a. infrarood- en zoutsteen)". Precieze types en temperaturen van alle 4 sauna's controleren bij het hotel vóór live-gang.
- **Sectie-titel:** Na bouw beoordelen of er ruimte is voor een kop boven de plattegrond.
- **Pin-posities Task 1–8:** Gebaseerd op de technische plattegrond-tekening. Worden verfijnd in Task 9.
